"""Release manifest prototype for wiki knowledge releases."""

from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml

from src.pipeline.atomic import atomic_write_json
from src.wiki_ops.retention import (
    RetentionInventory,
    collect_retention_inventory,
)
from src.wiki_ops.status import OpsStatus, collect_review_status
from src.wiki_paths.config import WikiPaths

SCHEMA_VERSION = 1
RELEASE_MANIFEST_AREA_KEYS = (
    "raw_readwise",
    "reviews",
    "synthesis_cache",
    "render_graph",
    "render_manifest",
    "wiki",
)
ReleaseStatus = Literal["ready", "warning", "blocked"]
PathKind = Literal["file", "directory", "missing", "other"]
CheckpointKind = Literal["release", "pre_ingest", "pre_review", "pre_synthesis", "pre_render"]


@dataclass(frozen=True)
class PathHash:
    """Deterministic hash metadata for one filesystem path."""

    path: Path
    exists: bool
    kind: PathKind
    file_count: int
    byte_count: int
    sha256: str | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable path hash payload."""
        return {
            "path": str(self.path),
            "exists": self.exists,
            "kind": self.kind,
            "file_count": self.file_count,
            "byte_count": self.byte_count,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class GitMetadata:
    """Read-only Git metadata for a release manifest."""

    repo_root: Path
    git_commit: str | None
    git_dirty: bool | None
    git_error: str | None = None

    def to_dict(self) -> dict[str, str | bool | None]:
        """Return a JSON-serializable Git metadata payload."""
        payload: dict[str, str | bool | None] = {
            "repo_root": str(self.repo_root),
            "git_commit": self.git_commit,
            "git_dirty": self.git_dirty,
        }
        if self.git_error is not None:
            payload["git_error"] = self.git_error
        return payload


@dataclass(frozen=True)
class CheckpointMetadata:
    """Optional external backup metadata for restoring a release."""

    kind: CheckpointKind
    snapshot_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-serializable checkpoint metadata payload."""
        return {
            "kind": self.kind,
            "snapshot_id": self.snapshot_id,
        }


@dataclass(frozen=True)
class ReleaseAreaSummary:
    """Hashed summary for one release manifest area."""

    data_class: str
    exists: bool
    file_count: int
    byte_count: int
    sha256: str | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable release area payload."""
        return asdict(self)


@dataclass(frozen=True)
class ReleaseManifest:
    """Conservative release manifest describing one knowledge release."""

    schema_version: int
    release_id: str
    created_at: str
    status: ReleaseStatus
    status_reasons: list[str]
    code: GitMetadata
    checkpoint: CheckpointMetadata
    vault: GitMetadata | None
    paths: dict[str, str]
    areas: dict[str, ReleaseAreaSummary]
    counts: dict[str, int]
    retention: dict[str, int | str]
    warnings: list[str]
    output_path: Path

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable release manifest payload."""
        return {
            "schema_version": self.schema_version,
            "release_id": self.release_id,
            "created_at": self.created_at,
            "status": self.status,
            "status_reasons": list(self.status_reasons),
            "code": self.code.to_dict(),
            "checkpoint": self.checkpoint.to_dict(),
            "vault": self.vault.to_dict() if self.vault is not None else None,
            "paths": dict(sorted(self.paths.items())),
            "areas": {key: self.areas[key].to_dict() for key in sorted(self.areas)},
            "counts": dict(sorted(self.counts.items())),
            "retention": self.retention,
            "warnings": list(self.warnings),
            "output_path": str(self.output_path),
        }


def generate_release_id(*, when: datetime | None = None) -> str:
    """Return a UTC release identifier in ``YYYYMMDDTHHMMSSZ`` format."""
    moment = when or datetime.now(UTC)
    return moment.strftime("%Y%m%dT%H%M%SZ")


def release_manifest_output_path(paths: WikiPaths, release_id: str) -> Path:
    """Return the JSON output path for one release manifest."""
    return paths.release_dir / f"{release_id}.json"


