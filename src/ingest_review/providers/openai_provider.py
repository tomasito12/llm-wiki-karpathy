"""OpenAI chat completions provider for ingestion classification."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import APIError, APITimeoutError, OpenAI, RateLimitError
from pydantic import ValidationError

from src.ingest_review.extract import SourceDocument
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import (
    PROMPT_VERSION,
    REGENERATABLE_SOURCE_SECTION_KEYS,
    LlmClassificationOutput,
    SectionRegenerateOutput,
    llm_output_json_schema,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an analyst helping curate a personal AI-engineering Markdown wiki.
Return only valid JSON matching the provided schema. Ground every substantive claim in the \
source text via supporting_snippet (or source_summary section text for narrative fields). \
If unknown, use empty strings or empty arrays and low confidence. Do not invent facts.
For how_to, topics, and industry_trends items, proposed_tags MUST be a subset of the \
allowlists provided in the user message; use [] if none apply.
For tools items, proposed_types MUST be a subset of the TOOL_TYPES_ALLOWLIST; use [] if none \
apply and set proposed_new_type if a new type is warranted.
For foundation_models items, proposed_types MUST be a subset of the MODEL_TYPES_ALLOWLIST; \
use [] if none apply and set proposed_new_type if a new type is warranted.
Always fill source_type_detection with the detected source type, confidence, and reasoning. \
If the source is an ai_industry_roundup, also populate roundup_signals. \
If the source is an interview_or_transcript, also populate interview_insights. \
Prefer reusing existing wiki pages (match_candidates) when the article overlaps with existing \
content; suggest append_to_existing over create_new_page whenever possible.

Voice for source_summary chapters: concise, direct, practical. Audience is an advanced AI \
practitioner focused on conversational AI, chatbots, voicebots, and service automation—not a \
research paper audience. Avoid LinkedIn tone, generic AI hype, buzzword stacking, and \
exaggerated claims. Prefer clarity and usefulness over completeness."""


SOURCE_CHAPTERS_RUBRIC = """## source_summary (required JSON subtree)

Fill every field below from the article. Empty string or [] only when truly absent.

**summary** (string): Usually 4–10 sentences; adapt to complexity. Core ideas and arguments only; \
no chronological retelling; no filler openers; explain concepts plainly; practical understanding \
over technical precision.

**key_insights** (array of strings, at most 5): Only insights that are actionable, strategically \
important, surprising, or practically useful—and non-obvious. One concise sentence per item. \
No generic observations.

**why_it_matters** (string): Broader significance for AI engineering, software development, AI \
products, service automation, business transformation, and industry evolution. Long-term and \
practical implications. No hype.

**implications_automation** (string): Concrete implications for customer-support automation, AI \
agents, voice/chat workflows, service operations, call-center change, AI-assisted support, \
manual work reduction, conversational UX, enterprise adoption in service orgs. If there are \
no meaningful implications, state explicitly that no major implications were identified—do \
not force weak connections.

**practical_relevance** (string): Short honest judgment (e.g. immediately useful, worth \
experimenting, strategically important, mostly hype/noise, early but promising, operationally \
relevant within 1–2 years, incremental improvement, potentially transformative). Nuanced, not \
certainty theater.

**limitations_and_open_questions** (string): Limitations, weak evidence, benchmark limits, \
unrealistic assumptions, missing implementation detail, unresolved operational concerns, \
economics, security/privacy, evaluation weaknesses. Skeptical where warranted.

**contradictions_and_skepticism** (string): Speculative claims, tension with common industry \
practice, hype without evidence, oversimplifications. Thoughtful skepticism—not a hostile \
attack. If nothing major, say so briefly.

**sources** (array of strings): URLs or references present in the article or metadata; else []."""


IMPL_STUDY_RUBRIC = """\
## implementation_studies (array of objects — implementation studies)

Only populate when the article describes a REAL company attempting to implement
a specific technology. Not for product announcements, benchmarks, or opinion pieces.

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
- suggested_existing_tags: tags from IMPL_STUDY_TAGS_ALLOWLIST only
- proposed_new_tags: tags NOT in the allowlist that you think useful; \
these require human approval
- match_candidates: existing wiki implementation-study pages that may overlap
- confidence: 0.0–1.0
- suggested_action: "create" | "update" | "ignore"

Voice: concise, direct, practical. Focus on operational reality over marketing \
claims. Skeptical where warranted. No hype, no LinkedIn tone."""


