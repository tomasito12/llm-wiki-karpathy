"""Shared proposal approve/reject bar and status helpers for entity review UIs."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.domain_tag_ui import find_review_node

DEFAULT_PROPOSAL_STATUS = "approved"


def proposal_save_message_key(key_prefix: str) -> str:
    """Session-state key for a per-proposal save confirmation (shown under the save button)."""
    return f"{key_prefix}_save_msg"


def set_proposal_save_message(key_prefix: str, message: str) -> None:
    """Queue a save confirmation for :func:`render_proposal_decision_bar`."""
    streamlit_runtime.session_state[proposal_save_message_key(key_prefix)] = message


def pop_proposal_save_message(key_prefix: str) -> str | None:
    """Return and clear a queued save confirmation, if any."""
    raw = streamlit_runtime.session_state.pop(proposal_save_message_key(key_prefix), None)
    return str(raw) if raw else None


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


def render_proposal_status_toggle(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
    artifact_path: Path,
    review_list_key: str,
) -> None:
    """Reject or Approve toggle (persisted immediately on click)."""
    proposal_id = str(node.get("proposal_id") or "")
    current = normalized_proposal_status(node)
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


def render_proposal_save_button(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
    artifact_path: Path,
    review_list_key: str,
    on_save_callback: Callable[[], None],
    save_button_label: str = "Save tags & approve",
) -> None:
    """Primary save action: persist edits and mark proposal approved."""
    if st.button(
        save_button_label,
        key=f"{key_prefix}_save",
        type="primary",
        use_container_width=True,
    ):
        node["proposal_status"] = DEFAULT_PROPOSAL_STATUS
        on_save_callback()
        streamlit_runtime.rerun()


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
    if on_save_callback is None:
        render_proposal_status_toggle(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key=review_list_key,
        )
    else:
        action_col, save_col = st.columns(2)
        with action_col:
            render_proposal_status_toggle(
                st,
                node,
                key_prefix=f"{key_prefix}_bar",
                artifact_path=artifact_path,
                review_list_key=review_list_key,
            )
        with save_col:
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
