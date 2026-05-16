"""Tests for cross-section proposal transfer (e.g. trend → topic)."""

from __future__ import annotations

import pytest

from src.ingest_review.proposal_regen import REGEN_SPECS
from src.ingest_review.proposal_transfer import (
    TRANSFER_TARGET_OPTIONS,
    resolve_transfer_specs,
    transfer_proposal_to_entity,
    transfer_target_label,
)
from src.ingest_review.schema import TopicRegenerateOutput


def _trend_to_topic_artifact() -> dict:
    return {
        "llm_output": {
            "industry_trends": [
                {
                    "trend_slug": "harness-decay",
                    "trend_title": "Harness Decay",
                    "trend_description": "Eval harnesses degrade over time.",
                },
            ],
            "topics": [],
        },
        "review": {
            "industry_trends": [
                {
                    "proposal_id": "pid-harness",
                    "proposal_status": "pending",
                    "llm_item": {
                        "trend_slug": "harness-decay",
                        "trend_title": "Harness Decay",
                        "trend_description": "Eval harnesses degrade over time.",
                    },
                    "sections": {"trend_title": {"status": "pending", "final_text": None}},
                    "tags": {"final_tags": ["evaluation"]},
                },
            ],
            "topics": [],
        },
    }


def test_transfer_target_options_includes_trend_to_topic() -> None:
    keys = [k for k, _ in TRANSFER_TARGET_OPTIONS["trend"]]
    assert "topic" in keys
    assert transfer_target_label("trend", "topic") == "Topic"


def test_transfer_trend_to_topic_moves_lists() -> None:
    art = _trend_to_topic_artifact()
    src_spec, tgt_spec = resolve_transfer_specs("trend", "topic")
    regen = TopicRegenerateOutput(
        knowledge_summary="Harness quality drifts as models and tasks change.",
        relevance_note="Affects eval design for agents.",
        confidence=0.75,
        value_level="high",
    )
    transfer_proposal_to_entity(
        art,
        "pid-harness",
        src_spec,
        tgt_spec,
        new_title="Harness Decay",
        regenerated=regen.model_dump(mode="json"),
        model="gpt-test",
        prompt_version="26",
    )
    assert art["review"]["industry_trends"] == []
    assert art["llm_output"]["industry_trends"] == []
    assert len(art["review"]["topics"]) == 1
    node = art["review"]["topics"][0]
    assert node["proposal_id"] == "pid-harness"
    assert node["llm_item"]["topic_title"] == "Harness Decay"
    assert node["llm_item"]["topic_slug"] == "harness-decay"
    assert "Harness quality" in node["llm_item"]["knowledge_summary"]
    assert node["tags"]["final_tags"] == []
    meta = node["proposal_regeneration_meta"]
    assert meta["transferred_from"]["entity"] == "trend"
    assert len(art["llm_output"]["topics"]) == 1
    assert art["llm_output"]["topics"][0]["topic_slug"] == "harness-decay"


def test_resolve_transfer_specs_rejects_same_entity() -> None:
    with pytest.raises(ValueError, match="must differ"):
        resolve_transfer_specs("topic", "topic")


def test_resolve_transfer_specs_rejects_invalid_pair() -> None:
    with pytest.raises(ValueError, match="Cannot transfer"):
        resolve_transfer_specs("trend", "tool")


def test_transfer_requires_nonempty_title() -> None:
    art = _trend_to_topic_artifact()
    src_spec, tgt_spec = REGEN_SPECS["trend"], REGEN_SPECS["topic"]
    with pytest.raises(ValueError, match="new_title"):
        transfer_proposal_to_entity(
            art,
            "pid-harness",
            src_spec,
            tgt_spec,
            new_title="  ",
            regenerated={},
            model="m",
            prompt_version="26",
        )
