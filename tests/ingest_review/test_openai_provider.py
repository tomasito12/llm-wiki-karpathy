"""Tests for OpenAI ingestion provider (mocked HTTP client)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.ingest_review.extract import load_readwise_pair
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.schema import LlmClassificationOutput
from src.ingest_review.wiki_snapshot import WikiSnapshot


@pytest.fixture(autouse=True)
def _monolithic_classification_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing provider tests target the monolithic prompt path."""
    monkeypatch.setenv("INGEST_CLASSIFICATION_PIPELINE", "monolithic")


def test_openai_provider_parses_json_response(tmp_path: Path) -> None:
    """Provider validates model JSON against the Pydantic schema."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-01"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    sample = LlmClassificationOutput()
    raw_json = json.dumps(sample.model_dump())

    class _Msg:
        content = raw_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 1}

    class _Completion:
        id = "cmpl-test"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()

    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prov = OpenAIIngestionProvider(client=fake_client)
    out, meta = prov.analyze_classification(
        document=doc,
        wiki=wiki,
        tool_types_allowlist=["mcp-server"],
        howto_tags_allowlist=["rag-retrieval"],
        model_types_allowlist=["frontier-model"],
        model="gpt-test",
        prompt_version="2",
        max_retries=2,
    )
    assert isinstance(out, LlmClassificationOutput)
    assert meta["request_id"] == "cmpl-test"


def test_openai_prompt_contains_source_type_rubrics(tmp_path: Path) -> None:
    """Prompt includes source type detection, roundup signals, and interview insights rubrics."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-rubric"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    sample = LlmClassificationOutput()
    raw_json = json.dumps(sample.model_dump())

    class _Msg:
        content = raw_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 1}

    class _Completion:
        id = "cmpl-rubric"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()

    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prov = OpenAIIngestionProvider(client=fake_client)
    prov.analyze_classification(
        document=doc,
        wiki=wiki,
        tool_types_allowlist=[],
        howto_tags_allowlist=[],
        model="gpt-test",
        prompt_version="2",
        max_retries=1,
    )
    call_args = fake_client.chat.completions.create.call_args
    user_msg = call_args.kwargs["messages"][1]["content"]
    assert "SOURCE_TYPE_DETECTION_RUBRIC" in user_msg
    assert "related_terms" in user_msg
    assert "exact same spelling" in user_msg
    assert "ROUNDUP_SIGNALS_RUBRIC" in user_msg
    assert "INTERVIEW_INSIGHTS_RUBRIC" in user_msg
    assert "## AI_TOOLS_ROUNDUP_EXTRACTION" in user_msg
    assert "do NOT cap tools or foundation_models" in user_msg
    assert "source_type_detection" in user_msg


def test_openai_prompt_includes_source_type_override(tmp_path: Path) -> None:
    """source_type_override injects an override block into the prompt."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-override"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    sample = LlmClassificationOutput()
    raw_json = json.dumps(sample.model_dump())

    class _Msg:
        content = raw_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 1}

    class _Completion:
        id = "cmpl-override"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()

    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prov = OpenAIIngestionProvider(client=fake_client)
    prov.analyze_classification(
        document=doc,
        wiki=wiki,
        tool_types_allowlist=[],
        howto_tags_allowlist=[],
        source_type_override="ai_industry_roundup",
        model="gpt-test",
        prompt_version="2",
        max_retries=1,
    )
    call_args = fake_client.chat.completions.create.call_args
    user_msg = call_args.kwargs["messages"][1]["content"]
    assert "SOURCE_TYPE_OVERRIDE" in user_msg
    assert "ai_industry_roundup" in user_msg


def test_prompt_contains_temporal_anchoring_rule(tmp_path: Path) -> None:
    """Prompt includes the TEMPORAL_ANCHORING_RULE block after Metadata."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-temporal"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    sample = LlmClassificationOutput()
    raw_json = json.dumps(sample.model_dump())

    class _Msg:
        content = raw_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 1}

    class _Completion:
        id = "cmpl-temporal"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()

    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prov = OpenAIIngestionProvider(client=fake_client)
    prov.analyze_classification(
        document=doc,
        wiki=wiki,
        tool_types_allowlist=[],
        howto_tags_allowlist=[],
        model="gpt-test",
        prompt_version="3",
        max_retries=1,
    )
    call_args = fake_client.chat.completions.create.call_args
    user_msg = call_args.kwargs["messages"][1]["content"]
    assert "TEMPORAL ANCHORING RULE" in user_msg
    assert "published_date" in user_msg
    assert "assessed_as_of" in user_msg


