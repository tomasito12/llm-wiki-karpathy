"""Load reviewed ingestion artifacts for full regeneration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest_review.artifact import load_artifact
from src.ingest_review.review_queue_status import status_from_artifact


def iter_review_paths(reviews_dir: Path) -> list[Path]:
    """Return review artifact paths in deterministic order."""
    if not reviews_dir.is_dir():
        return []
    return sorted(reviews_dir.glob("*/review.json"))


def load_review_artifacts(
    reviews_dir: Path,
    *,
    include_in_progress: bool = False,
) -> list[dict[str, Any]]:
    """Load review artifacts under ``reviews_dir``.

    By default only finished reviews are included. Pass ``include_in_progress=True``
    to also render in-progress review artifacts for vault preview runs.
    """
    artifacts: list[dict[str, Any]] = []
    for path in iter_review_paths(reviews_dir):
        artifact = load_artifact(path)
        if artifact is None:
            continue
        status = status_from_artifact(artifact)
        if status == "finished" or (include_in_progress and status == "in_progress"):
            artifacts.append(artifact)
    return sorted(
        artifacts,
        key=lambda item: str((item.get("source") or {}).get("source_id") or ""),
    )
