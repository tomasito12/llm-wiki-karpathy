"""Staging writer utilities for parsed markdown documents."""

from __future__ import annotations

import re
from pathlib import Path

from src.pipeline.atomic import atomic_write_text
from src.pipeline.models import ParsedDocument


def slugify(value: str) -> str:
    """Convert arbitrary text into a filesystem-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "document"


def stage_document(parsed: ParsedDocument, staging_dir: Path) -> Path:
    """Write one parsed document to staging and return its path."""
    staging_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(parsed.item.title)}-{parsed.item.item_id}.md"
    path = staging_dir / filename
    atomic_write_text(path, parsed.markdown)
    return path
