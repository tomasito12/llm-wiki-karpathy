"""Shared Streamlit helpers for per-proposal title regeneration."""

from __future__ import annotations

from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.proposal_transfer import TRANSFER_TARGET_OPTIONS, transfer_target_label

ENTITY_REVIEW_TAB_BY_KEY: dict[str, str] = {
    "glossary": "Glossary",
    "topic": "Topics",
    "how_to": "How-tos",
    "trend": "Trends",
    "tool": "Tools",
    "model": "Models",
    "impl_study": "Impl studies",
    "signal": "Signals",
    "insight": "Insights",
}


def entity_review_tab_for_key(entity_key: str) -> str | None:
    """Map regeneration entity key to dashboard ``review_entity_tab`` radio label."""
    return ENTITY_REVIEW_TAB_BY_KEY.get(entity_key)


def preserve_review_entity_tab_for_regen(entity_key: str) -> None:
    """Keep the dashboard on the matching entity tab across ``st.rerun()`` after regen."""
    tab = entity_review_tab_for_key(entity_key)
    if tab:
        streamlit_runtime.session_state["review_entity_tab"] = tab


def proposal_edit_key_prefix(
    source_key_prefix: str,
    proposal_id: str,
    entity_short_prefix: str,
    *,
    regen_count: int = 0,
) -> str:
    """Widget key prefix; *regen_count* bumps after LLM regen so inputs reset."""
    return f"{source_key_prefix}_{entity_short_prefix}_{proposal_id}_r{regen_count}"


def regen_count_from_node(node: dict[str, Any]) -> int:
    meta = node.get("proposal_regeneration_meta")
    if isinstance(meta, dict):
        return int(meta.get("regen_count") or 0)
    return 0


def render_proposal_regen_meta_caption(st: Any, node: dict[str, Any], entity_label: str) -> None:
    meta = node.get("proposal_regeneration_meta")
    if isinstance(meta, dict) and meta.get("last_regen_at"):
        cnt = meta.get("regen_count", 0)
        when = meta["last_regen_at"]
        mdl = meta.get("model", "")
        pv = meta.get("prompt_version", "")
        st.caption(f"{entity_label} regen: **{cnt}×** · last **{when}** · `{mdl}` · prompt `{pv}`")


def _queue_proposal_regen(
    entity_key: str,
    source_id: str,
    proposal_id: str,
    widget_prefix: str,
    *,
    target_entity: str | None = None,
) -> None:
    new_title = str(
        streamlit_runtime.session_state.get(f"{widget_prefix}_regen_new_title", "")
    ).strip()
    note = str(streamlit_runtime.session_state.get(f"{widget_prefix}_regen_note", "")).strip()
    pending: dict[str, str] = {
        "entity": entity_key,
        "source_id": source_id,
        "proposal_id": proposal_id,
        "new_title": new_title,
        "note": note,
    }
    if target_entity and target_entity != entity_key:
        pending["target_entity"] = target_entity
    streamlit_runtime.session_state["_pending_proposal_regen"] = pending


def pop_proposal_regen_msg(entity_key: str) -> str | None:
    """Pop success message for *entity_key* after app-level regeneration."""
    raw = streamlit_runtime.session_state.get("_proposal_regen_msg")
    if isinstance(raw, dict) and raw.get("entity") == entity_key:
        text = raw.get("text")
        streamlit_runtime.session_state.pop("_proposal_regen_msg", None)
        return str(text) if text else None
    return None


def consume_proposal_regen_banner() -> str | None:
    """Pop and return any pending proposal regen/transfer success message."""
    raw = streamlit_runtime.session_state.pop("_proposal_regen_msg", None)
    if isinstance(raw, dict):
        text = raw.get("text")
        return str(text) if text else None
    return None


def render_regenerate_with_new_title_controls(
    st: Any,
    *,
    entity_key: str,
    source_id: str,
    proposal_id: str,
    widget_prefix: str,
    current_title: str,
    title_label: str = "New page title",
    title_help: str | None = None,
) -> None:
    """Regen title input, optional note, and queue button (above decision bar)."""
    st.text_input(
        title_label,
        value=current_title,
        key=f"{widget_prefix}_regen_new_title",
        help=title_help
        or "Reframe this proposal under a broader wiki page title before regenerating.",
    )
    st.text_input(
        "Optional note for regeneration",
        key=f"{widget_prefix}_regen_note",
        placeholder="e.g. keep specifics in the summary, not the title",
    )
    st.button(
        "Regenerate with new title",
        key=f"{widget_prefix}_btn_regen",
        on_click=_queue_proposal_regen,
        args=(entity_key, source_id, proposal_id, widget_prefix),
        use_container_width=True,
    )


def render_reclassify_to_section_controls(
    st: Any,
    *,
    source_entity_key: str,
    source_id: str,
    proposal_id: str,
    widget_prefix: str,
    current_title: str,
    title_label: str = "Title in target section",
) -> None:
    """Let reviewer move this proposal to another wiki section via LLM regeneration."""
    options = TRANSFER_TARGET_OPTIONS.get(source_entity_key, [])
    if not options:
        return

    with st.expander("Move to another section", expanded=False):
        st.caption(
            "Re-extract this proposal under a different wiki entity "
            "(e.g. trend → topic). The item is removed from the current tab "
            "and appears under the target tab."
        )
        labels = [label for _, label in options]
        keys = [key for key, _ in options]
        choice_idx = st.selectbox(
            "Target section",
            range(len(labels)),
            format_func=lambda i: labels[i],
            key=f"{widget_prefix}_transfer_target",
        )
        target_entity = keys[choice_idx]
        target_label = transfer_target_label(source_entity_key, target_entity)

        st.text_input(
            title_label,
            value=current_title,
            key=f"{widget_prefix}_transfer_new_title",
            help="Wiki page title for the target section.",
        )
        st.text_input(
            "Optional note for reclassification",
            key=f"{widget_prefix}_transfer_note",
            placeholder="e.g. this is a durable topic, not a time-bound trend",
        )

        def _queue_transfer() -> None:
            new_title = str(
                streamlit_runtime.session_state.get(f"{widget_prefix}_transfer_new_title", "")
            ).strip()
            note = str(
                streamlit_runtime.session_state.get(f"{widget_prefix}_transfer_note", "")
            ).strip()
            pending: dict[str, str] = {
                "entity": source_entity_key,
                "target_entity": target_entity,
                "source_id": source_id,
                "proposal_id": proposal_id,
                "new_title": new_title,
                "note": note,
            }
            streamlit_runtime.session_state["_pending_proposal_regen"] = pending

        st.button(
            f"Regenerate as {target_label}",
            key=f"{widget_prefix}_btn_transfer",
            on_click=_queue_transfer,
            use_container_width=True,
            type="primary",
        )
