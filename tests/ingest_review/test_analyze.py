"""Tests for analyze orchestration helpers."""

from __future__ import annotations

from src.ingest_review.analyze import apply_tag_allowlists, validate_llm_dict
from src.ingest_review.schema import HowToProposal, LlmClassificationOutput, ToolProposal


def test_apply_tag_allowlists_filters_unknown() -> None:
    """Tags not on allowlists are removed from proposals."""
    parsed = LlmClassificationOutput(
        tools=[
            ToolProposal(name="X", proposed_tags=["mcp-server", "nope"]),
        ],
        how_to=[
            HowToProposal(question_title="Q", proposed_tags=["rag-retrieval", "bad"]),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        tool_tags={"mcp-server"},
        howto_tags={"rag-retrieval"},
    )
    assert out.tools[0].proposed_tags == ["mcp-server"]
    assert out.how_to[0].proposed_tags == ["rag-retrieval"]


def test_validate_llm_dict_round_trip() -> None:
    """validate_llm_dict accepts a dumped model dict."""
    data = LlmClassificationOutput().model_dump()
    again = validate_llm_dict(data)
    assert again.roundup.is_roundup is False
