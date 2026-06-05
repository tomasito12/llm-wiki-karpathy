"""Shared markdown rendering helpers."""

from __future__ import annotations

from collections.abc import Iterable

from src.wiki_render import layout
from src.wiki_render.evidence import EvidenceItem


def heading(level: int, text: str) -> str:
    """Return a markdown heading."""
    return f"{'#' * level} {text}\n\n"


def paragraph(text: str) -> str:
    """Return a paragraph when text is non-empty."""
    clean = str(text or "").strip()
    return f"{clean}\n\n" if clean else ""


def bullet_list(items: Iterable[str]) -> str:
    """Return a markdown bullet list."""
    lines = [f"- {item}" for item in items if str(item).strip()]
    return "\n".join(lines) + ("\n\n" if lines else "")


def value_lines(values: list[str]) -> list[str]:
    """Return escaped-ish display values for bullets."""
    return [str(value).strip() for value in values if str(value).strip()]


def lead_text(text: str) -> str:
    """Return Stage 1 placeholder lead text."""
    clean = str(text or "").strip() or "Not yet synthesized."
    return (
        "<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize "
        "from accumulated EvidenceItems -->\n"
        f"{clean}\n\n"
    )


def source_link(source_id: str, source_title: str | None = None) -> str:
    """Return a wikilink to a source page."""
    rel = f"{layout.SOURCES}/{layout.safe_slug(source_id)}.md"
    return layout.wikilink(rel, source_title or source_id)


def evidence_section(evidence: list[EvidenceItem]) -> str:
    """Render grouped evidence items."""
    if not evidence:
        return heading(2, "Evidence / supporting sources") + "No evidence items captured.\n\n"
    out = heading(2, "Evidence / supporting sources")
    for source_id in sorted({item.source_id for item in evidence}):
        items = [item for item in evidence if item.source_id == source_id]
        title = items[0].source_title
        out += heading(3, f"{title} ({items[0].source_date or 'undated'})")
        for item in sorted(items, key=lambda entry: (entry.stance, entry.field, entry.text)):
            label = f"`{item.evidence_id}` · {item.stance} · {item.field}"
            out += f"- {item.text} ({label}; {source_link(item.source_id, item.source_title)})\n"
        out += "\n"
    return out


def contradictions_section(evidence: list[EvidenceItem]) -> str:
    """Render counter/uncertainty evidence."""
    items = [item for item in evidence if item.stance in {"counter", "uncertainty"}]
    if not items:
        return (
            heading(2, "Contradictions / tensions")
            + "No contradictions captured in current sources.\n\n"
        )
    return heading(2, "Contradictions / tensions") + bullet_list(
        f"{item.text} ({item.stance}; {source_link(item.source_id, item.source_title)})"
        for item in items
    )


def sources_section(source_ids: list[str], source_titles: dict[str, str] | None = None) -> str:
    """Render source links."""
    titles = source_titles or {}
    return heading(2, "Sources") + bullet_list(
        source_link(source_id, titles.get(source_id)) for source_id in source_ids
    )
