"""Tests for the guided Update Wiki workflow."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from src.management_web.ops import ManagementRunCoordinator, OperationConflictError, OpsRunManager
from src.management_web.update_wiki_workflow import (
    UpdateWikiWorkflowManager,
    WorkflowValidationError,
    assess_update_wiki_availability,
    execute_synthesis_batch,
    validate_synthesis_batch_size,
    validate_synthesis_between_calls_seconds,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def _paths(tmp_path: Path) -> WikiPaths:
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    paths.reviews_dir.mkdir(parents=True)
    return paths


def _selection_stdout(total: int = 3, shown: int = 2) -> str:
    return json.dumps(
        {
            "total_changed": total,
            "shown": shown,
            "entries": [
                {
                    "title": "Context Engineering",
                    "category": "topic",
                    "source_count": 14,
                    "state": "stale",
                    "score": 140,
                }
            ],
        }
    )


def _render_dry_run_stdout(*, would_write: int = 23) -> str:
    return "\n".join(
        [
            "Wiki Render Summary (dry-run — no files changed)",
            "- output files: 1070",
            f"- would write: {would_write}",
            "- unchanged: 1047",
            "- would prune: 0",
        ]
    )


def _render_write_stdout() -> str:
    return "\n".join(
        [
            "Wiki Render Summary (write)",
            "- written: 23",
            "- unchanged: 1047",
            "- pruned: 0",
        ]
    )


def _lint_stdout() -> str:
    return "\n".join(
        [
            "Vault hygiene",
            "- safe delete candidates: 0",
            "- manual review items: 0",
            "- exact duplicate groups: 0",
        ]
    )


def _command_router(
    responses: dict[str, tuple[int, str, str]],
) -> Callable[[list[str], Path], tuple[int, str, str]]:
    """Return a command runner keyed by module name fragments."""

    def _runner(command: list[str], _cwd: Path) -> tuple[int, str, str]:
        joined = " ".join(command)
        for key, payload in responses.items():
            if key in joined:
                return payload
        return 0, "", ""

    return _runner


def _wait_until(predicate: Callable[[], bool], timeout_seconds: float = 3.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("Condition was not met before timeout.")


def _batch_runner(
    exit_code: int = 0,
    payload: dict | None = None,
) -> Callable[..., tuple[int, dict, str]]:
    """Return a synthesis batch runner stub for workflow tests."""

    def _runner(
        _paths: WikiPaths,
        _limit: int,
        _between_calls: float,
        progress_fn: Callable[[str], None] | None,
    ) -> tuple[int, dict, str]:
        if progress_fn is not None:
            progress_fn("processing topic:one index=1 total=2")
        batch_payload = payload or {
            "selected": 2,
            "attempted": 2,
            "written": 2,
            "failed": 0,
            "dry_run": False,
        }
        return exit_code, batch_payload, json.dumps(batch_payload)

    return _runner


def test_validate_synthesis_batch_size_rejects_out_of_range() -> None:
    """Batch size must stay within the configured workflow bounds."""
    with pytest.raises(WorkflowValidationError):
        validate_synthesis_batch_size(0)
    with pytest.raises(WorkflowValidationError):
        validate_synthesis_batch_size(101)
    assert validate_synthesis_batch_size(5) == 5


def test_validate_synthesis_between_calls_seconds_rejects_out_of_range() -> None:
    """Pause between syntheses must stay within the configured workflow bounds."""
    with pytest.raises(WorkflowValidationError):
        validate_synthesis_between_calls_seconds(-1)
    with pytest.raises(WorkflowValidationError):
        validate_synthesis_between_calls_seconds(3601)
    assert validate_synthesis_between_calls_seconds(300) == 300.0
    assert validate_synthesis_between_calls_seconds(0) == 0.0


def test_execute_synthesis_batch_loads_dotenv_then_reports_missing_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """In-process synthesis loads repo ``.env`` before requiring OPENAI_API_KEY."""
    load_calls: list[bool] = []

    def _fake_load_repo_dotenv(*, override: bool = False) -> Path:
        del override
        load_calls.append(True)
        return tmp_path

    monkeypatch.setattr(
        "src.ingest_review.paths.load_repo_dotenv",
        _fake_load_repo_dotenv,
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    exit_code, payload, message = execute_synthesis_batch(
        _paths(tmp_path),
        limit=1,
        between_calls=0.0,
    )

    assert load_calls == [True]
    assert exit_code == 2
    assert payload == {}
    assert "OPENAI_API_KEY is not set" in message


def test_execute_synthesis_batch_uses_key_loaded_from_dotenv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """After dotenv load, a present OPENAI_API_KEY allows synthesis to proceed."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def _fake_load_repo_dotenv(*, override: bool = False) -> Path:
        del override
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-from-dotenv")
        return tmp_path

    monkeypatch.setattr(
        "src.ingest_review.paths.load_repo_dotenv",
        _fake_load_repo_dotenv,
    )
    monkeypatch.setattr(
        "src.wiki_synthesis.planner.load_graph_export",
        lambda _path: {"pages": []},
    )

    captured: dict[str, object] = {}

    def _fake_run_synthesis_batch(*_args: object, **kwargs: object) -> object:
        captured.update(kwargs)

        class _Report:
            failed = 0

            def to_dict(self) -> dict[str, int]:
                return {"selected": 0, "attempted": 0, "written": 0, "failed": 0}

        return _Report()

    monkeypatch.setattr(
        "src.wiki_synthesis.batch.run_synthesis_batch",
        _fake_run_synthesis_batch,
    )
    monkeypatch.setattr(
        "src.wiki_synthesis.openai_provider.OpenAISynthesisProvider",
        lambda: object(),
    )
    monkeypatch.setattr(
        "src.ingest_review.review_scope.finished_source_ids",
        lambda _reviews_dir: set(),
    )

    exit_code, payload, _stdout = execute_synthesis_batch(
        _paths(tmp_path),
        limit=2,
        between_calls=1.5,
    )

    assert exit_code == 0
    assert payload["selected"] == 0
    assert captured["limit"] == 2
    assert captured["between_calls"] == 1.5
    assert captured["dry_run"] is False


