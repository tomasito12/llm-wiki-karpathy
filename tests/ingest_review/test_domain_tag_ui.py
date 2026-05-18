"""Tests for multi-tag domain routing UI helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.ingest_review.domain_tag_ui import (
    apply_registry_types_ui_to_node,
    apply_tag_ui_to_node,
    collect_approved_new_tags_from_review,
    effective_readonly_tags,
    effective_registry_types,
    init_widget_session_value,
    queue_widget_session_resync,
    widget_resync_key,
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


def test_effective_registry_types_prefers_approved_types() -> None:
    llm = {"proposed_types": ["chat-model", "off-list"]}
    node = {"approved_types": ["frontier-model"], "reviewer_types_added": []}
    assert effective_registry_types(llm, node, ["chat-model", "frontier-model"]) == [
        "frontier-model"
    ]


def test_effective_registry_types_includes_reviewer_manual_types() -> None:
    llm = {"proposed_types": ["chat-model"]}
    node = {"approved_types": [], "reviewer_types_added": ["custom-tool"]}
    assert effective_registry_types(llm, node) == ["custom-tool"]


def test_init_widget_session_value_applies_pending_resync() -> None:
    mock_st = MagicMock()
    widget_key = "pfx_types_manual"
    mock_st.session_state = {widget_resync_key(widget_key): "queued-type"}
    with patch("src.ingest_review.domain_tag_ui.streamlit_runtime", mock_st):
        init_widget_session_value(widget_key, "stored-type")
    assert mock_st.session_state[widget_key] == "queued-type"
    assert widget_resync_key(widget_key) not in mock_st.session_state


def test_queue_widget_session_resync_does_not_touch_widget_key() -> None:
    mock_st = MagicMock()
    widget_key = "pfx_types_manual"
    mock_st.session_state = {widget_key: "user-typed"}
    with patch("src.ingest_review.domain_tag_ui.streamlit_runtime", mock_st):
        queue_widget_session_resync(widget_key, "after-save")
    assert mock_st.session_state[widget_key] == "user-typed"
    assert mock_st.session_state[widget_resync_key(widget_key)] == "after-save"


def test_apply_registry_types_ui_to_node_persists_manual_and_offlist_export() -> None:
    node: dict = {"types": {}, "llm_item": {}}
    llm = node["llm_item"]
    apply_registry_types_ui_to_node(
        node,
        llm,
        {
            "selected_allowlist": ["chat-model"],
            "manual_csv": "my-new-type",
            "approve_new_map": {},
            "approve_offlist": True,
        },
        {"chat-model"},
    )
    assert node["types"]["approved_types"] == ["chat-model", "my-new-type"]
    assert node["types"]["reviewer_types_added"] == ["my-new-type"]
    assert "my-new-type" in node["types"]["approved_new_types"]
