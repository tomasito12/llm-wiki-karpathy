"""Tests for dashboard review queue selection helpers."""

from __future__ import annotations

from src.dashboard.review_queue_ui import (
    FILTER_AFTER_ANALYZE,
    PENDING_QUEUE_FILTER_KEY,
    apply_pending_queue_filter,
    build_source_selectbox_ids,
    queue_queue_filter_change,
    resolve_review_source_id,
    source_review_mode_session_key,
    source_widget_key_prefix,
)


def test_source_widget_key_prefix_uses_full_source_id() -> None:
    """Widget prefixes must not truncate IDs that share a 40-char prefix."""
    source_id = (
        "ainews-microsoft-build-mai-thinking-1-and-mai-family-models-01kt60w6z2qjzjg1hvr1wbz60g"
    )
    assert source_widget_key_prefix(source_id) == source_id
    assert source_widget_key_prefix(source_id) != source_id[:40]


def test_source_review_mode_session_key_is_unique_per_full_source_id() -> None:
    """Review-mode keys must differ for sources that only diverge after char 40."""
    a = "giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb"
    b = "giving-agents-computers-ivan-burazin-daytona-01ks64hjy5db7k6jfrxrnbaznb"
    assert source_review_mode_session_key(a) != source_review_mode_session_key(b)


def test_build_source_selectbox_ids_pins_filtered_out_current_source() -> None:
    """An active in-progress source stays selectable under a not-started filter."""
    visible = ["other-not-started"]
    current = "analyzed-in-progress"
    all_ids = {visible[0], current}

    selectbox_ids, pinned = build_source_selectbox_ids(
        visible,
        current_source_id=current,
        all_source_ids=all_ids,
    )

    assert pinned == current
    assert selectbox_ids == [current, "other-not-started"]


def test_build_source_selectbox_ids_leaves_visible_list_when_current_matches_filter() -> None:
    """No pin is added when the current source already matches the filter."""
    visible = ["a", "b"]
    selectbox_ids, pinned = build_source_selectbox_ids(
        visible,
        current_source_id="a",
        all_source_ids={"a", "b"},
    )
    assert pinned is None
    assert selectbox_ids == ["a", "b"]


def test_resolve_review_source_id_keeps_pinned_current_source() -> None:
    """Pinned sources must not reset to the first visible not-started item."""
    visible = ["other-not-started"]
    selectbox = ["analyzed-in-progress", "other-not-started"]

    resolved = resolve_review_source_id(
        selectbox,
        visible,
        current_source_id="analyzed-in-progress",
        pick_id=None,
    )

    assert resolved == "analyzed-in-progress"


def test_resolve_review_source_id_honors_pick_id() -> None:
    """Explicit pick_id overrides the current selection when it is valid."""
    resolved = resolve_review_source_id(
        ["a", "b"],
        ["a", "b"],
        current_source_id="a",
        pick_id="b",
    )
    assert resolved == "b"


def test_resolve_review_source_id_falls_back_to_first_visible() -> None:
    """Invalid current ids fall back to the first filter-visible source."""
    resolved = resolve_review_source_id(
        ["visible-a", "visible-b"],
        ["visible-a", "visible-b"],
        current_source_id="missing",
        pick_id=None,
    )
    assert resolved == "visible-a"


def test_filter_after_analyze_is_in_progress() -> None:
    """Analyze should move the queue filter to in-progress articles."""
    assert FILTER_AFTER_ANALYZE == "In progress"


def test_queue_and_apply_pending_filter_before_widget() -> None:
    """Filter changes must be queued and applied before the radio widget renders."""
    state: dict[str, object] = {"review_queue_filter_radio": "Not started"}

    queue_queue_filter_change(state, FILTER_AFTER_ANALYZE)
    assert state[PENDING_QUEUE_FILTER_KEY] == FILTER_AFTER_ANALYZE
    assert state["review_queue_filter_radio"] == "Not started"

    apply_pending_queue_filter(state)
    assert state["review_queue_filter_radio"] == FILTER_AFTER_ANALYZE
    assert PENDING_QUEUE_FILTER_KEY not in state
