"""Read-only knowledge store migration planning."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.wiki_ops.release_manifest import source_text_coverage_warning
from src.wiki_ops.retention import (
    DataClass,
    RetentionInventory,
    artifact_area_definitions,
    collect_retention_inventory,
    inventory_area,
)
from src.wiki_ops.status import OpsStatus, build_recommendations
from src.wiki_paths.config import WikiPaths

MIGRATION_PLAN_SCHEMA_VERSION = 1

CurrentLocation = Literal["code_repo", "knowledge_store", "vault", "external", "missing"]
TargetLocation = Literal["code_repo", "knowledge_store", "vault", "none"]
MigrationAction = Literal[
    "keep_in_code_repo",
    "copy_to_knowledge_store",
    "copy_to_vault",
    "already_external",
    "cleanup_candidate",
    "ignore_missing",
    "manual_decision_required",
]
ReadinessStatus = Literal["ready", "warning", "blocked"]
AreaStatus = Literal["ok", "warning", "blocked"]


@dataclass(frozen=True)
class MigrationAreaPlan:
    """Migration classification for one managed path area."""

    area_key: str
    current_path: Path
    target_path: Path | None
    current_location: CurrentLocation
    target_location: TargetLocation
    data_class: str
    migration_action: MigrationAction
    exists: bool
    file_count: int
    byte_count: int
    status: AreaStatus
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable migration area payload."""
        payload = asdict(self)
        payload["current_path"] = str(self.current_path)
        payload["target_path"] = str(self.target_path) if self.target_path is not None else None
        return payload


@dataclass(frozen=True)
class MigrationReadiness:
    """Overall migration readiness summary."""

    status: ReadinessStatus
    blocked_reasons: list[str]
    warnings: list[str]
    recommended_next_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable readiness payload."""
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeStoreMigrationPlan:
    """Read-only knowledge store migration plan."""

    schema_version: int
    created_at: datetime
    repo_root: Path
    knowledge_root: Path
    vault_root: Path
    areas: list[MigrationAreaPlan]
    readiness: MigrationReadiness

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable migration plan payload."""
        return migration_plan_to_json(self)


def build_migration_plan(
    paths: WikiPaths,
    *,
    require_external_knowledge_root: bool = False,
    require_external_vault_root: bool = False,
    ops_status: OpsStatus | None = None,
    retention: RetentionInventory | None = None,
    created_at: datetime | None = None,
) -> KnowledgeStoreMigrationPlan:
    """Build a read-only knowledge store migration plan."""
    moment = created_at or datetime.now(UTC)
    resolved_retention = retention or collect_retention_inventory(paths)
    retention_by_key = {area.key: area for area in resolved_retention.areas}
    areas = _build_migration_areas(paths, retention_by_key, ops_status=ops_status)
    readiness = _evaluate_readiness(
        paths,
        areas=areas,
        retention=resolved_retention,
        ops_status=ops_status,
        require_external_knowledge_root=require_external_knowledge_root,
        require_external_vault_root=require_external_vault_root,
    )
    return KnowledgeStoreMigrationPlan(
        schema_version=MIGRATION_PLAN_SCHEMA_VERSION,
        created_at=moment,
        repo_root=paths.repo_root,
        knowledge_root=paths.knowledge_root,
        vault_root=paths.vault_root,
        areas=areas,
        readiness=readiness,
    )


def migration_plan_to_json(plan: KnowledgeStoreMigrationPlan) -> dict[str, object]:
    """Serialize a migration plan to a JSON-compatible mapping."""
    return {
        "schema_version": plan.schema_version,
        "created_at": plan.created_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "roots": {
            "repo_root": str(plan.repo_root),
            "knowledge_root": str(plan.knowledge_root),
            "vault_root": str(plan.vault_root),
        },
        "readiness": plan.readiness.to_dict(),
        "areas": [area.to_dict() for area in plan.areas],
    }


