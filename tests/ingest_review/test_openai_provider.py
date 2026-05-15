"""Tests for OpenAI ingestion provider (mocked HTTP client)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from src.ingest_review.extract import load_readwise_pair
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.schema import LlmClassificationOutput
from src.ingest_review.wiki_snapshot import WikiSnapshot


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
    assert "ROUNDUP_SIGNALS_RUBRIC" in user_msg
    assert "INTERVIEW_INSIGHTS_RUBRIC" in user_msg
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
        assert "suggested_new_tag" in rubric, f"{name} missing suggested_new_tag"


def test_system_prompt_mentions_tag_structure() -> None:
    """SYSTEM_PROMPT delegates tag rules to TAG_ONTOLOGY_RUBRIC."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "TAG_ONTOLOGY_RUBRIC" in SYSTEM_PROMPT
    assert "PRIMARY_SECONDARY_SEMANTICS" in SYSTEM_PROMPT
    assert "proposed_types" in SYSTEM_PROMPT


def test_system_prompt_includes_extraction_meta() -> None:
    """SYSTEM_PROMPT references extraction_meta and value_level."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "extraction_meta" in SYSTEM_PROMPT
    assert "value_level" in SYSTEM_PROMPT
    assert "evidence_type" in SYSTEM_PROMPT
    assert "vendor_claim" in SYSTEM_PROMPT
    assert "roundup_signals" in SYSTEM_PROMPT
    assert "interview_insights" in SYSTEM_PROMPT


def test_rubrics_mention_evidence_type() -> None:
    """Entity rubrics instruct the LLM to set evidence_type."""
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


def test_evidence_type_rubric_in_user_prompt(tmp_path: Path) -> None:
    """User prompt includes EVIDENCE_TYPE_RUBRIC block."""
    from src.ingest_review.providers.openai_provider import EVIDENCE_TYPE_RUBRIC, _build_user_prompt

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
    assert EVIDENCE_TYPE_RUBRIC.split("\n")[0] in prompt
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


def test_glossary_rubric_includes_extraction_boundaries() -> None:
    """GLOSSARY_RUBRIC routes generic business terms away and defers patterns to topics."""
    from src.ingest_review.providers.openai_provider import GLOSSARY_RUBRIC

    assert "GLOSSARY EXTRACTION BOUNDARIES" in GLOSSARY_RUBRIC
    assert "flywheel" in GLOSSARY_RUBRIC
    assert "agent-first product design" in GLOSSARY_RUBRIC
    assert "prefer a topic contribution over a glossary term" in GLOSSARY_RUBRIC


def test_tag_ontology_rubric_in_user_prompt(tmp_path: Path) -> None:
    """Built user prompt includes tag ontology, sparsity, and primary/secondary semantics."""
    from src.ingest_review.providers.openai_provider import (
        PRIMARY_SECONDARY_SEMANTICS,
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
    assert PRIMARY_SECONDARY_SEMANTICS.split("\n")[0] in prompt
    assert "prefer reusing an existing approved tag" in prompt.lower()
    assert "gpt-5-4-launch" in prompt
    assert "Tag sparsity" in prompt
    assert "TOPIC_TAGS_ALLOWLIST" in TOPICS_RUBRIC
    assert "at most 2" in TOOLS_RUBRIC


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


def test_topics_and_howtos_rubric_route_away_from_impl_studies() -> None:
    """Topics and how-tos rubrics say not to use implementation_studies."""
    from src.ingest_review.providers.openai_provider import HOWTOS_RUBRIC, TOPICS_RUBRIC

    assert "NOT in implementation_studies" in TOPICS_RUBRIC
    assert "NOT in implementation_studies" in HOWTOS_RUBRIC


def test_system_prompt_references_impl_study_worthiness_gate() -> None:
    """SYSTEM_PROMPT delegates implementation studies to the worthiness gate."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "IMPLEMENTATION_STUDY_WORTHINESS GATE" in SYSTEM_PROMPT
    assert "IMPL_STUDY_RUBRIC" in SYSTEM_PROMPT