def test_rubric_has_no_unanchored_temporal_language() -> None:
    """Rubric constants must not contain banned unanchored temporal phrases."""
    from src.ingest_review.providers.openai_provider import (
        INTERVIEW_INSIGHTS_RUBRIC,
        MODELS_RUBRIC,
        ROUNDUP_SIGNALS_RUBRIC,
        SOURCE_CHAPTERS_RUBRIC,
    )

    banned_phrases = [
        "within 1-2 years",
        "within 1–2 years",
        "immediately useful",
        "useful in 6-12 months",
        "useful in 6–12 months",
        "matter in 6-12 months",
        "matter in 6–12 months",
    ]
    rubrics = {
        "SOURCE_CHAPTERS_RUBRIC": SOURCE_CHAPTERS_RUBRIC,
        "MODELS_RUBRIC": MODELS_RUBRIC,
        "ROUNDUP_SIGNALS_RUBRIC": ROUNDUP_SIGNALS_RUBRIC,
        "INTERVIEW_INSIGHTS_RUBRIC": INTERVIEW_INSIGHTS_RUBRIC,
    }
    for name, text in rubrics.items():
        for phrase in banned_phrases:
            assert phrase not in text, f"Banned phrase {phrase!r} found in {name}"


def test_openai_regenerate_source_section_parses_json(tmp_path: Path) -> None:
    """Narrow regen call validates SectionRegenerateOutput JSON."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-regen"
    (raw / f"{stem}.html").write_text("<p>hello world</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    regen_json = '{"section_key": "summary", "content": "Regenerated summary."}'

    class _Msg:
        content = regen_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 2}

    class _Completion:
        id = "cmpl-regen"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()
    prov = OpenAIIngestionProvider(client=fake_client)
    fragment, meta = prov.regenerate_source_section(
        document=doc,
        section_key="summary",
        current_value="old",
        reviewer_instruction=None,
        model="gpt-test",
        prompt_version="2",
        max_plain_text_chars=10_000,
        max_retries=2,
    )
    assert fragment["section_key"] == "summary"
    assert fragment["content"] == "Regenerated summary."
    assert meta["request_id"] == "cmpl-regen"


def test_openai_regenerate_topic_proposal_parses_json(tmp_path: Path) -> None:
    """Narrow topic regen call validates TopicRegenerateOutput JSON."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-topic-regen"
    (raw / f"{stem}.html").write_text("<p>local inference on device</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    regen_json = json.dumps(
        {
            "knowledge_summary": "Broader local inference including multimodal stacks.",
            "examples": "Vision + text on device.",
            "operational_insight": "Sample eval calls at scale.",
            "relevance_note": "Core deployment pattern.",
            "key_points": ["sampling"],
            "supporting_snippet": "local inference on device",
            "related_topics": ["edge-inference"],
            "confidence": 0.75,
            "suggested_action": "append_to_existing",
            "value_level": "high",
            "evidence_type": "independent_analysis",
        }
    )

    class _Msg:
        content = regen_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 4}

    class _Completion:
        id = "cmpl-topic-regen"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()
    prov = OpenAIIngestionProvider(client=fake_client)
    fragment, meta = prov.regenerate_topic_proposal(
        document=doc,
        current_topic={"topic_title": "Local Multimodal Inference"},
        new_title="Local Inference",
        reviewer_instruction="keep multimodal in summary",
        topic_tags_allowlist=["ai-infrastructure"],
        existing_topic_slugs=["edge-inference"],
        model="gpt-test",
        prompt_version="21",
        max_plain_text_chars=10_000,
        max_retries=2,
    )
    assert "multimodal" in fragment["knowledge_summary"]
    assert "topic_title" not in fragment
    assert meta["request_id"] == "cmpl-topic-regen"
    call_kwargs = fake_client.chat.completions.create.call_args.kwargs
    user_content = call_kwargs["messages"][1]["content"]
    assert "NEW_TOPIC_TITLE: Local Inference" in user_content
    assert "keep multimodal in summary" in user_content


def test_topic_regen_rubric_emphasizes_broader_title() -> None:
    """TOPIC_REGEN_RUBRIC reframes under reviewer title and keeps narrow angles in body."""
    from src.ingest_review.proposal_regen_provider import TOPIC_REGEN_RUBRIC

    assert "NEW_TOPIC_TITLE" in TOPIC_REGEN_RUBRIC
    assert "broader title NEW_TOPIC_TITLE" in TOPIC_REGEN_RUBRIC
    assert "knowledge_summary" in TOPIC_REGEN_RUBRIC
    assert "topic_title or topic_slug" in TOPIC_REGEN_RUBRIC


@pytest.mark.parametrize(
    ("rubric_name", "new_title_token", "forbidden_output"),
    [
        ("GLOSSARY_REGEN_RUBRIC", "NEW_TERM", "term"),
        ("HOWTO_REGEN_RUBRIC", "NEW_PAGE_TITLE", "question_title"),
        ("TREND_REGEN_RUBRIC", "NEW_TREND_TITLE", "trend_title"),
        ("TOOL_REGEN_RUBRIC", "NEW_TOOL_NAME", "name"),
        ("MODEL_REGEN_RUBRIC", "NEW_MODEL_NAME", "model_name"),
        ("IMPL_STUDY_REGEN_RUBRIC", "NEW_STUDY_TITLE", "title"),
    ],
)
def test_entity_regen_rubrics_mention_new_title_and_exclude_identifier(
    rubric_name: str,
    new_title_token: str,
    forbidden_output: str,
) -> None:
    from src.ingest_review import proposal_regen_provider as mod

    rubric = getattr(mod, rubric_name)
    assert new_title_token in rubric
    assert (
        f"Do not output {forbidden_output}" in rubric or f"not output {forbidden_output}" in rubric
    )


