"""OpenAI chat completions provider for ingestion classification."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError
from pydantic import ValidationError

from src.ingest_review.canonical_titles import build_canonical_title_prompt_blocks
from src.ingest_review.extract import SourceDocument
from src.ingest_review.proposal_regen_provider import run_proposal_regeneration
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import (
    PROMPT_VERSION,
    REGENERATABLE_SOURCE_SECTION_KEYS,
    GlossaryTagSuggestOutput,
    LlmClassificationOutput,
    SectionRegenerateOutput,
    llm_output_json_schema_for_classification,
)
from src.ingest_review.tags import normalize_tag, normalize_tag_list
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
exhaustive extraction, and high-value proposals over many medium-value proposals. \
Prefer ontology compression: the smallest durable set of abstractions that preserves value.

Every proposal MUST include a value_level field: "high", "medium", or "low".
- high: durable, operationally relevant, novel to the wiki, strong evidence, \
likely reused across multiple future sources
- medium: useful but not essential, moderate evidence, incremental contribution
- low: marginal value, weak evidence, narrow applicability, or already well-covered

Always fill source_evidence_profile with the dominant evidence basis for THIS SOURCE \
(not per topic/term). See SOURCE_EVIDENCE_PROFILE_RUBRIC. Per-proposal evidence_type is \
**optional** — include only when that extraction's basis differs from the source default.

Prefer fewer high-value proposals over many medium/low proposals.

For tags and types: follow TAG_ONTOLOGY_RUBRIC, REGISTRY_TYPES_SEMANTICS, and each \
entity rubric's tag/type addendum. Do not invent source-level tags.
For tools: proposed_types MUST be a subset of TOOL_TYPES_ALLOWLIST (at most 2 unless \
genuinely multi-category); first type = primary category, second = optional adjacent role.
For foundation_models: proposed_types MUST be a subset of MODEL_TYPES_ALLOWLIST (at most 2 \
unless genuinely multi-category); first = deployment/openness class, second = capability focus.
Before proposing glossary, topics, how_to, or implementation_studies, apply \
ABSTRACTION_SELECTION_RUBRIC to choose the most durable representation per knowledge unit. \
When filling entity arrays, apply COMPRESSION_PRESSURE_RUBRIC — prefer one strong proposal \
over several partially redundant proposals. Apply MINIMUM_NOVELTY_THRESHOLD_RUBRIC — omit \
familiar concepts unless the source adds genuinely new operational insight.
For implementation_studies: follow IMPLEMENTATION_STUDY_WORTHINESS GATE in IMPL_STUDY_RUBRIC; \
if the gate fails, return implementation_studies: [] and route per ABSTRACTION_SELECTION_RUBRIC \
(topics, how_to, industry_trends, roundup_signals, or interview_insights).

Always fill extraction_meta with skip_recommended, skip_reason, total_candidates_considered, \
and review_burden_estimate. If the article contains no durable, wiki-worthy knowledge, \
set skip_recommended=true and skip_reason explaining why; return empty arrays for all \
entity types. Do NOT force low-value extractions—EXCEPT for ai_tools_roundup and \
how_to_roundup: skip_recommended MUST be false; extract every primary list item for human \
review (use value_level \"low\" for thin entries).

Always fill source_evidence_profile and source_type_detection. \
Set source_type_detection with the detected source type, confidence, and reasoning. \
If the source is an ai_industry_roundup, also populate roundup_signals. \
If the source is an ai_tools_roundup, extract ONLY tools and foundation_models per \
AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC; leave roundup_signals empty []. \
If the source is how_to_roundup, extract ONLY how_to per HOW_TO_ROUNDUP_EXTRACTION_RUBRIC. \
If the source is an interview_or_transcript, also populate interview_insights. \
For page titles and terms, apply PAGE_MATCHING_RUBRIC before reusing any ``CANONICAL_*`` \
entry; follow TITLE_CANONICALIZATION_RUBRIC. Append/create wiki routing is **not** part \
of this step. \
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
Return empty arrays for all entity types. Do NOT force low-value extractions—EXCEPT \
ai_tools_roundup and how_to_roundup: skip_recommended MUST be false; completeness \
over curation."""


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
(or clearly standalone reviewed model); omit passing name-drops. Each entry MUST have a \
non-empty model_name matching the article (e.g. Mercury 2, Kimi K2.5).
- The numeric max lines under ## EXTRACTION BUDGETS do NOT cap tools or foundation_models for \
this source type; completeness for listed tools beats those limits. Treat all other proposal \
arrays as max zero (empty).
- extraction_meta.skip_recommended MUST be false. Include every primary enumerated app/tool even \
if value_level is \"low\"—the reviewer will reject unwanted items."""


