"""Persist reviewer decisions to skip sources without creating review artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.ingest_review.artifact import delete_review_artifact, review_artifact_path
from src.pipeline.atomic import atomic_write_json


def skipped_sources_path(reviews_root: Path) -> Path:
    """Path to the skip registry JSON alongside per-source review folders."""
    return reviews_root / "skipped_sources.json"


def _utc_now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def load_skipped_sources(reviews_root: Path) -> dict[str, dict[str, Any]]:
    """Return ``source_id`` → skip metadata (empty dict when file is missing)."""
    path = skipped_sources_path(reviews_root)
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    sources = raw.get("sources") if isinstance(raw, dict) else None
    if not isinstance(sources, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for sid, meta in sources.items():
        if isinstance(sid, str) and isinstance(meta, dict):
            out[sid] = meta
    return out


def load_skipped_source_ids(reviews_root: Path) -> set[str]:
    """Return the set of source IDs marked as skipped for extraction."""
    return set(load_skipped_sources(reviews_root))


def save_skipped_sources(reviews_root: Path, sources: dict[str, dict[str, Any]]) -> None:
    """Write the skip registry atomically."""
    path = skipped_sources_path(reviews_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, {"sources": sources})


def mark_source_skipped(
    reviews_root: Path,
    source_id: str,
    *,
    title: str = "",
    content_sha256: str = "",
) -> None:
    """Record that *source_id* should not be extracted or reviewed."""
    sources = load_skipped_sources(reviews_root)
    sources[source_id] = {
        "skipped_at": _utc_now_iso(),
        "title": title.strip(),
        "content_sha256": content_sha256.strip(),
    }
    save_skipped_sources(reviews_root, sources)


def unskip_source(reviews_root: Path, source_id: str) -> bool:
    """Remove *source_id* from the skip registry. Returns True when an entry existed."""
    sources = load_skipped_sources(reviews_root)
    if source_id not in sources:
        return False
    del sources[source_id]
    save_skipped_sources(reviews_root, sources)
    return True


def is_source_skipped(reviews_root: Path, source_id: str) -> bool:
    """Return True when *source_id* is in the skip registry."""
    return source_id in load_skipped_source_ids(reviews_root)


def skip_source_for_extraction(
    reviews_root: Path,
    source_id: str,
    *,
    title: str = "",
    content_sha256: str = "",
) -> bool:
    """Skip extraction: record skip decision and delete any existing review artifact.

    Returns True when a review.json file was removed.
    """
    mark_source_skipped(
        reviews_root,
        source_id,
        title=title,
        content_sha256=content_sha256,
    )
    return delete_review_artifact(source_id, state_reviews=reviews_root)


def skip_entry_for_source(reviews_root: Path, source_id: str) -> dict[str, Any] | None:
    """Return skip metadata for one source, or None if not skipped."""
    return load_skipped_sources(reviews_root).get(source_id)


def review_artifact_exists(reviews_root: Path, source_id: str) -> bool:
    """Return True when ``review.json`` exists for *source_id*."""
    return review_artifact_path(source_id, state_reviews=reviews_root).is_file()
