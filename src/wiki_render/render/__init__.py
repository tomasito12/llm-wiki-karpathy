"""Markdown renderers for generated wiki pages."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render import layout
from src.wiki_render.models import KnowledgeGraph, KnowledgePage, RenderedFile
from src.wiki_render.render.indexes import render_indexes
from src.wiki_render.render.knowledge import (
    RelatedPageIndex,
    render_implementation_study_page,
    render_individual_page,
    render_knowledge_page,
)
from src.wiki_render.render.source import render_source_page


def render_graph(
    graph: KnowledgeGraph,
    *,
    wiki_dir: Path,
    synthesis_cache_dir: Path | None = None,
) -> list[RenderedFile]:
    """Render the full graph to markdown files."""
    files: list[RenderedFile] = []
    related_page_index = _related_page_index(graph.knowledge_pages)
    files.extend(render_source_page(source, wiki_dir=wiki_dir) for source in graph.sources)
    files.extend(
        render_knowledge_page(
            page,
            synthesis_cache_dir=synthesis_cache_dir,
            related_page_index=related_page_index,
        )
        for page in graph.knowledge_pages
    )
    files.extend(render_individual_page(item) for item in graph.signals)
    files.extend(render_individual_page(item) for item in graph.insights)
    files.extend(render_implementation_study_page(item) for item in graph.implementation_studies)
    files.extend(render_indexes(graph))
    return files


def _related_page_index(pages: list[KnowledgePage]) -> RelatedPageIndex:
    """Return lookup keys for resolving reviewed related-page labels."""
    index: RelatedPageIndex = {}
    for page in pages:
        keys = {
            page.slug,
            page.title,
            page.path,
            page.path.removesuffix(".md"),
            *page.aliases,
        }
        for key in keys:
            clean = key.strip()
            if clean:
                index[(page.category, clean)] = page
                index[(page.category, layout.safe_slug(clean))] = page
    return index
