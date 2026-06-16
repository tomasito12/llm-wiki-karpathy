"""Plan Stage 2 synthesis work from the Stage 1 graph export."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.wiki_synthesis.cache import (
    VALIDATION_STALE,
    cached_input_hash,
    load_cache_entry,
    validate_cache_entry,
)
from src.wiki_synthesis.input_hash import synthesis_input_hash
from src.wiki_synthesis.models import PlanEntry, PlanSummary, SynthesisPlan

KNOWLEDGE_PAGES_KEY = "knowledge_pages"
EVIDENCE_OBJECT_KEYS: tuple[str, ...] = (
    "signals",
    "interview_insights",
    "implementation_studies",
)


def load_graph_export(path: Path) -> dict[str, Any]:
    """Load a wiki-render graph export from disk."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        msg = f"Graph export must be a JSON object: {path}"
        raise ValueError(msg)
    return payload


def plan_from_graph(
    graph: dict[str, Any],
    *,
    cache_dir: Path,
    category: str | None = None,
    entity: str | None = None,
    include_single_source: bool = False,
    changed_only: bool = False,
    limit: int | None = None,
) -> SynthesisPlan:
    """Return a Stage 2 synthesis plan for a graph export."""
    all_entries = [
        _entry_for_page(page, cache_dir=cache_dir, include_single_source=include_single_source)
        for page in _knowledge_pages(graph)
        if _matches_filters(page, category=category, entity=entity)
    ]
    filtered = [
        entry
        for entry in all_entries
        if not changed_only or entry.state not in {"unchanged", "skipped_single_source"}
    ]
    if limit is not None:
        filtered = filtered[: max(0, limit)]
    summary = _summary(
        all_entries=all_entries,
        shown=len(filtered),
        skipped_evidence_object=_evidence_object_count(graph, category=category, entity=entity),
    )
    return SynthesisPlan(entries=filtered, summary=summary)


def _entry_for_page(
    page: dict[str, Any],
    *,
    cache_dir: Path,
    include_single_source: bool,
) -> PlanEntry:
    """Return a planning entry for one knowledge page."""
    category = str(page.get("category", ""))
    slug = str(page.get("slug", ""))
    current_hash = synthesis_input_hash(page)
    source_count = _int_value(page.get("source_count"))
    evidence_count = _int_value(page.get("evidence_count"))
    if source_count <= 1 and not include_single_source:
        state = "skipped_single_source"
        reason = "single-source knowledge pages are not synthesized by default"
        cached_hash = ""
    else:
        cache_entry = load_cache_entry(cache_dir, category=category, slug=slug)
        cached_hash = cached_input_hash(cache_entry)
        if cache_entry is None:
            state = "new"
            reason = "no synthesis cache entry exists"
        else:
            validation = validate_cache_entry(cache_entry, current_input_hash=current_hash)
            if not validation.is_usable:
                state = "error"
                reason = validation.reason
            elif validation.state == VALIDATION_STALE:
                state = "stale"
                reason = validation.reason
            else:
                state = "unchanged"
                reason = validation.reason
            cached_hash = validation.cached_input_hash
    return PlanEntry(
        entity_id=str(page.get("entity_id", "")),
        category=category,
        slug=slug,
        title=str(page.get("title", "")),
        path=str(page.get("path", "")),
        state=state,
        reason=reason,
        source_count=source_count,
        evidence_count=evidence_count,
        current_input_hash=current_hash,
        cached_input_hash=cached_hash,
    )


def _knowledge_pages(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Return knowledge-page dictionaries from a graph export."""
    pages = graph.get(KNOWLEDGE_PAGES_KEY, [])
    if not isinstance(pages, list):
        return []
    return [page for page in pages if isinstance(page, dict)]


def _matches_filters(
    page: dict[str, Any],
    *,
    category: str | None,
    entity: str | None,
) -> bool:
    """Return whether a page matches optional category/entity filters."""
    if category and page.get("category") != category:
        return False
    if entity and page.get("entity_id") != entity:
        return False
    return True


def _evidence_object_count(
    graph: dict[str, Any],
    *,
    category: str | None,
    entity: str | None,
) -> int:
    """Return skipped evidence-object count for unfiltered full-plan visibility."""
    if entity:
        return 0
    count = 0
    for key in EVIDENCE_OBJECT_KEYS:
        if category and category != _category_for_evidence_key(key):
            continue
        values = graph.get(key, [])
        if isinstance(values, list):
            count += len(values)
    return count


def _category_for_evidence_key(key: str) -> str:
    """Return graph category for an evidence-object collection key."""
    if key == "interview_insights":
        return "insight"
    if key == "implementation_studies":
        return "impl_study"
    return "signal"


def _summary(
    *,
    all_entries: list[PlanEntry],
    shown: int,
    skipped_evidence_object: int,
) -> PlanSummary:
    """Return summary counts for planning entries."""
    return PlanSummary(
        total=len(all_entries) + skipped_evidence_object,
        shown=shown,
        unchanged=_count_state(all_entries, "unchanged"),
        new=_count_state(all_entries, "new"),
        stale=_count_state(all_entries, "stale"),
        skipped_single_source=_count_state(all_entries, "skipped_single_source"),
        skipped_evidence_object=skipped_evidence_object,
        error=_count_state(all_entries, "error"),
    )


def _count_state(entries: list[PlanEntry], state: str) -> int:
    """Return number of entries in a state."""
    return sum(1 for entry in entries if entry.state == state)


def _int_value(value: object) -> int:
    """Return an integer for numeric JSON values."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float):
        return int(value)
    return 0
