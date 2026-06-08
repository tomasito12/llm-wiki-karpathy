"""Helpers for ingest-review source queue selection in the dashboard."""

from __future__ import annotations

from typing import Any

FILTER_AFTER_ANALYZE = "In progress"
PENDING_QUEUE_FILTER_KEY = "_pending_queue_filter_radio"


def apply_pending_queue_filter(session_state: Any) -> None:
    """Apply a queued filter change before the filter radio widget renders."""
    pending = session_state.pop(PENDING_QUEUE_FILTER_KEY, None)
    if isinstance(pending, str) and pending.strip():
        session_state["review_queue_filter_radio"] = pending.strip()


def queue_queue_filter_change(session_state: Any, filter_label: str) -> None:
    """Queue a filter change for the next script run (safe after widgets render)."""
    session_state[PENDING_QUEUE_FILTER_KEY] = filter_label


def source_widget_key_prefix(source_id: str) -> str:
    """Return a collision-free Streamlit widget prefix for one source."""
    return source_id


def source_review_mode_session_key(source_id: str) -> str:
    """Session-state key for skip-extraction review mode on one source."""
    return f"{source_widget_key_prefix(source_id)}_review_mode"


def build_source_selectbox_ids(
    visible_ids: list[str],
    *,
    current_source_id: str | None,
    all_source_ids: set[str],
) -> tuple[list[str], str | None]:
    """Return selectbox options, pinning the active source when the filter hides it."""
    if (
        current_source_id
        and current_source_id in all_source_ids
        and current_source_id not in visible_ids
    ):
        return [current_source_id, *visible_ids], current_source_id
    return list(visible_ids), None


def resolve_review_source_id(
    selectbox_ids: list[str],
    visible_ids: list[str],
    *,
    current_source_id: object,
    pick_id: str | None,
) -> str:
    """Choose ``review_source_id`` before rendering the source selectbox."""
    if pick_id and pick_id in selectbox_ids:
        return pick_id
    if isinstance(current_source_id, str) and current_source_id in selectbox_ids:
        return current_source_id
    if visible_ids:
        return visible_ids[0]
    if selectbox_ids:
        return selectbox_ids[0]
    return ""
