"""Tests for enriched HowToProposal schema and key tuples."""

from __future__ import annotations

from src.ingest_review.schema import (
    HOWTO_LIST_KEYS,
    HOWTO_SCALAR_KEYS,
    HowToProposal,
)


def test_howto_proposal_defaults() -> None:
    """All fields default to empty/zero."""
    hp = HowToProposal()
    assert hp.question_title == ""
    assert hp.answer_summary == ""
    assert hp.supporting_snippet == ""
    assert hp.relevance_note == ""
    assert hp.caveats == ""
    assert hp.implementation_steps == []
    assert hp.prerequisites == []
    assert hp.related_howtos == []
    assert hp.primary_tag == ""
    assert hp.secondary_tag == ""
    assert hp.suggested_new_tag == ""
    assert hp.match_candidates == []
    assert hp.confidence == 0.0
    assert hp.suggested_action == "ignore"
    assert hp.value_level == "medium"


def test_howto_proposal_no_legacy_fields() -> None:
    """similar_existing_questions and tag_gap_notes are removed."""
    assert not hasattr(HowToProposal(), "similar_existing_questions")
    assert not hasattr(HowToProposal(), "tag_gap_notes")
    assert "similar_existing_questions" not in HowToProposal.model_fields
    assert "tag_gap_notes" not in HowToProposal.model_fields


def test_howto_proposal_accepts_knowledge_action_values() -> None:
    """HowToProposal accepts the knowledge-action vocabulary."""
    hp = HowToProposal(suggested_action="append_to_existing")
    assert hp.suggested_action == "append_to_existing"
    hp2 = HowToProposal(suggested_action="create_new_page")
    assert hp2.suggested_action == "create_new_page"


def test_howto_scalar_keys_match_model_fields() -> None:
    """Every key in HOWTO_SCALAR_KEYS is a field on HowToProposal."""
    fields = set(HowToProposal.model_fields)
    for k in HOWTO_SCALAR_KEYS:
        assert k in fields


def test_howto_list_keys_match_model_fields() -> None:
    """Every key in HOWTO_LIST_KEYS is a field on HowToProposal."""
    fields = set(HowToProposal.model_fields)
    for k in HOWTO_LIST_KEYS:
        assert k in fields


def test_howto_proposal_roundtrip_json() -> None:
    """Model dump and validate round-trips cleanly."""
    hp = HowToProposal(
        question_title="How to build evaluation pipelines?",
        answer_summary="Summary.",
        implementation_steps=["step 1", "step 2"],
        prerequisites=["prereq 1"],
        confidence=0.7,
        suggested_action="append_to_existing",
    )
    data = hp.model_dump(mode="json")
    restored = HowToProposal.model_validate(data)
    assert restored.question_title == "How to build evaluation pipelines?"
    assert restored.implementation_steps == ["step 1", "step 2"]