def test_openai_suggest_glossary_review_tag_parses_json() -> None:
    """Narrow tag-suggestion call validates GlossaryTagSuggestOutput JSON."""
    suggest_json = '{"suggested_tag": "graph-rag"}'

    class _Msg:
        content = suggest_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"total_tokens": 3}

    class _Completion:
        id = "cmpl-tag-suggest"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()
    prov = OpenAIIngestionProvider(client=fake_client)
    tags, meta = prov.suggest_domain_review_tag(
        entity_label="RAG",
        context_summary="Retrieval augments context.",
        allowlist=["orchestration", "evaluation"],
        model="gpt-test",
        prompt_version="9",
    )
    assert tags == ["graph-rag"]
    assert meta["request_id"] == "cmpl-tag-suggest"


def test_openai_suggest_glossary_review_tag_strips_allowlist_collision() -> None:
    """If the model echoes an allowlist tag, return empty string."""
    suggest_json = '{"suggested_tag": "orchestration"}'

    class _Msg:
        content = suggest_json

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {}

    class _Completion:
        id = "x"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()
    prov = OpenAIIngestionProvider(client=fake_client)
    tags, _meta = prov.suggest_domain_review_tag(
        entity_label="T",
        context_summary="D",
        allowlist=["orchestration"],
        model="gpt-test",
        prompt_version="1",
    )
    assert tags == []


def test_rubrics_mention_suggested_new_tag() -> None:
    """All entity-type rubrics include suggested_new_tag field instructions."""
    from src.ingest_review.providers.openai_provider import (
        GLOSSARY_RUBRIC,
        HOWTOS_RUBRIC,
        INTERVIEW_INSIGHTS_RUBRIC,
        ROUNDUP_SIGNALS_RUBRIC,
        TOPICS_RUBRIC,
        TRENDS_RUBRIC,
    )

    for name, rubric in [
        ("GLOSSARY_RUBRIC", GLOSSARY_RUBRIC),
        ("TOPICS_RUBRIC", TOPICS_RUBRIC),
        ("HOWTOS_RUBRIC", HOWTOS_RUBRIC),
        ("TRENDS_RUBRIC", TRENDS_RUBRIC),
        ("ROUNDUP_SIGNALS_RUBRIC", ROUNDUP_SIGNALS_RUBRIC),
        ("INTERVIEW_INSIGHTS_RUBRIC", INTERVIEW_INSIGHTS_RUBRIC),
    ]:
        assert "proposed_tags" in rubric or "TAG_ONTOLOGY_RUBRIC" in rubric, (
            f"{name} missing proposed_tags / TAG_ONTOLOGY_RUBRIC"
        )
        assert "suggested_new_tags" in rubric or "TAG_ONTOLOGY_RUBRIC" in rubric, (
            f"{name} missing suggested_new_tags / TAG_ONTOLOGY_RUBRIC"
        )


def test_system_prompt_mentions_tag_structure() -> None:
    """SYSTEM_PROMPT delegates tag rules to TAG_ONTOLOGY_RUBRIC."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "TAG_ONTOLOGY_RUBRIC" in SYSTEM_PROMPT
    assert "REGISTRY_TYPES_SEMANTICS" in SYSTEM_PROMPT
    assert "proposed_types" in SYSTEM_PROMPT


def test_system_prompt_includes_extraction_meta() -> None:
    """SYSTEM_PROMPT references extraction_meta and value_level."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "extraction_meta" in SYSTEM_PROMPT
    assert "value_level" in SYSTEM_PROMPT
    assert "source_evidence_profile" in SYSTEM_PROMPT
    assert "roundup_signals" in SYSTEM_PROMPT
    assert "interview_insights" in SYSTEM_PROMPT


def test_rubrics_mention_optional_evidence_override() -> None:
    """Entity rubrics mention optional per-proposal evidence_type override."""
    from src.ingest_review.providers.openai_provider import (
        GLOSSARY_RUBRIC,
        HOWTOS_RUBRIC,
        INTERVIEW_INSIGHTS_RUBRIC,
        MODELS_RUBRIC,
        ROUNDUP_SIGNALS_RUBRIC,
        TOOLS_RUBRIC,
        TOPICS_RUBRIC,
        TRENDS_RUBRIC,
    )

    for name, rubric in [
        ("GLOSSARY_RUBRIC", GLOSSARY_RUBRIC),
        ("TOPICS_RUBRIC", TOPICS_RUBRIC),
        ("HOWTOS_RUBRIC", HOWTOS_RUBRIC),
        ("TRENDS_RUBRIC", TRENDS_RUBRIC),
        ("TOOLS_RUBRIC", TOOLS_RUBRIC),
        ("MODELS_RUBRIC", MODELS_RUBRIC),
        ("ROUNDUP_SIGNALS_RUBRIC", ROUNDUP_SIGNALS_RUBRIC),
        ("INTERVIEW_INSIGHTS_RUBRIC", INTERVIEW_INSIGHTS_RUBRIC),
    ]:
        assert "evidence_type" in rubric, f"{name} missing evidence_type"


