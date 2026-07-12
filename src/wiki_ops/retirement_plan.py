"""Read-only old repo data retirement planning for wiki knowledge stores."""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from src.wiki_ops.release_manifest import collect_git_metadata
from src.wiki_ops.release_verify import ReleaseSelectionError, verify_release
from src.wiki_ops.retention import RetentionInventory, collect_retention_inventory
from src.wiki_ops.status import OpsStatus
from src.wiki_paths.config import WikiPaths

RETIREMENT_PLAN_SCHEMA_VERSION = 1

ProposedAction = Literal[
    "keep_tracked",
    "keep_untracked_local_config",
    "untrack_later",
    "manual_review",
    "ignore_rule_needed",
    "not_managed",
]
ReadinessStatus = Literal["ready", "warning", "blocked"]
PreconditionStatus = Literal["ok", "warning", "error", "not_checked"]

KEEP_TRACKED_ROOT_FILES = frozenset(
    {
        "pyproject.toml",
        "README.md",
        "AGENTS.md",
        ".gitignore",
    }
)
KEEP_UNTRACKED_CONFIG_FILES = frozenset({"config/wiki_paths.toml"})
UNTRACK_LATER_EXACT: dict[str, tuple[str, str]] = {
    "raw/.gitkeep": (
        "raw",
        "Raw directory placeholder belongs with externalized raw data.",
    ),
    "state/ingest_manifest.json": (
        "state/ingest_manifest",
        "Legacy ingest manifest belongs to external knowledge-store state.",
    ),
    "state/wiki_render_graph.json": (
        "state/wiki_render_graph",
        "Render graph belongs to external knowledge store.",
    ),
    "state/wiki_render_manifest.json": (
        "state/wiki_render_manifest",
        "Render manifest belongs to external knowledge store.",
    ),
}
UNTRACK_LATER_PREFIXES: tuple[tuple[str, str, str], ...] = (
    ("raw/readwise/", "raw/readwise", "Raw Readwise exports belong to external knowledge store."),
    ("state/reviews/", "state/reviews", "Review artifacts belong to external knowledge store."),
    (
        "state/synthesis/",
        "state/synthesis",
        "Synthesis cache entries belong to external knowledge store.",
    ),
    ("state/releases/", "state/releases", "Release manifests belong to external knowledge store."),
    (
        "state/synthesis_previews/",
        "state/synthesis_previews",
        "Temporary synthesis previews should not be tracked in the code repo.",
    ),
    (
        "state/synthesis_runs/",
        "state/synthesis_runs",
        "Synthesis run audit reports should not be tracked in the code repo.",
    ),
    (
        "state/synthesis_backups/",
        "state/synthesis_backups",
        "Temporary synthesis backups should not be tracked in the code repo.",
    ),
    (
        "state/synthesis_prompts/",
        "state/synthesis_prompts",
        "Temporary synthesis prompt previews should not be tracked in the code repo.",
    ),
    (
        "state/ingest_batches/",
        "state/ingest_batches",
        "Ingest batch logs should not be tracked in the code repo.",
    ),
    ("wiki/", "wiki", "Generated wiki pages belong to external private vault."),
    ("sources/", "sources", "Generated source pages belong to external private vault."),
    ("indexes/", "indexes", "Generated index pages belong to external private vault."),
)
MANUAL_REVIEW_PREFIXES = ("state/", "raw/", "wiki/", "sources/", "indexes/")
IGNORE_RULE_NEEDED_PATTERNS = (
    "__pycache__/**",
    "**/__pycache__/**",
    "*.pyc",
    ".pytest_cache/**",
    ".mypy_cache/**",
    ".ruff_cache/**",
    ".DS_Store",
    "*.log",
    "*.tmp",
    "*.swp",
)


@dataclass(frozen=True)
class RetirementFileEntry:
    """Classification for one Git-tracked file."""

    path: str
    area: str
    proposed_action: ProposedAction
    byte_count: int
    reason: str


