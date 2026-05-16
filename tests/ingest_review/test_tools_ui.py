"""Tests for tools review UI helpers (read-only markdown builders)."""

from __future__ import annotations

from src.ingest_review.tools_ui import (
    _prepare_tool_nodes,
    apply_tool_proposal_edits,
    apply_tool_scalar_edit,
    build_readonly_tools_markdown,
    effective_tool_scalar,
    format_tool_readonly_markdown,
)


def test_format_tool_readonly_markdown_includes_core_fields() -> None:
    """Read-only markdown reflects name, tier, types, and summary."""
    node = {
        "proposal_status": "pending",
        "llm_item": {
            "name": "AcmeAgent",
            "value_level": "high",
            "confidence": 0.9,
            "evidence_type": "benchmark",
            "suggested_action": "create",
            "proposed_types": ["mcp-server", "agent-runtime"],
            "short_description": "Does things.",
            "operational_relevance": "Useful for workflows.",
        },
    }
    md = format_tool_readonly_markdown(node)
    assert "## AcmeAgent" in md
    assert "High" in md
    assert "`mcp-server`" in md
    assert "**Summary**" in md
    assert "Does things." in md


def test_build_readonly_tools_markdown_tier_headers() -> None:
    """Catalog inserts value-tier section headers when tier changes."""
    nodes = [
        {
            "proposal_status": "pending",
            "llm_item": {"name": "A", "value_level": "high", "confidence": 1.0},
        },
        {
            "proposal_status": "pending",
            "llm_item": {"name": "B", "value_level": "low", "confidence": 0.5},
        },
    ]
    md = build_readonly_tools_markdown(nodes)
    assert "### High value" in md
    assert "### Low value" in md
    assert "## A" in md
    assert "## B" in md


def test_effective_tool_scalar_prefers_reviewer_final() -> None:
    """Reviewer final_text overrides LLM draft for read-only and field defaults."""
    llm_item = {"name": "Draft", "short_description": "Old"}
    sections = {"name": {"status": "modified", "final_text": "Final name"}}
    assert effective_tool_scalar(llm_item, sections, "name") == "Final name"
    assert effective_tool_scalar(llm_item, sections, "short_description") == "Old"


def test_apply_tool_scalar_edit_marks_modified_when_changed() -> None:
    """apply_tool_scalar_edit sets modified status when text differs from LLM."""
    llm_item = {"name": "Alpha"}
    sections: dict = {}
    apply_tool_scalar_edit(sections, llm_item, "name", "Beta")
    assert sections["name"]["status"] == "modified"
    assert sections["name"]["final_text"] == "Beta"


def test_apply_tool_proposal_edits_list_and_scalar() -> None:
    """apply_tool_proposal_edits applies scalars and list fields together."""
    node = {
        "llm_item": {
            "name": "T",
            "short_description": "S",
            "operational_relevance": "",
            "strengths": "",
            "weaknesses_limitations": "",
            "maturity_signals": "",
            "core_capabilities": ["a", "b"],
            "integration_ecosystem": [],
        },
        "sections": {},
    }
    apply_tool_proposal_edits(
        node,
        {
            "name": "T",
            "short_description": "S",
            "operational_relevance": "",
            "strengths": "",
            "weaknesses_limitations": "",
            "maturity_signals": "",
        },
        {"core_capabilities": "a\nb", "integration_ecosystem": ""},
    )
    assert node["sections"]["name"]["status"] == "approved"
    assert node["sections"]["core_capabilities"]["status"] == "approved"


def test_build_readonly_tools_markdown_empty() -> None:
    """Empty node list yields placeholder markdown."""
    assert "No tool proposals" in build_readonly_tools_markdown([])


def test_prepare_tool_nodes_sorts_and_fills_ids() -> None:
    """Nodes are sorted by value then confidence; missing ids are assigned."""
    artifact = {
        "llm_output": {
            "tools": [
                {"name": "Second", "value_level": "medium", "confidence": 0.5},
                {"name": "First", "value_level": "high", "confidence": 0.9},
            ]
        },
        "review": {
            "tools": [
                {"llm_item": {"name": "Second", "value_level": "medium", "confidence": 0.5}},
                {"llm_item": {"name": "First", "value_level": "high", "confidence": 0.9}},
            ]
        },
    }
    out = _prepare_tool_nodes(artifact)
    assert len(out) == 2
    assert all(n.get("proposal_id") for n in out)
    names = [(n.get("llm_item") or {}).get("name") for n in out]
    assert names[0] == "First"
    assert names[1] == "Second"
