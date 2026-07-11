"""Central path configuration for wiki tooling."""

from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_RELATIVE = Path("config/wiki_paths.toml")
PATHS_CONFIG_ENV = "LLM_WIKI_PATHS_CONFIG"

_PATH_FIELDS = (
    "raw_dir",
    "reviews_dir",
    "synthesis_dir",
    "graph_path",
    "manifest_path",
    "release_dir",
    "preview_dir",
    "run_dir",
    "backup_dir",
    "wiki_dir",
    "source_pages_dir",
    "source_index_path",
    "indexes_dir",
)
_ROOT_FIELDS = ("knowledge_root", "vault_root")
_KNOWN_PATH_KEYS = frozenset(_PATH_FIELDS + _ROOT_FIELDS)
_UNRESOLVED_PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")


class WikiPathsConfigError(Exception):
    """Raised when path configuration cannot be loaded."""


@dataclass(frozen=True)
class WikiPaths:
    """Resolved filesystem paths for wiki knowledge and vault output."""

    repo_root: Path
    knowledge_root: Path
    vault_root: Path
    raw_dir: Path
    reviews_dir: Path
    synthesis_dir: Path
    graph_path: Path
    manifest_path: Path
    release_dir: Path
    preview_dir: Path
    run_dir: Path
    backup_dir: Path
    wiki_dir: Path
    source_pages_dir: Path
    source_index_path: Path
    indexes_dir: Path

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable mapping of absolute path strings."""
        return {key: str(value) for key, value in asdict(self).items()}


def default_wiki_paths(repo_root: Path) -> WikiPaths:
    """Build repo-local default paths matching current command behavior."""
    root = repo_root.resolve()
    return WikiPaths(
        repo_root=root,
        knowledge_root=root,
        vault_root=root,
        raw_dir=root / "raw" / "readwise",
        reviews_dir=root / "state" / "reviews",
        synthesis_dir=root / "state" / "synthesis",
        graph_path=root / "state" / "wiki_render_graph.json",
        manifest_path=root / "state" / "wiki_render_manifest.json",
        release_dir=root / "state" / "releases",
        preview_dir=root / "state" / "synthesis_previews",
        run_dir=root / "state" / "synthesis_runs",
        backup_dir=root / "state" / "synthesis_backups",
        wiki_dir=root / "wiki",
        source_pages_dir=root / "wiki" / "sources" / "full",
        source_index_path=root / "wiki" / "sources" / "index.md",
        indexes_dir=root / "wiki" / "indexes",
    )


def resolve_path_template(value: str, variables: Mapping[str, Path]) -> str:
    """Expand ``{name}`` placeholders in a path template string.

    Callers should reject unresolved placeholders after expansion.
    """
    expanded = value
    for name, path in variables.items():
        expanded = expanded.replace(f"{{{name}}}", str(path))
    return expanded


def load_wiki_paths(
    *,
    repo_root: Path | None = None,
    config_path: Path | None = None,
    config_required: bool = False,
) -> WikiPaths:
    """Load wiki paths from defaults and an optional TOML config file.

    Resolution order for the config file location:

    1. ``config_path`` when provided
    2. ``LLM_WIKI_PATHS_CONFIG`` environment variable
    3. ``config/wiki_paths.toml`` under ``repo_root`` when that file exists

    Relative path entries in the config file are resolved relative to the
    config file's parent directory.

    Args:
        repo_root: Repository root directory. Defaults to three parents above
            this module (same as ``src.ingest_review.paths.repo_root``).
        config_path: Explicit config file path from a CLI flag or caller.
        config_required: When true, a missing ``config_path`` raises
            :class:`WikiPathsConfigError`.

    Returns:
        Resolved :class:`WikiPaths`.

    Raises:
        WikiPathsConfigError: When a required config file is missing or invalid.
    """
    from src.ingest_review.paths import repo_root as detect_repo_root

    root = (repo_root or detect_repo_root()).resolve()
    defaults = default_wiki_paths(root)
    resolved_config_path = _resolve_config_path(
        root,
        config_path=config_path,
        config_required=config_required,
    )
    if resolved_config_path is None:
        return defaults
    if not resolved_config_path.is_file():
        raise WikiPathsConfigError(
            f"Path config file not found: {resolved_config_path}",
        )
    raw_config = _read_paths_section(resolved_config_path)
    return _merge_config(defaults, raw_config, config_dir=resolved_config_path.parent)


def _resolve_config_path(
    repo_root: Path,
    *,
    config_path: Path | None,
    config_required: bool,
) -> Path | None:
    """Return the config file path to load, if any."""
    if config_path is not None:
        return config_path.expanduser()
    env_path = os.environ.get(PATHS_CONFIG_ENV)
    if env_path:
        return Path(env_path).expanduser()
    default_path = repo_root / DEFAULT_CONFIG_RELATIVE
    if default_path.is_file():
        return default_path
    if config_required:
        raise WikiPathsConfigError(
            f"Path config file not found: {config_path}",
        )
    return None


def _read_paths_section(config_path: Path) -> dict[str, Any]:
    """Read the ``[paths]`` table from a TOML config file."""
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise WikiPathsConfigError(
            f"Invalid TOML in path config {config_path}: {exc}",
        ) from exc
    paths_section = payload.get("paths")
    if paths_section is None:
        return {}
    if not isinstance(paths_section, dict):
        raise WikiPathsConfigError(
            f"Expected [paths] table in path config {config_path}",
        )
    return paths_section


def _merge_config(
    defaults: WikiPaths,
    raw_config: Mapping[str, Any],
    *,
    config_dir: Path,
) -> WikiPaths:
    """Merge config overrides onto repo-local defaults."""
    _validate_paths_section_keys(raw_config)
    current = defaults
    knowledge_root = _resolve_root_override(
        raw_config.get("knowledge_root"),
        field_name="knowledge_root",
        default=current.knowledge_root,
        config_dir=config_dir,
    )
    vault_root = _resolve_root_override(
        raw_config.get("vault_root"),
        field_name="vault_root",
        default=current.vault_root,
        config_dir=config_dir,
    )
    current = WikiPaths(
        repo_root=current.repo_root,
        knowledge_root=knowledge_root,
        vault_root=vault_root,
        raw_dir=current.raw_dir,
        reviews_dir=current.reviews_dir,
        synthesis_dir=current.synthesis_dir,
        graph_path=current.graph_path,
        manifest_path=current.manifest_path,
        release_dir=current.release_dir,
        preview_dir=current.preview_dir,
        run_dir=current.run_dir,
        backup_dir=current.backup_dir,
        wiki_dir=current.wiki_dir,
        source_pages_dir=current.source_pages_dir,
        source_index_path=current.source_index_path,
        indexes_dir=current.indexes_dir,
    )
    variables = {
        "repo_root": current.repo_root,
        "knowledge_root": current.knowledge_root,
        "vault_root": current.vault_root,
    }
    derived_defaults = _derived_defaults(current)
    overrides: dict[str, Path] = {}
    for field_name in _PATH_FIELDS:
        if field_name not in raw_config:
            continue
        raw_value = raw_config[field_name]
        if not isinstance(raw_value, str):
            raise WikiPathsConfigError(
                f"Expected string value for paths.{field_name}, got {type(raw_value).__name__}",
            )
        overrides[field_name] = _resolve_config_path_value(
            raw_value,
            field_name=field_name,
            variables=variables,
            config_dir=config_dir,
            fallback=derived_defaults[field_name],
        )
    return WikiPaths(
        repo_root=current.repo_root,
        knowledge_root=current.knowledge_root,
        vault_root=current.vault_root,
        raw_dir=overrides.get("raw_dir", derived_defaults["raw_dir"]),
        reviews_dir=overrides.get("reviews_dir", derived_defaults["reviews_dir"]),
        synthesis_dir=overrides.get("synthesis_dir", derived_defaults["synthesis_dir"]),
        graph_path=overrides.get("graph_path", derived_defaults["graph_path"]),
        manifest_path=overrides.get("manifest_path", derived_defaults["manifest_path"]),
        release_dir=overrides.get("release_dir", derived_defaults["release_dir"]),
        preview_dir=overrides.get("preview_dir", derived_defaults["preview_dir"]),
        run_dir=overrides.get("run_dir", derived_defaults["run_dir"]),
        backup_dir=overrides.get("backup_dir", derived_defaults["backup_dir"]),
        wiki_dir=overrides.get("wiki_dir", derived_defaults["wiki_dir"]),
        source_pages_dir=overrides.get(
            "source_pages_dir",
            derived_defaults["source_pages_dir"],
        ),
        source_index_path=overrides.get(
            "source_index_path",
            derived_defaults["source_index_path"],
        ),
        indexes_dir=overrides.get("indexes_dir", derived_defaults["indexes_dir"]),
    )


def _validate_paths_section_keys(raw_config: Mapping[str, Any]) -> None:
    """Reject unknown keys in the ``[paths]`` config table."""
    unknown = sorted(set(raw_config) - _KNOWN_PATH_KEYS)
    if unknown:
        joined = ", ".join(unknown)
        raise WikiPathsConfigError(f"Unknown keys in [paths]: {joined}")


def _assert_no_unresolved_placeholders(value: str, *, field_name: str) -> None:
    """Reject path values that still contain ``{placeholder}`` tokens."""
    matches = _UNRESOLVED_PLACEHOLDER_PATTERN.findall(value)
    if matches:
        joined = ", ".join(matches)
        raise WikiPathsConfigError(
            f"Unresolved placeholders in paths.{field_name}: {joined}",
        )


def _derived_defaults(current: WikiPaths) -> dict[str, Path]:
    """Build derived defaults after root overrides are applied."""
    knowledge = current.knowledge_root
    vault = current.vault_root
    repo = current.repo_root
    scratch_parent = knowledge / "state" if knowledge == repo else knowledge / "tmp"
    if vault == repo:
        source_pages_dir = repo / "wiki" / "sources" / "full"
        source_index_path = repo / "wiki" / "sources" / "index.md"
        indexes_dir = repo / "wiki" / "indexes"
    else:
        source_pages_dir = vault / "sources" / "full"
        source_index_path = vault / "sources" / "index.md"
        indexes_dir = vault / "indexes"
    return {
        "raw_dir": knowledge / "raw" / "readwise",
        "reviews_dir": knowledge / "state" / "reviews",
        "synthesis_dir": knowledge / "state" / "synthesis",
        "graph_path": knowledge / "state" / "wiki_render_graph.json",
        "manifest_path": knowledge / "state" / "wiki_render_manifest.json",
        "release_dir": knowledge / "state" / "releases",
        "preview_dir": scratch_parent / "synthesis_previews",
        "run_dir": scratch_parent / "synthesis_runs",
        "backup_dir": scratch_parent / "synthesis_backups",
        "wiki_dir": vault / "wiki" if vault != repo else repo / "wiki",
        "source_pages_dir": source_pages_dir,
        "source_index_path": source_index_path,
        "indexes_dir": indexes_dir,
    }


def _resolve_root_override(
    raw_value: Any,
    *,
    field_name: str,
    default: Path,
    config_dir: Path,
) -> Path:
    """Resolve an optional root override from config."""
    if raw_value is None:
        return default
    if not isinstance(raw_value, str):
        raise WikiPathsConfigError(
            f"Expected string value for paths.{field_name}, got {type(raw_value).__name__}",
        )
    return _resolve_config_path_value(
        raw_value,
        field_name=field_name,
        variables={},
        config_dir=config_dir,
        fallback=default,
    )


def _resolve_config_path_value(
    raw_value: str,
    *,
    field_name: str,
    variables: Mapping[str, Path],
    config_dir: Path,
    fallback: Path,
) -> Path:
    """Resolve one configured path value with template and relative rules."""
    expanded = resolve_path_template(raw_value, variables) if variables else raw_value
    _assert_no_unresolved_placeholders(expanded, field_name=field_name)
    path = Path(expanded)
    if not path.is_absolute():
        path = config_dir / path
    return path.resolve()