GLOSSARY_RUBRIC = """\
## glossary (array of objects — glossary term proposals)

Only extract terms where the source provides SUBSTANTIVE explanatory content.
Do NOT extract terms that are merely mentioned in passing.

CRITICAL: Only propose ESTABLISHED industry terms that already exist in \
professional usage and are verifiable via a web search. Do NOT propose \
neologisms coined by the article author, ad-hoc phrases, or terms invented \
for this specific article. If in doubt, omit the term.

A term is a good glossary candidate if the text:
- explicitly defines it
- explains what it means in practice
- contrasts it with related concepts
- describes how it is used operationally
- gives enough context to write a useful explanation

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
- relevance_note: why this term matters in the context of THIS article \
and for a practitioner's glossary. This is where article-specific \
relevance belongs — practical implications, why the source makes this \
term worth knowing, industry significance. 1-3 sentences.
- related_terms: other terms mentioned in the same conceptual context
- proposed_tags: tags from GLOSSARY_TAGS_ALLOWLIST only; \
empty array if allowlist is empty
- match_candidates: existing glossary terms that may overlap
- confidence: 0.0-1.0
- suggested_action: "create" | "update" | "ignore"

Voice: clear, practical, accessible. Define for a senior practitioner, \
not an academic. Prefer operational understanding over theoretical precision."""


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
- operational_insight: practical takeaway for a senior practitioner
- supporting_snippet: verbatim evidence from the source
- relevance_note: why this matters in the context of this source
- key_points: specific knowledge bullets worth accumulating (list of strings)
- related_topics: other topic slugs (list of strings)
- proposed_tags: tags from TOPIC_TAGS_ALLOWLIST only; [] if allowlist is empty
- match_candidates: existing topic pages that may overlap
- confidence: 0.0-1.0
- suggested_action: "append_to_existing" | "create_new_page" | "ignore"

Avoid: article-specific framing, ultra-narrow topics, hype-driven \
fragmentation, one-off concepts, duplicate existing topics.

Voice: clear, operational, synthesized. Write as reusable knowledge, \
not as article commentary."""


HOWTOS_RUBRIC = """\
## how_to (array of objects — how-to proposals)

Extract procedural/implementation knowledge, NOT theoretical summaries. \
Only extract how-tos where the source provides enough implementation \
substance — not vague advice.

Default to append_to_existing. New pages only when the how-to covers a \
genuinely distinct procedure not addressed by existing pages.

Each object MUST include:
- question_title: source-agnostic procedural question — no brand names, \
no article-specific framing, no answer leakage in the question itself
- answer_summary: synthesized guidance, 3-8 sentences, standalone
- supporting_snippet: verbatim evidence from the source
- relevance_note: why this how-to matters
- caveats: gotchas, failure modes, limitations — skeptical where warranted. \
Empty string only if genuinely none
- implementation_steps: concrete, ordered steps when the source supports \
them (list of strings)
- prerequisites: what a practitioner needs before attempting this (list \
of strings)
- related_howtos: cross-references to other how-to slugs (list of strings)
- proposed_tags: tags from HOWTO_TAGS_ALLOWLIST only; [] if none apply
- match_candidates: existing how-to pages that may overlap
- confidence: 0.0-1.0
- suggested_action: "append_to_existing" | "create_new_page" | "ignore"

Voice: direct, practical, implementation-focused. Write as reusable \
procedural guidance."""


TRENDS_RUBRIC = """\
## industry_trends (array of objects — trend observations)

Extract time-sensitive industry patterns, NOT timeless concepts (those \
belong in topics). Trend pages acknowledge uncertainty by design — no \
certainty theater.

Default to append_to_existing. New pages only for genuinely novel \
industry patterns not captured by existing trend pages.

Each object MUST include:
- trend_name: stable pattern name (e.g. inference-cost-collapse, NOT \
GPT-4o-price-cut)
- trend_description: standalone, source-agnostic description of the pattern
- evidence_from_source: what this article specifically contributes as evidence
- time_sensitivity: explicitly state how time-bound this observation is
- uncertainty_note: REQUIRED — explicitly acknowledge uncertainty, \
conflicting signals, or limited evidence. Empty string is NOT acceptable
- supporting_snippet: verbatim evidence from the source
- supporting_data_points: specific data or facts that support the trend \
(list of strings)
- related_trends: other trend names (list of strings)
- proposed_tags: tags from TREND_TAGS_ALLOWLIST only; [] if allowlist is \
empty
- match_candidates: existing trend pages that may overlap
- confidence: 0.0-1.0
- suggested_action: "append_to_existing" | "create_new_page" | "ignore"

