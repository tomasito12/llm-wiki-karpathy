"""Read-only private vault Git strategy assessment."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.wiki_contract.layout import is_managed_relative_path, is_preserved_wiki_path
from src.wiki_ops.source_access import SourceAccessStatus
from src.wiki_ops.status import OpsStatus
from src.wiki_paths.config import WikiPaths

VAULT_GIT_STRATEGY_SCHEMA_VERSION = 1
PLAIN_GIT_MAX_TOTAL_MIB = 100.0
PLAIN_GIT_MAX_SINGLE_FILE_MIB = 10.0
LFS_TRIGGER_TOTAL_MIB = 250.0
LFS_TRIGGER_SINGLE_FILE_MIB = 25.0
BINARY_EXTENSIONS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".pdf",
        ".zip",
        ".gz",
        ".tar",
        ".mp3",
        ".mp4",
        ".mov",
        ".heic",
    }
)
RemotePolicy = Literal["local_only", "private_remote_later", "blocked"]
ReadinessStatus = Literal["ready", "warning", "blocked"]
ContentClassification = Literal["managed_generated", "manual_or_legacy", "other"]


@dataclass(frozen=True)
class VaultFileEntry:
    """One file in the vault inventory."""

    relative_path: str
    byte_count: int

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable file entry."""
        return asdict(self)


@dataclass(frozen=True)
class VaultContentArea:
    """Classification summary for one vault content area."""

    classification: ContentClassification
    file_count: int
    byte_count: int
    examples: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable content area payload."""
        return asdict(self)


@dataclass(frozen=True)
class VaultGitInventory:
    """Filesystem facts for the private vault root."""

    vault_root: Path
    vault_exists: bool
    wiki_dir_exists: bool
    total_files: int
    markdown_files: int
    binary_files: int
    total_bytes: int
    wiki_bytes: int
    sources_bytes: int
    largest_files: list[VaultFileEntry]
    content_areas: list[VaultContentArea]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable inventory payload."""
        payload = asdict(self)
        payload["vault_root"] = str(self.vault_root)
        payload["largest_files"] = [entry.to_dict() for entry in self.largest_files]
        payload["content_areas"] = [area.to_dict() for area in self.content_areas]
        return payload


@dataclass(frozen=True)
class VaultGitState:
    """Current Git state for the private vault."""

    has_git: bool
    has_commits: bool
    has_remote: bool
    remote_names: list[str]
    uncommitted_files: int | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable Git state payload."""
        return asdict(self)


@dataclass(frozen=True)
class VaultGitRecommendations:
    """Recommended Git strategy for the private vault."""

    use_plain_git: bool
    use_git_lfs: bool
    remote_policy: RemotePolicy
    commit_full_source_text: bool
    ready_for_git_init: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable recommendations payload."""
        return asdict(self)


@dataclass(frozen=True)
class VaultGitReadiness:
    """Overall readiness for introducing local vault Git."""

    status: ReadinessStatus
    blocked_reasons: list[str]
    warnings: list[str]
    recommended_next_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable readiness payload."""
        return asdict(self)


@dataclass(frozen=True)
class VaultGitStrategy:
    """Read-only private vault Git strategy report."""

    schema_version: int
    created_at: datetime
    vault_root: Path
    wiki_dir: Path
    inventory: VaultGitInventory
    git_state: VaultGitState
    recommendations: VaultGitRecommendations
    readiness: VaultGitReadiness

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable strategy report."""
        return vault_git_strategy_to_json(self)


def default_vault_gitignore_content() -> str:
    """Return the recommended private-vault ``.gitignore`` template."""
    return """# Obsidian / editor local state
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/

# macOS
.DS_Store

# Local-only secrets
.env
"""


