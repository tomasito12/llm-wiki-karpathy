"""Tests for dashboard wiki path helpers."""

from __future__ import annotations

from pathlib import Path

from src.dashboard.paths import (
    REPO_LOCAL_INGESTION_WARNING,
    external_roots_configured,
    format_paths_config_label,
    ingestion_paths_point_inside_repo,
    load_dashboard_wiki_paths,
    path_is_inside_repo,
    resolve_active_paths_config_path,
)
from src.wiki_paths.config import default_wiki_paths, load_wiki_paths


def test_format_paths_config_label_without_config(tmp_path: Path) -> None:
    """Without a config file the label should mention repo-local defaults."""
    repo = tmp_path / "repo"
    repo.mkdir()

    assert format_paths_config_label(repo) == "repo-local defaults"
    assert resolve_active_paths_config_path(repo) is None


def test_format_paths_config_label_uses_default_config_file(tmp_path: Path) -> None:
    """The default config path under config/wiki_paths.toml should be detected."""
    repo = tmp_path / "repo"
    config_dir = repo / "config"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "wiki_paths.toml"
    config_path.write_text("[paths]\n", encoding="utf-8")

    assert resolve_active_paths_config_path(repo) == config_path
    assert format_paths_config_label(repo) == str(config_path.resolve())


def test_format_paths_config_label_respects_env_override(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """LLM_WIKI_PATHS_CONFIG should take precedence over the default config path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    env_config = tmp_path / "external.toml"
    env_config.write_text("[paths]\n", encoding="utf-8")
    monkeypatch.setenv("LLM_WIKI_PATHS_CONFIG", str(env_config))

    assert resolve_active_paths_config_path(repo) == env_config
    assert format_paths_config_label(repo) == str(env_config.resolve())


def test_load_dashboard_wiki_paths_reads_config(tmp_path: Path, monkeypatch) -> None:
    """Dashboard path loading should honor config/wiki_paths.toml when present."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    config_dir = repo / "config"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.chdir(repo)
    monkeypatch.setattr(
        "src.dashboard.paths.load_repo_dotenv",
        lambda: repo,
    )

    loaded_repo, paths, label = load_dashboard_wiki_paths()

    assert loaded_repo == repo
    assert paths.raw_dir == knowledge / "raw" / "readwise"
    assert paths.reviews_dir == knowledge / "state" / "reviews"
    assert label == str(config_path.resolve())


def test_external_roots_configured_detects_external_knowledge(tmp_path: Path) -> None:
    """External knowledge root should be detected when it differs from the repo."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    repo.mkdir()
    knowledge.mkdir()
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f'[paths]\nknowledge_root = "{knowledge}"\n',
        encoding="utf-8",
    )
    paths = load_wiki_paths(
        repo_root=repo,
        config_path=config_path,
    )

    assert external_roots_configured(paths) is True


def test_ingestion_paths_point_inside_repo_warns_for_repo_local_selection(tmp_path: Path) -> None:
    """Repo-local ingestion paths should trigger a warning when roots are externalized."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    vault = tmp_path / "vault"
    for path in (repo, knowledge, vault):
        path.mkdir()
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
vault_root = "{vault}"
""".strip(),
        encoding="utf-8",
    )
    paths = load_wiki_paths(repo_root=repo, config_path=config_path)

    assert ingestion_paths_point_inside_repo(
        paths,
        raw_dir=repo / "raw" / "readwise",
        reviews_root=repo / "state" / "reviews",
        wiki_root=repo / "wiki",
    )
    assert REPO_LOCAL_INGESTION_WARNING.startswith("Warning:")


def test_ingestion_paths_point_inside_repo_ignores_external_selections(tmp_path: Path) -> None:
    """External ingestion paths should not trigger the repo-local warning."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    vault = tmp_path / "vault"
    for path in (repo, knowledge, vault):
        path.mkdir()
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
vault_root = "{vault}"
""".strip(),
        encoding="utf-8",
    )
    paths = load_wiki_paths(repo_root=repo, config_path=config_path)

    assert (
        ingestion_paths_point_inside_repo(
            paths,
            raw_dir=paths.raw_dir,
            reviews_root=paths.reviews_dir,
            wiki_root=paths.wiki_dir,
        )
        is False
    )


def test_path_is_inside_repo_handles_outside_paths(tmp_path: Path) -> None:
    """Paths outside the repo should not be considered inside it."""
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()

    assert path_is_inside_repo(repo / "raw", repo) is True
    assert path_is_inside_repo(outside, repo) is False


def test_default_wiki_paths_remain_repo_local_without_config(tmp_path: Path) -> None:
    """Fallback defaults should still point at repo-local directories."""
    repo = tmp_path / "repo"
    repo.mkdir()
    paths = default_wiki_paths(repo)

    assert paths.raw_dir == repo / "raw" / "readwise"
    assert paths.reviews_dir == repo / "state" / "reviews"
    assert paths.wiki_dir == repo / "wiki"
