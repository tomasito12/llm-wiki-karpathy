"""Tests for Stage 2 synthesis review previews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json
from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.input_hash import synthesis_input_hash
from src.wiki_synthesis.review import build_review_preview


def test_build_review_preview_writes_synthesized_markdown(tmp_path: Path) -> None:
    """A fresh cache entry should render and write a synthesized preview."""
    graph = _graph()
    page = graph["knowledge_pages"][0]
    cache_dir = tmp_path / "cache"
    preview_dir = tmp_path / "previews"
    atomic_write_json(
        cache_file_path(cache_dir, category="topic", slug="local-models"),
        _cache_payload(page),
    )

    report, rendered = build_review_preview(
        graph,
        entity_id="topic:local-models",
        cache_dir=cache_dir,
        preview_dir=preview_dir,
    )

    preview_path = preview_dir / "topic" / "local-models.md"
    assert report.validation_state == "fresh"
    assert report.rendered_synthesis_state == "synthesized"
    assert report.wrote_preview
    assert preview_path.exists()
    assert "synthesis_state: synthesized" in rendered.text
    assert "Local models make inference controllable." in preview_path.read_text(encoding="utf-8")


def test_build_review_preview_reports_missing_cache_without_writing_on_dry_run(
    tmp_path: Path,
) -> None:
    """Dry-run should report missing cache and avoid writing a preview file."""
    report, rendered = build_review_preview(
        _graph(),
        entity_id="topic:local-models",
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        dry_run=True,
    )

    assert report.validation_state == "invalid"
    assert report.rendered_synthesis_state == "stage1-placeholder"
    assert not report.wrote_preview
    assert not Path(report.preview_path).exists()
    assert "synthesis_state: stage1-placeholder" in rendered.text


def _cache_payload(page: dict[str, Any]) -> dict[str, Any]:
    """Return a complete synthesis cache payload for a page."""
    return {
        "entity_id": page["entity_id"],
        "category": page["category"],
        "slug": page["slug"],
        "title": page["title"],
        "synthesis_schema_version": 1,
        "synthesis_prompt_version": 1,
        "synthesis_input_hash": synthesis_input_hash(page),
        "last_synthesized_at": "2026-06-17T00:00:00Z",
        "executive_synthesis": "Local models make inference controllable.",
        "what_to_remember": ["Use them when privacy or latency matters."],
        "consensus": ["They trade hosted convenience for control."],
        "tensions": ["They add operational work."],
        "evidence_quality": ["Two sources with consistent practitioner claims."],
        "practical_takeaway": "Start with narrow workloads before broad rollout.",
        "context_card": {
            "use_this_page_when": "Answering local deployment questions.",
            "best_for_questions_about": ["privacy", "latency"],
            "not_enough_for": ["benchmark selection"],
            "strongest_sources": ["Source A"],
            "related_tags": ["ai-engineering"],
        },
    }


def _graph() -> dict[str, Any]:
    """Return a minimal graph export with one knowledge page."""
    return {
        "sources": [
            {
                "source_id": "source-a",
                "title": "Source A",
                "published_date": "2026-01-01",
                "assessed_as_of": "2026-06-17",
                "tags": ["ai-engineering"],
            },
            {
                "source_id": "source-b",
                "title": "Source B",
                "published_date": "2026-02-01",
                "assessed_as_of": "2026-06-17",
                "tags": ["inference-systems"],
            },
        ],
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
                "first_seen": "2026-01-01",
                "last_seen": "2026-06-17",
                "source_ids": ["source-a", "source-b"],
                "source_count": 2,
                "evidence_count": 1,
                "value_level": "high",
                "confidence": 0.9,
                "supporting_count": 1,
                "counter_count": 0,
                "uncertainty_count": 0,
                "neutral_count": 0,
                "evidence_set_hash": "hash",
                "evidence": [
                    {
                        "evidence_id": "evidence-a",
                        "text": "Local models run near users.",
                        "source_id": "source-a",
                        "source_title": "Source A",
                        "source_date": "2026-01-01",
                        "published_date": "2026-01-01",
                        "assessed_as_of": "2026-06-17",
                        "ingested_at": "2026-06-17T00:00:00Z",
                        "category": "topic",
                        "entity_slug": "local-models",
                        "confidence": 0.9,
                        "value_level": "high",
                        "provenance": "summary",
                        "stance": "supporting",
                        "evidence_type": "claim",
                        "field": "knowledge_summary",
                    }
                ],
            }
        ],
    }