def hash_path(path: Path) -> PathHash:
    """Compute a deterministic SHA-256 hash for a file or directory path."""
    if not path.exists():
        return PathHash(
            path=path,
            exists=False,
            kind="missing",
            file_count=0,
            byte_count=0,
            sha256=None,
        )
    if path.is_symlink():
        return PathHash(
            path=path,
            exists=True,
            kind="other",
            file_count=0,
            byte_count=0,
            sha256=None,
        )
    if path.is_file():
        data = path.read_bytes()
        return PathHash(
            path=path,
            exists=True,
            kind="file",
            file_count=1,
            byte_count=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
        )
    if path.is_dir():
        file_count, byte_count, digest = _hash_directory(path)
        return PathHash(
            path=path,
            exists=True,
            kind="directory",
            file_count=file_count,
            byte_count=byte_count,
            sha256=digest,
        )
    return PathHash(
        path=path,
        exists=True,
        kind="other",
        file_count=0,
        byte_count=0,
        sha256=None,
    )


def collect_git_metadata(repo_root: Path) -> GitMetadata:
    """Collect read-only Git metadata with graceful fallback."""
    root = repo_root.resolve()
    try:
        commit_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return GitMetadata(
            repo_root=root,
            git_commit=None,
            git_dirty=None,
            git_error=str(exc),
        )
    if commit_result.returncode != 0:
        error = commit_result.stderr.strip() or "git rev-parse HEAD failed"
        return GitMetadata(
            repo_root=root,
            git_commit=None,
            git_dirty=None,
            git_error=error,
        )
    git_commit = commit_result.stdout.strip() or None
    if status_result.returncode != 0:
        error = status_result.stderr.strip() or "git status --porcelain failed"
        return GitMetadata(
            repo_root=root,
            git_commit=git_commit,
            git_dirty=None,
            git_error=error,
        )
    porcelain = status_result.stdout.strip()
    return GitMetadata(
        repo_root=root,
        git_commit=git_commit,
        git_dirty=bool(porcelain),
    )


def source_text_coverage_warning(wiki_dir: Path) -> str | None:
    """Return a warning when source full-text coverage is below the render guard."""
    return _source_text_coverage_warning(wiki_dir)


def build_release_manifest(
    paths: WikiPaths,
    *,
    release_id: str | None = None,
    created_at: datetime | None = None,
    ops_status: OpsStatus | None = None,
    inventory: RetentionInventory | None = None,
    checkpoint_kind: CheckpointKind = "release",
    snapshot_id: str | None = None,
) -> ReleaseManifest:
    """Build a release manifest from resolved paths and retention inventory."""
    moment = created_at or datetime.now(UTC)
    resolved_release_id = release_id or generate_release_id(when=moment)
    created_at_text = moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    resolved_inventory = inventory or collect_retention_inventory(paths)
    inventory_by_key = {area.key: area for area in resolved_inventory.areas}
    area_hashes = {
        key: hash_path(inventory_by_key[key].path)
        for key in RELEASE_MANIFEST_AREA_KEYS
        if key in inventory_by_key
    }
    git = collect_git_metadata(paths.repo_root)
    vault = collect_git_metadata(paths.vault_root)
    source_text_warning = _source_text_coverage_warning(paths.wiki_dir)
    status, status_reasons, warnings = evaluate_release_status(
        inventory=resolved_inventory,
        area_hashes=area_hashes,
        git=git,
        ops_status=ops_status,
        source_text_warning=source_text_warning,
    )
    areas = {
        key: ReleaseAreaSummary(
            data_class=inventory_by_key[key].data_class,
            exists=area_hashes[key].exists,
            file_count=area_hashes[key].file_count,
            byte_count=area_hashes[key].byte_count,
            sha256=area_hashes[key].sha256,
        )
        for key in RELEASE_MANIFEST_AREA_KEYS
        if key in inventory_by_key
    }
    counts = _build_release_counts(
        areas,
        ops_status=ops_status,
        reviews_dir=paths.reviews_dir,
    )
    preflight = resolved_inventory.cleanup_preflight
    return ReleaseManifest(
        schema_version=SCHEMA_VERSION,
        release_id=resolved_release_id,
        created_at=created_at_text,
        status=status,
        status_reasons=status_reasons,
        code=git,
        checkpoint=CheckpointMetadata(kind=checkpoint_kind, snapshot_id=snapshot_id),
        vault=vault,
        paths=_manifest_paths(paths),
        areas=areas,
        counts=counts,
        retention={
            "temporary_file_count": preflight.temporary_file_count,
            "temporary_byte_count": preflight.temporary_byte_count,
            "cleanup_candidate_count": preflight.cleanup_candidate_count,
            "cleanup_blocked_reason": preflight.cleanup_blocked_reason,
        },
        warnings=warnings,
        output_path=release_manifest_output_path(paths, resolved_release_id),
    )


