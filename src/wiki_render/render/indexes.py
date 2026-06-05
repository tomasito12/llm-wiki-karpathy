"""Render plugin-free index and diagnostics pages."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import TypeAlias

from src.wiki_render import TOOL_VERSION, layout
from src.wiki_render.frontmatter import markdown_document
from src.wiki_render.models import (
    IndividualPage,
    KnowledgeGraph,
    KnowledgePage,
    RenderedFile,
    SourceRecord,
)
from src.wiki_render.render.common import bullet_list, heading

IndexItem: TypeAlias = KnowledgePage | SourceRecord  # noqa: UP040
CATEGORY_INDEXES: tuple[str, ...] = (
    "source",
    "topic",
    "trend",
    "tool",
    "model",
    "glossary",
    "how_to",
    "impl_study",
)


def render_indexes(graph: KnowledgeGraph) -> list[RenderedFile]:
    """Render all generated index pages."""
    files = [
        _master_index(),
        _aliases_index(graph),
        _knowledge_graph_index(graph),
    ]
    for category in CATEGORY_INDEXES:
        files.append(_by_tag_index(graph, category))
    files.append(_monthly_index("signals-by-month", graph.signals))
    files.append(_monthly_index("interview-insights-by-month", graph.insights))
    return files


def _master_index() -> RenderedFile:
    """Render the index directory landing page."""
    names = [
        "sources-by-tag",
        "topics-by-tag",
        "trends-by-tag",
        "tools-by-tag",
        "models-by-tag",
        "glossary-by-tag",
        "how-to-by-tag",
        "implementation-studies-by-tag",
        "signals-by-month",
        "interview-insights-by-month",
        "aliases",
        "knowledge-graph",
    ]
    body = heading(1, "Generated Indexes")
    body += bullet_list(layout.wikilink(f"{layout.INDEXES}/{name}.md") for name in names)
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/index.md",
        text=markdown_document({"title": "Generated Indexes", "category": "index"}, body),
    )


def _by_tag_index(graph: KnowledgeGraph, category: str) -> RenderedFile:
    """Render pages in a category grouped by tag."""
    pages = _category_pages(graph, category)
    grouped: dict[str, list[IndexItem]] = defaultdict(list)
    if category == "source":
        for source in graph.sources:
            for tag in sorted(source.source_tags):
                grouped[tag].append(source)
    else:
        for page in pages:
            for tag in page.tags or ["untagged"]:
                grouped[tag].append(page)
    body = heading(1, _index_title(category))
    if not grouped:
        body += "No pages captured.\n\n"
    for tag in sorted(grouped):
        body += heading(2, tag)
        body += bullet_list(_link_for_index_item(item) for item in grouped[tag])
    name = _index_name(category)
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/{name}.md",
        text=markdown_document({"title": _index_title(category), "category": "index"}, body),
    )


def _monthly_index(name: str, items: list[IndividualPage]) -> RenderedFile:
    """Render chronological individual pages grouped by month."""
    grouped: dict[str, list[IndividualPage]] = defaultdict(list)
    for item in items:
        grouped[item.month].append(item)
    body = heading(1, name.replace("-", " ").title())
    if not grouped:
        body += "No pages captured.\n\n"
    for month in sorted(grouped, reverse=True):
        body += heading(2, month)
        body += bullet_list(layout.wikilink(item.path, item.title) for item in grouped[month])
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/{name}.md",
        text=markdown_document(
            {"title": name.replace("-", " ").title(), "category": "index"},
            body,
        ),
    )


def _aliases_index(graph: KnowledgeGraph) -> RenderedFile:
    """Render canonical page aliases for ontology maintenance."""
    body = heading(1, "Aliases")
    pages = [page for page in graph.knowledge_pages if page.aliases]
    if not pages:
        body += "No aliases captured.\n\n"
    for page in sorted(pages, key=lambda item: (item.category, item.title)):
        body += heading(2, page.title)
        body += bullet_list(page.aliases)
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/aliases.md",
        text=markdown_document({"title": "Aliases", "category": "diagnostics"}, body),
    )


def _knowledge_graph_index(graph: KnowledgeGraph) -> RenderedFile:
    """Render graph diagnostics."""
    body = heading(1, "Knowledge Graph Diagnostics")
    body += bullet_list(
        [
            f"Tool version: `{TOOL_VERSION}`",
            f"Taxonomy version: `{graph.taxonomy_version}`",
            f"Sources: {len(graph.sources)}",
            f"Knowledge pages: {len(graph.knowledge_pages)}",
            f"Signals: {len(graph.signals)}",
            f"Interview insights: {len(graph.insights)}",
        ]
    )
    for category in ("topic", "trend", "tool", "model"):
        pages = _category_pages(graph, category)
        body += heading(2, f"All {category}s")
        body += bullet_list(
            f"{layout.wikilink(page.path, page.title)} — sources: {page.source_count}, "
            f"evidence: {page.evidence_count}"
            for page in pages
        )
    duplicate_pages = [page for page in graph.knowledge_pages if page.duplicate_candidates]
    body += heading(2, "Duplicate candidates")
    body += (
        bullet_list(
            f"{layout.wikilink(page.path, page.title)}: {', '.join(page.duplicate_candidates)}"
            for page in duplicate_pages
        )
        or "No duplicate candidates captured.\n\n"
    )
    sources_without_pages = [
        source
        for source in graph.sources
        if not any(key.startswith("derived_") and values for key, values in source.derived.items())
    ]
    body += heading(2, "Sources without derived knowledge pages")
    body += (
        bullet_list(
            layout.wikilink(f"{layout.SOURCES}/{source.source_id}.md", source.title)
            for source in sources_without_pages
        )
        or "No source-only pages captured.\n\n"
    )
    body += heading(2, "Most-used tags")
    tag_counts = Counter(tag for page in graph.knowledge_pages for tag in page.tags)
    body += bullet_list(f"{tag}: {count}" for tag, count in tag_counts.most_common(25))
    body += heading(2, "Pages with contradictions")
    body += (
        bullet_list(
            layout.wikilink(page.path, page.title)
            for page in graph.knowledge_pages
            if page.stance_counts.get("counter", 0) or page.stance_counts.get("uncertainty", 0)
        )
        or "No contradiction or uncertainty evidence captured.\n\n"
    )
    body += heading(2, "Highest source-count pages")
    by_source_count = sorted(
        graph.knowledge_pages,
        key=lambda item: item.source_count,
        reverse=True,
    )
    body += bullet_list(
        f"{layout.wikilink(page.path, page.title)} — {page.source_count}"
        for page in by_source_count[:25]
    )
    body += heading(2, "Highest evidence-count pages")
    by_evidence_count = sorted(
        graph.knowledge_pages,
        key=lambda item: item.evidence_count,
        reverse=True,
    )
    body += bullet_list(
        f"{layout.wikilink(page.path, page.title)} — {page.evidence_count}"
        for page in by_evidence_count[:25]
    )
    body += heading(2, "Thinly-supported pages")
    body += (
        bullet_list(
            f"{layout.wikilink(page.path, page.title)} — sources: {page.source_count}, "
            f"evidence: {page.evidence_count}"
            for page in graph.knowledge_pages
            if page.source_count >= 3 and page.evidence_count <= page.source_count
        )
        or "No thinly-supported multi-source pages captured.\n\n"
    )
    return RenderedFile(
        relative_path=f"{layout.INDEXES}/knowledge-graph.md",
        text=markdown_document(
            {"title": "Knowledge Graph Diagnostics", "category": "diagnostics"},
            body,
        ),
    )


def _category_pages(graph: KnowledgeGraph, category: str) -> list[KnowledgePage]:
    """Return knowledge pages for an index category."""
    if category == "source":
        return []
    return sorted(
        [page for page in graph.knowledge_pages if page.category == category],
        key=lambda item: item.title,
    )


def _link_for_index_item(item: IndexItem) -> str:
    """Return a wikilink for a source or page-like item."""
    if isinstance(item, KnowledgePage):
        return layout.wikilink(item.path, item.title)
    source_id = item.source_id
    title = item.title
    return layout.wikilink(f"{layout.SOURCES}/{source_id}.md", title)


def _index_name(category: str) -> str:
    """Return generated index filename by category."""
    return {
        "source": "sources-by-tag",
        "topic": "topics-by-tag",
        "trend": "trends-by-tag",
        "tool": "tools-by-tag",
        "model": "models-by-tag",
        "glossary": "glossary-by-tag",
        "how_to": "how-to-by-tag",
        "impl_study": "implementation-studies-by-tag",
    }[category]


def _index_title(category: str) -> str:
    """Return generated index title by category."""
    return _index_name(category).replace("-", " ").title()
