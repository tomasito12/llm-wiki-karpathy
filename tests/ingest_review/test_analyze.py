"""Tests for analyze orchestration helpers."""

from __future__ import annotations

from src.ingest_review.analyze import apply_tag_allowlists, validate_llm_dict
from src.ingest_review.schema import (
    FoundationModelProposal,
    GlossaryProposal,
    HowToProposal,
    IndustryTrendProposal,
    InterviewInsight,
    LlmClassificationOutput,
    RoundupSignal,
    ToolProposal,
    TopicContribution,
)


def test_apply_tag_allowlists_splits_unknown_to_proposed_new() -> None:
    """Tags not on allowlists move to proposed_new_tags instead of being discarded."""
    parsed = LlmClassificationOutput(
        tools=[
            ToolProposal(name="X", proposed_types=["mcp-server", "nope"]),
        ],
        how_to=[
            HowToProposal(question_title="Q", proposed_tags=["rag-retrieval", "bad"]),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        tool_types={"mcp-server"},
        howto_tags={"rag-retrieval"},
    )
    assert out.tools[0].proposed_types == ["mcp-server"]
    assert out.how_to[0].proposed_tags == ["rag-retrieval"]
    assert out.how_to[0].proposed_new_tags == ["bad"]


def test_apply_tag_allowlists_filters_model_types() -> None:
    """Model types not on the allowlist are removed from proposals."""
    parsed = LlmClassificationOutput(
        foundation_models=[
            FoundationModelProposal(
                model_name="GPT-5",
                proposed_types=["frontier-model", "not-allowed"],
            ),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        tool_types=set(),
        howto_tags=set(),
        model_types={"frontier-model"},
    )
    assert out.foundation_models[0].proposed_types == ["frontier-model"]


def test_apply_tag_allowlists_splits_glossary_tags() -> None:
    """Glossary tags not on allowlist move to proposed_new_tags."""
    parsed = LlmClassificationOutput(
        glossary=[GlossaryProposal(term="RAG", proposed_tags=["known", "novel"])],
    )
    out = apply_tag_allowlists(parsed, set(), set(), glossary_tags={"known"})
    assert out.glossary[0].proposed_tags == ["known"]
    assert out.glossary[0].proposed_new_tags == ["novel"]


def test_apply_tag_allowlists_splits_topic_tags() -> None:
    """Topic tags not on allowlist move to proposed_new_tags."""
    parsed = LlmClassificationOutput(
        topics=[TopicContribution(topic_slug="x", proposed_tags=["ok", "new-one"])],
    )
    out = apply_tag_allowlists(parsed, set(), set(), topic_tags={"ok"})
    assert out.topics[0].proposed_tags == ["ok"]
    assert out.topics[0].proposed_new_tags == ["new-one"]


def test_apply_tag_allowlists_splits_trend_tags() -> None:
    """Trend tags not on allowlist move to proposed_new_tags."""
    parsed = LlmClassificationOutput(
        industry_trends=[IndustryTrendProposal(trend_name="t", proposed_tags=["a", "b"])],
    )
    out = apply_tag_allowlists(parsed, set(), set(), trend_tags={"a"})
    assert out.industry_trends[0].proposed_tags == ["a"]
    assert out.industry_trends[0].proposed_new_tags == ["b"]


def test_apply_tag_allowlists_splits_signal_tags() -> None:
    """Roundup signal tags not on trend allowlist move to proposed_new_tags."""
    parsed = LlmClassificationOutput(
        roundup_signals=[RoundupSignal(signal_title="s", proposed_tags=["ok", "novel"])],
    )
    out = apply_tag_allowlists(parsed, set(), set(), trend_tags={"ok"})
    assert out.roundup_signals[0].proposed_tags == ["ok"]
    assert out.roundup_signals[0].proposed_new_tags == ["novel"]


def test_apply_tag_allowlists_splits_insight_tags() -> None:
    """Interview insight tags not on topic allowlist move to proposed_new_tags."""
    parsed = LlmClassificationOutput(
        interview_insights=[InterviewInsight(insight_title="i", proposed_tags=["ok", "novel"])],
    )
    out = apply_tag_allowlists(parsed, set(), set(), topic_tags={"ok"})
    assert out.interview_insights[0].proposed_tags == ["ok"]
    assert out.interview_insights[0].proposed_new_tags == ["novel"]


def test_apply_tag_allowlists_preserves_existing_proposed_new() -> None:
    """Tags already in proposed_new_tags from LLM are preserved."""
    parsed = LlmClassificationOutput(
        glossary=[
            GlossaryProposal(
                term="X",
                proposed_tags=["overflow"],
                proposed_new_tags=["llm-proposed"],
            ),
        ],
    )
    out = apply_tag_allowlists(parsed, set(), set(), glossary_tags=set())
    assert "overflow" in out.glossary[0].proposed_new_tags
    assert "llm-proposed" in out.glossary[0].proposed_new_tags


def test_validate_llm_dict_round_trip() -> None:
    """validate_llm_dict accepts a dumped model dict."""
    data = LlmClassificationOutput().model_dump()
    again = validate_llm_dict(data)
    assert again.source_type_detection.detected_source_type == "unknown"
