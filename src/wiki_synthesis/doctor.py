"""Preflight checks for the Stage 2 synthesis workflow."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.wiki_synthesis.cache_lint import CacheLintReport, lint_synthesis_cache
from src.wiki_synthesis.models import SynthesisPlan
from src.wiki_synthesis.planner import plan_from_graph


@dataclass(frozen=True)
class DoctorCheck:
    """One preflight check result."""

    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable check."""
        return asdict(self)


@dataclass(frozen=True)
class DoctorReport:
    """Preflight report for one synthesis target or batch."""

    ready: bool
    model: str
    graph_path: str
    cache_dir: str
    preview_dir: str
    report_dir: str
    plan: SynthesisPlan
    cache_lint: CacheLintReport
    checks: list[DoctorCheck]

    @property
    def exit_code(self) -> int:
        """Return shell exit code for this report."""
        return 0 if self.ready else 1

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report."""
        return {
            "ready": self.ready,
            "model": self.model,
            "graph_path": self.graph_path,
            "cache_dir": self.cache_dir,
            "preview_dir": self.preview_dir,
            "report_dir": self.report_dir,
            "plan": self.plan.to_dict(),
            "cache_lint": self.cache_lint.to_dict(),
            "checks": [check.to_dict() for check in self.checks],
        }


def run_doctor(
    graph: dict[str, Any],
    *,
    graph_path: Path,
    cache_dir: Path,
    preview_dir: Path,
    report_dir: Path,
    model: str,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    limit: int = 1,
    require_api_key: bool = False,
    finished_source_ids: set[str] | None = None,
) -> DoctorReport:
    """Run preflight checks for the synthesis workflow."""
    plan = plan_from_graph(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_single_source=include_single_source,
        changed_only=True,
        limit=limit,
        finished_source_ids=finished_source_ids,
    )
    cache_lint = lint_synthesis_cache(
        graph,
        cache_dir=cache_dir,
        category=category,
        entity=entity,
        include_missing=False,
    )
    checks = [
        _path_check("graph", graph_path, must_exist=True),
        _dir_parent_check("cache_dir", cache_dir),
        _dir_parent_check("preview_dir", preview_dir),
        _dir_parent_check("report_dir", report_dir),
        _model_check(model),
        _api_key_check(require_api_key=require_api_key),
        _plan_check(plan),
        _cache_lint_check(cache_lint),
    ]
    return DoctorReport(
        ready=all(check.status != "error" for check in checks),
        model=model,
        graph_path=str(graph_path),
        cache_dir=str(cache_dir),
        preview_dir=str(preview_dir),
        report_dir=str(report_dir),
        plan=plan,
        cache_lint=cache_lint,
        checks=checks,
    )


def _path_check(name: str, path: Path, *, must_exist: bool) -> DoctorCheck:
    """Return a check for a path."""
    if must_exist and not path.exists():
        return DoctorCheck(name=name, status="error", message=f"path does not exist: {path}")
    return DoctorCheck(name=name, status="ok", message=str(path))


def _dir_parent_check(name: str, path: Path) -> DoctorCheck:
    """Return a check for a writable output directory parent."""
    parent = path if path.exists() else path.parent
    if not parent.exists():
        return DoctorCheck(
            name=name,
            status="error",
            message=f"parent directory does not exist: {parent}",
        )
    return DoctorCheck(name=name, status="ok", message=str(path))


def _model_check(model: str) -> DoctorCheck:
    """Return a model configuration check."""
    if not model.strip():
        return DoctorCheck(name="model", status="error", message="model is empty")
    return DoctorCheck(name="model", status="ok", message=model)


def _api_key_check(*, require_api_key: bool) -> DoctorCheck:
    """Return an API key availability check."""
    if os.environ.get("OPENAI_API_KEY"):
        return DoctorCheck(name="openai_api_key", status="ok", message="OPENAI_API_KEY is set")
    status = "error" if require_api_key else "warning"
    message = "OPENAI_API_KEY is not set"
    return DoctorCheck(name="openai_api_key", status=status, message=message)


def _plan_check(plan: SynthesisPlan) -> DoctorCheck:
    """Return a plan readiness check."""
    executable = [entry for entry in plan.entries if entry.state in {"new", "stale"}]
    if executable:
        return DoctorCheck(
            name="plan",
            status="ok",
            message=f"{len(executable)} executable synthesis target(s)",
        )
    return DoctorCheck(name="plan", status="warning", message="no executable synthesis targets")


def _cache_lint_check(report: CacheLintReport) -> DoctorCheck:
    """Return a cache lint readiness check."""
    if report.errors:
        return DoctorCheck(
            name="cache_lint",
            status="error",
            message=f"{report.errors} cache error(s)",
        )
    if report.warnings:
        return DoctorCheck(
            name="cache_lint",
            status="warning",
            message=f"{report.warnings} stale cache warning(s)",
        )
    return DoctorCheck(name="cache_lint", status="ok", message="no cache errors")
