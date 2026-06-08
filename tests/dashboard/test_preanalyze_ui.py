"""Tests for pre-analysis dashboard helpers."""

from __future__ import annotations

from pathlib import Path

from src.dashboard.preanalyze_ui import latest_preanalyze_log, read_log_tail


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