def build_vault_git_strategy(
    paths: WikiPaths,
    *,
    ops_status: OpsStatus | None = None,
    created_at: datetime | None = None,
) -> VaultGitStrategy:
    """Build a read-only private vault Git strategy report.

    Args:
        paths: Resolved wiki path configuration.
        ops_status: Optional ops status snapshot for source-access checks.
        created_at: Optional timestamp override for deterministic tests.

    Returns:
        A :class:`VaultGitStrategy` report with inventory, Git state, and
        recommendations.
    """
    moment = created_at or datetime.now(UTC)
    inventory = collect_vault_git_inventory(paths.vault_root, wiki_dir=paths.wiki_dir)
    git_state = collect_vault_git_state(paths.vault_root)
    recommendations = build_vault_git_recommendations(
        inventory=inventory,
        git_state=git_state,
        source_access=ops_status.source_access if ops_status is not None else None,
    )
    readiness = evaluate_vault_git_readiness(
        inventory=inventory,
        git_state=git_state,
        recommendations=recommendations,
        source_access=ops_status.source_access if ops_status is not None else None,
    )
    return VaultGitStrategy(
        schema_version=VAULT_GIT_STRATEGY_SCHEMA_VERSION,
        created_at=moment,
        vault_root=paths.vault_root,
        wiki_dir=paths.wiki_dir,
        inventory=inventory,
        git_state=git_state,
        recommendations=recommendations,
        readiness=readiness,
    )


def collect_vault_git_inventory(vault_root: Path, *, wiki_dir: Path) -> VaultGitInventory:
    """Measure vault size, file counts, and content classification."""
    vault_exists = vault_root.is_dir()
    wiki_dir_exists = wiki_dir.is_dir()
    if not vault_exists:
        return VaultGitInventory(
            vault_root=vault_root,
            vault_exists=False,
            wiki_dir_exists=wiki_dir_exists,
            total_files=0,
            markdown_files=0,
            binary_files=0,
            total_bytes=0,
            wiki_bytes=0,
            sources_bytes=0,
            largest_files=[],
            content_areas=[],
        )

    files = [
        path
        for path in vault_root.rglob("*")
        if path.is_file() and not _is_git_internal_path(path, vault_root=vault_root)
    ]
    markdown_files = 0
    binary_files = 0
    total_bytes = 0
    wiki_bytes = 0
    sources_bytes = 0
    largest: list[VaultFileEntry] = []
    area_counts: dict[ContentClassification, tuple[int, int, list[str]]] = {
        "managed_generated": (0, 0, []),
        "manual_or_legacy": (0, 0, []),
        "other": (0, 0, []),
    }

    for file_path in files:
        try:
            relative = file_path.relative_to(vault_root).as_posix()
            size = file_path.stat().st_size
        except (OSError, ValueError):
            continue
        total_bytes += size
        if file_path.suffix.lower() == ".md":
            markdown_files += 1
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            binary_files += 1
        largest.append(VaultFileEntry(relative_path=relative, byte_count=size))
        if relative.startswith("wiki/"):
            wiki_bytes += size
            if relative.startswith("wiki/sources/"):
                sources_bytes += size
            wiki_relative = relative.removeprefix("wiki/")
            classification = _classify_wiki_relative_path(wiki_relative)
        else:
            classification = "other"
        count, bytes_total, examples = area_counts[classification]
        examples = [*examples, relative]
        if len(examples) > 5:
            examples = examples[:5]
        area_counts[classification] = (count + 1, bytes_total + size, examples)

    largest.sort(key=lambda entry: entry.byte_count, reverse=True)
    content_areas = [
        VaultContentArea(
            classification=classification,
            file_count=count,
            byte_count=bytes_total,
            examples=examples,
        )
        for classification, (count, bytes_total, examples) in area_counts.items()
        if count > 0
    ]
    return VaultGitInventory(
        vault_root=vault_root,
        vault_exists=True,
        wiki_dir_exists=wiki_dir_exists,
        total_files=len(files),
        markdown_files=markdown_files,
        binary_files=binary_files,
        total_bytes=total_bytes,
        wiki_bytes=wiki_bytes,
        sources_bytes=sources_bytes,
        largest_files=largest[:15],
        content_areas=content_areas,
    )