def format_migration_plan_text(plan: KnowledgeStoreMigrationPlan) -> str:
    """Render a concise human-readable migration plan section."""
    lines = [
        "Knowledge Store Migration Plan",
        "",
        f"Readiness: {plan.readiness.status}",
        "",
        "Roots",
        f"- repo: {plan.repo_root}",
        f"- knowledge: {plan.knowledge_root}",
        f"- vault: {plan.vault_root}",
        "",
        "Areas",
    ]
    for area in plan.areas:
        size = _format_bytes(area.byte_count)
        lines.append(f"- {area.area_key}: {area.migration_action}, {area.file_count} files, {size}")
    if plan.readiness.warnings:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in plan.readiness.warnings)
    if plan.readiness.recommended_next_actions:
        lines.append("")
        lines.append("Recommended next actions")
        for index, action in enumerate(plan.readiness.recommended_next_actions, start=1):
            lines.append(f"{index}. {action}")
    return "\n".join(lines)


def _build_migration_areas(
    paths: WikiPaths,
    retention_by_key: dict[str, Any],
    *,
    ops_status: OpsStatus | None = None,
) -> list[MigrationAreaPlan]:
    """Build migration area plans from retention inventory and code paths."""
    specs = _migration_area_specs(paths)
    areas: list[MigrationAreaPlan] = []
    for spec in specs:
        retention_key = spec.get("retention_key", spec["area_key"])
        retention_area = retention_by_key.get(retention_key)
        if retention_area is not None:
            current_path = retention_area.path
            exists = retention_area.exists
            file_count = retention_area.file_count
            byte_count = retention_area.byte_count
            data_class = retention_area.data_class
            area_warnings = list(retention_area.warnings)
        else:
            current_path = spec["current_path"](paths)
            stats = inventory_area(
                _definition_for_path(spec["area_key"], current_path, spec["data_class"])
            )
            exists = stats.exists
            file_count = stats.file_count
            byte_count = stats.byte_count
            data_class = spec["data_class"]
            area_warnings = list(stats.warnings)
        target_path = spec["target_path"](paths)
        current_location = classify_current_location(current_path, paths)
        target_location = spec["target_location"]
        migration_action = _migration_action_for_area(
            current_location=current_location,
            target_location=target_location,
            spec_action=spec["action"],
            exists=exists,
            optional=spec.get("optional", False),
        )
        status = _area_status(
            exists=exists,
            optional=spec.get("optional", False),
            data_class=data_class,
            target_location=target_location,
            area_warnings=area_warnings,
            migration_action=migration_action,
        )
        empty_warnings, status_override = _empty_canonical_checks(
            spec["area_key"],
            exists=exists,
            file_count=file_count,
            ops_status=ops_status,
        )
        area_warnings.extend(empty_warnings)
        if status_override is not None:
            status = status_override
        elif empty_warnings and status == "ok":
            status = "warning"
        areas.append(
            MigrationAreaPlan(
                area_key=spec["area_key"],
                current_path=current_path,
                target_path=target_path,
                current_location=current_location,
                target_location=target_location,
                data_class=data_class,
                migration_action=migration_action,
                exists=exists,
                file_count=file_count,
                byte_count=byte_count,
                status=status,
                warnings=area_warnings,
            )
        )
    return areas


def classify_current_location(path: Path, paths: WikiPaths) -> CurrentLocation:
    """Classify where a path currently lives relative to known roots."""
    if not path.exists():
        return "missing"
    resolved = path.resolve()
    repo = paths.repo_root.resolve()
    knowledge = paths.knowledge_root.resolve()
    vault = paths.vault_root.resolve()
    if knowledge != repo and _path_is_relative_to(resolved, knowledge):
        return "knowledge_store"
    if vault != repo and _path_is_relative_to(resolved, vault):
        return "vault"
    if _path_is_relative_to(resolved, repo):
        return "code_repo"
    return "external"


