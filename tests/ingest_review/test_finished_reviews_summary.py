"""Tests for finished review JSON bundle export."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_review.finished_reviews_summary import (
    build_finished_reviews_bundle,
    load_review_artifacts,
    write_finished_reviews_bundle,
)


def _write_review(
    reviews_root: Path,
    source_id: str,
    *,
    finished_at: str | None,
    title: str,
) -> None:
    payload = {
        "source": {
            "source_id": source_id,
            "title": title,
        },
        "review_analytics": {"review_finished_at": finished_at},
    }
    out_dir = reviews_root / source_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "review.json").write_text(json.dumps(payload), encoding="utf-8")


def test_load_review_artifacts_filters_finished_by_default(tmp_path: Path) -> None:
    """Only artifacts with review_finished_at are returned by default."""
    _write_review(
        tmp_path, "finished-a", finished_at="2026-05-20T10:00:00+00:00", title="Finished A"
    )
    _write_review(tmp_path, "in-progress-b", finished_at=None, title="In Progress B")

    finished = load_review_artifacts(tmp_path)
    all_reviews = load_review_artifacts(tmp_path, scope="all")

    assert len(finished) == 1
    assert finished[0]["source"]["source_id"] == "finished-a"
    assert len(all_reviews) == 2


def test_build_finished_reviews_bundle_wraps_artifacts(tmp_path: Path) -> None:
    """Bundle JSON includes metadata and the full review objects."""
    _write_review(
        tmp_path, "finished-a", finished_at="2026-05-20T10:00:00+00:00", title="Finished A"
    )

    bundle = build_finished_reviews_bundle(tmp_path)

    assert bundle["count"] == 1
    assert bundle["scope"] == "finished"
    assert bundle["reviews"][0]["source"]["title"] == "Finished A"


def test_write_finished_reviews_bundle_creates_json_file(tmp_path: Path) -> None:
    """write_finished_reviews_bundle writes a parseable JSON bundle."""
    _write_review(
        tmp_path, "finished-a", finished_at="2026-05-20T10:00:00+00:00", title="Finished A"
    )
    output = tmp_path / "bundle.json"

    path = write_finished_reviews_bundle(output, reviews_root=tmp_path)

    assert path == output
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["count"] == 1
    assert payload["reviews"][0]["source"]["source_id"] == "finished-a"
