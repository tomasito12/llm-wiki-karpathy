"""Conservative temporary artifact cleanup planning and execution."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json
from src.wiki_ops.release_manifest import release_manifest_output_path
from src.wiki_ops.retention import artifact_area_definitions
from src.wiki_paths.config import WikiPaths

CLEANUP_SCHEMA_VERSION = 1
SUPPORTED_RELEASE_MANIFEST_SCHEMA = 1
CLEANUP_ALLOWLIST = frozenset(
    {
        "synthesis_previews",
        "synthesis_backups",
        "synthesis_prompts",
    }
)
CLEANUP_SKIP_REASONS = {
    "synthesis_runs": "kept for audit in first cleanup slice",
    "ingest_batches": "kept for audit in first cleanup slice",
}
CLEANUP_FILE_REASON = "clean after release"
REAL_CLEANUP_REQUIREMENT = "Real cleanup requires --after-release <release_id> and --yes."
MANIFEST_PATH_KEYS = (
    "raw_dir",
    "reviews_dir",
    "synthesis_dir",
    "wiki_dir",
    "graph_path",
    "manifest_path",
    "release_dir",
)


class CleanupValidationError(Exception):
    """Raised when cleanup cannot proceed safely."""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons = reasons
        super().__init__("; ".join(reasons))


class CleanupExecutionError(Exception):
    """Raised when cleanup execution fails."""

    def __init__(self, message: str, *, partial_paths: list[Path] | None = None) -> None:
        self.partial_paths = list(partial_paths or [])
        super().__init__(message)


@dataclass(frozen=True)
class CleanupCandidate:
    """One temporary file eligible for cleanup."""

    area_key: str
    path: Path
    byte_count: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable cleanup candidate payload."""
        return {
            "area_key": self.area_key,
            "path": str(self.path),
            "byte_count": self.byte_count,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CleanupSkippedArea:
    """Temporary area excluded from cleanup in this slice."""

    area_key: str
    path: Path
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable skipped-area payload."""
        return {
            "area_key": self.area_key,
            "path": str(self.path),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CleanupPlan:
    """Read-only cleanup plan for temporary artifacts."""

    dry_run: bool
    after_release: str | None
    release_manifest_path: Path | None
    candidates: list[CleanupCandidate]
    skipped_areas: list[CleanupSkippedArea]
    candidate_count: int
    candidate_bytes: int
    blocked: bool
    blocked_reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable cleanup plan payload."""
        return {
            "dry_run": self.dry_run,
            "after_release": self.after_release,
            "release_manifest_path": (
                str(self.release_manifest_path) if self.release_manifest_path is not None else None
            ),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "skipped_areas": [area.to_dict() for area in self.skipped_areas],
            "candidate_count": self.candidate_count,
            "candidate_bytes": self.candidate_bytes,
            "blocked": self.blocked,
            "blocked_reasons": list(self.blocked_reasons),
        }


@dataclass(frozen=True)
class CleanupResult:
    """Result of a real cleanup execution."""

    dry_run: bool
    deleted_count: int
    deleted_bytes: int
    deleted_paths: list[Path]
    report_path: Path | None
    partial: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable cleanup result payload."""
        payload = {
            "dry_run": self.dry_run,
            "deleted_count": self.deleted_count,
            "deleted_bytes": self.deleted_bytes,
            "deleted_paths": [str(path) for path in self.deleted_paths],
            "report_path": str(self.report_path) if self.report_path is not None else None,
            "partial": self.partial,
        }
        if self.error is not None:
            payload["error"] = self.error
        return payload


def build_cleanup_plan(
    paths: WikiPaths,
    *,
    dry_run: bool = True,
    after_release: str | None = None,
    selected_areas: frozenset[str] | None = None,
    allow_path_mismatch: bool = False,
) -> CleanupPlan:
    """Build a read-only cleanup plan for temporary artifacts."""
    area_filter = _resolve_area_filter(selected_areas)
    area_roots = _temporary_area_roots(paths)
    candidates = _collect_candidates(area_roots, area_filter)
    skipped_areas = _build_skipped_areas(area_roots, area_filter)
    blocked_reasons: list[str] = []
    release_manifest_path: Path | None = None

    if after_release is None:
        blocked_reasons.append(REAL_CLEANUP_REQUIREMENT)
    else:
        release_manifest_path = release_manifest_output_path(paths, after_release)
        blocked_reasons.extend(
            _validate_release_manifest(
                release_manifest_path,
                paths=paths,
                allow_path_mismatch=allow_path_mismatch,
            )
        )

    blocked = bool(blocked_reasons)

    return CleanupPlan(
        dry_run=dry_run,
        after_release=after_release,
        release_manifest_path=release_manifest_path,
        candidates=candidates,
        skipped_areas=skipped_areas,
        candidate_count=len(candidates),
        candidate_bytes=sum(candidate.byte_count for candidate in candidates),
        blocked=blocked,
        blocked_reasons=blocked_reasons,
    )


def execute_cleanup(
    plan: CleanupPlan,
    paths: WikiPaths,
    *,
    allow_path_mismatch: bool = False,
    created_at: datetime | None = None,
) -> CleanupResult:
    """Execute a validated cleanup plan and write an audit report.

    All candidates are safety-validated before any deletion begins. Partial
    cleanup reports are written only when deletion fails after validation.
    """
    if plan.dry_run:
        return CleanupResult(
            dry_run=True,
            deleted_count=0,
            deleted_bytes=0,
            deleted_paths=[],
            report_path=None,
        )
    if plan.after_release is None:
        raise CleanupValidationError([REAL_CLEANUP_REQUIREMENT])
    if plan.release_manifest_path is None:
        raise CleanupValidationError(["Release manifest path is missing from cleanup plan."])

    validation_errors = _validate_release_manifest(
        plan.release_manifest_path,
        paths=paths,
        allow_path_mismatch=allow_path_mismatch,
    )
    if validation_errors:
        raise CleanupValidationError(validation_errors)

    area_roots = _temporary_area_roots(paths)
    preflight_errors = _validate_all_candidates(
        plan.candidates,
        area_roots=area_roots,
        paths=paths,
    )
    if preflight_errors:
        raise CleanupValidationError(preflight_errors)

    deleted_paths: list[Path] = []
    deleted_bytes = 0
    error: str | None = None
    for candidate in plan.candidates:
        try:
            candidate.path.unlink()
        except OSError as exc:
            error = str(exc)
            break
        deleted_paths.append(candidate.path)
        deleted_bytes += candidate.byte_count

    report_path = write_cleanup_report(
        paths,
        after_release=plan.after_release,
        release_manifest_path=plan.release_manifest_path,
        dry_run=False,
        deleted_paths=deleted_paths,
        deleted_bytes=deleted_bytes,
        skipped_areas=plan.skipped_areas,
        created_at=created_at,
        partial=error is not None,
        error=error,
    )
    return CleanupResult(
        dry_run=False,
        deleted_count=len(deleted_paths),
        deleted_bytes=deleted_bytes,
        deleted_paths=deleted_paths,
        report_path=report_path,
        partial=error is not None,
        error=error,
    )


def _validate_all_candidates(
    candidates: list[CleanupCandidate],
    *,
    area_roots: dict[str, Path],
    paths: WikiPaths,
) -> list[str]:
    """Validate every cleanup candidate before any deletion occurs."""
    errors: list[str] = []
    for candidate in candidates:
        safety_error = validate_candidate_deletion(
            candidate,
            area_roots=area_roots,
            paths=paths,
        )
        if safety_error is not None:
            errors.append(safety_error)
            continue
        if not candidate.path.is_file():
            errors.append(f"Candidate is not a regular file: {candidate.path}")
    return errors


def validate_candidate_deletion(
    candidate: CleanupCandidate,
    *,
    area_roots: dict[str, Path],
    paths: WikiPaths,
) -> str | None:
    """Return an error message when a candidate fails safety validation."""
    if candidate.area_key not in CLEANUP_ALLOWLIST:
        return f"Area {candidate.area_key!r} is not in the cleanup allowlist."
    area_root = area_roots.get(candidate.area_key)
    if area_root is None:
        return f"Unknown cleanup area: {candidate.area_key}."
    if candidate.path.is_symlink():
        return f"Refusing to delete symlink: {candidate.path}"
    try:
        resolved = candidate.path.resolve()
        area_resolved = area_root.resolve()
    except OSError as exc:
        return str(exc)
    if not _path_is_relative_to(resolved, area_resolved):
        return f"Candidate path escapes temporary area {candidate.area_key}: {candidate.path}"
    if _path_is_protected(resolved, paths):
        return f"Candidate path is protected from cleanup: {candidate.path}"
    return None


def write_cleanup_report(
    paths: WikiPaths,
    *,
    after_release: str,
    release_manifest_path: Path,
    dry_run: bool,
    deleted_paths: list[Path],
    deleted_bytes: int,
    skipped_areas: list[CleanupSkippedArea],
    created_at: datetime | None = None,
    partial: bool = False,
    error: str | None = None,
) -> Path:
    """Write a cleanup audit report and return its path."""
    moment = created_at or datetime.now(UTC)
    report_path = cleanup_report_path(paths, when=moment)
    payload: dict[str, Any] = {
        "schema_version": CLEANUP_SCHEMA_VERSION,
        "created_at": moment.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "after_release": after_release,
        "release_manifest_path": str(release_manifest_path),
        "dry_run": dry_run,
        "deleted_count": len(deleted_paths),
        "deleted_bytes": deleted_bytes,
        "deleted_paths": [str(path) for path in deleted_paths],
        "skipped_areas": [
            {"area_key": area.area_key, "reason": area.reason} for area in skipped_areas
        ],
        "partial": partial,
    }
    if error is not None:
        payload["error"] = error
    atomic_write_json(report_path, payload)
    return report_path


def cleanup_report_path(paths: WikiPaths, *, when: datetime) -> Path:
    """Return the JSON report path for one cleanup run."""
    timestamp = when.strftime("%Y%m%dT%H%M%SZ")
    knowledge_root = paths.knowledge_root
    return knowledge_root / "state" / "cleanup_runs" / f"{timestamp}.json"


def format_cleanup_dry_run_text(plan: CleanupPlan) -> str:
    """Render a concise human-readable dry-run cleanup report."""
    lines = [
        "Wiki Cleanup Dry Run",
        f"- after release: {plan.after_release or 'not provided'}",
    ]
    if plan.blocked:
        lines.append("- cleanup status: blocked for real execution")
    else:
        lines.append("- cleanup status: ready for real execution")
    lines.append(
        f"- candidates: {plan.candidate_count} files, {_format_bytes(plan.candidate_bytes)}"
    )
    lines.append("- real cleanup requires --after-release <release_id> --yes")
    lines.append("")
    lines.append("Areas")
    area_counts = _candidate_counts_by_area(plan.candidates)
    for area_key in sorted(CLEANUP_ALLOWLIST):
        if area_key in area_counts:
            count, _bytes = area_counts[area_key]
            lines.append(f"- {area_key}: {count} files, {CLEANUP_FILE_REASON}")
    for skipped in plan.skipped_areas:
        count = area_counts.get(skipped.area_key, (0, 0))[0]
        if count:
            lines.append(f"- {skipped.area_key}: {count} files, skipped, {skipped.reason}")
        else:
            lines.append(f"- {skipped.area_key}: skipped, {skipped.reason}")
    if plan.blocked_reasons:
        lines.append("")
        lines.append("Blocked reasons")
        lines.extend(f"- {reason}" for reason in plan.blocked_reasons)
    return "\n".join(lines)


def format_cleanup_complete_text(result: CleanupResult, *, after_release: str) -> str:
    """Render a concise human-readable cleanup completion report."""
    lines = [
        "Wiki Cleanup Complete",
        f"- after release: {after_release}",
        f"- deleted: {result.deleted_count} files, {_format_bytes(result.deleted_bytes)}",
    ]
    if result.report_path is not None:
        lines.append(f"- report: {result.report_path}")
    if result.partial:
        lines.append("- partial: yes")
    return "\n".join(lines)


def load_release_manifest(path: Path) -> dict[str, Any]:
    """Load a release manifest JSON payload from disk."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = f"Release manifest must be a JSON object: {path}"
        raise CleanupValidationError([msg])
    return payload


def _resolve_area_filter(selected_areas: frozenset[str] | None) -> frozenset[str]:
    """Return the effective cleanup area filter."""
    if selected_areas is None:
        return CLEANUP_ALLOWLIST
    return selected_areas


def _temporary_area_roots(paths: WikiPaths) -> dict[str, Path]:
    """Map temporary area keys to resolved roots from retention definitions."""
    return {
        definition.key: definition.path
        for definition in artifact_area_definitions(paths)
        if definition.data_class == "temporary"
    }


def _collect_candidates(
    area_roots: dict[str, Path],
    area_filter: frozenset[str],
) -> list[CleanupCandidate]:
    """Collect cleanup candidates from allowed temporary areas."""
    candidates: list[CleanupCandidate] = []
    for area_key in sorted(area_filter):
        if area_key not in CLEANUP_ALLOWLIST:
            continue
        area_root = area_roots.get(area_key)
        if area_root is None:
            continue
        for file_path, byte_count in _collect_area_files(area_root):
            candidates.append(
                CleanupCandidate(
                    area_key=area_key,
                    path=file_path,
                    byte_count=byte_count,
                    reason=CLEANUP_FILE_REASON,
                )
            )
    candidates.sort(key=lambda candidate: str(candidate.path))
    return candidates


def _build_skipped_areas(
    area_roots: dict[str, Path],
    area_filter: frozenset[str],
) -> list[CleanupSkippedArea]:
    """Build skipped-area metadata for areas not cleaned in this slice."""
    skipped: list[CleanupSkippedArea] = []
    for area_key, reason in sorted(CLEANUP_SKIP_REASONS.items()):
        if area_key in area_filter:
            continue
        area_root = area_roots.get(area_key, Path())
        skipped.append(
            CleanupSkippedArea(
                area_key=area_key,
                path=area_root,
                reason=reason,
            )
        )
    return skipped


def _collect_area_files(area_root: Path) -> list[tuple[Path, int]]:
    """Collect regular files under one temporary area without following symlinks."""
    if not area_root.exists():
        return []
    if area_root.is_symlink():
        return []
    if area_root.is_file():
        if area_root.is_symlink():
            return []
        return [(area_root.resolve(), area_root.stat().st_size)]
    files: list[tuple[Path, int]] = []
    for root, dirnames, filenames in os.walk(area_root, followlinks=False):
        root_path = Path(root)
        dirnames[:] = [name for name in dirnames if not (root_path / name).is_symlink()]
        for filename in filenames:
            file_path = root_path / filename
            if file_path.is_symlink():
                continue
            try:
                stat = file_path.stat()
            except OSError:
                continue
            if not file_path.is_file():
                continue
            files.append((file_path.resolve(), stat.st_size))
    return files


def _validate_release_manifest(
    manifest_path: Path,
    *,
    paths: WikiPaths,
    allow_path_mismatch: bool,
) -> list[str]:
    """Validate a release manifest for real cleanup."""
    errors: list[str] = []
    if not manifest_path.is_file():
        errors.append(f"Release manifest not found: {manifest_path}")
        return errors
    try:
        payload = load_release_manifest(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Release manifest is unreadable: {exc}")
        return errors
    schema_version = payload.get("schema_version")
    if schema_version != SUPPORTED_RELEASE_MANIFEST_SCHEMA:
        errors.append(f"Unsupported release manifest schema version: {schema_version!r}.")
    status = payload.get("status")
    if status == "blocked":
        errors.append("Release manifest status is blocked.")
    manifest_paths = payload.get("paths")
    if not isinstance(manifest_paths, dict):
        errors.append("Release manifest is missing resolved paths.")
    elif not allow_path_mismatch and not _manifest_paths_match(manifest_paths, paths):
        errors.append("Release manifest paths do not match current resolved path configuration.")
    return errors


def _manifest_paths_match(manifest_paths: dict[str, Any], paths: WikiPaths) -> bool:
    """Return whether manifest paths match the current resolved configuration."""
    current_paths = {
        "raw_dir": str(paths.raw_dir.resolve()),
        "reviews_dir": str(paths.reviews_dir.resolve()),
        "synthesis_dir": str(paths.synthesis_dir.resolve()),
        "wiki_dir": str(paths.wiki_dir.resolve()),
        "graph_path": str(paths.graph_path.resolve()),
        "manifest_path": str(paths.manifest_path.resolve()),
        "release_dir": str(paths.release_dir.resolve()),
    }
    return all(str(manifest_paths.get(key)) == current_paths[key] for key in MANIFEST_PATH_KEYS)


def _path_is_protected(resolved_path: Path, paths: WikiPaths) -> bool:
    """Return whether a resolved path is protected from cleanup."""
    protected_roots = (
        paths.raw_dir,
        paths.reviews_dir,
        paths.synthesis_dir,
        paths.wiki_dir,
        paths.release_dir,
    )
    protected_files = (paths.graph_path, paths.manifest_path)
    for protected_root in protected_roots:
        if _path_is_relative_to(resolved_path, protected_root.resolve()):
            return True
    for protected_file in protected_files:
        if resolved_path == protected_file.resolve():
            return True
    return False


def _path_is_relative_to(path: Path, root: Path) -> bool:
    """Return whether ``path`` is equal to or nested under ``root``."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _candidate_counts_by_area(
    candidates: list[CleanupCandidate],
) -> dict[str, tuple[int, int]]:
    """Aggregate candidate counts and bytes by area key."""
    counts: dict[str, tuple[int, int]] = {}
    for candidate in candidates:
        current = counts.get(candidate.area_key, (0, 0))
        counts[candidate.area_key] = (
            current[0] + 1,
            current[1] + candidate.byte_count,
        )
    return counts


def _format_bytes(byte_count: int) -> str:
    """Format a byte count for human-readable output."""
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    if byte_count < 1024 * 1024 * 1024:
        return f"{byte_count / (1024 * 1024):.1f} MB"
    return f"{byte_count / (1024 * 1024 * 1024):.1f} GB"