HOW_TO_ROUNDUP_EXTRACTION_RUBRIC = """\
## HOW_TO_ROUNDUP_EXTRACTION (ONLY when detected_source_type == "how_to_roundup")

When the source is how_to_roundup:
- glossary, topics, tools, foundation_models, industry_trends, roundup_signals, \
implementation_studies, interview_insights MUST each be [] (no exceptions).
- how_to: one HowToProposal per distinct PRIMARY enumerated practice, technique, workflow, or \
tip the article gives substantive coverage to—match the article count when it claims e.g. \
\"N ways\" or \"N practices\" and each item is a real entry.
- Follow HOWTOS_RUBRIC for field quality (question_title as wiki page noun phrase, etc.).
- The numeric max lines under ## EXTRACTION BUDGETS do NOT cap how_to for this source type; \
completeness for listed practices beats those limits.
- extraction_meta.skip_recommended MUST be false. Include every primary enumerated practice even \
if value_level is \"low\"—the reviewer will reject unwanted items."""


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


ABSTRACTION_SELECTION_RUBRIC = """\
## ABSTRACTION SELECTION (applies before glossary, topics, how_to, implementation_studies)

Before extracting, for each distinct knowledge unit in the source, ask: \
"What is the MOST durable representation of this knowledge?"

Prefer (highest to lowest reuse):
1. **topics** — operational patterns, workflow principles, architectural concepts, \
AI-native design patterns that accumulate knowledge across many future sources
2. **how_to** — reusable procedures with org-agnostic implementation substance
3. **glossary** — narrow established primitives only (dictionary-worthy industry terms)
4. **implementation_studies** — only when IMPLEMENTATION_STUDY_WORTHINESS GATE passes
5. **industry_trends** — macro industry shifts with evidence, not article-local narratives

Deprioritize as primary extractions:
- Article-local terminology, branded phrasing, product slogans
- Generic dictionary or compliance vocabulary (e.g. Benchmark, Passkey, WCAG) unless \
operationally distinctive for AI engineering in this wiki's scope
- Implementation trivia, one-off stack choices, article narrative compression
- "Important concept" that is not a wiki-worthy durable abstraction

Tie-breaker when glossary, topic, and how_to all seem plausible — choose the representation with:
1. Highest reuse potential across future sources (not just this article)
2. Strongest operational abstraction (pattern > procedure > definition)
3. Lowest duplication risk vs EXISTING_TOPIC_TITLES, EXISTING_HOWTO_TITLES, \
EXISTING_GLOSSARY_TERMS, and CANONICAL_* lists

Default cardinality: **one primary entity type per knowledge unit**. Do NOT emit the same \
substance as glossary + topic + how_to. Prefer omitting over duplicating across layers.

Allowed dual extraction (rare): only when layers are **complementary**, not redundant — e.g. \
a glossary primitive ("Harness") plus a broader topics entry ("Agent Harness Engineering") \
when both add distinct durable value and field overlap is minimal.

Decision shortcuts:
- Reusable procedure, steps, org-agnostic → how_to
- Durable pattern/architecture/workflow design, no named-org deployment → topics
- Established primitive definition only, no broader pattern → glossary \
(after GLOSSARY-WORTHINESS GATE)
- Named org + deployment evidence → implementation_studies (after worthiness gate)
- Industry-wide shift, not one org → industry_trends
- Weak roundup signal → roundup_signals; interview takeaway → interview_insights

Worked negatives:
- For glossary hard exclusions and named negatives (Benchmark, Knowledge Management, \
Passkey, WCAG), apply GLOSSARY HARD EXCLUSIONS in GLOSSARY_RUBRIC.
- How-to when durable knowledge is a workflow pattern: e.g. Agentic Personal Knowledge \
Management → topics (operational architecture), not a narrow how_to

After layer selection, apply the matching entity rubric, MINIMUM_NOVELTY_THRESHOLD_RUBRIC, \
COMPRESSION_PRESSURE_RUBRIC, GLOSSARY-WORTHINESS GATE, IMPLEMENTATION_STUDY_WORTHINESS GATE, \
TITLE_CANONICALIZATION_RUBRIC, and extraction budgets."""


COMPRESSION_PRESSURE_RUBRIC = """\
## COMPRESSION PRESSURE (applies across all entity arrays)

If multiple extracted entities would describe substantially overlapping knowledge, prefer:
- **one stronger proposal** over several partially redundant proposals

This reduces:
- glossary/topic duplication (same substance at different abstraction layers)
- repeated operational explanations across proposals
- article-shaped ontology (many near-duplicate entries)

When overlapping candidates compete:
- Keep the proposal with the highest value_level; if tied, the strongest operational \
abstraction and lowest duplication risk vs EXISTING_* / CANONICAL_* lists
- Prefer the entity type already chosen by ABSTRACTION_SELECTION_RUBRIC
- Fold a secondary angle into key_points, operational_insight, knowledge_summary, or \
extended_explanation of the survivor — do not emit a second proposal for the same substance
- Merge near-duplicate titles per TITLE_CANONICALIZATION_RUBRIC rather than splitting \
into micro-variants

Prefer omitting marginal overlap over filling extraction budgets with redundant entries. \
Semantic compression beats exhaustive extraction."""


