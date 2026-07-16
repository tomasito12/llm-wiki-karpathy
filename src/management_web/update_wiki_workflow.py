"""Guided Update Wiki workflow orchestration for the management web app."""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from src.management_web.ops import (
    CommandRunner,
    ManagementRunCoordinator,
    _default_command_runner,
    _duration_seconds,
    _run_id,
    _tail,
    _utc_now,
    _utc_timestamp,
    build_operation_command,
    collect_management_ops_status,
    management_runs_dir,
)
from src.management_web.workflow_parsers import (
    loads_json_object,
    parse_batch_progress_message,
    parse_render_summary_text,
    parse_synthesis_batch_json,
    parse_synthesis_select_json,
    parse_wiki_lint_output,
    render_changes_pending,
)
from src.pipeline.atomic import atomic_write_json
from src.wiki_paths.config import WikiPaths

WorkflowRunStatus = Literal["running", "waiting_for_confirmation", "succeeded", "failed", "stopped"]
WorkflowStepStatus = Literal[
    "pending",
    "running",
    "succeeded",
    "failed",
    "skipped",
    "waiting",
]
ConfirmationAction = Literal["confirm", "skip"]

UPDATE_WIKI_WORKFLOW_ID = "update_wiki"
DEFAULT_SYNTHESIS_BATCH_SIZE = 5
DEFAULT_SYNTHESIS_BETWEEN_CALLS_SECONDS = 300.0
_MIN_BATCH_SIZE = 1
_MAX_BATCH_SIZE = 100
_MIN_BETWEEN_CALLS_SECONDS = 0.0
_MAX_BETWEEN_CALLS_SECONDS = 3600.0

SynthesisBatchRunner = Callable[
    [WikiPaths, int, float, Callable[[str], None] | None],
    tuple[int, dict[str, Any], str],
]

STEP_DEFINITIONS: tuple[tuple[str, str], ...] = (
    ("status", "Status check"),
    ("blocker_check", "Blocker check"),
    ("synthesis_planning", "Candidate planning"),
    ("synthesis_batch", "Synthesis batch"),
    ("render_dry_run", "Render preview"),
    ("render_write", "Render write"),
    ("wiki_lint", "Health check"),
    ("final_status", "Final status"),
)


class WorkflowValidationError(ValueError):
    """Raised when workflow parameters or confirmation requests are invalid."""


class WorkflowConflictError(RuntimeError):
    """Raised when workflow concurrency rules block a run."""


@dataclass(frozen=True)
class UpdateWikiAvailability:
    """Summary of whether an Update Wiki run is useful or blocked."""

    update_available: bool
    headline: str
    detail_line: str
    hints: tuple[str, ...]
    blocking_errors: tuple[str, ...]
    can_start: bool


def validate_synthesis_batch_size(value: int) -> int:
    """Validate the configured synthesis batch size for Update Wiki."""
    if value < _MIN_BATCH_SIZE or value > _MAX_BATCH_SIZE:
        raise WorkflowValidationError(
            f"synthesis_batch_size must be between {_MIN_BATCH_SIZE} and {_MAX_BATCH_SIZE}."
        )
    return value


def validate_synthesis_between_calls_seconds(value: float) -> float:
    """Validate the pause between synthesis API calls for Update Wiki."""
    if value < _MIN_BETWEEN_CALLS_SECONDS or value > _MAX_BETWEEN_CALLS_SECONDS:
        raise WorkflowValidationError(
            "synthesis_between_calls_seconds must be between "
            f"{int(_MIN_BETWEEN_CALLS_SECONDS)} and {int(_MAX_BETWEEN_CALLS_SECONDS)}."
        )
    return float(value)