def collect_vault_git_state(vault_root: Path) -> VaultGitState:
    """Inspect whether the private vault already has local Git state."""
    git_dir = vault_root / ".git"
    if not git_dir.exists():
        return VaultGitState(
            has_git=False,
            has_commits=False,
            has_remote=False,
            remote_names=[],
            uncommitted_files=None,
        )
    has_commits = _git_has_commits(vault_root)
    remote_names = _git_remote_names(vault_root)
    uncommitted_files = _git_uncommitted_count(vault_root) if has_commits else None
    return VaultGitState(
        has_git=True,
        has_commits=has_commits,
        has_remote=bool(remote_names),
        remote_names=remote_names,
        uncommitted_files=uncommitted_files,
    )


def build_vault_git_recommendations(
    *,
    inventory: VaultGitInventory,
    git_state: VaultGitState,
    source_access: SourceAccessStatus | None,
) -> VaultGitRecommendations:
    """Return conservative Git strategy recommendations for the private vault."""
    total_mib = _bytes_to_mib(inventory.total_bytes)
    largest_mib = _bytes_to_mib(
        inventory.largest_files[0].byte_count if inventory.largest_files else 0
    )
    use_git_lfs = total_mib >= LFS_TRIGGER_TOTAL_MIB or largest_mib >= LFS_TRIGGER_SINGLE_FILE_MIB
    use_plain_git = (
        inventory.vault_exists
        and not use_git_lfs
        and total_mib <= PLAIN_GIT_MAX_TOTAL_MIB
        and largest_mib <= PLAIN_GIT_MAX_SINGLE_FILE_MIB
    )
    remote_policy: RemotePolicy = "local_only"
    if source_access is not None and _source_access_needs_attention(source_access):
        remote_policy = "blocked"
    elif inventory.sources_bytes > 0:
        remote_policy = "private_remote_later"
    ready_for_git_init = (
        inventory.vault_exists
        and inventory.wiki_dir_exists
        and not git_state.has_git
        and use_plain_git
        and not use_git_lfs
        and (source_access is None or not _source_access_needs_attention(source_access))
    )
    return VaultGitRecommendations(
        use_plain_git=use_plain_git,
        use_git_lfs=use_git_lfs,
        remote_policy=remote_policy,
        commit_full_source_text=True,
        ready_for_git_init=ready_for_git_init,
    )


def evaluate_vault_git_readiness(
    *,
    inventory: VaultGitInventory,
    git_state: VaultGitState,
    recommendations: VaultGitRecommendations,
    source_access: SourceAccessStatus | None,
) -> VaultGitReadiness:
    """Evaluate whether local vault Git initialization is safe now."""
    blocked_reasons: list[str] = []
    warnings: list[str] = []
    actions: list[str] = []

    if not inventory.vault_exists:
        blocked_reasons.append(f"Vault root missing: {inventory.vault_root}")
    if not inventory.wiki_dir_exists:
        blocked_reasons.append(f"Wiki directory missing: {inventory.vault_root / 'wiki'}")
    if git_state.has_git and not git_state.has_commits:
        warnings.append("Vault already has .git but no commits yet.")
        actions.append("Review git status in the vault root and create the first manual commit.")
    if git_state.has_git and git_state.has_commits:
        warnings.append("Vault already initialized as a Git repository.")
        actions.append("Use normal manual git status/diff/commit workflow in the vault root.")
    if git_state.has_remote:
        warnings.append(
            "Vault already has a configured Git remote; do not push embedded source text "
            "without an explicit privacy review."
        )
    if recommendations.use_git_lfs:
        blocked_reasons.append(
            "Vault size or largest-file thresholds suggest Git LFS; do not initialize "
            "plain Git without an explicit LFS decision."
        )
    if not recommendations.use_plain_git and inventory.vault_exists:
        blocked_reasons.append(
            "Vault does not meet the current plain-Git size thresholds for automatic init."
        )
    if source_access is not None and _source_access_needs_attention(source_access):
        blocked_reasons.append(
            "Source access verification has gaps; fix them before versioning the vault."
        )
    elif source_access is not None and source_access.embedded_full_text > 0:
        warnings.append(
            "Vault contains embedded full source text; treat the repository as private "
            "and do not configure a remote push yet."
        )
    manual_examples = _manual_content_examples(inventory)
    if manual_examples:
        warnings.append(
            "Vault contains manual or legacy content that should be reviewed before cleanup: "
            + ", ".join(manual_examples)
        )

    if recommendations.ready_for_git_init:
        actions.extend(format_vault_git_init_steps(inventory.vault_root))
    elif not git_state.has_git and not blocked_reasons:
        actions.append(
            "Re-run hatch run wiki-ops-status --vault-git-strategy after fixing warnings."
        )

    status: ReadinessStatus
    if blocked_reasons:
        status = "blocked"
    elif warnings:
        status = "warning"
    else:
        status = "ready"
    if not actions and status == "ready":
        actions.append("No vault Git action required.")
    return VaultGitReadiness(
        status=status,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        recommended_next_actions=actions,
    )