MINIMUM_NOVELTY_THRESHOLD_RUBRIC = """\
## MINIMUM NOVELTY THRESHOLD (applies to all proposals)

Optimize for **novel** durable knowledge, not merely **correct** restatements of what \
experienced AI practitioners already know.

Do NOT extract concepts that are already broadly familiar to experienced AI practitioners \
unless the source adds at least one of:
- a new **operational framing** — how to run, evaluate, or operate systems differently in practice
- a new **architecture pattern** — structural design insight beyond a textbook recap
- a new **deployment implication** — production, scale, cost, reliability, or safety in practice
- a new **governance implication** — policy, compliance, risk, or human oversight in practice
- a new **systems-level interpretation** — how components interact end-to-end

If the extraction would only restate common practitioner knowledge, a standard definition, \
or article compression of widely known ideas with no source-specific additive insight, \
**omit it**. value_level "low" is not an excuse to emit familiar filler.

Tie to value_level:
- **high** — genuine novelty to the wiki or a fresh angle clearly grounded in the source
- **medium** — clear incremental insight beyond common knowledge; not a dictionary recap
- **low** — marginal; prefer omitting when novelty threshold is not met"""


SOURCE_EVIDENCE_PROFILE_RUBRIC = """\
## source_evidence_profile (required JSON subtree)

Classify the dominant evidence basis for the SOURCE as a whole — who is speaking and \
how claims are supported across the article. This is **not** a property of individual \
topics, glossary terms, or tools.

Fields:
- primary_evidence_type: exactly one of vendor_claim, independent_analysis, benchmark, \
user_report, implementation_case, research_result, expert_opinion, speculative_claim, \
mixed, unknown
- reasoning: array of 1–3 short strings explaining why this source fits that type

Evidence type definitions:
- vendor_claim — the company/vendor/provider discussed is the source of the claims \
(e.g. their blog, product announcement, press release, demo video).
- independent_analysis — independent writer, analyst, or third-party publication — not \
the vendor speaking for their own product.
- benchmark — the source depends mainly on benchmark numbers, evals, leaderboards.
- user_report — practitioner anecdotes, forum/social/blog experience reports dominate.
- implementation_case — concrete how-it-was-built / deployment descriptions dominate.
- research_result — grounded in paper, formal experiment, or research artifact.
- expert_opinion — named expert judgment or strategic interpretation dominates.
- speculative_claim — predictions or weakly evidenced forward-looking claims dominate.
- mixed — several evidence types matter equally; no single one dominates.
- unknown — unclear from the source.

Per-proposal evidence_type (optional on each proposal object):
- **Omit** evidence_type when the proposal inherits the source default.
- **Include** evidence_type only when this specific extraction clearly differs \
(e.g. vendor post with an independent benchmark section extracted as its own proposal).

Do NOT repeat the source default on every proposal."""


TAG_ONTOLOGY_RUBRIC = """\
## TAG ONTOLOGY (proposal-level routing — NOT source tags)

Tags classify each PROPOSAL for wiki routing and aggregation. They are NOT article labels, \
marketing phrases, or title echoes.

Mandatory procedure for every tagged proposal:
1. Read the entity's TAGS or TYPES allowlist section in this prompt.
2. Set proposed_tags to zero or more EXACT allowlist strings (copy verbatim). Quality over \
quantity: each tag must be clearly warranted — no synonyms, no title echoes, no weak fits.
3. Default to 1–2 proposed_tags when routing is clear; use 3+ only when each tag is \
distinct and necessary. Hard maximum: 5 allowlist tags per proposal.
4. NEVER put invented slugs, abbreviations, or off-list labels in proposed_tags.
5. Set suggested_new_tags only when the allowlist lacks a reasonable match after checking \
near-synonyms (e.g. agent-workflow vs agentic-workflows). Each entry must pass the new-tag \
gate below. Leave suggested_new_tags [] when allowlist tags suffice.

New-tag gate — each suggested_new_tags entry must be: distinct, recurring, broad enough for \
many future sources, and entity-appropriate. Verify no close allowlist match exists first.

Anti-patterns (never use as tags): article-specific slugs, launch/event names, vendor \
marketing ("enterprise-ready"), quality adjectives ("useful", "important"), title fragments \
("gpt-5-4-launch", "openai-flywheel"). Use kebab-case for suggested_new_tags entries.

Prefer reusing existing allowlist tags whenever reasonably possible. Leave proposed_tags [] \
when nothing fits and you are not confident in a new tag."""


REGISTRY_TYPES_SEMANTICS = """\
## REGISTRY TYPES (tools and foundation models only)

Tools and foundation models use proposed_types (not proposed_tags):
- proposed_types: zero or more EXACT strings from TOOL_TYPES_ALLOWLIST or MODEL_TYPES_ALLOWLIST.
- Same quality rules as proposed_tags: each type must fit well; max 5; no ordering hierarchy.
- suggested_new_type: single kebab-case candidate when the type registry lacks a fit (legacy \
field); prefer filling proposed_types from the allowlist when possible."""


