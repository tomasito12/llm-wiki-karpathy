"""CLI tests for release verification in wiki-ops-status."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import status_cli
from src.wiki_ops.release_manifest import build_release_manifest


def test_status_cli_verify_json_prints_only_verification_payload(tmp_path: Path, capsys) -> None:
    """Verify JSON mode should print only verification JSON."""
    _bootstrap_release_repo(tmp_path)
    _write_manifest(tmp_path, release_id="20260712T140520Z", status="ready")

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--verify-release",
            "latest",
            "--verify-json",
        ]
    )
    captured = capsys.readouterr().out
    payload = json.loads(captured)

    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert payload["release_id"] == "20260712T140520Z"
    assert "areas" in payload
    assert "sources" not in payload


def test_status_cli_verify_release_appends_readable_section(tmp_path: Path, capsys) -> None:
    """Verify mode should append a readable section to the normal status report."""
    _bootstrap_release_repo(tmp_path)
    _write_manifest(tmp_path, release_id="20260712T140520Z", status="ready")

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--verify-release",
            "latest",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured
    assert "Release Verification" in captured
    assert "20260712T140520Z" in captured


def test_status_cli_verify_release_missing_directory_exits_two(tmp_path: Path, caplog) -> None:
    """Missing release manifests should exit with code 2."""
    _bootstrap_release_repo(tmp_path)

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--verify-release",
            "latest",
        ]
    )

    assert exit_code == 2
    assert "No release manifests found" in caplog.text
    assert not (tmp_path / "state" / "releases").exists()


def test_status_cli_verify_release_content_mismatch_exits_two(tmp_path: Path, capsys) -> None:
    """Content drift should exit with code 2."""
    _bootstrap_release_repo(tmp_path)
    _write_manifest(tmp_path, release_id="20260712T140520Z", status="ready")
    (tmp_path / "raw" / "readwise" / "extra.md").write_text("changed", encoding="utf-8")

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--verify-release",
            "latest",
            "--verify-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "error"


def test_status_cli_verify_allow_path_mismatch_downgrades_path_error_to_warning(
    tmp_path: Path,
    capsys,
) -> None:
    """Allowed path mismatches should verify as warning when content still matches."""
    _bootstrap_release_repo(tmp_path)
    _write_manifest(tmp_path, release_id="20260712T140520Z", status="ready")
    moved_raw = tmp_path / "moved" / "raw"
    moved_raw.mkdir(parents=True)
    raw_dir = tmp_path / "raw" / "readwise"
    for file_path in raw_dir.glob("*"):
        (moved_raw / file_path.name).write_text(
            file_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--raw-dir",
            str(moved_raw),
            "--verify-release",
            "latest",
            "--verify-json",
            "--verify-allow-path-mismatch",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "warning"
    assert payload["path_status"] == "warning"


def _write_manifest(tmp_path: Path, *, release_id: str, status: str) -> None:
    """Write one release manifest that matches the current repo layout."""
    from src.wiki_paths.config import default_wiki_paths

    paths = default_wiki_paths(tmp_path)
    manifest = build_release_manifest(paths, release_id=release_id)
    payload = manifest.to_dict()
    payload["status"] = status
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    (release_dir / f"{release_id}.json").write_text(json.dumps(payload), encoding="utf-8")


def _bootstrap_release_repo(tmp_path: Path) -> None:
    """Create a minimal repo layout that satisfies release readiness checks."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source.html").write_text("<html></html>", encoding="utf-8")
    (raw_dir / "source.md").write_text("body", encoding="utf-8")
    review_dir = tmp_path / "state" / "reviews" / "source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text("{}", encoding="utf-8")
    synthesis_dir = tmp_path / "state" / "synthesis"
    synthesis_dir.mkdir(parents=True)
    graph_path = tmp_path / "state" / "wiki_render_graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text('{"sources": []}', encoding="utf-8")
    manifest_path = tmp_path / "state" / "wiki_render_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    wiki_source = tmp_path / "wiki" / "sources"
    wiki_source.mkdir(parents=True)
    (wiki_source / "source.md").write_text(
        "---\nsource_text_available: true\n---\nbody\n",
        encoding="utf-8",
    )
