"""Tests for shared proposal decision helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.proposal_decision_ui import (
    DEFAULT_PROPOSAL_STATUS,
    normalized_proposal_status,
    proposal_status_label,
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
