"""Shared CLI helpers for wiki path configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_paths.config import WikiPaths, load_wiki_paths


def add_paths_config_argument(parser: argparse.ArgumentParser) -> None:
    """Add the shared ``--paths-config`` option to a CLI parser."""
    parser.add_argument(
        "--paths-config",
        type=Path,
        default=None,
        help=(
            "Optional wiki paths TOML config file. "
            "Defaults to LLM_WIKI_PATHS_CONFIG or config/wiki_paths.toml when present."
        ),
    )


def load_paths_for_cli(
    args: argparse.Namespace,
    *,
    repo_root_override: Path | None = None,
) -> WikiPaths:
    """Load wiki paths for a parsed CLI namespace.

    When ``--paths-config`` is passed, the config file must exist.

    Args:
        args: Parsed CLI arguments containing an optional ``paths_config`` field.
        repo_root_override: Optional repository root override from ``--repo-root``.

    Returns:
        Resolved :class:`WikiPaths`.

    Raises:
        WikiPathsConfigError: When an explicitly requested config file is missing.
    """
    root = (repo_root_override or repo_root()).resolve()
    config_path = getattr(args, "paths_config", None)
    return load_wiki_paths(
        repo_root=root,
        config_path=config_path,
        config_required=config_path is not None,
    )


def resolve_cli_path(explicit: Path | None, *, configured: Path) -> Path:
    """Return an explicit CLI path or the configured default."""
    return explicit.resolve() if explicit is not None else configured.resolve()


def paths_with_status_cli_overrides(args: argparse.Namespace, paths: WikiPaths) -> WikiPaths:
    """Apply wiki-ops-status CLI path flags on top of configured paths."""
    return WikiPaths(
        repo_root=paths.repo_root,
        knowledge_root=paths.knowledge_root,
        vault_root=paths.vault_root,
        raw_dir=resolve_cli_path(args.raw_dir, configured=paths.raw_dir),
        reviews_dir=resolve_cli_path(args.reviews_dir, configured=paths.reviews_dir),
        synthesis_dir=resolve_cli_path(
            args.synthesis_cache_dir,
            configured=paths.synthesis_dir,
        ),
        graph_path=resolve_cli_path(args.graph_path, configured=paths.graph_path),
        manifest_path=resolve_cli_path(args.manifest_path, configured=paths.manifest_path),
        release_dir=paths.release_dir,
        preview_dir=resolve_cli_path(args.preview_dir, configured=paths.preview_dir),
        run_dir=resolve_cli_path(args.run_dir, configured=paths.run_dir),
        backup_dir=resolve_cli_path(args.backup_dir, configured=paths.backup_dir),
        wiki_dir=resolve_cli_path(args.wiki_dir, configured=paths.wiki_dir),
        source_pages_dir=paths.source_pages_dir,
        source_index_path=paths.source_index_path,
        indexes_dir=paths.indexes_dir,
    )
