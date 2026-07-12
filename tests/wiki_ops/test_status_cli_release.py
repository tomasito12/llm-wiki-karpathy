"""CLI tests for release manifest support in wiki-ops-status."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import status_cli


def test_status_cli_release_json_writes_no_files(tmp_path: Path, capsys) -> None:
    """JSON preview should not create release directories or manifest files."""
    _bootstrap_release_repo(tmp_path)
    release_dir = tmp_path / "state" / "releases"

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--release-json"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert not release_dir.exists()
    payload = json.loads(captured)
    assert payload["schema_version"] == 1
    assert "areas" in payload


def test_status_cli_release_dry_run_prints_preview_section(tmp_path: Path, capsys) -> None:
    """Dry-run should print a readable release preview section."""
    _bootstrap_release_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--release-dry-run"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Release Manifest Preview" in captured
    assert "release id:" in captured


def test_status_cli_write_release_manifest_requires_yes(tmp_path: Path, caplog) -> None:
    """Writing without --yes should fail with exit code 2."""
    _bootstrap_release_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--write-release-manifest"])

    assert exit_code == 2
    assert "--write-release-manifest requires --yes" in caplog.text
    assert not (tmp_path / "state" / "releases").exists()


def test_status_cli_write_release_manifest_with_yes_creates_one_file(
    tmp_path: Path,
    capsys,
) -> None:
    """Writing with --yes should create exactly one manifest file."""
    _bootstrap_release_repo(tmp_path)

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--write-release-manifest",
            "--yes",
        ]
    )
    captured = capsys.readouterr().out
    release_dir = tmp_path / "state" / "releases"

    assert exit_code == 0
    manifests = list(release_dir.glob("*.json"))
    assert len(manifests) == 1
    assert "Wrote release manifest:" in captured


def test_status_cli_write_release_manifest_does_not_overwrite_by_default(
    tmp_path: Path,
    caplog,
) -> None:
    """Existing manifest files should not be overwritten by default."""
    _bootstrap_release_repo(tmp_path)
    status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--write-release-manifest",
            "--yes",
            "--release-id",
            "20260712T223000Z",
        ]
    )

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "--write-release-manifest",
            "--yes",
            "--release-id",
            "20260712T223000Z",
        ]
    )

    assert exit_code == 2
    assert "Release manifest already exists" in caplog.text
    assert len(list((tmp_path / "state" / "releases").glob("*.json"))) == 1


def test_status_cli_release_respects_raw_dir_override(tmp_path: Path, capsys) -> None:
    """Release manifest should honor explicit --raw-dir overrides."""
    repo_root = tmp_path / "repo"
    alternate_raw = tmp_path / "alternate-raw"
    alternate_raw.mkdir()
    (alternate_raw / "alt-source.html").write_text("<html></html>", encoding="utf-8")
    (alternate_raw / "alt-source.md").write_text("body", encoding="utf-8")
    _bootstrap_release_repo(repo_root)

    status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--raw-dir",
            str(alternate_raw),
            "--release-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["paths"]["raw_dir"] == str(alternate_raw.resolve())
    assert payload["areas"]["raw_readwise"]["file_count"] == 2


def test_status_cli_release_respects_paths_config(tmp_path: Path, capsys) -> None:
    """Release manifest should honor configured raw_dir from --paths-config."""
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
    _bootstrap_release_repo(repo_root)

    status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--release-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert payload["paths"]["raw_dir"] == str(external_raw.resolve())
    assert payload["areas"]["raw_readwise"]["file_count"] == 2


def test_status_cli_existing_json_behavior_unchanged(tmp_path: Path, capsys) -> None:
    """Default --json status output should remain unchanged."""
    _bootstrap_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "sources" in payload
    assert "schema_version" not in payload


def test_status_cli_existing_retention_json_behavior_unchanged(tmp_path: Path, capsys) -> None:
    """Retention JSON output should remain unchanged."""
    _bootstrap_repo(tmp_path)

    exit_code = status_cli.main(["--repo-root", str(tmp_path), "--retention-json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "areas" in payload
    assert "cleanup_preflight" in payload
    assert "schema_version" not in payload


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


def _bootstrap_repo(tmp_path: Path) -> None:
    """Create minimal repo directories for CLI smoke tests."""
    (tmp_path / "raw" / "readwise").mkdir(parents=True)
    (tmp_path / "state" / "reviews").mkdir(parents=True)
    (tmp_path / "wiki").mkdir()