def test_source_evidence_profile_rubric_in_user_prompt(tmp_path: Path) -> None:
    """User prompt includes SOURCE_EVIDENCE_PROFILE_RUBRIC block."""
    from src.ingest_review.providers.openai_provider import (
        SOURCE_EVIDENCE_PROFILE_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-ev"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="7",
    )
    assert SOURCE_EVIDENCE_PROFILE_RUBRIC.split("\n")[0] in prompt
    assert "source_evidence_profile" in prompt
    assert "vendor_claim" in prompt


def test_glossary_rubric_has_no_article_referencing_language() -> None:
    """Glossary relevance_note instruction must not reference the source article."""
    from src.ingest_review.providers.openai_provider import GLOSSARY_RUBRIC

    banned = [
        "in the context of THIS article",
        "article-specific relevance",
        "why the source makes this",
    ]
    lower = GLOSSARY_RUBRIC.lower()
    for phrase in banned:
        assert phrase.lower() not in lower, (
            f"GLOSSARY_RUBRIC still contains banned phrase: {phrase!r}"
        )
    assert "NEVER reference the article" in GLOSSARY_RUBRIC


def test_topics_rubric_relevance_note_avoids_article_framing() -> None:
    """Topics relevance_note must instruct industry relevance, not article context."""
    from src.ingest_review.providers.openai_provider import TOPICS_RUBRIC

    assert "why this **topic** matters" in TOPICS_RUBRIC
    assert "NOT why it appeared in this source" in TOPICS_RUBRIC
    assert 'NEVER reference the article ("the article"' in TOPICS_RUBRIC
    banned = [
        "why this matters in the context of this source",
        "in the context of this source",
    ]
    lower = TOPICS_RUBRIC.lower()
    for phrase in banned:
        assert phrase.lower() not in lower, (
            f"TOPICS_RUBRIC still contains banned phrase: {phrase!r}"
        )


def test_topics_rubric_related_topics_not_tags() -> None:
    """related_topics must be distinguished from TOPIC_TAGS_ALLOWLIST."""
    from src.ingest_review.providers.openai_provider import TOPICS_RUBRIC

    assert "Do **NOT** put TOPIC_TAGS_ALLOWLIST" in TOPICS_RUBRIC
    assert "related_topics vs tags" in TOPICS_RUBRIC
    assert "ai-engineering" in TOPICS_RUBRIC


def test_glossary_rubric_includes_extraction_boundaries() -> None:
    """GLOSSARY_RUBRIC routes generic terms away and defers to abstraction rubric."""
    from src.ingest_review.providers.openai_provider import GLOSSARY_RUBRIC

    assert "GLOSSARY EXTRACTION BOUNDARIES" in GLOSSARY_RUBRIC
    assert "GLOSSARY HARD EXCLUSIONS" in GLOSSARY_RUBRIC
    assert "not a dictionary of common terms" in GLOSSARY_RUBRIC
    assert "ABSTRACTION_SELECTION_RUBRIC" in GLOSSARY_RUBRIC
    assert "last" in GLOSSARY_RUBRIC.lower()


def test_glossary_hard_exclusions_block() -> None:
    """GLOSSARY_RUBRIC defines hard exclusions, positive bar, and named negatives."""
    from src.ingest_review.providers.openai_provider import GLOSSARY_RUBRIC

    assert "GLOSSARY HARD EXCLUSIONS" in GLOSSARY_RUBRIC
    assert "Generic business vocabulary" in GLOSSARY_RUBRIC
    assert "Generic software terms" in GLOSSARY_RUBRIC
    assert "Mature web standards" in GLOSSARY_RUBRIC
    assert "Basic AI terminology" in GLOSSARY_RUBRIC
    assert "Ontology-worthy" in GLOSSARY_RUBRIC
    assert "Operationally differentiating" in GLOSSARY_RUBRIC
    assert "Benchmark" in GLOSSARY_RUBRIC
    assert "Knowledge Management" in GLOSSARY_RUBRIC
    assert "Passkey" in GLOSSARY_RUBRIC
    assert "WCAG" in GLOSSARY_RUBRIC
    assert "flywheel" in GLOSSARY_RUBRIC


def test_tag_ontology_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes tag ontology and registry types semantics."""
    from src.ingest_review.providers.openai_provider import (
        REGISTRY_TYPES_SEMANTICS,
        TAG_ONTOLOGY_RUBRIC,
        TOOLS_RUBRIC,
        TOPICS_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-tags"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=["coding-agent"],
        howto_tags=["rag"],
        glossary_tags=["evaluation"],
        topic_tags=["orchestration"],
        trend_tags=["adoption"],
        prompt_version="9",
    )
    assert TAG_ONTOLOGY_RUBRIC.split("\n")[0] in prompt
    assert REGISTRY_TYPES_SEMANTICS.split("\n")[0] in prompt
    assert "minimize drift" in prompt.lower()
    assert "retrieval anchors" in prompt.lower()
    assert "execution-layer-transformation" in prompt
    assert "TOOL_TAGS_ALLOWLIST" in prompt
    assert "proposed_tags" in TAG_ONTOLOGY_RUBRIC
    assert "TOPIC_TAGS_ALLOWLIST" in TOPICS_RUBRIC
    assert "proposed_types" in TOOLS_RUBRIC


def test_source_chapters_rubric_includes_accessible_overview() -> None:
    """SOURCE_CHAPTERS_RUBRIC defines Easy read for newcomers."""
    from src.ingest_review.providers.openai_provider import SOURCE_CHAPTERS_RUBRIC

    assert "**accessible_overview**" in SOURCE_CHAPTERS_RUBRIC
    assert "Easy read" in SOURCE_CHAPTERS_RUBRIC
    assert "abbreviations" in SOURCE_CHAPTERS_RUBRIC.lower()
    assert "7–10 sentences" in SOURCE_CHAPTERS_RUBRIC


def test_accessible_overview_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes accessible_overview instructions."""
    from src.ingest_review.providers.openai_provider import _build_user_prompt

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-easy"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="11",
    )
    assert "accessible_overview" in prompt
    assert "Easy read" in prompt


