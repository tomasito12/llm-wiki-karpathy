"""Tests for wiki operations status CLI."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import status_cli


def test_status_cli_json_output_is_valid_json(tmp_path: Path, capsys) -> None:
    """The CLI should print valid JSON when --json is passed."""
    _bootstrap_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--json"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    payload = json.loads(captured)
    assert "sources" in payload
    assert "recommendations" in payload


def test_status_cli_repo_root_derives_default_paths(tmp_path: Path, capsys) -> None:
    """Only --repo-root should resolve all default paths under that directory."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    for index in range(3):
        (raw_dir / f"source-{index}.html").write_text("<html></html>", encoding="utf-8")
        (raw_dir / f"source-{index}.md").write_text("body", encoding="utf-8")
    (tmp_path / "state" / "reviews").mkdir(parents=True)
    (tmp_path / "wiki").mkdir()

    status_cli.main(["--repo-root", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert payload["sources"]["raw_html"] == 3
    assert payload["sources"]["paired"] == 3
    assert payload["reviews"]["artifacts"] == 0
    assert payload["render"]["wiki_dir_exists"] is True


def test_status_cli_explicit_path_overrides_repo_root_default(tmp_path: Path, capsys) -> None:
    """An explicit path flag should override the repo-root-derived default."""
    repo_root = tmp_path / "repo"
    alternate_raw = tmp_path / "alternate-raw"
    repo_raw = repo_root / "raw" / "readwise"
    repo_raw.mkdir(parents=True)
    alternate_raw.mkdir()
    (repo_raw / "repo-source.html").write_text("<html></html>", encoding="utf-8")
    (repo_raw / "repo-source.md").write_text("body", encoding="utf-8")
    (alternate_raw / "alt-source.html").write_text("<html></html>", encoding="utf-8")
    (alternate_raw / "alt-source.md").write_text("body", encoding="utf-8")
    (repo_root / "state" / "reviews").mkdir(parents=True)
    (repo_root / "wiki").mkdir()

    status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--raw-dir",
            str(alternate_raw),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["sources"]["raw_html"] == 1
    assert payload["sources"]["paired"] == 1


def test_status_cli_text_output_contains_header(tmp_path: Path, capsys) -> None:
    """The CLI text report should include the status header."""
    _bootstrap_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path)])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured


def _bootstrap_repo(tmp_path: Path) -> None:
    """Create minimal repo directories for CLI smoke tests."""
    (tmp_path / "raw" / "readwise").mkdir(parents=True)
    (tmp_path / "state" / "reviews").mkdir(parents=True)
    (tmp_path / "wiki").mkdir()
