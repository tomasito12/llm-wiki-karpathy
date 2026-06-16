"""Synthesis cache helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "entity_id",
    "category",
    "slug",
    "title",
    "synthesis_input_hash",
    "executive_synthesis",
    "practical_takeaway",
)
REQUIRED_LIST_FIELDS: tuple[str, ...] = (
    "what_to_remember",
    "consensus",
    "tensions",
    "evidence_quality",
)
VALIDATION_FRESH = "fresh"
VALIDATION_STALE = "stale"
VALIDATION_INVALID = "invalid"


@dataclass(frozen=True)
class CacheValidation:
    """Validation result for one synthesis cache entry."""

    state: str
    reason: str
    cached_input_hash: str
    current_input_hash: str

    @property
    def is_usable(self) -> bool:
        """Return whether cached prose can be rendered."""
        return self.state in {VALIDATION_FRESH, VALIDATION_STALE}


def cache_file_path(cache_dir: Path, *, category: str, slug: str) -> Path:
    """Return the cache file path for one synthesized entity."""
    return cache_dir / category / f"{slug}.json"


def load_cache_entry(cache_dir: Path, *, category: str, slug: str) -> dict[str, Any] | None:
    """Load a synthesis cache entry when it exists and is valid JSON."""
    path = cache_file_path(cache_dir, category=category, slug=slug)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return None
    return payload


def cached_input_hash(entry: dict[str, Any] | None) -> str:
    """Return the cached synthesis input hash, or an empty string."""
    if not entry:
        return ""
    value = entry.get("synthesis_input_hash", "")
    return value if isinstance(value, str) else ""


def validate_cache_entry(
    entry: dict[str, Any] | None,
    *,
    current_input_hash: str,
) -> CacheValidation:
    """Validate that a cache entry has enough structure to render."""
    cached_hash = cached_input_hash(entry)
    if not entry:
        return CacheValidation(
            state=VALIDATION_INVALID,
            reason="cache entry is missing",
            cached_input_hash="",
            current_input_hash=current_input_hash,
        )
    missing_text = [
        field
        for field in REQUIRED_TEXT_FIELDS
        if not isinstance(entry.get(field), str) or not entry.get(field, "").strip()
    ]
    missing_lists = [
        field for field in REQUIRED_LIST_FIELDS if not isinstance(entry.get(field), list)
    ]
    if missing_text or missing_lists:
        missing = ", ".join([*missing_text, *missing_lists])
        return CacheValidation(
            state=VALIDATION_INVALID,
            reason=f"cache entry is missing required fields: {missing}",
            cached_input_hash=cached_hash,
            current_input_hash=current_input_hash,
        )
    if cached_hash != current_input_hash:
        return CacheValidation(
            state=VALIDATION_STALE,
            reason="cached synthesis input hash differs from current evidence hash",
            cached_input_hash=cached_hash,
            current_input_hash=current_input_hash,
        )
    return CacheValidation(
        state=VALIDATION_FRESH,
        reason="cache entry matches current evidence hash",
        cached_input_hash=cached_hash,
        current_input_hash=current_input_hash,
    )