def format_vault_git_init_steps(vault_root: Path) -> list[str]:
    """Return operator steps for the first local vault Git initialization."""
    vault = vault_root.resolve()
    return [
        f"cd {vault}",
        f"printf '%s\\n' {sh_quote_lines(default_vault_gitignore_content())} > .gitignore",
        "git init",
        "git add .",
        "git status",
        'git commit -m "Initial private vault snapshot after source-access verification"',
        "Keep the repository local-only until privacy and backup policy are reviewed.",
    ]


def format_vault_git_strategy_text(strategy: VaultGitStrategy) -> str:
    """Render a concise human-readable vault Git strategy section."""
    inventory = strategy.inventory
    git_state = strategy.git_state
    recommendations = strategy.recommendations
    readiness = strategy.readiness
    lines = [
        "Private Vault Git Strategy",
        "",
        "Roots",
        f"- vault root: {strategy.vault_root}",
        f"- wiki dir: {strategy.wiki_dir}",
        "",
        "Inventory",
        f"- vault exists: {'yes' if inventory.vault_exists else 'no'}",
        f"- wiki dir exists: {'yes' if inventory.wiki_dir_exists else 'no'}",
        f"- total files: {inventory.total_files}",
        f"- markdown files: {inventory.markdown_files}",
        f"- binary files: {inventory.binary_files}",
        f"- total size: {inventory.total_bytes} bytes "
        f"({_bytes_to_mib(inventory.total_bytes):.2f} MiB)",
        f"- wiki size: {inventory.wiki_bytes} bytes "
        f"({_bytes_to_mib(inventory.wiki_bytes):.2f} MiB)",
        f"- sources size: {inventory.sources_bytes} bytes "
        f"({_bytes_to_mib(inventory.sources_bytes):.2f} MiB)",
        "",
        "Git State",
        f"- has git: {'yes' if git_state.has_git else 'no'}",
        f"- has commits: {'yes' if git_state.has_commits else 'no'}",
        f"- has remote: {'yes' if git_state.has_remote else 'no'}",
    ]
    if git_state.remote_names:
        lines.append(f"- remotes: {', '.join(git_state.remote_names)}")
    if git_state.uncommitted_files is not None:
        lines.append(f"- uncommitted files: {git_state.uncommitted_files}")
    lines.extend(
        [
            "",
            "Recommendations",
            f"- use plain git: {'yes' if recommendations.use_plain_git else 'no'}",
            f"- use git lfs: {'yes' if recommendations.use_git_lfs else 'no'}",
            f"- remote policy: {recommendations.remote_policy}",
            "- commit full source text: "
            f"{'yes' if recommendations.commit_full_source_text else 'no'}",
            f"- ready for git init: {'yes' if recommendations.ready_for_git_init else 'no'}",
            "",
            f"Readiness: {readiness.status}",
        ]
    )
    if inventory.largest_files:
        lines.append("")
        lines.append("Largest Files")
        for entry in inventory.largest_files[:10]:
            lines.append(f"- {entry.relative_path}: {entry.byte_count} bytes")
    if inventory.content_areas:
        lines.append("")
        lines.append("Content Classification")
        for area in inventory.content_areas:
            lines.append(
                f"- {area.classification}: files={area.file_count} bytes={area.byte_count}"
            )
            if area.examples:
                lines.append(f"  examples: {', '.join(area.examples)}")
    if readiness.blocked_reasons:
        lines.append("")
        lines.append("Blocked Reasons")
        lines.extend(f"- {reason}" for reason in readiness.blocked_reasons)
    if readiness.warnings:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in readiness.warnings)
    lines.append("")
    lines.append("Recommended Next Actions")
    if readiness.recommended_next_actions:
        for index, action in enumerate(readiness.recommended_next_actions, start=1):
            lines.append(f"{index}. {action}")
    else:
        lines.append("1. No actions recommended.")
    return "\n".join(lines)


