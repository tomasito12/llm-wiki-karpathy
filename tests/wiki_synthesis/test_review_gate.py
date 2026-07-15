"""Tests for synthesis review gating."""

from __future__ import annotations

from src.wiki_synthesis.planner import plan_from_graph
from src.wiki_synthesis.review_gate import (
    knowledge_page_source_ids,
    page_uses_only_finished_sources,
)


def test_knowledge_page_source_ids_reads_source_ids_field() -> None:
    """Knowledge pages should expose their contributing source ids."""
    page = {"source_ids": ["source-a", "source-b"], "evidence": []}

    assert knowledge_page_source_ids(page) == {"source-a", "source-b"}


def test_page_uses_only_finished_sources_rejects_mixed_pages() -> None:
    """Synthesis should skip pages that still depend on in-progress sources."""
    page = {"source_ids": ["finished-a", "pending-b"]}

    assert page_uses_only_finished_sources(page, {"finished-a"}) is False
    assert page_uses_only_finished_sources(page, {"finished-a", "pending-b"}) is True


def test_plan_skips_pages_with_in_progress_sources(tmp_path) -> None:
    """Planner should mark mixed-source pages as skipped_in_progress_source."""
    graph = {
        "knowledge_pages": [
            {
                "entity_id": "topic:safe",
                "category": "topic",
                "slug": "safe",
                "title": "Safe",
                "path": "topics/safe.md",
                "aliases": [],
                "tags": [],
                "types": [],
                "source_ids": ["finished-a", "finished-b"],
                "source_count": 2,
                "evidence_count": 2,
                "value_level": "high",
                "confidence": 0.9,
                "evidence": [],
            },
            {
                "entity_id": "topic:mixed",
                "category": "topic",
                "slug": "mixed",
                "title": "Mixed",
                "path": "topics/mixed.md",
                "aliases": [],
                "tags": [],
                "types": [],
                "source_ids": ["finished-a", "pending-b"],
                "source_count": 2,
                "evidence_count": 2,
                "value_level": "high",
                "confidence": 0.9,
                "evidence": [],
            },
        ]
    }

    plan = plan_from_graph(
        graph,
        cache_dir=tmp_path / "cache",
        finished_source_ids={"finished-a", "finished-b"},
    )

    assert plan.summary.skipped_in_progress_source == 1
    states = {entry.slug: entry.state for entry in plan.entries}
    assert states["safe"] == "new"
    assert states["mixed"] == "skipped_in_progress_source"
