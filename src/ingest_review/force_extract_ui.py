"""Streamlit UI for reviewer-forced single-entity extraction."""

from __future__ import annotations

import os
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.proposal_regen import REGEN_SPECS

FORCE_EXTRACT_ENTITY_OPTIONS: tuple[tuple[str, str], ...] = (
    ("topic", "Topic"),
    ("glossary", "Glossary term"),
    ("how_to", "How-to"),
    ("trend", "Trend"),
    ("tool", "Tool"),
    ("model", "Foundation model"),
    ("impl_study", "Implementation study"),
)


def source_summary_is_empty(artifact: dict[str, Any]) -> bool:
    """True when stage-2 chapters have no substantive text."""
    ss = (artifact.get("llm_output") or {}).get("source_summary") or {}
    if not isinstance(ss, dict):
        return True
    for key in ("summary", "accessible_overview", "why_it_matters"):
        if str(ss.get(key) or "").strip():
            return False
    insights = ss.get("key_insights")
    return not (isinstance(insights, list) and insights)


def queue_forced_extract(
    *,
    source_id: str,
    entity_key: str,
    title: str,
    note: str,
) -> None:
    streamlit_runtime.session_state["_pending_forced_extract"] = {
        "source_id": source_id,
        "entity": entity_key,
        "title": title,
        "note": note,
    }


def render_force_extract_panel(
    st: Any,
    *,
    source_id: str,
    key_prefix: str,
    default_entity_key: str = "topic",
    default_title: str = "",
    compact: bool = False,
) -> None:
    """Title + entity picker + optional note; queues ``_pending_forced_extract`` on click."""
    title_key = f"{key_prefix}_force_title"
    entity_key_key = f"{key_prefix}_force_entity"
    note_key = f"{key_prefix}_force_note"
    entity_labels = [label for _, label in FORCE_EXTRACT_ENTITY_OPTIONS]
    entity_keys = [key for key, _ in FORCE_EXTRACT_ENTITY_OPTIONS]
    default_index = (
        entity_keys.index(default_entity_key) if default_entity_key in entity_keys else 0
    )
    if title_key not in streamlit_runtime.session_state and default_title.strip():
        streamlit_runtime.session_state[title_key] = default_title.strip()

    header = "Force extract one item" if not compact else "Force extract"
    with st.expander(header, expanded=not compact):
        st.caption(
            "Ask the LLM to extract a single topic, trend, tool, or other proposal by title "
            "— useful when automatic extraction skipped the article or missed an item."
        )
        c1, c2 = st.columns([2, 1])
        with c1:
            title = st.text_input(
                "Title or term",
                key=title_key,
                placeholder="e.g. Quantized Neural Networks",
            )
        with c2:
            picked = st.selectbox(
                "Entity type",
                options=entity_labels,
                index=default_index,
                key=entity_key_key,
            )
        note = st.text_area(
            "Optional instruction",
            key=note_key,
            height=68,
            placeholder="e.g. Focus on inference-time quantization, not training.",
        )
        entity_key = entity_keys[entity_labels.index(picked)]
        spec = REGEN_SPECS.get(entity_key)
        btn_label = f"Force extract as {spec.entity_label if spec else entity_key}"
        if st.button(
            btn_label,
            key=f"{key_prefix}_force_extract_btn",
            type="primary",
            disabled=not bool(os.environ.get("OPENAI_API_KEY")),
        ):
            if not str(title or "").strip():
                st.warning("Enter a title or term first.")
            else:
                queue_forced_extract(
                    source_id=source_id,
                    entity_key=entity_key,
                    title=str(title).strip(),
                    note=str(note or "").strip(),
                )
                st.rerun()
