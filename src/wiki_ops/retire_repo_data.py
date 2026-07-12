"""Execute repo-local knowledge and vault data untracking from retirement plans."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from src.pipeline.atomic import atomic_write_json, atomic_write_text
from src.wiki_ops.release_manifest import generate_release_id
from src.wiki_ops.retirement_plan import (
    RepoDataRetirementPlan,
    RetirementPrecondition,
    build_retirement_plan,
)
from src.wiki_ops.status import OpsStatus
from src.wiki_paths.config import WikiPaths

UNTRACKING_SCHEMA_VERSION = 1
DEFAULT_CHUNK_SIZE = 200
DEFAULT_AUDIT_DIR = Path("state/retirement_runs")
GITIGNORE_SECTION_HEADER = "# Externalized knowledge data and generated vault content"
REQUIRED_GITIGNORE_PATTERNS: tuple[str, ...] = (
    "config/wiki_paths.toml",
    "raw/**",
    "state/reviews/",
    "state/synthesis/",
    "state/wiki_render_graph.json",
    "state/wiki_render_manifest.json",
    "state/releases/",
    "state/synthesis_previews/",
    "state/synthesis_runs/",
    "state/synthesis_backups/",
    "state/synthesis_prompts/",
    "state/ingest_batches/",
    "state/ingest_manifest.json",
    "wiki/",
    "sources/",
    "indexes/",
)

ExecutionReadiness = Literal["ready", "blocked"]
ExecutionMode = Literal["dry_run", "real"]


class RepoDataUntrackingError(Exception):
    """Raised when repo data untracking cannot proceed."""


@dataclass(frozen=True)
class RepoDataUntrackingCandidate:
    """One file approved for Git untracking."""

    path: str
    area: str
    byte_count: int
    reason: str


@dataclass(frozen=True)
class RepoDataUntrackingPreflight:
    """Validated execution plan before untracking repo data."""

    readiness: ExecutionReadiness
    blocked_reasons: list[str]
    warnings: list[str]
    candidates: list[RepoDataUntrackingCandidate]
    gitignore_additions: list[str]
    chunks_planned: int
    preconditions: list[RetirementPrecondition]


@dataclass(frozen=True)
class RepoDataUntrackingReport:
    """Result of a dry-run or real repo data untracking operation."""

    schema_version: int
    mode: ExecutionMode
    readiness: ExecutionReadiness
    candidate_count: int
    gitignore_additions: list[str]
    gitignore_updated: bool
    chunks_planned: int
    chunks_executed: int
    files_untracked: list[str]
    local_files_deleted: int
    external_files_touched: int
    preconditions: list[RetirementPrecondition]
    candidates: list[RepoDataUntrackingCandidate]
    blocked_reasons: list[str]
    warnings: list[str]
    audit_report_path: Path | None = None


def build_untracking_preflight(
    paths: WikiPaths,
    *,
    retirement_plan: RepoDataRetirementPlan | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    ops_status: OpsStatus | None = None,
) -> RepoDataUntrackingPreflight:
    """Build and validate a repo data untracking execution plan."""
    if chunk_size <= 0:
        msg = "chunk_size must be positive"
        raise RepoDataUntrackingError(msg)
    plan = retirement_plan or build_retirement_plan(paths, ops_status=ops_status)
    candidates = collect_untracking_candidates(plan)
    gitignore_additions = detect_missing_gitignore_patterns(paths.repo_root / ".gitignore")
    blocked_reasons, warnings = _execution_blockers_and_warnings(
        plan,
        candidates=candidates,
    )
    readiness: ExecutionReadiness = "blocked" if blocked_reasons else "ready"
    chunks_planned = _planned_chunks(len(candidates), chunk_size)
    return RepoDataUntrackingPreflight(
        readiness=readiness,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        candidates=candidates,
        gitignore_additions=gitignore_additions,
        chunks_planned=chunks_planned,
        preconditions=plan.preconditions,
    )


def collect_untracking_candidates(
    retirement_plan: RepoDataRetirementPlan,
) -> list[RepoDataUntrackingCandidate]:
    """Return sorted untracking candidates from one retirement plan."""
    return [
        RepoDataUntrackingCandidate(
            path=entry.path,
            area=entry.area,
            byte_count=entry.byte_count,
            reason=entry.reason,
        )
        for entry in retirement_plan.files
        if entry.proposed_action == "untrack_later"
    ]


def detect_missing_gitignore_patterns(gitignore_path: Path) -> list[str]:
    """Return required ignore patterns that are not yet present."""
    existing = _gitignore_lines(gitignore_path)
    missing: list[str] = []
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        if pattern in existing:
            continue
        if any(_pattern_covers(existing_line, pattern) for existing_line in existing):
            continue
        missing.append(pattern)
    return missing


def append_missing_gitignore_patterns(gitignore_path: Path) -> list[str]:
    """Append missing required ignore patterns and return the additions."""
    missing = detect_missing_gitignore_patterns(gitignore_path)
    if not missing:
        return []
    if gitignore_path.is_file():
        content = gitignore_path.read_text(encoding="utf-8")
    else:
        content = ""
    if GITIGNORE_SECTION_HEADER in content:
        addition = "\n".join(missing) + "\n"
        updated = content.rstrip() + "\n" + addition
    else:
        block = "\n\n" + GITIGNORE_SECTION_HEADER + "\n" + "\n".join(missing) + "\n"
        updated = content.rstrip() + block
    atomic_write_text(gitignore_path, updated)
    return missing


def run_repo_data_untracking(
    paths: WikiPaths,
    *,
    dry_run: bool = True,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    audit_dir: Path | None = None,
    ops_status: OpsStatus | None = None,
    when: datetime | None = None,
) -> RepoDataUntrackingReport:
    """Dry-run or execute repo data untracking from the retirement plan."""
    moment = when or datetime.now(UTC)
    preflight = build_untracking_preflight(
        paths,
        chunk_size=chunk_size,
        ops_status=ops_status,
    )
    mode: ExecutionMode = "dry_run" if dry_run else "real"
    if dry_run or preflight.readiness == "blocked":
        return RepoDataUntrackingReport(
            schema_version=UNTRACKING_SCHEMA_VERSION,
            mode=mode,
            readiness=preflight.readiness,
            candidate_count=len(preflight.candidates),
            gitignore_additions=list(preflight.gitignore_additions),
            gitignore_updated=False,
            chunks_planned=preflight.chunks_planned,
            chunks_executed=0,
            files_untracked=[],
            local_files_deleted=0,
            external_files_touched=0,
            preconditions=preflight.preconditions,
            candidates=preflight.candidates,
            blocked_reasons=preflight.blocked_reasons,
            warnings=preflight.warnings,
            audit_report_path=None,
        )

    gitignore_path = paths.repo_root / ".gitignore"
    gitignore_additions = append_missing_gitignore_patterns(gitignore_path)
    candidate_paths = [candidate.path for candidate in preflight.candidates]
    files_untracked = _run_git_rm_cached_chunks(
        paths.repo_root,
        candidate_paths,
        chunk_size=chunk_size,
    )
    audit_path = _write_audit_report(
        paths,
        audit_dir=audit_dir or paths.repo_root / DEFAULT_AUDIT_DIR,
        report=_build_audit_payload(
            preflight=preflight,
            gitignore_additions=gitignore_additions,
            files_untracked=files_untracked,
            chunks_executed=_planned_chunks(len(files_untracked), chunk_size),
            when=moment,
        ),
        when=moment,
    )
    return RepoDataUntrackingReport(
        schema_version=UNTRACKING_SCHEMA_VERSION,
        mode="real",
        readiness="ready",
        candidate_count=len(preflight.candidates),
        gitignore_additions=gitignore_additions,
        gitignore_updated=bool(gitignore_additions),
        chunks_planned=preflight.chunks_planned,
        chunks_executed=_planned_chunks(len(files_untracked), chunk_size),
        files_untracked=files_untracked,
        local_files_deleted=0,
        external_files_touched=0,
        preconditions=preflight.preconditions,
        candidates=preflight.candidates,
        blocked_reasons=[],
        warnings=preflight.warnings,
        audit_report_path=audit_path,
    )


def untracking_report_to_json(report: RepoDataUntrackingReport) -> dict[str, object]:
    """Return a JSON-serializable untracking report payload."""
    return {
        "schema_version": report.schema_version,
        "mode": report.mode,
        "readiness": report.readiness,
        "candidate_count": report.candidate_count,
        "gitignore_additions": list(report.gitignore_additions),
        "gitignore_updated": report.gitignore_updated,
        "chunks_planned": report.chunks_planned,
        "chunks_executed": report.chunks_executed,
        "files_untracked": list(report.files_untracked),
        "local_files_deleted": report.local_files_deleted,
        "external_files_touched": report.external_files_touched,
        "blocked_reasons": list(report.blocked_reasons),
        "warnings": list(report.warnings),
        "audit_report_path": (
            str(report.audit_report_path) if report.audit_report_path is not None else None
        ),
        "preconditions": [
            {"key": item.key, "status": item.status, "message": item.message}
            for item in report.preconditions
        ],
        "candidates": [
            {
                "path": candidate.path,
                "area": candidate.area,
                "byte_count": candidate.byte_count,
                "reason": candidate.reason,
            }
            for candidate in report.candidates
        ],
    }


def format_untracking_report_text(report: RepoDataUntrackingReport) -> str:
    """Render a concise human-readable untracking report."""
    lines = [
        "Repo Data Untracking",
        f"- mode: {'dry-run' if report.mode == 'dry_run' else 'real'}",
        f"- candidates: {report.candidate_count}",
    ]
    if report.mode == "dry_run":
        lines.append(f"- gitignore additions: {len(report.gitignore_additions)}")
        lines.append(f"- readiness: {report.readiness}")
        area_totals = _largest_area_totals(report.candidates)
        if area_totals:
            lines.append("")
            lines.append("Largest areas")
            for area_key, file_count, byte_count in area_totals:
                lines.append(f"- {area_key}: {file_count} files, {_format_bytes(byte_count)}")
        lines.append("")
        lines.append("No files were untracked.")
    else:
        lines.append(f"- git rm --cached chunks: {report.chunks_executed}")
        lines.append(f"- gitignore updated: {'yes' if report.gitignore_updated else 'no'}")
        if report.audit_report_path is not None:
            lines.append(f"- audit report: {report.audit_report_path}")
        lines.append("")
        lines.append("Files were removed from Git tracking only. Local files were not deleted.")
    if report.blocked_reasons:
        lines.append("")
        lines.append("Blocked")
        lines.extend(f"- {reason}" for reason in report.blocked_reasons)
    if report.warnings:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report.warnings)
    return "\n".join(lines)


def _execution_blockers_and_warnings(
    plan: RepoDataRetirementPlan,
    *,
    candidates: list[RepoDataUntrackingCandidate],
) -> tuple[list[str], list[str]]:
    """Return execution blockers and non-blocking warnings."""
    blocked_reasons: list[str] = []
    warnings: list[str] = []

    if plan.git_inventory_error is not None:
        blocked_reasons.append(plan.git_inventory_error)
    if plan.summary.manual_review > 0:
        blocked_reasons.append(
            f"Retirement plan contains {plan.summary.manual_review} manual_review files."
        )
    if plan.summary.keep_untracked_local_config > 0:
        blocked_reasons.append("Local configuration files are still tracked in Git.")
    if not candidates:
        blocked_reasons.append("No untrack_later candidates were found.")

    for item in plan.preconditions:
        if (
            item.key in {"external_knowledge_root", "external_vault_root"}
            and item.status == "error"
        ):
            blocked_reasons.append(item.message)
        elif item.key == "latest_release_verification" and item.status == "error":
            blocked_reasons.append(item.message)
        elif item.key == "git_tracked_inventory" and item.status == "error":
            blocked_reasons.append(item.message)
        elif item.key == "git_working_tree" and item.status in {"warning", "error"}:
            blocked_reasons.append(item.message)
        elif item.key == "tracked_local_config" and item.status == "error":
            blocked_reasons.append(item.message)
        elif item.key == "synthesis_cache_lint" and item.status == "error":
            blocked_reasons.append(item.message)
        elif item.status == "warning":
            warnings.append(item.message)

    return _dedupe_preserve_order(blocked_reasons), _dedupe_preserve_order(warnings)


def _run_git_rm_cached_chunks(
    repo_root: Path,
    candidate_paths: list[str],
    *,
    chunk_size: int,
) -> list[str]:
    """Run chunked git rm --cached calls and return untracked paths."""
    untracked: list[str] = []
    for chunk in _chunk_paths(candidate_paths, chunk_size):
        result = subprocess.run(
            ["git", "rm", "--cached", "--", *chunk],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "git rm --cached failed"
            raise RepoDataUntrackingError(message)
        untracked.extend(chunk)
    return untracked


def _write_audit_report(
    paths: WikiPaths,
    *,
    audit_dir: Path,
    report: dict[str, object],
    when: datetime,
) -> Path:
    """Write one audit report JSON file under the repo-local audit directory."""
    audit_dir.mkdir(parents=True, exist_ok=True)
    output_path = audit_dir / f"{generate_release_id(when=when)}.json"
    atomic_write_json(output_path, report)
    return output_path


def _build_audit_payload(
    *,
    preflight: RepoDataUntrackingPreflight,
    gitignore_additions: list[str],
    files_untracked: list[str],
    chunks_executed: int,
    when: datetime,
) -> dict[str, object]:
    """Build the audit payload for one real untracking run."""
    return {
        "schema_version": UNTRACKING_SCHEMA_VERSION,
        "executed_at": when.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "candidate_count": len(preflight.candidates),
        "gitignore_additions": gitignore_additions,
        "chunks_executed": chunks_executed,
        "files_untracked": files_untracked,
        "local_files_deleted": 0,
        "external_files_touched": 0,
        "preconditions": [
            {"key": item.key, "status": item.status, "message": item.message}
            for item in preflight.preconditions
        ],
        "candidates": [
            {
                "path": candidate.path,
                "area": candidate.area,
                "byte_count": candidate.byte_count,
                "reason": candidate.reason,
            }
            for candidate in preflight.candidates
        ],
    }


def _gitignore_lines(gitignore_path: Path) -> set[str]:
    """Return normalized non-comment gitignore lines."""
    if not gitignore_path.is_file():
        return set()
    lines: set[str] = set()
    for line in gitignore_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.add(stripped)
    return lines


def _pattern_covers(existing_line: str, required_pattern: str) -> bool:
    """Return whether an existing gitignore line covers a required pattern."""
    if existing_line == required_pattern:
        return True
    if existing_line.endswith("/**") and required_pattern.startswith(existing_line[:-3]):
        return True
    if existing_line.endswith("/") and required_pattern.startswith(existing_line):
        return True
    return False


def _chunk_paths(paths: list[str], chunk_size: int) -> list[list[str]]:
    """Split candidate paths into fixed-size chunks."""
    if chunk_size <= 0:
        msg = "chunk_size must be positive"
        raise ValueError(msg)
    return [paths[index : index + chunk_size] for index in range(0, len(paths), chunk_size)]


def _planned_chunks(candidate_count: int, chunk_size: int) -> int:
    """Return the number of git rm chunks required for one candidate count."""
    if candidate_count == 0:
        return 0
    return (candidate_count + chunk_size - 1) // chunk_size


def _largest_area_totals(
    candidates: list[RepoDataUntrackingCandidate],
    *,
    limit: int = 5,
) -> list[tuple[str, int, int]]:
    """Return the largest candidate areas by byte count."""
    grouped: dict[str, tuple[int, int]] = {}
    for candidate in candidates:
        file_count, byte_count = grouped.get(candidate.area, (0, 0))
        grouped[candidate.area] = (file_count + 1, byte_count + candidate.byte_count)
    ranked = sorted(grouped.items(), key=lambda item: (-item[1][1], item[0]))
    return [(area, counts[0], counts[1]) for area, counts in ranked[:limit]]


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    """Return unique strings while preserving first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _format_bytes(byte_count: int) -> str:
    """Format a byte count for human-readable output."""
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    if byte_count < 1024 * 1024 * 1024:
        return f"{byte_count / (1024 * 1024):.1f} MB"
    return f"{byte_count / (1024 * 1024 * 1024):.1f} GB"
