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


def test_apply_tag_allowlists_validates_primary_tag() -> None:
    """Primary tags not on allowlists are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        tools=[
            ToolProposal(name="X", proposed_types=["mcp-server", "nope"]),
        ],
        how_to=[
            HowToProposal(
                question_title="Q",
                primary_tag="rag-retrieval",
                secondary_tag="bad",
            ),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        tool_types={"mcp-server"},
        howto_tags={"rag-retrieval"},
    )
    assert out.tools[0].proposed_types == ["mcp-server"]
    assert out.how_to[0].primary_tag == "rag-retrieval"
    assert out.how_to[0].secondary_tag == ""
    assert out.how_to[0].suggested_new_tag == "bad"


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


def test_apply_tag_allowlists_validates_glossary_tags() -> None:
    """Glossary tags not on allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        glossary=[GlossaryProposal(term="RAG", primary_tag="known", secondary_tag="novel")],
    )
    out = apply_tag_allowlists(parsed, set(), set(), glossary_tags={"known"})
    assert out.glossary[0].primary_tag == "known"
    assert out.glossary[0].secondary_tag == ""
    assert out.glossary[0].suggested_new_tag == "novel"


def test_apply_tag_allowlists_validates_topic_tags() -> None:
    """Topic tags not on allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        topics=[TopicContribution(topic_slug="x", primary_tag="ok", secondary_tag="new-one")],
    )
    out = apply_tag_allowlists(parsed, set(), set(), topic_tags={"ok"})
    assert out.topics[0].primary_tag == "ok"
    assert out.topics[0].secondary_tag == ""
    assert out.topics[0].suggested_new_tag == "new-one"


def test_apply_tag_allowlists_validates_trend_tags() -> None:
    """Trend tags not on allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        industry_trends=[IndustryTrendProposal(trend_name="t", primary_tag="a", secondary_tag="b")],
    )
    out = apply_tag_allowlists(parsed, set(), set(), trend_tags={"a"})
    assert out.industry_trends[0].primary_tag == "a"
    assert out.industry_trends[0].secondary_tag == ""
    assert out.industry_trends[0].suggested_new_tag == "b"


def test_apply_tag_allowlists_validates_signal_tags() -> None:
    """Roundup signal tags not on trend allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        roundup_signals=[RoundupSignal(signal_title="s", primary_tag="ok", secondary_tag="novel")],
    )
    out = apply_tag_allowlists(parsed, set(), set(), trend_tags={"ok"})
    assert out.roundup_signals[0].primary_tag == "ok"
    assert out.roundup_signals[0].secondary_tag == ""
    assert out.roundup_signals[0].suggested_new_tag == "novel"


def test_apply_tag_allowlists_validates_insight_tags() -> None:
    """Interview insight tags not on topic allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        interview_insights=[
            InterviewInsight(insight_title="i", primary_tag="ok", secondary_tag="novel"),
        ],
    )
    out = apply_tag_allowlists(parsed, set(), set(), topic_tags={"ok"})
    assert out.interview_insights[0].primary_tag == "ok"
    assert out.interview_insights[0].secondary_tag == ""
    assert out.interview_insights[0].suggested_new_tag == "novel"


def test_apply_tag_allowlists_normalizes_tag_casing() -> None:
    """Tag validation matches allowlist entries after normalization."""
    parsed = LlmClassificationOutput(
        topics=[
            TopicContribution(
                topic_slug="x",
                primary_tag="AI-Safety",
                secondary_tag="Evaluation",
            ),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        set(),
        set(),
        topic_tags={"ai-safety", "evaluation"},
    )
    assert out.topics[0].primary_tag == "ai-safety"
    assert out.topics[0].secondary_tag == "evaluation"
    assert out.topics[0].suggested_new_tag == ""


def test_apply_tag_allowlists_preserves_valid_primary_secondary_pair() -> None:
    """Both tags on allowlist are kept unchanged."""
    parsed = LlmClassificationOutput(
        glossary=[
            GlossaryProposal(
                term="T",
                primary_tag="known",
                secondary_tag="also-known",
            ),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        set(),
        set(),
        glossary_tags={"known", "also-known"},
    )
    assert out.glossary[0].primary_tag == "known"
    assert out.glossary[0].secondary_tag == "also-known"
    assert out.glossary[0].suggested_new_tag == ""


def test_apply_tag_allowlists_preserves_existing_suggested_new() -> None:
    """Tags already in suggested_new_tag from LLM are preserved."""
    parsed = LlmClassificationOutput(
        glossary=[
            GlossaryProposal(
                term="X",
                primary_tag="overflow",
                suggested_new_tag="llm-proposed",
            ),
        ],
    )
    out = apply_tag_allowlists(parsed, set(), set(), glossary_tags=set())
    assert out.glossary[0].primary_tag == ""
    assert out.glossary[0].suggested_new_tag == "llm-proposed"


def test_validate_llm_dict_round_trip() -> None:
    """validate_llm_dict accepts a dumped model dict."""
    data = LlmClassificationOutput().model_dump()
    again = validate_llm_dict(data)
    assert again.source_type_detection.detected_source_type == "unknown"


def test_extraction_meta_defaults() -> None:
    """ExtractionMeta defaults are present on new LlmClassificationOutput."""
    out = LlmClassificationOutput()
    assert out.extraction_meta.skip_recommended is False
    assert out.extraction_meta.skip_reason == ""
    assert out.extraction_meta.total_candidates_considered == 0
    assert out.extraction_meta.review_burden_estimate == "moderate"


def test_value_level_defaults_on_all_proposals() -> None:
    """All proposal models default to value_level='medium'."""
    from src.ingest_review.schema import (
        FoundationModelProposal,
        GlossaryProposal,
        HowToProposal,
        ImplementationStudyProposal,
        IndustryTrendProposal,
        InterviewInsight,
        RoundupSignal,
        ToolProposal,
        TopicContribution,
    )

    for cls in (
        GlossaryProposal,
        TopicContribution,
        HowToProposal,
        IndustryTrendProposal,
        ToolProposal,
        FoundationModelProposal,
        ImplementationStudyProposal,
        RoundupSignal,
        InterviewInsight,
    ):
        instance = cls()
        assert instance.value_level == "medium", f"{cls.__name__} value_level not 'medium'"


def test_evidence_type_defaults_on_all_proposals() -> None:
    """All proposal models default to evidence_type='unknown'."""
    from src.ingest_review.schema import (
        FoundationModelProposal,
        GlossaryProposal,
        HowToProposal,
        ImplementationStudyProposal,
        IndustryTrendProposal,
        InterviewInsight,
        RoundupSignal,
        ToolProposal,
        TopicContribution,
    )

    for cls in (
        GlossaryProposal,
        TopicContribution,
        HowToProposal,
        IndustryTrendProposal,
        ToolProposal,
        FoundationModelProposal,
        ImplementationStudyProposal,
        RoundupSignal,
        InterviewInsight,
    ):
        instance = cls()
        assert instance.evidence_type == "unknown", f"{cls.__name__} evidence_type not 'unknown'"


def test_validate_llm_dict_coerces_invalid_evidence_type() -> None:
    """Invalid evidence_type in LLM JSON is coerced to unknown."""
    data = LlmClassificationOutput().model_dump()
    data["topics"] = [{"topic_slug": "x", "evidence_type": "bogus"}]
    again = validate_llm_dict(data)
    assert again.topics[0].evidence_type == "unknown"