def test_section_regen_rubric_accessible_overview() -> None:
    """Per-section regen includes accessible_overview rubric."""
    from src.ingest_review.providers.openai_provider import _section_regen_rubric

    rubric = _section_regen_rubric("accessible_overview")
    assert rubric
    assert "newcomer" in rubric.lower() or "abbreviations" in rubric.lower()


def test_system_prompt_dual_voice_for_accessible_overview() -> None:
    """SYSTEM_PROMPT distinguishes practitioner summary from Easy read voice."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "accessible_overview" in SYSTEM_PROMPT
    assert "newcomer" in SYSTEM_PROMPT.lower() or "newcomer to AI" in SYSTEM_PROMPT


def test_impl_study_rubric_includes_worthiness_gate() -> None:
    """IMPL_STUDY_RUBRIC defines evidence gate, anti-patterns, and routing."""
    from src.ingest_review.providers.openai_provider import IMPL_STUDY_RUBRIC

    assert "IMPLEMENTATION_STUDY_WORTHINESS GATE" in IMPL_STUDY_RUBRIC
    assert "at least ONE" in IMPL_STUDY_RUBRIC
    assert "weekend" in IMPL_STUDY_RUBRIC.lower()
    assert "implementation_studies: []" in IMPL_STUDY_RUBRIC
    assert "EXTRACTION BOUNDARIES" in IMPL_STUDY_RUBRIC
    assert "ABSTRACTION_SELECTION_RUBRIC" in IMPL_STUDY_RUBRIC


def test_impl_study_worthiness_gate_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes implementation study worthiness gate."""
    from src.ingest_review.providers.openai_provider import IMPL_STUDY_RUBRIC, _build_user_prompt

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-impl"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="10",
    )
    assert "IMPLEMENTATION_STUDY_WORTHINESS GATE" in prompt
    assert "worthiness gate passes" in prompt
    assert IMPL_STUDY_RUBRIC.split("\n")[0] in prompt


def test_topics_and_howtos_rubric_reference_abstraction_selection() -> None:
    """Topics and how-tos rubrics delegate layer selection to global rubric."""
    from src.ingest_review.providers.openai_provider import HOWTOS_RUBRIC, TOPICS_RUBRIC

    assert "ABSTRACTION_SELECTION_RUBRIC" in TOPICS_RUBRIC
    assert "ABSTRACTION_SELECTION_RUBRIC" in HOWTOS_RUBRIC


def test_howtos_rubric_title_granularity_rules() -> None:
    """HOWTOS_RUBRIC requires broad noun-phrase page titles, not interrogative questions."""
    from src.ingest_review.providers.openai_provider import HOWTOS_RUBRIC

    assert "Title granularity" in HOWTOS_RUBRIC
    assert "wiki page title" in HOWTOS_RUBRIC
    assert "short noun phrase" in HOWTOS_RUBRIC
    assert "How do you" in HOWTOS_RUBRIC
    assert "Evaluation of a Production Voicebot" in HOWTOS_RUBRIC
    assert "EXISTING_HOWTO_TITLES" in HOWTOS_RUBRIC
    assert "suggested_action" not in HOWTOS_RUBRIC
    assert "micro-howto" in HOWTOS_RUBRIC
    assert "what_and_problem" in HOWTOS_RUBRIC
    assert "Plain-language fields" in HOWTOS_RUBRIC
    assert "relevance_note" not in HOWTOS_RUBRIC


