"""Shared finished-review fixtures for synthesis CLI tests."""

from __future__ import annotations

import json
from pathlib import Path


def write_finished_review(reviews_dir: Path, source_id: str) -> None:
    """Write a minimal finished review artifact for one source id."""
    review_dir = reviews_dir / source_id
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-05-01T00:00:00+00:00"}}),
        encoding="utf-8",
    )


def write_paths_config(
    tmp_path: Path,
    *,
    graph_path: Path,
    cache_dir: Path,
    reviews_dir: Path,
    wiki_dir: Path | None = None,
    preview_dir: Path | None = None,
    run_dir: Path | None = None,
) -> Path:
    """Write a minimal wiki paths config for synthesis CLI tests."""
    config_path = tmp_path / "wiki_paths.toml"
    lines = [
        "[paths]",
        f'graph_path = "{graph_path}"',
        f'synthesis_dir = "{cache_dir}"',
        f'reviews_dir = "{reviews_dir}"',
    ]
    if wiki_dir is not None:
        lines.append(f'wiki_dir = "{wiki_dir}"')
    if preview_dir is not None:
        lines.append(f'preview_dir = "{preview_dir}"')
    if run_dir is not None:
        lines.append(f'run_dir = "{run_dir}"')
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config_path
