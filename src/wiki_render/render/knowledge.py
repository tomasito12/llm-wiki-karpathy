"""Render merged knowledge pages and chronological items."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from src.wiki_contract.categories import FRONTMATTER_CATEGORY_BY_GRAPH
from src.wiki_render import layout
from src.wiki_render.frontmatter import markdown_document
from src.wiki_render.models import IndividualPage, KnowledgePage, RenderedFile
from src.wiki_render.render.common import (
    bullet_list,
    contradictions_section,
    evidence_section,
    heading,
    lead_text,
    paragraph,
    sources_section,
)
from src.wiki_synthesis import SYNTHESIS_PROMPT_VERSION, SYNTHESIS_SCHEMA_VERSION
from src.wiki_synthesis.cache import (
    VALIDATION_STALE,
    CacheValidation,
    load_cache_entry,
    validate_cache_entry,
)
from src.wiki_synthesis.render_input import synthesis_input_hash_for_knowledge_page

CATEGORY_LABELS: dict[str, str] = FRONTMATTER_CATEGORY_BY_GRAPH
RelatedPageIndex = dict[tuple[str, str], KnowledgePage]
RELATED_TARGET_CATEGORIES: dict[str, str] = {
    "related_topics": "topic",
    "related_terms": "glossary",
    "related_trends": "trend",
    "related_tools": "tool",
    "related_models": "model",
    "related_howtos": "how_to",
}

LEAD_KEYS: dict[str, tuple[str, ...]] = {
    "topic": ("knowledge_summary", "relevance_note"),
    "glossary": ("proposed_definition", "extended_explanation"),
    "trend": ("trend_description", "evidence_from_source"),
    "tool": ("short_description", "operational_relevance"),
    "model": ("operational_profile", "deployment_implications"),
    "how_to": ("what_and_problem", "answer_summary"),
}

DISPLAY_NAMES: dict[str, str] = {
    "knowledge_summary": "Core concept / definition",
    "proposed_definition": "Definition",
    "extended_explanation": "Current understanding",
    "trend_description": "Trend statement",
    "evidence_from_source": "Evidence timeline",
    "time_sensitivity": "Time sensitivity",
    "uncertainty_note": "Uncertainty / maturity",
    "short_description": "What it is",
    "operational_relevance": "Operational relevance",
    "strengths": "Strengths",
    "weaknesses_limitations": "Weaknesses / limitations",
    "maturity_signals": "Maturity signals",
    "operational_profile": "Operational profile",
    "deployment_implications": "Deployment implications",
    "service_automation_implications": "Service automation implications",
    "pricing_inference_implications": "Pricing / inference implications",
    "what_and_problem": "What and problem",
    "answer_summary": "Answer summary",
    "caveats": "Caveats",
    "overview": "Overview",
    "company": "Company / organization",
    "industry": "Industry / domain",
    "what_was_implemented": "What was implemented?",
    "business_objective": "Business objective",
    "technical_approach": "Technical approach",
    "deployment_context": "Deployment context",
    "outcome_status": "Outcome / current status",
    "success_or_failure_factors": "Why it succeeded or struggled",
    "operational_constraints": "Operational constraints",
    "ai_model_observations": "AI / model observations",
    "implications_for_service_automation": "Implications for service automation",
    "strategic_signals": "Strategic signals",
}

SKIP_BODY_KEYS = {
    "topic_slug",
    "topic_title",
    "trend_slug",
    "trend_title",
    "term",
    "name",
    "model_name",
    "question_title",
    "title",
    "supporting_snippet",
    "evidence_snippets",
}

IMPL_STUDY_BODY_KEYS: tuple[str, ...] = (
    "overview",
    "what_was_implemented",
    "business_objective",
    "technical_approach",
    "deployment_context",
    "outcome_status",
    "success_or_failure_factors",
    "operational_constraints",
    "ai_model_observations",
    "implications_for_service_automation",
    "strategic_signals",
)
IMPL_STUDY_LIST_KEYS: tuple[str, ...] = ("key_lessons", "open_questions", "related_sources")


def render_knowledge_page(
    page: KnowledgePage,
    *,
    synthesis_cache_dir: Path | None = None,
    related_page_index: RelatedPageIndex | None = None,
) -> RenderedFile:
    """Render one merged knowledge page."""
    cache_entry, validation = _load_renderable_synthesis(page, synthesis_cache_dir)
    if cache_entry and validation and validation.is_usable:
        return _render_synthesized_knowledge_page(
            page,
            cache_entry,
            validation,
            related_page_index=related_page_index,
        )

    frontmatter = {
        "title": page.title,
        "slug": page.slug,
        "entity_id": page.entity_id,
        "category": CATEGORY_LABELS[page.category],
        "tags": page.tags,
        "aliases": page.aliases,
        "first_seen": page.first_seen,
        "last_seen": page.last_seen,
        "source_count": page.source_count,
        "evidence_count": page.evidence_count,
        "source_ids": page.source_ids,
        "value_level": page.value_level,
        "confidence": page.confidence,
        "synthesis_state": page.synthesis_state,
        "maturity": page.maturity,
        "types": page.types,
    }
    body = heading(1, page.title)
    body += _lead_section(page)
    body += _value_sections(page)
    body += evidence_section(page.evidence)
    body += contradictions_section(page.evidence)
    body += _related_section(page, related_page_index)
    body += sources_section(page.source_ids, page.source_titles)
    return RenderedFile(relative_path=page.path, text=markdown_document(frontmatter, body))


def _load_renderable_synthesis(
    page: KnowledgePage,
    synthesis_cache_dir: Path | None,
) -> tuple[dict[str, Any] | None, CacheValidation | None]:
    """Load and validate an optional Stage 2 synthesis cache entry."""
    if synthesis_cache_dir is None:
        return None, None
    current_hash = synthesis_input_hash_for_knowledge_page(page)
    entry = load_cache_entry(
        synthesis_cache_dir,
        category=page.category,
        slug=page.slug,
    )
    validation = validate_cache_entry(entry, current_input_hash=current_hash)
    if not validation.is_usable:
        return None, validation
    return entry, validation


def _render_synthesized_knowledge_page(
    page: KnowledgePage,
    cache_entry: dict[str, Any],
    validation: CacheValidation,
    *,
    related_page_index: RelatedPageIndex | None = None,
) -> RenderedFile:
    """Render one merged knowledge page from an existing synthesis cache entry."""
    is_stale = validation.state == VALIDATION_STALE
    frontmatter = {
        "title": page.title,
        "slug": page.slug,
        "entity_id": page.entity_id,
        "category": CATEGORY_LABELS[page.category],
        "tags": page.tags,
        "aliases": page.aliases,
        "first_seen": page.first_seen,
        "last_seen": page.last_seen,
        "source_count": page.source_count,
        "evidence_count": page.evidence_count,
        "source_ids": page.source_ids,
        "value_level": page.value_level,
        "confidence": page.confidence,
        "synthesis_state": "stale" if is_stale else "synthesized",
        "synthesis_stale": is_stale,
        "synthesis_input_hash": validation.cached_input_hash,
        "current_input_hash": validation.current_input_hash,
        "synthesis_schema_version": cache_entry.get(
            "synthesis_schema_version",
            SYNTHESIS_SCHEMA_VERSION,
        ),
        "synthesis_prompt_version": cache_entry.get(
            "synthesis_prompt_version",
            SYNTHESIS_PROMPT_VERSION,
        ),
        "last_synthesized_at": cache_entry.get("last_synthesized_at", ""),
        "maturity": page.maturity,
        "types": page.types,
    }
    body = heading(1, page.title)
    if is_stale:
        body += (
            "> [!warning] Synthesis may be stale\n"
            "> New or changed evidence exists. The prose synthesis below was "
            "generated from an older evidence hash.\n\n"
        )
    body += heading(2, "Executive synthesis")
    body += paragraph(str(cache_entry.get("executive_synthesis", "")))
    body += _practical_example_section(cache_entry)
    body += _context_card_section(cache_entry)
    body += _cache_list_section("What to remember", cache_entry, "what_to_remember")
    body += _cache_list_section("Consensus", cache_entry, "consensus")
    body += _cache_list_section("Tensions / open questions", cache_entry, "tensions")
    body += _cache_list_section("Evidence quality", cache_entry, "evidence_quality")
    body += heading(2, "Practical takeaway")
    body += paragraph(str(cache_entry.get("practical_takeaway", "")))
    body += _evidence_index_section(page, validation, cache_entry)
    body += _related_section(page, related_page_index)
    body += sources_section(page.source_ids, page.source_titles)
    return RenderedFile(relative_path=page.path, text=markdown_document(frontmatter, body))


def _practical_example_section(cache_entry: dict[str, Any]) -> str:
    """Render an optional practical example from a synthesis cache entry."""
    value = cache_entry.get("practical_example")
    if not isinstance(value, dict):
        return ""
    title = _display_value(value.get("title"))
    example = _display_value(value.get("example"))
    why_it_helps = _display_value(value.get("why_it_helps"))
    basis = _display_value(value.get("basis"))
    if not title or not example:
        return ""
    body = heading(2, "Example in practice")
    body += heading(3, title)
    body += paragraph(example)
    if why_it_helps:
        body += bullet_list([f"Why it helps: {why_it_helps}"])
    if basis:
        body += bullet_list([f"Basis: `{basis}`"])
    return body


def _context_card_section(cache_entry: dict[str, Any]) -> str:
    """Render the compact routing card stored in a synthesis cache entry."""
    card = cache_entry.get("context_card")
    if not isinstance(card, dict):
        return ""
    rows: list[str] = []
    for key, label in (
        ("use_this_page_when", "Use this page when"),
        ("best_for_questions_about", "Best for questions about"),
        ("not_enough_for", "Not enough for"),
        ("strongest_sources", "Strongest sources"),
        ("related_tags", "Related tags"),
    ):
        value = _display_value(card.get(key))
        if value:
            rows.append(f"**{label}:** {value}")
    return heading(2, "Context card") + bullet_list(rows) if rows else ""


def _cache_list_section(title: str, cache_entry: dict[str, Any], key: str) -> str:
    """Render one list section from a synthesis cache entry."""
    value = cache_entry.get(key)
    if not isinstance(value, list):
        return ""
    return heading(2, title) + bullet_list(str(item) for item in value)


def _evidence_index_section(
    page: KnowledgePage,
    validation: CacheValidation,
    cache_entry: dict[str, Any],
) -> str:
    """Render audit metadata that lets humans and agents judge freshness."""
    lines = [
        f"Sources: {page.source_count}",
        f"Evidence items: {page.evidence_count}",
        f"Current input hash: `{validation.current_input_hash}`",
        f"Cached input hash: `{validation.cached_input_hash}`",
    ]
    synthesized_at = str(cache_entry.get("last_synthesized_at", "")).strip()
    if synthesized_at:
        lines.append(f"Last synthesized: {synthesized_at}")
    lines.append(f"Synthesis status: `{validation.state}`")
    return heading(2, "Evidence index") + bullet_list(lines)


def _display_value(value: Any) -> str:
    """Return a readable inline display value for cache metadata."""
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value or "").strip()


def render_individual_page(item: IndividualPage) -> RenderedFile:
    """Render one non-merged signal or interview insight."""
    title_key = "Signal" if item.category == "signal" else "Interview Insight"
    frontmatter = {
        "title": item.title,
        "slug": item.slug,
        "category": item.category,
        "tags": item.tags,
        "source_id": item.source_id,
        "source_title": item.source_title,
        "source_date": item.source_date or "unknown",
        "month": item.month,
        "evidence_count": item.evidence_count,
        "evidence_set_hash": item.evidence_set_hash,
        **_scalar_frontmatter(item.values),
    }
    body = heading(1, item.title)
    body += heading(2, title_key)
    for key in (
        "summary",
        "why_it_matters",
        "operational_relevance",
        "service_automation_relevance",
    ):
        value = item.values.get(key)
        if isinstance(value, str) and value.strip():
            body += heading(3, _titleize(key))
            body += paragraph(value)
    for key in (
        "mentioned_entities",
        "suggested_destinations",
        "contrarian_or_speculative_claims",
        "evidence_snippets",
    ):
        value = item.values.get(key)
        if isinstance(value, list) and value:
            body += heading(3, _titleize(key))
            body += bullet_list(str(entry) for entry in value)
    body += evidence_section(item.evidence)
    body += heading(2, "Source")
    body += bullet_list([f"[[sources/{item.source_id}|{item.source_title}]]"])
    return RenderedFile(relative_path=item.path, text=markdown_document(frontmatter, body))


def render_implementation_study_page(item: IndividualPage) -> RenderedFile:
    """Render one non-merged implementation study."""
    frontmatter = {
        "title": item.title,
        "slug": item.slug,
        "category": "implementation-study",
        "tags": item.tags,
        "source_id": item.source_id,
        "source_title": item.source_title,
        "source_date": item.source_date or "unknown",
        "month": item.month,
        "company": item.values.get("company", ""),
        "industry": item.values.get("industry", ""),
        "evidence_count": item.evidence_count,
        "evidence_set_hash": item.evidence_set_hash,
    }
    body = heading(1, item.title)
    body += heading(2, "Implementation Study")
    for key in IMPL_STUDY_BODY_KEYS:
        value = item.values.get(key)
        if isinstance(value, str) and value.strip():
            body += heading(3, DISPLAY_NAMES.get(key, _titleize(key)))
            body += paragraph(value)
    for key in IMPL_STUDY_LIST_KEYS:
        value = item.values.get(key)
        if isinstance(value, list) and value:
            body += heading(3, DISPLAY_NAMES.get(key, _titleize(key)))
            body += bullet_list(str(entry) for entry in value)
    snippets = item.values.get("evidence_snippets")
    if isinstance(snippets, list) and snippets:
        body += heading(3, "Evidence Snippets")
        formatted: list[str] = []
        for snippet in snippets:
            if not isinstance(snippet, dict):
                continue
            snippet_dict = cast(dict[str, object], snippet)
            claim = str(snippet_dict.get("claim") or "").strip()
            text = str(snippet_dict.get("snippet") or "").strip()
            provenance = str(snippet_dict.get("provenance") or "").strip()
            line = f"{claim} — {text}" if claim and text else claim or text
            if provenance:
                line = f"{line} ({provenance})"
            if line:
                formatted.append(line)
        if formatted:
            body += bullet_list(formatted)
    body += evidence_section(item.evidence)
    body += heading(2, "Source")
    body += bullet_list([f"[[sources/{item.source_id}|{item.source_title}]]"])
    return RenderedFile(relative_path=item.path, text=markdown_document(frontmatter, body))


def _lead_section(page: KnowledgePage) -> str:
    """Render the Stage 1 placeholder lead section."""
    keys = LEAD_KEYS.get(page.category, ())
    text = ""
    for key in keys:
        value = page.values.get(key)
        if isinstance(value, str) and value.strip():
            text = value
            break
    return heading(2, "Current understanding") + lead_text(text)


def _value_sections(page: KnowledgePage) -> str:
    """Render category values after the lead."""
    body = ""
    for key, value in page.values.items():
        if key in SKIP_BODY_KEYS or key in LEAD_KEYS.get(page.category, ()):
            continue
        if key in RELATED_TARGET_CATEGORIES:
            continue
        if isinstance(value, str):
            if value.strip():
                body += heading(2, DISPLAY_NAMES.get(key, _titleize(key)))
                body += paragraph(value)
        elif isinstance(value, list) and value:
            body += heading(2, DISPLAY_NAMES.get(key, _titleize(key)))
            body += bullet_list(str(item) for item in value)
    return body


def _related_section(
    page: KnowledgePage,
    related_page_index: RelatedPageIndex | None = None,
) -> str:
    """Render resolvable related concept values as Obsidian wikilinks."""
    related_links: list[str] = []
    seen: set[str] = set()
    for key, value in page.values.items():
        target_category = RELATED_TARGET_CATEGORIES.get(key)
        if not target_category or not isinstance(value, list):
            continue
        for item in value:
            related_page = _resolve_related_page(
                target_category,
                str(item),
                related_page_index,
            )
            if related_page is None or related_page.entity_id == page.entity_id:
                continue
            link = layout.wikilink(related_page.path, related_page.title)
            if link not in seen:
                seen.add(link)
                related_links.append(link)
    if not related_links:
        return heading(2, "Related pages") + "No related pages captured.\n\n"
    return heading(2, "Related pages") + bullet_list(related_links)


def _resolve_related_page(
    target_category: str,
    raw_value: str,
    related_page_index: RelatedPageIndex | None,
) -> KnowledgePage | None:
    """Resolve a reviewed related-page label to an existing knowledge page."""
    if related_page_index is None:
        return None
    clean = raw_value.strip()
    if not clean:
        return None
    return related_page_index.get((target_category, clean)) or related_page_index.get(
        (target_category, layout.safe_slug(clean))
    )


def _scalar_frontmatter(values: dict[str, Any]) -> dict[str, Any]:
    """Return scalar values useful for individual-page frontmatter."""
    result: dict[str, Any] = {}
    for key, value in values.items():
        if (
            isinstance(value, str)
            and value.strip()
            and key
            not in {
                "summary",
                "why_it_matters",
                "operational_relevance",
                "service_automation_relevance",
            }
        ):
            result[key] = value
    return result


def _titleize(key: str) -> str:
    """Return a readable heading from a snake-case key."""
    return key.replace("_", " ").title()
