"""OpenAI chat completions provider for ingestion classification."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError
from pydantic import ValidationError

from src.ingest_review.extract import SourceDocument
from src.ingest_review.proposal_regen_provider import run_proposal_regeneration
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import (
    PROMPT_VERSION,
    REGENERATABLE_SOURCE_SECTION_KEYS,
    GlossaryTagSuggestOutput,
    LlmClassificationOutput,
    SectionRegenerateOutput,
    llm_output_json_schema,
)
from src.ingest_review.tags import normalize_tag
from src.ingest_review.wiki_snapshot import WikiSnapshot

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an analyst helping curate a personal AI-engineering Markdown wiki.
Return only valid JSON matching the provided schema. Ground every substantive claim in the \
source text via supporting_snippet (or source_summary section text for narrative fields). \
If unknown, use empty strings or empty arrays and low confidence. Do not invent facts. \
Do not infer economy-wide or industry-wide shifts, "broader moves", or macro narratives \
from a single article or roundup unless the source text explicitly argues them with evidence. \
In prose fields (especially why_it_matters), if stakes are thin or purely promotional, say \
so briefly instead of padding with confident industry diagnosis.

CORE PRINCIPLE: maximize durable knowledge gained per minute of human review. \
Prefer precision over recall, durable knowledge over completeness, review speed over \
exhaustive extraction, and high-value proposals over many medium-value proposals.

Every proposal MUST include a value_level field: "high", "medium", or "low".
- high: durable, operationally relevant, novel to the wiki, strong evidence, \
likely reused across multiple future sources
- medium: useful but not essential, moderate evidence, incremental contribution
- low: marginal value, weak evidence, narrow applicability, or already well-covered

Every proposal MUST include evidence_type — classify the EVIDENCE BASIS for this \
proposal (not the topic). Use exactly one of: vendor_claim, independent_analysis, \
benchmark, user_report, implementation_case, research_result, expert_opinion, \
speculative_claim, mixed, unknown.
- vendor_claim: the company/vendor/provider/tool-maker/organization discussed is \
the source of the claim (e.g. their blog, product announcement, press release).
- independent_analysis: independent writer, analyst, third-party publication — not \
the vendor speaking for their own product.
- benchmark: the proposal depends mainly on benchmark numbers, evals, leaderboards, \
quantitative tests.
- user_report: practitioner anecdote, forum/social/blog user experience.
- implementation_case: concrete description of how something was implemented \
(architecture, rollout, stack).
- research_result: grounded in paper, formal experiment, or research artifact.
- expert_opinion: mainly a named expert's judgment or strategic read.
- speculative_claim: prediction or weakly evidenced forward-looking claim.
- mixed: multiple evidence types matter equally; no single one dominates.
- unknown: unclear from the source.

Prefer fewer high-value proposals over many medium/low proposals.

For tags and types: follow TAG_ONTOLOGY_RUBRIC, PRIMARY_SECONDARY_SEMANTICS, and each \
entity rubric's tag/type addendum. Do not invent source-level tags.
For tools: proposed_types MUST be a subset of TOOL_TYPES_ALLOWLIST (at most 2 unless \
genuinely multi-category); first type = primary category, second = optional adjacent role.
For foundation_models: proposed_types MUST be a subset of MODEL_TYPES_ALLOWLIST (at most 2 \
unless genuinely multi-category); first = deployment/openness class, second = capability focus.
For implementation_studies: follow IMPLEMENTATION_STUDY_WORTHINESS GATE in IMPL_STUDY_RUBRIC; \
if the gate fails, return implementation_studies: [] and extract value via topics, how_to, \
industry_trends, roundup_signals, or interview_insights instead.

Always fill extraction_meta with skip_recommended, skip_reason, total_candidates_considered, \
and review_burden_estimate. If the article contains no durable, wiki-worthy knowledge, \
set skip_recommended=true and skip_reason explaining why; return empty arrays for all \
entity types. Do NOT force low-value extractions.

Always fill source_type_detection with the detected source type, confidence, and reasoning. \
If the source is an ai_industry_roundup, also populate roundup_signals. \
If the source is an ai_tools_roundup, extract ONLY tools and foundation_models per \
AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC; leave roundup_signals empty []. \
If the source is an interview_or_transcript, also populate interview_insights. \
Prefer reusing existing wiki pages (match_candidates) when the article overlaps with existing \
content; suggest append_to_existing over create_new_page whenever possible. \
For how_to: question_title is a wiki page name (noun phrase), not an interview question—see \
HOWTOS_RUBRIC.

Anchor all temporal language to the source's published_date; never use unanchored words \
like "currently", "now", "soon", "recently", or "within 1-2 years".

Voice for source_summary chapters (except accessible_overview): concise, direct, practical. \
Audience is an advanced AI practitioner focused on conversational AI, chatbots, voicebots, \
and service automation—not a research paper audience. Avoid LinkedIn tone, generic AI hype, \
buzzword stacking, and exaggerated claims. Prefer clarity and usefulness over completeness.

For accessible_overview only ("Easy read"): write for a curious newcomer to AI—plain \
everyday language, no abbreviations (spell out terms), gentle pacing, usually 7–10 sentences. \
Expand and explain; do not compress like the practitioner summary."""


TEMPORAL_ANCHORING_RULE = """\
## TEMPORAL ANCHORING RULE (applies to ALL output fields)

All temporal judgments in prose fields (why_it_matters, time_sensitivity, \
operational_relevance, durability_estimate rationale, etc.) MUST be anchored to the \
source's published_date from the Metadata section.

Banned unanchored words: "currently", "now", "soon", "recently", "today", \
"at the time of writing", "in the coming months", "within 1-2 years", \
"immediately". These words lose meaning once the publication date is forgotten.

Required pattern: always include an explicit date anchor. Examples:
- "Actionable as of May 2025"
- "Likely relevant through mid-2027"
- "Early-stage as of Q2 2025; monitor"
- "Inference cost trends as of May 2025 suggest..."

Non-temporal qualifiers that need no anchor are fine: "incremental improvement", \
"potentially transformative", "hype/noise", "strategically important".

Time-bounded relevance (e.g. actionable as of <date>, monitor vs adopt) must reflect \
this article's shelf-life or the claims in the source—not general industry timing you \
have no data for outside what the source states.

For every model that has an assessed_as_of field, copy the published_date from \
Metadata (empty string if unknown)."""


EXTRACTION_BUDGET_RUBRIC = """\
## EXTRACTION BUDGETS (hard limits)

You MUST respect these limits. If more candidates exist than the budget allows, \
rank by value_level (high > medium > low) then confidence, and include only the \
top items within budget. Report total_candidates_considered in extraction_meta.

{budget_lines}

If the article contains no durable, wiki-worthy knowledge, set \
extraction_meta.skip_recommended = true and skip_reason explaining why. \
Return empty arrays for all entity types. Do NOT force low-value extractions."""


AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC = """\
## AI_TOOLS_ROUNDUP_EXTRACTION (ONLY when detected_source_type == "ai_tools_roundup")

Mutually exclusive with ai_industry_roundup-style roundup_signals: do NOT fill roundup_signals \
for this type (return []).

When the source is ai_tools_roundup:
- glossary, topics, how_to, industry_trends, roundup_signals, implementation_studies, \
interview_insights MUST each be [] (no exceptions).
- tools vs foundation_models: Put **application products** (IDEs, agents, SaaS, CLIs, MCP \
servers, orchestration platforms, etc.) in **tools**. Put **foundation / frontier / base \
models** and model families the article treats as a primary list subject (e.g. GPT-5, Claude 4, \
Gemini 2.5, Llama 4) in **foundation_models** — NOT in tools. If the headline is \"tool\" but the \
entry is clearly a **model release**, use foundation_models.
- tools: one ToolProposal per distinct PRIMARY enumerated **non-model** entry the article gives \
substantive coverage to—match the article count when it claims e.g. \"10 tools\" and each item \
is a real entry.
- foundation_models: one FoundationModelProposal per distinct PRIMARY enumerated **model** entry \
(or clearly standalone reviewed model); omit passing name-drops.
- The numeric max lines under ## EXTRACTION BUDGETS do NOT cap tools or foundation_models for \
this source type; completeness for listed tools beats those limits. Treat all other proposal \
arrays as max zero (empty)."""


VALUE_RANKING_RUBRIC = """\
## VALUE RANKING (applies to ALL proposals)

Every proposal MUST include a value_level field: "high", "medium", or "low".

High: durable knowledge likely relevant 12+ months after publication; \
operationally relevant to AI engineering, service automation, or agent workflows; \
novel to the wiki; strong evidence quality; high reuse potential.

Medium: useful but incremental; moderate evidence; partially covered by existing \
wiki content; good-to-have but not essential.

Low: marginal or transient value; weak evidence; already well-covered; very narrow \
applicability; term merely mentioned, not substantively explained.

Prefer fewer high-value proposals over many medium/low proposals. \
The system optimizes for: max durable knowledge gained per minute of human review."""


