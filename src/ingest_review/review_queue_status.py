"""Classify ingest-review sources by workflow status for dashboard queue UI."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Literal

from src.ingest_review.artifact import load_artifact, review_artifact_path

SourceReviewStatus = Literal["not_started", "in_progress", "finished"]

SOURCE_REVIEW_FILTER_OPTIONS: tuple[tuple[str, frozenset[SourceReviewStatus]], ...] = (
    ("In progress", frozenset({"in_progress"})),
    ("Needs work", frozenset({"not_started", "in_progress"})),
    ("Not started", frozenset({"not_started"})),
    ("Finished", frozenset({"finished"})),
    ("All", frozenset({"not_started", "in_progress", "finished"})),
)

DEFAULT_SOURCE_REVIEW_FILTER = "In progress"

UNFINISHED_STATUSES: frozenset[SourceReviewStatus] = frozenset({"not_started", "in_progress"})

STATUS_DISPLAY_ORDER: dict[SourceReviewStatus, int] = {
    "in_progress": 0,
    "not_started": 1,
    "finished": 2,
}

_STATUS_LABELS: dict[SourceReviewStatus, str] = {
    "not_started": "○ Not started",
    "in_progress": "◐ In progress",
    "finished": "✓ Finished",
}


def status_label(status: SourceReviewStatus) -> str:
    """Short human label for UI prefixes."""
    return _STATUS_LABELS[status]


def status_from_artifact(artifact: dict | None) -> SourceReviewStatus:
    """Derive workflow status from a loaded review artifact dict."""
    if not artifact:
        return "not_started"
    analytics = artifact.get("review_analytics")
    if not isinstance(analytics, dict):
        return "in_progress"
    finished = analytics.get("review_finished_at")
    if finished is not None and str(finished).strip():
        return "finished"
    return "in_progress"


def status_for_source(reviews_root: Path, source_id: str) -> SourceReviewStatus:
    """Classify one source by its on-disk ``review.json``."""
    path = review_artifact_path(source_id, state_reviews=reviews_root)
    if not path.is_file():
        return "not_started"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "in_progress"
    if not isinstance(raw, dict):
        return "in_progress"
    return status_from_artifact(raw)


def build_source_status_map(
    reviews_root: Path,
    source_ids: list[str],
) -> dict[str, SourceReviewStatus]:
    """Map each *source_id* to its review workflow status."""
    return {sid: status_for_source(reviews_root, sid) for sid in source_ids}


def filter_statuses_for_label(filter_label: str) -> frozenset[SourceReviewStatus]:
    """Return allowed statuses for a filter radio label."""
    for label, statuses in SOURCE_REVIEW_FILTER_OPTIONS:
        if label == filter_label:
            return statuses
    return SOURCE_REVIEW_FILTER_OPTIONS[0][1]


def count_by_status(status_map: dict[str, SourceReviewStatus]) -> dict[SourceReviewStatus, int]:
    """Count sources in each status bucket."""
    counts: dict[SourceReviewStatus, int] = {
        "not_started": 0,
        "in_progress": 0,
        "finished": 0,
    }
    for status in status_map.values():
        counts[status] += 1
    return counts


def filter_source_ids(
    source_ids: list[str],
    status_map: dict[str, SourceReviewStatus],
    allowed: frozenset[SourceReviewStatus],
) -> list[str]:
    """Keep *source_ids* whose status is in *allowed*, sorted for display."""
    filtered = [sid for sid in source_ids if status_map.get(sid) in allowed]
    return sorted(
        filtered,
        key=lambda sid: (
            STATUS_DISPLAY_ORDER.get(status_map.get(sid, "not_started"), 99),
            sid.lower(),
        ),
    )


def unfinished_source_ids(
    source_ids: list[str],
    status_map: dict[str, SourceReviewStatus],
) -> list[str]:
    """Source IDs that are not started or in progress (excludes finished)."""
    return filter_source_ids(source_ids, status_map, UNFINISHED_STATUSES)


def pick_random_unfinished_source_id(
    source_ids: list[str],
    status_map: dict[str, SourceReviewStatus],
    *,
    rng: random.Random | None = None,
) -> str | None:
    """Return a random *source_id* that is not finished, or ``None`` if the pool is empty."""
    pool = unfinished_source_ids(source_ids, status_map)
    if not pool:
        return None
    choice = rng or random
    return choice.choice(pool)


def artifact_title_for_source(reviews_root: Path, source_id: str) -> str | None:
    """Return stored source title from artifact if available."""
    path = review_artifact_path(source_id, state_reviews=reviews_root)
    art = load_artifact(path)
    if not art:
        return None
    src = art.get("source")
    if not isinstance(src, dict):
        return None
    title = str(src.get("title") or "").strip()
    return title or None