def detect_path_overlaps(paths: WikiPaths) -> list[str]:
    """Detect unsafe or ambiguous path relationships."""
    overlaps: list[str] = []
    knowledge = paths.knowledge_root.resolve()
    vault = paths.vault_root.resolve()
    if knowledge != vault:
        if _path_is_relative_to(knowledge, vault):
            overlaps.append("knowledge_root is inside vault_root.")
        if _path_is_relative_to(vault, knowledge):
            overlaps.append("vault_root is inside knowledge_root.")
    nested_pairs = (
        (paths.raw_dir, paths.wiki_dir, "raw_dir is inside wiki_dir."),
        (paths.wiki_dir, paths.raw_dir, "wiki_dir is inside raw_dir."),
        (paths.raw_dir, paths.reviews_dir, "raw_dir is inside reviews_dir."),
        (paths.reviews_dir, paths.raw_dir, "reviews_dir is inside raw_dir."),
        (paths.wiki_dir, paths.reviews_dir, "wiki_dir is inside reviews_dir."),
        (paths.reviews_dir, paths.wiki_dir, "reviews_dir is inside wiki_dir."),
    )
    for left, right, message in nested_pairs:
        if _path_is_relative_to(left.resolve(), right.resolve()):
            overlaps.append(message)
    for canonical in (paths.raw_dir, paths.reviews_dir, paths.synthesis_dir):
        if _path_is_relative_to(paths.wiki_dir.resolve(), canonical.resolve()):
            overlaps.append("wiki_dir is inside a canonical knowledge path.")
            break
    return overlaps


def _migration_area_specs(paths: WikiPaths) -> list[dict[str, Any]]:
    """Return static migration area specifications."""
    knowledge = paths.knowledge_root
    return [
        _retention_spec(
            "raw_readwise",
            "raw_readwise",
            "canonical",
            "knowledge_store",
            "copy_to_knowledge_store",
        ),
        _retention_spec(
            "reviews", "reviews", "canonical", "knowledge_store", "copy_to_knowledge_store"
        ),
        _retention_spec(
            "synthesis",
            "synthesis_cache",
            "canonical",
            "knowledge_store",
            "copy_to_knowledge_store",
        ),
        _retention_spec(
            "render_graph",
            "render_graph",
            "generated",
            "knowledge_store",
            "copy_to_knowledge_store",
        ),
        _retention_spec(
            "render_manifest",
            "render_manifest",
            "generated",
            "knowledge_store",
            "copy_to_knowledge_store",
        ),
        {
            "area_key": "releases",
            "retention_key": None,
            "current_path": lambda p: p.release_dir,
            "target_path": lambda p: p.release_dir,
            "data_class": "canonical",
            "target_location": "knowledge_store",
            "action": "copy_to_knowledge_store",
            "optional": True,
        },
        _retention_spec("wiki", "wiki", "generated", "vault", "copy_to_vault"),
        _retention_spec(
            "synthesis_previews",
            "synthesis_previews",
            "temporary",
            "none",
            "cleanup_candidate",
        ),
        _retention_spec(
            "synthesis_runs",
            "synthesis_runs",
            "temporary",
            "knowledge_store",
            "copy_to_knowledge_store",
        ),
        _retention_spec(
            "synthesis_backups",
            "synthesis_backups",
            "temporary",
            "none",
            "cleanup_candidate",
        ),
        {
            "area_key": "synthesis_prompts",
            "retention_key": "synthesis_prompts",
            "current_path": lambda p: knowledge / "state" / "synthesis_prompts",
            "target_path": lambda p: knowledge / "tmp" / "synthesis_prompts",
            "data_class": "temporary",
            "target_location": "knowledge_store",
            "action": "copy_to_knowledge_store",
            "optional": True,
        },
        {
            "area_key": "ingest_batches",
            "retention_key": "ingest_batches",
            "current_path": lambda p: knowledge / "state" / "ingest_batches",
            "target_path": lambda p: knowledge / "tmp" / "ingest_batches",
            "data_class": "temporary",
            "target_location": "knowledge_store",
            "action": "copy_to_knowledge_store",
            "optional": True,
        },
        {
            "area_key": "config",
            "retention_key": None,
            "current_path": lambda p: p.repo_root / "config",
            "target_path": lambda p: p.repo_root / "config",
            "data_class": "canonical",
            "target_location": "code_repo",
            "action": "keep_in_code_repo",
        },
        {
            "area_key": "docs",
            "retention_key": None,
            "current_path": lambda p: p.repo_root / "docs",
            "target_path": lambda p: p.repo_root / "docs",
            "data_class": "canonical",
            "target_location": "code_repo",
            "action": "keep_in_code_repo",
        },
    ]


