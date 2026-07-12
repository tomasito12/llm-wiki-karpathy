"""CLI tests for wiki-cleanup."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import cleanup_cli
from src.wiki_ops.release_manifest import (
    SCHEMA_VERSION,
    GitMetadata,
    ReleaseAreaSummary,
    ReleaseManifest,
    ReleaseStatus,
    write_release_manifest,
)
from src.wiki_paths.config import default_wiki_paths


def test_default_cli_behavior_is_dry_run(tmp_path: Path, capsys) -> None:
    """Running wiki-cleanup without flags should behave like dry-run."""
    _bootstrap_cleanup_repo(tmp_path)

    exit_code = cleanup_cli.main(["--repo-root", str(tmp_path)])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Cleanup Dry Run" in captured


def test_dry_run_writes_no_files_and_deletes_nothing(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    """Dry-run should not create cleanup reports or delete files."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    delete_calls: list[Path] = []

    def _track_unlink(self: Path, missing_ok: bool = False) -> None:
        delete_calls.append(self)
        raise AssertionError("unexpected delete")

    monkeypatch.setattr(Path, "unlink", _track_unlink, raising=False)

    exit_code = cleanup_cli.main(["--repo-root", str(tmp_path), "--dry-run", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["dry_run"] is True
    assert not (paths.knowledge_root / "state" / "cleanup_runs").exists()
    assert delete_calls == []


def test_yes_without_after_release_exits_two(tmp_path: Path, caplog) -> None:
    """Real cleanup without --after-release should fail."""
    _bootstrap_cleanup_repo(tmp_path)

    exit_code = cleanup_cli.main(["--repo-root", str(tmp_path), "--yes"])

    assert exit_code == 2
    assert "requires --after-release" in caplog.text


def test_dry_run_with_yes_exits_two(tmp_path: Path, caplog) -> None:
    """Combining --dry-run and --yes should fail."""
    _bootstrap_cleanup_repo(tmp_path)

    exit_code = cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--dry-run",
            "--yes",
            "--after-release",
            "20260712T223000Z",
        ]
    )

    assert exit_code == 2
    assert "Cannot combine --dry-run with --yes" in caplog.text


def test_missing_release_manifest_exits_two_for_real_cleanup(tmp_path: Path, caplog) -> None:
    """Missing release manifest should block real cleanup."""
    _bootstrap_cleanup_repo(tmp_path)

    exit_code = cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--yes",
            "--after-release",
            "20260712T223000Z",
        ]
    )

    assert exit_code == 2
    assert "Release manifest not found" in caplog.text


def test_blocked_release_manifest_exits_two_for_real_cleanup(tmp_path: Path, caplog) -> None:
    """Blocked release manifest should block real cleanup."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    _write_release_manifest(paths, release_id="20260712T223000Z", status="blocked")

    exit_code = cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--yes",
            "--after-release",
            "20260712T223000Z",
        ]
    )

    assert exit_code == 2
    assert "blocked" in caplog.text.lower()


def test_real_cleanup_with_valid_release_manifest_deletes_files(
    tmp_path: Path,
    capsys,
) -> None:
    """Valid release manifest should allow real cleanup of temporary files."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    preview = paths.preview_dir / "topic" / "example.md"
    preview.parent.mkdir(parents=True, exist_ok=True)
    preview.write_text("preview", encoding="utf-8")
    _write_release_manifest(paths, release_id="20260712T223000Z", status="warning")

    exit_code = cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--yes",
            "--after-release",
            "20260712T223000Z",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert preview.exists() is False
    assert "Wiki Cleanup Complete" in captured
    assert list((paths.knowledge_root / "state" / "cleanup_runs").glob("*.json"))


