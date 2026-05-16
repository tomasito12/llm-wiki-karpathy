"""Tests for TopicContribution schema and key tuples."""

from __future__ import annotations

from src.ingest_review.schema import (
    TOPIC_LIST_KEYS,
    TOPIC_SCALAR_KEYS,
    TopicContribution,
)


def test_topic_contribution_defaults() -> None:
    """All fields default to empty/zero."""
    tc = TopicContribution()
    assert tc.topic_slug == ""
    assert tc.topic_title == ""
    assert tc.knowledge_summary == ""
    assert tc.examples == ""
    assert tc.operational_insight == ""
    assert tc.supporting_snippet == ""
    assert tc.relevance_note == ""
    assert tc.key_points == []
    assert tc.related_topics == []
    assert tc.primary_tag == ""
    assert tc.secondary_tag == ""
    assert tc.suggested_new_tag == ""
    assert tc.match_candidates == []
    assert tc.confidence == 0.0
    assert tc.suggested_action == "ignore"
    assert tc.value_level == "medium"


def test_topic_contribution_accepts_knowledge_action_values() -> None:
    """TopicContribution accepts the knowledge-action vocabulary."""
    tc1 = TopicContribution(suggested_action="append_to_existing")
    assert tc1.suggested_action == "append_to_existing"
    tc2 = TopicContribution(suggested_action="create_new_page")
    assert tc2.suggested_action == "create_new_page"
    tc3 = TopicContribution(suggested_action="ignore")
    assert tc3.suggested_action == "ignore"


def test_topic_scalar_keys_match_model_fields() -> None:
    """Every key in TOPIC_SCALAR_KEYS is a field on TopicContribution."""
    fields = set(TopicContribution.model_fields)
    for k in TOPIC_SCALAR_KEYS:
        assert k in fields


def test_topic_list_keys_match_model_fields() -> None:
    """Every key in TOPIC_LIST_KEYS is a field on TopicContribution."""
    fields = set(TopicContribution.model_fields)
    for k in TOPIC_LIST_KEYS:
        assert k in fields


def test_topic_contribution_roundtrip_json() -> None:
    """Model dump and validate round-trips cleanly."""
    tc = TopicContribution(
        topic_slug="context-engineering",
        topic_title="Context Engineering",
        knowledge_summary="Summary.",
        key_points=["point 1"],
        confidence=0.85,
        suggested_action="append_to_existing",
    )
    data = tc.model_dump(mode="json")
    restored = TopicContribution.model_validate(data)
    assert restored.topic_slug == "context-engineering"
    assert restored.key_points == ["point 1"]
    assert restored.confidence == 0.85
