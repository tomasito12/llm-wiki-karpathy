"""Prompt construction for Stage 2 synthesis calls."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from src.wiki_synthesis import SYNTHESIS_PROMPT_VERSION, SYNTHESIS_SCHEMA_VERSION
from src.wiki_synthesis.cache import cached_input_hash
from src.wiki_synthesis.input_hash import synthesis_input_hash

SYSTEM_PROMPT = """You are an expert knowledge synthesizer for a personal AI-engineering
Obsidian wiki.

Your job is to synthesize reviewed evidence into a compact, human-readable,
source-aware knowledge page.

Rules:
- Use only the provided evidence and metadata.
- Do not invent facts, sources, numbers, dates, or claims.
- Preserve uncertainty, disagreement, weak evidence, and time sensitivity.
- Prefer useful synthesis over exhaustive restatement.
- Write for a reader who sits between AI engineering and business/domain work.
- Use plain language and make abstract ideas concrete through examples or practical relevance.
- Separate consensus from tensions and open questions.
- If evidence is thin, say so clearly.
- If sources disagree, describe the disagreement instead of resolving it artificially.
- The output must help two readers:
  1. a human quickly understanding whether this page answers their question
  2. an LLM agent deciding whether to load this page as context
- Return exactly one JSON object matching the requested schema."""

CATEGORY_INSTRUCTIONS: dict[str, str] = {
    "glossary": (
        "For glossary pages, prioritize a precise definition, practical meaning, and common "
        "misunderstandings. Do not turn the page into a broad topic essay."
    ),
    "topic": (
        "For topic pages, synthesize the concept, why it matters, operational implications, "
        "and where the evidence is still incomplete."
    ),
    "how_to": (
        "For how-to pages, prioritize actionable guidance, decision points, caveats, and "
        "prerequisites. Make the practical takeaway especially concrete."
    ),
    "trend": (
        "For trend pages, distinguish observed evidence from speculation. Include time "
        "sensitivity and whether the trend appears mature, emerging, or uncertain."
    ),
    "tool": (
        "For tool pages, focus on what it is useful for, constraints, maturity signals, and "
        "when not to use it. Avoid unsupported benchmarking claims."
    ),
    "model": (
        "For foundation model pages, focus on what the model is useful for, constraints, "
        "maturity signals, and when not to use it. Avoid unsupported benchmarking claims. "
        "Do not force a workflow example when the evidence is better expressed as practical "
        "relevance."
    ),
}

OUTPUT_SCHEMA = {
    "entity_id": "...",
    "category": "...",
    "slug": "...",
    "title": "...",
    "synthesis_schema_version": SYNTHESIS_SCHEMA_VERSION,
    "synthesis_prompt_version": SYNTHESIS_PROMPT_VERSION,
    "synthesis_input_hash": "...",
    "last_synthesized_at": "...",
    "executive_synthesis": "...",
    "practical_example": {
        "title": "...",
        "example": "...",
        "why_it_helps": "...",
        "basis": "source-grounded | illustrative",
    },
    "workflow_variants": [
        {
            "title": "...",
            "use_when": "...",
            "steps": ["..."],
            "caveats": ["..."],
            "sources": ["..."],
        }
    ],
    "what_to_remember": ["..."],
    "consensus": ["..."],
    "tensions": ["..."],
    "evidence_quality": ["..."],
    "practical_takeaway": "...",
    "context_card": {
        "use_this_page_when": "...",
        "best_for_questions_about": ["..."],
        "not_enough_for": ["..."],
        "strongest_sources": ["..."],
        "related_tags": ["..."],
    },
}


@dataclass(frozen=True)
class PromptBundle:
    """A complete chat prompt bundle for one synthesis call."""

    entity_id: str
    category: str
    slug: str
    title: str
    prompt_version: int
    synthesis_input_hash: str
    cached_input_hash: str
    system_prompt: str
    user_prompt: str

    def messages(self) -> list[dict[str, str]]:
        """Return chat-completion style messages."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable prompt bundle."""
        payload = asdict(self)
        payload["messages"] = self.messages()
        return payload


