"""Tests for trends two-column helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.trends_ui import (
    apply_trend_scalar_edit,
    effective_trend_scalar,
    format_trend_proposal_readonly_markdown,
)


def _sample_node() -> dict:
    return {
        "proposal_id": "abc",
        "proposal_status": "pending",
        "llm_item": {
            "trend_slug": "agentic-workflows",
            "trend_title": "Agentic Workflows",
            "trend_description": "Teams chain agents for complex tasks.",
            "value_level": "high",
            "confidence": 0.9,
            "evidence_type": "independent_analysis",
        },
        "sections": {},
        "tags": {},
    }


def test_effective_trend_scalar_prefers_final_text() -> None:
    llm = {"trend_title": "Draft"}
    sections = {"trend_title": {"final_text": "Final title", "status": "modified"}}
    assert effective_trend_scalar(llm, sections, "trend_title") == "Final title"


def test_apply_trend_scalar_edit_approved_when_unchanged() -> None:
    sections: dict = {}
    llm = {"trend_slug": "same-slug"}
    apply_trend_scalar_edit(sections, llm, "trend_slug", "same-slug")
    assert sections["trend_slug"]["status"] == "approved"


def test_format_trend_readonly_uses_title_and_slug() -> None:
    md = format_trend_proposal_readonly_markdown(_sample_node(), [])
    assert "## Agentic Workflows" in md
    assert "**Slug**" in md
    assert "agentic-workflows" in md
    assert "google.com/search" in md


def test_format_trend_readonly_falls_back_to_slug_for_heading() -> None:
    node = _sample_node()
    node["llm_item"] = {
        "trend_slug": "inference-cost-collapse",
        "trend_description": "Costs falling.",
    }
    md = format_trend_proposal_readonly_markdown(node, [])
    assert "inference-cost-collapse" in md
