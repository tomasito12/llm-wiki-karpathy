"""Fast single-column proposal review layout (navigator + compact cards)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.proposal_decision_ui import (
    pop_proposal_save_message,
    proposal_status_label,
    render_proposal_save_button,
    render_proposal_status_toggle,
)
from src.ingest_review.proposal_regen_ui import (
    _queue_proposal_regen,
    render_reclassify_to_section_controls,
)


@dataclass(frozen=True)
class CollapsedFieldSpec:
    """One scalar or list field inside the \"More fields\" expander."""

    key: str
    label: str
    tall: bool = False
    is_list: bool = False
    help_text: str | None = None


LabelForNode = Callable[[dict[str, Any], int], str]
RenderEditForNode = Callable[[dict[str, Any], int], None]
GetFieldValue = Callable[[dict[str, Any], dict[str, Any], str], str]


def proposal_autosave_session_key(registry_key: str) -> str:
    """Session-state key for the leave-card autosave callback."""
    return f"{registry_key}_proposal_autosave"


def register_card_autosave(
    registry_key: str,
    node: dict[str, Any],
    persist_callback: Callable[[], None],
) -> None:
    """Register persist-on-leave for Prev/Next and entity-tab switches."""
    from src.ingest_review.proposal_decision_ui import (
        DEFAULT_PROPOSAL_STATUS,
        normalized_proposal_status,
    )

    def _on_leave() -> None:
        persist_callback()
        if normalized_proposal_status(node) != "rejected":
            node["proposal_status"] = DEFAULT_PROPOSAL_STATUS

    streamlit_runtime.session_state[proposal_autosave_session_key(registry_key)] = _on_leave


def run_proposal_autosave(registry_key: str) -> bool:
    """Run registered autosave, if any. Returns True when a callback ran."""
    callback = streamlit_runtime.session_state.get(proposal_autosave_session_key(registry_key))
    if not callable(callback):
        return False
    callback()
    return True


def clear_proposal_autosave(registry_key: str) -> None:
    """Remove a registered autosave callback (e.g. when a tab has no proposals)."""
    streamlit_runtime.session_state.pop(proposal_autosave_session_key(registry_key), None)


def navigator_session_key(key_prefix: str) -> str:
    """Session-state key for the active proposal index within a tab."""
    return f"{key_prefix}_proposal_idx"


def clamp_proposal_index(index: int, count: int) -> int:
    """Clamp *index* to ``[0, count-1]`` (or 0 when empty)."""
    if count <= 0:
        return 0
    return max(0, min(index, count - 1))


def format_navigator_label(index: int, count: int, title: str) -> str:
    """Human-readable navigator caption: ``Proposal 2 of 5: Title``."""
    safe_title = title.strip() or "Untitled"
    if len(safe_title) > 72:
        safe_title = safe_title[:69] + "…"
    return f"Proposal {index + 1} of {count}: {safe_title}"


def render_proposal_navigator(
    st: Any,
    nodes: list[dict[str, Any]],
    *,
    key_prefix: str,
    label_for_node: LabelForNode,
) -> int:
    """Prev/next controls; returns the active proposal index."""
    count = len(nodes)
    if count <= 1:
        streamlit_runtime.session_state[navigator_session_key(key_prefix)] = 0
        if count == 1:
            st.caption(format_navigator_label(0, 1, label_for_node(nodes[0], 0)))
        return 0

    idx_key = navigator_session_key(key_prefix)
    raw_idx = int(streamlit_runtime.session_state.get(idx_key, 0) or 0)
    index = clamp_proposal_index(raw_idx, count)
    streamlit_runtime.session_state[idx_key] = index

    prev_col, label_col, next_col = st.columns([1, 4, 1])
    with prev_col:
        if st.button("◀ Prev", key=f"{key_prefix}_nav_prev", use_container_width=True):
            run_proposal_autosave(key_prefix)
            streamlit_runtime.session_state[idx_key] = clamp_proposal_index(index - 1, count)
            st.rerun()
    with label_col:
        st.markdown(
            f"**{format_navigator_label(index, count, label_for_node(nodes[index], index))}**"
        )
    with next_col:
        if st.button("Next ▶", key=f"{key_prefix}_nav_next", use_container_width=True):
            run_proposal_autosave(key_prefix)
            streamlit_runtime.session_state[idx_key] = clamp_proposal_index(index + 1, count)
            st.rerun()
    return int(streamlit_runtime.session_state.get(idx_key, index) or index)