TITLE_CANONICALIZATION_RUBRIC = """\
## Canonical titles (avoid fragmentation)

Before inventing a new page title, term, or slug, read the entity's ``CANONICAL_*`` list \
in this prompt (wiki index + approved prior reviews). Canonical lists are **candidates \
to evaluate**, not a menu to pick from.

- Reuse an existing canonical **title verbatim** (and listed slug when provided) **only** \
on a **strong page match** per PAGE_MATCHING_RUBRIC.
- Adjacent domain, shared security theme, shared tag, or keyword overlap ≠ reuse.
- When in doubt, invent a **new** broad stable title (or omit the proposal).
- Do **not** output near-synonyms or rewordings for the **same** knowledge unit (e.g. \
"Harness decay" vs "Harness Decay" when both mean the same primitive).
- If no canonical entry is a strong match, invent one broad, stable title per the entity rubric.
- Within one response, reuse the **same** title for the same concept across multiple \
extractions — do not create two proposals that differ only in wording.

Wiki append vs create-new-page routing is **out of scope** for this extraction step."""


PAGE_MATCHING_RUBRIC = """\
## PAGE MATCHING (applies before reusing any CANONICAL_* title or slug)

Existing-page reuse is good only when the new source contributes to the **same durable \
knowledge object**. Prefer reuse over unnecessary new pages — but only when reuse keeps \
the page boundary conceptually clean.

### Four overlap types (only #1 is title/slug reuse)

1. **Strong page match** — same core concept → set ``topic_title`` / ``term`` / \
``question_title`` / ``trend_title`` / ``name`` / ``model_name`` to the **exact** canonical \
spelling (and slug when applicable).
2. **Weak related concept** — put in ``related_topics`` / ``related_terms`` / \
``related_howtos`` / ``related_trends`` / ``related_tools`` / ``related_models`` only; \
**never** as the primary title/slug.
3. **Background association** — usually omit.
4. **Tag/category overlap** — ``proposed_tags`` only; never page reuse.

### Strong match checklist (most must be true)

- The source discusses the **same core concept**, not just an adjacent domain.
- The canonical title would be a **natural title** for this extracted knowledge.
- The source would add a **meaningful paragraph**, caveat, example, or evidence point.
- A reader opening that page **would expect** this new material there.
- The overlap is **central** to the extraction, not peripheral.
- Reuse would **not blur** the page boundary.

If these are not met, do **not** reuse the canonical title — use a new title or omit.

### Negative examples (weak match — do NOT reuse title)

- Cybersecurity / trusted access / zero-trust article → "Privacy Controls for AI Products" \
unless the source explicitly discusses privacy controls **inside AI products**.
- General account security / passkeys → "AI Governance" unless the source connects \
account security to AI governance workflows.
- Generic accessibility article → "Conversational AI" unless the source is about \
conversational interface accessibility.
- Local open-source model deployment → "AI Infrastructure" when the knowledge is really \
local coding-agent workflow (use a new topic or how-to instead).

These may share tags (e.g. ai-security) or appear in ``related_topics`` when weakly linked \
and explicitly supported by the source — not as the primary page title.

### Outcomes (classification expresses reuse via title/slug, not suggested_action)

- **Reuse existing page:** strong match → exact canonical title (+ slug).
- **New page:** durable valuable knowledge, no strong match → new broad stable title/slug.
- **No proposal:** weak, generic, or only loosely related — omit or value_level low.

### related_* vs primary title

``related_topics`` / ``related_terms`` / etc. are for **weak** cross-links only. \
Do **not** pick ``topic_slug`` because a related page exists in the wiki. \
Prefer ``[]`` over weak wiki slugs.

If ``match_candidates`` is ever emitted (regen/other steps): include **strong matches only**; \
leave empty when confidence is low."""


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
- source_evidence_profile should be implementation_case or mixed when deployment evidence \
dominates; use per-proposal evidence_type override only when a slice clearly differs
- Demote weak extractions with low confidence and value_level "low" when evidence is thin

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

ROUTING — when the worthiness gate fails, route per ABSTRACTION_SELECTION_RUBRIC:
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
- proposed_tags: allowlist tags from IMPL_STUDY_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- confidence: 0.0–1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

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

GLOSSARY HARD EXCLUSIONS — do NOT extract glossary entries for:
- **Generic business vocabulary** — e.g. knowledge management, flywheel, ecosystem, \
platform strategy, innovation loop, transformation journey, management terminology
- **Generic software terms** — e.g. passkey, API, database, authentication (unless the \
source teaches a genuinely new operational framing for AI systems)
- **Mature web standards** — e.g. WCAG, HTTP, OAuth (dictionary-level; omit unless the \
source adds genuinely new AI-chatbot or service-automation operational framing)
- **Basic AI terminology** — e.g. LLM, prompt, RAG, fine-tuning (widely known; omit \
unless the source reframes them operationally for this wiki)
- **Widely known concepts** — e.g. benchmark, evaluation in the generic sense (omit \
unless the source adds genuinely new operational framing beyond a textbook definition)

**Named negatives (default omit):** Benchmark, Knowledge Management, Passkey, WCAG — \
only propose if the source teaches operationally distinctive AI-engineering usage you \
could not get from a dictionary, standard doc, or common practitioner knowledge.

Glossary entries should feel:
- **Ontology-worthy** — a stable wiki primitive, not article vocabulary
- **Reusable across many future sources** — not one-article context
- **Operationally differentiating** — changes how a practitioner designs, evaluates, or \
operates AI systems

Criteria 1–5 still apply; if any is "no" **or** a hard exclusion matches, omit the term.

