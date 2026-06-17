"""Lint Stage 2 synthesis cache entries against the current graph."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.wiki_synthesis.cache import cache_file_path, load_cache_entry, validate_cache_entry
from src.wiki_synthesis.input_hash import synthesis_input_hash


@dataclass(frozen=True)
class CacheLintItem:
    """One synthesis cache lint result."""

    entity_id: str
    category: str
    slug: str
    title: str
    cache_path: str
    severity: str
    state: str
    reason: str
    current_input_hash: str
    cached_input_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable lint item."""
        return asdict(self)


@dataclass(frozen=True)
class CacheLintReport:
    """Summary of synthesis cache lint results."""

    checked: int
    ok: int
    warnings: int
    errors: int
    items: list[CacheLintItem]

    @property
    def exit_code(self) -> int:
        """Return shell exit code for this report."""
        return 1 if self.errors else 0

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable lint report."""
        return {
            "checked": self.checked,
            "ok": self.ok,
            "warnings": self.warnings,
            "errors": self.errors,
            "items": [item.to_dict() for item in self.items],
        }


def lint_synthesis_cache(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    category: str | None = None,
    entity: str | None = None,
    include_missing: bool = False,
) -> CacheLintReport:
    """Lint synthesis cache entries for graph pages and orphan files."""
    pages = _matching_pages(graph, category=category, entity=entity)
    graph_keys = {(str(page.get("category", "")), str(page.get("slug", ""))) for page in pages}
    items: list[CacheLintItem] = []
    for page in pages:
        cache_path = cache_file_path(
            cache_dir,
            category=str(page.get("category", "")),
            slug=str(page.get("slug", "")),
        )
        if not cache_path.exists() and not include_missing:
            continue
        items.append(_lint_page_cache(page, cache_dir=cache_dir))
    items.extend(
        _orphan_items(
            cache_dir,
            graph_keys=graph_keys,
            category=category,
            entity=entity,
        )
    )
    return CacheLintReport(
        checked=len(items),
        ok=sum(1 for item in items if item.severity == "ok"),
        warnings=sum(1 for item in items if item.severity == "warning"),
        errors=sum(1 for item in items if item.severity == "error"),
        items=items,
    )


def _lint_page_cache(page: dict[str, Any], *, cache_dir: Path) -> CacheLintItem:
    """Lint one graph page cache entry."""
    category = str(page.get("category", ""))
    slug = str(page.get("slug", ""))
    current_hash = synthesis_input_hash(page)
    entry = load_cache_entry(cache_dir, category=category, slug=slug)
    validation = validate_cache_entry(entry, current_input_hash=current_hash)
    if validation.state == "fresh":
        severity = "ok"
    elif validation.state == "stale":
        severity = "warning"
    else:
        severity = "error"
    return CacheLintItem(
        entity_id=str(page.get("entity_id", "")),
        category=category,
        slug=slug,
        title=str(page.get("title", "")),
        cache_path=str(cache_file_path(cache_dir, category=category, slug=slug)),
        severity=severity,
        state=validation.state,
        reason=validation.reason,
        current_input_hash=validation.current_input_hash,
        cached_input_hash=validation.cached_input_hash,
    )


def _orphan_items(
    cache_dir: Path,
    *,
    graph_keys: set[tuple[str, str]],
    category: str | None,
    entity: str | None,
) -> list[CacheLintItem]:
    """Return lint items for cache files without graph pages."""
    if entity:
        return []
    items: list[CacheLintItem] = []
    for path in sorted(cache_dir.glob("*/*.json")):
        cat = path.parent.name
        slug = path.stem
        if category and cat != category:
            continue
        if (cat, slug) in graph_keys:
            continue
        items.append(
            CacheLintItem(
                entity_id=f"{cat}:{slug}",
                category=cat,
                slug=slug,
                title=slug,
                cache_path=str(path),
                severity="error",
                state="orphan",
                reason="cache file has no matching graph page",
                current_input_hash="",
                cached_input_hash="",
            )
        )
    return items


def _matching_pages(
    graph: dict[str, Any],
    *,
    category: str | None,
    entity: str | None,
) -> list[dict[str, Any]]:
    """Return graph pages matching optional filters."""
    pages = graph.get("knowledge_pages", [])
    if not isinstance(pages, list):
        return []
    result: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        if category and page.get("category") != category:
            continue
        if entity and page.get("entity_id") != entity:
            continue
        result.append(page)
    return result
