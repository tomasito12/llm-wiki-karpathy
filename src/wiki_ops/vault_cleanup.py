"""Plan and execute conservative cleanup of stale vault markdown files."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.pipeline.atomic import atomic_write_json
from src.wiki_lint.vault_hygiene import (
    VaultHygieneStatus,
    collect_vault_hygiene_status,
    deletable_paths_from_status,
    duplicate_removal_paths,
)
from src.wiki_ops.cleanup import _validate_release_manifest
from src.wiki_ops.release_manifest import release_manifest_output_path
from src.wiki_paths.config import WikiPaths

VaultCleanupKind = Literal["orphan_stale", "duplicate"]
REAL_VAULT_CLEANUP_REQUIREMENT = (
    "Real vault cleanup requires --after-release <release_id> and --yes."
)


class VaultCleanupValidationError(Exception):
    """Raised when vault cleanup cannot proceed safely."""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons = reasons
        super().__init__("; ".join(reasons))


@dataclass(frozen=True)
class VaultCleanupCandidate:
    """One vault markdown file eligible for cleanup."""

    relative_path: str
    absolute_path: Path
    kind: VaultCleanupKind
    reason: str
    byte_count: int

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable cleanup candidate payload."""
        return {
            "relative_path": self.relative_path,
            "absolute_path": str(self.absolute_path),
            "kind": self.kind,
            "reason": self.reason,
            "byte_count": self.byte_count,
        }


@dataclass(frozen=True)
class VaultCleanupPlan:
    """Read-only vault cleanup plan derived from hygiene findings."""

    dry_run: bool
    after_release: str | None
    release_manifest_path: Path | None
    wiki_dir: Path
    render_manifest_path: Path
    candidates: tuple[VaultCleanupCandidate, ...]
    excluded_protected: int
    excluded_manual: int
    candidate_count: int
    candidate_bytes: int
    blocked: bool
    blocked_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable vault cleanup plan payload."""
        return {
            "dry_run": self.dry_run,
            "after_release": self.after_release,
            "release_manifest_path": (
                str(self.release_manifest_path) if self.release_manifest_path is not None else None
            ),
            "wiki_dir": str(self.wiki_dir),
            "render_manifest_path": str(self.render_manifest_path),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "excluded_protected": self.excluded_protected,
            "excluded_manual": self.excluded_manual,
            "candidate_count": self.candidate_count,
            "candidate_bytes": self.candidate_bytes,
            "blocked": self.blocked,
            "blocked_reasons": list(self.blocked_reasons),
        }


@dataclass(frozen=True)
class VaultCleanupResult:
    """Result of a real vault cleanup execution."""

    dry_run: bool
    deleted_count: int
    deleted_bytes: int
    deleted_paths: tuple[Path, ...]
    report_path: Path | None
    partial: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable vault cleanup result payload."""
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


def build_vault_cleanup_plan(
    paths: WikiPaths,
    *,
    repo_root: Path,
    dry_run: bool = True,
    after_release: str | None = None,
    allow_path_mismatch: bool = False,
) -> VaultCleanupPlan:
    """Build a read-only vault cleanup plan from current hygiene findings."""
    hygiene_status, _warnings = collect_vault_hygiene_status(
        wiki_dir=paths.wiki_dir,
        manifest_path=paths.manifest_path,
        reviews_dir=paths.reviews_dir,
        raw_dir=paths.raw_dir,
        repo_root=repo_root,
        synthesis_cache_dir=paths.synthesis_dir,
    )
    candidates = _build_candidates(paths.wiki_dir, hygiene_status)
    blocked_reasons = _blocked_reasons(
        paths,
        hygiene_status=hygiene_status,
        after_release=after_release,
        allow_path_mismatch=allow_path_mismatch,
    )
    release_manifest_path = (
        release_manifest_output_path(paths, after_release) if after_release else None
    )
    candidate_bytes = sum(candidate.byte_count for candidate in candidates)
    return VaultCleanupPlan(
        dry_run=dry_run,
        after_release=after_release,
        release_manifest_path=release_manifest_path,
        wiki_dir=paths.wiki_dir,
        render_manifest_path=paths.manifest_path,
        candidates=candidates,
        excluded_protected=len(hygiene_status.protected_in_progress),
        excluded_manual=len(hygiene_status.manual_review),
        candidate_count=len(candidates),
        candidate_bytes=candidate_bytes,
        blocked=bool(blocked_reasons),
        blocked_reasons=tuple(blocked_reasons),
    )


