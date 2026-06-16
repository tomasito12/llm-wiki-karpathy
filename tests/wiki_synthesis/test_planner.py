"""Tests for Stage 2 synthesis planning."""

from __future__ import annotations

import json
from pathlib import Path

from src.pipeline.atomic import atomic_write_json
from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.input_hash import synthesis_input_hash
from src.wiki_synthesis.planner import plan_from_graph


def test_plan_skips_single_source_pages_by_default(tmp_path: Path) -> None:
    """Single-source knowledge pages should not trigger Stage 2 by default."""
    graph = {"knowledge_pages": [_page(source_count=1)], "signals": [{}]}

    plan = plan_from_graph(graph, cache_dir=tmp_path / "cache")

    assert plan.summary.skipped_single_source == 1
    assert plan.summary.skipped_evidence_object == 1
    assert plan.entries[0].state == "skipped_single_source"


def test_plan_marks_uncached_multi_source_page_new(tmp_path: Path) -> None:
    """A multi-source page without cache should be planned as new."""
    graph = {"knowledge_pages": [_page(source_count=2)]}

    plan = plan_from_graph(graph, cache_dir=tmp_path / "cache")

    assert plan.summary.new == 1
    assert plan.entries[0].state == "new"


def test_plan_marks_matching_cache_unchanged(tmp_path: Path) -> None:
    """A matching cached input hash should avoid synthesis work."""
    page = _page(source_count=2)
    cache_path = cache_file_path(tmp_path / "cache", category="topic", slug="local-models")
    atomic_write_json(cache_path, _cache_entry(page, synthesis_input_hash(page)))

    plan = plan_from_graph({"knowledge_pages": [page]}, cache_dir=tmp_path / "cache")

    assert plan.summary.unchanged == 1
    assert plan.entries[0].state == "unchanged"


def test_plan_marks_mismatched_cache_stale(tmp_path: Path) -> None:
    """A mismatched cached input hash should mark a page stale."""
    page = _page(source_count=2)
    cache_path = cache_file_path(tmp_path / "cache", category="topic", slug="local-models")
    atomic_write_json(cache_path, _cache_entry(page, "oldhash"))

    plan = plan_from_graph({"knowledge_pages": [page]}, cache_dir=tmp_path / "cache")

    assert plan.summary.stale == 1
    assert plan.entries[0].state == "stale"


def test_plan_changed_only_hides_unchanged_entries(tmp_path: Path) -> None:
    """Changed-only output should keep summary counts but hide unchanged entries."""
    page = _page(source_count=2)
    cache_path = cache_file_path(tmp_path / "cache", category="topic", slug="local-models")
    atomic_write_json(cache_path, _cache_entry(page, synthesis_input_hash(page)))

    plan = plan_from_graph(
        {"knowledge_pages": [page]},
        cache_dir=tmp_path / "cache",
        changed_only=True,
    )

    assert plan.summary.unchanged == 1
    assert plan.summary.shown == 0
    assert plan.entries == []


def test_loadable_cache_json_is_stable(tmp_path: Path) -> None:
    """Cache files should be ordinary JSON artifacts."""
    page = _page(source_count=2)
    cache_path = cache_file_path(tmp_path / "cache", category="topic", slug="local-models")
    atomic_write_json(cache_path, _cache_entry(page, synthesis_input_hash(page)))

    assert json.loads(cache_path.read_text(encoding="utf-8"))["synthesis_input_hash"]


def test_plan_marks_incomplete_cache_as_error(tmp_path: Path) -> None:
    """A cache file with only a hash should not be treated as renderable synthesis."""
    page = _page(source_count=2)
    cache_path = cache_file_path(tmp_path / "cache", category="topic", slug="local-models")
    atomic_write_json(cache_path, {"synthesis_input_hash": synthesis_input_hash(page)})

    plan = plan_from_graph({"knowledge_pages": [page]}, cache_dir=tmp_path / "cache")

    assert plan.summary.error == 1
    assert plan.entries[0].state == "error"


def _page(*, source_count: int) -> dict[str, object]:
    """Return a minimal graph-export knowledge page."""
    source_ids = [f"source-{index}" for index in range(source_count)]
    return {
        "entity_id": "topic:local-models",
        "category": "topic",
        "slug": "local-models",
        "title": "Local Models",
        "path": "topics/local-models.md",
        "aliases": [],
        "tags": ["infrastructure"],
        "types": [],
        "source_ids": source_ids,
        "source_count": source_count,
        "evidence_count": 1,
        "value_level": "high",
        "confidence": 0.9,
        "supporting_count": 1,
        "counter_count": 0,
        "uncertainty_count": 0,
        "neutral_count": 0,
        "evidence": [
            {
                "evidence_id": "abc",
                "text": "Local models run near users.",
                "source_id": "source-0",
                "field": "knowledge_summary",
                "stance": "neutral",
            }
        ],
    }


def _cache_entry(page: dict[str, object], input_hash: str) -> dict[str, object]:
    """Return a complete minimal synthesis cache entry for a page."""
    return {
        "entity_id": page["entity_id"],
        "category": page["category"],
        "slug": page["slug"],
        "title": page["title"],
        "synthesis_input_hash": input_hash,
        "executive_synthesis": "Local models run near users.",
        "what_to_remember": ["They can reduce hosted API dependency."],
        "consensus": ["Useful for privacy or latency needs."],
        "tensions": ["Operational overhead can outweigh control."],
        "evidence_quality": ["Small but consistent evidence set."],
        "practical_takeaway": "Use when control matters more than convenience.",
    }