CRITICAL: Only propose ESTABLISHED industry terms that already exist in \
professional usage and are verifiable via a web search. Do NOT propose \
neologisms coined by the article author, ad-hoc phrases, or terms invented \
for this specific article. If in doubt, omit the term.

GLOSSARY EXTRACTION BOUNDARIES — see GLOSSARY HARD EXCLUSIONS above. The glossary is \
not a dictionary of common terms; it is for durable conceptual primitives and recurring \
operational AI concepts only. Do NOT propose marketing abstractions, temporary framing, \
product slogans, or company-specific narratives.

Apply ABSTRACTION_SELECTION_RUBRIC before proposing any term. Glossary is the \
**last** choice for durable knowledge, not the default — use only for narrow \
established primitives after layer selection.

Page matching: reuse an existing ``term`` from CANONICAL_GLOSSARY_TERMS / EXISTING_GLOSSARY_TERMS \
**only** on a strong page match (PAGE_MATCHING_RUBRIC). Weakly related concepts belong in \
``related_terms``, not as the primary ``term``.

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
- related_terms: **weak** cross-links only — each string MUST use the **exact same spelling \
and wording** as the ``term`` field of another object in **this** ``glossary`` array when \
that concept is also proposed, OR as a term from **EXISTING_GLOSSARY_TERMS** when weakly \
related. Do **not** use ``related_terms`` to substitute for choosing the primary ``term``. \
Do **not** invent alternate surface forms. If no valid weak link applies, use ``[]``.
- proposed_tags: allowlist tags from GLOSSARY_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- confidence: 0.0-1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

Voice: clear, practical, accessible. Define for a senior practitioner, \
not an academic. Prefer operational understanding over theoretical precision.

Tag semantics (GLOSSARY_TAGS_ALLOWLIST): broad durable domain for routing — \
not article-specific labels. Follow TAG_ONTOLOGY_RUBRIC."""


TOPICS_RUBRIC = """\
## topics (array of objects — topic contributions)

Extract reusable operational knowledge units, NOT article summaries.
Each contribution answers: "What does this article teach about [concept X] \
that is useful long-term?"

Only extract topics that are: reusable across multiple contexts, operationally \
relevant, likely to reappear, conceptually stable, and broad enough to \
aggregate knowledge from many future sources.

Page matching: ``topic_title`` / ``topic_slug`` reuse a CANONICAL_TOPIC entry **only** on a \
strong page match (PAGE_MATCHING_RUBRIC). If overlap is weak or adjacent, invent a **new** \
slug/title — do not absorb into a loosely related wiki page.

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
- related_topics: **weak** cross-links to other topic pages only — each string MUST be a \
``topic_slug`` from another object in **this** ``topics`` array and/or the wiki index when \
the source explicitly supports a weak relationship. Do **NOT** use ``related_topics`` to \
choose ``topic_slug``. Do **NOT** put TOPIC_TAGS_ALLOWLIST entries here (e.g. ai-engineering, \
knowledge-management). Prefer ``[]`` over forcing a weak wiki slug. Do **not** repeat this \
object's own ``topic_slug``.
- proposed_tags: allowlist tags from TOPIC_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- confidence: 0.0-1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

Avoid: article-specific framing, ultra-narrow topics, hype-driven \
fragmentation, one-off concepts, duplicate existing topics.

Voice: clear, operational, synthesized. Write as reusable knowledge, \
not as article commentary.

Tag semantics (TOPIC_TAGS_ALLOWLIST): strategic/operational domain for the \
knowledge unit — not the article title. Follow TAG_ONTOLOGY_RUBRIC.

related_topics vs tags: ``related_topics`` = weak wiki topic slugs; ``proposed_tags`` = \
allowlist routing tags only.

Layer selection: see ABSTRACTION_SELECTION_RUBRIC. Page matching: see PAGE_MATCHING_RUBRIC."""


HOWTOS_RUBRIC = """\
## how_to (array of objects — how-to proposals)

Extract procedural/implementation knowledge, NOT theoretical summaries. \
Only extract how-tos where the source provides enough implementation \
substance — not vague advice.

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

Compare the **core procedure** to **EXISTING_HOWTO_TITLES**; reuse a canonical how-to title \
**only** on a strong page match (PAGE_MATCHING_RUBRIC). Prefer **fewer, broader** how-tos. \
If the source only supports a narrow edge case with no reusable procedure, omit the proposal \
or fold substance into a broader how-to title per TITLE_CANONICALIZATION_RUBRIC.

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
- related_howtos: **weak** cross-references to other how-to slugs only; not a substitute for \
``question_title`` (list of strings)
- proposed_tags: allowlist tags from HOWTO_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- confidence: 0.0-1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

Avoid: interrogative titles, conditional clauses in titles, article-specific \
framing, ultra-narrow micro-howtos, duplicate existing how-tos.

Voice: ``what_and_problem`` and ``answer_summary`` use easy read; other fields stay \
direct and implementation-focused. Write as reusable procedural guidance.

Tag semantics (HOWTO_TAGS_ALLOWLIST): workflow/implementation area — overlap with \
topic tags is OK. Follow TAG_ONTOLOGY_RUBRIC.

