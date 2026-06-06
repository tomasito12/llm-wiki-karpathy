"""Tests for ingest queue review status."""

from __future__ import annotations

from pathlib import Path

from src.ingest_queue.queue import list_ingest_items


def test_pending_when_review_json_missing(tmp_path: Path) -> None:
    """Exports with sidecar but no review artifact are pending."""
    raw = tmp_path / "raw"
    reviews = tmp_path / "reviews"
    raw.mkdir()
    reviews.mkdir()
    stem = "article-one"
    (raw / f"{stem}.html").write_text("<html></html>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: Article\n---\n", encoding="utf-8")

    items = list_ingest_items(raw, reviews)
    assert len(items) == 1
    assert items[0].status == "pending"


def test_reviewed_when_review_json_exists(tmp_path: Path) -> None:
    """Review artifact presence marks item reviewed."""
    raw = tmp_path / "raw"
    reviews = tmp_path / "reviews"
    raw.mkdir()
    reviews.mkdir()
    stem = "article-two"
    (raw / f"{stem}.html").write_text("<html></html>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: Article\n---\n", encoding="utf-8")
    review_dir = reviews / stem
    review_dir.mkdir()
    (review_dir / "review.json").write_text("{}", encoding="utf-8")

    items = list_ingest_items(raw, reviews)
    assert items[0].status == "reviewed"


def test_incomplete_when_md_sidecar_missing(tmp_path: Path) -> None:
    """Missing markdown sidecar marks export incomplete."""
    raw = tmp_path / "raw"
    reviews = tmp_path / "reviews"
    raw.mkdir()
    reviews.mkdir()
    stem = "article-three"
    (raw / f"{stem}.html").write_text("<html></html>", encoding="utf-8")

    items = list_ingest_items(raw, reviews)
    assert items[0].status == "incomplete"


def test_empty_raw_dir_returns_no_items(tmp_path: Path) -> None:
    """Empty raw directory yields empty queue."""
    raw = tmp_path / "raw"
    reviews = tmp_path / "reviews"
    raw.mkdir()
    reviews.mkdir()
    assert list_ingest_items(raw, reviews) == []
