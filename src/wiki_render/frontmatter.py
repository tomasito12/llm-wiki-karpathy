"""Deterministic YAML frontmatter helpers."""

from __future__ import annotations

from typing import Any

import yaml


def frontmatter_block(data: dict[str, Any]) -> str:
    """Return a deterministic YAML frontmatter block."""
    clean = {key: _clean(value) for key, value in data.items() if _include(value)}
    body = yaml.safe_dump(
        clean,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()
    return f"---\n{body}\n---\n\n"


def markdown_document(frontmatter: dict[str, Any], body: str) -> str:
    """Return a complete markdown document with final newline."""
    return f"{frontmatter_block(frontmatter)}{body.strip()}\n"


def _include(value: Any) -> bool:
    """Return True when a value should appear in frontmatter."""
    if value is None:
        return False
    if value == "":
        return False
    if isinstance(value, list | tuple | set | dict) and not value:
        return False
    return True


def _clean(value: Any) -> Any:
    """Return JSON/YAML-friendly deterministic values."""
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if isinstance(value, dict):
        return {key: _clean(value[key]) for key in sorted(value)}
    return value