def vault_git_strategy_to_json(strategy: VaultGitStrategy) -> dict[str, Any]:
    """Serialize a vault Git strategy report to JSON-compatible data."""
    return {
        "schema_version": strategy.schema_version,
        "created_at": strategy.created_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "roots": {
            "vault_root": str(strategy.vault_root),
            "wiki_dir": str(strategy.wiki_dir),
        },
        "inventory": strategy.inventory.to_dict(),
        "git_state": strategy.git_state.to_dict(),
        "recommendations": strategy.recommendations.to_dict(),
        "readiness": strategy.readiness.to_dict(),
    }


def build_vault_git_recommendations_for_status(strategy: VaultGitStrategy) -> list[str]:
    """Return short recommendations suitable for the main ops status report."""
    recommendations = strategy.recommendations
    readiness = strategy.readiness
    if readiness.status == "blocked":
        return ["Resolve vault Git strategy blockers before initializing the private vault."]
    if recommendations.ready_for_git_init:
        return [
            "Vault Git strategy is ready: initialize local plain Git in the vault root "
            "with the documented .gitignore template."
        ]
    if strategy.git_state.has_git:
        return ["Use manual vault Git commits after successful render and wiki-lint checks."]
    if readiness.warnings:
        return ["Review vault Git strategy warnings before initializing local Git."]
    return []


def _is_git_internal_path(path: Path, *, vault_root: Path) -> bool:
    """Return whether a path lives inside the vault's ``.git`` directory."""
    try:
        relative = path.relative_to(vault_root)
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] == ".git"


def _classify_wiki_relative_path(relative_path: str) -> ContentClassification:
    """Classify one wiki-relative path for vault Git reporting."""
    if is_managed_relative_path(relative_path):
        return "managed_generated"
    if is_preserved_wiki_path(relative_path) or relative_path.startswith("questions/"):
        return "manual_or_legacy"
    return "other"


def _manual_content_examples(inventory: VaultGitInventory) -> list[str]:
    """Return example manual/legacy paths from the inventory."""
    for area in inventory.content_areas:
        if area.classification == "manual_or_legacy":
            return list(area.examples)
    return []


def _source_access_needs_attention(status: SourceAccessStatus) -> bool:
    """Return whether source access gaps should block vault Git work."""
    return bool(
        not status.wiki_dir_exists
        or status.external_url_only
        or status.malformed_pages
        or status.source_id_mismatches
        or status.source_pages_missing_raw_markdown
        or status.graph_sources_missing_pages
        or status.broken_source_link_targets
    )


def _bytes_to_mib(byte_count: int) -> float:
    """Convert bytes to mebibytes."""
    return byte_count / 1024 / 1024


def _git_has_commits(vault_root: Path) -> bool:
    """Return whether the vault Git repository has at least one commit."""
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=vault_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def _git_remote_names(vault_root: Path) -> list[str]:
    """Return configured Git remote names for the vault repository."""
    completed = subprocess.run(
        ["git", "remote"],
        cwd=vault_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _git_uncommitted_count(vault_root: Path) -> int | None:
    """Return the number of uncommitted paths in the vault repository."""
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=vault_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    return len([line for line in completed.stdout.splitlines() if line.strip()])


def sh_quote_lines(text: str) -> str:
    """Return shell-quoted newline-separated text for use in a printf command."""
    return " ".join(f"'{line}'" for line in text.splitlines())