Voice: measured, evidence-grounded, explicitly uncertain where warranted. \
No hype, no certainty theater."""


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
- strengths: operational strengths — concrete capabilities, not marketing claims
- weaknesses_limitations: REQUIRED skeptical assessment — limitations, costs, \
scalability issues, ecosystem immaturity, missing features. If none are evident \
from the source, state that explicitly
- maturity_signals: adoption level, ecosystem health, community size, enterprise \
readiness. Use honest descriptors: "rapidly growing", "niche developer tool", \
"experimental", "strong enterprise adoption", etc.
- supporting_snippet: verbatim evidence from the source
- core_capabilities: specific features worth noting (list of strings)
- integration_ecosystem: concrete integrations, APIs, compatibility (list of \
strings)
- related_tools: comparable or complementary tools (list of strings)
- proposed_types: from TOOL_TYPES_ALLOWLIST ONLY. Answer "What kind of thing \
is this?" — NOT "What is it good for?" A tool can have multiple types. Use [] \
if no approved type fits
- proposed_new_type: if no existing type fits, propose ONE new type in \
kebab-case; null otherwise. The human reviewer approves or rejects
- match_candidates: existing tool pages that may overlap
- confidence: 0.0-1.0
- suggested_action: prefer "append_to_existing" for tools already in the wiki; \
"create_new_page" only for genuinely new tools worth tracking long-term

Classification rule: types describe WHAT THE TOOL IS, not what it does well. \
Good: coding-assistant, desktop-app, voice-ai. Bad: productivity, useful, fast.

Voice: clear, operational, skeptical. No hype, no marketing language."""


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
- strengths: operational strengths — concrete capabilities, not marketing claims
- weaknesses_limitations: REQUIRED skeptical assessment — inference cost, planning \
weaknesses, formatting instability, hallucination patterns, context degradation. \
If none evident, state that explicitly
- workflow_implications: how this model changes AI engineering, orchestration, \
evaluation, automation workflows. Examples: "enables larger autonomous coding \
loops", "reduces prompt engineering effort", "lowers orchestration complexity"
- service_automation_implications: implications for conversational AI, chatbots, \
voicebots, support automation, containment rates, handoff reduction. If no \
meaningful implications, state explicitly. Avoid vague business language
- maturity_signals: adoption, ecosystem maturity, enterprise readiness. Use honest \
descriptors: "rapidly adopted", "experimental", "strong enterprise momentum", etc.
- pricing_inference_implications: cost observations, latency, inference economics, \
deployment feasibility for high-volume use cases
- supporting_snippet: verbatim evidence from the source
- core_capabilities: specific capabilities worth noting — coding, long-context, \
tool calling, voice, structured outputs, planning, etc. (list of strings)
- benchmark_observations: ONLY operationally meaningful evidence — SWE-Bench \
discussions, latency comparisons, context-window observations, tool-use evals. \
Do NOT create benchmark dumps (list of strings)
- comparative_observations: comparisons against other models — "stronger coding \
than X", "cheaper than Y", "faster than Z". Extremely valuable (list of strings)
- related_models: comparable or complementary models (list of strings)
- proposed_types: from MODEL_TYPES_ALLOWLIST ONLY. Answer "What kind of model \
is this?" A model can have multiple types. Use [] if no approved type fits
- proposed_new_type: if no existing type fits, propose ONE new type in kebab-case; \
null otherwise
- match_candidates: existing model pages that may overlap
- confidence: 0.0-1.0
- suggested_action: prefer "append_to_existing" for models already in the wiki; \
"create_new_page" only for genuinely new models worth tracking long-term

Classification rule: types describe WHAT THE MODEL IS, not subjective quality. \
Good: reasoning-model, coding-model, multimodal-model. \
Bad: powerful, smart, enterprise-ready.

Prioritize observations likely to remain useful in 6-12 months. Transient hype \
or short-lived benchmark excitement belongs in trends, not model pages.

