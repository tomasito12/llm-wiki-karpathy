"""Tests for vault orphan and duplicate cleanup."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops.release_manifest import SCHEMA_VERSION
from src.wiki_ops.vault_cleanup import (
    REAL_VAULT_CLEANUP_REQUIREMENT,
    build_vault_cleanup_plan,
    execute_vault_cleanup,
    format_vault_cleanup_dry_run_text,
)
from src.wiki_paths.config import WikiPaths


def _paths(tmp_path: Path) -> WikiPaths:
    """Build wiki paths for vault cleanup tests."""
    knowledge = tmp_path / "knowledge"
    vault = tmp_path / "vault"
    wiki = vault / "wiki"
    wiki.mkdir(parents=True)
    knowledge.mkdir()
    return WikiPaths(
        repo_root=tmp_path / "repo",
        knowledge_root=knowledge,
        vault_root=vault,
        raw_dir=knowledge / "raw" / "readwise",
        reviews_dir=knowledge / "state" / "reviews",
        synthesis_dir=knowledge / "state" / "synthesis",
        graph_path=knowledge / "state" / "wiki_render_graph.json",
        manifest_path=knowledge / "state" / "wiki_render_manifest.json",
        release_dir=knowledge / "state" / "releases",
        preview_dir=knowledge / "tmp" / "synthesis_previews",
        run_dir=knowledge / "tmp" / "synthesis_runs",
        backup_dir=knowledge / "tmp" / "synthesis_backups",
        wiki_dir=wiki,
        source_pages_dir=wiki / "sources" / "full",
        source_index_path=wiki / "sources" / "index.md",
        indexes_dir=wiki / "indexes",
    )


def _write_manifest(manifest_path: Path, paths: list[str]) -> None:
    """Write a minimal render manifest fixture."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"files": [{"path": path, "sha256": "abc"} for path in paths]}),
        encoding="utf-8",
    )


def _write_release_manifest(release_path: Path, *, wiki_dir: Path) -> None:
    """Write a minimal release manifest fixture."""
    release_path.parent.mkdir(parents=True, exist_ok=True)
    release_path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "ready",
                "paths": {
                    "raw_dir": "/tmp/raw",
                    "reviews_dir": "/tmp/reviews",
                    "synthesis_dir": "/tmp/synthesis",
                    "wiki_dir": str(wiki_dir.resolve()),
                    "graph_path": "/tmp/graph.json",
                    "manifest_path": "/tmp/manifest.json",
                    "release_dir": str(release_path.parent.resolve()),
                },
            }
        ),
        encoding="utf-8",
    )


def test_build_vault_cleanup_plan_includes_stale_orphan(tmp_path: Path) -> None:
    """Cleanup plan should include stale managed orphans."""
    paths = _paths(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(paths.manifest_path, ["topics/current.md"])
    (paths.wiki_dir / "topics").mkdir(parents=True)
    (paths.wiki_dir / "topics" / "current.md").write_text("# current\n", encoding="utf-8")
    (paths.wiki_dir / "topics" / "stale.md").write_text("# stale\n", encoding="utf-8")

    plan = build_vault_cleanup_plan(paths, repo_root=repo)

    relative_paths = {candidate.relative_path for candidate in plan.candidates}
    assert relative_paths == {"topics/stale.md"}
    assert plan.candidates[0].kind == "orphan_stale"
    assert REAL_VAULT_CLEANUP_REQUIREMENT in plan.blocked_reasons


def test_build_vault_cleanup_plan_prefers_manifest_duplicate_keep_path(tmp_path: Path) -> None:
    """Duplicate cleanup should remove only non-canonical duplicate paths."""
    paths = _paths(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    body = "# duplicate\n"
    (paths.wiki_dir / "topics").mkdir(parents=True)
    (paths.wiki_dir / "topics" / "keep.md").write_text(body, encoding="utf-8")
    (paths.wiki_dir / "topics" / "remove.md").write_text(body, encoding="utf-8")
    _write_manifest(paths.manifest_path, ["topics/keep.md"])

    plan = build_vault_cleanup_plan(paths, repo_root=repo)

    relative_paths = {candidate.relative_path for candidate in plan.candidates}
    assert relative_paths == {"topics/remove.md"}
    assert plan.candidates[0].kind == "duplicate"


def test_build_vault_cleanup_plan_includes_orphans_and_duplicate_removals(
    tmp_path: Path,
) -> None:
    """Cleanup plan should combine stale orphans and duplicate removals."""
    paths = _paths(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    body = "# duplicate\n"
    (paths.wiki_dir / "topics").mkdir(parents=True)
    (paths.wiki_dir / "topics" / "current.md").write_text("# current\n", encoding="utf-8")
    (paths.wiki_dir / "topics" / "stale.md").write_text("# stale\n", encoding="utf-8")
    (paths.wiki_dir / "topics" / "keep.md").write_text(body, encoding="utf-8")
    (paths.wiki_dir / "topics" / "remove.md").write_text(body, encoding="utf-8")
    _write_manifest(paths.manifest_path, ["topics/current.md", "topics/keep.md"])

    plan = build_vault_cleanup_plan(paths, repo_root=repo)

    relative_paths = {candidate.relative_path for candidate in plan.candidates}
    assert relative_paths == {"topics/remove.md", "topics/stale.md"}


def test_execute_vault_cleanup_deletes_candidates_after_release(tmp_path: Path) -> None:
    """Real cleanup should delete planned files when release validation passes."""
    paths = _paths(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(paths.manifest_path, ["topics/current.md"])
    stale = paths.wiki_dir / "topics" / "stale.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("# stale\n", encoding="utf-8")
    (paths.wiki_dir / "topics" / "current.md").write_text("# current\n", encoding="utf-8")
    release_id = "20260715T120000Z"
    _write_release_manifest(
        paths.release_dir / f"{release_id}.json",
        wiki_dir=paths.wiki_dir,
    )

    plan = build_vault_cleanup_plan(
        paths,
        repo_root=repo,
        dry_run=False,
        after_release=release_id,
        allow_path_mismatch=True,
    )
    assert not plan.blocked
    assert len(plan.candidates) == 1

    result = execute_vault_cleanup(
        plan,
        paths,
        repo_root=repo,
        allow_path_mismatch=True,
    )

    assert result.deleted_count == 1
    assert not stale.exists()
    assert result.report_path is not None
    assert result.report_path.is_file()


def test_format_vault_cleanup_dry_run_text_lists_candidates(tmp_path: Path) -> None:
    """Dry-run text should list delete candidates and real cleanup requirements."""
    paths = _paths(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(paths.manifest_path, [])
    stale = paths.wiki_dir / "topics" / "stale.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("# stale\n", encoding="utf-8")

    plan = build_vault_cleanup_plan(paths, repo_root=repo)
    text = format_vault_cleanup_dry_run_text(plan)

    assert "topics/stale.md" in text
    assert REAL_VAULT_CLEANUP_REQUIREMENT in text


def test_build_vault_cleanup_plan_blocks_without_render_manifest(tmp_path: Path) -> None:
    """Missing render manifest should block real cleanup."""
    paths = _paths(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()

    plan = build_vault_cleanup_plan(
        paths,
        repo_root=repo,
        dry_run=False,
        after_release="20260715T120000Z",
    )

    assert plan.blocked
    assert any("Render manifest is missing" in reason for reason in plan.blocked_reasons)
