"""Tests for ImplementationStudyProposal schema and constants."""

from __future__ import annotations

from src.ingest_review.schema import (
    IMPL_STUDY_LIST_KEYS,
    IMPL_STUDY_SCALAR_KEYS,
    EvidenceSnippet,
    ImplementationStudyProposal,
    LlmClassificationOutput,
)


def test_impl_study_proposal_defaults_are_empty() -> None:
    """A default proposal has empty strings and empty lists."""
    p = ImplementationStudyProposal()
    assert p.title == ""
    assert p.company == ""
    assert p.industry == ""
    assert p.key_lessons == []
    assert p.evidence_snippets == []
    assert p.confidence == 0.0
    assert p.suggested_action == "ignore"


def test_impl_study_proposal_full_roundtrip() -> None:
    """A fully populated proposal survives model_dump / model_validate."""
    data = {
        "title": "Drive-through AI pilot",
        "company": "McDonald's",
        "industry": "Quick-service restaurant",
        "overview": "Tested AI order-taking at 100 locations.",
        "what_was_implemented": "IBM Watson voice ordering",
        "business_objective": "Reduce labour costs",
        "technical_approach": "NLU + TTS on drive-through intercom",
        "deployment_context": "100 US drive-through locations",
        "outcome_status": "Pilot ended, system removed",
        "success_or_failure_factors": "Accuracy below 85% threshold",
        "operational_constraints": "Noisy environment, accent diversity",
        "ai_model_observations": "NLU accuracy insufficient for production",
        "implications_for_service_automation": "Voice ordering needs higher accuracy",
        "strategic_signals": "Fast food chains still pursuing automation",
        "key_lessons": ["Accuracy matters more than speed", "Pilot before commit"],
        "open_questions": ["Will generative AI improve accuracy?"],
        "related_sources": ["https://example.com/article"],
        "evidence_snippets": [
            {"claim": "Accuracy was 85%", "snippet": "...", "provenance": "stated"},
        ],
        "suggested_existing_tags": ["voice-ai", "drive-through"],
        "proposed_new_tags": ["fast-food-ai"],
        "match_candidates": [],
        "confidence": 0.85,
        "suggested_action": "create",
    }
    p = ImplementationStudyProposal.model_validate(data)
    assert p.company == "McDonald's"
    assert p.confidence == 0.85
    assert len(p.evidence_snippets) == 1
    assert p.evidence_snippets[0].provenance == "stated"
    dumped = p.model_dump(mode="json")
    restored = ImplementationStudyProposal.model_validate(dumped)
    assert restored == p


def test_evidence_snippet_defaults() -> None:
    """Default snippet has empty fields and 'stated' provenance."""
    s = EvidenceSnippet()
    assert s.claim == ""
    assert s.provenance == "stated"


def test_evidence_snippet_accepts_all_provenances() -> None:
    """All three provenance literals are accepted."""
    for prov in ("stated", "inferred", "interpretation"):
        s = EvidenceSnippet(provenance=prov)
        assert s.provenance == prov


def test_llm_output_uses_implementation_studies_key() -> None:
    """LlmClassificationOutput has implementation_studies (not enterprise_studies)."""
    out = LlmClassificationOutput()
    assert hasattr(out, "implementation_studies")
    assert not hasattr(out, "enterprise_studies")
    assert out.implementation_studies == []


def test_llm_output_parses_with_implementation_studies() -> None:
    """JSON with implementation_studies key round-trips through LlmClassificationOutput."""
    data = {
        "implementation_studies": [
            {"title": "Test", "company": "Co", "confidence": 0.5, "suggested_action": "create"},
        ],
    }
    out = LlmClassificationOutput.model_validate(data)
    assert len(out.implementation_studies) == 1
    assert out.implementation_studies[0].company == "Co"


def test_impl_study_scalar_keys_match_model_fields() -> None:
    """IMPL_STUDY_SCALAR_KEYS are all valid string fields on the model."""
    model_fields = ImplementationStudyProposal.model_fields
    for key in IMPL_STUDY_SCALAR_KEYS:
        assert key in model_fields, f"{key} not in ImplementationStudyProposal"


def test_impl_study_list_keys_match_model_fields() -> None:
    """IMPL_STUDY_LIST_KEYS are all valid list[str] fields on the model."""
    model_fields = ImplementationStudyProposal.model_fields
    for key in IMPL_STUDY_LIST_KEYS:
        assert key in model_fields, f"{key} not in ImplementationStudyProposal"


def test_backward_compat_old_enterprise_study_shape() -> None:
    """Old EnterpriseStudyProposal fields produce a valid ImplementationStudyProposal."""
    old_data = {
        "company_name": "Acme",
        "implemented_technology": "chatbot",
        "business_context": "support",
        "implementation_pattern": "pilot",
        "lessons_learned": "works",
        "supporting_snippet": "...",
        "proposed_tags": ["voice-ai"],
        "confidence": 0.7,
        "suggested_action": "create",
    }
    p = ImplementationStudyProposal.model_validate(old_data)
    assert p.confidence == 0.7
    assert p.title == ""
    assert p.company == ""
