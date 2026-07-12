"""Tests for wiki path CLI helpers."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.wiki_paths.cli_helpers import paths_with_status_cli_overrides
from src.wiki_paths.config import default_wiki_paths


def test_paths_with_status_cli_overrides_applies_explicit_raw_dir(tmp_path: Path) -> None:
    """Explicit --raw-dir should override configured raw_dir for retention paths."""
    repo_root = tmp_path / "repo"
    alternate_raw = tmp_path / "alternate-raw"
    repo_root.mkdir()
    alternate_raw.mkdir()
    paths = default_wiki_paths(repo_root)
    args = argparse.Namespace(
        raw_dir=alternate_raw,
        reviews_dir=None,
        wiki_dir=None,
        graph_path=None,
        manifest_path=None,
        synthesis_cache_dir=None,
        preview_dir=None,
        run_dir=None,
        backup_dir=None,
    )

    resolved = paths_with_status_cli_overrides(args, paths)

    assert resolved.raw_dir == alternate_raw.resolve()
    assert resolved.reviews_dir == paths.reviews_dir.resolve()


def test_paths_with_status_cli_overrides_keeps_configured_defaults(tmp_path: Path) -> None:
    """Without explicit flags, configured paths should remain unchanged."""
    paths = default_wiki_paths(tmp_path)
    args = argparse.Namespace(
        raw_dir=None,
        reviews_dir=None,
        wiki_dir=None,
        graph_path=None,
        manifest_path=None,
        synthesis_cache_dir=None,
        preview_dir=None,
        run_dir=None,
        backup_dir=None,
    )

    resolved = paths_with_status_cli_overrides(args, paths)

    assert resolved.raw_dir == paths.raw_dir.resolve()
    assert resolved.wiki_dir == paths.wiki_dir.resolve()
