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
For tools and how_to items, proposed_tags MUST be a subset of the allowlists provided in the \
user message; use [] if none apply.
Prefer reusing existing wiki pages (match_candidates, similar_existing_questions) when the \
article overlaps; suggest create only when justified.

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
    tool_tags: list[str],
    howto_tags: list[str],
    impl_study_tags: list[str] | None = None,
    glossary_tags: list[str] | None = None,
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
    impl_titles = wiki.implementation_study_titles[:100] if wiki.implementation_study_titles else []
    blocks = [
        "## Metadata\n" + "\n".join(meta_lines),
        "## EXISTING_GLOSSARY_TERMS\n" + "\n".join(f"- {t}" for t in wiki.glossary_terms[:150]),
        "## EXISTING_QUESTION_HINTS\n" + "\n".join(f"- {q}" for q in wiki.question_hints[:150]),
        "## EXISTING_TOOL_NAMES\n" + "\n".join(f"- {t}" for t in wiki.tool_names[:200]),
        "## EXISTING_FOUNDATION_MODEL_NAMES\n"
        + "\n".join(f"- {m}" for m in wiki.foundation_model_names[:120]),
        "## EXISTING_IMPLEMENTATION_STUDY_TITLES\n" + "\n".join(f"- {t}" for t in impl_titles),
        "## TOOL_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in tool_tags),
        "## HOWTO_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in howto_tags),
        "## IMPL_STUDY_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in impl_tags),
        "## GLOSSARY_TAGS_ALLOWLIST\n" + "\n".join(f"- {t}" for t in gloss_tags),
        "## SOURCE_CHAPTERS_RUBRIC\n" + SOURCE_CHAPTERS_RUBRIC,
        "## GLOSSARY_RUBRIC\n" + GLOSSARY_RUBRIC,
        "## IMPL_STUDY_RUBRIC\n" + IMPL_STUDY_RUBRIC,
        "## JSON_SCHEMA_HINT\n" + schema_hint,
        "## ARTICLE_PLAIN_TEXT\n" + doc.plain_text,
        "## Instructions\n"
        "Output one JSON object matching the schema keys: source_summary, glossary, tools, "
        "foundation_models, how_to, implementation_studies, industry_trends, roundup. "
        "Prioritize high-signal source_summary chapters per SOURCE_CHAPTERS_RUBRIC. "
        "For glossary, follow GLOSSARY_RUBRIC strictly. "
        "For implementation_studies, follow IMPL_STUDY_RUBRIC strictly. "
        "Use empty arrays when a category does not apply. For roundup: set is_roundup true only "
        "for digests/newsletters whose primary purpose is listing many external items.",
    ]
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
        tool_tags_allowlist: list[str],
        howto_tags_allowlist: list[str],
        impl_study_tags_allowlist: list[str] | None = None,
        glossary_tags_allowlist: list[str] | None = None,
        model: str,
        prompt_version: str,
        max_retries: int = 3,
    ) -> tuple[LlmClassificationOutput, dict[str, Any]]:
        """Call OpenAI and validate against :class:`LlmClassificationOutput`."""
        user_prompt = _build_user_prompt(
            document,
            wiki,
            tool_tags_allowlist,
            howto_tags_allowlist,
            impl_study_tags_allowlist,
            glossary_tags_allowlist,
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
