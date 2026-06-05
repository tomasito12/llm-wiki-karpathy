"""Render merged knowledge pages and chronological items."""

from __future__ import annotations

from typing import Any

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

CATEGORY_LABELS: dict[str, str] = {
    "topic": "topic",
    "glossary": "glossary",
    "trend": "industry-trend",
    "tool": "tool",
    "model": "foundation-model",
    "how_to": "how-to",
    "impl_study": "implementation-study",
}

LEAD_KEYS: dict[str, tuple[str, ...]] = {
    "topic": ("knowledge_summary", "relevance_note"),
    "glossary": ("proposed_definition", "extended_explanation"),
    "trend": ("trend_description", "evidence_from_source"),
    "tool": ("short_description", "operational_relevance"),
    "model": ("operational_profile", "deployment_implications"),
    "how_to": ("what_and_problem", "answer_summary"),
    "impl_study": ("overview", "what_was_implemented"),
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


def render_knowledge_page(page: KnowledgePage) -> RenderedFile:
    """Render one merged knowledge page."""
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
    body += _related_section(page)
    body += sources_section(page.source_ids, page.source_titles)
    return RenderedFile(relative_path=page.path, text=markdown_document(frontmatter, body))


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
        "source_date": item.source_date,
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
        if isinstance(value, str):
            if value.strip():
                body += heading(2, DISPLAY_NAMES.get(key, _titleize(key)))
                body += paragraph(value)
        elif isinstance(value, list) and value:
            body += heading(2, DISPLAY_NAMES.get(key, _titleize(key)))
            body += bullet_list(str(item) for item in value)
    return body


def _related_section(page: KnowledgePage) -> str:
    """Render related concept values from merged fields."""
    related: list[str] = []
    for key, value in page.values.items():
        if key.startswith("related") and isinstance(value, list):
            related.extend(str(item) for item in value)
    if not related:
        return heading(2, "Related pages") + "No related pages captured.\n\n"
    return heading(2, "Related pages") + bullet_list(sorted(set(related)))


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
