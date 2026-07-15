"""Write generated wiki files with advisory manifest and safe prune."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json, atomic_write_text
from src.wiki_render import layout
from src.wiki_render.models import RenderedFile


@dataclass(frozen=True)
class WriteReport:
    """Summary of a render write run."""

    planned: int
    written: int
    unchanged: int
    pruned: int
    skipped_prune: bool
    protected_from_prune: int = 0
    write_paths: tuple[str, ...] = ()
    prune_paths: tuple[str, ...] = ()


def write_rendered_files(
    *,
    wiki_dir: Path,
    files: list[RenderedFile],
    manifest_path: Path,
    run_metadata: dict[str, Any],
    dry_run: bool = False,
    prune: bool = True,
    protected_paths: set[str] | None = None,
) -> WriteReport:
    """Write rendered files and advisory manifest."""
    unique = _unique_files(files)
    written = 0
    unchanged = 0
    write_paths: list[str] = []
    for rendered in unique:
        target = wiki_dir / rendered.relative_path
        if target.exists() and target.read_text(encoding="utf-8") == rendered.text:
            unchanged += 1
            continue
        write_paths.append(rendered.relative_path)
        if not dry_run:
            atomic_write_text(target, rendered.text)
        written += 1

    previous_paths = _previous_manifest_paths(manifest_path)
    current_paths = {rendered.relative_path for rendered in unique}
    pruned = 0
    protected_from_prune = 0
    skipped_prune = False
    protected = protected_paths or set()
    prune_paths: list[str] = []
    stale_paths = sorted(previous_paths - current_paths)
    if prune and previous_paths:
        for rel in stale_paths:
            if rel in protected:
                protected_from_prune += 1
                continue
            if not layout.is_managed_relative_path(rel):
                continue
            target = wiki_dir / rel
            if target.is_file():
                prune_paths.append(rel)
                if not dry_run:
                    target.unlink()
                pruned += 1
    elif prune and not previous_paths:
        skipped_prune = True

    manifest = {
        **run_metadata,
        "files": [
            {
                "path": rendered.relative_path,
                "sha256": hashlib.sha256(rendered.text.encode("utf-8")).hexdigest(),
            }
            for rendered in unique
        ],
    }
    if not dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(manifest_path, manifest)
    return WriteReport(
        planned=len(unique),
        written=written,
        unchanged=unchanged,
        pruned=pruned,
        skipped_prune=skipped_prune,
        protected_from_prune=protected_from_prune,
        write_paths=tuple(write_paths),
        prune_paths=tuple(prune_paths),
    )


def _unique_files(files: list[RenderedFile]) -> list[RenderedFile]:
    """Return one rendered file per relative path."""
    by_path: dict[str, RenderedFile] = {}
    for rendered in files:
        by_path[rendered.relative_path] = rendered
    return [by_path[path] for path in sorted(by_path)]


def _previous_manifest_paths(manifest_path: Path) -> set[str]:
    """Read previous generated relative paths from a manifest."""
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
