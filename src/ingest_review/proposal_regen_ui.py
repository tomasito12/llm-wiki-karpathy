"""Shared Streamlit helpers for per-proposal title regeneration."""

from __future__ import annotations

from typing import Any

import streamlit as streamlit_runtime


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
) -> None:
    new_title = str(
        streamlit_runtime.session_state.get(f"{widget_prefix}_regen_new_title", "")
    ).strip()
    note = str(streamlit_runtime.session_state.get(f"{widget_prefix}_regen_note", "")).strip()
    streamlit_runtime.session_state["_pending_proposal_regen"] = {
        "entity": entity_key,
        "source_id": source_id,
        "proposal_id": proposal_id,
        "new_title": new_title,
        "note": note,
    }


def pop_proposal_regen_msg(entity_key: str) -> str | None:
    """Pop success message for *entity_key* after app-level regeneration."""
    raw = streamlit_runtime.session_state.pop("_proposal_regen_msg", None)
    if isinstance(raw, dict) and raw.get("entity") == entity_key:
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
