"""Tests for ingest queue CLI path configuration."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_queue import cli


def _bootstrap_raw_and_reviews(
    raw_dir: Path,
    reviews_dir: Path,
) -> None:
    """Create one paired export and an empty reviews directory."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    reviews_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "source.html").write_text("<html></html>", encoding="utf-8")
    (raw_dir / "source.md").write_text("body", encoding="utf-8")


def test_ingest_queue_uses_configured_paths(tmp_path: Path, capsys) -> None:
    """Configured external paths should be used when no explicit flags are passed."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    raw_dir = knowledge / "raw" / "readwise"
    reviews_dir = knowledge / "state" / "reviews"
    repo.mkdir()
    _bootstrap_raw_and_reviews(raw_dir, reviews_dir)
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
""".strip(),
        encoding="utf-8",
    )

    code = cli.main(["--paths-config", str(config_path), "--json"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["status"] == "pending"


def test_ingest_queue_explicit_raw_dir_overrides_config(tmp_path: Path, capsys) -> None:
    """Explicit --raw-dir should override configured defaults."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    alternate_raw = tmp_path / "alternate-raw"
    reviews_dir = knowledge / "state" / "reviews"
    repo.mkdir()
    _bootstrap_raw_and_reviews(knowledge / "raw" / "readwise", reviews_dir)
    _bootstrap_raw_and_reviews(alternate_raw, reviews_dir)
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
""".strip(),
        encoding="utf-8",
    )

    code = cli.main(
        [
            "--paths-config",
            str(config_path),
            "--raw-dir",
            str(alternate_raw),
            "--json",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1


def test_ingest_queue_without_config_uses_repo_local_defaults(tmp_path: Path, monkeypatch) -> None:
    """Without config the CLI should keep repo-local defaults."""
    repo = tmp_path / "repo"
    raw_dir = repo / "raw" / "readwise"
    reviews_dir = repo / "state" / "reviews"
    repo.mkdir()
    _bootstrap_raw_and_reviews(raw_dir, reviews_dir)
    monkeypatch.setattr("src.ingest_queue.cli._repo_root", lambda: repo)

    code = cli.main(["--json"])

    assert code == 0


def test_ingest_queue_missing_paths_config_exits_two(tmp_path: Path) -> None:
    """Invalid --paths-config should exit with code 2."""
    code = cli.main(["--paths-config", str(tmp_path / "missing.toml"), "--json"])
    assert code == 2