Layer selection: see ABSTRACTION_SELECTION_RUBRIC. Page matching: see PAGE_MATCHING_RUBRIC."""


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

Page matching: reuse ``trend_title`` / ``trend_slug`` from CANONICAL_TREND_TITLES **only** on \
a strong page match (PAGE_MATCHING_RUBRIC).

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
- related_trends: **weak** cross-links to other trend_slug values only; not a substitute \
for ``trend_slug`` (kebab-case list of strings)
- proposed_tags: allowlist tags from TREND_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- confidence: 0.0-1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

Voice: measured, evidence-grounded, explicitly uncertain where warranted. \
No hype, no certainty theater.

Tag semantics (TREND_TAGS_ALLOWLIST): durable industry pattern domain — not \
headline or vendor campaign labels. Follow TAG_ONTOLOGY_RUBRIC.

Page matching: see PAGE_MATCHING_RUBRIC."""


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
If a tool is merely mentioned in passing, set confidence < 0.3 and value_level = "low".

Page matching: reuse ``name`` from CANONICAL_TOOL_NAMES **only** when the source is about \
that **same product** (strong identity match per PAGE_MATCHING_RUBRIC).

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
- confidence: 0.0-1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

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
REGISTRY_TYPES_SEMANTICS for proposed_types."""


MODELS_RUBRIC = """\
## foundation_models (array of objects — model proposals)

Only extract models where the source provides OPERATIONALLY USEFUL information — \
not passing mentions. A model deserves extraction when the source contains \
meaningful operational evaluation, deployment implications, comparative observations, \
or strategic significance.

Model-worthiness criteria:
- Operational evaluation: real-world capabilities, tradeoffs, and differentiators
- Deployment implications: how the model changes engineering, orchestration, or production \
workflows when adopted
- Comparative observations: meaningful comparison against other models
- Strategic significance: important enough that future sources will enrich it
- Reusable knowledge: observations likely useful beyond this single article
If a model is merely mentioned without operational depth, set confidence < 0.3 and \
value_level = "low".

Page matching: reuse ``model_name`` from CANONICAL_FOUNDATION_MODEL_NAMES **only** for the \
**same model identity** (strong match per PAGE_MATCHING_RUBRIC).

Each object MUST include:
- model_name: REQUIRED non-empty string — the model's established name exactly as the source \
states it (e.g. Mercury 2, Kimi K2.5, DeepSeek V4, GPT-5). Never leave blank; the name must \
appear in supporting_snippet or operational_profile.
- provider: organization name (OpenAI, Anthropic, Google, Meta, DeepSeek, etc.)
- operational_profile: **combined** operational identity and strengths — what the model \
is good at, what differentiates it, and why capabilities matter (explanatory prose or \
markdown bullets per TOOLS_RUBRIC Explanatory depth). NOT a generic "X is an LLM" blurb. \
Typically 3-6 bullets or 3-6 sentences when the source supports depth. Do **not** repeat \
deployment_implications here.
- deployment_implications: how **adopting or deploying** this model changes AI engineering, \
orchestration, evaluation, automation, and service workflows — production constraints, \
integration patterns, harness design, cost/latency tradeoffs at scale. Examples: "enables \
larger autonomous coding loops", "reduces need for aggressive RAG chunking at 1M context". \
Do **not** repeat operational_profile strengths here.
- weaknesses_limitations: REQUIRED skeptical assessment in the same explanatory \
style — inference cost, planning weaknesses, formatting instability, hallucination \
patterns, context degradation, each with enough context to understand the tradeoff. \
If none evident, state that explicitly in a full sentence.
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
- confidence: 0.0-1.0
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

Classification rule: types describe WHAT THE MODEL IS, not subjective quality. \
Good: reasoning-model, coding-model, multimodal-model. \
Bad: powerful, smart, enterprise-ready.

Prioritize observations likely to remain useful 6-12 months after the source's \
publication date. Transient hype or short-lived benchmark excitement belongs in \
trends, not model pages.

Compression: operational_profile + deployment_implications must be **non-overlapping** — \
one combined profile beats restating the same points in multiple fields (no legacy \
operational_summary / strengths / workflow_implications split).

Voice: clear, operational, skeptical. No hype, no certainty theater.