EVIDENCE_TYPE_RUBRIC = """\
## EVIDENCE TYPE (every proposal object)

Classify the evidence basis for THIS proposal — not the topic label.
Use exactly one string for evidence_type:

- vendor_claim — company/vendor/model-provider/tool-maker claims about their own offering; \
vendor blog or announcement framing.
- independent_analysis — third-party or independent author assessment (not the vendor).
- benchmark — proposal rests mainly on benchmark/eval/leaderboard/quantitative numbers.
- user_report — practitioner report, anecdote, forum/blog/social experience.
- implementation_case — concrete how-it-was-built / how-it-was-deployed description.
- research_result — paper, formal experiment, or cited research artifact.
- expert_opinion — named expert's judgment or strategic interpretation dominates.
- speculative_claim — prediction or future-facing claim without strong grounding.
- mixed — several evidence types are equally important.
- unknown — basis unclear from text.

Rules: A useful proposal from an OpenAI post about their own model is still often \
vendor_claim. Use speculative_claim for weak predictions. Use benchmark only when \
quantitative eval evidence is central. Use implementation_case only with real \
implementation detail. Do not leave evidence_type blank — use unknown if unsure."""


TAG_ONTOLOGY_RUBRIC = """\
## TAG ONTOLOGY (proposal-level routing — NOT source tags)

Tags classify each PROPOSAL for wiki routing and aggregation. They are NOT article labels, \
marketing phrases, or title echoes.

Mandatory procedure for every tagged proposal:
1. Read the entity's TAGS or TYPES allowlist section in this prompt.
2. Pick the best existing tag(s) from that list whenever reasonably possible.
3. Set primary_tag to the single best EXACT allowlist string (copy verbatim from the list), \
or "" if none fit. NEVER put an invented slug, abbreviation, or off-list label in primary_tag.
4. Set secondary_tag only to a second EXACT allowlist string when it adds distinct \
cross-cutting value, or "" otherwise. NEVER put off-list text in secondary_tag.
5. Set suggested_new_tag ONLY when no reasonable allowlist match exists after a semantic \
scan — including checking near-synonyms (e.g. agent-workflow vs agentic-workflows). \
If primary_tag and secondary_tag are both "", you MAY leave suggested_new_tag "" as well.

Tag sparsity (strict):
- Most proposals need only primary_tag; leave secondary_tag "" unless clearly warranted.
- Never use secondary_tag as a synonym or minor variant of primary_tag.
- Maximum two allowlist tags per proposal (primary + optional secondary).
- Empty primary_tag and secondary_tag when nothing fits and you are not confident in a \
new tag under the new-tag gate below.

New-tag gate — suggest suggested_new_tag only if the concept is: distinct, recurring, \
broad enough for many future sources, and entity-appropriate. Before suggesting, verify \
no close allowlist match exists.

Anti-patterns (never use as tags): article-specific slugs, launch/event names, vendor \
marketing ("enterprise-ready"), quality adjectives ("useful", "important"), title fragments \
("gpt-5-4-launch", "openai-flywheel"). Use kebab-case for suggested_new_tag.

Prefer reusing an existing approved tag whenever reasonably possible."""


PRIMARY_SECONDARY_SEMANTICS = """\
## PRIMARY / SECONDARY SEMANTICS

Domain entities (glossary, topics, trends, how_to, implementation_studies, roundup_signals, \
interview_insights):
- primary_tag: main strategic domain — the single primary wiki routing bucket this proposal \
belongs to first (copy exactly from allowlist), e.g. ai-safety, orchestration, evaluation.
- secondary_tag: cross-cutting relationship — optional second allowlist tag only when the \
proposal clearly also belongs to another major theme (not a synonym or minor variant of \
primary).

Tools (proposed_types list — same ordering spirit, not primary_tag fields):
- First type in proposed_types: what kind of tool this is (main category).
- Second type (if any): adjacent operational role or secondary classification.
- At most 2 types unless the tool is genuinely multi-category.

Foundation models (proposed_types list):
- First type: deployment / openness / operational profile (e.g. open-weights, api-hosted).
- Second type (if any): capability specialization (e.g. coding, reasoning, multimodal).

Roundup signals use TREND_TAGS_ALLOWLIST semantics. Interview insights use \
TOPIC_TAGS_ALLOWLIST semantics."""


SOURCE_CHAPTERS_RUBRIC = """## source_summary (required JSON subtree)

Fill every field below from the article. Empty string or [] only when truly absent.

**summary** (string): Usually 4–10 sentences; adapt to complexity. Core ideas and arguments only; \
no chronological retelling; no filler openers; explain concepts plainly; practical understanding \
over technical precision. Audience: advanced AI practitioner.

**accessible_overview** (string — "Easy read"): Usually 7–10 sentences; shorter only if the \
article has little substance. Audience: intelligent reader new to AI—interested but not technical. \
Use everyday language; spell out terms instead of abbreviations (e.g. "large language model" not \
"LLM"; explain "retrieval-augmented generation" in full if needed). Cover what the article is \
about, why people care, and the main story in order—not a compressed expert brief. Avoid jargon \
stacks, acronym dumps, benchmark numbers without explanation, and telegraphic wiki-style bullets. \
Write after mentally drafting summary: expand and explain; do NOT copy summary verbatim or make \
this section shorter than summary.

**key_insights** (array of strings, at most 5): Only insights that are actionable, strategically \
important, surprising, or practically useful—and non-obvious. One concise sentence per item. \
No generic observations.

**why_it_matters** (string): One flowing piece of prose (usually 7–12 sentences when the source \
is rich; shorter when thin). Structure: **Opening (about the first half)** — why the piece \
matters for AI engineering, building products, or technical reading. Tie every sentence to \
what the source actually says (claims, listed capabilities, roundup items). **Do not** in the \
opening mention customer support, contact centers, voicebots, meeting capture, \
dictation-to-workflow, back-office automation, or the phrase "service automation" — \
reserve all of that for the closing. \
**Closing (last 2–4 sentences only)** — \
service automation/support/voice/meetings/back-office implications **only if** the article \
substantively discusses them; otherwise omit entirely (no filler). \
Do **not** repeat the same automation thesis twice; the closing extends or narrows, it does not \
duplicate the opening. **Anti-patterns** (forbidden as unsourced global claims): "broader shift", \
"the industry is moving", "reflects a shift from X to Y", "signals that …", framing that the \
"useful comparison is no longer …" for the whole industry unless the source explicitly argues \
that. Prefer: "The article argues…", "The piece surfaces…", "The roundup lists…". If the article \
is shallow or stakes are unclear, say significance is **limited** or **unclear** in a sentence \
or two. \
End with a short honest time-bounded judgment anchored to the source's publication date \
(actionable as of that date, monitor vs adopt, hype vs durable where grounded in the text). \
No hype. No certainty theater.

**limitations_and_open_questions** (string): Limitations, weak evidence, benchmark limits, \
unrealistic assumptions, missing implementation detail, unresolved operational concerns, \
economics, security/privacy, evaluation weaknesses. Skeptical where warranted.

**contradictions_and_skepticism** (string): Speculative claims, tension with common industry \
practice, hype without evidence, oversimplifications. Thoughtful skepticism—not a hostile \
attack. If nothing major, say so briefly.

**sources** (array of strings): URLs or references present in the article or metadata; else []."""


