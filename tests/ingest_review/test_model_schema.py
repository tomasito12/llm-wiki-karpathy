"""Tests for the enriched FoundationModelProposal schema."""

from __future__ import annotations

from src.ingest_review.schema import (
    MODEL_LIST_KEYS,
    MODEL_SCALAR_KEYS,
    FoundationModelProposal,
)


def test_foundation_model_proposal_defaults() -> None:
    """Fresh FoundationModelProposal has sensible defaults."""
    m = FoundationModelProposal()
    assert m.model_name == ""
    assert m.provider == ""
    assert m.operational_summary == ""
    assert m.strengths == ""
    assert m.weaknesses_limitations == ""
    assert m.workflow_implications == ""
    assert m.service_automation_implications == ""
    assert m.maturity_signals == ""
    assert m.pricing_inference_implications == ""
    assert m.supporting_snippet == ""
    assert m.core_capabilities == []
    assert m.benchmark_observations == []
    assert m.comparative_observations == []
    assert m.related_models == []
    assert m.proposed_types == []
    assert m.proposed_new_type is None
    assert m.match_candidates == []
    assert m.confidence == 0.0
    assert m.suggested_action == "ignore"


def test_foundation_model_proposal_scalar_keys_match_fields() -> None:
    """MODEL_SCALAR_KEYS reference real fields on FoundationModelProposal."""
    fields = FoundationModelProposal.model_fields
    for k in MODEL_SCALAR_KEYS:
        assert k in fields, f"Missing scalar field: {k}"


def test_foundation_model_proposal_list_keys_match_fields() -> None:
    """MODEL_LIST_KEYS reference real fields on FoundationModelProposal."""
    fields = FoundationModelProposal.model_fields
    for k in MODEL_LIST_KEYS:
        assert k in fields, f"Missing list field: {k}"


def test_foundation_model_proposal_removed_fields() -> None:
    """Old flat fields no longer exist on the enriched model."""
    fields = FoundationModelProposal.model_fields
    assert "article_summary" not in fields
    assert "newsworthy_attributes" not in fields


def test_foundation_model_proposal_json_round_trip() -> None:
    """JSON serialization round-trips correctly."""
    m = FoundationModelProposal(
        model_name="GPT-5",
        provider="OpenAI",
        operational_summary="Strong for coding.",
        core_capabilities=["long-context", "tool calling"],
        proposed_types=["frontier-model", "coding-model"],
        proposed_new_type="agent-model",
        confidence=0.85,
        suggested_action="create_new_page",
    )
    data = m.model_dump(mode="json")
    restored = FoundationModelProposal.model_validate(data)
    assert restored.model_name == "GPT-5"
    assert restored.proposed_types == ["frontier-model", "coding-model"]
    assert restored.proposed_new_type == "agent-model"
    assert restored.confidence == 0.85
    assert restored.core_capabilities == ["long-context", "tool calling"]


def test_provider_is_required_string() -> None:
    """Provider is now a required string, not optional."""
    m = FoundationModelProposal(provider="Anthropic")
    assert m.provider == "Anthropic"
    m2 = FoundationModelProposal()
    assert m2.provider == ""
