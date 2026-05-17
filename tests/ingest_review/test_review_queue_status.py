"""Tests for review queue status classification."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_review.review_queue_status import (
    SourceReviewStatus,
    build_source_status_map,
    count_by_status,
    filter_source_ids,
    filter_statuses_for_label,
    pick_random_unfinished_source_id,
    status_for_source,
    status_from_artifact,
    status_label,
    unfinished_source_ids,
)


def test_status_from_artifact_not_started() -> None:
    assert status_from_artifact(None) == "not_started"


def test_status_from_artifact_in_progress() -> None:
    assert status_from_artifact({"review_analytics": {"review_finished_at": None}}) == "in_progress"
    assert status_from_artifact({"review_analytics": {}}) == "in_progress"


def test_status_from_artifact_finished() -> None:
    art = {"review_analytics": {"review_finished_at": "2026-05-15T12:00:00+00:00"}}
    assert status_from_artifact(art) == "finished"


def test_status_for_source_not_started(tmp_path: Path) -> None:
    assert status_for_source(tmp_path / "reviews", "missing-source") == "not_started"


def test_status_for_source_in_progress(tmp_path: Path) -> None:
    reviews = tmp_path / "reviews" / "src-a"
    reviews.mkdir(parents=True)
    (reviews / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": None}}),
        encoding="utf-8",
    )
    assert status_for_source(tmp_path / "reviews", "src-a") == "in_progress"


def test_status_for_source_finished(tmp_path: Path) -> None:
    reviews = tmp_path / "reviews" / "src-b"
    reviews.mkdir(parents=True)
    (reviews / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-05-16T10:00:00+00:00"}}),
        encoding="utf-8",
    )
    assert status_for_source(tmp_path / "reviews", "src-b") == "finished"


def test_build_source_status_map(tmp_path: Path) -> None:
    root = tmp_path / "reviews"
    for sid, finished in (("a", None), ("b", "2026-01-01T00:00:00+00:00")):
        d = root / sid
        d.mkdir(parents=True)
        payload: dict = {"review_analytics": {"review_finished_at": finished}}
        (d / "review.json").write_text(json.dumps(payload), encoding="utf-8")
    m = build_source_status_map(root, ["a", "b", "c"])
    assert m["a"] == "in_progress"
    assert m["b"] == "finished"
    assert m["c"] == "not_started"


def test_filter_source_ids_in_progress_only() -> None:
    status_map: dict[str, SourceReviewStatus] = {
        "a": "in_progress",
        "b": "finished",
        "c": "not_started",
    }
    allowed = filter_statuses_for_label("In progress")
    assert filter_source_ids(["c", "b", "a"], status_map, allowed) == ["a"]


def test_count_by_status() -> None:
    status_map: dict[str, SourceReviewStatus] = {
        "x": "in_progress",
        "y": "in_progress",
        "z": "finished",
    }
    assert count_by_status(status_map) == {
        "not_started": 0,
        "in_progress": 2,
        "finished": 1,
    }


def test_status_label() -> None:
    assert "progress" in status_label("in_progress").lower()
    assert "finished" in status_label("finished").lower()


def test_unfinished_source_ids_excludes_finished() -> None:
    status_map: dict[str, SourceReviewStatus] = {
        "a": "not_started",
        "b": "in_progress",
        "c": "finished",
    }
    assert set(unfinished_source_ids(list(status_map), status_map)) == {"a", "b"}


def test_pick_random_unfinished_source_id() -> None:
    status_map: dict[str, SourceReviewStatus] = {
        "only": "finished",
    }
    assert pick_random_unfinished_source_id(["only"], status_map) is None

    status_map2: dict[str, SourceReviewStatus] = {"x": "in_progress", "y": "finished"}
    rng = __import__("random").Random(0)
    assert pick_random_unfinished_source_id(["x", "y"], status_map2, rng=rng) == "x"