IMPL_STUDY_RUBRIC = """\
## implementation_studies (array of objects — implementation studies)

Implementation studies are organizational operational deployment cases with auditable \
real-world evidence — NOT generic "someone built something" narratives.

IMPLEMENTATION_STUDY_WORTHINESS GATE — before adding ANY object, the source must \
support at least ONE of:
1. Production deployment evidence (live or serious pilot in real operations; not a \
local-only demo) — populate deployment_context
2. Operational metrics (latency, cost, volume, accuracy, ROI, headcount, ticket \
deflection, etc.) — cite in evidence_snippets and outcome_status
3. Organizational adoption (rollout scope, teams, geographies, user counts, \
change-management) — not solo "I tried this"
4. Measurable outcomes (before/after, success/failure with specifics) — outcome_status
5. Scaling constraints (what broke or limited scale) — operational_constraints
6. Real-world success/failure lessons grounded in what happened — \
success_or_failure_factors / key_lessons
7. Operational maintenance learnings (monitoring, drift, incidents, human handoff)
8. Non-trivial deployment complexity (integration, safety, compliance, multi-system \
rollout) — technical_approach + deployment_context

If NONE apply, return implementation_studies: []. Extract value via topics, how_to, \
industry_trends, roundup_signals, or interview_insights instead.

When the gate passes, ALL hard requirements apply:
- Named company (explicit organization; not anonymous "a team")
- At least 2 evidence_snippets with at least 1 provenance: "stated" (verbatim-supported)
- deployment_context and outcome_status non-empty and specific (not "unknown", "TBD", \
or generic filler)
- evidence_type should be implementation_case or mixed when deployment evidence \
dominates; not speculative_claim or expert_opinion alone
- Default suggested_action: "ignore" unless confidence >= 0.6 AND value_level is \
high or medium with clear evidence

IMPLEMENTATION STUDY EXTRACTION BOUNDARIES — do NOT propose for:
- Personal experiments, weekend builds, solo side projects ("I built this over the weekend")
- Architecture essays, pattern explainers, stack diagrams without operational outcomes
- Speculative workflow ideas or future visions without deployment facts
- Prototype writeups without production or serious pilot evidence
- Conceptual blog posts or thought leadership without deployment facts
- Tool tutorials disguised as case studies
- Generic practitioner narratives ("we use X in our stack") without deployment evidence
- Vendor marketing with no concrete metrics or deployment detail (usually ignore)
- Re-describing the article title as a fake "study"

ROUTING (prefer other entity types when gate fails):
- Procedural knowledge, no org-specific deployment case → how_to (or topics)
- Durable architecture/operational pattern, no specific org deployment → topics
- Industry-wide shift, not one org → industry_trends
- Weak signal in a roundup → roundup_signals
- Gate passes → at most 1 implementation_study (respect budget)
- Gate fails → implementation_studies: []

Positive indicators: named org + industry + time-bounded rollout; pilot→production \
(or pilot ended) arc; production constraints discovered; failure modes with \
operational root cause; verifiable third-party case study claims.

Not for product announcements, benchmarks-only pieces, or pure opinion.

Each object MUST include:
- title: short descriptive implementation title
- company: company or organization name
- industry: business domain (e.g. quick-service restaurant, healthcare, telecom)
- overview: what happened (real implementation, not generic summary)
- what_was_implemented: specific technology/system/workflow
- business_objective: why the company pursued this
- technical_approach: how they did it (vendors, architecture, methods) — \
only what the source supports
- deployment_context: where/how it was tested or deployed
- outcome_status: what happened (pilot ended, scaled, failed, ongoing)
- success_or_failure_factors: why it worked or didn't
- operational_constraints: production constraints that mattered
- ai_model_observations: what this case suggests about AI systems
- implications_for_service_automation: what this teaches about support \
automation, voicebots, chatbots, contact centers — if no implications, \
say so explicitly
- strategic_signals: broader strategic patterns
- key_lessons: short practical lessons (list of strings)
- open_questions: unresolved questions (list of strings)
- related_sources: URLs/references from the article
- evidence_snippets: array of {claim, snippet, provenance} where \
provenance is "stated", "inferred", or "interpretation"
- primary_tag: most fitting tag from IMPL_STUDY_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from IMPL_STUDY_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- match_candidates: existing wiki implementation-study pages that may overlap
- confidence: 0.0–1.0
- suggested_action: "create" | "update" | "ignore"
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

Voice: concise, direct, practical. Focus on operational reality over marketing \
claims. Skeptical where warranted. No hype, no LinkedIn tone.

Tag semantics (IMPL_STUDY_TAGS_ALLOWLIST): domain of the implementation case. \
Follow TAG_ONTOLOGY_RUBRIC."""


GLOSSARY_RUBRIC = """\
## glossary (array of objects — glossary term proposals)

GLOSSARY-WORTHINESS GATE — before proposing any term, ALL must be true:
1. Would this term deserve a standalone glossary entry in ANY future article?
2. Is it an established industry term (not article-specific jargon)?
3. Is it reusable across multiple AI engineering contexts?
4. Does the source provide enough depth for a useful definition?
5. Is it NOT merely a supporting term mentioned in passing?
If any answer is "no", do NOT propose it. Prefer 1-2 high-value terms \
over 5+ marginal ones.

CRITICAL: Only propose ESTABLISHED industry terms that already exist in \
professional usage and are verifiable via a web search. Do NOT propose \
neologisms coined by the article author, ad-hoc phrases, or terms invented \
for this specific article. If in doubt, omit the term.

GLOSSARY EXTRACTION BOUNDARIES — the glossary is for durable conceptual \
primitives and recurring operational AI concepts, NOT generic business \
vocabulary, strategy language, management terminology, marketing \
abstractions, temporary framing, product slogans, or company-specific \
narratives. Do NOT propose terms such as: flywheel, ecosystem, platform \
strategy, innovation loop, transformation journey.

Operational or product patterns (e.g. agent-first product design, \
orchestration-first UX, context-centric workflows, coding-agent development \
loops) are broader patterns — extract them under topics, not glossary. \
A glossary entry must be a reusable AI/engineering concept, a durable \
operational abstraction, a recurring industry term, or a semantically \
distinct primitive likely to recur across many future sources.

When uncertain whether something is a glossary primitive or a broader \
pattern, prefer a topic contribution over a glossary term (or omit).

Each object MUST include:
- term: the term or phrase (use the most common established industry form)
- proposed_definition: a STANDALONE, context-free definition — like a \
dictionary or encyclopedia entry. 1-3 sentences. MUST NOT reference \
"this article", "the source", "the author", or any article-specific \
context. Write as if the reader has never seen the source article. \
Pure concept definition only. Avoid academic or buzzword-heavy language.
- extended_explanation: a longer explanation (3-8 sentences when the \
source supports it) aimed at making the concept accessible to someone \
who is not yet an expert. Use analogies, simpler terms, concrete \
examples, or comparisons with related concepts to build understanding. \
Do NOT reference the article. Empty string only if the source provides \
no depth beyond a bare definition.
- supporting_snippet: verbatim quote from the source that supports \
the definition
- relevance_note: why this concept matters for AI practitioners — NOT \
why it matters for this article. Focus on: where it appears in \
real-world AI systems, how it affects AI engineering / orchestration / \
evaluation / automation / agent workflows, and relevance to \
conversational AI, chatbots, voicebots, or service automation. \
NEVER reference the article ("the article focuses on…", "this paper \
argues…"). 1-3 sentences of durable operational/industry relevance.
- related_terms: cross-references ONLY—each string MUST use the **exact same spelling \
and wording** as the ``term`` field of another object in **this** ``glossary`` array when \
that concept is also proposed, OR as a term from **EXISTING_GLOSSARY_TERMS** in the prompt \
when the concept is already in the wiki. Do **not** invent alternate surface forms. Do **not** \
use abbreviations or acronyms in ``related_terms`` when the batch or wiki uses the **full \
phrase** as the canonical term (e.g. use ``Reinforcement Learning from Human Feedback``, not \
``RLHF``, unless ``RLHF`` is itself the established ``term``). You may use acronyms freely in \
``extended_explanation`` / ``supporting_snippet`` prose; ``related_terms`` must stay aligned to \
canonical glossary titles. If no exact batch/wiki label applies, omit that edge (leave out the \
string) rather than approximating.
- primary_tag: most fitting tag from GLOSSARY_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from GLOSSARY_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- match_candidates: existing glossary terms that may overlap
- confidence: 0.0-1.0
- suggested_action: "create" | "update" | "ignore"
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

Voice: clear, practical, accessible. Define for a senior practitioner, \
not an academic. Prefer operational understanding over theoretical precision.

Tag semantics (GLOSSARY_TAGS_ALLOWLIST): broad durable domain for routing — \
not article-specific labels. Follow TAG_ONTOLOGY_RUBRIC and PRIMARY_SECONDARY_SEMANTICS."""


TOPICS_RUBRIC = """\
## topics (array of objects — topic contributions)

Extract reusable operational knowledge units, NOT article summaries.
Each contribution answers: "What does this article teach about [concept X] \
that is useful long-term?"

Only extract topics that are: reusable across multiple contexts, operationally \
relevant, likely to reappear, conceptually stable, and broad enough to \
aggregate knowledge from many future sources.

Default to append_to_existing. New pages (create_new_page) only for genuinely \
novel, broad, stable concepts not covered by any existing topic.

Each object MUST include:
- topic_slug: kebab-case stable identifier — broad enough to accumulate many \
future contributions (e.g. context-engineering, NOT openai-context-engineering-\
announcement)
- topic_title: human-readable form of the slug
- knowledge_summary: 3-8 sentences, source-agnostic, synthesized. No "this \
article says..." or "the author argues..."
- examples: OPTIONAL. Only when the source contains a **concrete, quotable \
illustration** that makes the abstract topic easier to grasp — e.g. a named product \
integration, a short verbatim quote from the source, or a specific scenario explicitly \
described. Write 1-4 sentences OR include a brief quoted clause taken from the source. \
Must be grounded in explicit source text; do **not** invent examples. This is **not** a \
second abstract summary — if the passage is only generic with no good concrete example, \
use "" (empty string).
- operational_insight: practical takeaway for a senior practitioner
- supporting_snippet: verbatim evidence from the source
- relevance_note: why this **topic** matters for AI practitioners and the industry \
long-term — NOT why it appeared in this source or what the article emphasizes. \
Focus on durable operational/industry significance: where the pattern shows up in \
real systems, who benefits, and how it affects engineering, orchestration, evaluation, \
automation, or agent/service workflows. NEVER reference the article ("the article", \
"this piece", "the author's strongest distinction", "in this source"). 1-3 sentences; \
empty string only if you cannot state industry relevance without article framing.
- key_points: specific knowledge bullets worth accumulating (list of strings)
- related_topics: cross-links to **other topic pages** only — each string MUST be the \
``topic_slug`` of another object in **this** ``topics`` array and/or a slug from \
**EXISTING_TOPIC_TITLES** / the wiki topics index. Use kebab-case stable identifiers \
(e.g. workflow-automation, context-engineering). Do **NOT** put TOPIC_TAGS_ALLOWLIST \
entries here (e.g. ai-engineering, knowledge-management, ai-infrastructure) — those \
belong only in primary_tag/secondary_tag. Do **not** repeat this object's own \
topic_slug. Use [] when no valid cross-link exists.
- primary_tag: most fitting tag from TOPIC_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from TOPIC_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- match_candidates: existing topic pages that may overlap
- confidence: 0.0-1.0
- suggested_action: "append_to_existing" | "create_new_page" | "ignore"
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

Avoid: article-specific framing, ultra-narrow topics, hype-driven \
fragmentation, one-off concepts, duplicate existing topics.

Voice: clear, operational, synthesized. Write as reusable knowledge, \
not as article commentary.

Tag semantics (TOPIC_TAGS_ALLOWLIST): strategic/operational domain for the \
knowledge unit — not the article title. Follow TAG_ONTOLOGY_RUBRIC.

related_topics vs tags: ``related_topics`` = wiki topic page slugs; \
``primary_tag``/``secondary_tag`` = allowlist routing tags only. Never interchange them.

Routing: operational or architecture patterns WITHOUT a specific organizational \
deployment case belong here — NOT in implementation_studies."""