@dataclass(frozen=True)
class RetirementAreaSummary:
    """Aggregated retirement classification for one area."""

    key: str
    proposed_action: ProposedAction
    file_count: int
    byte_count: int


@dataclass(frozen=True)
class RetirementPrecondition:
    """One retirement readiness precondition."""

    key: str
    status: PreconditionStatus
    message: str


@dataclass(frozen=True)
class RetirementPlanSummary:
    """Summary counts for a retirement plan."""

    tracked_files: int
    keep_tracked: int
    untrack_later: int
    manual_review: int
    keep_untracked_local_config: int
    ignore_rule_needed: int
    not_managed: int
    total_bytes: int


@dataclass(frozen=True)
class RepoDataRetirementPlan:
    """Read-only old repo data retirement plan."""

    schema_version: int
    code_root: Path
    readiness: ReadinessStatus
    summary: RetirementPlanSummary
    preconditions: list[RetirementPrecondition]
    areas: list[RetirementAreaSummary]
    files: list[RetirementFileEntry]
    recommended_next_actions: list[str]
    git_inventory_error: str | None = None


def build_retirement_plan(
    paths: WikiPaths,
    *,
    ops_status: OpsStatus | None = None,
    retention: RetentionInventory | None = None,
) -> RepoDataRetirementPlan:
    """Build a read-only retirement plan for Git-tracked code repository files."""
    resolved_retention = retention or collect_retention_inventory(paths)
    tracked_paths, git_error = list_tracked_files(paths.repo_root)
    files = _classify_tracked_files(paths.repo_root, tracked_paths)
    summary = _summarize_files(files)
    areas = _summarize_areas(files)
    preconditions = _collect_preconditions(
        paths,
        files=files,
        git_error=git_error,
        retention=resolved_retention,
        ops_status=ops_status,
    )
    readiness = _evaluate_readiness(
        files=files,
        preconditions=preconditions,
        git_error=git_error,
    )
    actions = _recommended_next_actions(
        files=files,
        readiness=readiness,
        preconditions=preconditions,
    )
    return RepoDataRetirementPlan(
        schema_version=RETIREMENT_PLAN_SCHEMA_VERSION,
        code_root=paths.repo_root,
        readiness=readiness,
        summary=summary,
        preconditions=preconditions,
        areas=areas,
        files=files,
        recommended_next_actions=actions,
        git_inventory_error=git_error,
    )


