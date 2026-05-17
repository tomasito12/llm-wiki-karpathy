"""Tests for analyze orchestration helpers."""

from __future__ import annotations

from src.ingest_review.analyze import (
    apply_tag_allowlists,
    apply_tools_roundup_entity_strip,
    sanitize_topics_related_topics,
    validate_llm_dict,
)
from src.ingest_review.glossary_related_terms_align import align_glossary_related_terms
from src.ingest_review.impl_study_gate import filter_impl_study_proposals
from src.ingest_review.schema import (
    FoundationModelProposal,
    GlossaryProposal,
    HowToProposal,
    ImplementationStudyProposal,
    IndustryTrendProposal,
    InterviewInsight,
    LlmClassificationOutput,
    RoundupSignal,
    SourceTypeDetection,
    ToolProposal,
    TopicContribution,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


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


def test_sanitize_topics_related_topics_after_tag_allowlists() -> None:
    """Tag slugs in related_topics are stripped while batch cross-links remain."""
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        topic_slugs=[],
    )
    parsed = LlmClassificationOutput(
        topics=[
            TopicContribution(
                topic_slug="alpha",
                primary_tag="ai-engineering",
                related_topics=["ai-engineering", "beta"],
            ),
            TopicContribution(topic_slug="beta", related_topics=[]),
        ],
    )
    tagged = apply_tag_allowlists(parsed, set(), set(), topic_tags={"ai-engineering"})
    out = sanitize_topics_related_topics(tagged, {"ai-engineering"}, wiki)
    assert out.topics[0].related_topics == ["beta"]


def test_apply_tag_allowlists_validates_trend_tags() -> None:
    """Trend tags not on allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        industry_trends=[
            IndustryTrendProposal(
                trend_slug="t",
                trend_title="T",
                primary_tag="a",
                secondary_tag="b",
            )
        ],
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


def test_apply_tag_allowlists_validates_impl_study_tags() -> None:
    """Implementation study tags not on allowlist are demoted to suggested_new_tag."""
    parsed = LlmClassificationOutput(
        implementation_studies=[
            ImplementationStudyProposal(
                title="T",
                company="Co",
                primary_tag="voice-ai",
                secondary_tag="not-on-list",
            ),
        ],
    )
    out = apply_tag_allowlists(
        parsed,
        set(),
        set(),
        impl_study_tags={"voice-ai"},
    )
    assert out.implementation_studies[0].primary_tag == "voice-ai"
    assert out.implementation_studies[0].secondary_tag == ""
    assert out.implementation_studies[0].suggested_new_tag == "not-on-list"


def test_filter_impl_study_proposals_via_analyze_import() -> None:
    """filter_impl_study_proposals demotes architecture-essay style proposals."""
    weak = ImplementationStudyProposal(
        title="Orchestration layers",
        company="BlogCo",
        deployment_context="",
        outcome_status="unknown",
    )
    out = filter_impl_study_proposals([weak])
    assert out[0].suggested_action == "ignore"


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


def test_validate_llm_dict_accepts_ai_tools_roundup_source_type() -> None:
    """detected_source_type may be ai_tools_roundup per schema."""
    data = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="ai_tools_roundup")
    ).model_dump()
    again = validate_llm_dict(data)
    assert again.source_type_detection.detected_source_type == "ai_tools_roundup"


def test_apply_tools_roundup_entity_strip_clears_forbidden_arrays() -> None:
    """ai_tools_roundup strips non-tool entities while preserving tools and foundation_models."""
    parsed = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="ai_tools_roundup"),
        glossary=[GlossaryProposal(term="RAG", primary_tag="a", secondary_tag="")],
        topics=[TopicContribution(topic_slug="x", primary_tag="b", secondary_tag="")],
        how_to=[HowToProposal(question_title="Q", primary_tag="c", secondary_tag="")],
        industry_trends=[
            IndustryTrendProposal(
                trend_slug="t",
                trend_title="T",
                primary_tag="d",
                secondary_tag="",
            )
        ],
        roundup_signals=[RoundupSignal(signal_title="s", primary_tag="e", secondary_tag="")],
        implementation_studies=[
            ImplementationStudyProposal(title="T", company="Co", primary_tag="f", secondary_tag=""),
        ],
        interview_insights=[
            InterviewInsight(insight_title="i", primary_tag="g", secondary_tag=""),
        ],
        tools=[ToolProposal(name="ToolA", proposed_types=["mcp-server"])],
        foundation_models=[
            FoundationModelProposal(model_name="M", proposed_types=["frontier-model"]),
        ],
    )
    out = apply_tools_roundup_entity_strip(parsed)
    assert out.tools == parsed.tools
    assert out.foundation_models == parsed.foundation_models
    assert out.glossary == []
    assert out.topics == []
    assert out.how_to == []
    assert out.industry_trends == []
    assert out.roundup_signals == []
    assert out.implementation_studies == []
    assert out.interview_insights == []


def test_apply_tools_roundup_entity_strip_noop_for_other_source_types() -> None:
    """Non-tools roundup source types are unchanged."""
    parsed = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
        topics=[TopicContribution(topic_slug="x", primary_tag="a", secondary_tag="")],
    )
    out = apply_tools_roundup_entity_strip(parsed)
    assert out.topics == parsed.topics


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
    """Proposal models default to no per-proposal evidence override (inherit source)."""
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
        assert instance.evidence_type is None, f"{cls.__name__} evidence_type should be None"


def test_validate_llm_dict_strips_invalid_evidence_type_override() -> None:
    """Invalid per-proposal evidence_type is dropped (inherit source profile)."""
    data = LlmClassificationOutput().model_dump()
    data["topics"] = [{"topic_slug": "x", "evidence_type": "bogus"}]
    again = validate_llm_dict(data)
    assert again.topics[0].evidence_type is None


def test_align_glossary_related_terms_expands_acronym_in_batch() -> None:
    """align_glossary_related_terms rewrites related_terms using sibling canonical terms."""
    parsed = LlmClassificationOutput(
        glossary=[
            GlossaryProposal(term="Constitutional AI", related_terms=["RLHF"]),
            GlossaryProposal(term="Reinforcement Learning from Human Feedback"),
        ],
    )
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    out = align_glossary_related_terms(parsed, wiki)
    assert out.glossary[0].related_terms == ["Reinforcement Learning from Human Feedback"]