HOWTOS_RUBRIC = """\
## how_to (array of objects — how-to proposals)

Extract procedural/implementation knowledge, NOT theoretical summaries. \
Only extract how-tos where the source provides enough implementation \
substance — not vague advice.

Default to append_to_existing. New pages only when the how-to covers a \
genuinely distinct procedure not addressed by existing pages.

### Plain-language fields (what_and_problem, answer_summary)

Write ``what_and_problem`` and ``answer_summary`` for a curious newcomer to AI—plain \
everyday language, no unexplained abbreviations (spell out terms), gentle pacing.

- ``what_and_problem``: 4–8 sentences. First section a reader sees after the page \
title. Explain what this how-to is about and which real-world problem or constraint \
it addresses (e.g. scale, missing data, compliance). No "this article says…"; no \
article-specific framing.
- ``answer_summary``: 3–8 sentences in the same easy voice. Summarize how to approach \
the procedure in plain terms—standalone guidance a non-expert can follow. Open with \
situational context when the source stresses it.

``implementation_steps``, ``prerequisites``, and ``caveats`` may stay more procedural \
and practitioner-focused.

### Title granularity (question_title)

The JSON field is ``question_title``, but it is the **wiki page title** for a \
durable how-to article—not a copy of the source's rhetorical question.

- Use a **short noun phrase** (about 3–8 words): a topic-style label for the \
core procedure. Title Case is fine.
- **Do NOT** start titles with: ``How to``, ``How do you``, ``How should``, \
``What is the best way to``, or similar interrogative/openers.
- **Do NOT** put situational qualifiers in the title: no trailing ``when …``, \
``if …``, ``without …``, ``for teams that …``, or article-specific constraints.
- **Do NOT** use brand names, article-specific framing, or answer leakage in \
the title (same as before).

Put constraints and scenario context in ``what_and_problem`` (and optionally the \
open of ``answer_summary`` when the source emphasizes it).

**BAD title:** ``How do you evaluate a production voicebot when you cannot review \
every call manually?``
**GOOD title:** ``Evaluation of a Production Voicebot``
**GOOD what_and_problem:** Explains how to check a production voice assistant when \
listening to every call by hand is not realistic at high call volume.

**Self-check before output:** ``question_title`` must NOT contain ``?``, must NOT \
start with ``How``/``What``/``When``/``Why``, and must NOT include ``when``, ``if``, \
or ``without`` clauses—move those to ``what_and_problem``.

Before ``create_new_page``, compare the **core procedure** to \
**EXISTING_HOWTO_TITLES** and ``match_candidates``. If an existing page covers the \
same procedure, use ``append_to_existing`` and align the title with that page's style. \
Prefer **fewer, broader** how-tos over many micro-variants (same spirit as topics: \
avoid ultra-narrow fragmentation).

If the source only supports a narrow edge case with no reusable procedure, use \
``suggested_action: "ignore"`` or merge into a broader existing how-to rather than \
creating a micro-howto.

Each object MUST include:
- question_title: wiki page title (noun phrase per Title granularity above)
- what_and_problem: plain-language intro—what this is and what problem it solves
- answer_summary: plain-language procedural guidance, 3-8 sentences, standalone
- supporting_snippet: verbatim evidence from the source
- caveats: gotchas, failure modes, limitations — skeptical where warranted. \
Empty string only if genuinely none
- implementation_steps: concrete, ordered steps when the source supports \
them (list of strings)
- prerequisites: what a practitioner needs before attempting this (list \
of strings)
- related_howtos: cross-references to other how-to slugs (list of strings)
- primary_tag: most fitting tag from HOWTO_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from HOWTO_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- match_candidates: existing how-to pages that may overlap
- confidence: 0.0-1.0
- suggested_action: "append_to_existing" | "create_new_page" | "ignore"
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

Avoid: interrogative titles, conditional clauses in titles, article-specific \
framing, ultra-narrow micro-howtos, duplicate existing how-tos.

Voice: ``what_and_problem`` and ``answer_summary`` use easy read; other fields stay \
direct and implementation-focused. Write as reusable procedural guidance.

Tag semantics (HOWTO_TAGS_ALLOWLIST): workflow/implementation area — overlap with \
topic tags is OK. Follow TAG_ONTOLOGY_RUBRIC.

Routing: reusable procedures without org-specific deployment evidence belong here \
— NOT in implementation_studies."""


TOPIC_REGEN_RUBRIC = """\
Regenerate ONE topic contribution under a reviewer-supplied NEW_TOPIC_TITLE.

Rules:
- Reframe all fields for the broader title NEW_TOPIC_TITLE — it must be a stable wiki page \
name (noun phrase), broad enough to accumulate knowledge across many future sources.
- If the prior draft was narrower than NEW_TOPIC_TITLE (e.g. "Local Multimodal Inference" → \
"Local Inference"), move the narrower angle into knowledge_summary and examples — NOT into \
the title (title is set by the reviewer; you do not output topic_title or topic_slug).
- Ground every claim in ARTICLE_PLAIN_TEXT via supporting_snippet; do not invent facts.
- Source-agnostic voice: no "this article says…", no article-specific framing in \
relevance_note (durable industry significance only).
- related_topics: kebab-case topic_slug cross-references from EXISTING_TOPIC_SLUGS only; \
never TOPIC_TAGS_ALLOWLIST entries.
- Preserve operational usefulness; 3–8 sentences for knowledge_summary when substance allows.
- examples: concrete illustration from source only, or "" if none.
- Follow REVIEWER_NOTE when provided."""


TRENDS_RUBRIC = """\
## industry_trends (array of objects — trend observations)

Extract time-sensitive industry patterns, NOT timeless concepts (those \
belong in topics). Trend pages acknowledge uncertainty by design — no \
certainty theater.

Default to append_to_existing. New pages only for genuinely novel \
industry patterns not captured by existing trend pages.

Each object MUST include:
- trend_slug: stable kebab-case wiki page id (e.g. inference-cost-collapse, NOT \
GPT-4o-price-cut or headline labels)
- trend_title: human-readable page title for the same pattern (e.g. Inference \
Cost Collapse) — broad enough to accumulate evidence across sources
- trend_description: standalone, source-agnostic description of the pattern
- evidence_from_source: what this article specifically contributes as evidence
- time_sensitivity: explicitly state how time-bound this observation is
- uncertainty_note: REQUIRED — explicitly acknowledge uncertainty, \
conflicting signals, or limited evidence. Empty string is NOT acceptable
- supporting_snippet: verbatim evidence from the source
- supporting_data_points: specific data or facts that support the trend \
(list of strings)
- related_trends: other trend_slug values (kebab-case list of strings)
- primary_tag: most fitting tag from TREND_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from TREND_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- match_candidates: existing trend pages that may overlap
- confidence: 0.0-1.0
- suggested_action: "append_to_existing" | "create_new_page" | "ignore"
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

Voice: measured, evidence-grounded, explicitly uncertain where warranted. \
No hype, no certainty theater.

Tag semantics (TREND_TAGS_ALLOWLIST): durable industry pattern domain — not \
headline or vendor campaign labels. Follow TAG_ONTOLOGY_RUBRIC."""


