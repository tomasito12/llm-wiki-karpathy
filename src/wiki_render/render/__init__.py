"""Markdown renderers for generated wiki pages."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render.models import KnowledgeGraph, RenderedFile
from src.wiki_render.render.indexes import render_indexes
from src.wiki_render.render.knowledge import (
    render_implementation_study_page,
    render_individual_page,
    render_knowledge_page,
)
from src.wiki_render.render.source import render_source_page


def render_graph(graph: KnowledgeGraph, *, wiki_dir: Path) -> list[RenderedFile]:
    """Render the full graph to markdown files."""
    files: list[RenderedFile] = []
    files.extend(render_source_page(source, wiki_dir=wiki_dir) for source in graph.sources)
    files.extend(render_knowledge_page(page) for page in graph.knowledge_pages)
    files.extend(render_individual_page(item) for item in graph.signals)
    files.extend(render_individual_page(item) for item in graph.insights)
    files.extend(render_implementation_study_page(item) for item in graph.implementation_studies)
    files.extend(render_indexes(graph))
    return files
