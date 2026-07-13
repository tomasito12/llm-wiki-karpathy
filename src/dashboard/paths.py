"""Wiki path loading helpers for the Streamlit dashboard."""

from __future__ import annotations

import os
from pathlib import Path

from src.ingest_review.paths import load_repo_dotenv
from src.wiki_paths.config import (
    DEFAULT_CONFIG_RELATIVE,
    PATHS_CONFIG_ENV,
    WikiPaths,
    load_wiki_paths,
)

REPO_LOCAL_INGESTION_WARNING = (
    "Warning: selected ingestion paths point inside the code repo. This may recreate "
    "repo-local data that has been externalized."
)


def resolve_active_paths_config_path(repo_root: Path) -> Path | None:
    """Return the wiki paths config file that would be loaded, if any."""
    env_path = os.environ.get(PATHS_CONFIG_ENV)
    if env_path:
        return Path(env_path).expanduser()
    default_path = repo_root / DEFAULT_CONFIG_RELATIVE
    if default_path.is_file():
        return default_path
    return None


def format_paths_config_label(repo_root: Path) -> str:
    """Return a human-readable label for the active path configuration source."""
    config_path = resolve_active_paths_config_path(repo_root)
    if config_path is None:
        return "repo-local defaults"
    return str(config_path.resolve())


def load_dashboard_wiki_paths() -> tuple[Path, WikiPaths, str]:
    """Load wiki paths for the dashboard and return repo root, paths, and config label."""
    repo_root = load_repo_dotenv()
    paths = load_wiki_paths(repo_root=repo_root)
    label = format_paths_config_label(repo_root)
    return repo_root, paths, label


def external_roots_configured(paths: WikiPaths) -> bool:
    """Return True when knowledge or vault roots differ from the code repo."""
    repo = paths.repo_root.resolve()
    return paths.knowledge_root.resolve() != repo or paths.vault_root.resolve() != repo


def path_is_inside_repo(path: Path, repo_root: Path) -> bool:
    """Return True when ``path`` resolves under ``repo_root``."""
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def ingestion_paths_point_inside_repo(
    paths: WikiPaths,
    *,
    raw_dir: Path,
    reviews_root: Path,
    wiki_root: Path,
) -> bool:
    """Return True when any selected ingestion path sits inside the code repo."""
    if not external_roots_configured(paths):
        return False
    repo = paths.repo_root.resolve()
    return any(
        path_is_inside_repo(selected, repo) for selected in (raw_dir, reviews_root, wiki_root)
    )


def readwise_library_index_path(paths: WikiPaths) -> Path:
    """Return the default Readwise library index path for configured roots."""
    return paths.knowledge_root / "state" / "readwise_library.json"