TOOLS_RUBRIC = """\
## tools (array of objects — tool proposals)

Only extract tools where the source provides OPERATIONALLY USEFUL information — \
not passing mentions. A tool is a distinct product, platform, framework, or \
application (not a tiny feature inside another tool).

Tool-worthiness criteria (ALL must apply):
- Operationally relevant: affects real workflows, engineering, automation
- Reusable: likely to recur across multiple future sources
- Distinct: meaningful standalone product, not a feature of another tool
- Accumulative: future sources could meaningfully enrich this tool's page
If a tool is merely mentioned in passing, set confidence < 0.3 and \
suggested_action = "ignore".

Each object MUST include:
- name: the tool's established name (e.g. Cursor, LangGraph, Ollama)
- short_description: 1-3 concise sentences explaining what the tool IS and does. \
Avoid hype, focus on practical understanding
- operational_relevance: 2-5 sentences on where this tool fits into real \
workflows. Evaluate for: support automation, AI agents, orchestration, \
evaluation, coding productivity, workflow automation, operational AI systems. \
Audience is a senior practitioner in conversational AI, chatbots, voicebots, \
service automation
- strengths: operational strengths in **explanatory prose or markdown bullets** \
(see Explanatory depth below). Each point must say *why it matters in practice*, \
not just name a feature. Typically 3-6 bullets or 2-4 sentences minimum when \
the source supports depth.
- weaknesses_limitations: REQUIRED skeptical assessment in the same explanatory \
style — limitations, costs, scalability issues, ecosystem immaturity, missing \
features, each with enough context that a reader understands the tradeoff. If \
none are evident from the source, state that explicitly in a full sentence.
- maturity_signals: adoption level, ecosystem health, community size, enterprise \
readiness — written as 2-4 explanatory sentences (not a comma-separated keyword \
list). Use honest descriptors: "rapidly growing", "niche developer tool", \
"experimental", "strong enterprise adoption", etc., with brief evidence from the source.
- supporting_snippet: verbatim evidence from the source
- core_capabilities: specific capabilities worth noting (list of strings). Each \
list item must be one **full sentence** explaining what the capability does and \
why it is notable — NOT a bare noun phrase or comma-joined feature name.
- integration_ecosystem: concrete integrations, APIs, compatibility (list of \
strings). Same rule: one explanatory sentence per integration, not keyword dumps.
- related_tools: comparable or complementary tools (list of strings)
- proposed_types: from TOOL_TYPES_ALLOWLIST ONLY; at most 2 unless genuinely \
multi-category. First = primary category, second = optional adjacent role. \
Answer "What kind of thing is this?" — NOT quality/popularity. Use [] if none fit
- proposed_new_type: if no existing type fits after checking near-synonyms in \
the allowlist, propose ONE new type in kebab-case; null otherwise
- match_candidates: existing tool pages that may overlap
- confidence: 0.0-1.0
- suggested_action: prefer "append_to_existing" for tools already in the wiki; \
"create_new_page" only for genuinely new tools worth tracking long-term
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

### Explanatory depth (strengths, weaknesses_limitations, maturity_signals, lists)

These fields capture high-value operational insight — **do not compress into keyword \
salads**. Forbidden pattern: comma-separated feature names with no explanation \
(e.g. "self-hosted deployment, multi-tier memory, model-agnostic selection").

Required instead:
- **Prose**: connected sentences that explain mechanism and practitioner value, OR
- **Bullets**: markdown lines starting with ``- `` where each bullet is 1-2 sentences \
explaining one capability/tradeoff and when it matters.

**BAD strengths:** "Self-hosted deployment, internal skill creation, multi-tier memory, \
model-agnostic model selection, containerized terminal execution."
**GOOD strengths (bullets):**
- Supports self-hosted deployment so teams can keep agent memory and execution on \
their own infrastructure rather than a vendor cloud.
- Ships a multi-tier memory model (working vs long-term) so recurring tasks can \
improve without re-prompting from scratch each session.

Use ``core_capabilities`` / ``integration_ecosystem`` for enumerations only when each \
list entry is already a full explanatory sentence; otherwise put the detail in \
``strengths`` or ``operational_relevance``.

Classification rule: types describe WHAT THE TOOL IS, not what it does well. \
Good: coding-assistant, desktop-app, voice-ai. Bad: productivity, useful, fast.

Voice: clear, operational, skeptical. No hype, no marketing language.

Type semantics (TOOL_TYPES_ALLOWLIST): what the tool IS — follow \
PRIMARY_SECONDARY_SEMANTICS for ordering of proposed_types."""


MODELS_RUBRIC = """\
## foundation_models (array of objects — model proposals)

Only extract models where the source provides OPERATIONALLY USEFUL information — \
not passing mentions. A model deserves extraction when the source contains \
meaningful operational evaluation, workflow implications, comparative observations, \
or strategic significance.

Model-worthiness criteria:
- Operational evaluation: real-world strengths, weaknesses, workflows, or capabilities
- Workflow implications: how the model changes engineering or automation workflows
- Comparative observations: meaningful comparison against other models
- Strategic significance: important enough that future sources will enrich it
- Reusable knowledge: observations likely useful beyond this single article
If a model is merely mentioned without operational depth, set confidence < 0.3 \
and suggested_action = "ignore".

Each object MUST include:
- model_name: the model's established name (e.g. GPT-5, Claude Sonnet, Gemini)
- provider: organization name (OpenAI, Anthropic, Google, Meta, DeepSeek, etc.)
- operational_summary: 1-3 sentences on what the model is operationally good at \
and what differentiates it. NOT a generic description like "X is a large language \
model." Instead: "X appears strong for long-horizon coding and agent orchestration."
- strengths: operational strengths in explanatory prose or markdown bullets (same \
rules as TOOLS_RUBRIC Explanatory depth) — each point explains *why* the capability \
matters, not a bare feature label. Typically 3-6 bullets or 2-4 sentences when the \
source supports depth.
- weaknesses_limitations: REQUIRED skeptical assessment in the same explanatory \
style — inference cost, planning weaknesses, formatting instability, hallucination \
patterns, context degradation, each with enough context to understand the tradeoff. \
If none evident, state that explicitly in a full sentence.
- workflow_implications: how this model changes AI engineering, orchestration, \
evaluation, automation workflows. Examples: "enables larger autonomous coding \
loops", "reduces prompt engineering effort", "lowers orchestration complexity"
- service_automation_implications: implications for conversational AI, chatbots, \
voicebots, support automation, containment rates, handoff reduction. If no \
meaningful implications, state explicitly. Avoid vague business language
- maturity_signals: adoption, ecosystem maturity, enterprise readiness — 2-4 \
explanatory sentences (not comma-separated keywords). Use honest descriptors with \
brief source-backed context.
- pricing_inference_implications: cost observations, latency, inference economics, \
deployment feasibility for high-volume use cases
- supporting_snippet: verbatim evidence from the source
- core_capabilities: specific capabilities worth noting (list of strings) — one \
full explanatory sentence per item, not bare feature names — coding, long-context, \
tool calling, voice, structured outputs, planning, etc. (list of strings)
- benchmark_observations: ONLY operationally meaningful evidence — SWE-Bench \
discussions, latency comparisons, context-window observations, tool-use evals. \
Do NOT create benchmark dumps (list of strings)
- comparative_observations: comparisons against other models — "stronger coding \
than X", "cheaper than Y", "faster than Z". Extremely valuable (list of strings)
- related_models: comparable or complementary models (list of strings)
- proposed_types: from MODEL_TYPES_ALLOWLIST ONLY; at most 2 unless genuinely \
multi-category. First = deployment/openness profile, second = capability focus. \
Use [] if no approved type fits
- proposed_new_type: if no existing type fits after checking near-synonyms in \
the allowlist, propose ONE new type in kebab-case; null otherwise
- match_candidates: existing model pages that may overlap
- confidence: 0.0-1.0
- suggested_action: prefer "append_to_existing" for models already in the wiki; \
"create_new_page" only for genuinely new models worth tracking long-term
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

Classification rule: types describe WHAT THE MODEL IS, not subjective quality. \
Good: reasoning-model, coding-model, multimodal-model. \
Bad: powerful, smart, enterprise-ready.

Prioritize observations likely to remain useful 6-12 months after the source's \
publication date. Transient hype or short-lived benchmark excitement belongs in \
trends, not model pages.

Voice: clear, operational, skeptical. No hype, no certainty theater.

Type semantics (MODEL_TYPES_ALLOWLIST): operational profile — follow \
PRIMARY_SECONDARY_SEMANTICS for ordering of proposed_types."""


SOURCE_TYPE_DETECTION_RUBRIC = """\
## source_type_detection (required JSON subtree)

Classify the source into exactly one type. Be conservative — default to \
"standard_article" for most content. Only choose specialized types when \
structural signals are strong.

Supported types:
- "standard_article" — default for most AI articles, blog posts, reports, \
opinion pieces
- "ai_industry_roundup" — digests, newsletters, radar posts, weekly AI news \
summaries whose primary purpose is aggregating many short items, links, or \
news blurbs. The key signal is a BUNDLE of loosely related items, not a \
single coherent argument
- "ai_tools_roundup" — curated multi-item piece whose PRIMARY structure is \
numbered or clearly separated reviews of named AI tools (and optionally \
models), each with substantive description; "N tools" / "tool 1…N" patterns, \
repeated per-tool blurbs. Prefer this over ai_industry_roundup when most \
main items are tools with dedicated coverage—not a general news link digest
- "interview_or_transcript" — long-form conversations with interviewer/ \
interviewee structure, Q&A format, multiple speaker perspectives, or \
transcript-like content
- "technical_howto" — primarily step-by-step tutorial or implementation guide
- "research_paper_or_report" — academic paper, formal research report, or \
technical whitepaper with citations and methodology
- "unknown" — use when genuinely uncertain

Disambiguation: ai_industry_roundup for general multi-topic news digests; \
ai_tools_roundup when the centerpiece is a curated tool list with reviews.

Fields:
- detected_source_type: one of the types above
- confidence: 0.0–1.0 (be conservative — 0.9+ only when structural signals \
are unambiguous)
- reasoning: array of 1–3 short strings explaining the classification \
decision"""


