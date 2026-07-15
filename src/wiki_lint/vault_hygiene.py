"""Read-only vault hygiene checks against the wiki-render manifest."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from src.wiki_contract.layout import is_managed_relative_path, is_preserved_wiki_path
from src.wiki_render.resolve import taxonomy_version
from src.wiki_render.scope import protected_prune_paths_for_in_progress

VaultHygieneCategory = Literal[
    "safe_delete_candidate",
    "protected_in_progress",
    "manual_review",
]

MANUAL_REVIEW_PREFIXES: tuple[str, ...] = (
    "legacy/",
    "notes/",
    "questions/",
)

MANUAL_ROOT_FILES: frozenset[str] = frozenset(
    {
        "AGENTS.md",
        "log.md",
    }
)


@dataclass(frozen=True)
class VaultHygieneItem:
    """One vault path that needs hygiene attention."""

    path: str
    category: VaultHygieneCategory
    reason: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable hygiene item."""
        return asdict(self)


@dataclass(frozen=True)
class VaultDuplicateGroup:
    """Exact duplicate markdown files sharing one content hash."""

    sha256: str
    paths: tuple[str, ...]
    recommended_keep: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable duplicate group."""
        return asdict(self)


@dataclass(frozen=True)
class VaultHygieneStatus:
    """Summary of vault files not tracked by the current render manifest."""

    manifest_exists: bool
    manifest_paths: int
    vault_markdown_files: int
    orphan_total: int
    safe_delete_candidates: tuple[VaultHygieneItem, ...]
    protected_in_progress: tuple[VaultHygieneItem, ...]
    manual_review: tuple[VaultHygieneItem, ...]
    manual_root_items: tuple[VaultHygieneItem, ...]
    duplicate_groups: tuple[VaultDuplicateGroup, ...]
    recommended_actions: tuple[str, ...]

    @property
    def needs_attention(self) -> bool:
        """Return True when hygiene findings require operator review."""
        return bool(
            self.safe_delete_candidates
            or self.duplicate_groups
            or (
                self.manifest_exists
                and self.orphan_total > len(self.protected_in_progress) + len(self.manual_review)
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable hygiene status snapshot."""
        return {
            "manifest_exists": self.manifest_exists,
            "manifest_paths": self.manifest_paths,
            "vault_markdown_files": self.vault_markdown_files,
            "orphan_total": self.orphan_total,
            "safe_delete_candidates": [item.to_dict() for item in self.safe_delete_candidates],
            "protected_in_progress": [item.to_dict() for item in self.protected_in_progress],
            "manual_review": [item.to_dict() for item in self.manual_review],
            "manual_root_items": [item.to_dict() for item in self.manual_root_items],
            "duplicate_groups": [group.to_dict() for group in self.duplicate_groups],
            "recommended_actions": list(self.recommended_actions),
        }


def load_manifest_paths(manifest_path: Path) -> set[str]:
    """Return relative wiki paths recorded in the render manifest."""
    if not manifest_path.is_file():
        return set()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    files = payload.get("files")
    if not isinstance(files, list):
        return set()
    paths: set[str] = set()
    for item in files:
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.add(item["path"])
    return paths


def duplicate_removal_paths(groups: tuple[VaultDuplicateGroup, ...]) -> tuple[str, ...]:
    """Return vault-relative duplicate paths that should be removed."""
    removals: list[str] = []
    for group in groups:
        removals.extend(path for path in group.paths if path != group.recommended_keep)
    return tuple(sorted(set(removals)))


def deletable_paths_from_status(status: VaultHygieneStatus) -> tuple[str, ...]:
    """Return all vault-relative paths eligible for automated cleanup."""
    keep_paths = {group.recommended_keep for group in status.duplicate_groups}
    paths = {
        item.path
        for item in status.safe_delete_candidates
        if item.path not in keep_paths
    }
    paths.update(duplicate_removal_paths(status.duplicate_groups))
    return tuple(sorted(paths))


