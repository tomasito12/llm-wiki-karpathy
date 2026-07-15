"""Helpers for finished vs in-progress review scope."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.artifact import load_artifact
from src.ingest_review.review_queue_status import status_from_artifact


def iter_review_artifact_paths(reviews_dir: Path) -> list[Path]:
    """Return review artifact paths in deterministic order."""
    if not reviews_dir.is_dir():
        return []
    return sorted(reviews_dir.glob("*/review.json"))


def source_id_from_artifact(artifact: dict) -> str:
    """Return the canonical source id from one review artifact."""
    source = artifact.get("source")
    if isinstance(source, dict):
        source_id = str(source.get("source_id") or "").strip()
        if source_id:
            return source_id
    return ""


def finished_source_ids(reviews_dir: Path) -> set[str]:
    """Return source ids whose review artifacts are marked finished."""
    finished: set[str] = set()
    for path in iter_review_artifact_paths(reviews_dir):
        artifact = load_artifact(path)
        if artifact is None or status_from_artifact(artifact) != "finished":
            continue
        source_id = source_id_from_artifact(artifact)
        if not source_id:
            source_id = path.parent.name
        finished.add(source_id)
    return finished


def in_progress_source_ids(reviews_dir: Path) -> set[str]:
    """Return source ids with in-progress review artifacts."""
    in_progress: set[str] = set()
    for path in iter_review_artifact_paths(reviews_dir):
        artifact = load_artifact(path)
        if artifact is None or status_from_artifact(artifact) != "in_progress":
            continue
        source_id = source_id_from_artifact(artifact)
        if not source_id:
            source_id = path.parent.name
        in_progress.add(source_id)
    return in_progress
