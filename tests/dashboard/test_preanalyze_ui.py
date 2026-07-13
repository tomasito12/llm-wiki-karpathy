"""Tests for pre-analysis dashboard helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from src.dashboard.preanalyze_ui import (
    latest_preanalyze_log,
    read_log_tail,
    start_preanalyze_process,
)


def test_latest_preanalyze_log_returns_newest_log(tmp_path: Path) -> None:
    """The newest log by modification time is selected."""
    older = tmp_path / "older.log"
    newer = tmp_path / "newer.log"
    older.write_text("old", encoding="utf-8")
    newer.write_text("new", encoding="utf-8")
    newer.touch()

    assert latest_preanalyze_log(tmp_path) == newer


def test_read_log_tail_returns_last_lines(tmp_path: Path) -> None:
    """Only the requested number of trailing log lines is returned."""
    log_path = tmp_path / "run.log"
    log_path.write_text("one\ntwo\nthree\n", encoding="utf-8")

    assert read_log_tail(log_path, max_lines=2) == "two\nthree"


def test_start_preanalyze_process_includes_explicit_paths_and_config(tmp_path: Path) -> None:
    """Background pre-analysis should pass explicit paths and paths config to the CLI."""
    repo = tmp_path / "repo"
    repo.mkdir()
    raw_dir = tmp_path / "raw"
    reviews = tmp_path / "reviews"
    wiki = tmp_path / "wiki"
    log_dir = tmp_path / "logs"
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text("[paths]\n", encoding="utf-8")

    with patch("src.dashboard.preanalyze_ui.subprocess.Popen") as mock_popen:
        log_path = start_preanalyze_process(
            repo_root=repo,
            raw_dir=raw_dir,
            reviews_root=reviews,
            wiki_root=wiki,
            model="test-model",
            prompt_version="v1",
            limit=5,
            log_dir=log_dir,
            paths_config=config_path,
        )

    command = mock_popen.call_args.args[0]
    assert "--raw-dir" in command
    assert str(raw_dir) in command
    assert "--reviews-dir" in command
    assert str(reviews) in command
    assert "--wiki-root" in command
    assert str(wiki) in command
    assert "--paths-config" in command
    assert str(config_path) in command
    assert log_path.parent == log_dir