def collect_vault_hygiene_status(
    *,
    wiki_dir: Path,
    manifest_path: Path,
    reviews_dir: Path,
    raw_dir: Path,
    repo_root: Path,
    synthesis_cache_dir: Path,
) -> tuple[VaultHygieneStatus, list[str]]:
    """Compare vault markdown files against the render manifest.

    Args:
        wiki_dir: Generated wiki root inside the private vault.
        manifest_path: Advisory wiki-render manifest path.
        reviews_dir: Human review artifacts directory.
        raw_dir: Canonical raw export directory.
        repo_root: Code repository root for taxonomy resolution.
        synthesis_cache_dir: Stage 2 synthesis cache directory.

    Returns:
        A hygiene status snapshot and actionable warning messages.
    """
    warnings: list[str] = []
    if not wiki_dir.is_dir():
        empty = VaultHygieneStatus(
            manifest_exists=manifest_path.is_file(),
            manifest_paths=len(load_manifest_paths(manifest_path)),
            vault_markdown_files=0,
            orphan_total=0,
            safe_delete_candidates=(),
            protected_in_progress=(),
            manual_review=(),
            manual_root_items=(),
            duplicate_groups=(),
            recommended_actions=("Verify wiki_dir path configuration.",),
        )
        return empty, [f"Vault hygiene cannot run; wiki directory missing: {wiki_dir}"]

    manifest_paths = load_manifest_paths(manifest_path)
    if not manifest_path.is_file():
        warnings.append(
            "Render manifest is missing; vault hygiene orphan counts are unavailable.",
        )

    vault_paths = {path.relative_to(wiki_dir).as_posix(): path for path in wiki_dir.rglob("*.md")}
    orphans = sorted(set(vault_paths) - manifest_paths)

    protected_paths = protected_prune_paths_for_in_progress(
        reviews_dir=reviews_dir,
        wiki_dir=wiki_dir,
        raw_dir=raw_dir,
        repo_root=repo_root,
        synthesis_cache_dir=synthesis_cache_dir,
        taxonomy_version=taxonomy_version(repo_root),
    )

    safe_delete: list[VaultHygieneItem] = []
    protected: list[VaultHygieneItem] = []
    manual: list[VaultHygieneItem] = []
    manual_root: list[VaultHygieneItem] = []

    for relpath in orphans:
        item = _classify_orphan(
            relpath,
            protected_paths=protected_paths,
        )
        if item.category == "safe_delete_candidate":
            safe_delete.append(item)
        elif item.category == "protected_in_progress":
            protected.append(item)
        else:
            manual.append(item)
        if _is_manual_root_item(relpath):
            manual_root.append(item)

    duplicate_groups = _find_duplicate_groups(vault_paths, manifest_paths=manifest_paths)
    recommended_actions = _recommended_actions(
        manifest_exists=manifest_path.is_file(),
        safe_delete_count=len(safe_delete),
        protected_count=len(protected),
        manual_count=len(manual),
        duplicate_group_count=len(duplicate_groups),
    )

    status = VaultHygieneStatus(
        manifest_exists=manifest_path.is_file(),
        manifest_paths=len(manifest_paths),
        vault_markdown_files=len(vault_paths),
        orphan_total=len(orphans),
        safe_delete_candidates=tuple(safe_delete),
        protected_in_progress=tuple(protected),
        manual_review=tuple(manual),
        manual_root_items=tuple(manual_root),
        duplicate_groups=tuple(duplicate_groups),
        recommended_actions=tuple(recommended_actions),
    )
    warnings.extend(_hygiene_warnings(status))
    return status, warnings


def format_vault_hygiene_text(status: VaultHygieneStatus) -> str:
    """Return a concise human-readable vault hygiene report."""
    lines = [
        "Vault Hygiene",
        f"- manifest paths: {status.manifest_paths}",
        f"- vault markdown files: {status.vault_markdown_files}",
        f"- orphan generated pages: {status.orphan_total}",
        f"- safe delete candidates: {len(status.safe_delete_candidates)}",
        f"- protected in-progress pages: {len(status.protected_in_progress)}",
        f"- manual review items: {len(status.manual_review)}",
        f"- exact duplicate groups: {len(status.duplicate_groups)}",
    ]
    if status.manual_root_items:
        lines.append(f"- manual root items: {len(status.manual_root_items)}")
    if status.recommended_actions:
        lines.extend(["", "Recommended actions"])
        for index, action in enumerate(status.recommended_actions, start=1):
            lines.append(f"{index}. {action}")
    return "\n".join(lines)


