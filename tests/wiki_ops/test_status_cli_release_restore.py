"""CLI tests for release restore support in wiki-ops-status."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from src.wiki_ops import status_cli


def test_status_cli_restore_requires_snapshot_root(tmp_path: Path, caplog) -> None:
    """Restore should fail without --restore-snapshot-root."""
    repo_root, config_path, _snapshot_root = _bootstrap_external_layout(tmp_path)
    _write_manifest(repo_root, config_path, snapshot_id="restic:fake")

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--restore-release",
            "20260713T200000Z",
        ]
    )

    assert exit_code == 2
    assert "--restore-release requires --restore-snapshot-root" in caplog.text


def test_status_cli_restore_requires_yes_unless_dry_run(tmp_path: Path, caplog) -> None:
    """Restore should require --yes unless --restore-dry-run is set."""
    repo_root, config_path, snapshot_root = _bootstrap_external_layout(tmp_path)
    _write_manifest(repo_root, config_path, snapshot_id="restic:fake")

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--restore-release",
            "20260713T200000Z",
            "--restore-snapshot-root",
            str(snapshot_root),
        ]
    )

    assert exit_code == 2
    assert "--restore-release requires --yes" in caplog.text


def test_status_cli_restore_dry_run_prints_plan(tmp_path: Path, capsys) -> None:
    """Dry-run restore should print a readable restore plan."""
    repo_root, config_path, snapshot_root = _bootstrap_external_layout(tmp_path)
    _write_manifest(repo_root, config_path, snapshot_id="restic:fake")

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--restore-release",
            "20260713T200000Z",
            "--restore-snapshot-root",
            str(snapshot_root),
            "--restore-areas",
            "render_graph",
            "--restore-dry-run",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Release Restore" in captured
    assert "render_graph" in captured


def test_status_cli_restore_json_prints_payload(tmp_path: Path, capsys) -> None:
    """JSON output should include snapshot metadata and planned items."""
    repo_root, config_path, snapshot_root = _bootstrap_external_layout(tmp_path)
    _write_manifest(repo_root, config_path, snapshot_id="restic:fake")
    capsys.readouterr()

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--restore-release",
            "20260713T200000Z",
            "--restore-snapshot-root",
            str(snapshot_root),
            "--restore-areas",
            "render_graph",
            "--restore-dry-run",
            "--restore-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["release_id"] == "20260713T200000Z"
    assert payload["snapshot_id"] == "restic:fake"
    assert payload["dry_run"] is True
    assert payload["items"][0]["area_key"] == "render_graph"


def _write_manifest(repo_root: Path, config_path: Path, *, snapshot_id: str) -> None:
    """Write one release manifest using the CLI codepath."""
    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--write-release-manifest",
            "--yes",
            "--release-id",
            "20260713T200000Z",
            "--snapshot-id",
            snapshot_id,
        ]
    )
    assert exit_code == 0


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

    return repo_root, config_path, snapshot_root
