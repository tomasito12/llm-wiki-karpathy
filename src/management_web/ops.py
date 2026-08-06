"""Allowlisted pipeline operations for the management web cockpit."""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.pipeline.atomic import atomic_write_json
from src.wiki_ops.status import OpsStatusConfig, collect_ops_status
from src.wiki_paths.config import WikiPaths

OperationRunStatus = Literal["queued", "running", "succeeded", "failed", "cancelled"]
ParameterType = Literal["integer", "boolean", "float"]

_TAIL_CHARS = 8000
_MAX_LIMIT = 100


class OperationValidationError(ValueError):
    """Raised when an operation id or parameters are invalid."""


class OperationConflictError(RuntimeError):
    """Raised when confirmation or concurrency rules block a run."""


class ManagementRunCoordinator:
    """Ensure only one manual operation or workflow runs at a time."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_kind: str | None = None
        self._active_run_id: str | None = None

    def try_acquire(self, *, kind: str, run_id: str) -> None:
        """Reserve the single active run slot for one operation or workflow."""
        with self._lock:
            if self._active_kind is not None:
                raise OperationConflictError("Another operation is already running.")
            self._active_kind = kind
            self._active_run_id = run_id

    def release(self, run_id: str) -> None:
        """Release the active run slot when a run finishes."""
        with self._lock:
            if self._active_run_id == run_id:
                self._active_kind = None
                self._active_run_id = None

    def active_run_id(self) -> str | None:
        """Return the currently active run id, if any."""
        with self._lock:
            return self._active_run_id


@dataclass(frozen=True)
class OperationParameterDefinition:
    """One validated parameter exposed to the management web UI."""

    name: str
    label: str
    type: ParameterType
    default: bool | int | float
    required: bool = False
    minimum: int | float | None = None
    maximum: int | float | None = None


@dataclass(frozen=True)
class OperationDefinition:
    """Hardcoded allowlisted operation metadata."""

    id: str
    label: str
    description: str
    writes: bool
    llm_calls: bool
    requires_confirmation: bool
    parameters: tuple[OperationParameterDefinition, ...]
    module: str


CommandRunner = Callable[[list[str], Path], tuple[int, str, str]]


def _default_command_runner(command: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run one allowlisted module command and capture stdout/stderr."""
    try:
        completed = subprocess.run(  # noqa: S603
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return 1, "", str(exc)
    return completed.returncode, completed.stdout, completed.stderr


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def _utc_timestamp() -> str:
    return _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_id(operation_id: str, started_at: datetime) -> str:
    slug = operation_id.replace("_", "-")
    return f"{started_at.strftime('%Y%m%dT%H%M%SZ')}-{slug}"


def _tail(text: str) -> str:
    if len(text) <= _TAIL_CHARS:
        return text
    return text[-_TAIL_CHARS:]


def effective_paths_config(paths: WikiPaths, paths_config: Path | None) -> Path | None:
    """Return the paths config file used for subprocess module invocations."""
    if paths_config is not None:
        return paths_config
    candidate = paths.repo_root / "config" / "wiki_paths.toml"
    return candidate if candidate.is_file() else None


def _paths_config_args(paths: WikiPaths, paths_config: Path | None) -> list[str]:
    resolved = effective_paths_config(paths, paths_config)
    return ["--paths-config", str(resolved)] if resolved is not None else []


def _ops_status_config(paths: WikiPaths) -> OpsStatusConfig:
    return OpsStatusConfig(
        repo_root=paths.repo_root,
        raw_dir=paths.raw_dir,
        reviews_dir=paths.reviews_dir,
        wiki_dir=paths.wiki_dir,
        graph_path=paths.graph_path,
        manifest_path=paths.manifest_path,
        synthesis_cache_dir=paths.synthesis_dir,
        preview_dir=paths.preview_dir,
        run_dir=paths.run_dir,
        backup_dir=paths.backup_dir,
        readwise_index_path=paths.knowledge_root / "state" / "readwise_library.json",
    )


def collect_management_ops_status(paths: WikiPaths) -> dict[str, Any]:
    """Collect current ops status without writes or LLM calls."""
    return collect_ops_status(_ops_status_config(paths)).to_dict()


def management_runs_dir(paths: WikiPaths) -> Path:
    """Return the directory for management-launched run reports."""
    return paths.knowledge_root / "tmp" / "management_runs"


def _python_command(module: str, *args: str) -> list[str]:
    return [sys.executable, "-m", module, *args]


def _build_wiki_lint_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    _ = parameters
    return _python_command("src.wiki_lint", *_paths_config_args(paths, paths_config))


def _build_wiki_render_dry_run_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    _ = parameters
    return _python_command(
        "src.wiki_render",
        *_paths_config_args(paths, paths_config),
        "--dry-run",
    )


def _build_wiki_render_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    args = [*_paths_config_args(paths, paths_config)]
    if bool(parameters.get("require_source_text", True)):
        args.append("--require-source-text")
    return _python_command("src.wiki_render", *args)


def _build_synthesis_select_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    limit = int(parameters["limit"])
    return _python_command(
        "src.wiki_synthesis.select_cli",
        *_paths_config_args(paths, paths_config),
        "--limit",
        str(limit),
        "--json",
    )


def _build_synthesis_batch_dry_run_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    limit = int(parameters["limit"])
    return _python_command(
        "src.wiki_synthesis.batch_cli",
        *_paths_config_args(paths, paths_config),
        "--dry-run",
        "--limit",
        str(limit),
        "--json",
    )


def _build_synthesis_batch_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    limit = int(parameters["limit"])
    between_calls = float(parameters["between_calls"])
    args = [
        *_paths_config_args(paths, paths_config),
        "--yes",
        "--limit",
        str(limit),
        "--between-calls",
        str(between_calls),
        "--json",
    ]
    if bool(parameters.get("continue_on_error", False)):
        args.append("--continue-on-error")
    return _python_command("src.wiki_synthesis.batch_cli", *args)


def _build_readwise_sync_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    """Build the normal incremental Readwise sync command with automatic dedupe."""
    _ = parameters
    return _python_command("src.readwise", *_paths_config_args(paths, paths_config))


def _build_ingest_preanalyze_command(
    paths: WikiPaths,
    paths_config: Path | None,
    parameters: dict[str, Any],
) -> list[str]:
    """Build a bounded pre-analysis command for pending source documents."""
    return _python_command(
        "src.ingest_batch.cli",
        *_paths_config_args(paths, paths_config),
        "--limit",
        str(int(parameters["limit"])),
        "--between-articles",
        str(float(parameters["between_articles"])),
    )


_OPERATION_BUILDERS: dict[str, Callable[[WikiPaths, Path | None, dict[str, Any]], list[str]]] = {
    "readwise_sync": _build_readwise_sync_command,
    "ingest_preanalyze": _build_ingest_preanalyze_command,
    "wiki_lint": _build_wiki_lint_command,
    "wiki_render_dry_run": _build_wiki_render_dry_run_command,
    "wiki_render": _build_wiki_render_command,
    "synthesis_select": _build_synthesis_select_command,
    "synthesis_batch_dry_run": _build_synthesis_batch_dry_run_command,
    "synthesis_batch": _build_synthesis_batch_command,
}


OPERATION_DEFINITIONS: tuple[OperationDefinition, ...] = (
    OperationDefinition(
        id="readwise_sync",
        label="Readwise sync",
        description="Download new processed Readwise documents and remove near-duplicates.",
        writes=True,
        llm_calls=False,
        requires_confirmation=True,
        parameters=(),
        module="src.readwise",
    ),
    OperationDefinition(
        id="ingest_preanalyze",
        label="Ingest pre-analysis",
        description="Pre-analyze a bounded batch of pending documents with OpenAI.",
        writes=True,
        llm_calls=True,
        requires_confirmation=True,
        parameters=(
            OperationParameterDefinition(
                name="limit",
                label="Documents",
                type="integer",
                default=10,
                minimum=1,
                maximum=_MAX_LIMIT,
            ),
            OperationParameterDefinition(
                name="between_articles",
                label="Pause between documents (seconds)",
                type="float",
                default=300.0,
                minimum=0,
                maximum=3600,
            ),
        ),
        module="src.ingest_batch.cli",
    ),
    OperationDefinition(
        id="wiki_lint",
        label="Wiki lint",
        description="Validate generated wiki markdown and vault hygiene without writes.",
        writes=False,
        llm_calls=False,
        requires_confirmation=False,
        parameters=(),
        module="src.wiki_lint",
    ),
    OperationDefinition(
        id="wiki_render_dry_run",
        label="Wiki render dry-run",
        description="Preview generated wiki changes from finished reviews.",
        writes=False,
        llm_calls=False,
        requires_confirmation=False,
        parameters=(),
        module="src.wiki_render",
    ),
    OperationDefinition(
        id="wiki_render",
        label="Wiki render",
        description="Write generated Obsidian wiki pages from finished reviews.",
        writes=True,
        llm_calls=False,
        requires_confirmation=True,
        parameters=(
            OperationParameterDefinition(
                name="require_source_text",
                label="Require source text",
                type="boolean",
                default=True,
            ),
        ),
        module="src.wiki_render",
    ),
    OperationDefinition(
        id="synthesis_select",
        label="Synthesis select",
        description="Rank changed synthesis candidates without LLM calls.",
        writes=False,
        llm_calls=False,
        requires_confirmation=False,
        parameters=(
            OperationParameterDefinition(
                name="limit",
                label="Limit",
                type="integer",
                default=20,
            ),
        ),
        module="src.wiki_synthesis.select_cli",
    ),
    OperationDefinition(
        id="synthesis_batch_dry_run",
        label="Synthesis batch dry-run",
        description="Plan a bounded synthesis batch without API calls or cache writes.",
        writes=False,
        llm_calls=False,
        requires_confirmation=False,
        parameters=(
            OperationParameterDefinition(
                name="limit",
                label="Limit",
                type="integer",
                default=10,
            ),
        ),
        module="src.wiki_synthesis.batch_cli",
    ),
    OperationDefinition(
        id="synthesis_batch",
        label="Synthesis batch",
        description="Run a bounded synthesis batch with OpenAI calls and cache writes.",
        writes=True,
        llm_calls=True,
        requires_confirmation=True,
        parameters=(
            OperationParameterDefinition(
                name="limit",
                label="Limit",
                type="integer",
                default=5,
            ),
            OperationParameterDefinition(
                name="between_calls",
                label="Pause between calls (seconds)",
                type="float",
                default=300.0,
            ),
            OperationParameterDefinition(
                name="continue_on_error",
                label="Continue on error",
                type="boolean",
                default=False,
            ),
        ),
        module="src.wiki_synthesis.batch_cli",
    ),
)


def get_operation_definition(operation_id: str) -> OperationDefinition:
    """Return one allowlisted operation definition."""
    for operation in OPERATION_DEFINITIONS:
        if operation.id == operation_id:
            return operation
    raise OperationValidationError(f"Unknown operation_id: {operation_id}")


def list_operation_definitions() -> list[OperationDefinition]:
    """Return all allowlisted operation definitions."""
    return list(OPERATION_DEFINITIONS)


def _coerce_parameter(
    definition: OperationParameterDefinition,
    raw_value: Any,
) -> bool | int | float:
    if definition.type == "boolean":
        if not isinstance(raw_value, bool):
            raise OperationValidationError(f"Parameter {definition.name} must be a boolean.")
        return raw_value
    if definition.type == "integer":
        if isinstance(raw_value, bool) or not isinstance(raw_value, int):
            raise OperationValidationError(f"Parameter {definition.name} must be an integer.")
        if raw_value < 1 or raw_value > _MAX_LIMIT:
            raise OperationValidationError(
                f"Parameter {definition.name} must be between 1 and {_MAX_LIMIT}."
            )
        return raw_value
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
        raise OperationValidationError(f"Parameter {definition.name} must be a number.")
    minimum = definition.minimum if definition.minimum is not None else 0
    maximum = definition.maximum
    if raw_value < minimum or (maximum is not None and raw_value > maximum):
        if maximum is not None:
            raise OperationValidationError(
                f"Parameter {definition.name} must be between {minimum} and {maximum}."
            )
        raise OperationValidationError(
            f"Parameter {definition.name} must be {minimum} or greater."
        )
    return float(raw_value)


def normalize_operation_parameters(
    operation: OperationDefinition,
    parameters: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate and apply defaults for one operation request."""
    payload = parameters or {}
    unknown = sorted(set(payload) - {param.name for param in operation.parameters})
    if unknown:
        raise OperationValidationError(f"Unknown parameters: {', '.join(unknown)}")
    normalized: dict[str, Any] = {}
    for param in operation.parameters:
        if param.name in payload:
            normalized[param.name] = _coerce_parameter(param, payload[param.name])
        else:
            normalized[param.name] = param.default
    return normalized


def build_operation_command(
    paths: WikiPaths,
    paths_config: Path | None,
    operation_id: str,
    parameters: dict[str, Any] | None,
) -> tuple[OperationDefinition, dict[str, Any], list[str]]:
    """Build the subprocess command for one allowlisted operation."""
    operation = get_operation_definition(operation_id)
    normalized = normalize_operation_parameters(operation, parameters)
    builder = _OPERATION_BUILDERS[operation.id]
    return operation, normalized, builder(paths, paths_config, normalized)


def _duration_seconds(started_at: str, finished_at: str | None) -> float | None:
    if not finished_at:
        return None
    start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    finish = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    return max(0.0, (finish - start).total_seconds())


class OpsRunManager:
    """Manage one-at-a-time management web pipeline runs."""

    def __init__(
        self,
        *,
        paths: WikiPaths,
        paths_config: Path | None = None,
        command_runner: CommandRunner | None = None,
        coordinator: ManagementRunCoordinator | None = None,
    ) -> None:
        self._paths = paths
        self._paths_config = paths_config
        self._command_runner = command_runner or _default_command_runner
        self._coordinator = coordinator or ManagementRunCoordinator()
        self._active_run_id: str | None = None

    @property
    def paths(self) -> WikiPaths:
        return self._paths

    def runs_dir(self) -> Path:
        return management_runs_dir(self._paths)

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
            raise FileNotFoundError(f"Run not found: {run_id}")
        return json.loads(report_path.read_text(encoding="utf-8"))

    def list_runs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent run reports newest first."""
        runs_dir = self.runs_dir()
        if not runs_dir.is_dir():
            return []
        reports: list[dict[str, Any]] = []
        for path in sorted(runs_dir.glob("*.json"), reverse=True):
            try:
                report = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if report.get("workflow_id"):
                continue
            reports.append(report)
            if len(reports) >= limit:
                break
        return reports

    def get_run(self, run_id: str) -> dict[str, Any]:
        """Return one run report."""
        return self._load_report(run_id)

    def active_run(self) -> dict[str, Any] | None:
        """Return the currently active run report, if any."""
        active_run_id = self._coordinator.active_run_id()
        if active_run_id is None:
            return None
        try:
            return self._load_report(active_run_id)
        except FileNotFoundError:
            return None

    def start_run(
        self,
        operation_id: str,
        *,
        parameters: dict[str, Any] | None = None,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        """Queue and start one allowlisted operation."""
        operation, normalized, command = build_operation_command(
            self._paths,
            self._paths_config,
            operation_id,
            parameters,
        )
        if operation.requires_confirmation and not confirmed:
            raise OperationConflictError(
                "Operation requires explicit confirmation before it can run."
            )
        started_at = _utc_timestamp()
        run_id = _run_id(operation.id, _utc_now())
        report: dict[str, Any] = {
            "run_id": run_id,
            "operation_id": operation.id,
            "label": operation.label,
            "status": "queued",
            "parameters": normalized,
            "command": command,
            "cwd": str(self._paths.repo_root),
            "writes": operation.writes,
            "llm_calls": operation.llm_calls,
            "started_at": started_at,
            "finished_at": None,
            "duration_seconds": None,
            "exit_code": None,
            "stdout_tail": "",
            "stderr_tail": "",
            "report_path": None,
        }
        self._coordinator.try_acquire(kind="operation", run_id=run_id)
        self._write_report(report)
        self._active_run_id = run_id
        thread = threading.Thread(
            target=self._execute_run,
            args=(run_id, command),
            daemon=True,
            name=f"management-run-{run_id}",
        )
        thread.start()
        return report

    def _execute_run(self, run_id: str, command: list[str]) -> None:
        report = self._load_report(run_id)
        report["status"] = "running"
        self._write_report(report)
        exit_code, stdout, stderr = self._command_runner(command, self._paths.repo_root)
        finished_at = _utc_timestamp()
        report.update(
            {
                "status": "succeeded" if exit_code == 0 else "failed",
                "finished_at": finished_at,
                "duration_seconds": _duration_seconds(str(report["started_at"]), finished_at),
                "exit_code": exit_code,
                "stdout_tail": _tail(stdout),
                "stderr_tail": _tail(stderr),
            }
        )
        self._write_report(report)
        self._coordinator.release(run_id)
        if self._active_run_id == run_id:
            self._active_run_id = None


def format_ops_status_summary(status: dict[str, Any]) -> str:
    """Return a compact one-line pipeline status summary for the UI."""
    sources = status.get("sources") or {}
    reviews = status.get("reviews") or {}
    synthesis = status.get("synthesis") or {}
    render = status.get("render") or {}
    paired = sources.get("paired", 0)
    finished = reviews.get("finished", 0)
    stale = synthesis.get("stale", 0)
    render_bits: list[str] = []
    if render.get("manifest_exists") and render.get("graph_exists"):
        render_bits.append("render current")
    else:
        render_bits.append("render incomplete")
    if stale:
        render_bits.append(f"{stale} stale syntheses")
    return f"{paired} sources · {finished} reviewed · {' · '.join(render_bits)}"


def recommendation_operation_id(recommendation: str) -> str | None:
    """Map one ops status recommendation to a cockpit operation id when possible."""
    lowered = recommendation.lower()
    if "dry-run" in lowered and "synthesis" in lowered:
        return "synthesis_batch_dry_run"
    if "synthesis" in lowered and "batch" in lowered:
        return "synthesis_batch"
    if "synthesis" in lowered and ("refresh" in lowered or "stale" in lowered):
        return "synthesis_batch_dry_run"
    if "render" in lowered and "dry-run" in lowered:
        return "wiki_render_dry_run"
    if "render" in lowered:
        return "wiki_render"
    if "lint" in lowered:
        return "wiki_lint"
    if "synthesis" in lowered and "select" in lowered:
        return "synthesis_select"
    return None
