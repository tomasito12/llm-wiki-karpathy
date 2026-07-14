"""Tests for private vault Git strategy reporting."""

from __future__ import annotations

from pathlib import Path

from src.wiki_ops.source_access import SourceAccessStatus
from src.wiki_ops.vault_git_strategy import (
    build_vault_git_recommendations,
    build_vault_git_strategy,
    collect_vault_git_inventory,
    collect_vault_git_state,
    default_vault_gitignore_content,
    evaluate_vault_git_readiness,
    format_vault_git_strategy_text,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def test_collect_vault_git_inventory_measures_markdown_and_binary_files(
    tmp_path: Path,
) -> None:
    """Inventory should count markdown, binary, and classified wiki content."""
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    (wiki_dir / "notes").mkdir()
    (wiki_dir / "sources" / "source-a.md").write_text("source body", encoding="utf-8")
    (wiki_dir / "topics").mkdir(parents=True)
    (wiki_dir / "topics" / "topic-a.md").write_text("topic body", encoding="utf-8")
    (wiki_dir / "notes" / "note.md").write_text("manual note", encoding="utf-8")
    (vault_root / "attachment.png").write_bytes(b"\x89PNG")

    inventory = collect_vault_git_inventory(vault_root, wiki_dir=wiki_dir)

    assert inventory.vault_exists is True
    assert inventory.total_files == 4
    assert inventory.markdown_files == 3
    assert inventory.binary_files == 1
    assert inventory.wiki_bytes > 0
    assert inventory.sources_bytes > 0
    managed = next(
        area for area in inventory.content_areas if area.classification == "managed_generated"
    )
    manual = next(
        area for area in inventory.content_areas if area.classification == "manual_or_legacy"
    )
    assert managed.file_count == 2
    assert manual.file_count == 1


def test_build_vault_git_recommendations_prefers_plain_git_for_small_vault(
    tmp_path: Path,
) -> None:
    """Small markdown-only vaults should recommend plain Git and local-only remotes."""
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    (wiki_dir / "sources" / "source-a.md").write_text("x" * 1000, encoding="utf-8")
    inventory = collect_vault_git_inventory(vault_root, wiki_dir=wiki_dir)
    git_state = collect_vault_git_state(vault_root)
    source_access = SourceAccessStatus(
        wiki_dir_exists=True,
        source_pages_total=1,
        embedded_full_text=1,
        locally_linked_source_text=0,
        external_url_only=0,
        malformed_pages=[],
        source_id_mismatches=[],
        source_pages_missing_raw_markdown=[],
        graph_sources=1,
        graph_sources_missing_pages=[],
        source_links_total=0,
        broken_source_link_targets=[],
    )

    recommendations = build_vault_git_recommendations(
        inventory=inventory,
        git_state=git_state,
        source_access=source_access,
    )

    assert recommendations.use_plain_git is True
    assert recommendations.use_git_lfs is False
    assert recommendations.remote_policy == "private_remote_later"
    assert recommendations.commit_full_source_text is True
    assert recommendations.ready_for_git_init is True


def test_build_vault_git_recommendations_blocks_when_source_access_has_gaps(
    tmp_path: Path,
) -> None:
    """Source access gaps should block remote policy and git init readiness."""
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    inventory = collect_vault_git_inventory(vault_root, wiki_dir=wiki_dir)
    git_state = collect_vault_git_state(vault_root)
    source_access = SourceAccessStatus(
        wiki_dir_exists=True,
        source_pages_total=1,
        embedded_full_text=0,
        locally_linked_source_text=0,
        external_url_only=1,
        malformed_pages=[],
        source_id_mismatches=[],
        source_pages_missing_raw_markdown=[],
        graph_sources=1,
        graph_sources_missing_pages=[],
        source_links_total=0,
        broken_source_link_targets=[],
    )

    recommendations = build_vault_git_recommendations(
        inventory=inventory,
        git_state=git_state,
        source_access=source_access,
    )
    readiness = evaluate_vault_git_readiness(
        inventory=inventory,
        git_state=git_state,
        recommendations=recommendations,
        source_access=source_access,
    )

    assert recommendations.ready_for_git_init is False
    assert recommendations.remote_policy == "blocked"
    assert readiness.status == "blocked"
    assert any("Source access verification has gaps" in item for item in readiness.blocked_reasons)


def test_collect_vault_git_state_detects_existing_repository(tmp_path: Path) -> None:
    """Existing vault Git metadata should be reported without writes."""
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    (vault_root / ".git").mkdir()

    git_state = collect_vault_git_state(vault_root)

    assert git_state.has_git is True
    assert git_state.has_commits is False
    assert git_state.has_remote is False


def test_build_vault_git_strategy_reports_large_file_lfs_trigger(tmp_path: Path) -> None:
    """Very large vault files should recommend Git LFS and block plain init."""
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    (wiki_dir / "sources" / "huge.md").write_text("x" * (26 * 1024 * 1024), encoding="utf-8")
    paths = _paths_for_vault(tmp_path, vault_root=vault_root, wiki_dir=wiki_dir)

    strategy = build_vault_git_strategy(paths)

    assert strategy.recommendations.use_git_lfs is True
    assert strategy.recommendations.ready_for_git_init is False
    assert strategy.readiness.status == "blocked"
    assert "Git LFS" in strategy.readiness.blocked_reasons[0]


def test_format_vault_git_strategy_text_includes_readiness_and_actions(tmp_path: Path) -> None:
    """Text output should expose readiness and init steps for small ready vaults."""
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    (wiki_dir / "sources" / "source-a.md").write_text("body", encoding="utf-8")
    paths = _paths_for_vault(tmp_path, vault_root=vault_root, wiki_dir=wiki_dir)
    strategy = build_vault_git_strategy(paths)

    report = format_vault_git_strategy_text(strategy)

    assert "Private Vault Git Strategy" in report
    assert "ready for git init: yes" in report
    assert "git init" in report
    assert "Initial private vault snapshot" in report


def test_default_vault_gitignore_content_excludes_obsidian_workspace_state() -> None:
    """The vault gitignore template should ignore editor-local Obsidian state."""
    content = default_vault_gitignore_content()

    assert ".obsidian/workspace.json" in content
    assert ".DS_Store" in content
    assert "wiki/" not in content


def test_collect_vault_git_inventory_ignores_git_internal_files(tmp_path: Path) -> None:
    """Inventory should exclude .git objects from vault size reporting."""
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    (wiki_dir / "sources" / "source-a.md").write_text("body", encoding="utf-8")
    git_objects = vault_root / ".git" / "objects" / "ab"
    git_objects.mkdir(parents=True)
    (git_objects / "cdef").write_bytes(b"x" * 5000)

    inventory = collect_vault_git_inventory(vault_root, wiki_dir=wiki_dir)

    assert inventory.total_files == 1
    assert inventory.total_bytes < 5000


def _paths_for_vault(tmp_path: Path, *, vault_root: Path, wiki_dir: Path) -> WikiPaths:
    """Return wiki paths pointing at a temporary vault fixture."""
    defaults = default_wiki_paths(tmp_path / "repo")
    return WikiPaths(
        repo_root=defaults.repo_root,
        knowledge_root=tmp_path / "knowledge",
        vault_root=vault_root,
        raw_dir=defaults.raw_dir,
        reviews_dir=defaults.reviews_dir,
        synthesis_dir=defaults.synthesis_dir,
        graph_path=defaults.graph_path,
        manifest_path=defaults.manifest_path,
        release_dir=defaults.release_dir,
        preview_dir=defaults.preview_dir,
        run_dir=defaults.run_dir,
        backup_dir=defaults.backup_dir,
        wiki_dir=wiki_dir,
        source_pages_dir=wiki_dir / "sources",
        source_index_path=wiki_dir / "sources" / "index.md",
        indexes_dir=wiki_dir / "indexes",
    )
