"""Tests for shared proposal decision helpers (no Streamlit runtime)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.ingest_review.proposal_decision_ui import (
    DEFAULT_PROPOSAL_STATUS,
    normalized_proposal_status,
    pop_proposal_save_message,
    proposal_save_message_key,
    proposal_status_label,
    set_proposal_save_message,
)


def test_default_proposal_status_is_approved() -> None:
    assert DEFAULT_PROPOSAL_STATUS == "approved"


def test_normalized_proposal_status_treats_pending_as_approved() -> None:
    assert normalized_proposal_status({"proposal_status": "pending"}) == "approved"
    assert normalized_proposal_status({}) == "approved"


def test_normalized_proposal_status_keeps_rejected() -> None:
    assert normalized_proposal_status({"proposal_status": "rejected"}) == "rejected"


def test_proposal_status_label_approved() -> None:
    assert proposal_status_label({"proposal_status": "approved"}) == "Approved"
    assert proposal_status_label({"proposal_status": "pending"}) == "Approved"


def test_proposal_status_label_rejected() -> None:
    assert proposal_status_label({"proposal_status": "rejected"}) == "Rejected"


def test_proposal_status_label_deferred() -> None:
    assert proposal_status_label({"proposal_status": "deferred"}) == "Deferred"


def test_proposal_save_message_key_uses_key_prefix() -> None:
    assert proposal_save_message_key("topic_0") == "topic_0_save_msg"


def test_set_and_pop_proposal_save_message_round_trip() -> None:
    mock_st = MagicMock()
    mock_st.session_state = {}
    with patch("src.ingest_review.proposal_decision_ui.streamlit_runtime", mock_st):
        set_proposal_save_message("topic_0", "Saved **Foo**.")
        assert mock_st.session_state["topic_0_save_msg"] == "Saved **Foo**."
        assert pop_proposal_save_message("topic_0") == "Saved **Foo**."
        assert pop_proposal_save_message("topic_0") is None


def test_pop_proposal_save_message_when_missing_returns_none() -> None:
    mock_st = MagicMock()
    mock_st.session_state = {}
    with patch("src.ingest_review.proposal_decision_ui.streamlit_runtime", mock_st):
        assert pop_proposal_save_message("topic_missing") is None
