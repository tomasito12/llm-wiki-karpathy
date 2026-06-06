"""Shared required heading contracts for render and lint."""

from __future__ import annotations

SOURCE_H2_HEADINGS: tuple[str, ...] = (
    "Key insights",
    "Derived knowledge pages",
    "Why it matters",
    "Limitations / open questions",
    "Contradictions / unverified claims",
    "Source metadata",
)

EVIDENCE_SECTION_HEADING = "Evidence / supporting sources"

MERGED_KNOWLEDGE_SECTION_HEADINGS: tuple[str, ...] = (
    "Current understanding",
    EVIDENCE_SECTION_HEADING,
    "Sources",
)

_EVIDENCE_TYPE_HEADINGS: dict[str, str] = {
    "signal": "Signal",
    "insight": "Interview Insight",
    "implementation-study": "Implementation Study",
}


def required_h2_headings_for(frontmatter_category: str) -> tuple[str, ...] | None:
    """Return required level-2 headings for a frontmatter category, if fixed."""
    if frontmatter_category == "source":
        return SOURCE_H2_HEADINGS
    type_heading = _EVIDENCE_TYPE_HEADINGS.get(frontmatter_category)
    if type_heading is not None:
        return (type_heading, EVIDENCE_SECTION_HEADING, "Source")
    return None