def build_prompt_bundle(
    graph: dict[str, Any],
    *,
    entity_id: str,
    previous_cache: dict[str, Any] | None = None,
) -> PromptBundle:
    """Build the full Stage 2 synthesis prompt bundle for one entity."""
    page = find_knowledge_page(graph, entity_id=entity_id)
    current_hash = synthesis_input_hash(page)
    category = str(page.get("category", ""))
    system_prompt = _system_prompt_for_category(category)
    user_prompt = "\n\n".join(
        [
            _entity_block(page, current_hash),
            _page_purpose_block(),
            _single_source_block(page),
            _source_overview_block(graph, page),
            _evidence_block(page),
            _previous_synthesis_block(previous_cache),
            _output_schema_block(current_hash),
            _style_rules_block(category),
        ]
    )
    return PromptBundle(
        entity_id=str(page.get("entity_id", "")),
        category=category,
        slug=str(page.get("slug", "")),
        title=str(page.get("title", "")),
        prompt_version=SYNTHESIS_PROMPT_VERSION,
        synthesis_input_hash=current_hash,
        cached_input_hash=cached_input_hash(previous_cache),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def find_knowledge_page(graph: dict[str, Any], *, entity_id: str) -> dict[str, Any]:
    """Return one knowledge page from a graph export by entity id."""
    pages = graph.get("knowledge_pages", [])
    if not isinstance(pages, list):
        msg = "Graph export does not contain a knowledge_pages list"
        raise ValueError(msg)
    for page in pages:
        if isinstance(page, dict) and page.get("entity_id") == entity_id:
            return page
    msg = f"Knowledge entity not found: {entity_id}"
    raise ValueError(msg)


def _system_prompt_for_category(category: str) -> str:
    """Return the system prompt with category-specific guidance appended."""
    instruction = CATEGORY_INSTRUCTIONS.get(category)
    if not instruction:
        return SYSTEM_PROMPT
    return f"{SYSTEM_PROMPT}\n\nCategory-specific rule:\n- {instruction}"


def _entity_block(page: dict[str, Any], current_hash: str) -> str:
    """Return the entity metadata prompt block."""
    fields = [
        ("entity_id", page.get("entity_id", "")),
        ("category", page.get("category", "")),
        ("title", page.get("title", "")),
        ("slug", page.get("slug", "")),
        ("path", page.get("path", "")),
        ("tags", page.get("tags", [])),
        ("aliases", page.get("aliases", [])),
        ("source_count", page.get("source_count", 0)),
        ("evidence_count", page.get("evidence_count", 0)),
        ("current_input_hash", current_hash),
    ]
    return "ENTITY\n" + "\n".join(f"- {key}: {_inline_value(value)}" for key, value in fields)


def _page_purpose_block() -> str:
    """Return the page-purpose prompt block."""
    return """PAGE PURPOSE
This page should become an Obsidian-readable synthesis page.
It should answer:
- What should I remember?
- What concrete example, workflow, use case, or practical relevance makes this easier?
- When is this page useful?
- What do the sources agree on?
- Where are the tensions, caveats, or uncertainty?
- How strong is the evidence?
- What is the practical takeaway?"""


def _single_source_block(page: dict[str, Any]) -> str:
    """Return a warning block when the entity has only one source."""
    if _int_value(page.get("source_count")) != 1:
        return ""
    return """SINGLE-SOURCE MODE
This entity currently has evidence from only one source.
Do not imply consensus across sources.
Treat this as a source-grounded readable summary, not as a multi-source synthesis.
Clearly state in evidence_quality that the evidence is single-source and thin."""


def _source_overview_block(graph: dict[str, Any], page: dict[str, Any]) -> str:
    """Return compact source metadata for the page's source ids."""
    sources = _source_map(graph)
    source_ids = page.get("source_ids", [])
    ids = [str(source_id) for source_id in source_ids] if isinstance(source_ids, list) else []
    lines = ["SOURCES"]
    for source_id in ids:
        source = sources.get(source_id, {})
        title = str(source.get("title") or source_id)
        published = str(source.get("published_date") or "unknown")
        assessed = str(source.get("assessed_as_of") or "unknown")
        tags = _inline_value(source.get("tags", []))
        lines.append(
            f"- {source_id}: {title} | published={published} | assessed={assessed} | tags={tags}"
        )
    if len(lines) == 1:
        lines.append("- No source metadata provided.")
    return "\n".join(lines)


def _evidence_block(page: dict[str, Any]) -> str:
    """Return all evidence items in a compact prompt format."""
    evidence = page.get("evidence", [])
    items = evidence if isinstance(evidence, list) else []
    lines = [
        "EVIDENCE",
        "Each item is reviewed evidence from Stage 1. Treat it as the grounding layer.",
    ]
    if not items:
        lines.append("- No evidence items provided.")
        return "\n".join(lines)
    for item in sorted(
        (entry for entry in items if isinstance(entry, dict)),
        key=lambda entry: str(entry.get("evidence_id", "")),
    ):
        lines.extend(_evidence_lines(item))
    return "\n".join(lines)


def _evidence_lines(item: dict[str, Any]) -> list[str]:
    """Return prompt lines for one evidence item."""
    evidence_id = str(item.get("evidence_id") or "unknown")
    source_id = str(item.get("source_id") or "unknown-source")
    source_title = str(item.get("source_title") or source_id)
    field = str(item.get("field") or "unknown_field")
    stance = str(item.get("stance") or "neutral")
    confidence = _inline_value(item.get("confidence"))
    date = str(item.get("source_date") or item.get("published_date") or "unknown")
    text = str(item.get("text") or "").strip()
    return [
        (
            f"- [{evidence_id}] stance={stance} field={field} confidence={confidence} "
            f"source={source_id} ({source_title}) date={date}"
        ),
        f"  claim: {text}",
    ]


def _previous_synthesis_block(previous_cache: dict[str, Any] | None) -> str:
    """Return a continuity block from an existing synthesis cache entry."""
    if not previous_cache:
        return "PREVIOUS SYNTHESIS\nNone."
    compact = {
        key: previous_cache.get(key)
        for key in (
            "synthesis_input_hash",
            "last_synthesized_at",
            "executive_synthesis",
            "practical_example",
            "workflow_variants",
            "what_to_remember",
            "consensus",
            "tensions",
            "evidence_quality",
            "practical_takeaway",
            "context_card",
        )
        if key in previous_cache
    }
    return (
        "PREVIOUS SYNTHESIS\n"
        "Use this only as continuity context. Do not preserve it if current evidence no "
        "longer supports it.\n\n"
        f"{json.dumps(compact, indent=2, sort_keys=True)}"
    )


def _output_schema_block(current_hash: str) -> str:
    """Return the required output schema prompt block."""
    schema = dict(OUTPUT_SCHEMA)
    schema["synthesis_input_hash"] = current_hash
    return (
        "OUTPUT JSON SCHEMA\n"
        "Return exactly this shape. Fill every field with supported content.\n\n"
        f"{json.dumps(schema, indent=2, sort_keys=True)}"
    )


def _style_rules_block(category: str) -> str:
    """Return writing style rules for the synthesis output."""
    base = f"""STYLE RULES
- Write concise, plain English for a technically curious domain expert.
- Avoid unnecessary technical abstraction when a concrete example or relevance framing would help.
- Avoid hype.
- Avoid generic statements.
- Make uncertainty visible.
- Prefer 3 to 7 bullets per list.
- practical_example must be 80 to 140 words.
- Interpret practical_example according to the category guidance below.
- If the example is directly described by the sources, set basis to "source-grounded".
- If the example is a plausible application of the synthesized pattern, set basis to
  "illustrative" and do not present it as a sourced fact.
- Do not invent real customer names, EnBW-specific facts, benchmarks, dates, or numeric outcomes.
- Do not cite evidence IDs in every sentence, but keep source names in strongest_sources.

{_practical_example_guidance(category)}"""
    workflow_guidance = _workflow_variants_guidance(category)
    return f"{base}\n\n{workflow_guidance}"


def _practical_example_guidance(category: str) -> str:
    """Return category-specific guidance for the practical_example field."""
    if category == "model":
        return """CATEGORY GUIDANCE FOR practical_example
- Treat practical_example as "Practical relevance", not as a hypothetical workflow.
- The title should name the relevance angle, such as "Worth watching for coding agents".
- The example field should explain where this model appears relevant, where evidence is thin,
  and whether it is worth testing, watching, or ignoring for now.
- Prefer basis "source-grounded"; use "illustrative" only when clearly framed as inference."""
    if category == "tool":
        return """CATEGORY GUIDANCE FOR practical_example
- Treat practical_example as "Typical use case".
- The title should name the use case.
- Prefer service automation, chatbot, voicebot, contact-center, enterprise workflow, or
  AI-workflow examples when they fit the evidence."""
    if category == "how_to":
        return """CATEGORY GUIDANCE FOR practical_example
- Treat practical_example as "Example workflow".
- The title should name the workflow.
- Show what a practitioner would actually do, in sequence, without adding unsupported steps."""
    return """CATEGORY GUIDANCE FOR practical_example
- Treat practical_example as "Example in practice".
- Prefer service automation, chatbot, voicebot, contact-center, enterprise workflow, or
  AI-workflow examples when they fit the evidence."""


def _workflow_variants_guidance(category: str) -> str:
    """Return category-specific guidance for workflow variants."""
    if category != "how_to":
        return """CATEGORY GUIDANCE FOR workflow_variants
- Use an empty list unless the evidence explicitly describes distinct workflows."""
    return """CATEGORY GUIDANCE FOR workflow_variants
- Always include at least one workflow variant for how-to pages.
- If sources describe materially different workflows, list them as separate variants.
- Do not merge incompatible workflows into one artificial step sequence.
- Each variant should explain when to use it, the main steps, caveats, and source titles.
- If all sources describe the same basic workflow, include one consolidated variant."""


def _source_map(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return source records keyed by source id."""
    sources = graph.get("sources", [])
    if not isinstance(sources, list):
        return {}
    return {
        str(source.get("source_id")): source
        for source in sources
        if isinstance(source, dict) and source.get("source_id")
    }


def _inline_value(value: Any) -> str:
    """Return a compact one-line representation for prompt metadata."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "none"
    if value is None:
        return "unknown"
    return str(value)


def _int_value(value: Any) -> int:
    """Return an integer value for prompt condition checks."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return int(value)
    return 0
