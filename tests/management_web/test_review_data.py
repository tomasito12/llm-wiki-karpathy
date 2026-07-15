"""Tests for read-only management web review data normalization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.management_web.review_data import (
    build_review_queue,
    get_source_detail,
    read_raw_markdown,
    validate_source_id,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def _paths(tmp_path: Path) -> WikiPaths:
    """Return repo-local wiki paths rooted in a temporary directory."""
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    paths.reviews_dir.mkdir(parents=True)
    return paths


def _write_raw(paths: WikiPaths, source_id: str, *, markdown: str | None = "Body") -> None:
    """Create a raw HTML export and optional Markdown sidecar."""
    (paths.raw_dir / f"{source_id}.html").write_text("<html>Article</html>", encoding="utf-8")
    if markdown is not None:
        (paths.raw_dir / f"{source_id}.md").write_text(markdown, encoding="utf-8")


def _write_artifact(
    paths: WikiPaths,
    source_id: str,
    artifact: dict[str, object],
) -> None:
    """Write one review artifact under the configured reviews directory."""
    review_dir = paths.reviews_dir / source_id
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text(json.dumps(artifact), encoding="utf-8")


def _artifact(*, finished: bool = False) -> dict[str, object]:
    """Return a minimal but representative review artifact."""
    review_finished_at = "2026-07-15T10:00:00Z" if finished else None
    return {
        "source": {
            "title": "Analyzed Article",
            "author": "Ada Lovelace",
            "publication": "Example Weekly",
            "published_date": "2026-07-01",
            "canonical_url": "https://example.test/article",
            "category": "article",
            "readwise_id": "rw-123",
            "raw_html": "raw/readwise/analyzed.html",
            "raw_md": "raw/readwise/analyzed.md",
            "content_sha256": "stored-hash",
        },
        "content_sha256": "stored-hash",
        "review_analytics": {"review_finished_at": review_finished_at},
        "llm_output": {
            "source_summary": {
                "summary": "A concise summary.",
                "key_insights": ["First useful insight", "Second useful insight"],
            },
            "topics": [
                {
                    "topic_title": "Agentic coding workflows",
                    "topic_description": "How agents shape software work.",
                    "topic_tags": ["ai-engineering", "agents"],
                    "evidence": "The article discusses coding agents.",
                }
            ],
            "glossary": [
                {
                    "term": "Retrieval augmented generation",
                    "definition": "Grounding generation with retrieved context.",
                    "tags": ["rag"],
                }
            ],
            "industry_trends": [
                {
                    "trend_title": "Teams adopt AI review assistants",
                    "trend_description": "Review assistants become part of delivery workflows.",
                    "trend_tags": ["software-delivery"],
                }
            ],
        },
    }


def test_build_review_queue_classifies_counts_and_items(tmp_path: Path) -> None:
    """Queue loading should classify pending, incomplete, in-progress, and finished sources."""
    paths = _paths(tmp_path)
    _write_raw(paths, "pending")
    _write_raw(paths, "incomplete", markdown=None)
    _write_raw(paths, "in-progress")
    _write_artifact(paths, "in-progress", _artifact())
    _write_raw(paths, "finished")
    _write_artifact(paths, "finished", _artifact(finished=True))

    queue = build_review_queue(paths, status="all", limit=10, offset=0, query=None)

    assert queue.counts.total == 4
    assert queue.counts.pending == 1
    assert queue.counts.incomplete == 1
    assert queue.counts.in_progress == 1
    assert queue.counts.finished == 1
    assert {item.source_id: item.status for item in queue.items} == {
        "finished": "finished",
        "in-progress": "in_progress",
        "incomplete": "incomplete",
        "pending": "pending",
    }


def test_build_review_queue_filters_searches_and_paginates(tmp_path: Path) -> None:
    """Queue filtering should apply status, text query, limit, and offset predictably."""
    paths = _paths(tmp_path)
    _write_raw(paths, "alpha-source")
    _write_artifact(paths, "alpha-source", _artifact())
    _write_raw(paths, "beta-source")
    _write_artifact(paths, "beta-source", _artifact())
    _write_raw(paths, "gamma-source")

    queue = build_review_queue(paths, status="in_progress", limit=1, offset=1, query="source")

    assert queue.counts.in_progress == 2
    assert [item.source_id for item in queue.items] == ["beta-source"]
    assert queue.limit == 1
    assert queue.offset == 1


def test_get_source_detail_normalizes_artifact_for_review_card(tmp_path: Path) -> None:
    """Source detail should expose metadata, summary, tags, and entity groups for the UI."""
    paths = _paths(tmp_path)
    _write_raw(paths, "analyzed", markdown="# Article\n\nRaw markdown body")
    _write_artifact(paths, "analyzed", _artifact())

    detail = get_source_detail(paths, "analyzed")

    assert detail.source_id == "analyzed"
    assert detail.status == "in_progress"
    assert detail.metadata.title == "Analyzed Article"
    assert detail.summary.short == "A concise summary."
    assert detail.summary.key_insights == ["First useful insight", "Second useful insight"]
    assert detail.tags == ["agents", "ai-engineering", "rag", "software-delivery"]
    assert detail.entities.topics[0].title == "Agentic coding workflows"
    assert detail.entities.glossary[0].title == "Retrieval augmented generation"
    assert detail.entities.trends[0].title == "Teams adopt AI review assistants"
    assert detail.debug.artifact["content_sha256"] == "stored-hash"


def test_get_source_detail_tolerates_missing_optional_fields(tmp_path: Path) -> None:
    """Missing optional artifact fields should not prevent source detail rendering."""
    paths = _paths(tmp_path)
    _write_raw(paths, "minimal")
    _write_artifact(paths, "minimal", {"llm_output": {"topics": ["unexpected scalar"]}})

    detail = get_source_detail(paths, "minimal")

    assert detail.metadata.title == "minimal"
    assert detail.summary.short == ""
    assert detail.tags == []
    assert detail.entities.topics[0].title == "unexpected scalar"
    assert detail.entities.glossary == []
    assert detail.entities.trends == []


def test_read_raw_markdown_returns_available_content(tmp_path: Path) -> None:
    """Raw source reading should return local Markdown without writing files."""
    paths = _paths(tmp_path)
    _write_raw(paths, "source", markdown="Local source text")

    raw = read_raw_markdown(paths, "source")

    assert raw.available is True
    assert raw.content == "Local source text"
    assert raw.path == str(paths.raw_dir / "source.md")


def test_read_raw_markdown_returns_unavailable_when_sidecar_missing(tmp_path: Path) -> None:
    """Missing Markdown sidecars should produce an unavailable read-only response."""
    paths = _paths(tmp_path)
    _write_raw(paths, "source", markdown=None)

    raw = read_raw_markdown(paths, "source")

    assert raw.available is False
    assert raw.content == ""
    assert raw.path is None


@pytest.mark.parametrize("source_id", ["../secret", "nested/source", "source.json", ""])
def test_validate_source_id_rejects_path_traversal(source_id: str) -> None:
    """Source IDs must never be interpreted as arbitrary filesystem paths."""
    with pytest.raises(ValueError, match="Invalid source_id"):
        validate_source_id(source_id)
