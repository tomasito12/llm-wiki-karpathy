"""Shared proposal approve/reject bar and status helpers for entity review UIs."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.domain_tag_ui import find_review_node

DEFAULT_PROPOSAL_STATUS = "approved"


def normalized_proposal_status(node: dict[str, Any]) -> str:
    """Return proposal_status, treating legacy ``pending`` as approved."""
    raw = str(node.get("proposal_status") or DEFAULT_PROPOSAL_STATUS)
    if raw == "pending":
        return DEFAULT_PROPOSAL_STATUS
    return raw


def proposal_status_label(node: dict[str, Any]) -> str:
    """Human-readable status for edit-card header chip."""
    status = normalized_proposal_status(node)
    if status == "rejected":
        return "Rejected"
    if status == "deferred":
        return "Deferred"
    return "Approved"


def set_proposal_status_on_click(
    proposal_id: str,
    status: str,
    artifact_path: Path,
    review_list_key: str,
) -> None:
    """Streamlit on_click: set proposal_status and persist immediately."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    node = find_review_node(artifact, proposal_id, review_list_key)
    if not node:
        return
    node["proposal_status"] = status
    node.pop("_edit_mode", None)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)


def render_proposal_decision_bar(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
    artifact_path: Path,
    review_list_key: str,
    on_save_callback: Callable[[], None] | None = None,
    save_button_label: str = "Save edit & approve",
) -> None:
    """Bottom action row: Reject or Approve toggle plus optional save-and-approve."""
    proposal_id = str(node.get("proposal_id") or "")
    current = normalized_proposal_status(node)

    if on_save_callback is None:
        (action_col,) = st.columns(1)
        save_col = None
    else:
        action_col, save_col = st.columns(2)

    with action_col:
        if current == "rejected":
            st.button(
                "Approve",
                key=f"{key_prefix}_approve",
                on_click=set_proposal_status_on_click,
                args=(proposal_id, DEFAULT_PROPOSAL_STATUS, artifact_path, review_list_key),
                use_container_width=True,
            )
        else:
            st.button(
                "Reject",
                key=f"{key_prefix}_reject",
                on_click=set_proposal_status_on_click,
                args=(proposal_id, "rejected", artifact_path, review_list_key),
                use_container_width=True,
            )

    if save_col is not None and on_save_callback is not None:
        with save_col:
            if st.button(
                save_button_label,
                key=f"{key_prefix}_save",
                type="primary",
                use_container_width=True,
            ):
                node["proposal_status"] = DEFAULT_PROPOSAL_STATUS
                on_save_callback()