def render_fast_proposal_review(
    st: Any,
    nodes: list[dict[str, Any]],
    *,
    key_prefix: str,
    empty_readonly_text: str,
    label_for_node: LabelForNode,
    render_edit_for_node: RenderEditForNode,
) -> None:
    """Single-column review: navigator when multiple proposals, one edit card."""
    if not nodes:
        st.markdown(empty_readonly_text)
        return
    index = render_proposal_navigator(
        st,
        nodes,
        key_prefix=key_prefix,
        label_for_node=label_for_node,
    )
    index = clamp_proposal_index(index, len(nodes))
    render_edit_for_node(nodes[index], index)


def render_fast_card_header(
    st: Any,
    node: dict[str, Any],
    *,
    badge: str,
    key_prefix: str,
    artifact_path: Path,
    review_list_key: str,
) -> None:
    """Value badge, status chip, and Reject/Approve toggle at the top of a card."""
    status_lbl = proposal_status_label(node)
    header_col, action_col = st.columns([3, 1])
    with header_col:
        st.markdown(f"**{badge}** · **{status_lbl}**")
    with action_col:
        render_proposal_status_toggle(
            st,
            node,
            key_prefix=f"{key_prefix}_header",
            artifact_path=artifact_path,
            review_list_key=review_list_key,
        )


def render_readonly_context_hint(
    st: Any,
    *,
    label: str,
    value: str,
) -> None:
    """Show non-editable context above a title field (editable copy lives in an expander)."""
    text = value.strip()
    if not text:
        return
    st.caption(label)
    st.markdown(text)


def render_inline_regenerate_title_controls(
    st: Any,
    *,
    entity_key: str,
    source_id: str,
    proposal_id: str,
    widget_prefix: str,
    current_title: str,
    title_label: str = "New page title",
) -> None:
    """New title on its own row; note + regenerate share a second row with room for the label."""
    st.text_input(
        title_label,
        key=f"{widget_prefix}_regen_new_title",
        label_visibility="collapsed",
        placeholder=f"New title (empty = suggest; current: {current_title})",
    )
    note_col, btn_col = st.columns([4, 2], vertical_alignment="bottom")
    with note_col:
        st.text_input(
            "Regen note",
            key=f"{widget_prefix}_regen_note",
            label_visibility="collapsed",
            placeholder="Optional note for regeneration",
        )
    with btn_col:
        st.button(
            "Regenerate",
            key=f"{widget_prefix}_btn_regen",
            on_click=_queue_proposal_regen,
            args=(entity_key, source_id, proposal_id, widget_prefix),
            use_container_width=True,
        )


def render_context_expander(
    st: Any,
    *,
    label: str,
    field_key: str,
    field_label: str,
    value: str,
    widget_key: str,
    field_values: dict[str, str],
    tall: bool = True,
    extra_fields: list[tuple[str, str, str, bool]] | None = None,
) -> None:
    """Collapsed description/context textarea (and optional companion fields)."""
    with st.expander(label, expanded=False):
        field_values[field_key] = st.text_area(
            field_label,
            value=value,
            height=160 if tall else 100,
            key=widget_key,
        )
        if extra_fields:
            for ek, elabel, evalue, etall in extra_fields:
                field_values[ek] = st.text_area(
                    elabel,
                    value=evalue,
                    height=120 if etall else 72,
                    key=f"{widget_key}_{ek}",
                )


