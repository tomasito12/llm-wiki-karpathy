"""Tests for generated wiki indexes."""

from __future__ import annotations

from src.wiki_render.models import KnowledgeGraph, SourceRecord
from src.wiki_render.render.indexes import render_indexes


def test_system_status_index_is_stable_between_renders() -> None:
    """Rendering indexes twice with the same graph produces identical output."""
    graph = KnowledgeGraph(
        sources=[
            _source_record(
                source_id="source-a",
                ingested_at="2026-06-17T12:00:00Z",
                published_date="May 2026",
            )
        ],
        knowledge_pages=[],
        signals=[],
        insights=[],
        implementation_studies=[],
        alias_map={},
        taxonomy_version="test-taxonomy",
    )

    first = _rendered_text(graph, "indexes/system-status.md")
    second = _rendered_text(graph, "indexes/system-status.md")

    assert first == second
    assert "Graph snapshot: `2026-06-17T12:00:00Z`" in first
    assert "rendered_at" not in first


def test_system_status_index_handles_empty_graph() -> None:
    """An empty graph still renders a deterministic status page."""
    graph = KnowledgeGraph(
        sources=[],
        knowledge_pages=[],
        signals=[],
        insights=[],
        implementation_studies=[],
        alias_map={},
        taxonomy_version="test-taxonomy",
    )

    text = _rendered_text(graph, "indexes/system-status.md")

    assert "Graph snapshot: `unknown`" in text


def _rendered_text(graph: KnowledgeGraph, relative_path: str) -> str:
    """Return a rendered index text by path."""
    rendered = {file.relative_path: file.text for file in render_indexes(graph)}
    return rendered[relative_path]


def _source_record(
    source_id: str,
    ingested_at: str,
    published_date: str = "2026-01-01",
) -> SourceRecord:
    """Build a minimal source record for index tests."""
    return SourceRecord(
        source_id=source_id,
        title="Source A",
        author="",
        publication="",
        canonical_url="",
        published_date=published_date,
        assessed_as_of="2026-06-16T12:00:00Z",
        ingested_at=ingested_at,
        content_sha256="hash",
        raw_md_rel_path="raw/readwise/source-a.md",
        raw_html_rel_path="raw/readwise/source-a.html",
        summary="",
        accessible_overview="",
        key_insights=[],
        why_it_matters="",
        limitations_and_open_questions="",
        contradictions_and_skepticism="",
    )
