"""Read-only release manifest verification for wiki knowledge stores."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.wiki_ops.release_manifest import (
    RELEASE_MANIFEST_AREA_KEYS,
    SCHEMA_VERSION,
    hash_path,
)
from src.wiki_paths.config import WikiPaths

VerificationStatus = Literal["ok", "warning", "error"]

MANIFEST_PATH_KEY_BY_AREA: dict[str, str] = {
    "raw_readwise": "raw_dir",
    "reviews": "reviews_dir",
    "synthesis_cache": "synthesis_dir",
    "render_graph": "graph_path",
    "render_manifest": "manifest_path",
    "wiki": "wiki_dir",
}


class ReleaseSelectionError(Exception):
    """Raised when a release manifest cannot be selected."""


@dataclass(frozen=True)
class ReleaseAreaVerification:
    """Verification result for one release manifest area."""

    area_key: str
    expected_path: Path | None
    current_path: Path | None
    expected_exists: bool
    current_exists: bool
    expected_file_count: int
    current_file_count: int
    expected_byte_count: int
    current_byte_count: int
    expected_sha256: str | None
    current_sha256: str | None
    status: VerificationStatus
    messages: list[str]


@dataclass(frozen=True)
class ReleaseVerificationReport:
    """Read-only verification report for one release manifest."""

    schema_version: int
    release_id: str
    manifest_path: Path
    checked_at: datetime
    status: VerificationStatus
    manifest_status: str | None
    path_status: VerificationStatus
    area_results: list[ReleaseAreaVerification]
    messages: list[str]


def select_release_manifest_path(paths: WikiPaths, selector: str) -> Path:
    """Return the release manifest path for ``latest`` or an explicit release id."""
    release_dir = paths.release_dir
    if selector == "latest":
        if not release_dir.is_dir():
            msg = f"No release manifests found: {release_dir} does not exist."
            raise ReleaseSelectionError(msg)
        manifests = sorted(release_dir.glob("*.json"))
        if not manifests:
            msg = f"No release manifests found in {release_dir}."
            raise ReleaseSelectionError(msg)
        return manifests[-1]
    manifest_path = release_dir / f"{selector}.json"
    if not manifest_path.is_file():
        msg = f"Release manifest not found: {manifest_path}"
        raise ReleaseSelectionError(msg)
    return manifest_path


def verify_release(
    paths: WikiPaths,
    *,
    selector: str,
    allow_path_mismatch: bool = False,
    checked_at: datetime | None = None,
) -> ReleaseVerificationReport:
    """Verify current knowledge store state against one release manifest."""
    moment = checked_at or datetime.now(UTC)
    manifest_path = select_release_manifest_path(paths, selector)
    release_id = manifest_path.stem
    payload, load_error = _load_manifest_payload(manifest_path)
    if load_error is not None:
        return _error_report(
            release_id=release_id,
            manifest_path=manifest_path,
            checked_at=moment,
            messages=[load_error],
        )
    assert payload is not None
    schema_version = payload.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        return _error_report(
            release_id=release_id,
            manifest_path=manifest_path,
            checked_at=moment,
            manifest_status=_manifest_status(payload),
            messages=[f"Unsupported release manifest schema version: {schema_version!r}."],
        )

    manifest_paths = payload.get("paths")
    manifest_areas = payload.get("areas")
    if not isinstance(manifest_paths, dict) or not isinstance(manifest_areas, dict):
        return _error_report(
            release_id=release_id,
            manifest_path=manifest_path,
            checked_at=moment,
            manifest_status=_manifest_status(payload),
            messages=["Release manifest is missing paths or areas."],
        )

    messages: list[str] = []
    manifest_status = _manifest_status(payload)
    area_results: list[ReleaseAreaVerification] = []
    for area_key in RELEASE_MANIFEST_AREA_KEYS:
        expected_area = manifest_areas.get(area_key)
        if not isinstance(expected_area, dict):
            area_results.append(
                _missing_required_area_verification(
                    area_key,
                    paths=paths,
                    manifest_paths=manifest_paths,
                )
            )
            continue
        area_results.append(
            _verify_area(
                area_key,
                expected_area=expected_area,
                paths=paths,
                manifest_paths=manifest_paths,
                allow_path_mismatch=allow_path_mismatch,
            )
        )

    for area_key, expected_area in manifest_areas.items():
        if area_key in RELEASE_MANIFEST_AREA_KEYS:
            continue
        if isinstance(expected_area, dict):
            messages.append(f"Manifest contains unknown area: {area_key}.")

    path_status = _aggregate_path_status(area_results)
    status = _aggregate_status(
        area_results=area_results,
        manifest_status=manifest_status,
        path_status=path_status,
        messages=messages,
    )
    messages.extend(_manifest_status_messages(manifest_status, payload))

    return ReleaseVerificationReport(
        schema_version=SCHEMA_VERSION,
        release_id=release_id,
        manifest_path=manifest_path,
        checked_at=moment,
        status=status,
        manifest_status=manifest_status,
        path_status=path_status,
        area_results=area_results,
        messages=_dedupe_preserve_order(messages),
    )


def release_verification_to_json(report: ReleaseVerificationReport) -> dict[str, object]:
    """Return a JSON-serializable release verification payload."""
    return {
        "schema_version": report.schema_version,
        "release_id": report.release_id,
        "manifest_path": str(report.manifest_path),
        "checked_at": report.checked_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": report.status,
        "manifest_status": report.manifest_status,
        "path_status": report.path_status,
        "messages": list(report.messages),
        "areas": [
            {
                "area_key": area.area_key,
                "expected_path": (
                    str(area.expected_path) if area.expected_path is not None else None
                ),
                "current_path": (str(area.current_path) if area.current_path is not None else None),
                "expected_exists": area.expected_exists,
                "current_exists": area.current_exists,
                "expected_file_count": area.expected_file_count,
                "current_file_count": area.current_file_count,
                "expected_byte_count": area.expected_byte_count,
                "current_byte_count": area.current_byte_count,
                "expected_sha256": area.expected_sha256,
                "current_sha256": area.current_sha256,
                "status": area.status,
                "messages": list(area.messages),
            }
            for area in report.area_results
        ],
    }


def format_release_verification_text(report: ReleaseVerificationReport) -> str:
    """Render a concise human-readable release verification report."""
    lines = [
        "Release Verification",
        f"- release: {report.release_id}",
        f"- manifest: {report.manifest_path}",
        f"- status: {report.status}",
    ]
    if report.manifest_status is not None:
        lines.append(f"- manifest status: {report.manifest_status}")
    lines.append("")
    lines.append("Areas")
    for area in report.area_results:
        if area.status == "ok":
            lines.append(
                f"- {area.area_key}: ok, {area.current_file_count} files, "
                f"{_format_bytes(area.current_byte_count)}"
            )
        else:
            summary = area.messages[0] if area.messages else area.status
            lines.append(f"- {area.area_key}: {area.status}, {summary}")
    if report.messages:
        lines.append("")
        lines.append("Messages")
        lines.extend(f"- {message}" for message in report.messages)
    return "\n".join(lines)


def _verify_area(
    area_key: str,
    *,
    expected_area: dict[str, Any],
    paths: WikiPaths,
    manifest_paths: dict[str, Any],
    allow_path_mismatch: bool,
) -> ReleaseAreaVerification:
    """Compare one manifest area against the current resolved path."""
    current_path = _current_path_for_area(area_key, paths)
    path_key = MANIFEST_PATH_KEY_BY_AREA[area_key]
    expected_path_raw = manifest_paths.get(path_key)
    expected_exists = bool(expected_area.get("exists"))
    expected_file_count = _int_value(expected_area.get("file_count"))
    expected_byte_count = _int_value(expected_area.get("byte_count"))
    expected_sha256 = _optional_str(expected_area.get("sha256"))

    current_hash = hash_path(current_path)
    current_exists = current_hash.exists
    current_file_count = current_hash.file_count
    current_byte_count = current_hash.byte_count
    current_sha256 = current_hash.sha256

    messages: list[str] = []
    status: VerificationStatus = "ok"
    if path_key not in manifest_paths or expected_path_raw is None:
        messages.append("Required manifest path is missing.")
        status = "error"
        expected_path = None
    else:
        expected_path = Path(str(expected_path_raw))
        paths_match = _paths_match(expected_path, current_path)
        if not paths_match:
            if allow_path_mismatch:
                messages.append("Path differs from manifest.")
                status = "warning"
            else:
                messages.append("Path differs from manifest.")
                status = "error"

    if expected_exists and not current_exists:
        messages.append("Current path is missing.")
        status = "error"
    if current_file_count != expected_file_count:
        messages.append("File count differs.")
        status = "error"
    if current_byte_count != expected_byte_count:
        messages.append("Byte count differs.")
        status = "error"
    if expected_sha256 != current_sha256:
        if current_sha256 is None and current_exists:
            messages.append("Current path hash could not be computed.")
        else:
            messages.append("sha256 differs.")
        status = "error"

    if status == "warning" and any(
        message in {"File count differs.", "Byte count differs.", "sha256 differs."}
        for message in messages
    ):
        status = "error"

    return ReleaseAreaVerification(
        area_key=area_key,
        expected_path=expected_path,
        current_path=current_path,
        expected_exists=expected_exists,
        current_exists=current_exists,
        expected_file_count=expected_file_count,
        current_byte_count=current_byte_count,
        expected_byte_count=expected_byte_count,
        current_file_count=current_file_count,
        expected_sha256=expected_sha256,
        current_sha256=current_sha256,
        status=status,
        messages=messages,
    )


def _missing_required_area_verification(
    area_key: str,
    *,
    paths: WikiPaths,
    manifest_paths: dict[str, Any],
) -> ReleaseAreaVerification:
    """Return an error result when a required manifest area is absent."""
    current_path = _current_path_for_area(area_key, paths)
    path_key = MANIFEST_PATH_KEY_BY_AREA[area_key]
    expected_path_raw = manifest_paths.get(path_key)
    expected_path = Path(str(expected_path_raw)) if expected_path_raw is not None else None
    current_hash = hash_path(current_path)
    return ReleaseAreaVerification(
        area_key=area_key,
        expected_path=expected_path,
        current_path=current_path,
        expected_exists=False,
        current_exists=current_hash.exists,
        expected_file_count=0,
        current_file_count=current_hash.file_count,
        expected_byte_count=0,
        current_byte_count=current_hash.byte_count,
        expected_sha256=None,
        current_sha256=current_hash.sha256,
        status="error",
        messages=["Required manifest area is missing."],
    )


def _current_path_for_area(area_key: str, paths: WikiPaths) -> Path:
    """Return the current resolved path for one manifest area key."""
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
    msg = f"Unknown release area key: {area_key}"
    raise ValueError(msg)


def _load_manifest_payload(manifest_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Load one release manifest JSON payload."""
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"Release manifest is malformed: {exc}."
    if not isinstance(payload, dict):
        return None, "Release manifest must be a JSON object."
    return payload, None