ROUNDUP_SIGNALS_RUBRIC = """\
## roundup_signals (array of objects — ONLY when \
source_type_detection.detected_source_type == "ai_industry_roundup")

Decompose the roundup into independent signal items. The roundup itself is \
NOT the knowledge object — extract the durable operational signals within it.

Most signals should be wiki_worthiness "ignore". Only promote signals that \
answer: "Will this still matter 6–12 months after the source's publication date?"

Prioritize: recurring patterns, workflow changes, architectural shifts, \
operational lessons, infrastructure developments, meaningful tooling/model \
developments. Avoid: transient hype, engagement bait, vanity metrics, \
low-signal commentary.

Each object MUST include:
- signal_title: concise, pattern-oriented title (e.g. "Context pipelines \
becoming the product boundary", NOT "OpenAI announcement")
- signal_type: one of "trend", "topic", "tool", "model", "howto", \
"research_eval", "infrastructure", "pricing_economics", "ignore"
- summary: 2–5 concise sentences: what the signal is, why it matters, \
operational implications
- why_it_matters: broader industry implications
- operational_relevance: implications for AI engineering, orchestration, \
evaluation, agents, automation, service automation
- service_automation_relevance: implications for chatbots, voicebots, \
customer support automation, AI-assisted support systems. If no meaningful \
relevance exists, state "No direct service automation implications identified."
- signal_strength: "low", "medium", or "high"
- time_horizon: "transient", "short_term", "medium_term", or "long_term"
- wiki_worthiness: "ignore", "weak_candidate", "review_candidate", or \
"strong_candidate"
- primary_tag: most fitting tag from TREND_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from TREND_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- suggested_destinations: routing hints as array of strings (e.g. \
["topics/", "trends/"])
- mentioned_entities: organizations, tools, models mentioned (array of strings)
- evidence_snippets: supporting source quotes for provenance (array of strings)
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

If source is NOT a roundup, return an empty array [].

Voice: clear, operational, durable. No hype.

Tag semantics: use TREND_TAGS_ALLOWLIST (same domain vocabulary as industry_trends). \
Follow TAG_ONTOLOGY_RUBRIC."""


INTERVIEW_INSIGHTS_RUBRIC = """\
## interview_insights (array of objects — ONLY when \
source_type_detection.detected_source_type == "interview_or_transcript")

Extract durable operational knowledge and meaningful viewpoints — NOT a \
chronological conversation summary. Focus on reusable insights, conceptual \
shifts, architectural observations, and strategic viewpoints.

Prioritize: operational insights, architectural patterns, workflow \
implications, implementation lessons, durable conceptual arguments, \
recurring industry themes. Avoid: conversational filler, personality-driven \
commentary, repetitive anecdotes, weak predictions.

Each object MUST include:
- insight_title: concise, reusable title (e.g. "Harness quality becoming \
more important than raw model quality", NOT "Speaker discusses models")
- insight_type: one of "topic", "trend", "model", "tool", "infrastructure", \
"orchestration", "service_automation", "privacy_security", "research_eval", \
"ignore"
- summary: 2–6 concise sentences explaining the insight, the reasoning behind \
it, and why it matters. Avoid chronological interview summaries
- why_it_matters: broader implications for AI engineering, orchestration, \
enterprise adoption, automation, service automation
- operational_relevance: implications for workflows, architecture decisions, \
orchestration strategies, evaluation approaches, automation systems, \
coding-agent workflows
- service_automation_relevance: implications for chatbots, voicebots, \
support automation, conversational reliability, human handoff systems. If no \
meaningful relevance exists, state "No direct service automation implications \
identified."
- confidence: "low", "medium", or "high"
- durability_estimate: "transient", "medium_term", or "long_term"
- wiki_worthiness: "ignore", "weak_candidate", "review_candidate", or \
"strong_candidate"
- primary_tag: most fitting tag from TOPIC_TAGS_ALLOWLIST; "" if none fit
- secondary_tag: optional second tag from TOPIC_TAGS_ALLOWLIST; "" if none
- suggested_new_tag: if a new tag is warranted, in kebab-case; "" otherwise
- suggested_destinations: routing hints (array of strings, e.g. \
["topics/", "models/"])
- mentioned_entities: organizations, tools, models mentioned (array of strings)
- contrarian_or_speculative_claims: strong predictions, contrarian takes, \
speculative claims — explicitly mark as speculative (array of strings)
- evidence_snippets: supporting source quotes for provenance (array of strings)
- value_level: "high", "medium", or "low"
- evidence_type: vendor_claim | independent_analysis | benchmark | user_report | \
implementation_case | research_result | expert_opinion | speculative_claim | mixed | unknown

If source is NOT an interview/transcript, return an empty array [].

Voice: clear, operational, synthesized. No conversational filler.

Tag semantics: use TOPIC_TAGS_ALLOWLIST (same domain vocabulary as topics). \
Follow TAG_ONTOLOGY_RUBRIC."""


def _section_regen_rubric(section_key: str) -> str:
    """Narrow rubric text for one section (avoid brittle string splits in production)."""
    fixed = {
        "summary": (
            "Usually 4–10 sentences; adapt to complexity. Core ideas only; no chronological "
            "retelling; no filler; practical clarity for an advanced practitioner."
        ),
        "accessible_overview": (
            "Usually 7–10 sentences (shorter if thin source). Plain language for an AI newcomer; "
            "no abbreviations; explain the article story gently—not a compressed expert summary."
        ),
        "key_insights": (
            "Array of at most 5 strings: actionable, strategically important, surprising, "
            "or practically useful—and non-obvious. One sentence each."
        ),
        "why_it_matters": (
            "One flow: opening half = engineering/product stakes from the source only; "
            "never mention service automation, support, voicebots, contact centers, or meeting "
            "capture there. Last 2–4 sentences only = automation/support implications if "
            "substantiated; no duplicate thesis. No unsourced macro shifts (broader industry "
            "move, signals that…). Say limited/unclear if thin. Date-anchored closing judgment."
        ),
        "limitations_and_open_questions": (
            "Weak evidence, scalability, benchmarks, assumptions, missing detail, operations, "
            "economics, privacy/security, evaluation gaps."
        ),
        "contradictions_and_skepticism": (
            "Speculative claims, hype without evidence, oversimplifications. If none, say briefly."
        ),
        "sources": "URLs/references from article or metadata; else empty array.",
    }
    return fixed.get(section_key, "")


