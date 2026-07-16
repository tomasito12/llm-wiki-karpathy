"""Tests for Stage 2 operational index rendering."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_synthesis import indexes_cli
from src.wiki_synthesis.indexes import render_synthesis_indexes
from src.wiki_synthesis.planner import plan_from_graph
from tests.wiki_synthesis.review_fixture import write_finished_review, write_paths_config


def test_render_needs_synthesis_index_lists_new_pages(tmp_path: Path) -> None:
    """The needs-synthesis index should expose new synthesis candidates."""
    graph = _graph()
    plan = plan_from_graph(graph, cache_dir=tmp_path / "cache")

    files = render_synthesis_indexes(graph, plan, tags=["ai-engineering"])
    page = next(file for file in files if file.relative_path == "indexes/needs-synthesis.md")

    assert "title: Needs Synthesis" in page.text
    assert "[[topics/context-engineering|Context Engineering]]" in page.text
    assert "sources: 3" in page.text
    assert "evidence: 9" in page.text


def test_render_tag_hub_groups_human_and_llm_entry_points(tmp_path: Path) -> None:
    """A tag hub should group useful pages by intent-oriented section."""
    graph = _graph()
    plan = plan_from_graph(graph, cache_dir=tmp_path / "cache")

    files = render_synthesis_indexes(graph, plan, tags=["ai-engineering"])
    page = next(file for file in files if file.relative_path == "indexes/tags/ai-engineering.md")

    assert "tag: ai-engineering" in page.text
    assert "## Best entry points" in page.text
    assert "## How-to answers" in page.text
    assert "## Concepts and definitions" in page.text
    assert "## Primary sources" in page.text
    assert "[[how-to/evaluation-of-a-rag-system|Evaluation of a RAG System]]" in page.text
    assert "[[sources/source-a|Source A]]" in page.text
    assert "LLM context recipe" in page.text


def test_indexes_cli_paths_config_overrides_graph_cache_and_wiki_dir(
    tmp_path: Path,
) -> None:
    """Indexes CLI should write synthesis indexes into the configured vault."""
    external = tmp_path / "external"
    graph_path = external / "state" / "wiki_render_graph.json"
    cache_dir = external / "state" / "synthesis"
    reviews_dir = external / "state" / "reviews"
    wiki_dir = external / "vault" / "wiki"
    graph_path.parent.mkdir(parents=True)
    cache_dir.mkdir(parents=True)
    write_finished_review(reviews_dir, "source-a")
    write_finished_review(reviews_dir, "source-b")
    write_finished_review(reviews_dir, "source-c")
    graph_path.write_text(json.dumps(_graph()), encoding="utf-8")
    config_path = write_paths_config(
        tmp_path,
        graph_path=graph_path,
        cache_dir=cache_dir,
        reviews_dir=reviews_dir,
        wiki_dir=wiki_dir,
    )

    exit_code = indexes_cli.main(
        [
            "--paths-config",
            str(config_path),
            "--tag",
            "ai-engineering",
        ]
    )

    assert exit_code == 0
    assert (wiki_dir / "indexes" / "needs-synthesis.md").exists()
    assert (wiki_dir / "indexes" / "synthesis-status.md").exists()
    assert (wiki_dir / "indexes" / "tags" / "ai-engineering.md").exists()
    assert not (tmp_path / "wiki" / "indexes" / "needs-synthesis.md").exists()


def _graph() -> dict[str, object]:
    """Return a small graph export with mixed page types."""
    return {
        "knowledge_pages": [
            {
                "entity_id": "topic:context-engineering",
                "category": "topic",
                "slug": "context-engineering",
                "title": "Context Engineering",
                "path": "topics/context-engineering.md",
                "aliases": [],
                "tags": ["ai-engineering", "context-engineering"],
                "types": [],
                "source_ids": ["source-a", "source-b", "source-c"],
                "source_count": 3,
                "evidence_count": 9,
                "value_level": "high",
                "confidence": 0.94,
                "supporting_count": 4,
                "counter_count": 0,
                "uncertainty_count": 1,
                "neutral_count": 4,
                "synthesis_state": "stage1-placeholder",
                "evidence": [{"evidence_id": "a", "text": "Context matters."}],
            },
            {
                "entity_id": "how_to:evaluation-of-a-rag-system",
                "category": "how_to",
                "slug": "evaluation-of-a-rag-system",
                "title": "Evaluation of a RAG System",
                "path": "how-to/evaluation-of-a-rag-system.md",
                "aliases": [],
                "tags": ["ai-engineering"],
                "types": [],
                "source_ids": ["source-a", "source-b"],
                "source_count": 2,
                "evidence_count": 6,
                "value_level": "high",
                "confidence": 0.91,
                "supporting_count": 3,
                "counter_count": 0,
                "uncertainty_count": 0,
                "neutral_count": 3,
                "synthesis_state": "stage1-placeholder",
                "evidence": [{"evidence_id": "b", "text": "Evaluate retrieval."}],
            },
        ],
        "sources": [
            {
                "source_id": "source-a",
                "title": "Source A",
                "tags": ["ai-engineering"],
            }
        ],
        "signals": [
            {
                "category": "signal",
                "title": "Signal A",
                "path": "signals/2026-06/source-a-signal-a.md",
                "tags": ["ai-engineering"],
                "evidence_count": 2,
            }
        ],
        "interview_insights": [],
        "implementation_studies": [],
    }