def test_system_prompt_howto_titles_are_page_names() -> None:
    """SYSTEM_PROMPT reinforces how-to titles as page names, not questions."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "question_title is a wiki page name" in SYSTEM_PROMPT
    assert "HOWTOS_RUBRIC" in SYSTEM_PROMPT


def test_abstraction_selection_rubric_content() -> None:
    """ABSTRACTION_SELECTION_RUBRIC defines layer arbitration and tie-breakers."""
    from src.ingest_review.providers.openai_provider import ABSTRACTION_SELECTION_RUBRIC

    assert "MOST durable" in ABSTRACTION_SELECTION_RUBRIC
    assert "Highest reuse potential" in ABSTRACTION_SELECTION_RUBRIC
    assert "Lowest duplication risk" in ABSTRACTION_SELECTION_RUBRIC
    assert "complementary" in ABSTRACTION_SELECTION_RUBRIC.lower()
    assert "one primary entity type" in ABSTRACTION_SELECTION_RUBRIC.lower()
    assert "Agent Harness Engineering" in ABSTRACTION_SELECTION_RUBRIC
    assert "GLOSSARY HARD EXCLUSIONS" in ABSTRACTION_SELECTION_RUBRIC
    assert "Voicebox" in ABSTRACTION_SELECTION_RUBRIC
    assert "tools: []" in ABSTRACTION_SELECTION_RUBRIC
    assert "ai_tools_roundup" in ABSTRACTION_SELECTION_RUBRIC


def test_abstraction_selection_requires_tools_on_deep_product_reviews() -> None:
    from src.ingest_review.providers.openai_provider import (
        ABSTRACTION_SELECTION_RUBRIC,
        COMPRESSION_PRESSURE_RUBRIC,
        SYSTEM_PROMPT,
        TOOLS_RUBRIC,
    )

    assert "complementary ``tools``" in SYSTEM_PROMPT
    assert "Single-product reviews" in TOOLS_RUBRIC
    assert "MUST extract that product" in TOOLS_RUBRIC
    assert "Exception (complementary layers)" in COMPRESSION_PRESSURE_RUBRIC
    assert "Named product/model + cross-cutting pattern" in ABSTRACTION_SELECTION_RUBRIC


def test_system_prompt_references_abstraction_rubric() -> None:
    """SYSTEM_PROMPT delegates entity-type choice to ABSTRACTION_SELECTION_RUBRIC."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "ABSTRACTION_SELECTION_RUBRIC" in SYSTEM_PROMPT
    assert "ontology compression" in SYSTEM_PROMPT.lower()


def test_abstraction_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes abstraction rubric before entity rubrics."""
    from src.ingest_review.providers.openai_provider import (
        ABSTRACTION_SELECTION_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-abstraction"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="30",
    )
    assert "## ABSTRACTION SELECTION" in prompt
    assert ABSTRACTION_SELECTION_RUBRIC.split("\n")[0] in prompt
    gloss_idx = prompt.index("## GLOSSARY_RUBRIC")
    abs_idx = prompt.index("## ABSTRACTION SELECTION")
    assert abs_idx < gloss_idx


def test_entity_rubrics_reference_abstraction_rubric() -> None:
    """Entity rubrics cross-reference the global abstraction selection rubric."""
    from src.ingest_review.providers.openai_provider import (
        GLOSSARY_RUBRIC,
        HOWTOS_RUBRIC,
        IMPL_STUDY_RUBRIC,
        TOOLS_RUBRIC,
        TOPICS_RUBRIC,
    )

    for name, rubric in [
        ("GLOSSARY_RUBRIC", GLOSSARY_RUBRIC),
        ("TOPICS_RUBRIC", TOPICS_RUBRIC),
        ("HOWTOS_RUBRIC", HOWTOS_RUBRIC),
        ("IMPL_STUDY_RUBRIC", IMPL_STUDY_RUBRIC),
        ("TOOLS_RUBRIC", TOOLS_RUBRIC),
    ]:
        assert "ABSTRACTION_SELECTION_RUBRIC" in rubric, f"{name} missing cross-reference"


def test_compression_pressure_rubric_content() -> None:
    """COMPRESSION_PRESSURE_RUBRIC prefers one strong proposal over redundant overlap."""
    from src.ingest_review.providers.openai_provider import COMPRESSION_PRESSURE_RUBRIC

    assert "substantially overlapping" in COMPRESSION_PRESSURE_RUBRIC
    assert "one stronger proposal" in COMPRESSION_PRESSURE_RUBRIC
    assert "glossary/topic duplication" in COMPRESSION_PRESSURE_RUBRIC
    assert "repeated operational explanations" in COMPRESSION_PRESSURE_RUBRIC


def test_system_prompt_references_compression_pressure() -> None:
    """SYSTEM_PROMPT applies compression pressure when filling entity arrays."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "COMPRESSION_PRESSURE_RUBRIC" in SYSTEM_PROMPT


def test_compression_pressure_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes compression rubric before glossary rubric."""
    from src.ingest_review.providers.openai_provider import (
        COMPRESSION_PRESSURE_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-compression"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="32",
    )
    assert "## COMPRESSION PRESSURE" in prompt
    assert COMPRESSION_PRESSURE_RUBRIC.split("\n")[0] in prompt
    comp_idx = prompt.index("## COMPRESSION PRESSURE")
    gloss_idx = prompt.index("## GLOSSARY_RUBRIC")
    assert comp_idx < gloss_idx


def test_abstraction_rubric_references_compression_pressure() -> None:
    """ABSTRACTION_SELECTION_RUBRIC chains to compression pressure after layer selection."""
    from src.ingest_review.providers.openai_provider import ABSTRACTION_SELECTION_RUBRIC

    assert "COMPRESSION_PRESSURE_RUBRIC" in ABSTRACTION_SELECTION_RUBRIC


def test_minimum_novelty_threshold_rubric_content() -> None:
    """MINIMUM_NOVELTY_THRESHOLD_RUBRIC requires source-specific novelty beyond common knowledge."""
    from src.ingest_review.providers.openai_provider import MINIMUM_NOVELTY_THRESHOLD_RUBRIC

    assert "broadly familiar" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC
    assert "operational framing" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC
    assert "architecture pattern" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC
    assert "deployment implication" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC
    assert "governance implication" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC
    assert "systems-level interpretation" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC
    assert "not merely" in MINIMUM_NOVELTY_THRESHOLD_RUBRIC.lower()


def test_system_prompt_references_minimum_novelty_threshold() -> None:
    """SYSTEM_PROMPT applies minimum novelty threshold to proposals."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "MINIMUM_NOVELTY_THRESHOLD_RUBRIC" in SYSTEM_PROMPT


