"""Tests for source-level evidence profile and per-proposal overrides."""

from __future__ import annotations

from src.ingest_review.evidence import (
    apply_evidence_hierarchy,
    compact_evidence_in_llm_dict,
    effective_proposal_evidence_type,
    infer_primary_evidence_type_from_proposals,
    proposal_evidence_subtitle_part,
    source_primary_evidence_type,
)
from src.ingest_review.schema import LlmClassificationOutput, TopicContribution


def test_infer_primary_from_proposals_mode() -> None:
    llm = {
        "glossary": [
            {"term": "A", "evidence_type": "vendor_claim"},
            {"term": "B", "evidence_type": "vendor_claim"},
            {"term": "C", "evidence_type": "independent_analysis"},
        ],
    }
    assert infer_primary_evidence_type_from_proposals(llm) == "vendor_claim"


def test_compact_strips_matching_proposal_evidence_type() -> None:
    llm = {
        "source_evidence_profile": {"primary_evidence_type": "vendor_claim", "reasoning": []},
        "topics": [
            {"topic_title": "A", "evidence_type": "vendor_claim"},
            {"topic_title": "B", "evidence_type": "independent_analysis"},
        ],
    }
    compact_evidence_in_llm_dict(llm)
    assert "evidence_type" not in llm["topics"][0]
    assert llm["topics"][1]["evidence_type"] == "independent_analysis"


def test_apply_evidence_hierarchy_sets_profile_when_missing() -> None:
    parsed = LlmClassificationOutput.model_validate(
        {
            "topics": [
                TopicContribution(
                    topic_title="T",
                    evidence_type="vendor_claim",
                ).model_dump()
            ],
        }
    )
    out = apply_evidence_hierarchy(parsed)
    assert out.source_evidence_profile.primary_evidence_type == "vendor_claim"
    assert out.topics[0].evidence_type is None


def test_effective_proposal_evidence_inherits_source() -> None:
    primary = "vendor_claim"
    assert effective_proposal_evidence_type(primary, {}) == "vendor_claim"
    assert (
        effective_proposal_evidence_type(primary, {"evidence_type": "independent_analysis"})
        == "independent_analysis"
    )


def test_proposal_subtitle_empty_when_inheriting() -> None:
    artifact = {
        "llm_output": {
            "source_evidence_profile": {"primary_evidence_type": "vendor_claim"},
        },
        "review": {
            "source_evidence_profile": {
                "llm_item": {"primary_evidence_type": "vendor_claim"},
            },
        },
    }
    assert proposal_evidence_subtitle_part(artifact, {}) == ""
    assert (
        proposal_evidence_subtitle_part(artifact, {"evidence_type": "independent_analysis"})
        == "Override: Independent Analysis"
    )


def test_source_primary_from_review_final_item() -> None:
    artifact = {
        "llm_output": {
            "source_evidence_profile": {"primary_evidence_type": "vendor_claim"},
        },
        "review": {
            "source_evidence_profile": {
                "final_item": {"primary_evidence_type": "benchmark"},
            },
        },
    }
    assert source_primary_evidence_type(artifact) == "benchmark"
