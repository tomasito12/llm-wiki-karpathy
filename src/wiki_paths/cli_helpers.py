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