def evaluate_release_status(
    *,
    inventory: RetentionInventory,
    area_hashes: dict[str, PathHash],
    git: GitMetadata,
    ops_status: OpsStatus | None,
    source_text_warning: str | None,
) -> tuple[ReleaseStatus, list[str], list[str]]:
    """Classify release readiness from inventory, hashes, and optional ops status."""
    status_reasons: list[str] = []
    warnings = list(inventory.warnings)

    if _has_blocked_conditions(inventory, area_hashes, status_reasons):
        return "blocked", status_reasons, warnings

    warning = False
    if inventory.cleanup_preflight.temporary_file_count > 0:
        warning = True
        status_reasons.append("Temporary artifacts are present.")
    if git.git_dirty is True:
        warning = True
        status_reasons.append("Git worktree has uncommitted changes.")
    if ops_status is not None:
        warning = warning or _append_ops_status_warnings(ops_status, status_reasons)
    if source_text_warning is not None:
        warning = True
        status_reasons.append(source_text_warning)

    if warning:
        return "warning", status_reasons, warnings
    return "ready", status_reasons, warnings


def format_release_dry_run_text(manifest: ReleaseManifest, paths: WikiPaths) -> str:
    """Render a concise human-readable release manifest preview."""
    inventory = collect_retention_inventory(paths)
    lines = [
        "Release Manifest Preview",
        f"- release id: {manifest.release_id}",
        f"- status: {manifest.status}",
    ]
    for data_class in ("canonical", "generated", "temporary"):
        totals = inventory.totals_by_class.get(data_class, {"areas": 0, "files": 0, "bytes": 0})
        lines.append(
            f"- {data_class}: {totals['areas']} areas, {totals['files']} files, "
            f"{_format_bytes(totals['bytes'])}"
        )
    temporary_count = manifest.retention["temporary_file_count"]
    if isinstance(temporary_count, int):
        lines.append(f"- temporary artifacts: {temporary_count} files")
    try:
        output = manifest.output_path.relative_to(paths.repo_root)
    except ValueError:
        output = manifest.output_path
    lines.append(f"- output path: {output}")
    if manifest.status_reasons:
        lines.append("")
        lines.append("Status reasons")
        lines.extend(f"- {reason}" for reason in manifest.status_reasons)
    if manifest.warnings:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in manifest.warnings)
    return "\n".join(lines)


def write_release_manifest(
    manifest: ReleaseManifest,
    *,
    overwrite: bool = False,
) -> Path:
    """Write one release manifest JSON file to disk."""
    output_path = manifest.output_path
    if output_path.exists() and not overwrite:
        msg = f"Release manifest already exists: {output_path}"
        raise FileExistsError(msg)
    atomic_write_json(output_path, manifest.to_dict())
    return output_path


def _build_release_counts(
    areas: dict[str, ReleaseAreaSummary],
    *,
    ops_status: OpsStatus | None,
    reviews_dir: Path,
) -> dict[str, int]:
    """Build semantic release counts for manifest summaries."""
    reviews_count = (
        ops_status.reviews.artifacts
        if ops_status is not None
        else collect_review_status(reviews_dir).artifacts
    )
    return {
        "raw_files": areas["raw_readwise"].file_count,
        "reviews": reviews_count,
        "synthesis_entries": areas["synthesis_cache"].file_count,
        "wiki_files": areas["wiki"].file_count,
    }


def _manifest_paths(paths: WikiPaths) -> dict[str, str]:
    """Return the path subset included in release manifests."""
    return {
        "raw_dir": str(paths.raw_dir),
        "reviews_dir": str(paths.reviews_dir),
        "synthesis_dir": str(paths.synthesis_dir),
        "wiki_dir": str(paths.wiki_dir),
        "graph_path": str(paths.graph_path),
        "manifest_path": str(paths.manifest_path),
        "release_dir": str(paths.release_dir),
    }


