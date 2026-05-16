"""Tests for topic proposal regeneration merge logic."""

from __future__ import annotations

import pytest

from src.ingest_review.schema import TopicRegenerateOutput
from src.ingest_review.topic_regen import apply_regenerated_topic_proposal


def _sample_artifact() -> dict:
    return {
        "llm_output": {
            "topics": [
                {
                    "topic_slug": "local-multimodal-inference",
                    "topic_title": "Local Multimodal Inference",
                    "knowledge_summary": "Old summary about multimodal only.",
                    "key_points": ["multimodal only"],
                    "related_topics": [],
                },
            ],
        },
        "review": {
            "topics": [
                {
                    "proposal_id": "pid-1",
                    "proposal_status": "approved",
                    "llm_item": {
                        "topic_slug": "local-multimodal-inference",
                        "topic_title": "Local Multimodal Inference",
                        "knowledge_summary": "Old summary about multimodal only.",
                        "primary_tag": "ai-infrastructure",
                        "key_points": ["multimodal only"],
                    },
                    "sections": {
                        "topic_title": {
                            "status": "modified",
                            "final_text": "Local Multimodal Inference",
                        },
                    },
                    "tags": {"final_primary_tag": "ai-infrastructure"},
                },
            ],
        },
    }


def test_apply_regenerated_topic_updates_title_slug_and_llm_output() -> None:
    art = _sample_artifact()
    regen = TopicRegenerateOutput(
        knowledge_summary="Broader local inference including multimodal deployment notes.",
        examples="Runs vision + text on device.",
        operational_insight="Use sampling for eval at scale.",
        relevance_note="Covers evaluation when manual review is impractical.",
        key_points=["sampling", "multimodal stacks"],
        supporting_snippet="verbatim from source",
        confidence=0.8,
        value_level="high",
        suggested_action="append_to_existing",
        evidence_type="independent_analysis",
    )
    apply_regenerated_topic_proposal(
        art,
        "pid-1",
        new_title="Local Inference",
        regenerated=regen,
        model="gpt-test",
        prompt_version="21",
    )
    node = art["review"]["topics"][0]
    assert node["llm_item"]["topic_title"] == "Local Inference"
    assert node["llm_item"]["topic_slug"] == "local-inference"
    assert "multimodal" in node["llm_item"]["knowledge_summary"]
    assert node["llm_item"]["primary_tag"] == "ai-infrastructure"
    assert node["tags"]["final_primary_tag"] == "ai-infrastructure"
    assert node["sections"]["topic_title"]["final_text"] is None
    assert node["sections"]["topic_title"]["status"] == "pending"
    assert art["llm_output"]["topics"][0]["topic_title"] == "Local Inference"
    assert art["llm_output"]["topics"][0]["topic_slug"] == "local-inference"
    meta = node.get("proposal_regeneration_meta")
    assert isinstance(meta, dict)
    assert meta.get("regen_count") == 1


def test_apply_regenerated_topic_requires_non_empty_title() -> None:
    art = _sample_artifact()
    with pytest.raises(ValueError, match="new_title"):
        apply_regenerated_topic_proposal(
            art,
            "pid-1",
            new_title="  ",
            regenerated=TopicRegenerateOutput(),
            model="m",
            prompt_version="21",
        )


def test_apply_regenerated_topic_unknown_proposal_raises() -> None:
    art = _sample_artifact()
    with pytest.raises(ValueError, match="Unknown topic"):
        apply_regenerated_topic_proposal(
            art,
            "missing",
            new_title="Local Inference",
            regenerated=TopicRegenerateOutput(),
            model="m",
            prompt_version="21",
        )
