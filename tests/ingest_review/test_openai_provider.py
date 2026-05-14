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


def test_rubrics_mention_proposed_new_tags() -> None:
    """All entity-type rubrics include proposed_new_tags field instructions."""
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
        assert "proposed_new_tags" in rubric, f"{name} missing proposed_new_tags"


def test_system_prompt_mentions_proposed_new_tags() -> None:
    """SYSTEM_PROMPT references proposed_new_tags for user awareness."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "proposed_new_tags" in SYSTEM_PROMPT


def test_system_prompt_includes_glossary_in_tag_instruction() -> None:
    """SYSTEM_PROMPT tag instruction must list glossary alongside other entity types."""
    from src.ingest_review.providers.openai_provider import SYSTEM_PROMPT

    assert "glossary" in SYSTEM_PROMPT.lower()
    assert "roundup_signals" in SYSTEM_PROMPT
    assert "interview_insights" in SYSTEM_PROMPT


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
