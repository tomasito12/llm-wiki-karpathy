"""Shared required frontmatter field contracts."""

from __future__ import annotations

REQUIRED_FIELDS_ALL: tuple[str, ...] = ("title", "category")

REQUIRED_FIELDS_BY_FRONTMATTER: dict[str, tuple[str, ...]] = {
    "source": ("source_id",),
    "topic": ("slug", "entity_id", "synthesis_state"),
    "glossary": ("slug", "entity_id", "synthesis_state"),
    "industry-trend": ("slug", "entity_id", "synthesis_state"),
    "tool": ("slug", "entity_id", "synthesis_state"),
    "foundation-model": ("slug", "entity_id", "synthesis_state"),
    "how-to": ("slug", "entity_id", "synthesis_state"),
    "signal": ("source_id", "source_date", "month", "slug"),
    "insight": ("source_id", "source_date", "month", "slug"),
    "implementation-study": ("source_id", "source_date", "month", "slug", "company", "industry"),
    "index": (),
    "diagnostics": (),
}

DERIVED_FRONTMATTER_KEYS: frozenset[str] = frozenset(
    {
        "derived_topics",
        "derived_glossary",
        "derived_trends",
        "derived_tools",
        "derived_models",
        "derived_how_to",
        "derived_signals",
        "derived_interview_insights",
        "derived_implementation_studies",
        "derived_pages",
    }
)


def required_fields_for(frontmatter_category: str) -> tuple[str, ...]:
    """Return required frontmatter keys for one rendered category."""
    specific = REQUIRED_FIELDS_BY_FRONTMATTER.get(frontmatter_category, ())
    return REQUIRED_FIELDS_ALL + specific
