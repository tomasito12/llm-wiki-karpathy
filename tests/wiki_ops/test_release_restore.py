"""Tests for release restore planning/execution from filesystem snapshots."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from src.wiki_ops.release_manifest import build_release_manifest, write_release_manifest
from src.wiki_ops.release_restore import ReleaseRestoreError, restore_release_from_snapshot
from src.wiki_paths.config import load_wiki_paths


def test_restore_fail_closed_without_snapshot_id(tmp_path: Path) -> None:
    """Restore must refuse when snapshot metadata is missing."""
    repo_root, config_path, _snapshot_root = _bootstrap_external_layout(tmp_path)
    paths = load_wiki_paths(repo_root=repo_root, config_path=config_path)
    manifest = build_release_manifest(paths, release_id="20260713T200000Z")
    paths.release_dir.mkdir(parents=True, exist_ok=True)
    write_release_manifest(manifest, overwrite=True)

    with pytest.raises(ReleaseRestoreError, match="snapshot_id"):
        restore_release_from_snapshot(
            paths,
            selector="20260713T200000Z",
            snapshot_root=tmp_path / "snap",
            area_selector=["all"],
            dry_run=True,
        )


def test_restore_dry_run_plans_paths_without_modifying(tmp_path: Path) -> None:
    """Dry-run should plan restore actions but not change destination files."""
    repo_root, config_path, snapshot_root = _bootstrap_external_layout(tmp_path)
    paths = load_wiki_paths(repo_root=repo_root, config_path=config_path)
    manifest = build_release_manifest(
        paths,
        release_id="20260713T200000Z",
        snapshot_id="restic:fake",
    )
    paths.release_dir.mkdir(parents=True, exist_ok=True)
    write_release_manifest(manifest, overwrite=True)

    original = paths.graph_path.read_text(encoding="utf-8")
    paths.graph_path.write_text('{"sources": ["changed"]}', encoding="utf-8")

    plan, report = restore_release_from_snapshot(
        paths,
        selector="20260713T200000Z",
        snapshot_root=snapshot_root,
        area_selector=["render_graph"],
        dry_run=True,
    )

    assert report is None
    assert plan.dry_run is True
    assert plan.release_id == "20260713T200000Z"
    assert any(item.area_key == "render_graph" for item in plan.items)
    assert paths.graph_path.read_text(encoding="utf-8") != original


def test_restore_executes_and_then_verifies(tmp_path: Path) -> None:
    """Executing a restore should replace files and return a verify report."""
    repo_root, config_path, snapshot_root = _bootstrap_external_layout(tmp_path)
    paths = load_wiki_paths(repo_root=repo_root, config_path=config_path)
    manifest = build_release_manifest(
        paths,
        release_id="20260713T200000Z",
        snapshot_id="restic:fake",
    )
    paths.release_dir.mkdir(parents=True, exist_ok=True)
    write_release_manifest(manifest, overwrite=True)

    # Drift one file so verify will fail before restore.
    paths.graph_path.write_text('{"sources": ["changed"]}', encoding="utf-8")

    executed, report = restore_release_from_snapshot(
        paths,
        selector="20260713T200000Z",
        snapshot_root=snapshot_root,
        area_selector=["render_graph"],
        dry_run=False,
    )

    assert executed.status == "executed"
    assert report is not None
    assert report.release_id == "20260713T200000Z"
    assert report.status in {"ok", "warning"}


def _bootstrap_external_layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create repo_root + external knowledge/vault roots + snapshot copy."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    knowledge_root = tmp_path / "llm-wiki-data"
    vault_root = tmp_path / "llm-wiki-vault-private"
    raw_dir = knowledge_root / "raw" / "readwise"
    reviews_dir = knowledge_root / "state" / "reviews" / "source"
    synthesis_dir = knowledge_root / "state" / "synthesis"
    graph_path = knowledge_root / "state" / "wiki_render_graph.json"
    manifest_path = knowledge_root / "state" / "wiki_render_manifest.json"
    wiki_dir = vault_root / "wiki"
    wiki_sources = wiki_dir / "sources"

    raw_dir.mkdir(parents=True)
    (raw_dir / "source.md").write_text("body", encoding="utf-8")
    (raw_dir / "source.html").write_text("<html></html>", encoding="utf-8")
    reviews_dir.mkdir(parents=True)
    (reviews_dir / "review.json").write_text("{}", encoding="utf-8")
    synthesis_dir.mkdir(parents=True)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text('{"sources": []}', encoding="utf-8")
    manifest_path.write_text("{}", encoding="utf-8")
    wiki_sources.mkdir(parents=True)
    (wiki_sources / "source.md").write_text(
        "---\nsource_text_available: true\n---\nbody\n",
        encoding="utf-8",
    )

    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        "\n".join(
            [
                "[paths]",
                f'knowledge_root = "{knowledge_root}"',
                f'vault_root = "{vault_root}"',
                'raw_dir = "{knowledge_root}/raw/readwise"',
                'reviews_dir = "{knowledge_root}/state/reviews"',
                'synthesis_dir = "{knowledge_root}/state/synthesis"',
                'graph_path = "{knowledge_root}/state/wiki_render_graph.json"',
                'manifest_path = "{knowledge_root}/state/wiki_render_manifest.json"',
                'release_dir = "{knowledge_root}/state/releases"',
                'preview_dir = "{knowledge_root}/tmp/synthesis_previews"',
                'run_dir = "{knowledge_root}/tmp/synthesis_runs"',
                'backup_dir = "{knowledge_root}/tmp/synthesis_backups"',
                'wiki_dir = "{vault_root}/wiki"',
            ]
        ),
        encoding="utf-8",
    )

    snapshot_root = tmp_path / "snapshot"
    snapshot_root.mkdir()
    shutil.copytree(knowledge_root, snapshot_root / knowledge_root.name)
    shutil.copytree(vault_root, snapshot_root / vault_root.name)

    # Sanity: snapshot content should match manifest expectations.
    graph_snapshot_path = snapshot_root / knowledge_root.name / "state" / "wiki_render_graph.json"
    payload = json.loads(graph_snapshot_path.read_text(encoding="utf-8"))
    assert payload == {"sources": []}

    return repo_root, config_path, snapshot_root
