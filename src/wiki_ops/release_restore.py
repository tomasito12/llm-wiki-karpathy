"""Restore a knowledge release from an external filesystem snapshot.

This module is intentionally conservative:

- restore is opt-in via CLI and requires explicit --yes unless dry-run
- restore is fail-closed unless the selected release manifest records a snapshot id
- restore is limited to replacing selected paths from a snapshot directory
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.wiki_ops.release_manifest import RELEASE_MANIFEST_AREA_KEYS, SCHEMA_VERSION
from src.wiki_ops.release_verify import ReleaseSelectionError, verify_release
from src.wiki_paths.config import WikiPaths

RestoreStatus = Literal["planned", "executed"]


class ReleaseRestoreError(Exception):
    """Raised when a release restore cannot be planned or executed."""


@dataclass(frozen=True)
class RestoreItem:
    """One filesystem path to be restored from snapshot -> destination."""

    area_key: str
    source_path: Path
    destination_path: Path
    kind: Literal["file", "directory"]


@dataclass(frozen=True)
class ReleaseRestorePlan:
    """A restore plan for one release selector and snapshot root."""

    schema_version: int
    release_id: str
    manifest_path: Path
    snapshot_id: str
    snapshot_root: Path
    common_root: Path
    created_at: datetime
    dry_run: bool
    status: RestoreStatus
    items: list[RestoreItem]
    messages: list[str]


def restore_release_from_snapshot(
    paths: WikiPaths,
    *,
    selector: str,
    snapshot_root: Path,
    area_selector: list[str],
    dry_run: bool,
    allow_verify_path_mismatch: bool = False,
    now: datetime | None = None,
):
    """Plan and optionally execute a restore, then verify against the manifest."""
    moment = now or datetime.now(UTC)
    manifest_path = _select_manifest_path(paths, selector)
    payload = _load_manifest(manifest_path)
    schema_version = payload.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        msg = f"Unsupported release manifest schema version: {schema_version!r}."
        raise ReleaseRestoreError(msg)

    checkpoint = payload.get("checkpoint")
    if not isinstance(checkpoint, dict):
        raise ReleaseRestoreError("Release manifest is missing checkpoint metadata.")
    snapshot_id = checkpoint.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id.strip():
        raise ReleaseRestoreError(
            "Release manifest does not record a snapshot_id; refusing to restore.",
        )

    resolved_areas = _normalize_area_selector(area_selector)
    common_root = _common_root(paths.knowledge_root, paths.vault_root)
    items: list[RestoreItem] = []
    messages: list[str] = []
    for area_key in resolved_areas:
        destination_path = _current_path_for_area(area_key, paths)
        source_path = _snapshot_source_path(
            snapshot_root,
            common_root=common_root,
            destination_path=destination_path,
        )
        kind = "file" if destination_path.suffix else "directory"
        if destination_path.is_file():
            kind = "file"
        if destination_path.is_dir():
            kind = "directory"
        if source_path.is_file():
            kind = "file"
        if source_path.is_dir():
            kind = "directory"
        items.append(
            RestoreItem(
                area_key=area_key,
                source_path=source_path,
                destination_path=destination_path,
                kind=kind,
            )
        )

    plan = ReleaseRestorePlan(
        schema_version=SCHEMA_VERSION,
        release_id=manifest_path.stem,
        manifest_path=manifest_path,
        snapshot_id=snapshot_id.strip(),
        snapshot_root=snapshot_root.resolve(),
        common_root=common_root,
        created_at=moment,
        dry_run=dry_run,
        status="planned",
        items=items,
        messages=messages,
    )

    if dry_run:
        return plan, None

    _execute_plan(plan)
    executed = _replace(plan, status="executed")
    report = verify_release(
        paths,
        selector=executed.release_id,
        allow_path_mismatch=allow_verify_path_mismatch,
    )
    return executed, report


def release_restore_plan_to_json(
    plan: ReleaseRestorePlan,
    *,
    verify_report: object | None,
) -> dict[str, object]:
    """Return a JSON-serializable restore payload."""
    payload: dict[str, object] = {
        "schema_version": plan.schema_version,
        "release_id": plan.release_id,
        "manifest_path": str(plan.manifest_path),
        "snapshot_id": plan.snapshot_id,
        "snapshot_root": str(plan.snapshot_root),
        "common_root": str(plan.common_root),
        "created_at": plan.created_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "dry_run": plan.dry_run,
        "status": plan.status,
        "messages": list(plan.messages),
        "items": [
            {
                "area_key": item.area_key,
                "kind": item.kind,
                "source_path": str(item.source_path),
                "destination_path": str(item.destination_path),
            }
            for item in plan.items
        ],
    }
    if verify_report is not None:
        payload["verify_report"] = verify_report
    return payload


def format_release_restore_plan_text(plan: ReleaseRestorePlan) -> str:
    """Render a concise human-readable restore plan."""
    lines = [
        "Release Restore",
        f"- release: {plan.release_id}",
        f"- snapshot id: {plan.snapshot_id}",
        f"- snapshot root: {plan.snapshot_root}",
        f"- dry-run: {plan.dry_run}",
        f"- status: {plan.status}",
        "",
        "Areas",
    ]
    for item in plan.items:
        lines.append(f"- {item.area_key}: {item.kind}, {item.destination_path}")
    if plan.messages:
        lines.append("")
        lines.append("Messages")
        lines.extend(f"- {msg}" for msg in plan.messages)
    return "\n".join(lines)


def _select_manifest_path(paths: WikiPaths, selector: str) -> Path:
    """Select one manifest path, surfacing selection errors as restore errors."""
    try:
        from src.wiki_ops.release_verify import select_release_manifest_path

        return select_release_manifest_path(paths, selector)
    except ReleaseSelectionError as exc:
        raise ReleaseRestoreError(str(exc)) from exc


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load a release manifest JSON payload."""
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReleaseRestoreError(f"Failed to read release manifest: {exc}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReleaseRestoreError(f"Release manifest is malformed: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleaseRestoreError("Release manifest must be a JSON object.")
    return payload


def _normalize_area_selector(area_selector: list[str]) -> list[str]:
    """Normalize comma-split area selector parts into a list of valid area keys."""
    if any(part == "all" for part in area_selector):
        return list(RELEASE_MANIFEST_AREA_KEYS)
    resolved: list[str] = []
    for part in area_selector:
        for token in str(part).split(","):
            value = token.strip()
            if not value:
                continue
            if value not in RELEASE_MANIFEST_AREA_KEYS:
                raise ReleaseRestoreError(f"Unknown restore area: {value}")
            if value not in resolved:
                resolved.append(value)
    if not resolved:
        raise ReleaseRestoreError("No restore areas selected.")
    return resolved


def _common_root(knowledge_root: Path, vault_root: Path) -> Path:
    """Return the common filesystem root containing both knowledge and vault roots."""
    try:
        common = os.path.commonpath([str(knowledge_root.resolve()), str(vault_root.resolve())])
    except OSError as exc:
        raise ReleaseRestoreError(f"Failed to compute common root: {exc}") from exc
    return Path(common)


def _snapshot_source_path(
    snapshot_root: Path,
    *,
    common_root: Path,
    destination_path: Path,
) -> Path:
    """Map a destination path to the corresponding location in a snapshot."""
    try:
        relative = destination_path.resolve().relative_to(common_root.resolve())
    except (OSError, ValueError) as exc:
        raise ReleaseRestoreError(
            f"Destination path is outside the common root: {destination_path}",
        ) from exc
    return snapshot_root.resolve() / relative


def _current_path_for_area(area_key: str, paths: WikiPaths) -> Path:
    """Return the current resolved path for one release manifest area key."""
    if area_key == "raw_readwise":
        return paths.raw_dir
    if area_key == "reviews":
        return paths.reviews_dir
    if area_key == "synthesis_cache":
        return paths.synthesis_dir
    if area_key == "render_graph":
        return paths.graph_path
    if area_key == "render_manifest":
        return paths.manifest_path
    if area_key == "wiki":
        return paths.wiki_dir
    raise ReleaseRestoreError(f"Unknown release area key: {area_key}")


def _execute_plan(plan: ReleaseRestorePlan) -> None:
    """Execute a restore plan by replacing destination paths with snapshot copies."""
    if not plan.snapshot_root.is_dir():
        raise ReleaseRestoreError(f"Snapshot root does not exist: {plan.snapshot_root}")
    for item in plan.items:
        if item.kind == "file":
            _replace_file(item.source_path, item.destination_path)
        else:
            _replace_directory(item.source_path, item.destination_path)


def _replace_file(source_path: Path, destination_path: Path) -> None:
    """Replace a destination file with a snapshot file."""
    if not source_path.is_file():
        raise ReleaseRestoreError(f"Snapshot file missing: {source_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    data = source_path.read_bytes()
    destination_path.write_bytes(data)


def _replace_directory(source_path: Path, destination_path: Path) -> None:
    """Replace a destination directory with a snapshot directory."""
    if not source_path.is_dir():
        raise ReleaseRestoreError(f"Snapshot directory missing: {source_path}")
    parent = destination_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    temp_dir = parent / f".restore_tmp_{destination_path.name}_{os.getpid()}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    shutil.copytree(source_path, temp_dir)
    if destination_path.exists():
        shutil.rmtree(destination_path)
    temp_dir.rename(destination_path)


def _replace(plan: ReleaseRestorePlan, **kwargs: object) -> ReleaseRestorePlan:
    """Return a modified copy of a frozen dataclass."""
    payload = asdict(plan)
    payload.update(kwargs)
    payload["manifest_path"] = plan.manifest_path
    payload["snapshot_root"] = plan.snapshot_root
    payload["common_root"] = plan.common_root
    payload["created_at"] = plan.created_at
    payload["items"] = plan.items
    return ReleaseRestorePlan(**payload)
