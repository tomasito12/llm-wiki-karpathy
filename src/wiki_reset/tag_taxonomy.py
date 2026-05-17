"""Baseline ingestion-review tag taxonomies for a fresh wiki reset."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import yaml

from src.ingest_review.paths import repo_root
from src.ingest_review.tags import (
    default_glossary_tags_path,
    default_howto_tags_path,
    default_impl_study_tags_path,
    default_model_types_path,
    default_tool_types_path,
    default_topic_tags_path,
    default_trend_tags_path,
    load_tag_list,
    normalize_tag,
)
from src.pipeline.atomic import atomic_write_text

_PathFn = Callable[[Path | None], Path]

_TAXONOMY_SPECS: tuple[tuple[_PathFn, str, list[str]], ...] = (
    (
        default_topic_tags_path,
        "Topic proposal tags (ingestion review).",
        ["ai-engineering", "knowledge-management"],
    ),
    (
        default_glossary_tags_path,
        "Glossary proposal tags (ingestion review).",
        ["ai-engineering", "knowledge-management"],
    ),
    (
        default_howto_tags_path,
        "How-to proposal tags (ingestion review).",
        ["ai-engineering", "onboarding-workflow"],
    ),
    (
        default_trend_tags_path,
        "Industry trend proposal tags (ingestion review).",
        ["ai-governance", "knowledge-management"],
    ),
    (
        default_impl_study_tags_path,
        "Implementation-study tags (patterns/themes; industry is a separate field).",
        ["enterprise-ai-adoption", "production-failure"],
    ),
    (
        default_tool_types_path,
        "Approved tool types (ingestion review). LLM may only propose types from this list.",
        ["cloud-saas", "coding-agent", "workflow-automation"],
    ),
    (
        default_model_types_path,
        "Approved model types (ingestion review). LLM may only propose types from this list.",
        ["embedding-model", "frontier-model", "open-weight-model"],
    ),
)


def tag_taxonomy_paths(root: Path | None = None) -> list[Path]:
    """All YAML allowlist paths managed by wiki-reset tag taxonomy reset."""
    return [fn(root) for fn, _, _ in _TAXONOMY_SPECS]


def baseline_tag_taxonomy(root: Path | None = None) -> dict[Path, list[str]]:
    """Resolved paths → normalized baseline tag lists."""
    return {
        fn(root): [normalize_tag(t) for t in tags if normalize_tag(t)]
        for fn, _, tags in _TAXONOMY_SPECS
    }


def write_tag_taxonomy_file(path: Path, tags: list[str], *, comment: str | None = None) -> None:
    """Overwrite one allowlist YAML file with a normalized ``tags:`` list."""
    normalized = sorted({normalize_tag(t) for t in tags if normalize_tag(t)})
    lines: list[str] = []
    if comment:
        lines.append(f"# {comment}")
    body = yaml.dump({"tags": normalized}, default_flow_style=False, sort_keys=False)
    lines.append(body.rstrip())
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, "\n".join(lines))


def reset_tag_taxonomy(root: Path | None = None) -> list[str]:
    """Reset all review tag/type allowlists to baseline seeds.

    Returns sorted POSIX paths relative to repo *root*.
    """
    base = root or repo_root()
    written: list[str] = []
    for fn, comment, tags in _TAXONOMY_SPECS:
        path = fn(base)
        write_tag_taxonomy_file(path, tags, comment=comment)
        written.append(path.relative_to(base).as_posix())
    return sorted(written)


def tag_taxonomy_differs_from_baseline(root: Path | None = None) -> bool:
    """Return True if any allowlist file differs from the baseline seeds."""
    for path, expected in baseline_tag_taxonomy(root).items():
        current = load_tag_list(path)
        if sorted(current) != sorted(expected):
            return True
    return False
