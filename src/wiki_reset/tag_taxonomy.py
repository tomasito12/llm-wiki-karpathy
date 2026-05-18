"""Baseline ingestion-review tag taxonomies for a fresh wiki reset."""

from __future__ import annotations

from pathlib import Path

import yaml

from src.ingest_review.paths import repo_root
from src.ingest_review.tag_registry import TAG_TAXONOMIES, taxonomy_path
from src.ingest_review.tags import load_tag_list, normalize_tag
from src.pipeline.atomic import atomic_write_text


def tag_taxonomy_paths(root: Path | None = None) -> list[Path]:
    """All YAML allowlist paths managed by wiki-reset tag taxonomy reset."""
    return [taxonomy_path(spec, root) for spec in TAG_TAXONOMIES]


def baseline_tag_taxonomy(root: Path | None = None) -> dict[Path, list[str]]:
    """Resolved paths → normalized baseline tag lists."""
    return {
        taxonomy_path(spec, root): [
            normalize_tag(t) for t in spec.baseline_tags if normalize_tag(t)
        ]
        for spec in TAG_TAXONOMIES
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
    for spec in TAG_TAXONOMIES:
        path = taxonomy_path(spec, base)
        write_tag_taxonomy_file(path, list(spec.baseline_tags), comment=spec.description)
        written.append(path.relative_to(base).as_posix())
    return sorted(written)


def tag_taxonomy_differs_from_baseline(root: Path | None = None) -> bool:
    """Return True if any allowlist file differs from the baseline seeds."""
    for path, expected in baseline_tag_taxonomy(root).items():
        current = load_tag_list(path)
        if sorted(current) != sorted(expected):
            return True
    return False
