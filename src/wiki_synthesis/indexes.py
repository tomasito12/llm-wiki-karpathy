"""Render Stage 2 operational indexes for Obsidian."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from src.pipeline.atomic import atomic_write_text
from src.wiki_render import layout
from src.wiki_render.frontmatter import markdown_document
from src.wiki_render.models import RenderedFile
from src.wiki_render.render.common import bullet_list, heading
from src.wiki_synthesis.models import PlanEntry, SynthesisPlan

DEFAULT_TAG_HUBS: tuple[str, ...] = (
    "ai-engineering",
    "agent-systems",
    "agent-orchestration",
    "knowledge-systems",
    "context-engineering",
    "coding-agents",
    "inference-systems",
    "human-ai-workflows",
    "support-automation",
)

CATEGORY_LABELS: dict[str, str] = {
    "glossary": "Glossary",
    "how_to": "How-to",
    "impl_study": "Implementation Study",
    "insight": "Interview Insight",
    "model": "Foundation Model",
    "signal": "Signal",
    "source": "Source",
    "tool": "Tool",
    "topic": "Topic",
    "trend": "Industry Trend",
}

KNOWLEDGE_CATEGORY_ORDER: dict[str, int] = {
    "how_to": 0,
    "topic": 1,
    "glossary": 2,
    "trend": 3,
    "tool": 4,
    "model": 5,
}


@dataclass(frozen=True)
class IndexItem:
    """One page that can appear in a synthesis-routing index."""

    category: str
    title: str
    path: str
    tags: list[str]
    source_count: int = 0
    evidence_count: int = 0
    confidence: float | None = None
    value_level: str = ""
    synthesis_state: str = ""
    plan_state: str = ""


def render_synthesis_indexes(
    graph: dict[str, Any],
    plan: SynthesisPlan,
    *,
    tags: list[str] | None = None,
) -> list[RenderedFile]:
    """Render Stage 2 operational index files."""
    tag_names = tags if tags is not None else list(DEFAULT_TAG_HUBS)
    items = _collect_index_items(graph, plan)
    return [
        _needs_synthesis_index(plan),
        _synthesis_status_index(plan),
        *[_tag_hub(tag, items) for tag in tag_names],
    ]


def write_synthesis_indexes(
    *,
    wiki_dir: Path,
    files: list[RenderedFile],
    dry_run: bool = False,
) -> tuple[int, int]:
    """Write synthesis index files and return planned/written counts."""
    written = 0
    for rendered in files:
        target = wiki_dir / rendered.relative_path
        if target.exists() and target.read_text(encoding="utf-8") == rendered.text:
            continue
        if not dry_run:
            atomic_write_text(target, rendered.text)
        written += 1
    return len(files), written


def _needs_synthesis_index(plan: SynthesisPlan) -> RenderedFile:
    """Render pages that need initial or refreshed synthesis."""
    body = heading(1, "Needs Synthesis")
    body += (
        "Pages listed here are eligible for Stage 2 synthesis and do not currently have "
        "a matching synthesis cache entry.\n\n"
    )
    actionable = [entry for entry in plan.entries if entry.state in {"new", "stale"}]
    if not actionable:
        body += "No pages currently need synthesis.\n\n"
    for state in ("stale", "new"):
        entries = [entry for entry in actionable if entry.state == state]
        if not entries:
            continue
        body += heading(2, state.title())
        body += bullet_list(_plan_entry_line(entry) for entry in _sort_plan_entries(entries))
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/needs-synthesis.md",
        text=markdown_document(
            {
                "title": "Needs Synthesis",
                "category": "index",
                "index_kind": "synthesis-status",
            },
            body,
        ),
    )


def _synthesis_status_index(plan: SynthesisPlan) -> RenderedFile:
    """Render a compact synthesis planning status dashboard."""
    summary = plan.summary
    body = heading(1, "Synthesis Status")
    body += bullet_list(
        [
            f"Total considered: {summary.total}",
            f"New: {summary.new}",
            f"Stale: {summary.stale}",
            f"Unchanged: {summary.unchanged}",
            f"Skipped single-source pages: {summary.skipped_single_source}",
            f"Skipped evidence objects: {summary.skipped_evidence_object}",
            f"Errors: {summary.error}",
        ]
    )
    body += heading(2, "Routing")
    body += bullet_list(
        [
            layout.wikilink(f"{layout.INDEXES}/needs-synthesis.md", "Needs Synthesis"),
            layout.wikilink(f"{layout.INDEXES}/index.md", "Generated Indexes"),
            layout.wikilink(f"{layout.INDEXES}/knowledge-graph.md", "Knowledge Graph"),
        ]
    )
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/synthesis-status.md",
        text=markdown_document(
            {
                "title": "Synthesis Status",
                "category": "index",
                "index_kind": "synthesis-status",
            },
            body,
        ),
    )


def _tag_hub(tag: str, items: list[IndexItem]) -> RenderedFile:
    """Render one tag hub for human and LLM routing."""
    matching = [item for item in items if tag in item.tags]
    body = heading(1, tag)
    body += (
        "This tag hub is a routing page. Use it to choose a small set of useful pages "
        "before opening full source or evidence pages.\n\n"
    )
    body += heading(2, "Best entry points")
    body += (
        bullet_list(_item_line(item) for item in _best_entry_points(matching))
        or "No entry points captured for this tag.\n\n"
    )
    body += _tag_section("How-to answers", matching, {"how_to"})
    body += _tag_section("Concepts and definitions", matching, {"topic", "glossary"})
    body += _tag_section("Trends and market direction", matching, {"trend", "signal"})
    body += _tag_section("Tools and models", matching, {"tool", "model"})
    body += _tag_section("Primary sources", matching, {"source"}, limit=20)
    body += _tag_section(
        "Evidence objects",
        matching,
        {"signal", "insight", "impl_study"},
        limit=20,
    )
    body += heading(2, "LLM context recipe")
    body += bullet_list(
        [
            "Start with the best entry points.",
            "Prefer how-to pages for procedural questions.",
            "Use source pages when provenance or article-level context matters.",
            "Use evidence objects for recent signals, interview claims, and case examples.",
        ]
    )
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/tags/{layout.safe_slug(tag)}.md",
        text=markdown_document(
            {
                "title": tag,
                "category": "index",
                "index_kind": "tag-hub",
                "tag": tag,
                "tags": [tag],
            },
            body,
        ),
    )


def _tag_section(
    title: str,
    items: list[IndexItem],
    categories: set[str],
    *,
    limit: int = 12,
) -> str:
    """Render a section of matching tag-hub items."""
    selected = [item for item in items if item.category in categories]
    body = heading(2, title)
    body += (
        bullet_list(_item_line(item) for item in _sort_items(selected)[:limit])
        or "No pages captured.\n\n"
    )
    return body


def _best_entry_points(items: list[IndexItem]) -> list[IndexItem]:
    """Return the best initial pages for a tag hub."""
    knowledge = [
        item
        for item in items
        if item.category in KNOWLEDGE_CATEGORY_ORDER and item.source_count >= 2
    ]
    return _sort_items(knowledge)[:8]


def _collect_index_items(graph: dict[str, Any], plan: SynthesisPlan) -> list[IndexItem]:
    """Collect indexable items from graph export and synthesis plan."""
    plan_by_entity = {entry.entity_id: entry for entry in plan.entries}
    items: list[IndexItem] = []
    for page in _list_dicts(graph.get("knowledge_pages")):
        plan_entry = plan_by_entity.get(str(page.get("entity_id", "")))
        items.append(_knowledge_item(page, plan_entry))
    for source in _list_dicts(graph.get("sources")):
        items.append(_source_item(source))
    for item in _list_dicts(graph.get("signals")):
        items.append(_individual_item(item, category="signal"))
    for item in _list_dicts(graph.get("interview_insights")):
        items.append(_individual_item(item, category="insight"))
    for item in _list_dicts(graph.get("implementation_studies")):
        items.append(_individual_item(item, category="impl_study"))
    return items


def _knowledge_item(page: dict[str, Any], plan_entry: PlanEntry | None) -> IndexItem:
    """Return an index item for a knowledge page."""
    return IndexItem(
        category=str(page.get("category", "")),
        title=str(page.get("title", "")),
        path=str(page.get("path", "")),
        tags=_string_list(page.get("tags")),
        source_count=_int_value(page.get("source_count")),
        evidence_count=_int_value(page.get("evidence_count")),
        confidence=_float_or_none(page.get("confidence")),
        value_level=str(page.get("value_level", "")),
        synthesis_state=str(page.get("synthesis_state", "")),
        plan_state=plan_entry.state if plan_entry else "",
    )


def _source_item(source: dict[str, Any]) -> IndexItem:
    """Return an index item for a source page."""
    source_id = str(source.get("source_id", ""))
    return IndexItem(
        category="source",
        title=str(source.get("title", "")),
        path=f"{layout.SOURCES}/{source_id}.md",
        tags=_string_list(source.get("tags")),
    )


def _individual_item(item: dict[str, Any], *, category: str) -> IndexItem:
    """Return an index item for a non-merged evidence object."""
    return IndexItem(
        category=category,
        title=str(item.get("title", "")),
        path=str(item.get("path", "")),
        tags=_string_list(item.get("tags")),
        evidence_count=_int_value(item.get("evidence_count")),
    )


def _plan_entry_line(entry: PlanEntry) -> str:
    """Return a rich Markdown line for a plan entry."""
    return (
        f"{layout.wikilink(entry.path, entry.title)} — {entry.state}; "
        f"sources: {entry.source_count}; evidence: {entry.evidence_count}; "
        f"hash: `{entry.current_input_hash}`"
    )


def _item_line(item: IndexItem) -> str:
    """Return a rich Markdown line for a tag-hub item."""
    details = [CATEGORY_LABELS.get(item.category, item.category)]
    if item.plan_state:
        details.append(f"state: {item.plan_state}")
    if item.source_count:
        details.append(f"sources: {item.source_count}")
    if item.evidence_count:
        details.append(f"evidence: {item.evidence_count}")
    if item.confidence is not None:
        details.append(f"confidence: {item.confidence:.2f}")
    return f"{layout.wikilink(item.path, item.title)} — {'; '.join(details)}"


def _sort_plan_entries(entries: list[PlanEntry]) -> list[PlanEntry]:
    """Sort plan entries by impact and title."""
    return sorted(
        entries,
        key=lambda entry: (-entry.source_count, -entry.evidence_count, entry.category, entry.title),
    )


def _sort_items(items: list[IndexItem]) -> list[IndexItem]:
    """Sort index items by category priority, impact, and title."""
    return sorted(
        items,
        key=lambda item: (
            KNOWLEDGE_CATEGORY_ORDER.get(item.category, 99),
            -item.source_count,
            -item.evidence_count,
            item.title.lower(),
        ),
    )


def _list_dicts(value: object) -> list[dict[str, Any]]:
    """Return dictionary items from a JSON list value."""
    if not isinstance(value, list):
        return []
    output: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            output.append(cast(dict[str, Any], item))
    return output


def _string_list(value: object) -> list[str]:
    """Return a sorted list of string values."""
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if str(item).strip())


def _int_value(value: object) -> int:
    """Return an integer for numeric JSON values."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return int(value)
    return 0


def _float_or_none(value: object) -> float | None:
    """Return a float for numeric JSON values."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    return None
