"""Tests for multi-tag domain routing UI helpers."""

from __future__ import annotations

from src.ingest_review.domain_tag_ui import (
    apply_tag_ui_to_node,
    collect_approved_new_tags_from_review,
    effective_readonly_tags,
)
from src.ingest_review.proposal_regen_ui import proposal_edit_key_prefix


def test_effective_readonly_tags_prefers_final_tags() -> None:
    llm = {"proposed_tags": ["orchestration", "evaluation"], "primary_tag": ""}
    node = {"final_tags": ["ai-engineering"], "approved_new_tags": []}
    assert effective_readonly_tags(llm, node, ["ai-engineering", "orchestration"]) == [
        "ai-engineering"
    ]


def test_effective_readonly_tags_falls_back_to_allowlisted_llm_proposals() -> None:
    llm = {"proposed_tags": ["orchestration", "off-list"], "primary_tag": ""}
    assert effective_readonly_tags(llm, {}, ["orchestration"]) == ["orchestration"]


def test_apply_tag_ui_to_node_persists_multiselect_and_approved_new() -> None:
    node: dict = {"tags": {}, "llm_item": {}}
    llm = node["llm_item"]
    apply_tag_ui_to_node(
        node,
        llm,
        {
            "selected_allowlist": ["orchestration", "evaluation"],
            "manual_csv": "custom-slug",
            "approve_new_map": {"custom-slug": True},
            "approve_offlist": False,
        },
        {"orchestration", "evaluation"},
    )
    assert node["tags"]["final_tags"] == ["orchestration", "evaluation", "custom-slug"]
    assert "custom-slug" in node["tags"]["approved_new_tags"]


def test_collect_approved_new_tags_from_review() -> None:
    artifact = {
        "review": {
            "glossary": [
                {
                    "tags": {"approved_new_tags": ["graph-rag"]},
                    "llm_item": {},
                },
                {
                    "tags": {"new_tag_approved": True},
                    "llm_item": {"suggested_new_tag": "legacy-tag"},
                },
            ],
        },
    }
    assert collect_approved_new_tags_from_review(artifact, "glossary") == [
        "graph-rag",
        "legacy-tag",
    ]


def test_proposal_edit_key_prefix_includes_regen_count() -> None:
    assert proposal_edit_key_prefix("src", "pid", "g", regen_count=2) == "src_g_pid_r2"