def _retention_spec(
    area_key: str,
    retention_key: str,
    data_class: str,
    target_location: TargetLocation,
    action: MigrationAction,
) -> dict[str, Any]:
    """Build one migration spec backed by retention inventory."""
    return {
        "area_key": area_key,
        "retention_key": retention_key,
        "current_path": lambda paths, key=retention_key: _retention_path(paths, key),
        "target_path": lambda paths, key=retention_key: _retention_path(paths, key),
        "data_class": data_class,
        "target_location": target_location,
        "action": action,
    }


def _retention_path(paths: WikiPaths, key: str) -> Path:
    """Resolve a retention-backed path for migration planning."""
    for definition in artifact_area_definitions(paths):
        if definition.key == key:
            return definition.path
    msg = f"Unknown retention area: {key}"
    raise KeyError(msg)


def _definition_for_path(area_key: str, path: Path, data_class: DataClass):
    """Build a minimal artifact definition for inventory counting."""
    from src.wiki_ops.retention import ArtifactAreaDefinition

    return ArtifactAreaDefinition(
        key=area_key,
        path=path,
        data_class=data_class,
        purpose="migration planning",
        cleanup_policy="n/a",
        must_backup=False,
        git_policy="n/a",
        optional=True,
    )


def _migration_action_for_area(
    *,
    current_location: CurrentLocation,
    target_location: TargetLocation,
    spec_action: MigrationAction,
    exists: bool,
    optional: bool,
) -> MigrationAction:
    """Derive the migration action for one area."""
    if not exists:
        return "ignore_missing" if optional else spec_action
    if spec_action == "keep_in_code_repo":
        return "keep_in_code_repo"
    if spec_action == "cleanup_candidate":
        return "cleanup_candidate"
    if target_location == "code_repo":
        return "keep_in_code_repo"
    if current_location == target_location:
        return "already_external"
    if current_location == "external" and target_location in {"knowledge_store", "vault"}:
        return "already_external"
    if current_location == "code_repo":
        return spec_action
    if current_location == "missing":
        return "ignore_missing" if optional else spec_action
    return spec_action


def _area_status(
    *,
    exists: bool,
    optional: bool,
    data_class: str,
    target_location: TargetLocation,
    area_warnings: list[str],
    migration_action: MigrationAction,
) -> AreaStatus:
    """Classify one area's migration status."""
    if area_warnings:
        return "warning"
    if not exists and target_location == "code_repo":
        return "warning"
    if not exists and data_class == "canonical" and not optional:
        return "blocked"
    if not exists and optional:
        return "ok"
    if migration_action == "manual_decision_required":
        return "warning"
    return "ok"


