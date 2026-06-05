"""Tests for reviewer skip registry (no review.json)."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_review.artifact import review_artifact_path
from src.ingest_review.skipped_sources import (
    is_source_skipped,
    load_skipped_source_ids,
    mark_source_skipped,
    skip_source_for_extraction,
    skipped_sources_path,
    unskip_source,
)


def test_mark_source_skipped_writes_registry(tmp_path: Path) -> None:
    reviews_root = tmp_path / "reviews"
    mark_source_skipped(
        reviews_root,
        "article-a",
        title="Example",
        content_sha256="abc123",
    )
    path = skipped_sources_path(reviews_root)
    assert path.is_file()
    payload = json.loads(path.read_text(encoding="utf-8"))
    entry = payload["sources"]["article-a"]
    assert entry["title"] == "Example"
    assert entry["content_sha256"] == "abc123"
    assert entry["skipped_at"]


def test_skip_source_for_extraction_deletes_review_json(tmp_path: Path) -> None:
    reviews_root = tmp_path / "reviews"
    artifact_path = review_artifact_path("article-b", state_reviews=reviews_root)
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text('{"review": {}}', encoding="utf-8")

    removed = skip_source_for_extraction(
        reviews_root,
        "article-b",
        title="Gone",
        content_sha256="hash",
    )

    assert removed is True
    assert not artifact_path.is_file()
    assert is_source_skipped(reviews_root, "article-b")


def test_skip_source_for_extraction_without_existing_artifact(tmp_path: Path) -> None:
    reviews_root = tmp_path / "reviews"
    removed = skip_source_for_extraction(reviews_root, "never-analyzed")
    assert removed is False
    assert load_skipped_source_ids(reviews_root) == {"never-analyzed"}


def test_unskip_source_removes_registry_entry(tmp_path: Path) -> None:
    reviews_root = tmp_path / "reviews"
    mark_source_skipped(reviews_root, "article-c")
    assert unskip_source(reviews_root, "article-c") is True
    assert not is_source_skipped(reviews_root, "article-c")
    assert unskip_source(reviews_root, "article-c") is False