def execute_vault_cleanup(
    plan: VaultCleanupPlan,
    paths: WikiPaths,
    *,
    repo_root: Path,
    allow_path_mismatch: bool = False,
) -> VaultCleanupResult:
    """Delete vault cleanup candidates after re-validating hygiene state."""
    if plan.dry_run:
        msg = "execute_vault_cleanup requires a non-dry-run plan"
        raise VaultCleanupValidationError([msg])
    if plan.blocked:
        raise VaultCleanupValidationError(list(plan.blocked_reasons))

    fresh_plan = build_vault_cleanup_plan(
        paths,
        repo_root=repo_root,
        dry_run=False,
        after_release=plan.after_release,
        allow_path_mismatch=allow_path_mismatch,
    )
    allowed_paths = {candidate.relative_path for candidate in fresh_plan.candidates}
    planned_paths = {candidate.relative_path for candidate in plan.candidates}
    if planned_paths != allowed_paths:
        raise VaultCleanupValidationError(
            ["Vault cleanup plan is stale; rerun wiki-vault-cleanup --dry-run."],
        )

    deleted_paths: list[Path] = []
    deleted_bytes = 0
    for candidate in plan.candidates:
        if not candidate.absolute_path.is_file():
            continue
        deleted_bytes += candidate.byte_count
        candidate.absolute_path.unlink()
        deleted_paths.append(candidate.absolute_path)

    report_path = _write_cleanup_report(
        paths,
        plan=plan,
        deleted_paths=deleted_paths,
        deleted_bytes=deleted_bytes,
    )
    return VaultCleanupResult(
        dry_run=False,
        deleted_count=len(deleted_paths),
        deleted_bytes=deleted_bytes,
        deleted_paths=tuple(deleted_paths),
        report_path=report_path,
    )


def format_vault_cleanup_dry_run_text(plan: VaultCleanupPlan) -> str:
    """Return a concise dry-run report for vault cleanup."""
    lines = [
        "Vault Cleanup Dry Run",
        f"- wiki dir: {plan.wiki_dir}",
        f"- render manifest: {plan.render_manifest_path}",
        f"- after release: {plan.after_release or '(not set)'}",
        f"- delete candidates: {plan.candidate_count} files, {_format_bytes(plan.candidate_bytes)}",
        f"- excluded protected in-progress pages: {plan.excluded_protected}",
        f"- excluded manual review items: {plan.excluded_manual}",
    ]
    if plan.blocked:
        lines.append("- cleanup status: blocked for real execution")
        lines.extend(f"- {reason}" for reason in plan.blocked_reasons)
    else:
        lines.append("- cleanup status: ready for real execution")
    lines.extend(
        [
            "",
            "Real cleanup command",
            REAL_VAULT_CLEANUP_REQUIREMENT,
        ]
    )
    if plan.candidates:
        lines.extend(["", "Delete candidates"])
        for candidate in plan.candidates:
            lines.append(f"- {candidate.relative_path} ({candidate.kind}): {candidate.reason}")
    else:
        lines.extend(["", "No vault cleanup candidates found."])
    return "\n".join(lines)


def format_vault_cleanup_complete_text(
    result: VaultCleanupResult,
    *,
    after_release: str | None,
) -> str:
    """Return a concise completion report for vault cleanup."""
    lines = [
        "Vault Cleanup Complete",
        f"- after release: {after_release}",
        f"- deleted: {result.deleted_count} files, {_format_bytes(result.deleted_bytes)}",
    ]
    if result.report_path is not None:
        lines.append(f"- report: {result.report_path}")
    if result.partial:
        lines.append("- partial: yes")
    return "\n".join(lines)