def _build_user_prompt(
    doc: SourceDocument,
    wiki: WikiSnapshot,
    tool_types: list[str],
    howto_tags: list[str],
    impl_study_tags: list[str] | None = None,
    glossary_tags: list[str] | None = None,
    topic_tags: list[str] | None = None,
    trend_tags: list[str] | None = None,
    model_types: list[str] | None = None,
    source_type_override: str | None = None,
    extraction_budgets: dict[str, int] | None = None,
    *,
    prompt_version: str,
) -> str:
    """Assemble the user message with metadata, lists, and article body."""
    meta_lines = [
        f"prompt_version: {prompt_version}",
        f"source_id: {doc.source_id}",
        f"title: {doc.title or ''}",
        f"author: {doc.author or ''}",
        f"published_date: {doc.published_date or ''}",
        f"canonical_url: {doc.canonical_url or ''}",
    ]
    schema_hint = json.dumps(llm_output_json_schema(), indent=2)[:24_000]
    impl_tags = impl_study_tags or []
    gloss_tags = glossary_tags or []
    t_tags = topic_tags or []
    tr_tags = trend_tags or []
    m_types = model_types or []
    budgets = extraction_budgets or {}
    budget_lines_parts: list[str] = []
    budget_labels = {
        "glossary": "glossary",
        "topics": "topics",
        "how_to": "how_to",
        "industry_trends": "industry_trends",
        "tools": "tools (only if substantially discussed)",
        "foundation_models": "foundation_models (only if substantially discussed)",
        "implementation_studies": (
            "implementation_studies (only if worthiness gate passes; else [])"
        ),
        "roundup_signals": "roundup_signals",
        "interview_insights": "interview_insights",
    }
    for bk, label in budget_labels.items():
        mx = budgets.get(bk, 3)
        budget_lines_parts.append(f"- {label}: max {mx} proposals")
    budget_block = EXTRACTION_BUDGET_RUBRIC.format(budget_lines="\n".join(budget_lines_parts))
    impl_titles = wiki.implementation_study_titles[:100] if wiki.implementation_study_titles else []
    topic_titles = wiki.topic_titles[:100] if wiki.topic_titles else []
    howto_titles = wiki.howto_titles[:100] if wiki.howto_titles else []
    trend_titles = wiki.trend_titles[:100] if wiki.trend_titles else []
    trend_slugs = wiki.trend_slugs[:100] if wiki.trend_slugs else []
    blocks = [
        "## Metadata\n" + "\n".join(meta_lines),
        TEMPORAL_ANCHORING_RULE,
        budget_block,
        AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC,
        VALUE_RANKING_RUBRIC,
        EVIDENCE_TYPE_RUBRIC,
        TAG_ONTOLOGY_RUBRIC,
        PRIMARY_SECONDARY_SEMANTICS,
        "## EXISTING_GLOSSARY_TERMS\n" + "\n".join(f"- {t}" for t in wiki.glossary_terms[:150]),
        "## EXISTING_TOOL_NAMES\n" + "\n".join(f"- {t}" for t in wiki.tool_names[:200]),
        "## EXISTING_FOUNDATION_MODEL_NAMES\n"
        + "\n".join(f"- {m}" for m in wiki.foundation_model_names[:120]),
        "## EXISTING_IMPLEMENTATION_STUDY_TITLES\n" + "\n".join(f"- {t}" for t in impl_titles),
        "## EXISTING_TOPIC_TITLES\n" + "\n".join(f"- {t}" for t in topic_titles),
        "## EXISTING_HOWTO_TITLES\n" + "\n".join(f"- {t}" for t in howto_titles),
        "## EXISTING_TREND_TITLES\n" + "\n".join(f"- {t}" for t in trend_titles),
        "## EXISTING_TREND_SLUGS\n" + "\n".join(f"- {s}" for s in trend_slugs),
        "## TOOL_TYPES_ALLOWLIST\n" + "\n".join(f"- {t}" for t in tool_types),
        "## MODEL_TYPES_ALLOWLIST\n" + "\n".join(f"- {t}" for t in m_types),
        "## HOWTO_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in howto_tags),
        "## IMPL_STUDY_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in impl_tags),
        "## GLOSSARY_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in gloss_tags),
        "## TOPIC_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in t_tags),
        "## TREND_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in tr_tags),
        "## SOURCE_TYPE_DETECTION_RUBRIC\n" + SOURCE_TYPE_DETECTION_RUBRIC,
        "## SOURCE_CHAPTERS_RUBRIC\n" + SOURCE_CHAPTERS_RUBRIC,
        "## GLOSSARY_RUBRIC\n" + GLOSSARY_RUBRIC,
        "## IMPL_STUDY_RUBRIC\n" + IMPL_STUDY_RUBRIC,
        "## TOPICS_RUBRIC\n" + TOPICS_RUBRIC,
        "## HOWTOS_RUBRIC\n" + HOWTOS_RUBRIC,
        "## TRENDS_RUBRIC\n" + TRENDS_RUBRIC,
        "## TOOLS_RUBRIC\n" + TOOLS_RUBRIC,
        "## MODELS_RUBRIC\n" + MODELS_RUBRIC,
        "## ROUNDUP_SIGNALS_RUBRIC\n" + ROUNDUP_SIGNALS_RUBRIC,
        "## INTERVIEW_INSIGHTS_RUBRIC\n" + INTERVIEW_INSIGHTS_RUBRIC,
        "## JSON_SCHEMA_HINT\n" + schema_hint,
    ]
    if source_type_override:
        blocks.append(
            f"## SOURCE_TYPE_OVERRIDE\nTreat this source as: {source_type_override}. "
            "Set source_type_detection.detected_source_type accordingly. If "
            "ai_industry_roundup, populate roundup_signals; if ai_tools_roundup, "
            "follow AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC only (no roundup_signals); "
            "if interview_or_transcript, populate interview_insights."
        )
    blocks.extend(
        [
            "## ARTICLE_PLAIN_TEXT\n" + doc.plain_text,
            "## Instructions\n"
            "Output one JSON object matching the schema keys: extraction_meta, "
            "source_type_detection, source_summary, glossary, tools, foundation_models, "
            "how_to, topics, implementation_studies, industry_trends, roundup_signals, "
            "interview_insights. "
            "FIRST: fill extraction_meta (skip_recommended, skip_reason, "
            "total_candidates_considered, review_burden_estimate). "
            "If skip_recommended is true, return empty arrays for all entity types. "
            "THEN: fill source_type_detection per SOURCE_TYPE_DETECTION_RUBRIC. "
            "THEN: fill source_summary per SOURCE_CHAPTERS_RUBRIC. "
            "IF detected_source_type is ai_tools_roundup: follow "
            "AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC "
            "exactly—leave glossary, topics, how_to, industry_trends, roundup_signals, "
            "implementation_studies, interview_insights as []; extract every primary enumerated "
            "tool; the stated numeric caps under ## EXTRACTION BUDGETS do not limit tools or "
            "foundation_models for this type only. "
            "ELSE: fill glossary, tools, foundation_models, how_to, topics, "
            "implementation_studies, industry_trends per their rubrics and RESPECT extraction "
            "budgets. Every proposal MUST have a value_level field. "
            "For glossary, each related_terms entry MUST match a sibling ``term`` or "
            "EXISTING_GLOSSARY_TERMS exactly (see GLOSSARY_RUBRIC; avoid abbreviations when the "
            "full form is canonical). "
            "IF detected_source_type is ai_industry_roundup, ALSO fill roundup_signals per "
            "ROUNDUP_SIGNALS_RUBRIC. "
            "IF detected_source_type is interview_or_transcript, ALSO fill interview_insights per "
            "INTERVIEW_INSIGHTS_RUBRIC. "
            "Use empty arrays when a category does not apply.",
        ]
    )
    return "\n\n".join(blocks)


def _parse_json_content(raw: str) -> dict[str, Any]:
    """Parse model string content as JSON object."""
    return json.loads(raw)


def _truncate_plain_text(plain: str, max_chars: int | None) -> str:
    if max_chars is None or len(plain) <= max_chars:
        return plain
    return plain[:max_chars] + "\n[TRUNCATED]"


