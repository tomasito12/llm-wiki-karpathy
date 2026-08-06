"""Tests for management web pipeline operations."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from src.management_web.ops import (
    OperationConflictError,
    OperationValidationError,
    OpsRunManager,
    build_operation_command,
    format_ops_status_summary,
    get_operation_definition,
    list_operation_definitions,
    normalize_operation_parameters,
    recommendation_operation_id,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def _paths(tmp_path: Path) -> WikiPaths:
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    paths.reviews_dir.mkdir(parents=True)
    return paths


def test_list_operation_definitions_returns_allowlisted_mvp_operations() -> None:
    """The registry should expose only the MVP cockpit operations."""
    operation_ids = {operation.id for operation in list_operation_definitions()}

    assert operation_ids == {
        "ingest_preanalyze",
        "readwise_sync",
        "wiki_lint",
        "wiki_render_dry_run",
        "wiki_render",
        "synthesis_select",
        "synthesis_batch_dry_run",
        "synthesis_batch",
    }


def test_ingestion_operation_definitions_are_bounded_and_confirmed() -> None:
    """Ingestion operations should expose safe defaults and require confirmation."""
    readwise_sync = get_operation_definition("readwise_sync")
    preanalyze = get_operation_definition("ingest_preanalyze")

    assert readwise_sync.writes is True
    assert readwise_sync.llm_calls is False
    assert readwise_sync.requires_confirmation is True
    assert readwise_sync.parameters == ()
    assert preanalyze.writes is True
    assert preanalyze.llm_calls is True
    assert preanalyze.requires_confirmation is True
    assert normalize_operation_parameters(preanalyze, {}) == {
        "limit": 10,
        "between_articles": 300.0,
    }


def test_get_operation_definition_rejects_unknown_id() -> None:
    """Unknown operation ids should fail validation."""
    with pytest.raises(OperationValidationError, match="Unknown operation_id"):
        get_operation_definition("not_allowed")


def test_normalize_operation_parameters_applies_defaults() -> None:
    """Missing parameters should receive operation defaults."""
    operation = get_operation_definition("synthesis_select")

    normalized = normalize_operation_parameters(operation, {})

    assert normalized == {"limit": 20}


def test_normalize_operation_parameters_rejects_unknown_keys() -> None:
    """Unexpected parameter names should be rejected."""
    operation = get_operation_definition("wiki_lint")

    with pytest.raises(OperationValidationError, match="Unknown parameters"):
        normalize_operation_parameters(operation, {"limit": 5})


def test_normalize_operation_parameters_rejects_invalid_integer() -> None:
    """Integer parameters must stay within the configured bounds."""
    operation = get_operation_definition("synthesis_batch_dry_run")

    with pytest.raises(OperationValidationError, match="must be between 1 and 100"):
        normalize_operation_parameters(operation, {"limit": 0})


def test_build_operation_command_includes_paths_config(tmp_path: Path) -> None:
    """Subprocess commands should include the configured paths file when present."""
    paths = _paths(tmp_path)
    paths_config = tmp_path / "config" / "wiki_paths.toml"
    paths_config.parent.mkdir(parents=True)
    paths_config.write_text("[paths]\n", encoding="utf-8")

    _, _, command = build_operation_command(
        paths,
        paths_config,
        "wiki_render_dry_run",
        {},
    )

    assert command[1:3] == ["-m", "src.wiki_render"]
    assert "--paths-config" in command
    assert "--dry-run" in command


def test_build_operation_command_for_synthesis_batch(tmp_path: Path) -> None:
    """Real synthesis batch commands should include confirmation flags and limits."""
    paths = _paths(tmp_path)

    _, normalized, command = build_operation_command(
        paths,
        None,
        "synthesis_batch",
        {"limit": 3, "between_calls": 120, "continue_on_error": True},
    )

    assert normalized == {"limit": 3, "between_calls": 120.0, "continue_on_error": True}
    assert "src.wiki_synthesis.batch_cli" in command
    assert "--yes" in command
    assert "--limit" in command
    assert "--between-calls" in command
    assert "--continue-on-error" in command


def test_build_operation_command_for_readwise_sync_keeps_automatic_dedupe(
    tmp_path: Path,
) -> None:
    """Readwise sync should use the normal CLI path without disabling dedupe."""
    paths = _paths(tmp_path)

    _, normalized, command = build_operation_command(paths, None, "readwise_sync", {})

    assert normalized == {}
    assert command[1:3] == ["-m", "src.readwise"]
    assert "--no-dedupe" not in command


def test_build_operation_command_for_ingest_preanalyze(tmp_path: Path) -> None:
    """Pre-analysis should pass the selected limit and between-article pause."""
    paths = _paths(tmp_path)

    _, normalized, command = build_operation_command(
        paths,
        None,
        "ingest_preanalyze",
        {"limit": 7, "between_articles": 450},
    )

    assert normalized == {"limit": 7, "between_articles": 450.0}
    assert command[1:3] == ["-m", "src.ingest_batch.cli"]
    assert command[command.index("--limit") + 1] == "7"
    assert command[command.index("--between-articles") + 1] == "450.0"


def test_ingest_preanalyze_rejects_pause_above_one_hour() -> None:
    """The management UI should not allow an accidental unbounded pause."""
    operation = get_operation_definition("ingest_preanalyze")

    with pytest.raises(OperationValidationError, match="between 0 and 3600"):
        normalize_operation_parameters(operation, {"between_articles": 3601})


def test_ops_run_manager_starts_read_only_operation_without_confirmation(tmp_path: Path) -> None:
    """Read-only operations should start immediately without confirmation."""
    paths = _paths(tmp_path)
    manager = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (0, "ok", ""),
    )

    report = manager.start_run("wiki_lint")

    assert report["status"] == "queued"
    assert report["operation_id"] == "wiki_lint"
    finished = _wait_for_terminal_run(manager, str(report["run_id"]))
    assert finished["status"] == "succeeded"
    assert finished["exit_code"] == 0
    assert finished["stdout_tail"] == "ok"
    assert finished["report_path"] is not None


def test_ops_run_manager_requires_confirmation_for_write_operation(tmp_path: Path) -> None:
    """Write operations should be blocked until explicitly confirmed."""
    paths = _paths(tmp_path)
    manager = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (0, "", ""),
    )

    with pytest.raises(OperationConflictError, match="requires explicit confirmation"):
        manager.start_run("wiki_render")


def test_ops_run_manager_requires_confirmation_for_llm_operation(tmp_path: Path) -> None:
    """LLM-capable operations should also require confirmation."""
    paths = _paths(tmp_path)
    manager = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (0, "", ""),
    )

    with pytest.raises(OperationConflictError, match="requires explicit confirmation"):
        manager.start_run("synthesis_batch")


def test_ops_run_manager_allows_confirmed_write_operation(tmp_path: Path) -> None:
    """Confirmed write operations should start and persist a run report."""
    paths = _paths(tmp_path)
    manager = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (0, "rendered", ""),
    )

    report = manager.start_run("wiki_render", confirmed=True)
    finished = _wait_for_terminal_run(manager, str(report["run_id"]))

    assert finished["status"] == "succeeded"
    assert finished["writes"] is True
    report_path = Path(str(finished["report_path"]))
    assert report_path.is_file()
    assert json.loads(report_path.read_text(encoding="utf-8"))["stdout_tail"] == "rendered"


def test_ops_run_manager_records_failed_run(tmp_path: Path) -> None:
    """Failed runs should record a non-zero exit code and stderr tail."""
    paths = _paths(tmp_path)
    manager = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (2, "", "boom"),
    )

    report = manager.start_run("wiki_lint")
    finished = _wait_for_terminal_run(manager, str(report["run_id"]))

    assert finished["status"] == "failed"
    assert finished["exit_code"] == 2
    assert finished["stderr_tail"] == "boom"


def test_ops_run_manager_allows_only_one_active_run(tmp_path: Path) -> None:
    """MVP concurrency should reject a second run while one is active."""
    paths = _paths(tmp_path)
    started = False

    def slow_runner(_command: list[str], _cwd: Path) -> tuple[int, str, str]:
        nonlocal started
        started = True
        time.sleep(0.2)
        return 0, "", ""

    manager = OpsRunManager(paths=paths, command_runner=slow_runner)
    first = manager.start_run("wiki_lint")
    _wait_until(lambda: started)

    with pytest.raises(OperationConflictError, match="already running"):
        manager.start_run("wiki_lint")

    _wait_for_terminal_run(manager, str(first["run_id"]))


def test_ops_run_manager_lists_recent_runs_newest_first(tmp_path: Path) -> None:
    """Recent runs should be returned newest first."""
    paths = _paths(tmp_path)
    manager = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (0, "", ""),
    )
    first = manager.start_run("wiki_lint")
    _wait_for_terminal_run(manager, str(first["run_id"]))
    time.sleep(1.1)
    second = manager.start_run("wiki_lint")
    _wait_for_terminal_run(manager, str(second["run_id"]))

    runs = manager.list_runs(limit=10)

    assert [run["run_id"] for run in runs[:2]] == [second["run_id"], first["run_id"]]


def test_format_ops_status_summary_is_compact() -> None:
    """Status summary should expose the key pipeline facts in one line."""
    summary = format_ops_status_summary(
        {
            "sources": {"paired": 12},
            "reviews": {"finished": 8},
            "synthesis": {"stale": 3},
            "render": {"manifest_exists": True, "graph_exists": True},
        }
    )

    assert summary == "12 sources · 8 reviewed · render current · 3 stale syntheses"


def test_recommendation_operation_id_maps_known_phrases() -> None:
    """Known recommendation phrases should map to cockpit operation ids."""
    assert (
        recommendation_operation_id("Refresh stale synthesis entries before final render.")
        == "synthesis_batch_dry_run"
    )
    assert (
        recommendation_operation_id("Run wiki-render --dry-run to refresh.")
        == "wiki_render_dry_run"
    )
    assert (
        recommendation_operation_id("Run hatch run wiki-render to create graph state.")
        == "wiki_render"
    )


def _wait_until(predicate: Callable[[], bool], timeout_seconds: float = 2.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("Condition was not met before timeout.")


def _wait_for_terminal_run(manager: OpsRunManager, run_id: str) -> dict[str, object]:
    terminal = {"succeeded", "failed", "cancelled"}

    def finished() -> bool:
        report = manager.get_run(run_id)
        return str(report["status"]) in terminal

    _wait_until(finished)
    return manager.get_run(run_id)
