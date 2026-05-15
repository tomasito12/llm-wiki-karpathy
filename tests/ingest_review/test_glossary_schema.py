"""Tests for GlossaryProposal schema and constants."""

from __future__ import annotations

from src.ingest_review.schema import (
    GLOSSARY_LIST_KEYS,
    GLOSSARY_SCALAR_KEYS,
    GlossaryProposal,
    LlmClassificationOutput,
)


def test_glossary_proposal_defaults_are_empty() -> None:
    """A default proposal has empty strings and empty lists."""
    p = GlossaryProposal()
    assert p.term == ""
    assert p.proposed_definition == ""
    assert p.extended_explanation == ""
    assert p.supporting_snippet == ""
    assert p.relevance_note == ""
    assert p.related_terms == []
    assert p.primary_tag == ""
    assert p.secondary_tag == ""
    assert p.suggested_new_tag == ""
    assert p.match_candidates == []
    assert p.confidence == 0.0
    assert p.suggested_action == "ignore"
    assert p.value_level == "medium"
    assert p.evidence_type == "unknown"


def test_glossary_proposal_full_roundtrip() -> None:
    """A fully populated proposal survives model_dump / model_validate."""
    data = {
        "term": "agentic workflow",
        "proposed_definition": "An AI workflow where the model decides its own next steps.",
        "extended_explanation": "In agentic workflows, the LLM iteratively plans and executes.",
        "supporting_snippet": "The agent decides which tool to call next...",
        "relevance_note": "Core pattern in modern AI application design.",
        "related_terms": ["tool calling", "chain of thought"],
        "primary_tag": "agentic-ai",
        "match_candidates": [
            {"title_or_slug": "agentic-workflow", "match_kind": "exact", "confidence": 0.95},
        ],
        "confidence": 0.9,
        "suggested_action": "create",
    }
    p = GlossaryProposal.model_validate(data)
    assert p.term == "agentic workflow"
    assert p.confidence == 0.9
    assert len(p.related_terms) == 2
    assert len(p.match_candidates) == 1
    dumped = p.model_dump(mode="json")
    restored = GlossaryProposal.model_validate(dumped)
    assert restored == p


def test_glossary_proposal_no_tag_gap_notes() -> None:
    """tag_gap_notes field has been removed."""
    assert not hasattr(GlossaryProposal(), "tag_gap_notes")
    assert "tag_gap_notes" not in GlossaryProposal.model_fields


def test_glossary_scalar_keys_match_model_fields() -> None:
    """GLOSSARY_SCALAR_KEYS are all valid string fields on the model."""
    model_fields = GlossaryProposal.model_fields
    for key in GLOSSARY_SCALAR_KEYS:
        assert key in model_fields, f"{key} not in GlossaryProposal"


def test_glossary_list_keys_match_model_fields() -> None:
    """GLOSSARY_LIST_KEYS are all valid list[str] fields on the model."""
    model_fields = GlossaryProposal.model_fields
    for key in GLOSSARY_LIST_KEYS:
        assert key in model_fields, f"{key} not in GlossaryProposal"


def test_llm_output_glossary_uses_enriched_model() -> None:
    """LlmClassificationOutput glossary items use the enriched GlossaryProposal."""
    data = {
        "glossary": [
            {
                "term": "MCP server",
                "proposed_definition": "A server that exposes tools to AI models.",
                "extended_explanation": "Longer explanation.",
                "supporting_snippet": "From the article...",
                "relevance_note": "Core infrastructure concept.",
                "related_terms": ["tool calling"],
                "primary_tag": "",
                "confidence": 0.8,
                "suggested_action": "create",
            },
        ],
    }
    out = LlmClassificationOutput.model_validate(data)
    assert len(out.glossary) == 1
    assert out.glossary[0].extended_explanation == "Longer explanation."
    assert out.glossary[0].relevance_note == "Core infrastructure concept."


def test_backward_compat_old_glossary_shape() -> None:
    """Old thin GlossaryProposal fields produce a valid enriched model."""
    old_data = {
        "term": "RAG",
        "proposed_definition": "Retrieval-augmented generation.",
        "supporting_snippet": "...",
        "confidence": 0.7,
        "suggested_action": "create",
    }
    p = GlossaryProposal.model_validate(old_data)
    assert p.confidence == 0.7
    assert p.extended_explanation == ""
    assert p.relevance_note == ""
    assert p.related_terms == []
    assert p.primary_tag == ""
    assert p.secondary_tag == ""
    assert p.suggested_new_tag == ""
