"""Tests for Stage 2 synthesis execution."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.executor import (
    normalize_synthesis_payload,
    run_synthesis,
)
from src.wiki_synthesis.prompts import PromptBundle, build_prompt_bundle


def test_run_synthesis_dry_run_plans_without_calling_provider(tmp_path: Path) -> None:
    """Dry-run should select executable targets without calling the provider."""
    provider = RaisingProvider()

    report = run_synthesis(
        _graph(),
        cache_dir=tmp_path / "cache",
        provider=provider,
        model="test-model",
        entity="topic:local-models",
        dry_run=True,
    )

    assert report.planned == 1
    assert report.called == 0
    assert report.written == 0
    assert report.items[0].action == "planned"


def test_run_synthesis_skips_single_source_by_default(tmp_path: Path) -> None:
    """Single-source pages should remain skipped unless explicitly included."""
    report = run_synthesis(
        _graph(source_count=1),
        cache_dir=tmp_path / "cache",
        provider=RaisingProvider(),
        model="test-model",
        entity="topic:local-models",
        dry_run=True,
    )

    assert report.planned == 0
    assert report.items == []


def test_run_synthesis_can_include_single_source_pages(tmp_path: Path) -> None:
    """The executor should plan single-source pages when explicitly requested."""
    report = run_synthesis(
        _graph(source_count=1),
        cache_dir=tmp_path / "cache",
        provider=RaisingProvider(),
        model="test-model",
        entity="topic:local-models",
        include_single_source=True,
        dry_run=True,
    )

    assert report.planned == 1
    assert report.items[0].state == "new"


def test_run_synthesis_writes_validated_cache(tmp_path: Path) -> None:
    """A valid provider response should become a cache file."""
    graph = _graph()
    cache_dir = tmp_path / "cache"

    report = run_synthesis(
        graph,
        cache_dir=cache_dir,
        provider=StaticProvider(_provider_payload()),
        model="test-model",
        entity="topic:local-models",
        dry_run=False,
        now_fn=lambda: datetime(2026, 6, 16, 12, 0, tzinfo=UTC),
    )

    cache_path = cache_file_path(cache_dir, category="topic", slug="local-models")
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert report.called == 1
    assert report.written == 1
    assert payload["entity_id"] == "topic:local-models"
    assert payload["synthesis_input_hash"] == report.items[0].current_input_hash
    assert payload["last_synthesized_at"] == "2026-06-16T12:00:00Z"
    assert payload["executive_synthesis"] == "Local models make inference controllable."
    assert payload["practical_example"]["basis"] == "illustrative"
    assert report.items[0].model == "test-model"
    assert report.items[0].provider_request_id == "test-topic:local-models-test-model"
    assert report.items[0].token_usage == {"total_tokens": 123}


def test_run_synthesis_rejects_incomplete_provider_payload(tmp_path: Path) -> None:
    """Incomplete provider output should fail before writing cache."""
    with pytest.raises(ValueError, match="Missing required text field"):
        run_synthesis(
            _graph(),
            cache_dir=tmp_path / "cache",
            provider=StaticProvider({"what_to_remember": ["x"]}),
            model="test-model",
            entity="topic:local-models",
            dry_run=False,
        )

    cache_path = cache_file_path(tmp_path / "cache", category="topic", slug="local-models")
    assert not cache_path.exists()


def test_normalize_synthesis_payload_overwrites_untrusted_metadata() -> None:
    """Provider metadata should not override locally trusted cache metadata."""
    bundle = build_prompt_bundle(_graph(), entity_id="topic:local-models")

    payload = normalize_synthesis_payload(
        {
            **_provider_payload(),
            "entity_id": "topic:wrong",
            "synthesis_input_hash": "wronghash",
        },
        bundle=bundle,
        now=datetime(2026, 6, 16, 12, 0, tzinfo=UTC),
    )

    assert payload["entity_id"] == "topic:local-models"
    assert payload["synthesis_input_hash"] == bundle.synthesis_input_hash


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
        "practical_example": _practical_example(),
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


def _practical_example() -> dict[str, str]:
    """Return a complete practical-example payload."""
    return {
        "title": "Local assistant for private support drafts",
        "example": (
            "A support team could run a local model to draft first-pass answers for "
            "internal knowledge-base questions before any sensitive customer details "
            "leave the laptop or internal network."
        ),
        "why_it_helps": "It makes the privacy and latency tradeoff concrete.",
        "basis": "illustrative",
    }


def _graph(*, source_count: int = 2) -> dict[str, Any]:
    """Return a minimal graph export with one executable knowledge page."""
    source_ids = ["source-a", "source-b"][:source_count]
    return {
        "sources": [
            {
                "source_id": "source-a",
                "title": "Source A",
                "published_date": "2026-01-01",
                "assessed_as_of": "2026-06-16",
                "tags": ["ai-engineering"],
            },
            {
                "source_id": "source-b",
                "title": "Source B",
                "published_date": "2026-02-01",
                "assessed_as_of": "2026-06-16",
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
                        "evidence_id": "evidence-a",
                        "text": "Local models run near users.",
                        "source_id": "source-a",
                        "source_title": "Source A",
                        "source_date": "2026-01-01",
                        "published_date": "2026-01-01",
                        "assessed_as_of": "2026-06-16",
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