def _classify_orphan(
    relpath: str,
    *,
    protected_paths: set[str],
) -> VaultHygieneItem:
    """Classify one vault path that is absent from the render manifest."""
    if relpath in protected_paths:
        return VaultHygieneItem(
            path=relpath,
            category="protected_in_progress",
            reason="Generated from an in-progress review; protected from render prune.",
        )
    if _is_manual_vault_path(relpath):
        return VaultHygieneItem(
            path=relpath,
            category="manual_review",
            reason="Manual or preserved vault path outside the managed render manifest.",
        )
    if is_managed_relative_path(relpath):
        return VaultHygieneItem(
            path=relpath,
            category="safe_delete_candidate",
            reason="Managed generated page not present in the current render manifest.",
        )
    return VaultHygieneItem(
        path=relpath,
        category="manual_review",
        reason="Path is outside managed generated folders.",
    )


def _is_manual_vault_path(relpath: str) -> bool:
    """Return True when a path should be reviewed manually rather than auto-deleted."""
    if relpath in MANUAL_ROOT_FILES:
        return True
    if is_preserved_wiki_path(relpath):
        return True
    return any(relpath.startswith(prefix) for prefix in MANUAL_REVIEW_PREFIXES)


def _is_manual_root_item(relpath: str) -> bool:
    """Return True for high-salience manual root items from migration Finding 7."""
    if relpath in MANUAL_ROOT_FILES:
        return True
    if "/" not in relpath and relpath not in {"index.md"}:
        return True
    return any(relpath.startswith(prefix) for prefix in MANUAL_REVIEW_PREFIXES)


def _find_duplicate_groups(
    vault_paths: dict[str, Path],
    *,
    manifest_paths: set[str],
) -> list[VaultDuplicateGroup]:
    """Return exact duplicate groups among managed generated markdown files."""
    by_hash: dict[str, list[str]] = {}
    for relpath, path in vault_paths.items():
        if not is_managed_relative_path(relpath):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        by_hash.setdefault(digest, []).append(relpath)

    groups: list[VaultDuplicateGroup] = []
    for digest, paths in sorted(by_hash.items(), key=lambda item: item[1][0]):
        if len(paths) < 2:
            continue
        ordered = sorted(paths)
        recommended_keep = _recommended_duplicate_keep(ordered, manifest_paths=manifest_paths)
        groups.append(
            VaultDuplicateGroup(
                sha256=digest,
                paths=tuple(ordered),
                recommended_keep=recommended_keep,
            )
        )
    return groups


def _recommended_duplicate_keep(
    paths: list[str],
    *,
    manifest_paths: set[str],
) -> str:
    """Pick the path most likely to remain canonical among duplicates."""
    manifest_matches = [path for path in paths if path in manifest_paths]
    if manifest_matches:
        return sorted(manifest_matches, key=len)[0]
    return sorted(paths, key=len)[0]


def _recommended_actions(
    *,
    manifest_exists: bool,
    safe_delete_count: int,
    protected_count: int,
    manual_count: int,
    duplicate_group_count: int,
) -> list[str]:
    """Return operator guidance based on hygiene counts."""
    actions: list[str] = []
    if not manifest_exists:
        actions.append("Run wiki-render to create a current manifest before deleting orphans.")
    if safe_delete_count:
        actions.append(
            "Review safe-delete orphan candidates; rerun wiki-render with prune or delete "
            "manually after backup.",
        )
    if duplicate_group_count:
        actions.append(
            "Review exact duplicate groups and keep only the recommended path in each group.",
        )
    if manual_count:
        actions.append(
            "Review manual or preserved vault paths (legacy/, notes/, questions/, root files) "
            "before archiving or deleting.",
        )
    if protected_count and not safe_delete_count and not duplicate_group_count:
        actions.append(
            "In-progress protected source pages are expected until reviews are finished.",
        )
    if not actions:
        actions.append("No vault hygiene action required.")
    return actions


def _hygiene_warnings(status: VaultHygieneStatus) -> list[str]:
    """Return top-level warning strings for ops status integration."""
    warnings: list[str] = []
    if status.safe_delete_candidates:
        warnings.append(
            f"Vault has {len(status.safe_delete_candidates)} stale generated orphan page(s).",
        )
    if status.duplicate_groups:
        warnings.append(
            f"Vault has {len(status.duplicate_groups)} exact duplicate markdown group(s).",
        )
    if status.manual_root_items:
        warnings.append(
            f"Vault has {len(status.manual_root_items)} manual root or legacy item(s) to review.",
        )
    return warnings
