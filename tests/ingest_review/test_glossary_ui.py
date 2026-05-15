"""Tests for glossary two-column UI helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.glossary_ui import (
    apply_glossary_proposal_edits,
    apply_glossary_scalar_edit,
    build_readonly_glossary_markdown,
    effective_glossary_scalar,
    format_glossary_term_readonly_markdown,
)


def _sample_node() -> dict:
    return {
        "proposal_id": "abc123",
        "proposal_status": "pending",
        "llm_item": {
            "term": "RAG",
            "proposed_definition": "Retrieval augments generation.",
            "extended_explanation": "Longer text.",
            "relevance_note": "Core pattern.",
            "confidence": 0.9,
            "value_level": "high",
            "evidence_type": "vendor_claim",
        },
        "sections": {},
        "tags": {},
    }


def test_effective_glossary_scalar_prefers_final_text() -> None:
    """final_text overrides LLM draft when set."""
    llm = {"term": "RAG"}
    sections = {"term": {"final_text": "Retrieval-Augmented Generation", "status": "modified"}}
    assert effective_glossary_scalar(llm, sections, "term") == "Retrieval-Augmented Generation"


def test_apply_glossary_scalar_edit_modified_when_differs() -> None:
    """Edited field sets status modified and stores final_text."""
    sections: dict = {}
    llm = {"proposed_definition": "Original"}
    apply_glossary_scalar_edit(sections, llm, "proposed_definition", "Edited")
    node = sections["proposed_definition"]
    assert node["status"] == "modified"
    assert node["final_text"] == "Edited"


def test_apply_glossary_scalar_edit_approved_when_unchanged() -> None:
    """Unchanged field clears final_text and sets approved."""
    sections: dict = {}
    llm = {"term": "RAG"}
    apply_glossary_scalar_edit(sections, llm, "term", "RAG")
    node = sections["term"]
    assert node["status"] == "approved"
    assert node["final_text"] is None


def test_apply_glossary_proposal_edits_all_reviewable_fields() -> None:
    """Batch apply updates every reviewable scalar section."""
    node = _sample_node()
    apply_glossary_proposal_edits(
        node,
        {
            "term": "RAG",
            "proposed_definition": "New def",
            "extended_explanation": "New ext",
            "relevance_note": "New rel",
        },
    )
    assert node["sections"]["proposed_definition"]["status"] == "modified"


def test_format_glossary_term_readonly_markdown_includes_sections() -> None:
    """Read-only term block includes heading and definition."""
    md = format_glossary_term_readonly_markdown(_sample_node(), ["rag"])
    assert "## RAG" in md
    assert "**Definition**" in md
    assert "Retrieval augments generation." in md


def test_build_readonly_glossary_markdown_tier_headers() -> None:
    """Multiple value levels get tier subheadings."""
    high = _sample_node()
    low = {
        "proposal_id": "x",
        "proposal_status": "pending",
        "llm_item": {
            "term": "Low term",
            "proposed_definition": "d",
            "value_level": "low",
        },
        "sections": {},
        "tags": {},
    }
    md = build_readonly_glossary_markdown([high, low], [])
    assert "### High value" in md
    assert "### Low value" in md
    assert "## RAG" in md
    assert "## Low term" in md
