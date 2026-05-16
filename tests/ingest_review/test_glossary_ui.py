"""Tests for glossary two-column UI helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.glossary_related_terms_align import build_related_term_resolution_maps
from src.ingest_review.glossary_ui import (
    apply_glossary_proposal_edits,
    apply_glossary_scalar_edit,
    build_readonly_glossary_markdown,
    collect_glossary_new_tags,
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


def test_format_glossary_shows_warning_for_unaligned_related_terms() -> None:
    """Read-only markdown flags related strings that do not resolve to batch/wiki labels."""
    node = {
        "llm_item": {
            "term": "Alpha",
            "proposed_definition": "d",
            "related_terms": ["not-in-index"],
            "value_level": "high",
        },
        "sections": {},
    }
    norm_to, acr_to = build_related_term_resolution_maps(["Alpha"], [])
    md = format_glossary_term_readonly_markdown(
        node,
        [],
        norm_to=norm_to,
        acr_to=acr_to,
    )
    assert "not-in-index" in md
    assert "not matching any sibling or wiki glossary label" in md


def test_effective_glossary_scalar_normalizes_term_display() -> None:
    """Term field is shown with leading letter capitalized when LLM used lowercase."""
    llm = {"term": "kanban"}
    assert effective_glossary_scalar(llm, {}, "term") == "Kanban"


def test_apply_glossary_scalar_edit_term_approve_normalizes_llm_item() -> None:
    """Saving a lowercase term that matches normalized draft approves and updates llm_item."""
    sections: dict = {}
    llm: dict = {"term": "frontmatter"}
    apply_glossary_scalar_edit(sections, llm, "term", "frontmatter")
    assert sections["term"]["status"] == "approved"
    assert llm["term"] == "Frontmatter"


def test_format_glossary_term_readonly_markdown_tags_after_definition() -> None:
    """Read-only block places **Tags** after definition and before extended explanation."""
    node = _sample_node()
    node["llm_item"] = dict(node["llm_item"])
    node["llm_item"]["primary_tag"] = "agentic-workflows"
    node["llm_item"]["extended_explanation"] = "Ext body."
    md = format_glossary_term_readonly_markdown(node, ["agentic-workflows"])
    def_pos = md.index("**Definition**")
    tags_pos = md.index("**Tags**")
    ext_pos = md.index("**Extended explanation**")
    assert def_pos < tags_pos < ext_pos
    assert "agentic-workflows" in md


def test_format_glossary_term_readonly_hides_offlist_llm_tags_without_final() -> None:
    """LLM off-allowlist tags are omitted from read-only until reviewer sets a final.*"""
    node = _sample_node()
    node["llm_item"] = dict(node["llm_item"])
    node["llm_item"]["primary_tag"] = "made-up-slug"
    md = format_glossary_term_readonly_markdown(node, ["rag", "orchestration"])
    assert "**Tags**" not in md


def test_format_glossary_term_readonly_shows_final_offlist_tag() -> None:
    """Reviewer final tag is shown even when not yet on the allowlist."""
    node = _sample_node()
    node["tags"] = {"final_primary_tag": "custom-slug"}
    md = format_glossary_term_readonly_markdown(node, ["rag"])
    assert "**Tags**" in md
    assert "custom-slug" in md


def test_collect_glossary_new_tags_normalizes_suggested() -> None:
    """Exporter normalizes suggested_new_tag strings."""
    artifact = {
        "review": {
            "glossary": [
                {
                    "tags": {"new_tag_approved": True},
                    "llm_item": {"suggested_new_tag": "  My Tag  "},
                }
            ]
        }
    }
    assert collect_glossary_new_tags(artifact) == ["my-tag"]