def _build_candidates(
    wiki_dir: Path,
    hygiene_status: VaultHygieneStatus,
) -> tuple[VaultCleanupCandidate, ...]:
    """Convert hygiene findings into concrete cleanup candidates."""
    duplicate_removals = set(duplicate_removal_paths(hygiene_status.duplicate_groups))
    safe_delete_by_path = {
        item.path: item for item in hygiene_status.safe_delete_candidates
    }
    candidates: list[VaultCleanupCandidate] = []
    for relative_path in deletable_paths_from_status(hygiene_status):
        if relative_path in duplicate_removals:
            candidates.append(
                _candidate_for_path(
                    wiki_dir,
                    relative_path,
                    kind="duplicate",
                    reason=(
                        "Exact duplicate markdown file; keep recommended path from hygiene report."
                    ),
                )
            )
            continue
        item = safe_delete_by_path.get(relative_path)
        if item is None:
            continue
        candidates.append(
            _candidate_for_path(
                wiki_dir,
                relative_path,
                kind="orphan_stale",
                reason=item.reason,
            )
        )
    candidates.sort(key=lambda candidate: candidate.relative_path)
    return tuple(candidates)


def _candidate_for_path(
    wiki_dir: Path,
    relative_path: str,
    *,
    kind: VaultCleanupKind,
    reason: str,
) -> VaultCleanupCandidate:
    """Build one cleanup candidate for a wiki-relative markdown path."""
    absolute_path = (wiki_dir / relative_path).resolve()
    wiki_root = wiki_dir.resolve()
    if not str(absolute_path).startswith(str(wiki_root)):
        msg = f"Refusing cleanup path outside wiki dir: {relative_path}"
        raise VaultCleanupValidationError([msg])
    byte_count = absolute_path.stat().st_size if absolute_path.is_file() else 0
    return VaultCleanupCandidate(
        relative_path=relative_path,
        absolute_path=absolute_path,
        kind=kind,
        reason=reason,
        byte_count=byte_count,
    )


def _blocked_reasons(
    paths: WikiPaths,
    *,
    hygiene_status: VaultHygieneStatus,
    after_release: str | None,
    allow_path_mismatch: bool,
) -> list[str]:
    """Return reasons that block real vault cleanup."""
    blocked: list[str] = []
    if not paths.wiki_dir.is_dir():
        blocked.append(f"Wiki directory not found: {paths.wiki_dir}")
    if not hygiene_status.manifest_exists:
        blocked.append(
            "Render manifest is missing; run wiki-render before vault cleanup.",
        )
    if after_release is None:
        blocked.append(REAL_VAULT_CLEANUP_REQUIREMENT)
    else:
        release_manifest_path = release_manifest_output_path(paths, after_release)
        blocked.extend(
            _validate_release_manifest(
                release_manifest_path,
                paths=paths,
                allow_path_mismatch=allow_path_mismatch,
            )
        )
    return blocked


def _write_cleanup_report(
    paths: WikiPaths,
    *,
    plan: VaultCleanupPlan,
    deleted_paths: list[Path],
    deleted_bytes: int,
) -> Path:
    """Write an audit report for one vault cleanup execution."""
    report_dir = paths.knowledge_root / "tmp" / "vault_cleanup_runs"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    report_path = report_dir / f"{timestamp}.json"
    payload = {
        "created_at": datetime.now(tz=UTC).isoformat(),
        "after_release": plan.after_release,
        "release_manifest_path": (
            str(plan.release_manifest_path) if plan.release_manifest_path is not None else None
        ),
        "wiki_dir": str(plan.wiki_dir),
        "render_manifest_path": str(plan.render_manifest_path),
        "deleted_count": len(deleted_paths),
        "deleted_bytes": deleted_bytes,
        "deleted_paths": [str(path) for path in deleted_paths],
        "planned_candidates": [candidate.to_dict() for candidate in plan.candidates],
    }
    atomic_write_json(report_path, payload)
    return report_path


def _format_bytes(byte_count: int) -> str:
    """Return a short human-readable byte size."""
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    return f"{byte_count / (1024 * 1024):.1f} MB"
