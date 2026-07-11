"""Tests for central wiki path configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.wiki_paths.config import (
    WikiPathsConfigError,
    default_wiki_paths,
    load_wiki_paths,
    resolve_path_template,
)


def test_default_wiki_paths_match_repo_local_layout(tmp_path: Path) -> None:
    """Without config, paths should match current repo-local defaults."""
    paths = default_wiki_paths(tmp_path)

    assert paths.repo_root == tmp_path.resolve()
    assert paths.knowledge_root == tmp_path.resolve()
    assert paths.vault_root == tmp_path.resolve()
    assert paths.raw_dir == tmp_path / "raw" / "readwise"
    assert paths.reviews_dir == tmp_path / "state" / "reviews"
    assert paths.synthesis_dir == tmp_path / "state" / "synthesis"
    assert paths.graph_path == tmp_path / "state" / "wiki_render_graph.json"
    assert paths.manifest_path == tmp_path / "state" / "wiki_render_manifest.json"
    assert paths.preview_dir == tmp_path / "state" / "synthesis_previews"
    assert paths.run_dir == tmp_path / "state" / "synthesis_runs"
    assert paths.backup_dir == tmp_path / "state" / "synthesis_backups"
    assert paths.wiki_dir == tmp_path / "wiki"
    assert paths.source_pages_dir == tmp_path / "wiki" / "sources" / "full"
    assert paths.source_index_path == tmp_path / "wiki" / "sources" / "index.md"
    assert paths.indexes_dir == tmp_path / "wiki" / "indexes"


def test_load_wiki_paths_without_config_uses_defaults(tmp_path: Path) -> None:
    """Missing config files should fall back to repo-local defaults."""
    paths = load_wiki_paths(repo_root=tmp_path)

    assert paths.raw_dir == tmp_path / "raw" / "readwise"
    assert paths.wiki_dir == tmp_path / "wiki"


def test_load_wiki_paths_from_env_override(tmp_path: Path, monkeypatch) -> None:
    """LLM_WIKI_PATHS_CONFIG should load an external config file."""
    knowledge_root = tmp_path / "knowledge"
    config_path = tmp_path / "custom-paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge_root}"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("LLM_WIKI_PATHS_CONFIG", str(config_path))

    paths = load_wiki_paths(repo_root=tmp_path / "repo")

    assert paths.knowledge_root == knowledge_root.resolve()
    assert paths.raw_dir == knowledge_root / "raw" / "readwise"
    assert paths.preview_dir == knowledge_root / "tmp" / "synthesis_previews"


def test_config_file_overrides_roots_and_derives_child_paths(tmp_path: Path) -> None:
    """Root overrides should derive child paths using the external layout."""
    knowledge_root = tmp_path / "data"
    vault_root = tmp_path / "vault"
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge_root}"
vault_root = "{vault_root}"
""".strip(),
        encoding="utf-8",
    )

    paths = load_wiki_paths(
        repo_root=tmp_path / "repo",
        config_path=config_path,
        config_required=True,
    )

    assert paths.reviews_dir == knowledge_root / "state" / "reviews"
    assert paths.synthesis_dir == knowledge_root / "state" / "synthesis"
    assert paths.wiki_dir == vault_root / "wiki"
    assert paths.source_pages_dir == vault_root / "sources" / "full"
    assert paths.indexes_dir == vault_root / "indexes"


def test_individual_path_entry_overrides_derived_default(tmp_path: Path) -> None:
    """Explicit path entries should override derived defaults."""
    custom_reviews = tmp_path / "custom-reviews"
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
reviews_dir = "{custom_reviews}"
""".strip(),
        encoding="utf-8",
    )

    paths = load_wiki_paths(
        repo_root=tmp_path,
        config_path=config_path,
        config_required=True,
    )

    assert paths.reviews_dir == custom_reviews.resolve()
    assert paths.raw_dir == tmp_path / "raw" / "readwise"


def test_relative_paths_resolve_relative_to_config_directory(tmp_path: Path) -> None:
    """Relative config paths should resolve against the config file parent."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    relative_target = tmp_path / "external" / "reviews"
    config_path = config_dir / "wiki_paths.toml"
    config_path.write_text(
        """
[paths]
reviews_dir = "../external/reviews"
""".strip(),
        encoding="utf-8",
    )

    paths = load_wiki_paths(
        repo_root=tmp_path / "repo",
        config_path=config_path,
        config_required=True,
    )

    assert paths.reviews_dir == relative_target.resolve()


