"""Tests for enriched ToolProposal model and key tuples."""

from __future__ import annotations

from src.ingest_review.schema import (
    TOOL_LIST_KEYS,
    TOOL_SCALAR_KEYS,
    ToolProposal,
)


def test_tool_proposal_defaults() -> None:
    """Default ToolProposal has empty fields and sane defaults."""
    tp = ToolProposal()
    assert tp.name == ""
    assert tp.short_description == ""
    assert tp.operational_relevance == ""
    assert tp.strengths == ""
    assert tp.weaknesses_limitations == ""
    assert tp.maturity_signals == ""
    assert tp.supporting_snippet == ""
    assert tp.core_capabilities == []
    assert tp.integration_ecosystem == []
    assert tp.related_tools == []
    assert tp.proposed_types == []
    assert tp.proposed_new_type is None
    assert tp.match_candidates == []
    assert tp.confidence == 0.0
    assert tp.suggested_action == "ignore"


def test_tool_proposal_scalar_keys_cover_model_fields() -> None:
    """TOOL_SCALAR_KEYS covers all string scalar fields."""
    fields = ToolProposal.model_fields
    for k in TOOL_SCALAR_KEYS:
        assert k in fields, f"Missing field: {k}"


def test_tool_proposal_list_keys_cover_model_fields() -> None:
    """TOOL_LIST_KEYS covers all list fields (excluding match_candidates/proposed_types)."""
    fields = ToolProposal.model_fields
    for k in TOOL_LIST_KEYS:
        assert k in fields, f"Missing field: {k}"


def test_tool_proposal_has_no_legacy_fields() -> None:
    """Old fields removed from ToolProposal."""
    assert not hasattr(ToolProposal, "tool_type")
    assert not hasattr(ToolProposal, "tag_gap_notes")
    assert not hasattr(ToolProposal, "proposed_tags")


def test_tool_proposal_json_roundtrip() -> None:
    """ToolProposal survives JSON serialization and deserialization."""
    tp = ToolProposal(
        name="Cursor",
        short_description="AI coding assistant.",
        operational_relevance="Improves coding workflows.",
        strengths="Strong repo awareness.",
        weaknesses_limitations="Expensive.",
        maturity_signals="Rapidly growing.",
        supporting_snippet="Quote from article.",
        core_capabilities=["codebase indexing", "MCP integration"],
        integration_ecosystem=["OpenAI-compatible APIs"],
        related_tools=["Claude Code", "Aider"],
        proposed_types=["coding-agent", "ide-extension"],
        proposed_new_type=None,
        confidence=0.85,
        suggested_action="create_new_page",
    )
    data = tp.model_dump(mode="json")
    restored = ToolProposal.model_validate(data)
    assert restored.name == "Cursor"
    assert restored.core_capabilities == ["codebase indexing", "MCP integration"]
    assert restored.proposed_types == ["coding-agent", "ide-extension"]
    assert restored.confidence == 0.85


def test_tool_proposal_proposed_new_type_nullable() -> None:
    """proposed_new_type accepts a string or None."""
    tp = ToolProposal(proposed_new_type="ai-gadget")
    assert tp.proposed_new_type == "ai-gadget"
    tp2 = ToolProposal(proposed_new_type=None)
    assert tp2.proposed_new_type is None