def _error_report(
    *,
    release_id: str,
    manifest_path: Path,
    checked_at: datetime,
    messages: list[str],
    manifest_status: str | None = None,
) -> ReleaseVerificationReport:
    """Build an error report when manifest loading or parsing fails."""
    return ReleaseVerificationReport(
        schema_version=SCHEMA_VERSION,
        release_id=release_id,
        manifest_path=manifest_path,
        checked_at=checked_at,
        status="error",
        manifest_status=manifest_status,
        path_status="error",
        area_results=[],
        messages=messages,
    )


def _manifest_status(payload: dict[str, Any]) -> str | None:
    """Return manifest status text when present."""
    status = payload.get("status")
    return status if isinstance(status, str) else None


def _manifest_status_messages(manifest_status: str | None, payload: dict[str, Any]) -> list[str]:
    """Return report-level messages derived from manifest status metadata."""
    if manifest_status is None:
        return []
    messages = [f"Manifest status is {manifest_status}."]
    status_reasons = payload.get("status_reasons")
    if isinstance(status_reasons, list):
        for reason in status_reasons:
            if isinstance(reason, str) and reason:
                messages.append(reason)
    return messages


def _aggregate_path_status(area_results: list[ReleaseAreaVerification]) -> VerificationStatus:
    """Aggregate path comparison status across all areas."""
    if any(
        message in {"Path differs from manifest.", "Required manifest path is missing."}
        and area.status == "error"
        for area in area_results
        for message in area.messages
    ):
        return "error"
    if any(
        "Path differs from manifest." in message
        for area in area_results
        for message in area.messages
    ):
        return "warning"
    return "ok"


def _aggregate_status(
    *,
    area_results: list[ReleaseAreaVerification],
    manifest_status: str | None,
    path_status: VerificationStatus,
    messages: list[str],
) -> VerificationStatus:
    """Compute overall verification status."""
    if any(area.status == "error" for area in area_results):
        return "error"
    if path_status == "error":
        return "error"
    warning = bool(messages) or any(area.status == "warning" for area in area_results)
    if manifest_status in {"warning", "blocked"}:
        warning = True
    if path_status == "warning":
        warning = True
    if warning:
        return "warning"
    return "ok"


def _paths_match(expected_path: Path | None, current_path: Path) -> bool:
    """Return whether two paths refer to the same filesystem location."""
    if expected_path is None:
        return True
    try:
        return expected_path.resolve() == current_path.resolve()
    except OSError:
        return str(expected_path) == str(current_path)


def _int_value(value: object) -> int:
    """Coerce one integer-like manifest field."""
    if isinstance(value, int):
        return value
    return 0


def _optional_str(value: object) -> str | None:
    """Coerce one optional string manifest field."""
    return value if isinstance(value, str) else None


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
