"""Tests for the high-level Stage 2 synthesis workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.prompts import PromptBundle
from src.wiki_synthesis.workflow import run_synthesis_workflow, write_workflow_audit_report


def test_workflow_dry_run_plans_without_preview(tmp_path: Path) -> None:
    """Dry-run should plan work without calling a provider or writing previews."""
    report = run_synthesis_workflow(
        _graph(),
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        provider=RaisingProvider(),
        model="test-model",
        entity="topic:local-models",
        dry_run=True,
    )

    assert report.run.planned == 1
    assert report.run.called == 0
    assert report.run.written == 0
    assert report.reviews == []
    assert not (tmp_path / "previews").exists()


def test_workflow_real_run_writes_cache_and_review_preview(tmp_path: Path) -> None:
    """A real workflow run should write cache and render a review preview."""
    cache_dir = tmp_path / "cache"
    preview_dir = tmp_path / "previews"

    report = run_synthesis_workflow(
        _graph(),
        cache_dir=cache_dir,
        preview_dir=preview_dir,
        provider=StaticProvider(_provider_payload()),
        model="test-model",
        entity="topic:local-models",
        dry_run=False,
    )

    cache_path = cache_file_path(cache_dir, category="topic", slug="local-models")
    preview_path = preview_dir / "topic" / "local-models.md"
    assert report.run.called == 1
    assert report.run.written == 1
    assert len(report.reviews) == 1
    assert cache_path.exists()
    assert preview_path.exists()
    assert json.loads(cache_path.read_text(encoding="utf-8"))["entity_id"] == "topic:local-models"
    assert "synthesis_state: synthesized" in preview_path.read_text(encoding="utf-8")


def test_write_workflow_audit_report(tmp_path: Path) -> None:
    """Audit reports should preserve run, review, and option metadata."""
    report = run_synthesis_workflow(
        _graph(),
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        provider=StaticProvider(_provider_payload()),
        model="test-model",
        entity="topic:local-models",
        dry_run=False,
    )

    path = write_workflow_audit_report(
        report,
        report_dir=tmp_path / "runs",
        options={"entity": "topic:local-models", "model": "test-model"},
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["created_at"].endswith("Z")
    assert payload["options"]["entity"] == "topic:local-models"
    assert payload["run"]["written"] == 1
    assert payload["run"]["items"][0]["token_usage"] == {"total_tokens": 123}
    assert payload["reviews"][0]["rendered_synthesis_state"] == "synthesized"


class StaticProvider:
    """Provider returning a predefined payload."""

    def __init__(self, payload: dict[str, Any]) -> None:
        """Store the payload."""
        self.payload = payload

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return the stored payload."""
        return self.payload, {
            "request_id": f"test-{bundle.entity_id}-{model}",
            "token_usage": {"total_tokens": 123},
        }


class RaisingProvider:
    """Provider that fails if called."""

    def synthesize(
        self, bundle: PromptBundle, *, model: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Raise because dry-run should not call providers."""
        msg = f"unexpected call for {bundle.entity_id} with {model}"
        raise AssertionError(msg)


def _provider_payload() -> dict[str, Any]:
    """Return a complete provider synthesis payload."""
    return {
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
    """Return a minimal graph export with one executable knowledge page."""
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
