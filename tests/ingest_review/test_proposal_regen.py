"""Tests for shared per-proposal regeneration merge logic."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from src.ingest_review.domain_tag_ui import find_review_node
from src.ingest_review.proposal_regen import REGEN_SPECS, apply_regenerated_proposal
from src.ingest_review.schema import (
    GlossaryRegenerateOutput,
    ToolRegenerateOutput,
    TopicRegenerateOutput,
    TrendRegenerateOutput,
    normalize_glossary_term_capitalization,
)


def _topic_artifact() -> dict:
    return {
        "llm_output": {
            "topics": [
                {
                    "topic_slug": "narrow-topic",
                    "topic_title": "Narrow Topic",
                    "knowledge_summary": "Old.",
                },
            ],
        },
        "review": {
            "topics": [
                {
                    "proposal_id": "pid-t",
                    "llm_item": {
                        "topic_slug": "narrow-topic",
                        "topic_title": "Narrow Topic",
                        "knowledge_summary": "Old.",
                    },
                    "sections": {
                        "topic_title": {"status": "modified", "final_text": "Narrow Topic"},
                    },
                },
            ],
        },
    }


def _glossary_artifact() -> dict:
    return {
        "llm_output": {"glossary": [{"term": "rag pipeline", "proposed_definition": "Old."}]},
        "review": {
            "glossary": [
                {
                    "proposal_id": "pid-g",
                    "llm_item": {"term": "rag pipeline", "proposed_definition": "Old."},
                    "sections": {},
                },
            ],
        },
    }


def _trend_artifact() -> dict:
    return {
        "llm_output": {
            "industry_trends": [
                {
                    "trend_slug": "narrow-trend",
                    "trend_title": "Narrow Trend",
                    "trend_description": "Old.",
                    "uncertainty_note": "Some uncertainty.",
                },
            ],
        },
        "review": {
            "industry_trends": [
                {
                    "proposal_id": "pid-tr",
                    "llm_item": {
                        "trend_slug": "narrow-trend",
                        "trend_title": "Narrow Trend",
                        "trend_description": "Old.",
                        "uncertainty_note": "Some uncertainty.",
                    },
                    "sections": {},
                },
            ],
        },
    }


def _tool_artifact() -> dict:
    return {
        "llm_output": {"tools": [{"name": "Tool A", "short_description": "Old."}]},
        "review": {
            "tools": [
                {
                    "proposal_id": "pid-tool",
                    "llm_item": {"name": "Tool A", "short_description": "Old."},
                    "sections": {},
                },
            ],
        },
    }


@pytest.mark.parametrize(
    (
        "entity_key",
        "artifact_factory",
        "proposal_id",
        "new_title",
        "regen_cls",
        "title_field",
        "expected_title",
    ),
    [
        (
            "topic",
            _topic_artifact,
            "pid-t",
            "Broad Topic",
            TopicRegenerateOutput,
            "topic_title",
            "Broad Topic",
        ),
        (
            "glossary",
            _glossary_artifact,
            "pid-g",
            "rag",
            GlossaryRegenerateOutput,
            "term",
            normalize_glossary_term_capitalization("rag"),
        ),
        (
            "trend",
            _trend_artifact,
            "pid-tr",
            "Broad Trend",
            TrendRegenerateOutput,
            "trend_title",
            "Broad Trend",
        ),
        (
            "tool",
            _tool_artifact,
            "pid-tool",
            "Tool Platform",
            ToolRegenerateOutput,
            "name",
            "Tool Platform",
        ),
    ],
)
def test_apply_regenerated_proposal_updates_title_and_regen_meta(
    entity_key: str,
    artifact_factory: Callable[[], dict],
    proposal_id: str,
    new_title: str,
    regen_cls: type,
    title_field: str,
    expected_title: str,
) -> None:
    art = artifact_factory()
    spec = REGEN_SPECS[entity_key]
    regen = regen_cls()
    apply_regenerated_proposal(
        art,
        proposal_id,
        spec,
        new_title=new_title,
        regenerated=regen.model_dump(mode="json"),
        model="gpt-test",
        prompt_version="25",
    )
    node = find_review_node(art, proposal_id, spec.review_list_key)
    assert node is not None
    assert node["llm_item"][title_field] == expected_title
    meta = node.get("proposal_regeneration_meta")
    assert isinstance(meta, dict)
    assert meta.get("regen_count") == 1
    llm_out = art["llm_output"][spec.llm_output_key][0]
    assert llm_out[title_field] == expected_title


def test_apply_regenerated_topic_sets_slug() -> None:
    art = _topic_artifact()
    apply_regenerated_proposal(
        art,
        "pid-t",
        REGEN_SPECS["topic"],
        new_title="Broad Topic",
        regenerated=TopicRegenerateOutput(knowledge_summary="New summary.").model_dump(mode="json"),
        model="m",
        prompt_version="25",
    )
    assert art["review"]["topics"][0]["llm_item"]["topic_slug"] == "broad-topic"


def test_apply_regenerated_proposal_empty_title_raises() -> None:
    art = _topic_artifact()
    with pytest.raises(ValueError, match="new_title"):
        apply_regenerated_proposal(
            art,
            "pid-t",
            REGEN_SPECS["topic"],
            new_title="  ",
            regenerated={},
            model="m",
            prompt_version="25",
        )
