"""Tests for temporary dashboard operations controls."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.dashboard.ops_ui import (
    DashboardCommandResult,
    _output_interpretation,
    command_text,
    render_command_result,
    run_dashboard_command,
)


def test_command_text_joins_command_parts() -> None:
    """Command text should be readable in the dashboard output."""
    assert command_text(["python", "-m", "src.wiki_render", "--dry-run"]) == (
        "python -m src.wiki_render --dry-run"
    )


def test_run_dashboard_command_captures_success(tmp_path: Path) -> None:
    """The command runner should capture stdout and return code."""
    result = run_dashboard_command(
        label="Version",
        command=[sys.executable, "-c", "print('ok')"],
        cwd=tmp_path,
    )

    assert result.ok
    assert result.stdout.strip() == "ok"
    assert result.stderr == ""


def test_run_dashboard_command_handles_timeout(tmp_path: Path) -> None:
    """Timeouts should become a normal command result for display."""
    result = run_dashboard_command(
        label="Slow command",
        command=[sys.executable, "-c", "import time; time.sleep(2)"],
        cwd=tmp_path,
        timeout_seconds=1,
    )

    assert result.returncode == 124
    assert "Timed out" in result.stderr


def test_render_command_result_outputs_stdout() -> None:
    """Rendering a successful command should show success and output."""
    mock_st = MagicMock()
    result = DashboardCommandResult(
        label="Ops status",
        command=["python", "-m", "src.wiki_ops.status_cli"],
        returncode=0,
        stdout="all good\n",
        stderr="",
    )

    render_command_result(mock_st, result)

    mock_st.success.assert_called_once()
    mock_st.code.assert_called_once_with("all good", language="text")


def test_render_command_result_outputs_error() -> None:
    """Rendering a failed command should show stderr."""
    mock_st = MagicMock()
    result = DashboardCommandResult(
        label="Render",
        command=["python", "-m", "src.wiki_render"],
        returncode=2,
        stdout="",
        stderr="boom\n",
    )

    render_command_result(mock_st, result)

    mock_st.error.assert_called_once()
    mock_st.code.assert_called_once_with("boom", language="text")


def test_output_interpretation_returns_hint_for_known_labels() -> None:
    """Known command labels should get a plain-language output hint."""
    assert _output_interpretation("Show synthesis plan") is not None
    assert _output_interpretation("Unknown label") is None


def test_render_command_result_shows_interpretation_for_known_label() -> None:
    """Rendering should include an info hint when the label is recognized."""
    mock_st = MagicMock()
    result = DashboardCommandResult(
        label="Batch dry-run",
        command=["python", "-m", "src.wiki_synthesis.batch_cli", "--dry-run"],
        returncode=0,
        stdout="planned=3\n",
        stderr="",
    )

    render_command_result(mock_st, result)

    mock_st.info.assert_called_once()


def test_render_button_command_uses_current_interpreter(tmp_path: Path) -> None:
    """The operations UI should run Python modules directly, not shell out through Hatch."""
    from src.dashboard.ops_ui import _python_command, _render_button_command

    mock_st = MagicMock()
    mock_st.button.return_value = True
    mock_st.spinner.return_value.__enter__.return_value = None
    mock_st.spinner.return_value.__exit__.return_value = False
    command = _python_command("src.wiki_ops.status_cli")

    with patch("src.dashboard.ops_ui.run_dashboard_command") as mock_run:
        mock_run.return_value = DashboardCommandResult(
            label="Ops status",
            command=command,
            returncode=0,
            stdout="ok",
            stderr="",
        )
        _render_button_command(
            mock_st,
            label="Ops status",
            key="ops_status_button",
            command=command,
            repo_root=tmp_path,
        )

    mock_run.assert_called_once()
    assert command[:3] == [sys.executable, "-m", "src.wiki_ops.status_cli"]
    mock_st.rerun.assert_called_once()