class OpenAIIngestionProvider(IngestionProvider):
    """OpenAI Chat Completions with structured JSON (schema validate locally)."""

    def __init__(self, client: OpenAI | None = None) -> None:
        """Initialize with optional shared client (for tests)."""
        self._client = client or OpenAI()

    @property
    def provider_name(self) -> str:
        """Return ``openai``."""
        return "openai"

    def analyze_classification(
        self,
        *,
        document: SourceDocument,
        wiki: WikiSnapshot,
        tool_types_allowlist: list[str],
        howto_tags_allowlist: list[str],
        impl_study_tags_allowlist: list[str] | None = None,
        glossary_tags_allowlist: list[str] | None = None,
        topic_tags_allowlist: list[str] | None = None,
        trend_tags_allowlist: list[str] | None = None,
        model_types_allowlist: list[str] | None = None,
        source_type_override: str | None = None,
        extraction_budgets: dict[str, int] | None = None,
        model: str,
        prompt_version: str,
        max_retries: int = 3,
    ) -> tuple[LlmClassificationOutput, dict[str, Any]]:
        """Call OpenAI and validate against :class:`LlmClassificationOutput`."""
        user_prompt = _build_user_prompt(
            document,
            wiki,
            tool_types_allowlist,
            howto_tags_allowlist,
            impl_study_tags_allowlist,
            glossary_tags_allowlist,
            topic_tags_allowlist,
            trend_tags_allowlist,
            model_types=model_types_allowlist,
            source_type_override=source_type_override,
            extraction_budgets=extraction_budgets,
            prompt_version=prompt_version or PROMPT_VERSION,
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + " Respond with one JSON object only."},
            {"role": "user", "content": user_prompt},
        ]
        # Prefer json_schema when the API accepts it; fall back to json_object.
        schema = llm_output_json_schema()
        response_formats: list[dict[str, Any] | None] = [
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "ingest_classification",
                    "schema": schema,
                    "strict": False,
                },
            },
            {"type": "json_object"},
            None,
        ]

        last_error: str | None = None
        max_attempts = max(3, max_retries) * 2
        fmt_index = 0
        for attempt in range(max_attempts):
            response_format = response_formats[min(fmt_index, len(response_formats) - 1)]
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "timeout": 120.0,
                }
                if response_format is not None:
                    kwargs["response_format"] = response_format
                completion = self._client.chat.completions.create(**kwargs)
                choice = completion.choices[0]
                raw = choice.message.content or ""
                data = _parse_json_content(raw)
                parsed = LlmClassificationOutput.model_validate(data)
                meta: dict[str, Any] = {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                }
                return parsed, meta
            except json.JSONDecodeError as exc:
                last_error = f"json: {exc}"
                logger.warning("JSON decode failed: %s", last_error)
                time.sleep(0.5 * (attempt + 1))
            except ValidationError as exc:
                last_error = f"validate: {exc}"
                logger.warning("Schema validation failed: %s", last_error)
                repair = (
                    "\n\n## Previous output failed validation\n"
                    f"{str(exc)[:8000]}\n"
                    "Return corrected JSON only."
                )
                messages = [
                    messages[0],
                    {"role": "user", "content": user_prompt + repair},
                ]
                time.sleep(0.3 * (attempt + 1))
            except (RateLimitError, APITimeoutError, APIError) as exc:
                last_error = str(exc)
                logger.warning(
                    "OpenAI HTTP error (format=%s): %s",
                    fmt_index,
                    last_error,
                )
                if isinstance(exc, RateLimitError) or "429" in last_error:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    fmt_index += 1
        raise RuntimeError(f"OpenAI classification failed: {last_error}")

    def regenerate_source_section(
        self,
        *,
        document: SourceDocument,
        section_key: str,
        current_value: str | list[str] | None,
        reviewer_instruction: str | None,
        model: str,
        prompt_version: str,
        max_plain_text_chars: int | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Regenerate one ``source_summary`` field via a narrow JSON completion."""
        if section_key not in REGENERATABLE_SOURCE_SECTION_KEYS:
            raise ValueError(f"Unsupported section_key: {section_key}")
        rubric = _section_regen_rubric(section_key)
        body = _truncate_plain_text(document.plain_text, max_plain_text_chars)
        current_json = json.dumps(current_value, ensure_ascii=False)
        user_blocks = [
            f"prompt_version: {prompt_version or PROMPT_VERSION}",
            f"source_id: {document.source_id}",
            f"SECTION_TO_REGENERATE: {section_key}",
            f"SECTION_RUBRIC:\n{rubric}",
            "## REVIEWER_NOTE\n"
            + (reviewer_instruction.strip() if reviewer_instruction else "(none)"),
            "## CURRENT_DRAFT_JSON\n" + current_json,
            "## ARTICLE_PLAIN_TEXT\n" + body,
            "## Instructions\n"
            'Return one JSON object: {"section_key": "<same key>", "content": <string OR array '
            "of strings>}. For key_insights and sources, content MUST be an array of strings. "
            "For all other keys, content MUST be a single string.",
        ]
        user_prompt = "\n\n".join(user_blocks)
        regen_schema = SectionRegenerateOutput.model_json_schema()
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + " Respond with one JSON object only; keys section_key and content only.",
            },
            {"role": "user", "content": user_prompt},
        ]
        response_formats: list[dict[str, Any] | None] = [
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "source_section_regen",
                    "schema": regen_schema,
                    "strict": False,
                },
            },
            {"type": "json_object"},
            None,
        ]
        last_error: str | None = None
        max_attempts = max(2, max_retries) * 2
        fmt_index = 0
        for attempt in range(max_attempts):
            response_format = response_formats[min(fmt_index, len(response_formats) - 1)]
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "timeout": 90.0,
                }
                if response_format is not None:
                    kwargs["response_format"] = response_format
                completion = self._client.chat.completions.create(**kwargs)
                raw = completion.choices[0].message.content or ""
                data = _parse_json_content(raw)
                out = SectionRegenerateOutput.model_validate(data)
                if out.section_key != section_key:
                    raise ValueError(
                        f"mismatched section_key: {out.section_key!r} != {section_key!r}"
                    )
                content: str | list[str]
                if section_key in ("key_insights", "sources"):
                    if isinstance(out.content, str):
                        lines = [ln.strip() for ln in out.content.splitlines() if ln.strip()]
                        content = lines or (
                            [] if not out.content.strip() else [out.content.strip()]
                        )
                    else:
                        content = [str(x).strip() for x in out.content if str(x).strip()]
                    if section_key == "key_insights":
                        content = content[:5]
                else:
                    if isinstance(out.content, list):
                        content = "\n".join(str(x) for x in out.content)
                    else:
                        content = str(out.content)
                meta: dict[str, Any] = {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                    "prompt_version": prompt_version or PROMPT_VERSION,
                }
                return {"section_key": section_key, "content": content}, meta
            except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
                last_error = str(exc)
                logger.warning("Section regen parse/validate failed: %s", last_error)
                repair = (
                    "\n\n## Previous output failed\n"
                    f"{str(exc)[:4000]}\n"
                    "Return corrected JSON with keys section_key and content only."
                )
                messages = [
                    messages[0],
                    {"role": "user", "content": user_prompt + repair},
                ]
                time.sleep(0.3 * (attempt + 1))
            except (RateLimitError, APITimeoutError, APIError) as exc:
                last_error = str(exc)
                logger.warning("OpenAI section regen HTTP error: %s", last_error)
                if isinstance(exc, RateLimitError) or "429" in last_error:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    fmt_index += 1
        raise RuntimeError(f"OpenAI section regeneration failed: {last_error}")

    def regenerate_proposal(
        self,
        *,
        entity_key: str,
        document: SourceDocument,
        current_item: dict[str, Any],
        new_title: str,
        reviewer_instruction: str | None,
        context_sections: dict[str, str],
        model: str,
        prompt_version: str,
        max_plain_text_chars: int | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Regenerate one proposal under a reviewer-supplied title (any entity)."""
        return run_proposal_regeneration(
            self._client,
            entity_key=entity_key,
            document=document,
            current_item=current_item,
            new_title=new_title,
            reviewer_instruction=reviewer_instruction,
            context_sections=context_sections,
            model=model,
            prompt_version=prompt_version,
            max_plain_text_chars=max_plain_text_chars,
            max_retries=max_retries,
        )

    def regenerate_topic_proposal(
        self,
        *,
        document: SourceDocument,
        current_topic: dict[str, Any],
        new_title: str,
        reviewer_instruction: str | None,
        topic_tags_allowlist: list[str],
        existing_topic_slugs: list[str],
        model: str,
        prompt_version: str,
        max_plain_text_chars: int | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Regenerate one topic proposal under a reviewer-supplied title."""
        slug_lines = "\n".join(f"- {s}" for s in existing_topic_slugs[:120] if str(s).strip())
        tag_lines = "\n".join(f"- {t}" for t in topic_tags_allowlist if str(t).strip())
        context = {
            "EXISTING_TOPIC_SLUGS": slug_lines or "(none)",
            "TOPIC_TAGS_ALLOWLIST": tag_lines or "(none)",
        }
        return self.regenerate_proposal(
            entity_key="topic",
            document=document,
            current_item=current_topic,
            new_title=new_title,
            reviewer_instruction=reviewer_instruction,
            context_sections=context,
            model=model,
            prompt_version=prompt_version,
            max_plain_text_chars=max_plain_text_chars,
            max_retries=max_retries,
        )

    def suggest_domain_review_tag(
        self,
        *,
        entity_label: str,
        context_summary: str,
        allowlist: list[str],
        model: str,
        prompt_version: str,
        max_retries: int = 2,
    ) -> tuple[str, dict[str, Any]]:
        """Return one kebab-case tag not in allowlist, or ""."""
        allow_norms = {normalize_tag(str(t)) for t in allowlist if str(t).strip()}
        lines = "\n".join(f"- {normalize_tag(str(t))}" for t in allowlist if str(t).strip())
        user_prompt = "\n\n".join(
            [
                f"prompt_version: {prompt_version or PROMPT_VERSION}",
                "## TASK",
                "Propose ONE new wiki routing tag in kebab-case for this entity, OR return "
                "empty suggested_tag if an entry in ALLOWLIST is a reasonable fit (the reviewer "
                "will map manually). Do NOT output any tag that appears in ALLOWLIST.",
                "## ENTITY / TITLE\n" + entity_label.strip(),
                "## SUMMARY / CONTEXT\n" + (context_summary.strip() or "(none)"),
                "## ALLOWLIST (do not repeat any of these)\n" + (lines or "(empty)"),
                "## Instructions\n"
                'Return JSON only: {"suggested_tag": "<kebab-case or empty>"}. '
                "Distinct, recurring, broad enough for many future wiki entries under this domain. "
                "No article-specific or vendor-marketing slugs.",
            ]
        )
        schema = GlossaryTagSuggestOutput.model_json_schema()
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + " Respond with one JSON object only; keys as specified in user message.",
            },
            {"role": "user", "content": user_prompt},
        ]
        response_formats: list[dict[str, Any] | None] = [
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "domain_tag_suggest",
                    "schema": schema,
                    "strict": False,
                },
            },
            {"type": "json_object"},
            None,
        ]
        last_error: str | None = None
        max_attempts = max(2, max_retries) * 2
        fmt_index = 0
        for attempt in range(max_attempts):
            response_format = response_formats[min(fmt_index, len(response_formats) - 1)]
            try:
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "timeout": 60.0,
                }
                if response_format is not None:
                    kwargs["response_format"] = response_format
                completion = self._client.chat.completions.create(**kwargs)
                raw = completion.choices[0].message.content or ""
                data = _parse_json_content(raw)
                out = GlossaryTagSuggestOutput.model_validate(data)
                sug = normalize_tag(str(out.suggested_tag or ""))
                if sug and sug in allow_norms:
                    sug = ""
                meta: dict[str, Any] = {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                    "prompt_version": prompt_version or PROMPT_VERSION,
                }
                return sug, meta
            except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
                last_error = str(exc)
                logger.warning("Domain tag suggest parse failed: %s", last_error)
                messages = [
                    messages[0],
                    {
                        "role": "user",
                        "content": user_prompt
                        + "\n\n## Previous output invalid\n"
                        + str(exc)[:2000]
                        + '\nReturn {"suggested_tag": ""} or one valid kebab-case tag.',
                    },
                ]
                time.sleep(0.3 * (attempt + 1))
            except (RateLimitError, APITimeoutError, APIError) as exc:
                last_error = str(exc)
                logger.warning("Domain tag suggest HTTP error: %s", last_error)
                if isinstance(exc, RateLimitError) or "429" in last_error:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    fmt_index += 1
        logger.warning("Domain tag suggest failed: %s", last_error)
        return "", {"error": last_error or "unknown"}