def test_placeholder_expansion_uses_configured_roots(tmp_path: Path) -> None:
    """Template placeholders should expand using configured root paths."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    knowledge_root = tmp_path / "knowledge"
    config_path = config_dir / "wiki_paths.toml"
    config_path.write_text(
        """
[paths]
knowledge_root = "../knowledge"
graph_path = "{knowledge_root}/state/wiki_render_graph.json"
""".strip(),
        encoding="utf-8",
    )

    paths = load_wiki_paths(
        repo_root=tmp_path / "repo",
        config_path=config_path,
        config_required=True,
    )

    assert paths.graph_path == (knowledge_root / "state" / "wiki_render_graph.json").resolve()


def test_resolve_path_template_replaces_known_variables(tmp_path: Path) -> None:
    """resolve_path_template should substitute all provided variables."""
    variables = {
        "knowledge_root": tmp_path / "knowledge",
        "vault_root": tmp_path / "vault",
    }
    expanded = resolve_path_template(
        "{knowledge_root}/state/reviews",
        variables,
    )

    assert expanded == str(tmp_path / "knowledge" / "state" / "reviews")


def test_explicitly_requested_missing_config_raises_clear_error(tmp_path: Path) -> None:
    """An explicit --paths-config path must exist."""
    missing = tmp_path / "missing.toml"

    with pytest.raises(WikiPathsConfigError, match="Path config file not found"):
        load_wiki_paths(
            repo_root=tmp_path,
            config_path=missing,
            config_required=True,
        )


def test_default_config_location_is_used_when_present(tmp_path: Path) -> None:
    """config/wiki_paths.toml under repo root should load automatically."""
    knowledge_root = tmp_path / "knowledge"
    config_path = tmp_path / "config" / "wiki_paths.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge_root}"
""".strip(),
        encoding="utf-8",
    )

    paths = load_wiki_paths(repo_root=tmp_path)

    assert paths.knowledge_root == knowledge_root.resolve()


def test_wiki_paths_to_dict_returns_absolute_strings(tmp_path: Path) -> None:
    """WikiPaths.to_dict should serialize absolute path strings."""
    payload = default_wiki_paths(tmp_path).to_dict()

    assert payload["raw_dir"].endswith("raw/readwise")
    assert Path(payload["wiki_dir"]).is_absolute()


def test_invalid_toml_raises_config_error(tmp_path: Path) -> None:
    """Invalid TOML should raise WikiPathsConfigError."""
    config_path = tmp_path / "bad.toml"
    config_path.write_text("paths = [", encoding="utf-8")

    with pytest.raises(WikiPathsConfigError, match="Invalid TOML"):
        load_wiki_paths(
            repo_root=tmp_path,
            config_path=config_path,
            config_required=True,
        )


def test_unknown_paths_keys_raise_config_error(tmp_path: Path) -> None:
    """Typos in [paths] keys should fail instead of being ignored."""
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        """
[paths]
syntheses_dir = "../custom/synthesis"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(WikiPathsConfigError, match="Unknown keys in \\[paths\\]: syntheses_dir"):
        load_wiki_paths(
            repo_root=tmp_path,
            config_path=config_path,
            config_required=True,
        )


def test_unresolved_placeholders_raise_config_error(tmp_path: Path) -> None:
    """Misspelled template placeholders should fail instead of becoming relative paths."""
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        """
[paths]
synthesis_dir = "{knowlege_root}/state/synthesis"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(
        WikiPathsConfigError,
        match="Unresolved placeholders in paths.synthesis_dir: \\{knowlege_root\\}",
    ):
        load_wiki_paths(
            repo_root=tmp_path,
            config_path=config_path,
            config_required=True,
        )
