"""Tests for implementation-study evidence gate heuristics."""

from __future__ import annotations

from src.ingest_review.impl_study_gate import (
    demote_weak_impl_study,
    filter_impl_study_proposals,
    format_impl_study_evidence_caption,
    impl_study_likely_misclassified,
    impl_study_meets_evidence_threshold,
)
from src.ingest_review.schema import EvidenceSnippet, ImplementationStudyProposal


def _strong_proposal() -> ImplementationStudyProposal:
    return ImplementationStudyProposal(
        title="Contact center GenAI rollout",
        company="Acme Corp",
        deployment_context="Production pilot across 12 US contact centers from Q2 2025.",
        outcome_status="Ticket deflection improved 18% during the 90-day pilot.",
        operational_constraints="Latency budget under 2s required GPU scaling.",
        evidence_snippets=[
            EvidenceSnippet(
                claim="Pilot in production",
                snippet="deployed to twelve centers",
                provenance="stated",
            ),
            EvidenceSnippet(
                claim="Metric",
                snippet="18% deflection",
                provenance="stated",
            ),
        ],
        confidence=0.8,
        suggested_action="create",
        value_level="high",
    )


def test_impl_study_meets_evidence_threshold_strong_case() -> None:
    """Strong deployment case with stated snippets passes the gate."""
    assert impl_study_meets_evidence_threshold(_strong_proposal()) is True


def test_impl_study_meets_evidence_threshold_weekend_build_fails() -> None:
    """Personal experiment without deployment evidence fails the gate."""
    weak = ImplementationStudyProposal(
        title="My RAG weekend project",
        company="",
        overview="I built a RAG agent over the weekend.",
        deployment_context="",
        outcome_status="unknown",
        evidence_snippets=[],
        confidence=0.7,
    )
    assert impl_study_meets_evidence_threshold(weak) is False


def test_filter_impl_study_proposals_demotes_weak() -> None:
    """Weak proposals are demoted to ignore/low confidence instead of dropped."""
    weak = ImplementationStudyProposal(
        title="Architecture layers post",
        company="SomeCo",
        deployment_context="",
        outcome_status="TBD",
        confidence=0.9,
        suggested_action="create",
        value_level="high",
    )
    out = filter_impl_study_proposals([weak])
    assert len(out) == 1
    assert out[0].suggested_action == "ignore"
    assert out[0].value_level == "low"
    assert out[0].confidence <= 0.25


def test_filter_impl_study_proposals_keeps_strong() -> None:
    """Strong proposals pass through unchanged."""
    strong = _strong_proposal()
    out = filter_impl_study_proposals([strong])
    assert out[0].suggested_action == "create"
    assert out[0].value_level == "high"


def test_demote_weak_impl_study_caps_confidence() -> None:
    """Demotion sets ignore, low value, and capped confidence."""
    p = demote_weak_impl_study(
        ImplementationStudyProposal(confidence=0.95, suggested_action="create")
    )
    assert p.suggested_action == "ignore"
    assert p.value_level == "low"
    assert p.confidence == 0.25


def test_format_impl_study_evidence_caption_shows_gate_state() -> None:
    """Caption includes gate pass/fail and snippet counts."""
    cap = format_impl_study_evidence_caption(_strong_proposal().model_dump())
    assert "Evidence gate: pass" in cap
    assert "Stated snippets: 2/2" in cap


def test_impl_study_likely_misclassified_empty_snippets() -> None:
    """No snippets triggers misclassification hint."""
    weak = ImplementationStudyProposal(
        deployment_context="",
        outcome_status="",
        evidence_snippets=[],
    )
    assert impl_study_likely_misclassified(weak.model_dump()) is True


def test_impl_study_likely_misclassified_strong_case() -> None:
    """Strong case is not flagged as misclassified."""
    assert impl_study_likely_misclassified(_strong_proposal().model_dump()) is False
