"""Tests for enriched IndustryTrendProposal schema and key tuples."""

from __future__ import annotations

from src.ingest_review.schema import (
    TREND_LIST_KEYS,
    TREND_SCALAR_KEYS,
    IndustryTrendProposal,
)


def test_trend_proposal_defaults() -> None:
    """All fields default to empty/zero."""
    tp = IndustryTrendProposal()
    assert tp.trend_name == ""
    assert tp.trend_description == ""
    assert tp.evidence_from_source == ""
    assert tp.time_sensitivity == ""
    assert tp.uncertainty_note == ""
    assert tp.supporting_snippet == ""
    assert tp.supporting_data_points == []
    assert tp.related_trends == []
    assert tp.primary_tag == ""
    assert tp.secondary_tag == ""
    assert tp.suggested_new_tag == ""
    assert tp.match_candidates == []
    assert tp.confidence == 0.0
    assert tp.suggested_action == "ignore"
    assert tp.value_level == "medium"


def test_trend_proposal_no_legacy_fields() -> None:
    """Old fields are removed."""
    assert "short_explanation" not in IndustryTrendProposal.model_fields
    assert "why_article_supports" not in IndustryTrendProposal.model_fields
    assert "evidence_as_of" not in IndustryTrendProposal.model_fields
    assert "claim_type" not in IndustryTrendProposal.model_fields
    assert "supporting_snippets" not in IndustryTrendProposal.model_fields


def test_trend_proposal_accepts_knowledge_action_values() -> None:
    """IndustryTrendProposal accepts the knowledge-action vocabulary."""
    tp = IndustryTrendProposal(suggested_action="append_to_existing")
    assert tp.suggested_action == "append_to_existing"
    tp2 = IndustryTrendProposal(suggested_action="create_new_page")
    assert tp2.suggested_action == "create_new_page"


def test_trend_scalar_keys_match_model_fields() -> None:
    """Every key in TREND_SCALAR_KEYS is a field on IndustryTrendProposal."""
    fields = set(IndustryTrendProposal.model_fields)
    for k in TREND_SCALAR_KEYS:
        assert k in fields


def test_trend_list_keys_match_model_fields() -> None:
    """Every key in TREND_LIST_KEYS is a field on IndustryTrendProposal."""
    fields = set(IndustryTrendProposal.model_fields)
    for k in TREND_LIST_KEYS:
        assert k in fields


def test_trend_proposal_roundtrip_json() -> None:
    """Model dump and validate round-trips cleanly."""
    tp = IndustryTrendProposal(
        trend_name="inference-cost-collapse",
        trend_description="Inference costs are falling rapidly.",
        uncertainty_note="Based on limited data points.",
        supporting_data_points=["GPT-4o 50% cheaper"],
        confidence=0.65,
        suggested_action="append_to_existing",
    )
    data = tp.model_dump(mode="json")
    restored = IndustryTrendProposal.model_validate(data)
    assert restored.trend_name == "inference-cost-collapse"
    assert restored.supporting_data_points == ["GPT-4o 50% cheaper"]
