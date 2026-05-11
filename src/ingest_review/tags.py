"""Load review-layer tag allowlists from YAML config."""

from __future__ import annotations

from pathlib import Path

import yaml

from src.ingest_review.paths import repo_root


def load_tag_list(path: Path) -> list[str]:
    """Load a YAML file that is either a bare list or ``{ tags: [...] }``."""
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, dict) and "tags" in raw:
        inner = raw["tags"]
        if isinstance(inner, list):
            return [str(x) for x in inner]
    return []


def default_tool_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_tools.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_tools.yaml"


def default_howto_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_howto.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_howto.yaml"


def load_tool_tags(root: Path | None = None) -> list[str]:
    """Return tool proposal tag allowlist."""
    return load_tag_list(default_tool_tags_path(root))


def load_howto_tags(root: Path | None = None) -> list[str]:
    """Return how-to proposal tag allowlist."""
    return load_tag_list(default_howto_tags_path(root))
