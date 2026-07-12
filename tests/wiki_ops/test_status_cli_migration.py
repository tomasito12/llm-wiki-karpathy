"""CLI tests for migration plan support in wiki-ops-status."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import status_cli


def test_status_cli_migration_plan_appends_readable_section(tmp_path: Path, capsys) -> None:
    """The CLI should append a migration section when --migration-plan is passed."""
    _bootstrap_repo_local_layout(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--migration-plan"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured
    assert "Knowledge Store Migration Plan" in captured
    assert "Readiness:" in captured


def test_status_cli_migration_json_emits_valid_json_only(tmp_path: Path, capsys) -> None:
    """Migration JSON mode should emit valid JSON without creating files."""
    paths_root = tmp_path / "repo"
    _bootstrap_repo_local_layout(paths_root)
    release_dir = paths_root / "state" / "releases"

    exit_code = status_cli.main(["--repo-root", str(paths_root), "--migration-json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert "areas" in payload
    assert "Wiki Ops Status" not in json.dumps(payload)
    assert not release_dir.exists()


def test_status_cli_migration_json_respects_require_external_knowledge_root(
    tmp_path: Path,
    capsys,
) -> None:
    """Migration JSON should reflect blocked readiness for repo-local knowledge root."""
    _bootstrap_repo_local_layout(tmp_path)

    status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--migration-json",
            "--require-external-knowledge-root",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["readiness"]["status"] == "blocked"


def test_status_cli_existing_retention_json_unchanged(tmp_path: Path, capsys) -> None:
    """Retention JSON output should remain unchanged."""
    _bootstrap_repo_local_layout(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--retention-json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "cleanup_preflight" in payload
    assert "schema_version" not in payload


def _bootstrap_repo_local_layout(tmp_path: Path) -> None:
    """Create a minimal repo-local layout for migration CLI tests."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source.md").write_text("body", encoding="utf-8")
    review_dir = tmp_path / "state" / "reviews" / "source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text("{}", encoding="utf-8")
    (tmp_path / "state" / "synthesis").mkdir(parents=True)
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "page.md").write_text("page", encoding="utf-8")
    graph_dir = tmp_path / "state"
    graph_dir.mkdir(parents=True, exist_ok=True)
    (graph_dir / "wiki_render_graph.json").write_text("{}", encoding="utf-8")
    (graph_dir / "wiki_render_manifest.json").write_text("{}", encoding="utf-8")
    preview_dir = tmp_path / "state" / "synthesis_previews"
    preview_dir.mkdir(parents=True)
    (preview_dir / "preview.md").write_text("preview", encoding="utf-8")
