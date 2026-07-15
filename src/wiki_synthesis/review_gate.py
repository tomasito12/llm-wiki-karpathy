"""Gate Stage 2 synthesis to fully finished review evidence."""

from __future__ import annotations

from typing import Any


def knowledge_page_source_ids(page: dict[str, Any]) -> set[str]:
    """Return source ids referenced by one knowledge page."""
    source_ids = page.get("source_ids")
    ids: set[str] = set()
    if isinstance(source_ids, list):
        ids.update(str(item).strip() for item in source_ids if str(item).strip())
    if ids:
        return ids
    evidence = page.get("evidence")
    if not isinstance(evidence, list):
        return ids
    for item in evidence:
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("source_id") or "").strip()
        if source_id:
            ids.add(source_id)
    return ids


def page_uses_only_finished_sources(
    page: dict[str, Any],
    finished_source_ids: set[str],
) -> bool:
    """Return whether every source on a knowledge page is finished."""
    source_ids = knowledge_page_source_ids(page)
    if not source_ids:
        return False
    return source_ids.issubset(finished_source_ids)