def execute_synthesis_batch(
    paths: WikiPaths,
    limit: int,
    between_calls: float,
    progress_fn: Callable[[str], None] | None = None,
) -> tuple[int, dict[str, Any], str]:
    """Run one real synthesis batch in-process and return exit code plus JSON payload."""
    from src.ingest_review.review_scope import finished_source_ids
    from src.wiki_synthesis.batch import run_synthesis_batch
    from src.wiki_synthesis.openai_provider import OpenAISynthesisProvider
    from src.wiki_synthesis.planner import load_graph_export

    if not os.environ.get("OPENAI_API_KEY"):
        return 2, {}, "OPENAI_API_KEY is not set. Add it to .env or export it."

    graph = load_graph_export(paths.graph_path)
    model = os.environ.get(
        "WIKI_SYNTHESIS_OPENAI_MODEL",
        os.environ.get("INGEST_OPENAI_MODEL", "gpt-4o-mini"),
    )
    progress_lines: list[str] = []

    def _progress(message: str) -> None:
        progress_lines.append(message)
        if progress_fn is not None:
            progress_fn(message)

    batch_report = run_synthesis_batch(
        graph,
        cache_dir=paths.synthesis_dir,
        preview_dir=paths.preview_dir,
        report_dir=paths.run_dir,
        provider_factory=lambda: OpenAISynthesisProvider(),
        model=model,
        limit=limit,
        dry_run=False,
        between_calls=between_calls,
        continue_on_error=False,
        progress_fn=_progress,
        finished_source_ids=finished_source_ids(paths.reviews_dir),
    )
    payload = batch_report.to_dict()
    payload["progress"] = progress_lines
    stdout = json.dumps(payload, indent=2, sort_keys=True)
    exit_code = 1 if batch_report.failed else 0
    return exit_code, payload, stdout


def assess_update_wiki_availability(status: dict[str, Any]) -> UpdateWikiAvailability:
    """Return whether Update Wiki should be offered and any blockers."""
    synthesis = status.get("synthesis") or {}
    render = status.get("render") or {}
    pipeline = status.get("pipeline") or {}
    artifacts = status.get("artifacts") or {}
    source_access = status.get("source_access") or {}
    vault_hygiene = status.get("vault_hygiene") or {}

    blocking_errors: list[str] = []
    hints: list[str] = []
    stale = int(synthesis.get("stale") or 0)
    errors = int(synthesis.get("errors") or 0)
    plan = synthesis.get("plan") or {}
    changed_candidates = int(plan.get("new") or 0) + int(plan.get("stale") or 0)
    render_ready = bool(render.get("manifest_exists")) and bool(render.get("graph_exists"))
    render_stale = bool(pipeline.get("render_stale"))
    uncommitted_durable = int(artifacts.get("uncommitted_durable_files") or 0)

    if errors:
        blocking_errors.append("Fix synthesis cache errors before updating the wiki.")
    if _source_access_is_blocking(source_access):
        blocking_errors.append("Fix source text coverage and source access gaps before updating.")

    if stale:
        hints.append(f"{stale} stale syntheses are ready for the next update.")
    if changed_candidates:
        hints.append(f"{changed_candidates} changed synthesis candidates are available.")
    if render_stale or not render_ready:
        hints.append("Render snapshot needs refresh.")
    if uncommitted_durable:
        hints.append("Durable files are uncommitted.")
    if vault_hygiene.get("safe_delete_candidates"):
        hints.append("Vault hygiene items need review.")
    if vault_hygiene.get("duplicate_groups"):
        hints.append("Duplicate vault pages need review.")

    update_available = bool(
        blocking_errors
        or stale
        or changed_candidates
        or render_stale
        or not render_ready
        or uncommitted_durable
    )
    if blocking_errors:
        headline = "Update blocked"
        detail_line = " · ".join(blocking_errors[:2])
        can_start = False
    elif update_available:
        headline = "Wiki update available"
        detail_bits = []
        if stale:
            detail_bits.append(f"{stale} stale syntheses")
        if render_stale or not render_ready:
            detail_bits.append("render needs refresh")
        if errors:
            detail_bits.append(f"{errors} blocking errors")
        else:
            detail_bits.append("no blocking errors")
        detail_line = " · ".join(detail_bits) if detail_bits else "Work is available"
        can_start = True
    else:
        headline = "Wiki is up to date"
        detail_line = "No render needed · synthesis cache fresh · lint clean"
        can_start = True
    return UpdateWikiAvailability(
        update_available=update_available and not blocking_errors,
        headline=headline,
        detail_line=detail_line,
        hints=tuple(hints),
        blocking_errors=tuple(blocking_errors),
        can_start=can_start,
    )


