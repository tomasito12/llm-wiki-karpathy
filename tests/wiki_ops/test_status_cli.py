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


def test_status_cli_paths_json_outputs_resolved_paths(tmp_path: Path, capsys) -> None:
    """The CLI should print resolved path configuration with --paths-json."""
    _bootstrap_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--paths-json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["raw_dir"].endswith("raw/readwise")
    assert payload["wiki_dir"].endswith("wiki")


def test_status_cli_paths_config_overrides_defaults(tmp_path: Path, capsys) -> None:
    """Config file paths should apply when --paths-config is passed."""
    repo_root = tmp_path / "repo"
    external_raw = tmp_path / "external-raw"
    external_raw.mkdir()
    (external_raw / "source.html").write_text("<html></html>", encoding="utf-8")
    (external_raw / "source.md").write_text("body", encoding="utf-8")
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
raw_dir = "{external_raw}"
""".strip(),
        encoding="utf-8",
    )
    (repo_root / "state" / "reviews").mkdir(parents=True)
    (repo_root / "wiki").mkdir()

    status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["sources"]["raw_html"] == 1
    assert payload["sources"]["paired"] == 1


def test_status_cli_explicit_path_overrides_paths_config(tmp_path: Path, capsys) -> None:
    """Explicit CLI flags should override config file values."""
    repo_root = tmp_path / "repo"
    config_raw = tmp_path / "config-raw"
    cli_raw = tmp_path / "cli-raw"
    for directory in (config_raw, cli_raw):
        directory.mkdir()
        (directory / "source.html").write_text("<html></html>", encoding="utf-8")
        (directory / "source.md").write_text("body", encoding="utf-8")
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
raw_dir = "{config_raw}"
""".strip(),
        encoding="utf-8",
    )
    (repo_root / "state" / "reviews").mkdir(parents=True)
    (repo_root / "wiki").mkdir()

    status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--raw-dir",
            str(cli_raw),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["sources"]["raw_html"] == 1


def test_status_cli_missing_paths_config_returns_error(tmp_path: Path, caplog) -> None:
    """An explicit missing config file should fail with a clear error."""
    _bootstrap_repo(tmp_path)
    missing = tmp_path / "missing.toml"

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--paths-config",
            str(missing),
        ]
    )

    assert exit_code == 2
    assert "Path config file not found" in caplog.text


def test_status_cli_text_output_contains_header(tmp_path: Path, capsys) -> None:
    """The CLI text report should include the status header."""
    _bootstrap_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path)])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured


def test_status_cli_retention_json_output_is_valid_json(tmp_path: Path, capsys) -> None:
    """The CLI should print valid retention JSON with --retention-json."""
    _bootstrap_repo(tmp_path)
    raw_dir = tmp_path / "raw" / "readwise"
    (raw_dir / "source.md").write_text("body", encoding="utf-8")

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--retention-json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "areas" in payload
    assert "cleanup_preflight" in payload
    assert payload["cleanup_preflight"]["cleanup_candidate_count"] == 0


def test_status_cli_retention_includes_readable_section(tmp_path: Path, capsys) -> None:
    """The CLI should append a retention section when --retention is passed."""
    _bootstrap_repo(tmp_path)
    preview_dir = tmp_path / "state" / "synthesis_previews"
    preview_dir.mkdir(parents=True)
    (preview_dir / "preview.md").write_text("preview", encoding="utf-8")

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--retention"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured
    assert "Retention Inventory" in captured
    assert "synthesis_previews" in captured


def test_status_cli_retention_respects_raw_dir_override(tmp_path: Path, capsys) -> None:
    """Retention inventory should honor explicit --raw-dir overrides."""
    repo_root = tmp_path / "repo"
    alternate_raw = tmp_path / "alternate-raw"
    repo_raw = repo_root / "raw" / "readwise"
    repo_raw.mkdir(parents=True)
    alternate_raw.mkdir()
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
            "--retention-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    raw_area = next(area for area in payload["areas"] if area["key"] == "raw_readwise")

    assert raw_area["file_count"] == 2
    assert raw_area["path"] == str(alternate_raw.resolve())


def test_status_cli_retention_respects_paths_config(tmp_path: Path, capsys) -> None:
    """Retention inventory should honor configured raw_dir from --paths-config."""
    repo_root = tmp_path / "repo"
    external_raw = tmp_path / "external-raw"
    external_raw.mkdir()
    (external_raw / "source.md").write_text("body", encoding="utf-8")
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
raw_dir = "{external_raw}"
""".strip(),
        encoding="utf-8",
    )
    (repo_root / "state" / "reviews").mkdir(parents=True)
    (repo_root / "wiki").mkdir()

    status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--retention-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    raw_area = next(area for area in payload["areas"] if area["key"] == "raw_readwise")

    assert raw_area["file_count"] == 1
    assert raw_area["path"] == str(external_raw.resolve())


def _bootstrap_repo(tmp_path: Path) -> None:
    """Create minimal repo directories for CLI smoke tests."""
    (tmp_path / "raw" / "readwise").mkdir(parents=True)
    (tmp_path / "state" / "reviews").mkdir(parents=True)
    (tmp_path / "wiki").mkdir()
