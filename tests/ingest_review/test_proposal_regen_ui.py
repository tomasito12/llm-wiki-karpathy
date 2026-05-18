"""Tests for shared proposal regeneration Streamlit helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.ingest_review.proposal_regen_ui import (
    _queue_proposal_regen,
    entity_review_tab_for_key,
    pop_proposal_regen_msg,
    preserve_review_entity_tab_for_regen,
    proposal_edit_key_prefix,
    regen_count_from_node,
)


def test_proposal_edit_key_prefix_includes_regen_count() -> None:
    assert proposal_edit_key_prefix("src", "pid9", "g", regen_count=0) == "src_g_pid9_r0"
    assert proposal_edit_key_prefix("src", "pid9", "tool", regen_count=2) == "src_tool_pid9_r2"


def test_regen_count_from_node_defaults_to_zero() -> None:
    assert regen_count_from_node({}) == 0
    assert regen_count_from_node({"proposal_regeneration_meta": {"regen_count": 3}}) == 3


def test_queue_proposal_regen_sets_pending_payload() -> None:
    mock_st = MagicMock()
    mock_st.session_state = {
        "pfx_regen_new_title": "  Broader Term  ",
        "pfx_regen_note": "note here",
    }
    with patch("src.ingest_review.proposal_regen_ui.streamlit_runtime", mock_st):
        _queue_proposal_regen("glossary", "src-1", "pid-2", "pfx")
    assert mock_st.session_state["_pending_proposal_regen"] == {
        "entity": "glossary",
        "source_id": "src-1",
        "proposal_id": "pid-2",
        "new_title": "Broader Term",
        "note": "note here",
    }


def test_entity_review_tab_for_key_maps_dashboard_labels() -> None:
    assert entity_review_tab_for_key("glossary") == "Glossary"
    assert entity_review_tab_for_key("topic") == "Topics"
    assert entity_review_tab_for_key("unknown") is None


def test_preserve_review_entity_tab_for_regen_sets_session_state() -> None:
    mock_st = MagicMock()
    mock_st.session_state = {}
    with patch("src.ingest_review.proposal_regen_ui.streamlit_runtime", mock_st):
        preserve_review_entity_tab_for_regen("glossary")
    assert mock_st.session_state["review_entity_tab"] == "Glossary"


def test_preserve_review_entity_tab_for_regen_ignores_unknown_entity() -> None:
    mock_st = MagicMock()
    mock_st.session_state = {"review_entity_tab": "Topics"}
    with patch("src.ingest_review.proposal_regen_ui.streamlit_runtime", mock_st):
        preserve_review_entity_tab_for_regen("not_an_entity")
    assert mock_st.session_state["review_entity_tab"] == "Topics"


def test_pop_proposal_regen_msg_entity_filter() -> None:
    import streamlit as st

    st.session_state["_proposal_regen_msg"] = {
        "entity": "trend",
        "text": "Regenerated trend as **X**.",
    }
    assert pop_proposal_regen_msg("trend") == "Regenerated trend as **X**."
    st.session_state["_proposal_regen_msg"] = {"entity": "trend", "text": "x"}
    assert pop_proposal_regen_msg("topic") is None
