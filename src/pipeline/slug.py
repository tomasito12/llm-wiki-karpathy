"""Filesystem-safe slug helpers."""

from __future__ import annotations

import re


def slugify(value: str) -> str:
    """Convert arbitrary text into a filesystem-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "document"