Type semantics (MODEL_TYPES_ALLOWLIST): operational profile — follow \
REGISTRY_TYPES_SEMANTICS for proposed_types."""


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
numbered or clearly separated reviews of named tools, apps, SaaS products, or \
free/paid alternatives (including non-AI productivity apps), and optionally \
models; "N tools/apps/alternatives" patterns, repeated per-item blurbs. Examples: \
\"10 AI tools\", \"free alternatives to apps I was paying for\". Prefer this over \
ai_industry_roundup when most main items are named products with dedicated coverage
- "how_to_roundup" — curated multi-item piece whose PRIMARY structure is numbered or \
clearly separated practices, techniques, workflows, or tips (procedures—not named \
products); "N ways to…", "N practices", step-by-step list guides. Prefer over \
technical_howto when there are many distinct how-to items, not one unified tutorial
- "interview_or_transcript" — long-form conversations with interviewer/ \
interviewee structure, Q&A format, multiple speaker perspectives, or \
transcript-like content
- "technical_howto" — primarily step-by-step tutorial or implementation guide
- "research_paper_or_report" — academic paper, formal research report, or \
technical whitepaper with citations and methodology
- "unknown" — use when genuinely uncertain

Disambiguation: ai_industry_roundup for general multi-topic news digests; \
ai_tools_roundup when items are named apps/tools/products; how_to_roundup when \
items are practices/techniques/workflows; technical_howto for one primary tutorial.

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
- proposed_tags: allowlist tags from TREND_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- suggested_destinations: routing hints as array of strings (e.g. \
["topics/", "trends/"])
- mentioned_entities: organizations, tools, models mentioned (array of strings)
- evidence_snippets: supporting source quotes for provenance (array of strings)
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

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
- proposed_tags: allowlist tags from TOPIC_TAGS_ALLOWLIST (see TAG ONTOLOGY)
- suggested_new_tags: off-list registry candidates when warranted (see TAG ONTOLOGY)
- suggested_destinations: routing hints (array of strings, e.g. \
["topics/", "models/"])
- mentioned_entities: organizations, tools, models mentioned (array of strings)
- contrarian_or_speculative_claims: strong predictions, contrarian takes, \
speculative claims — explicitly mark as speculative (array of strings)
- evidence_snippets: supporting source quotes for provenance (array of strings)
- value_level: "high", "medium", or "low"
- evidence_type: (optional) only if this proposal differs from source_evidence_profile

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
    reviews_root: Path | None = None,
    *,
    prompt_version: str,
) -> str:
    """Assemble the user message with metadata, lists, and article body."""
    meta_lines = [
        f"prompt_version: {prompt_version}",
        f"source_id: {doc.source_id}",
        f"title: {doc.title or ''}",
        f"author: {doc.author or ''}",
        f"publication: {doc.publication or ''}",
        f"published_date: {doc.published_date or ''}",
        f"canonical_url: {doc.canonical_url or ''}",
    ]
    schema_hint = json.dumps(llm_output_json_schema_for_classification(), indent=2)[:24_000]
    canonical_blocks = build_canonical_title_prompt_blocks(wiki, reviews_root)
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
        note = ""
        if bk == "tools":
            note = " (uncapped when detected type is ai_tools_roundup)"
        elif bk == "how_to":
            note = " (uncapped when detected type is how_to_roundup)"
        elif bk == "foundation_models":
            note = " (uncapped when detected type is ai_tools_roundup)"
        budget_lines_parts.append(f"- {label}: max {mx} proposals{note}")
    budget_block = EXTRACTION_BUDGET_RUBRIC.format(budget_lines="\n".join(budget_lines_parts))
    trend_slugs = wiki.trend_slugs[:100] if wiki.trend_slugs else []
    blocks = [
        "## Metadata\n" + "\n".join(meta_lines),
        TEMPORAL_ANCHORING_RULE,
        budget_block,
        AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC,
        HOW_TO_ROUNDUP_EXTRACTION_RUBRIC,
        VALUE_RANKING_RUBRIC,
        ABSTRACTION_SELECTION_RUBRIC,
        COMPRESSION_PRESSURE_RUBRIC,
        MINIMUM_NOVELTY_THRESHOLD_RUBRIC,
        SOURCE_EVIDENCE_PROFILE_RUBRIC,
        TAG_ONTOLOGY_RUBRIC,
        REGISTRY_TYPES_SEMANTICS,
        TITLE_CANONICALIZATION_RUBRIC,
        PAGE_MATCHING_RUBRIC,
        "## CANONICAL_GLOSSARY_TERMS\n" + canonical_blocks["CANONICAL_GLOSSARY_TERMS"],
        "## CANONICAL_TOOL_NAMES\n" + canonical_blocks["CANONICAL_TOOL_NAMES"],
        "## CANONICAL_FOUNDATION_MODEL_NAMES\n"
        + canonical_blocks["CANONICAL_FOUNDATION_MODEL_NAMES"],
        "## CANONICAL_IMPL_STUDY_TITLES\n" + canonical_blocks["CANONICAL_IMPL_STUDY_TITLES"],
        "## CANONICAL_TOPIC_TITLES\n" + canonical_blocks["CANONICAL_TOPIC_TITLES"],
        "## CANONICAL_HOWTO_TITLES\n" + canonical_blocks["CANONICAL_HOWTO_TITLES"],
        "## CANONICAL_TREND_TITLES\n" + canonical_blocks["CANONICAL_TREND_TITLES"],
        "## EXISTING_TOPIC_SLUGS\n" + "\n".join(f"- {s}" for s in wiki.topic_slugs[:100])
        or "(none)",
        "## EXISTING_TREND_SLUGS\n" + "\n".join(f"- {s}" for s in trend_slugs) or "(none)",
        "## TOOL_TYPES_ALLOWLIST\n" + "\n".join(f"- {t}" for t in tool_types),
        "## MODEL_TYPES_ALLOWLIST\n" + "\n".join(f"- {t}" for t in m_types),
        "## HOWTO_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in howto_tags),
        "## IMPL_STUDY_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in impl_tags),
        "## GLOSSARY_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in gloss_tags),
        "## TOPIC_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in t_tags),
        "## TREND_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in tr_tags),
        "## SOURCE_TYPE_DETECTION_RUBRIC\n" + SOURCE_TYPE_DETECTION_RUBRIC,
        "## SOURCE_EVIDENCE_PROFILE_RUBRIC\n" + SOURCE_EVIDENCE_PROFILE_RUBRIC,
        "## SOURCE_CHAPTERS_RUBRIC\n" + SOURCE_CHAPTERS_RUBRIC,
        "## PAGE_MATCHING_RUBRIC\n" + PAGE_MATCHING_RUBRIC,
        "## ABSTRACTION_SELECTION_RUBRIC\n" + ABSTRACTION_SELECTION_RUBRIC,
        "## COMPRESSION_PRESSURE_RUBRIC\n" + COMPRESSION_PRESSURE_RUBRIC,
        "## MINIMUM_NOVELTY_THRESHOLD_RUBRIC\n" + MINIMUM_NOVELTY_THRESHOLD_RUBRIC,
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
            "if how_to_roundup, follow HOW_TO_ROUNDUP_EXTRACTION_RUBRIC only; "
            "if interview_or_transcript, populate interview_insights."
        )
    blocks.extend(
        [
            "## ARTICLE_PLAIN_TEXT\n" + doc.plain_text,
            "## Instructions\n"
            "Output one JSON object matching the schema keys: extraction_meta, "
            "source_evidence_profile, source_type_detection, source_summary, glossary, "
            "tools, foundation_models, "
            "how_to, topics, implementation_studies, industry_trends, roundup_signals, "
            "interview_insights. "
            "FIRST: fill extraction_meta (skip_recommended, skip_reason, "
            "total_candidates_considered, review_burden_estimate). "
            "If skip_recommended is true, return empty arrays for all entity types—NEVER when "
            "detected type is ai_tools_roundup or how_to_roundup (skip_recommended must be "
            "false for those). "
            "THEN: fill source_type_detection per SOURCE_TYPE_DETECTION_RUBRIC. "
            "THEN: fill source_evidence_profile per SOURCE_EVIDENCE_PROFILE_RUBRIC. "
            "THEN: fill source_summary per SOURCE_CHAPTERS_RUBRIC. "
            "IF detected_source_type is ai_tools_roundup: follow "
            "AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC "
            "exactly—leave glossary, topics, how_to, industry_trends, roundup_signals, "
            "implementation_studies, interview_insights as []; extract every primary enumerated "
            "tool/app; skip_recommended must be false; numeric caps under ## EXTRACTION BUDGETS "
            "do not limit tools or foundation_models for this type only. "
            "IF detected_source_type is how_to_roundup: follow HOW_TO_ROUNDUP_EXTRACTION_RUBRIC "
            "exactly—leave glossary, topics, tools, foundation_models, industry_trends, "
            "roundup_signals, implementation_studies, interview_insights as []; extract every "
            "primary enumerated practice; skip_recommended must be false; numeric caps do not "
            "limit how_to for this type only. "
            "ELSE: apply PAGE_MATCHING_RUBRIC before reusing any CANONICAL_* title or slug. "
            "For each candidate knowledge unit, apply ABSTRACTION_SELECTION_RUBRIC "
            "first; then fill glossary, tools, foundation_models, how_to, topics, "
            "implementation_studies, industry_trends per their rubrics and RESPECT extraction "
            "budgets. Apply MINIMUM_NOVELTY_THRESHOLD_RUBRIC and COMPRESSION_PRESSURE_RUBRIC "
            "across all proposals before finalizing arrays — omit familiar concepts without "
            "source-specific additive insight; prefer one stronger proposal over partially "
            "redundant overlap. "
            "Do not place the same substance in multiple entity types unless the rubric allows "
            "complementary dual extraction. Every proposal MUST have a value_level field. "
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
        reviews_root: Path | None = None,
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
            reviews_root=reviews_root,
            prompt_version=prompt_version or PROMPT_VERSION,
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + " Respond with one JSON object only."},
            {"role": "user", "content": user_prompt},
        ]
        # Prefer json_schema when the API accepts it; fall back to json_object.
        schema = llm_output_json_schema_for_classification()
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
        source_entity_key: str | None = None,
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
            source_entity_key=source_entity_key,
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
    ) -> tuple[list[str], dict[str, Any]]:
        """Return kebab-case tag(s) not in allowlist (usually zero or one)."""
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
                tags = normalize_tag_list(out.suggested_tags, cap=0)
                single = normalize_tag(str(out.suggested_tag or ""))
                if single and single not in tags:
                    tags.insert(0, single)
                filtered = [t for t in tags if t and t not in allow_norms]
                meta: dict[str, Any] = {
                    "request_id": completion.id,
                    "token_usage": completion.usage.model_dump() if completion.usage else None,
                    "prompt_version": prompt_version or PROMPT_VERSION,
                }
                return filtered, meta
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
        return [], {"error": last_error or "unknown"}
