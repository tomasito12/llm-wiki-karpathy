"""Tests for topics two-column helpers (no Streamlit runtime)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.ingest_review.topic_related_topics_suggest import RelatedTopicCandidate
from src.ingest_review.topics_ui import (
    apply_topic_list_edit,
    apply_topic_proposal_edits,
    apply_topic_scalar_edit,
    build_readonly_topics_markdown,
    collect_topic_new_tags,
    effective_topic_list,
    effective_topic_scalar,
    format_topic_proposal_readonly_markdown,
    topic_edit_key_prefix,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def _sample_node() -> dict:
    return {
        "proposal_id": "abc",
        "proposal_status": "pending",
        "llm_item": {
            "topic_slug": "rag-patterns",
            "topic_title": "RAG patterns",
            "knowledge_summary": "Retrieval augments prompts.",
            "operational_insight": "Use chunking.",
            "relevance_note": "Core wiki theme.",
            "primary_tag": "orchestration",
            "value_level": "high",
            "confidence": 0.85,
            "evidence_type": "independent_analysis",
        },
        "sections": {},
        "tags": {},
    }


def test_effective_topic_scalar_prefers_final_text() -> None:
    llm = {"topic_title": "Draft"}
    sections = {
        "topic_title": {"final_text": "Reviewer title", "status": "modified"},
    }
    assert effective_topic_scalar(llm, sections, "topic_title") == "Reviewer title"


def test_apply_topic_scalar_edit_modified_when_differs() -> None:
    sections: dict = {}
    llm = {"knowledge_summary": "Original"}
    apply_topic_scalar_edit(sections, llm, "knowledge_summary", "Edited")
    node = sections["knowledge_summary"]
    assert node["status"] == "modified"
    assert node["final_text"] == "Edited"


def test_apply_topic_scalar_edit_approved_when_unchanged() -> None:
    sections: dict = {}
    llm = {"topic_title": "RAG patterns"}
    apply_topic_scalar_edit(sections, llm, "topic_title", "RAG patterns")
    node = sections["topic_title"]
    assert node["status"] == "approved"
    assert node["final_text"] is None


def test_apply_topic_list_edit_modified_when_differs() -> None:
    sections: dict = {}
    llm = {"key_points": ["a", "b"]}
    apply_topic_list_edit(sections, llm, "key_points", "x\ny")
    node = sections["key_points"]
    assert node["status"] == "modified"
    assert node["final_list"] == ["x", "y"]


def test_apply_topic_proposal_edits_all_reviewable_fields() -> None:
    node = _sample_node()
    apply_topic_proposal_edits(
        node,
        {
            "topic_slug": "rag-patterns",
            "topic_title": "RAG patterns",
            "knowledge_summary": "New summary",
            "examples": "",
            "operational_insight": "Op",
            "relevance_note": "Rel",
            "key_points": "one",
        },
    )
    assert node["sections"]["knowledge_summary"]["status"] == "modified"


def test_effective_topic_list_modified_branch() -> None:
    llm = {"key_points": ["a", "b"]}
    sections = {
        "key_points": {
            "status": "modified",
            "final_list": ["x"],
            "llm_list": ["a", "b"],
        },
    }
    assert effective_topic_list(llm, sections, "key_points") == ["x"]


def test_format_topic_readonly_hides_evidence_when_inheriting_source() -> None:
    artifact = {
        "llm_output": {
            "source_evidence_profile": {"primary_evidence_type": "independent_analysis"},
        },
        "review": {
            "source_evidence_profile": {
                "llm_item": {"primary_evidence_type": "independent_analysis"},
            },
        },
    }
    md = format_topic_proposal_readonly_markdown(_sample_node(), [], artifact=artifact)
    assert "Independent Analysis" not in md
    assert "Override" not in md


def test_format_topic_readonly_includes_google_link() -> None:
    md = format_topic_proposal_readonly_markdown(_sample_node(), [])
    assert '[Google: "RAG patterns"]' in md
    assert "google.com/search" in md
    assert "q=RAG+patterns" in md or "q=RAG%20patterns" in md


def test_format_topic_readonly_tags_after_knowledge_summary() -> None:
    node = _sample_node()
    node["llm_item"] = dict(node["llm_item"])
    node["llm_item"]["examples"] = "Claude works inside Slack as a teammate."
    node["llm_item"]["operational_insight"] = "Op body."
    md = format_topic_proposal_readonly_markdown(node, ["orchestration"])
    ks = md.index("**Knowledge summary**")
    ex = md.index("**Examples**")
    tags = md.index("**Tags**")
    op = md.index("**Operational insight**")
    assert ks < ex < tags < op
    assert "orchestration" in md


def test_format_topic_readonly_omits_examples_when_empty() -> None:
    node = _sample_node()
    node["llm_item"] = dict(node["llm_item"])
    node["llm_item"]["operational_insight"] = "Op"
    md = format_topic_proposal_readonly_markdown(node, ["orchestration"])
    assert "**Examples**" not in md


def test_format_topic_readonly_hides_offlist_llm_tags_without_final() -> None:
    node = _sample_node()
    node["llm_item"] = dict(node["llm_item"])
    node["llm_item"]["primary_tag"] = "made-up"
    md = format_topic_proposal_readonly_markdown(node, ["orchestration"])
    assert "**Tags**" not in md


def test_collect_topic_new_tags_normalizes() -> None:
    artifact = {
        "review": {
            "topics": [
                {
                    "tags": {"new_tag_approved": True},
                    "llm_item": {"suggested_new_tag": "  My Tag  "},
                }
            ]
        }
    }
    assert collect_topic_new_tags(artifact) == ["my-tag"]


def test_build_readonly_topics_markdown_tier_headers() -> None:
    high = _sample_node()
    low = {
        "proposal_id": "z",
        "proposal_status": "pending",
        "llm_item": {
            "topic_title": "Low topic",
            "knowledge_summary": "x",
            "value_level": "low",
        },
        "sections": {},
    }
    md = build_readonly_topics_markdown([high, low], [])
    assert "### High value" in md
    assert "### Low value" in md


def test_topic_edit_key_prefix_includes_regen_count() -> None:
    assert topic_edit_key_prefix("src", "pid9", regen_count=0) == "src_t_pid9_r0"
    assert topic_edit_key_prefix("src", "pid9", regen_count=2) == "src_t_pid9_r2"


def test_format_topic_readonly_related_topics_section_with_suggestions() -> None:
    suggestions = [
        RelatedTopicCandidate("context-engineering", "Context Engineering", "wiki"),
    ]
    md = format_topic_proposal_readonly_markdown(
        _sample_node(),
        [],
        related_suggestions=suggestions,
    )
    assert "**Related topics**" in md
    assert "context-engineering" in md
    assert "*Suggested:*" not in md
    assert "this review" not in md
    assert "other review" not in md


def test_apply_topic_proposal_edits_persists_related_topics() -> None:
    node = _sample_node()
    apply_topic_proposal_edits(
        node,
        {
            "topic_slug": "rag-patterns",
            "topic_title": "RAG patterns",
            "knowledge_summary": "x",
            "examples": "",
            "operational_insight": "",
            "relevance_note": "",
            "key_points": "",
            "related_topics": "context-engineering\nprompt-engineering",
        },
    )
    assert effective_topic_list(node["llm_item"], node["sections"], "related_topics") == [
        "context-engineering",
        "prompt-engineering",
    ]


def test_format_topic_readonly_related_topics_prefers_stored_over_suggestions() -> None:
    node = _sample_node()
    node["llm_item"] = dict(node["llm_item"])
    node["llm_item"]["related_topics"] = ["context-engineering", "prompt-engineering"]
    suggestions = [
        RelatedTopicCandidate("context-engineering", "Context Engineering", "wiki"),
    ]
    md = format_topic_proposal_readonly_markdown(node, [], related_suggestions=suggestions)
    assert "- context-engineering" in md
    assert "- prompt-engineering" in md
    assert "*Suggested:*" not in md
    assert "*Stored:*" not in md


def test_build_readonly_topics_markdown_includes_related_when_wiki_passed() -> None:
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        topic_titles=["Context Engineering"],
        topic_slugs=["context-engineering"],
    )
    node = _sample_node()
    node["llm_item"]["knowledge_summary"] = (
        "Retrieval augments prompts using context engineering techniques."
    )
    md = build_readonly_topics_markdown([node], [], artifact={}, wiki=wiki, reviews_root=None)
    assert "**Related topics**" in md


def test_queue_topic_regen_sets_pending_payload() -> None:
    """Topic regen uses shared queue with entity=topic."""
    from src.ingest_review.proposal_regen_ui import _queue_proposal_regen

    mock_st = MagicMock()
    mock_st.session_state = {
        "pfx_regen_new_title": "  Local Inference  ",
        "pfx_regen_note": "keep multimodal in summary",
    }
    with patch("src.ingest_review.proposal_regen_ui.streamlit_runtime", mock_st):
        _queue_proposal_regen("topic", "src-42", "pid-9", "pfx")
    assert mock_st.session_state["_pending_proposal_regen"] == {
        "entity": "topic",
        "source_id": "src-42",
        "proposal_id": "pid-9",
        "new_title": "Local Inference",
        "note": "keep multimodal in summary",
    }