def availability_to_dict(availability: UpdateWikiAvailability) -> dict[str, Any]:
    """Return a JSON-serializable availability payload."""
    return {
        "update_available": availability.update_available,
        "headline": availability.headline,
        "detail_line": availability.detail_line,
        "hints": list(availability.hints),
        "blocking_errors": list(availability.blocking_errors),
        "can_start": availability.can_start,
    }


class UpdateWikiWorkflowManager:
    """Orchestrate the guided Update Wiki workflow."""

    def __init__(
        self,
        *,
        paths: WikiPaths,
        paths_config: Path | None = None,
        command_runner: CommandRunner | None = None,
        coordinator: ManagementRunCoordinator | None = None,
        synthesis_batch_runner: SynthesisBatchRunner | None = None,
    ) -> None:
        self._paths = paths
        self._paths_config = paths_config
        self._command_runner = command_runner or _default_command_runner
        self._coordinator = coordinator or ManagementRunCoordinator()
        self._synthesis_batch_runner = synthesis_batch_runner or execute_synthesis_batch

    @property
    def coordinator(self) -> ManagementRunCoordinator:
        """Return the shared run coordinator."""
        return self._coordinator

    def runs_dir(self) -> Path:
        """Return the directory for workflow run reports."""
        return management_runs_dir(self._paths)

    def availability(self) -> dict[str, Any]:
        """Return current Update Wiki availability from ops status."""
        status = collect_management_ops_status(self._paths)
        availability = assess_update_wiki_availability(status)
        payload = availability_to_dict(availability)
        payload["status"] = status
        payload["collected_at"] = _utc_timestamp()
        return payload

    def list_runs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent Update Wiki workflow runs newest first."""
        runs_dir = self.runs_dir()
        if not runs_dir.is_dir():
            return []
        reports: list[dict[str, Any]] = []
        for path in sorted(runs_dir.glob("*.json"), reverse=True):
            try:
                report = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if report.get("workflow_id") != UPDATE_WIKI_WORKFLOW_ID:
                continue
            reports.append(report)
            if len(reports) >= limit:
                break
        return reports

    def get_run(self, run_id: str) -> dict[str, Any]:
        """Return one Update Wiki workflow run report."""
        report = self._load_report(run_id)
        if report.get("workflow_id") != UPDATE_WIKI_WORKFLOW_ID:
            raise FileNotFoundError(f"Workflow run not found: {run_id}")
        return report

    def active_run(self) -> dict[str, Any] | None:
        """Return the active workflow run report, if any."""
        active_run_id = self._coordinator.active_run_id()
        if active_run_id is None:
            return None
        try:
            report = self._load_report(active_run_id)
        except FileNotFoundError:
            return None
        if report.get("workflow_id") != UPDATE_WIKI_WORKFLOW_ID:
            return None
        return report

    def start(
        self,
        *,
        synthesis_batch_size: int = DEFAULT_SYNTHESIS_BATCH_SIZE,
        synthesis_between_calls_seconds: float = DEFAULT_SYNTHESIS_BETWEEN_CALLS_SECONDS,
    ) -> dict[str, Any]:
        """Start one Update Wiki workflow run."""
        batch_size = validate_synthesis_batch_size(synthesis_batch_size)
        between_calls = validate_synthesis_between_calls_seconds(synthesis_between_calls_seconds)
        started_at = _utc_timestamp()
        run_id = _run_id(UPDATE_WIKI_WORKFLOW_ID, _utc_now())
        report = _new_workflow_report(
            run_id=run_id,
            batch_size=batch_size,
            between_calls=between_calls,
            started_at=started_at,
        )
        self._coordinator.try_acquire(kind="workflow", run_id=run_id)
        self._write_report(report)
        self._start_worker(run_id)
        return report

    def confirm(self, run_id: str, confirmation_id: str) -> dict[str, Any]:
        """Confirm one waiting workflow step and resume execution."""
        report = self.get_run(run_id)
        if report.get("status") != "waiting_for_confirmation":
            raise WorkflowConflictError("Workflow is not waiting for confirmation.")
        pending = report.get("pending_confirmation") or {}
        if pending.get("id") != confirmation_id:
            raise WorkflowValidationError("Unknown confirmation_id for this workflow run.")
        context = report.setdefault("context", {})
        if confirmation_id == "synthesis_batch":
            context["synthesis_decision"] = "confirm"
        elif confirmation_id == "render_write":
            context["render_decision"] = "confirm"
        else:
            raise WorkflowValidationError("Unknown confirmation_id for this workflow run.")
        report["status"] = "running"
        report["pending_confirmation"] = None
        self._write_report(report)
        self._start_worker(run_id)
        return self.get_run(run_id)

    def skip(self, run_id: str, confirmation_id: str) -> dict[str, Any]:
        """Skip one waiting workflow step and resume execution."""
        report = self.get_run(run_id)
        if report.get("status") != "waiting_for_confirmation":
            raise WorkflowConflictError("Workflow is not waiting for confirmation.")
        pending = report.get("pending_confirmation") or {}
        if pending.get("id") != confirmation_id:
            raise WorkflowValidationError("Unknown confirmation_id for this workflow run.")
        context = report.setdefault("context", {})
        if confirmation_id == "synthesis_batch":
            context["synthesis_decision"] = "skip"
        elif confirmation_id == "render_write":
            context["render_decision"] = "skip"
        else:
            raise WorkflowValidationError("Unknown confirmation_id for this workflow run.")
        report["status"] = "running"
        report["pending_confirmation"] = None
        self._write_report(report)
        self._start_worker(run_id)
        return self.get_run(run_id)

    def _start_worker(self, run_id: str) -> None:
        """Launch one background worker for an Update Wiki workflow run."""
        thread = threading.Thread(
            target=self._execute_workflow,
            args=(run_id,),
            daemon=True,
            name=f"update-wiki-{run_id}",
        )
        thread.start()

    def _execute_workflow(self, run_id: str) -> None:
        """Run or resume the Update Wiki workflow until the next pause or terminal state."""
        try:
            report = self._load_report(run_id)
            report["status"] = "running"
            report["pending_confirmation"] = None
            self._write_report(report)
            batch_size = int((report.get("parameters") or {}).get("synthesis_batch_size", 5))
            between_calls = float(
                (report.get("parameters") or {}).get(
                    "synthesis_between_calls_seconds",
                    DEFAULT_SYNTHESIS_BETWEEN_CALLS_SECONDS,
                )
            )
            context = report.setdefault("context", {})

            if not self._step_done(report, "status") and not self._run_status_step(report):
                return
            if not self._step_done(report, "blocker_check") and not self._run_blocker_step(report):
                return

            if not self._step_done(report, "synthesis_planning"):
                selected_count = self._run_synthesis_planning(report, batch_size=batch_size)
                context["selected_synthesis_count"] = selected_count
                self._write_report(report)
                if report["status"] == "failed":
                    return
                if selected_count == 0:
                    self._mark_step(
                        report,
                        "synthesis_batch",
                        "skipped",
                        ["No synthesis candidates needed"],
                    )
                elif not context.get("synthesis_decision"):
                    self._pause_for_confirmation(
                        report,
                        confirmation_id="synthesis_batch",
                        title=f"Run {min(batch_size, selected_count)} synthesis updates now?",
                        description=(
                            "This may call the OpenAI API and will write synthesis cache files."
                        ),
                        confirm_label="Run synthesis",
                        skip_label="Skip synthesis for now",
                        extra_lines=[
                            (
                                f"{min(batch_size, selected_count)} of "
                                f"{selected_count} synthesis candidates will be processed."
                            ),
                            (
                                f"Pause between syntheses: {int(between_calls)}s"
                                if between_calls > 0
                                else "No pause between syntheses"
                            ),
                        ],
                    )
                    return

            if not self._step_done(report, "synthesis_batch"):
                decision = context.get("synthesis_decision")
                if decision == "skip":
                    self._mark_step(report, "synthesis_batch", "skipped", ["Synthesis skipped"])
                elif decision == "confirm":
                    if not self._run_synthesis_batch(
                        report,
                        batch_size=batch_size,
                        between_calls=between_calls,
                    ):
                        return

            if not self._step_done(report, "render_dry_run") and not self._run_render_dry_run(
                report
            ):
                return

            render_stdout = str(context.get("render_dry_run_stdout") or "")
            if not self._step_done(report, "render_write"):
                if render_changes_pending(render_stdout):
                    if not context.get("render_decision"):
                        write_count = _render_write_count(render_stdout)
                        prune_count = _render_prune_count(render_stdout)
                        self._pause_for_confirmation(
                            report,
                            confirmation_id="render_write",
                            title="Write generated wiki files?",
                            description="This writes generated Obsidian wiki output.",
                            confirm_label="Write render",
                            skip_label="Stop here",
                            extra_lines=[
                                (
                                    f"{write_count} files will be updated · "
                                    f"{prune_count} stale files pruned"
                                )
                            ],
                        )
                        return
                    if context.get("render_decision") == "skip":
                        self._finish(report, status="stopped", headline="Wiki update stopped")
                        return
                    if not self._run_render_write(report):
                        return
                else:
                    self._mark_step(
                        report,
                        "render_write",
                        "skipped",
                        ["No render write needed"],
                    )

            lint_warning = False
            if not self._step_done(report, "wiki_lint"):
                lint_warning = self._run_wiki_lint(report)
            if not self._step_done(report, "final_status"):
                self._run_final_status(report)
            if lint_warning:
                self._finish(
                    report, status="failed", headline="Wiki update completed with warnings"
                )
            else:
                self._finish(report, status="succeeded", headline="Wiki updated successfully")
        finally:
            try:
                terminal_report = self._load_report(run_id)
            except FileNotFoundError:
                return
            if terminal_report.get("status") not in {"running", "waiting_for_confirmation"}:
                self._coordinator.release(run_id)

    def _run_status_step(self, report: dict[str, Any]) -> bool:
        """Collect current ops status for the workflow."""
        self._set_current_step(report, "status")
        self._mark_step_running(report, "status")
        try:
            status = collect_management_ops_status(self._paths)
        except OSError as exc:
            self._fail_step(report, "status", str(exc))
            self._finish(report, status="failed", headline="Wiki update failed")
            return False
        availability = assess_update_wiki_availability(status)
        synthesis = status.get("synthesis") or {}
        plan = synthesis.get("plan") or {}
        changed = int(plan.get("new") or 0) + int(plan.get("stale") or 0)
        self._mark_step(
            report,
            "status",
            "succeeded",
            [
                availability.headline,
                availability.detail_line,
                f"{changed} synthesis candidates found" if changed else "No synthesis candidates",
            ],
        )
        report.setdefault("context", {})["initial_status"] = status
        self._write_report(report)
        return True

    def _run_blocker_step(self, report: dict[str, Any]) -> bool:
        """Stop early when hard blockers are present."""
        self._set_current_step(report, "blocker_check")
        self._mark_step_running(report, "blocker_check")
        status = (report.get("context") or {}).get("initial_status") or {}
        availability = assess_update_wiki_availability(status)
        if availability.blocking_errors:
            self._mark_step(report, "blocker_check", "failed", list(availability.blocking_errors))
            self._finish(report, status="failed", headline="Wiki update blocked")
            return False
        soft_warnings = list(availability.hints)
        self._mark_step(
            report,
            "blocker_check",
            "succeeded",
            soft_warnings or ["No blockers detected"],
        )
        self._write_report(report)
        return True

    def _run_synthesis_planning(self, report: dict[str, Any], *, batch_size: int) -> int:
        """Plan the next synthesis batch without LLM calls."""
        self._set_current_step(report, "synthesis_planning")
        self._mark_step_running(report, "synthesis_planning")
        _, _, command = build_operation_command(
            self._paths,
            self._paths_config,
            "synthesis_select",
            {"limit": batch_size},
        )
        exit_code, stdout, stderr = self._command_runner(command, self._paths.repo_root)
        payload = loads_json_object(stdout) or {}
        summary = (
            parse_synthesis_select_json(payload) if payload else first_meaningful_lines(stdout)
        )
        selected_count = int(payload.get("shown") or 0)
        status: WorkflowStepStatus = "succeeded" if exit_code == 0 else "failed"
        self._mark_step(
            report,
            "synthesis_planning",
            status,
            summary or ["Candidate planning completed"],
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )
        report.setdefault("context", {})["selection"] = payload
        self._write_report(report)
        if exit_code != 0:
            self._finish(
                report, status="failed", headline="Wiki update failed during candidate planning"
            )
        return selected_count if exit_code == 0 else 0

    def _run_synthesis_batch(
        self,
        report: dict[str, Any],
        *,
        batch_size: int,
        between_calls: float,
    ) -> bool:
        """Run a confirmed synthesis batch."""
        self._set_current_step(report, "synthesis_batch")
        self._mark_step_running(report, "synthesis_batch")

        def _on_progress(message: str) -> None:
            self._update_step_progress(report, "synthesis_batch", message)

        exit_code, payload, stdout = self._synthesis_batch_runner(
            self._paths,
            batch_size,
            between_calls,
            _on_progress,
        )
        stderr = "" if exit_code == 0 else stdout if not payload else ""
        summary = parse_synthesis_batch_json(payload) if payload else first_meaningful_lines(stdout)
        status: WorkflowStepStatus = "succeeded" if exit_code == 0 else "failed"
        self._mark_step(
            report,
            "synthesis_batch",
            status,
            summary or ["Synthesis batch finished"],
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )
        self._write_report(report)
        if exit_code != 0:
            self._finish(
                report, status="failed", headline="Wiki update failed during synthesis batch"
            )
            return False
        return True

    def _update_step_progress(
        self,
        report: dict[str, Any],
        step_id: str,
        message: str,
    ) -> None:
        """Persist live progress for one running workflow step."""
        step = report["steps"][self._step_index(report, step_id)]
        if step.get("status") != "running":
            return
        progress_lines = list(step.get("progress_lines") or [])
        progress_lines.append(message)
        step["progress_lines"] = progress_lines[-20:]
        parsed = parse_batch_progress_message(message)
        if parsed is not None:
            step["progress_current"] = parsed["current"]
            step["progress_total"] = parsed["total"]
            step["progress_message"] = parsed["display_message"]
            step["summary_lines"] = [parsed["display_message"]]
        else:
            step["progress_message"] = message
            step["summary_lines"] = [message]
        self._write_report(report)

    def _run_render_dry_run(self, report: dict[str, Any]) -> bool:
        """Preview render changes without writing."""
        self._set_current_step(report, "render_dry_run")
        self._mark_step_running(report, "render_dry_run")
        _, _, command = build_operation_command(
            self._paths,
            self._paths_config,
            "wiki_render_dry_run",
            {},
        )
        exit_code, stdout, stderr = self._command_runner(command, self._paths.repo_root)
        summary = parse_render_summary_text(stdout)
        status: WorkflowStepStatus = "succeeded" if exit_code == 0 else "failed"
        self._mark_step(
            report,
            "render_dry_run",
            status,
            summary,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )
        report.setdefault("context", {})["render_dry_run_stdout"] = stdout
        self._write_report(report)
        if exit_code != 0:
            self._finish(
                report, status="failed", headline="Wiki update failed during render preview"
            )
            return False
        return True

    def _run_render_write(self, report: dict[str, Any]) -> bool:
        """Write render output after explicit confirmation."""
        self._set_current_step(report, "render_write")
        self._mark_step_running(report, "render_write")
        _, _, command = build_operation_command(
            self._paths,
            self._paths_config,
            "wiki_render",
            {"require_source_text": True},
        )
        exit_code, stdout, stderr = self._command_runner(command, self._paths.repo_root)
        summary = parse_render_summary_text(stdout)
        status: WorkflowStepStatus = "succeeded" if exit_code == 0 else "failed"
        self._mark_step(
            report,
            "render_write",
            status,
            summary,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )
        self._write_report(report)
        if exit_code != 0:
            self._finish(report, status="failed", headline="Wiki update failed during render write")
            return False
        return True

    def _run_wiki_lint(self, report: dict[str, Any]) -> bool:
        """Run wiki lint after render steps complete."""
        self._set_current_step(report, "wiki_lint")
        self._mark_step_running(report, "wiki_lint")
        _, _, command = build_operation_command(
            self._paths,
            self._paths_config,
            "wiki_lint",
            {},
        )
        exit_code, stdout, stderr = self._command_runner(command, self._paths.repo_root)
        summary = parse_wiki_lint_output(stdout + "\n" + stderr)
        status: WorkflowStepStatus = "succeeded" if exit_code == 0 else "failed"
        self._mark_step(
            report,
            "wiki_lint",
            status,
            summary,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
        )
        self._write_report(report)
        return exit_code != 0

    def _run_final_status(self, report: dict[str, Any]) -> None:
        """Refresh ops status at the end of the workflow."""
        self._set_current_step(report, "final_status")
        self._mark_step_running(report, "final_status")
        status = collect_management_ops_status(self._paths)
        availability = assess_update_wiki_availability(status)
        self._mark_step(
            report,
            "final_status",
            "succeeded",
            [availability.headline, availability.detail_line],
        )
        report.setdefault("context", {})["final_status"] = status
        self._write_report(report)

    def _pause_for_confirmation(
        self,
        report: dict[str, Any],
        *,
        confirmation_id: str,
        title: str,
        description: str,
        confirm_label: str,
        skip_label: str,
        extra_lines: list[str],
    ) -> None:
        """Pause the workflow until the user confirms or skips."""
        report["status"] = "waiting_for_confirmation"
        report["current_step"] = confirmation_id
        report["pending_confirmation"] = {
            "id": confirmation_id,
            "title": title,
            "description": description,
            "confirm_label": confirm_label,
            "skip_label": skip_label,
            "summary_lines": extra_lines,
        }
        self._write_report(report)

    def _step_done(self, report: dict[str, Any], step_id: str) -> bool:
        """Return whether one workflow step already reached a terminal state."""
        for step in report.get("steps", []):
            if step.get("id") != step_id:
                continue
            return step.get("status") in {"succeeded", "failed", "skipped"}
        return False

    def _finish(self, report: dict[str, Any], *, status: WorkflowRunStatus, headline: str) -> None:
        """Mark the workflow run terminal."""
        finished_at = _utc_timestamp()
        report.update(
            {
                "status": status,
                "headline": headline,
                "finished_at": finished_at,
                "duration_seconds": _duration_seconds(str(report["started_at"]), finished_at),
                "pending_confirmation": None,
            }
        )
        self._write_report(report)

    def _report_path(self, run_id: str) -> Path:
        return self.runs_dir() / f"{run_id}.json"

    def _write_report(self, report: dict[str, Any]) -> Path:
        report_path = self._report_path(str(report["run_id"]))
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report["report_path"] = str(report_path)
        atomic_write_json(report_path, report)
        return report_path

    def _load_report(self, run_id: str) -> dict[str, Any]:
        report_path = self._report_path(run_id)
        if not report_path.is_file():
            raise FileNotFoundError(f"Workflow run not found: {run_id}")
        return json.loads(report_path.read_text(encoding="utf-8"))

    def _set_current_step(self, report: dict[str, Any], step_id: str) -> None:
        report["current_step"] = step_id

    def _step_index(self, report: dict[str, Any], step_id: str) -> int:
        steps = report.setdefault("steps", [])
        for index, step in enumerate(steps):
            if step.get("id") == step_id:
                return index
        steps.append(_new_step(step_id))
        return len(steps) - 1

    def _mark_step_running(self, report: dict[str, Any], step_id: str) -> None:
        step = report["steps"][self._step_index(report, step_id)]
        step["status"] = "running"

    def _mark_step(
        self,
        report: dict[str, Any],
        step_id: str,
        status: WorkflowStepStatus,
        summary_lines: list[str],
        *,
        stdout: str = "",
        stderr: str = "",
        exit_code: int | None = None,
    ) -> None:
        """Update one workflow step with summary and technical output."""
        step = report["steps"][self._step_index(report, step_id)]
        label = next(
            (step_label for sid, step_label in STEP_DEFINITIONS if sid == step_id), step_id
        )
        step.update(
            {
                "label": label,
                "status": status,
                "summary_lines": summary_lines,
                "technical_stdout": _tail(stdout),
                "technical_stderr": _tail(stderr),
                "exit_code": exit_code,
            }
        )

    def _fail_step(self, report: dict[str, Any], step_id: str, message: str) -> None:
        self._mark_step(report, step_id, "failed", [message])


def first_meaningful_lines(text: str, limit: int = 4) -> list[str]:
    """Return the first non-empty stdout/stderr lines."""
    return [line.strip() for line in text.splitlines() if line.strip()][:limit]


def _new_workflow_report(
    *,
    run_id: str,
    batch_size: int,
    between_calls: float,
    started_at: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "workflow_id": UPDATE_WIKI_WORKFLOW_ID,
        "status": "running",
        "current_step": "status",
        "headline": "Update Wiki started",
        "started_at": started_at,
        "finished_at": None,
        "duration_seconds": None,
        "parameters": {
            "synthesis_batch_size": batch_size,
            "synthesis_between_calls_seconds": between_calls,
        },
        "steps": [_new_step(step_id) for step_id, _ in STEP_DEFINITIONS],
        "pending_confirmation": None,
        "context": {},
        "report_path": None,
    }


def _new_step(step_id: str) -> dict[str, Any]:
    label = next((label for sid, label in STEP_DEFINITIONS if sid == step_id), step_id)
    return {
        "id": step_id,
        "label": label,
        "status": "pending",
        "writes": step_id in {"synthesis_batch", "render_write"},
        "llm_calls": step_id == "synthesis_batch",
        "summary_lines": [],
        "technical_stdout": "",
        "technical_stderr": "",
        "exit_code": None,
        "progress_current": None,
        "progress_total": None,
        "progress_message": None,
        "progress_lines": [],
    }


def _source_access_is_blocking(source_access: dict[str, Any]) -> bool:
    if not source_access:
        return False
    return bool(
        source_access.get("malformed_pages")
        or source_access.get("source_id_mismatches")
        or source_access.get("source_pages_missing_raw_markdown")
        or source_access.get("graph_sources_missing_pages")
        or source_access.get("broken_source_link_targets")
    )


def _render_write_count(text: str) -> int:
    from src.management_web.workflow_parsers import _first_int_match

    return _first_int_match(text, r"would write:\s*(\d+)") or 0


def _render_prune_count(text: str) -> int:
    from src.management_web.workflow_parsers import _first_int_match

    return _first_int_match(text, r"would prune:\s*(\d+)") or 0
