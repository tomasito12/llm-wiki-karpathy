"""Tests for Stage 2 synthesis cache linting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json
from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.cache_lint import lint_synthesis_cache
from src.wiki_synthesis.input_hash import synthesis_input_hash


def test_lint_synthesis_cache_marks_fresh_cache_ok(tmp_path: Path) -> None:
    """A complete matching cache should lint as ok."""
    graph = _graph()
    page = graph["knowledge_pages"][0]
    atomic_write_json(
        cache_file_path(tmp_path / "cache", category="topic", slug="local-models"),
        _cache_entry(page, synthesis_input_hash(page)),
    )

    report = lint_synthesis_cache(graph, cache_dir=tmp_path / "cache")

    assert report.ok == 1
    assert report.warnings == 0
    assert report.errors == 0
    assert report.exit_code == 0


def test_lint_synthesis_cache_marks_stale_cache_warning(tmp_path: Path) -> None:
    """A complete mismatched cache should lint as a warning."""
    graph = _graph()
    page = graph["knowledge_pages"][0]
    atomic_write_json(
        cache_file_path(tmp_path / "cache", category="topic", slug="local-models"),
        _cache_entry(page, "oldhash"),
    )

    report = lint_synthesis_cache(graph, cache_dir=tmp_path / "cache")

    assert report.ok == 0
    assert report.warnings == 1
    assert report.errors == 0
    assert report.items[0].state == "stale"
    assert report.exit_code == 0


def test_lint_synthesis_cache_marks_invalid_cache_error(tmp_path: Path) -> None:
    """An incomplete cache should lint as an error."""
    graph = _graph()
    atomic_write_json(
        cache_file_path(tmp_path / "cache", category="topic", slug="local-models"),
        {"synthesis_input_hash": "hash"},
    )

    report = lint_synthesis_cache(graph, cache_dir=tmp_path / "cache")

    assert report.errors == 1
    assert report.items[0].state == "invalid"
    assert report.exit_code == 1


def test_lint_synthesis_cache_marks_orphan_cache_error(tmp_path: Path) -> None:
    """A cache file without a matching graph page should lint as an error."""
    atomic_write_json(
        cache_file_path(tmp_path / "cache", category="topic", slug="orphan"),
        {"synthesis_input_hash": "hash"},
    )

    report = lint_synthesis_cache(_graph(), cache_dir=tmp_path / "cache")

    assert report.errors == 1
    assert report.items[0].state == "orphan"
    assert report.exit_code == 1


def test_lint_synthesis_cache_can_require_missing_entity_cache(tmp_path: Path) -> None:
    """A requested missing entity cache should lint as an error."""
    report = lint_synthesis_cache(
        _graph(),
        cache_dir=tmp_path / "cache",
        entity="topic:local-models",
        include_missing=True,
    )

    assert report.errors == 1
    assert report.items[0].state == "invalid"
    assert report.items[0].reason == "cache entry is missing"


def test_lint_synthesis_cache_ignores_missing_entity_cache_by_default(tmp_path: Path) -> None:
    """A missing entity cache should be ignored unless explicitly required."""
    report = lint_synthesis_cache(
        _graph(),
        cache_dir=tmp_path / "cache",
        entity="topic:local-models",
    )

    assert report.checked == 0
    assert report.errors == 0


def _cache_entry(page: dict[str, Any], input_hash: str) -> dict[str, Any]:
    """Return a complete minimal cache entry."""
    return {
        "entity_id": page["entity_id"],
        "category": page["category"],
        "slug": page["slug"],
        "title": page["title"],
        "synthesis_input_hash": input_hash,
        "executive_synthesis": "Local models make inference controllable.",
        "what_to_remember": ["Use them when privacy or latency matters."],
        "consensus": ["They trade hosted convenience for control."],
        "tensions": ["They add operational work."],
        "evidence_quality": ["Two sources with consistent practitioner claims."],
        "practical_takeaway": "Start with narrow workloads before broad rollout.",
    }


def _graph() -> dict[str, Any]:
    """Return a minimal graph export with one knowledge page."""
    return {
        "knowledge_pages": [
            {
                "entity_id": "topic:local-models",
                "category": "topic",
                "slug": "local-models",
                "title": "Local Models",
                "path": "topics/local-models.md",
                "aliases": [],
                "tags": ["ai-engineering"],
                "types": [],
                "source_ids": ["source-a", "source-b"],
                "source_count": 2,
                "evidence_count": 1,
                "value_level": "high",
                "confidence": 0.9,
                "supporting_count": 1,
                "counter_count": 0,
                "uncertainty_count": 0,
                "neutral_count": 0,
                "evidence": [
                    {
                        "evidence_id": "evidence-a",
                        "text": "Local models run near users.",
                        "source_id": "source-a",
                        "field": "knowledge_summary",
                        "stance": "supporting",
                    }
                ],
            }
        ]
    }
