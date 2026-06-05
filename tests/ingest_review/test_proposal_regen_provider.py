"""Tests for proposal regeneration provider helpers."""

from __future__ import annotations

from src.ingest_review.proposal_regen_provider import (
    regen_payload_for_apply,
    resolve_effective_regen_title,
)


def test_resolve_effective_regen_title_prefers_reviewer_title() -> None:
    regen = {"proposed_title": "LLM title", "trend_description": "body"}
    assert resolve_effective_regen_title("Reviewer title", regen) == "Reviewer title"


def test_resolve_effective_regen_title_uses_proposed_title_when_reviewer_empty() -> None:
    regen = {"proposed_title": "  Clearer trend title  ", "trend_description": "body"}
    assert resolve_effective_regen_title("", regen) == "Clearer trend title"
    assert resolve_effective_regen_title("   ", regen) == "Clearer trend title"


def test_resolve_effective_regen_title_returns_empty_when_both_missing() -> None:
    assert resolve_effective_regen_title("", {"trend_description": "body"}) == ""


def test_regen_payload_for_apply_strips_proposed_title() -> None:
    payload = regen_payload_for_apply(
        {"proposed_title": "New title", "trend_description": "desc", "confidence": 0.8}
    )
    assert "proposed_title" not in payload
    assert payload["trend_description"] == "desc"
    assert payload["confidence"] == 0.8