def test_start_persists_between_calls_parameter(tmp_path: Path) -> None:
    """Start request should store the configured pause between syntheses."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router({"select_cli": (0, _selection_stdout(), "")}),
    )

    report = manager.start(synthesis_batch_size=3, synthesis_between_calls_seconds=450)

    assert report["parameters"]["synthesis_batch_size"] == 3
    assert report["parameters"]["synthesis_between_calls_seconds"] == 450.0


def test_assess_update_wiki_availability_marks_stale_work_as_available() -> None:
    """Stale synthesis and render drift should make Update Wiki available."""
    availability = assess_update_wiki_availability(
        {
            "synthesis": {"stale": 42, "errors": 0, "plan": {"new": 1, "stale": 41}},
            "render": {"manifest_exists": True, "graph_exists": True},
            "pipeline": {"render_stale": True},
            "artifacts": {"uncommitted_durable_files": 2},
        }
    )

    assert availability.update_available is True
    assert availability.headline == "Wiki update available"
    assert availability.can_start is True


def test_workflow_pauses_before_synthesis_batch(tmp_path: Path) -> None:
    """Workflow should wait for confirmation before LLM synthesis."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {
                "select_cli": (0, _selection_stdout(), ""),
            }
        ),
    )

    report = manager.start(synthesis_batch_size=2)

    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    waiting = manager.get_run(str(report["run_id"]))
    assert waiting["pending_confirmation"]["id"] == "synthesis_batch"
    assert "Run 2 synthesis updates now?" in waiting["pending_confirmation"]["title"]
    synthesis_step = next(step for step in waiting["steps"] if step["id"] == "synthesis_batch")
    assert synthesis_step["status"] == "waiting"


