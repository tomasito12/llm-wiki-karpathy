"""Central path configuration for wiki tooling."""

from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import (
    WikiPaths,
    WikiPathsConfigError,
    default_wiki_paths,
    load_wiki_paths,
    resolve_path_template,
)

__all__ = [
    "WikiPaths",
    "WikiPathsConfigError",
    "add_paths_config_argument",
    "default_wiki_paths",
    "load_paths_for_cli",
    "load_wiki_paths",
    "resolve_cli_path",
    "resolve_path_template",
]