def _evaluate_readiness(
    paths: WikiPaths,
    *,
    areas: list[MigrationAreaPlan],
    retention: RetentionInventory,
    ops_status: OpsStatus | None,
    require_external_knowledge_root: bool,
    require_external_vault_root: bool,
) -> MigrationReadiness:
    """Evaluate overall migration readiness."""
    blocked_reasons: list[str] = []
    warnings: list[str] = []
    actions: list[str] = []

    overlaps = detect_path_overlaps(paths)
    blocked_reasons.extend(overlaps)

    if (
        require_external_knowledge_root
        and paths.knowledge_root.resolve() == paths.repo_root.resolve()
    ):
        blocked_reasons.append(
            "External knowledge_root is required but knowledge_root equals repo_root."
        )
    if require_external_vault_root and paths.vault_root.resolve() == paths.repo_root.resolve():
        blocked_reasons.append("External vault_root is required but vault_root equals repo_root.")

    for area in areas:
        if area.status == "blocked":
            blocked_reasons.append(f"Required area missing or invalid: {area.area_key}.")
        elif area.status == "warning" and area.area_key in {"config", "docs"} and not area.exists:
            warnings.append(f"Code repository area missing: {area.area_key}.")
        for warning in area.warnings:
            if warning not in warnings:
                warnings.append(warning)

    if paths.knowledge_root.resolve() == paths.repo_root.resolve():
        warnings.append("No external knowledge_root is configured yet.")
        actions.append(
            "Create or update config/wiki_paths.toml with external knowledge_root and vault_root."
        )
    if paths.vault_root.resolve() == paths.repo_root.resolve():
        warnings.append("No external vault_root is configured yet.")

    if retention.cleanup_preflight.temporary_file_count > 0:
        warnings.append(
            "Temporary artifacts exist. Run cleanup after a non-blocked release "
            "before a real migration."
        )
        actions.append("Run temporary cleanup after release before copy migration.")

    release_statuses = _load_release_manifest_statuses(paths.release_dir)
    if not release_statuses:
        warnings.append("No release manifest exists.")
        actions.append("Create a non-blocked release manifest before real migration.")
    else:
        _latest_id, latest_status = release_statuses[-1]
        if latest_status == "blocked":
            blocked_reasons.append("Latest release manifest status is blocked.")
        elif latest_status == "warning":
            warnings.append("Latest release manifest readiness is warning.")

    if ops_status is not None:
        recommendations = build_recommendations(ops_status)
        if not any("No render needed." in item for item in recommendations):
            warnings.append("wiki-render appears needed before migration.")
            actions.append("Run wiki-render before migration because rendered wiki is not current.")
        if ops_status.synthesis.errors:
            blocked_reasons.append("Synthesis cache lint reported errors.")
        uncommitted = (
            ops_status.artifacts.uncommitted_durable
            + ops_status.artifacts.uncommitted_synthesis_cache
            + ops_status.artifacts.uncommitted_render_outputs
            + ops_status.artifacts.uncommitted_other
        )
        if uncommitted > 0:
            warnings.append(f"Uncommitted durable or repo files detected ({uncommitted}).")
            actions.append("Resolve uncommitted durable files before migration.")
        if ops_status.synthesis.cache_entries > 0 and not paths.synthesis_dir.exists():
            blocked_reasons.append("Synthesis cache entries exist but synthesis_dir is missing.")

    source_warning = source_text_coverage_warning(paths.wiki_dir)
    if source_warning is not None:
        warnings.append(source_warning)

    if not paths.raw_dir.exists():
        blocked_reasons.append("Required canonical path missing: raw_readwise.")
    if not paths.reviews_dir.exists():
        blocked_reasons.append("Required canonical path missing: reviews.")

    if require_external_knowledge_root:
        actions.append(
            "Run wiki-ops-status --migration-plan --require-external-knowledge-root "
            "after configuring paths."
        )

    status: ReadinessStatus
    if blocked_reasons:
        status = "blocked"
    elif warnings:
        status = "warning"
    else:
        status = "ready"

    if not actions and status == "ready":
        actions.append("Migration planning looks ready for a future copy-only migration slice.")

    deduped_actions = _dedupe_preserve_order(actions)
    deduped_warnings = _dedupe_preserve_order(warnings)
    deduped_blocked = _dedupe_preserve_order(blocked_reasons)
    return MigrationReadiness(
        status=status,
        blocked_reasons=deduped_blocked,
        warnings=deduped_warnings,
        recommended_next_actions=deduped_actions,
    )


def _empty_canonical_checks(
    area_key: str,
    *,
    exists: bool,
    file_count: int,
    ops_status: OpsStatus | None,
) -> tuple[list[str], AreaStatus | None]:
    """Return warnings and optional status overrides for suspicious empty canonical areas."""
    warnings: list[str] = []
    if area_key == "raw_readwise" and exists and file_count == 0:
        warnings.append("Raw source directory exists but contains no files.")
        if ops_status is not None and (
            ops_status.reviews.artifacts > 0 or (ops_status.render.graph_sources or 0) > 0
        ):
            warnings.append(
                "Raw exports are empty while review artifacts or graph sources exist."
            )
            return warnings, "blocked"
        return warnings, "warning"
    if area_key == "reviews" and exists and file_count == 0:
        warnings.append("Review directory exists but contains no review artifacts.")
        return warnings, "warning"
    return warnings, None


def _load_release_manifest_statuses(release_dir: Path) -> list[tuple[str, str]]:
    """Load release manifest ids and statuses from disk."""
    if not release_dir.is_dir():
        return []
    statuses: list[tuple[str, str]] = []
    for manifest_path in sorted(release_dir.glob("*.json")):
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        status = payload.get("status")
        if isinstance(status, str):
            statuses.append((manifest_path.stem, status))
    return statuses


def _path_is_relative_to(path: Path, root: Path) -> bool:
    """Return whether ``path`` is equal to or nested under ``root``."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


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