def test_auto_confirm_skips_synthesis_confirmation_gate(tmp_path: Path) -> None:
    """Auto-confirm should continue past synthesis without waiting for approval."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {
                "select_cli": (0, _selection_stdout(), ""),
                "--dry-run": (0, _render_dry_run_stdout(would_write=0), ""),
                "wiki_lint": (0, _lint_stdout(), ""),
            }
        ),
        synthesis_batch_runner=_batch_runner(),
    )
    report = manager.start(synthesis_batch_size=2, auto_confirm=True)
    _wait_until(
        lambda: (
            manager.get_run(str(report["run_id"]))["status"] in {"succeeded", "failed", "stopped"}
        )
    )
    finished = manager.get_run(str(report["run_id"]))
    assert finished["status"] == "succeeded"
    synthesis_step = next(step for step in finished["steps"] if step["id"] == "synthesis_batch")
    assert synthesis_step["status"] == "succeeded"
    assert finished.get("pending_confirmation") is None


def test_active_run_returns_in_progress_workflow(tmp_path: Path) -> None:
    """Active run lookup should expose a running workflow report."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router({"select_cli": (0, _selection_stdout(), "")}),
    )
    report = manager.start(synthesis_batch_size=2)
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )

    active = manager.active_run()

    assert active is not None
    assert active["run_id"] == report["run_id"]
    assert active["status"] == "waiting_for_confirmation"


def test_workflow_rejects_wrong_confirmation_id(tmp_path: Path) -> None:
    """Confirmation must match the pending workflow gate."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router({"select_cli": (0, _selection_stdout(), "")}),
    )
    report = manager.start(synthesis_batch_size=2)
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )

    with pytest.raises(WorkflowValidationError):
        manager.confirm(str(report["run_id"]), "render_write")


def test_skip_synthesis_continues_to_render_dry_run(tmp_path: Path) -> None:
    """Skipping synthesis should continue with render preview."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {
                "select_cli": (0, _selection_stdout(), ""),
                "--dry-run": (0, _render_dry_run_stdout(would_write=0), ""),
                "wiki_lint": (0, _lint_stdout(), ""),
            }
        ),
    )
    report = manager.start(synthesis_batch_size=2)
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    manager.skip(str(report["run_id"]), "synthesis_batch")
    _wait_until(
        lambda: (
            manager.get_run(str(report["run_id"]))["status"] in {"succeeded", "failed", "stopped"}
        )
    )
    finished = manager.get_run(str(report["run_id"]))
    synthesis_step = next(step for step in finished["steps"] if step["id"] == "synthesis_batch")
    assert synthesis_step["status"] == "skipped"
    assert any(
        step["id"] == "render_dry_run" and step["status"] == "succeeded"
        for step in finished["steps"]
    )


def test_render_write_pauses_when_dry_run_has_changes(tmp_path: Path) -> None:
    """Render write should wait for confirmation when dry-run reports changes."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {
                "select_cli": (0, json.dumps({"total_changed": 0, "shown": 0, "entries": []}), ""),
                "--dry-run": (0, _render_dry_run_stdout(would_write=23), ""),
            }
        ),
    )
    report = manager.start()
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    waiting = manager.get_run(str(report["run_id"]))
    assert waiting["pending_confirmation"]["id"] == "render_write"


def test_confirmed_workflow_runs_lint_after_render_write(tmp_path: Path) -> None:
    """Lint should run automatically after a confirmed render write."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {
                "select_cli": (0, json.dumps({"total_changed": 0, "shown": 0, "entries": []}), ""),
                "--dry-run": (0, _render_dry_run_stdout(would_write=23), ""),
                "wiki_render": (0, _render_write_stdout(), ""),
                "wiki_lint": (0, _lint_stdout(), ""),
            }
        ),
    )
    report = manager.start()
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    manager.confirm(str(report["run_id"]), "render_write")
    _wait_until(lambda: manager.get_run(str(report["run_id"]))["status"] == "succeeded")
    finished = manager.get_run(str(report["run_id"]))
    assert any(
        step["id"] == "wiki_lint" and step["status"] == "succeeded" for step in finished["steps"]
    )