def render_collapsed_fields(
    st: Any,
    *,
    specs: list[CollapsedFieldSpec],
    get_value: GetFieldValue,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    key_prefix: str,
    field_values: dict[str, str],
    extra_content: Callable[[], None] | None = None,
) -> None:
    """Render secondary scalar/list fields inside a collapsed expander."""
    if not specs and extra_content is None:
        return
    with st.expander("More fields", expanded=False):
        for spec in specs:
            value = get_value(llm_item, sections, spec.key)
            if spec.is_list:
                field_values[spec.key] = st.text_area(
                    spec.label,
                    value=value,
                    height=100,
                    key=f"{key_prefix}_more_{spec.key}",
                    help=spec.help_text or "One bullet per line.",
                )
            else:
                field_values[spec.key] = st.text_area(
                    spec.label,
                    value=value,
                    height=120 if spec.tall else 72,
                    key=f"{key_prefix}_more_{spec.key}",
                    help=spec.help_text,
                )
        if extra_content is not None:
            extra_content()


def render_source_evidence_expander(st: Any, llm_item: dict[str, Any]) -> None:
    """Read-only supporting snippet when present."""
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    if not snippet:
        return
    with st.expander("Source evidence (read-only)", expanded=False):
        st.text(snippet[:4000] + ("…" if len(snippet) > 4000 else ""))


def render_fast_card_save_row(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
    artifact_path: Path,
    review_list_key: str,
    on_save_callback: Callable[[], None],
    save_button_label: str = "Save tags & approve",
) -> None:
    """Primary save button and confirmation message."""
    render_proposal_save_button(
        st,
        node,
        key_prefix=key_prefix,
        artifact_path=artifact_path,
        review_list_key=review_list_key,
        on_save_callback=on_save_callback,
        save_button_label=save_button_label,
    )
    save_msg = pop_proposal_save_message(key_prefix)
    if save_msg:
        st.success(save_msg)


def fast_card_widget_key(key_prefix: str, field_key: str, *, zone: str) -> str:
    """Session-state widget key for a field in title, context, or more zone."""
    if zone == "title":
        return f"{key_prefix}_edit_{field_key}"
    if zone == "context":
        return f"{key_prefix}_ctx_{field_key}"
    if zone == "more":
        return f"{key_prefix}_more_{field_key}"
    msg = f"unknown zone: {zone}"
    raise ValueError(msg)


def context_companion_widget_key(
    key_prefix: str,
    parent_context_key: str,
    field_key: str,
) -> str:
    """Widget key for a secondary field nested under a context expander."""
    return f"{key_prefix}_ctx_{parent_context_key}_{field_key}"


def read_fast_card_field_values(
    key_prefix: str,
    *,
    title_keys: tuple[str, ...] = (),
    context_keys: tuple[str, ...] = (),
    context_companion_fields: tuple[tuple[str, str], ...] = (),
    more_scalar_keys: tuple[str, ...] = (),
    more_list_keys: tuple[str, ...] = (),
    field_values: dict[str, str] | None = None,
) -> dict[str, str]:
    """Merge in-memory widget returns with session state (save row may run before lower widgets)."""
    merged: dict[str, str] = dict(field_values or {})
    for key in title_keys:
        merged[key] = str(
            streamlit_runtime.session_state.get(
                fast_card_widget_key(key_prefix, key, zone="title"), ""
            )
        )
    for key in context_keys:
        merged[key] = str(
            streamlit_runtime.session_state.get(
                fast_card_widget_key(key_prefix, key, zone="context"), ""
            )
        )
    for field_key, parent_context_key in context_companion_fields:
        merged[field_key] = str(
            streamlit_runtime.session_state.get(
                context_companion_widget_key(key_prefix, parent_context_key, field_key),
                "",
            )
        )
    for key in (*more_scalar_keys, *more_list_keys):
        merged[key] = str(
            streamlit_runtime.session_state.get(
                fast_card_widget_key(key_prefix, key, zone="more"), ""
            )
        )
    return merged


def render_fast_card_reclassify(
    st: Any,
    node: dict[str, Any],
    *,
    reclassify_entity_key: str,
    source_id: str,
    current_title: str,
    key_prefix: str,
) -> None:
    """Optional move-to-section controls at the bottom of a card."""
    proposal_id = str(node.get("proposal_id") or "")
    render_reclassify_to_section_controls(
        st,
        source_entity_key=reclassify_entity_key,
        source_id=source_id,
        proposal_id=proposal_id,
        widget_prefix=key_prefix,
        current_title=current_title,
        title_label="Title in target section",
    )