def test_json_output_is_valid_json(tmp_path: Path, capsys) -> None:
    """--json should emit valid cleanup plan JSON."""
    _bootstrap_cleanup_repo(tmp_path)

    exit_code = cleanup_cli.main(["--repo-root", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "candidates" in payload
    assert "blocked_reasons" in payload


def test_area_filter_limits_candidates(tmp_path: Path, capsys) -> None:
    """--area should limit cleanup candidates to one allowlisted area."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    preview = paths.preview_dir / "preview.md"
    preview.write_text("preview", encoding="utf-8")
    backup = paths.backup_dir / "backup.json"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text("{}", encoding="utf-8")

    cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--json",
            "--area",
            "synthesis_previews",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert {candidate["area_key"] for candidate in payload["candidates"]} <= {
        "synthesis_previews"
    }


def test_unknown_area_exits_two(tmp_path: Path, caplog) -> None:
    """Unknown cleanup areas should fail."""
    _bootstrap_cleanup_repo(tmp_path)

    exit_code = cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--area",
            "wiki",
        ]
    )

    assert exit_code == 2
    assert "non-allowed cleanup area" in caplog.text


def test_path_mismatch_exits_two_without_allow_flag(tmp_path: Path, caplog) -> None:
    """Path mismatch should block real cleanup unless explicitly allowed."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    _write_release_manifest(paths, release_id="20260712T223000Z", status="warning")
    moved_wiki = tmp_path / "moved-wiki"
    moved_wiki.mkdir()
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
wiki_dir = "{moved_wiki}"
""".strip(),
        encoding="utf-8",
    )

    exit_code = cleanup_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--paths-config",
            str(config_path),
            "--yes",
            "--after-release",
            "20260712T223000Z",
        ]
    )

    assert exit_code == 2
    assert "paths do not match" in caplog.text


def _bootstrap_cleanup_repo(tmp_path: Path):
    """Create a minimal repo with temporary artifacts."""
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    (paths.raw_dir / "source.md").write_text("body", encoding="utf-8")
    review_dir = paths.reviews_dir / "source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text("{}", encoding="utf-8")
    paths.synthesis_dir.mkdir(parents=True)
    paths.wiki_dir.mkdir(parents=True)
    (paths.wiki_dir / "page.md").write_text("page", encoding="utf-8")
    paths.graph_path.parent.mkdir(parents=True, exist_ok=True)
    paths.graph_path.write_text("{}", encoding="utf-8")
    paths.manifest_path.write_text("{}", encoding="utf-8")
    paths.preview_dir.mkdir(parents=True, exist_ok=True)
    (paths.preview_dir / "seed.md").write_text("seed", encoding="utf-8")
    return paths


def _write_release_manifest(
    paths,
    *,
    release_id: str,
    status: ReleaseStatus,
) -> Path:
    """Write a minimal valid release manifest for cleanup tests."""
    manifest = ReleaseManifest(
        schema_version=SCHEMA_VERSION,
        release_id=release_id,
        created_at="2026-07-12T22:30:00Z",
        status=status,
        status_reasons=[],
        code=GitMetadata(repo_root=paths.repo_root, git_commit="abc", git_dirty=False),
        paths={
            "raw_dir": str(paths.raw_dir),
            "reviews_dir": str(paths.reviews_dir),
            "synthesis_dir": str(paths.synthesis_dir),
            "wiki_dir": str(paths.wiki_dir),
            "graph_path": str(paths.graph_path),
            "manifest_path": str(paths.manifest_path),
            "release_dir": str(paths.release_dir),
        },
        areas={
            "raw_readwise": ReleaseAreaSummary("canonical", True, 1, 1, "hash"),
            "reviews": ReleaseAreaSummary("canonical", True, 1, 1, "hash"),
            "synthesis_cache": ReleaseAreaSummary("canonical", True, 0, 0, "hash"),
            "render_graph": ReleaseAreaSummary("generated", True, 1, 1, "hash"),
            "render_manifest": ReleaseAreaSummary("generated", True, 1, 1, "hash"),
            "wiki": ReleaseAreaSummary("generated", True, 1, 1, "hash"),
        },
        counts={"raw_files": 1, "reviews": 1, "synthesis_entries": 0, "wiki_files": 1},
        retention={
            "temporary_file_count": 1,
            "temporary_byte_count": 1,
            "cleanup_candidate_count": 0,
            "cleanup_blocked_reason": "test",
        },
        warnings=[],
        output_path=paths.release_dir / f"{release_id}.json",
    )
    return write_release_manifest(manifest)