def test_synthesis_batch_failure_stops_before_render(tmp_path: Path) -> None:
    """A failed synthesis batch must not proceed to render."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {
                "select_cli": (0, _selection_stdout(), ""),
            }
        ),
        synthesis_batch_runner=_batch_runner(exit_code=1),
    )
    report = manager.start(synthesis_batch_size=2)
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    manager.confirm(str(report["run_id"]), "synthesis_batch")
    _wait_until(lambda: manager.get_run(str(report["run_id"]))["status"] == "failed")
    finished = manager.get_run(str(report["run_id"]))
    render_step = next(step for step in finished["steps"] if step["id"] == "render_dry_run")
    assert render_step["status"] == "pending"


def test_synthesis_batch_updates_progress_while_running(tmp_path: Path) -> None:
    """Synthesis batch should publish live progress for polling clients."""
    progress_seen = {"value": False}

    def _progress_batch_runner(
        _paths: WikiPaths,
        _limit: int,
        _between_calls: float,
        progress_fn: Callable[[str], None] | None,
    ) -> tuple[int, dict, str]:
        if progress_fn is not None:
            progress_fn("processing topic:one index=1 total=2")
            progress_fn("waiting topic:one index=1 total=2 seconds=300 remaining=299")
        progress_seen["value"] = True
        payload = {
            "selected": 2,
            "attempted": 2,
            "written": 2,
            "failed": 0,
            "dry_run": False,
        }
        return 0, payload, json.dumps(payload)

    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router({"select_cli": (0, _selection_stdout(), "")}),
        synthesis_batch_runner=_progress_batch_runner,
    )
    report = manager.start(synthesis_batch_size=2, synthesis_between_calls_seconds=300)
    _wait_until(
        lambda: manager.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    manager.confirm(str(report["run_id"]), "synthesis_batch")
    _wait_until(lambda: progress_seen["value"])
    _wait_until(lambda: manager.get_run(str(report["run_id"]))["status"] in {"succeeded", "failed"})
    finished = manager.get_run(str(report["run_id"]))
    synthesis_step = next(step for step in finished["steps"] if step["id"] == "synthesis_batch")
    assert synthesis_step["status"] == "succeeded"
    assert synthesis_step["progress_lines"]
    assert "waiting topic:one" in synthesis_step["progress_lines"][-1]


def test_only_one_workflow_or_operation_may_run_at_a_time(tmp_path: Path) -> None:
    """Shared coordinator should block overlapping workflow and operation runs."""
    paths = _paths(tmp_path)
    coordinator = ManagementRunCoordinator()
    workflow = UpdateWikiWorkflowManager(
        paths=paths,
        coordinator=coordinator,
        command_runner=_command_router({"select_cli": (0, _selection_stdout(), "")}),
    )
    operations = OpsRunManager(paths=paths, coordinator=coordinator)

    report = workflow.start()
    _wait_until(
        lambda: workflow.get_run(str(report["run_id"]))["status"] == "waiting_for_confirmation"
    )
    with pytest.raises(OperationConflictError, match="already running"):
        operations.start_run("wiki_lint")


def test_workflow_report_is_written_atomically(tmp_path: Path) -> None:
    """Workflow runs should persist one JSON report under management_runs."""
    coordinator = ManagementRunCoordinator()
    manager = UpdateWikiWorkflowManager(
        paths=_paths(tmp_path),
        coordinator=coordinator,
        command_runner=_command_router(
            {"select_cli": (0, json.dumps({"total_changed": 0, "shown": 0, "entries": []}), "")}
        ),
    )
    report = manager.start()
    _wait_until(
        lambda: (
            manager.get_run(str(report["run_id"]))["status"] in {"succeeded", "failed", "stopped"}
        )
    )
    finished = manager.get_run(str(report["run_id"]))
    report_path = Path(str(finished["report_path"]))
    assert report_path.is_file()
    assert json.loads(report_path.read_text(encoding="utf-8"))["workflow_id"] == "update_wiki"