def _hash_directory(path: Path) -> tuple[int, int, str]:
    """Hash a directory tree deterministically without following symlinked directories."""
    hasher = hashlib.sha256()
    entries: list[tuple[str, str, int]] = []
    file_count = 0
    byte_count = 0
    for root, dirnames, filenames in os.walk(path, followlinks=False):
        root_path = Path(root)
        dirnames[:] = [name for name in dirnames if not (root_path / name).is_symlink()]
        for filename in filenames:
            file_path = root_path / filename
            if file_path.is_symlink():
                continue
            relative = file_path.relative_to(path).as_posix()
            data = file_path.read_bytes()
            entries.append((relative, hashlib.sha256(data).hexdigest(), len(data)))
    for relative, file_hash, size in sorted(entries, key=lambda item: item[0]):
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(file_hash.encode("ascii"))
        hasher.update(b"\0")
        hasher.update(str(size).encode("ascii"))
        hasher.update(b"\n")
        file_count += 1
        byte_count += size
    return file_count, byte_count, hasher.hexdigest()


def _has_blocked_conditions(
    inventory: RetentionInventory,
    area_hashes: dict[str, PathHash],
    status_reasons: list[str],
) -> bool:
    """Return whether required release data is missing."""
    blocked = False
    for warning in inventory.warnings:
        if warning.startswith("Canonical path missing:"):
            blocked = True
            status_reasons.append(warning)
    for key in ("render_graph", "render_manifest"):
        path_hash = area_hashes.get(key)
        if path_hash is None or not path_hash.exists or path_hash.kind == "missing":
            blocked = True
            status_reasons.append(f"Required generated path missing: {key}.")
    wiki = area_hashes.get("wiki")
    if wiki is None or not wiki.exists or wiki.file_count == 0:
        blocked = True
        status_reasons.append("Wiki directory is missing or empty.")
    raw = area_hashes.get("raw_readwise")
    if raw is None or not raw.exists or raw.file_count == 0:
        blocked = True
        status_reasons.append("Raw source directory is missing or empty.")
    reviews = area_hashes.get("reviews")
    if reviews is None or not reviews.exists or reviews.file_count == 0:
        blocked = True
        status_reasons.append("Review directory is missing or empty.")
    synthesis = area_hashes.get("synthesis_cache")
    if synthesis is None or not synthesis.exists:
        blocked = True
        status_reasons.append("Synthesis cache directory is missing.")
    return blocked


def _append_ops_status_warnings(ops_status: OpsStatus, status_reasons: list[str]) -> bool:
    """Append ops-status-derived warning reasons and return whether any were added."""
    warning = False
    uncommitted = (
        ops_status.artifacts.uncommitted_durable
        + ops_status.artifacts.uncommitted_synthesis_cache
        + ops_status.artifacts.uncommitted_render_outputs
        + ops_status.artifacts.uncommitted_previews
        + ops_status.artifacts.uncommitted_runs
        + ops_status.artifacts.uncommitted_backups
        + ops_status.artifacts.uncommitted_other
    )
    if uncommitted > 0:
        warning = True
        status_reasons.append(f"Uncommitted files detected ({uncommitted}).")
    if ops_status.synthesis.stale and ops_status.synthesis.stale > 0:
        warning = True
        status_reasons.append("Stale synthesis cache entries are present.")
    if ops_status.synthesis.errors and ops_status.synthesis.errors > 0:
        warning = True
        status_reasons.append("Synthesis cache lint reported errors.")
    return warning


def _source_text_coverage_warning(wiki_dir: Path) -> str | None:
    """Return a warning when source full-text coverage is below the render guard."""
    sources_dir = wiki_dir / "sources"
    if not sources_dir.is_dir():
        return None
    total = 0
    available = 0
    for path in sorted(sources_dir.glob("*.md")):
        if path.name == "index.md":
            continue
        total += 1
        frontmatter = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter.get("source_text_available") is True:
            available += 1
    if total == 0:
        return None
    ratio = available / total
    if ratio >= 0.5:
        return None
    return (
        "Low source full-text coverage: "
        f"{available}/{total} source pages have source_text_available=true "
        f"({ratio:.1%})."
    )


def _parse_frontmatter(text: str) -> dict[str, object]:
    """Parse YAML frontmatter from a markdown document."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        payload = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _format_bytes(byte_count: int) -> str:
    """Format a byte count for human-readable output."""
    if byte_count < 1024:
        return f"{byte_count} B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f} KB"
    if byte_count < 1024 * 1024 * 1024:
        return f"{byte_count / (1024 * 1024):.1f} MB"
    return f"{byte_count / (1024 * 1024 * 1024):.1f} GB"
