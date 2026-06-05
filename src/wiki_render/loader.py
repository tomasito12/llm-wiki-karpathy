"""Load reviewed ingestion artifacts for full regeneration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest_review.artifact import load_artifact


def iter_review_paths(reviews_dir: Path) -> list[Path]:
    """Return review artifact paths in deterministic order."""
    return sorted(reviews_dir.glob("*/review.json"))


def load_review_artifacts(reviews_dir: Path) -> list[dict[str, Any]]:
    """Load and migrate all review artifacts under ``reviews_dir``."""
    artifacts: list[dict[str, Any]] = []
    for path in iter_review_paths(reviews_dir):
        artifact = load_artifact(path)
        if artifact is not None:
            artifacts.append(artifact)
    return sorted(
        artifacts,
        key=lambda item: str((item.get("source") or {}).get("source_id") or ""),
    )
