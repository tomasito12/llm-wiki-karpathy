"""Tests for dashboard Readwise sync helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.dashboard.readwise_sync_ui import (
    format_sync_summary,
    readwise_token_from_env,
    try_readwise_sync,
)
from src.readwise.sync import SyncResult


def test_readwise_token_from_env_prefers_readwise_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("READWISE_TOKEN", "  token-a  ")
    monkeypatch.setenv("READWISE_API_TOKEN", "token-b")
    assert readwise_token_from_env() == "token-a"


def test_readwise_token_from_env_falls_back_to_api_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("READWISE_TOKEN", raising=False)
    monkeypatch.setenv("READWISE_API_TOKEN", "token-b")
    assert readwise_token_from_env() == "token-b"


def test_readwise_token_from_env_returns_none_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("READWISE_TOKEN", raising=False)
    monkeypatch.delenv("READWISE_API_TOKEN", raising=False)
    assert readwise_token_from_env() is None


def test_format_sync_summary_basic() -> None:
    result = SyncResult(
        examined=5,
        exported=2,
        skipped=3,
        dry_run=False,
        incremental_filter_active=True,
        incremental_watermark="2026-01-01T00:00:00+00:00",
    )
    text = format_sync_summary(result)
    assert "examined **5**" in text
    assert "exported **2**" in text
    assert "skipped **3**" in text


def test_format_sync_summary_includes_watermark_hint_when_empty() -> None:
    result = SyncResult(
        examined=0,
        exported=0,
        skipped=0,
        dry_run=False,
        incremental_filter_active=True,
        incremental_watermark="2026-05-01T00:00:00+00:00",
    )
    text = format_sync_summary(result)
    assert "watermark" in text
    assert "2026-05-01T00:00:00+00:00" in text


def test_try_readwise_sync_returns_error_without_token(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("READWISE_TOKEN", raising=False)
    monkeypatch.delenv("READWISE_API_TOKEN", raising=False)
    result, error = try_readwise_sync(
        repo_root=tmp_path,
        output_dir=tmp_path / "raw" / "readwise",
    )
    assert result is None
    assert error is not None
    assert "READWISE_TOKEN" in error


def test_try_readwise_sync_calls_run_sync(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("READWISE_TOKEN", "test-token")
    expected = SyncResult(
        examined=1,
        exported=1,
        skipped=0,
        dry_run=False,
        incremental_filter_active=True,
        incremental_watermark=None,
    )
    with patch("src.dashboard.readwise_sync_ui.run_sync", return_value=expected) as mock_run:
        result, error = try_readwise_sync(
            repo_root=tmp_path,
            output_dir=tmp_path / "raw" / "readwise",
            prune_missing=True,
            reset_watermark=True,
        )
    assert error is None
    assert result == expected
    mock_run.assert_called_once_with(
        "test-token",
        index_path=tmp_path / "state" / "readwise_library.json",
        output_dir=tmp_path / "raw" / "readwise",
        repo_root=tmp_path,
        dry_run=False,
        prune_missing=True,
        reset_watermark=True,
    )


def test_render_readwise_sync_sidebar_queues_flash_on_success() -> None:
    from src.dashboard.readwise_sync_ui import render_readwise_sync_sidebar

    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.button.return_value = True
    mock_st.checkbox.side_effect = [False, False]
    expected = SyncResult(
        examined=2,
        exported=1,
        skipped=1,
        dry_run=False,
        incremental_filter_active=True,
        incremental_watermark=None,
    )
    with patch(
        "src.dashboard.readwise_sync_ui.try_readwise_sync",
        return_value=(expected, None),
    ):
        render_readwise_sync_sidebar(
            mock_st,
            repo_root=Path("/repo"),
            output_dir=Path("/repo/raw/readwise"),
        )
    assert "_readwise_sync_flash" in mock_st.session_state
    mock_st.rerun.assert_called_once()