def test_minimum_novelty_threshold_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes novelty threshold rubric before entity rubrics."""
    from src.ingest_review.providers.openai_provider import (
        MINIMUM_NOVELTY_THRESHOLD_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-novelty"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="33",
    )
    assert "## MINIMUM NOVELTY" in prompt
    assert MINIMUM_NOVELTY_THRESHOLD_RUBRIC.split("\n")[0] in prompt
    novelty_idx = prompt.index("## MINIMUM NOVELTY")
    gloss_idx = prompt.index("## GLOSSARY_RUBRIC")
    assert novelty_idx < gloss_idx


def test_abstraction_rubric_references_minimum_novelty_threshold() -> None:
    """ABSTRACTION_SELECTION_RUBRIC chains to minimum novelty threshold after layer selection."""
    from src.ingest_review.providers.openai_provider import ABSTRACTION_SELECTION_RUBRIC

    assert "MINIMUM_NOVELTY_THRESHOLD_RUBRIC" in ABSTRACTION_SELECTION_RUBRIC


def test_models_rubric_uses_compressed_prose_fields() -> None:
    """MODELS_RUBRIC uses operational_profile and deployment_implications only."""
    from src.ingest_review.providers.openai_provider import MODELS_RUBRIC

    assert "operational_profile" in MODELS_RUBRIC
    assert "deployment_implications" in MODELS_RUBRIC
    assert "- operational_summary:" not in MODELS_RUBRIC
    assert "- strengths:" not in MODELS_RUBRIC
    assert "- workflow_implications:" not in MODELS_RUBRIC
    assert "non-overlapping" in MODELS_RUBRIC.lower()


def test_page_matching_rubric_content() -> None:
    """PAGE_MATCHING_RUBRIC defines strong vs weak overlap and named negatives."""
    from src.ingest_review.providers.openai_provider import PAGE_MATCHING_RUBRIC

    assert "Strong page match" in PAGE_MATCHING_RUBRIC
    assert "Weak related concept" in PAGE_MATCHING_RUBRIC
    assert "Privacy Controls for AI Products" in PAGE_MATCHING_RUBRIC
    assert "passkeys" in PAGE_MATCHING_RUBRIC.lower()
    assert "related_topics" in PAGE_MATCHING_RUBRIC


def test_title_canonicalization_references_page_matching() -> None:
    """TITLE_CANONICALIZATION_RUBRIC defers reuse to PAGE_MATCHING_RUBRIC."""
    from src.ingest_review.providers.openai_provider import TITLE_CANONICALIZATION_RUBRIC

    assert "PAGE_MATCHING_RUBRIC" in TITLE_CANONICALIZATION_RUBRIC
    assert "strong page match" in TITLE_CANONICALIZATION_RUBRIC.lower()
    assert "clearly belongs" not in TITLE_CANONICALIZATION_RUBRIC.lower()


def test_topics_rubric_separates_slug_reuse_from_related_topics() -> None:
    """TOPICS_RUBRIC must not use related_topics to choose topic_slug."""
    from src.ingest_review.providers.openai_provider import TOPICS_RUBRIC

    assert "PAGE_MATCHING_RUBRIC" in TOPICS_RUBRIC
    assert "Do **NOT** use ``related_topics`` to" in TOPICS_RUBRIC
    assert "weak" in TOPICS_RUBRIC.lower()


def test_page_matching_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes PAGE_MATCHING_RUBRIC before entity rubrics."""
    from src.ingest_review.providers.openai_provider import (
        PAGE_MATCHING_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-page-match"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="35",
    )
    assert "## PAGE_MATCHING_RUBRIC" in prompt
    assert PAGE_MATCHING_RUBRIC.split("\n")[0] in prompt
    assert "PAGE MATCHING" in prompt
    page_idx = prompt.index("## PAGE_MATCHING_RUBRIC")
    gloss_idx = prompt.index("## GLOSSARY_RUBRIC")
    assert page_idx < gloss_idx


def test_system_prompt_references_page_matching() -> None:
    """SYSTEM_PROMPT applies page matching before canonical reuse."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "PAGE_MATCHING_RUBRIC" in SYSTEM_PROMPT


def test_system_prompt_references_title_generation() -> None:
    """SYSTEM_PROMPT distinguishes topic vs trend title rules."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "TITLE_GENERATION_RUBRIC" in SYSTEM_PROMPT
    assert "Topic vs Trend" in SYSTEM_PROMPT