def list_tracked_files(repo_root: Path) -> tuple[list[str], str | None]:
    """Return repository-relative paths tracked by Git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        return [], str(exc)
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip() or "git ls-files failed"
        return [], error
    if not result.stdout:
        return [], None
    paths = [item for item in result.stdout.decode("utf-8").split("\0") if item]
    return sorted(paths), None


def classify_tracked_path(path: str) -> tuple[str, ProposedAction, str]:
    """Classify one repository-relative tracked path."""
    normalized = path.replace("\\", "/")

    if normalized in KEEP_UNTRACKED_CONFIG_FILES:
        return (
            "config",
            "keep_untracked_local_config",
            "Local path configuration must not be tracked in Git.",
        )
    if normalized == ".env" or normalized.startswith(".env."):
        return (
            "config",
            "keep_untracked_local_config",
            "Local env files must not be tracked in Git.",
        )

    if normalized.startswith("src/"):
        return ("src", "keep_tracked", "Application source code belongs in the code repository.")
    if normalized.startswith("tests/"):
        return ("tests", "keep_tracked", "Tests and fixtures belong in the code repository.")
    if normalized.startswith("docs/"):
        return ("docs", "keep_tracked", "Documentation belongs in the code repository.")
    if normalized in KEEP_TRACKED_ROOT_FILES:
        return ("repo_root", "keep_tracked", "Repository metadata belongs in the code repository.")
    if normalized.startswith("config/") and normalized.endswith(".example.toml"):
        return (
            "config",
            "keep_tracked",
            "Example path configuration belongs in the code repository.",
        )
    if normalized.startswith("config/"):
        return (
            "config",
            "keep_tracked",
            "Code repository configuration belongs in the code repository.",
        )

    exact = UNTRACK_LATER_EXACT.get(normalized)
    if exact is not None:
        area, reason = exact
        return area, "untrack_later", reason
    for prefix, area, reason in UNTRACK_LATER_PREFIXES:
        if normalized.startswith(prefix):
            return area, "untrack_later", reason

    for zone in MANUAL_REVIEW_PREFIXES:
        if normalized.startswith(zone):
            area = _manual_review_area(normalized, zone)
            return (
                area,
                "manual_review",
                f"Unknown tracked file under {zone.rstrip('/')} requires manual review.",
            )

    if _matches_ignore_rule_needed(normalized):
        return (
            "misc",
            "ignore_rule_needed",
            "Tracked file matches a pattern that should be covered by .gitignore.",
        )

    return ("other", "not_managed", "Outside old-repo data retirement scope.")


def retirement_plan_to_json(plan: RepoDataRetirementPlan) -> dict[str, object]:
    """Return a JSON-serializable retirement plan payload."""
    return {
        "schema_version": plan.schema_version,
        "code_root": str(plan.code_root),
        "readiness": plan.readiness,
        "summary": {
            "tracked_files": plan.summary.tracked_files,
            "keep_tracked": plan.summary.keep_tracked,
            "untrack_later": plan.summary.untrack_later,
            "manual_review": plan.summary.manual_review,
            "keep_untracked_local_config": plan.summary.keep_untracked_local_config,
            "ignore_rule_needed": plan.summary.ignore_rule_needed,
            "not_managed": plan.summary.not_managed,
            "total_bytes": plan.summary.total_bytes,
        },
        "preconditions": [
            {"key": item.key, "status": item.status, "message": item.message}
            for item in plan.preconditions
        ],
        "areas": [
            {
                "key": area.key,
                "proposed_action": area.proposed_action,
                "file_count": area.file_count,
                "byte_count": area.byte_count,
            }
            for area in plan.areas
        ],
        "files": [
            {
                "path": entry.path,
                "area": entry.area,
                "proposed_action": entry.proposed_action,
                "byte_count": entry.byte_count,
                "reason": entry.reason,
            }
            for entry in plan.files
        ],
        "recommended_next_actions": list(plan.recommended_next_actions),
        "git_inventory_error": plan.git_inventory_error,
    }


def format_retirement_plan_text(plan: RepoDataRetirementPlan) -> str:
    """Render a concise human-readable retirement plan."""
    lines = [
        "Old Repo Data Retirement",
        f"- tracked files inspected: {plan.summary.tracked_files}",
        f"- keep tracked: {plan.summary.keep_tracked}",
        f"- untrack later: {plan.summary.untrack_later}",
        f"- manual review: {plan.summary.manual_review}",
        f"- readiness: {plan.readiness}",
    ]
    untrack_areas = [
        area for area in plan.areas if area.proposed_action == "untrack_later" and area.file_count
    ]
    if untrack_areas:
        lines.append("")
        lines.append("Largest untrack-later areas")
        for area in sorted(untrack_areas, key=lambda item: (-item.byte_count, item.key))[:5]:
            lines.append(f"- {area.key}: {area.file_count} files, {_format_bytes(area.byte_count)}")
    manual_review_files = [
        entry for entry in plan.files if entry.proposed_action == "manual_review"
    ]
    if manual_review_files:
        lines.append("")
        lines.append("Manual review files")
        for entry in manual_review_files[:10]:
            lines.append(f"- {entry.path}: {entry.reason}")
        remaining = len(manual_review_files) - 10
        if remaining > 0:
            lines.append(f"- ... {remaining} more")
    lines.append("")
    lines.append("Preconditions")
    for item in plan.preconditions:
        lines.append(f"- {item.key.replace('_', ' ')}: {item.status}")
    if plan.git_inventory_error:
        lines.append(f"- git inventory error: {plan.git_inventory_error}")
    if plan.recommended_next_actions:
        lines.append("")
        lines.append("Recommended next actions")
        for index, action in enumerate(plan.recommended_next_actions, start=1):
            lines.append(f"{index}. {action}")
    return "\n".join(lines)


def _classify_tracked_files(repo_root: Path, tracked_paths: list[str]) -> list[RetirementFileEntry]:
    """Classify tracked files and attach byte counts."""
    entries: list[RetirementFileEntry] = []
    for rel_path in tracked_paths:
        area, action, reason = classify_tracked_path(rel_path)
        absolute = repo_root / rel_path
        byte_count = absolute.stat().st_size if absolute.is_file() else 0
        entries.append(
            RetirementFileEntry(
                path=rel_path,
                area=area,
                proposed_action=action,
                byte_count=byte_count,
                reason=reason,
            )
        )
    return entries


def _summarize_files(files: list[RetirementFileEntry]) -> RetirementPlanSummary:
    """Aggregate file classifications into summary counts."""
    counts = {
        "keep_tracked": 0,
        "untrack_later": 0,
        "manual_review": 0,
        "keep_untracked_local_config": 0,
        "ignore_rule_needed": 0,
        "not_managed": 0,
    }
    total_bytes = 0
    for entry in files:
        counts[entry.proposed_action] += 1
        total_bytes += entry.byte_count
    return RetirementPlanSummary(
        tracked_files=len(files),
        keep_tracked=counts["keep_tracked"],
        untrack_later=counts["untrack_later"],
        manual_review=counts["manual_review"],
        keep_untracked_local_config=counts["keep_untracked_local_config"],
        ignore_rule_needed=counts["ignore_rule_needed"],
        not_managed=counts["not_managed"],
        total_bytes=total_bytes,
    )


def _summarize_areas(files: list[RetirementFileEntry]) -> list[RetirementAreaSummary]:
    """Aggregate file classifications by area key."""
    grouped: dict[tuple[str, ProposedAction], list[RetirementFileEntry]] = {}
    for entry in files:
        key = (entry.area, entry.proposed_action)
        grouped.setdefault(key, []).append(entry)
    areas = [
        RetirementAreaSummary(
            key=area_key,
            proposed_action=action,
            file_count=len(entries),
            byte_count=sum(item.byte_count for item in entries),
        )
        for (area_key, action), entries in grouped.items()
    ]
    return sorted(areas, key=lambda item: item.key)


def _collect_preconditions(
    paths: WikiPaths,
    *,
    files: list[RetirementFileEntry],
    git_error: str | None,
    retention: RetentionInventory,
    ops_status: OpsStatus | None,
) -> list[RetirementPrecondition]:
    """Collect retirement readiness preconditions."""
    preconditions: list[RetirementPrecondition] = []

    knowledge_external = paths.knowledge_root.resolve() != paths.repo_root.resolve()
    if knowledge_external and paths.knowledge_root.exists():
        preconditions.append(
            RetirementPrecondition(
                key="external_knowledge_root",
                status="ok",
                message="External knowledge root is configured.",
            )
        )
    elif knowledge_external:
        preconditions.append(
            RetirementPrecondition(
                key="external_knowledge_root",
                status="error",
                message="External knowledge root is configured but does not exist.",
            )
        )
    else:
        preconditions.append(
            RetirementPrecondition(
                key="external_knowledge_root",
                status="error",
                message="Primary knowledge paths still point at the code repository.",
            )
        )

    vault_external = paths.vault_root.resolve() != paths.repo_root.resolve()
    if vault_external and paths.vault_root.exists():
        preconditions.append(
            RetirementPrecondition(
                key="external_vault_root",
                status="ok",
                message="External vault root is configured.",
            )
        )
    elif vault_external:
        preconditions.append(
            RetirementPrecondition(
                key="external_vault_root",
                status="error",
                message="External vault root is configured but does not exist.",
            )
        )
    else:
        preconditions.append(
            RetirementPrecondition(
                key="external_vault_root",
                status="error",
                message="Generated vault paths still point at the code repository.",
            )
        )

    try:
        verification = verify_release(paths, selector="latest")
        if verification.status == "error":
            status: PreconditionStatus = "error"
        elif verification.status == "warning":
            status = "warning"
        else:
            status = "ok"
        preconditions.append(
            RetirementPrecondition(
                key="latest_release_verification",
                status=status,
                message=f"Latest release verification status is {verification.status}.",
            )
        )
    except ReleaseSelectionError as exc:
        preconditions.append(
            RetirementPrecondition(
                key="latest_release_verification",
                status="warning",
                message=str(exc),
            )
        )

    preconditions.append(
        RetirementPrecondition(
            key="render_dry_run",
            status="not_checked",
            message="Render dry-run is not checked by this command.",
        )
    )

    git = collect_git_metadata(paths.repo_root)
    if git_error is not None:
        preconditions.append(
            RetirementPrecondition(
                key="git_tracked_inventory",
                status="error",
                message=git_error,
            )
        )
    elif git.git_dirty is True:
        preconditions.append(
            RetirementPrecondition(
                key="git_working_tree",
                status="warning",
                message="Git working tree has uncommitted changes.",
            )
        )
    elif git.git_dirty is False:
        preconditions.append(
            RetirementPrecondition(
                key="git_working_tree",
                status="ok",
                message="Git working tree is clean.",
            )
        )
    else:
        preconditions.append(
            RetirementPrecondition(
                key="git_working_tree",
                status="warning",
                message=git.git_error or "Git working tree status is unknown.",
            )
        )

    if retention.cleanup_preflight.temporary_file_count > 0:
        preconditions.append(
            RetirementPrecondition(
                key="temporary_artifacts",
                status="warning",
                message=(
                    "Temporary artifacts exist "
                    f"({retention.cleanup_preflight.temporary_file_count} files)."
                ),
            )
        )

    if any(entry.proposed_action == "keep_untracked_local_config" for entry in files):
        preconditions.append(
            RetirementPrecondition(
                key="tracked_local_config",
                status="error",
                message="Local configuration files are still tracked in Git.",
            )
        )

    if ops_status is not None and ops_status.synthesis.errors:
        preconditions.append(
            RetirementPrecondition(
                key="synthesis_cache_lint",
                status="error",
                message="Synthesis cache lint reported errors.",
            )
        )

    return preconditions


def _evaluate_readiness(
    *,
    files: list[RetirementFileEntry],
    preconditions: list[RetirementPrecondition],
    git_error: str | None,
) -> ReadinessStatus:
    """Compute overall retirement readiness."""
    if git_error is not None:
        return "blocked"
    if any(item.status == "error" for item in preconditions):
        return "blocked"
    if any(entry.proposed_action == "manual_review" for entry in files):
        return "warning"
    if any(item.status == "warning" for item in preconditions):
        return "warning"
    return "ready"


def _recommended_next_actions(
    *,
    files: list[RetirementFileEntry],
    readiness: ReadinessStatus,
    preconditions: list[RetirementPrecondition],
) -> list[str]:
    """Return operator-facing next actions."""
    actions: list[str] = []
    if any(entry.proposed_action == "manual_review" for entry in files):
        actions.append("Review manual_review files.")
    verification = next(
        (item for item in preconditions if item.key == "latest_release_verification"),
        None,
    )
    if verification is not None and verification.status != "ok":
        actions.append("Confirm latest release verification before untracking.")
    if readiness != "blocked":
        actions.append(
            "In a later approved step, run git rm --cached only for untrack_later files."
        )
    if any(entry.proposed_action == "ignore_rule_needed" for entry in files):
        actions.append("Review ignore_rule_needed files and update .gitignore if needed.")
    if readiness == "ready" and not actions:
        actions.append("Retirement plan looks ready for a future approved untracking step.")
    return _dedupe_preserve_order(actions)


def _manual_review_area(normalized: str, zone: str) -> str:
    """Return an area key for one manual-review path."""
    parts = normalized.split("/")
    if zone == "state/" and len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def _matches_ignore_rule_needed(normalized: str) -> bool:
    """Return whether a tracked path matches ignore-rule-needed patterns."""
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in IGNORE_RULE_NEEDED_PATTERNS)


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