Voice: clear, operational, skeptical. No hype, no certainty theater."""


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
- "interview_or_transcript" — long-form conversations with interviewer/ \
interviewee structure, Q&A format, multiple speaker perspectives, or \
transcript-like content
- "technical_howto" — primarily step-by-step tutorial or implementation guide
- "research_paper_or_report" — academic paper, formal research report, or \
technical whitepaper with citations and methodology
- "unknown" — use when genuinely uncertain

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
answer: "Will this still matter in 6–12 months?"

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
- suggested_destinations: routing hints as array of strings (e.g. \
["topics/", "trends/"])
- mentioned_entities: organizations, tools, models mentioned (array of strings)
- evidence_snippets: supporting source quotes for provenance (array of strings)

If source is NOT a roundup, return an empty array [].

Voice: clear, operational, durable. No hype."""


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
- suggested_destinations: routing hints (array of strings, e.g. \
["topics/", "models/"])
- mentioned_entities: organizations, tools, models mentioned (array of strings)
- contrarian_or_speculative_claims: strong predictions, contrarian takes, \
speculative claims — explicitly mark as speculative (array of strings)
- evidence_snippets: supporting source quotes for provenance (array of strings)

If source is NOT an interview/transcript, return an empty array [].

Voice: clear, operational, synthesized. No conversational filler."""


def _section_regen_rubric(section_key: str) -> str:
    """Narrow rubric text for one section (avoid brittle string splits in production)."""
    fixed = {
        "summary": (
            "Usually 4–10 sentences; adapt to complexity. Core ideas only; no chronological "
            "retelling; no filler; practical clarity."
        ),
        "key_insights": (
            "Array of at most 5 strings: actionable, strategically important, surprising, "
            "or practically useful—and non-obvious. One sentence each."
        ),
        "why_it_matters": (
            "Significance for AI engineering, software development, AI products, service "
            "automation, business transformation, industry evolution. No hype."
        ),
        "implications_automation": (
            "Concrete implications for chatbots, voicebots, support automation, agents, "
            "operations. If none, state that no major implications were identified."
        ),
        "practical_relevance": (
            "Short honest judgment (e.g. immediately useful, hype/noise, incremental, "
            "transformative). Nuanced."
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
    impl_titles = wiki.implementation_study_titles[:100] if wiki.implementation_study_titles else []
    topic_titles = wiki.topic_titles[:100] if wiki.topic_titles else []
    howto_titles = wiki.howto_titles[:100] if wiki.howto_titles else []
    trend_titles = wiki.trend_titles[:100] if wiki.trend_titles else []
    blocks = [
        "## Metadata\n" + "\n".join(meta_lines),
        "## EXISTING_GLOSSARY_TERMS\n" + "\n".join(f"- {t}" for t in wiki.glossary_terms[:150]),
        "## EXISTING_TOOL_NAMES\n" + "\n".join(f"- {t}" for t in wiki.tool_names[:200]),
        "## EXISTING_FOUNDATION_MODEL_NAMES\n"
        + "\n".join(f"- {m}" for m in wiki.foundation_model_names[:120]),
        "## EXISTING_IMPLEMENTATION_STUDY_TITLES\n" + "\n".join(f"- {t}" for t in impl_titles),
        "## EXISTING_TOPIC_TITLES\n" + "\n".join(f"- {t}" for t in topic_titles),
        "## EXISTING_HOWTO_TITLES\n" + "\n".join(f"- {t}" for t in howto_titles),
        "## EXISTING_TREND_TITLES\n" + "\n".join(f"- {t}" for t in trend_titles),
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
            "Set source_type_detection.detected_source_type accordingly and populate "
            "the corresponding specialized extraction (roundup_signals or "
            "interview_insights) if applicable."
        )
    blocks.extend(
        [
            "## ARTICLE_PLAIN_TEXT\n" + doc.plain_text,
            "## Instructions\n"
            "Output one JSON object matching the schema keys: source_type_detection, "
            "source_summary, glossary, tools, foundation_models, how_to, topics, "
            "implementation_studies, industry_trends, roundup_signals, interview_insights. "
            "FIRST: fill source_type_detection per SOURCE_TYPE_DETECTION_RUBRIC. "
            "THEN: always fill source_summary, glossary, tools, foundation_models, how_to, "
            "topics, implementation_studies, industry_trends per their rubrics. "
            "IF source type is ai_industry_roundup, ALSO fill roundup_signals per "
            "ROUNDUP_SIGNALS_RUBRIC. "
            "IF source type is interview_or_transcript, ALSO fill interview_insights per "
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