def test_title_generation_rubric_distinguishes_topics_and_trends() -> None:
    from src.ingest_review.providers.openai_provider import TITLE_GENERATION_RUBRIC

    assert "Core distinction: Topic vs Trend" in TITLE_GENERATION_RUBRIC
    assert "Agent Runtime Architecture" in TITLE_GENERATION_RUBRIC
    assert "Shifts Toward Behavioral Auditing" in TITLE_GENERATION_RUBRIC
    assert "Efficiency as Capability" in TITLE_GENERATION_RUBRIC
    assert "3–5" in TITLE_GENERATION_RUBRIC
    assert "evaluation checklist" in TITLE_GENERATION_RUBRIC.lower()


def test_topics_and_trends_rubrics_reference_title_generation() -> None:
    from src.ingest_review.providers.openai_provider import TOPICS_RUBRIC, TRENDS_RUBRIC

    assert "TITLE_GENERATION_RUBRIC" in TOPICS_RUBRIC
    assert "conceptual-domain" in TOPICS_RUBRIC
    assert "no** directional" in TOPICS_RUBRIC.lower()
    assert "TITLE_GENERATION_RUBRIC" in TRENDS_RUBRIC
    assert "industry-change" in TRENDS_RUBRIC
    assert "not** a topic-style noun stack" in TRENDS_RUBRIC


def test_title_generation_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes TITLE_GENERATION_RUBRIC before entity rubrics."""
    from src.ingest_review.providers.openai_provider import (
        TITLE_GENERATION_RUBRIC,
        _build_user_prompt,
    )

    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "doc-title-gen"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    prompt = _build_user_prompt(
        doc,
        wiki,
        tool_types=[],
        howto_tags=[],
        prompt_version="36",
    )
    assert "## TITLE_GENERATION_RUBRIC" in prompt
    assert TITLE_GENERATION_RUBRIC.split("\n")[0] in prompt
    assert "Topic vs Trend" in prompt
    title_idx = prompt.index("## TITLE_GENERATION_RUBRIC")
    topics_idx = prompt.index("## TOPICS_RUBRIC")
    assert title_idx < topics_idx


def test_prompt_version_is_39() -> None:
    """Prompt version bumped for staged classification pipeline."""
    from src.ingest_review.schema import PROMPT_VERSION

    assert PROMPT_VERSION == "39"


def test_title_canonicalization_rubric_replaces_suggested_action() -> None:
    """Classification uses canonical titles, not append/create routing."""
    from src.ingest_review.providers.openai_provider import (
        HOWTOS_RUBRIC,
        SYSTEM_PROMPT,
        TITLE_CANONICALIZATION_RUBRIC,
        TOPICS_RUBRIC,
        TRENDS_RUBRIC,
    )

    assert "Canonical titles" in TITLE_CANONICALIZATION_RUBRIC
    assert "append_to_existing" not in TITLE_CANONICALIZATION_RUBRIC
    assert "suggested_action" not in TOPICS_RUBRIC
    assert "match_candidates" not in HOWTOS_RUBRIC
    assert "SUGGESTED_ACTION_RUBRIC" not in SYSTEM_PROMPT
    assert "Default to append_to_existing" not in TRENDS_RUBRIC


def test_classification_schema_omits_suggested_action() -> None:
    """LLM classification schema hint excludes deferred routing fields."""
    from src.ingest_review.schema import llm_output_json_schema_for_classification

    schema = llm_output_json_schema_for_classification()
    blob = json.dumps(schema)
    assert "suggested_action" not in blob
    assert "match_candidates" not in blob


def test_tag_ontology_rubric_uses_proposed_tags() -> None:
    """TAG_ONTOLOGY_RUBRIC describes multi-tag proposed_tags, not primary/secondary cap."""
    from src.ingest_review.providers.openai_provider import TAG_ONTOLOGY_RUBRIC

    assert "proposed_tags" in TAG_ONTOLOGY_RUBRIC
    assert "suggested_new_tags" in TAG_ONTOLOGY_RUBRIC
    assert "Maximum two allowlist tags" not in TAG_ONTOLOGY_RUBRIC


def test_trends_rubric_uses_slug_and_title() -> None:
    from src.ingest_review.providers.openai_provider import TRENDS_RUBRIC

    assert "trend_slug" in TRENDS_RUBRIC
    assert "trend_title" in TRENDS_RUBRIC
    assert "trend_name" not in TRENDS_RUBRIC


def test_tools_rubric_requires_explanatory_strengths_not_keywords() -> None:
    """TOOLS_RUBRIC forbids comma-separated keyword dumps in strengths."""
    from src.ingest_review.providers.openai_provider import TOOLS_RUBRIC

    assert "Explanatory depth" in TOOLS_RUBRIC
    assert "keyword" in TOOLS_RUBRIC.lower() or "keyword salads" in TOOLS_RUBRIC
    assert "BAD strengths" in TOOLS_RUBRIC
    assert "GOOD strengths" in TOOLS_RUBRIC
    assert "markdown bullets" in TOOLS_RUBRIC.lower() or "bullets" in TOOLS_RUBRIC


def test_system_prompt_references_impl_study_worthiness_gate() -> None:
    """SYSTEM_PROMPT delegates implementation studies to the worthiness gate."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "IMPLEMENTATION_STUDY_WORTHINESS GATE" in SYSTEM_PROMPT
    assert "IMPL_STUDY_RUBRIC" in SYSTEM_PROMPT
