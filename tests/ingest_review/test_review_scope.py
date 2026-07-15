"""Tests for finished vs in-progress review scope helpers."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_review.review_scope import (
    finished_source_ids,
    in_progress_source_ids,
)


def test_finished_source_ids_returns_only_finished_reviews(tmp_path: Path) -> None:
    """Finished scope should ignore in-progress review artifacts."""
    reviews_dir = tmp_path / "reviews"
    finished_dir = reviews_dir / "finished-source"
    pending_dir = reviews_dir / "pending-source"
    finished_dir.mkdir(parents=True)
    pending_dir.mkdir(parents=True)
    (finished_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-05-01T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    (pending_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": None}}),
        encoding="utf-8",
    )

    assert finished_source_ids(reviews_dir) == {"finished-source"}
    assert in_progress_source_ids(reviews_dir) == {"pending-source"}
