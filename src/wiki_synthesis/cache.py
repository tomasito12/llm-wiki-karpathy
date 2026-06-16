"""Synthesis cache helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
