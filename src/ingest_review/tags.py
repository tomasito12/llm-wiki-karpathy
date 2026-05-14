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


def default_tool_types_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tool_types.yaml``."""
    return (root or repo_root()) / "config" / "review_tool_types.yaml"


def default_howto_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_howto.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_howto.yaml"


def load_tool_types(root: Path | None = None) -> list[str]:
    """Return approved tool type registry."""
    return load_tag_list(default_tool_types_path(root))


def load_howto_tags(root: Path | None = None) -> list[str]:
    """Return how-to proposal tag allowlist."""
    return load_tag_list(default_howto_tags_path(root))


def default_glossary_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_glossary.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_glossary.yaml"


def load_glossary_tags(root: Path | None = None) -> list[str]:
    """Return glossary tag allowlist."""
    return load_tag_list(default_glossary_tags_path(root))


def default_topic_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_topics.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_topics.yaml"


def load_topic_tags(root: Path | None = None) -> list[str]:
    """Return topic tag allowlist."""
    return load_tag_list(default_topic_tags_path(root))


def default_trend_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_trends.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_trends.yaml"


def load_trend_tags(root: Path | None = None) -> list[str]:
    """Return trend tag allowlist."""
    return load_tag_list(default_trend_tags_path(root))


def default_model_types_path(root: Path | None = None) -> Path:
    """Path to ``config/review_model_types.yaml``."""
    return (root or repo_root()) / "config" / "review_model_types.yaml"


def load_model_types(root: Path | None = None) -> list[str]:
    """Return approved model type registry."""
    return load_tag_list(default_model_types_path(root))


def default_impl_study_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_impl_study.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_impl_study.yaml"


def load_impl_study_tags(root: Path | None = None) -> list[str]:
    """Return implementation-study tag allowlist."""
    return load_tag_list(default_impl_study_tags_path(root))


def append_tags_to_yaml(path: Path, new_tags: list[str]) -> None:
    """Append new tags to a YAML allowlist file, deduplicating."""
    existing = set(load_tag_list(path))
    to_add = [t for t in new_tags if t and t not in existing]
    if not to_add:
        return
    import yaml

    from src.pipeline.atomic import atomic_write_text

    all_tags = list(existing) + to_add
    all_tags.sort()
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(
        path,
        yaml.dump({"tags": all_tags}, default_flow_style=False, sort_keys=False),
    )
