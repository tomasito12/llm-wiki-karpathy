"""Tests for staged classification pipeline and prompt caching layout."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.ingest_review.classification_pipeline import (
    apply_source_type_override,
    classification_pipeline_mode,
    run_staged_classification,
    should_skip_later_stages,
)
from src.ingest_review.classification_prompts import (
    build_cached_classification_prefix,
    build_entities_prompt_suffix,
    build_prompt_cache_key,
    build_triage_prompt_suffix,
)
from src.ingest_review.extract import load_readwise_pair
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.schema import (
    EntitiesStageOutput,
    ExtractionMeta,
    LlmClassificationOutput,
    SourceTypeDetection,
    SummaryStageOutput,
    TriageStageOutput,
    empty_entities_stage_output,
    merge_stage_outputs,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_classification_pipeline_mode_default_staged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default pipeline mode is staged when env unset."""
    monkeypatch.delenv("INGEST_CLASSIFICATION_PIPELINE", raising=False)
    assert classification_pipeline_mode() == "staged"


def test_classification_pipeline_mode_monolithic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INGEST_CLASSIFICATION_PIPELINE", "monolithic")
    assert classification_pipeline_mode() == "monolithic"


def test_build_cached_classification_prefix_stable(tmp_path: Path) -> None:
    """Prefix is byte-identical for the same document."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "cache-prefix"
    (raw / f"{stem}.html").write_text("<p>article</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    a = build_cached_classification_prefix(doc, prompt_version="39")
    b = build_cached_classification_prefix(doc, prompt_version="39")
    assert a == b
    assert "## ARTICLE_PLAIN_TEXT" in a
    assert a.index("## Metadata") < a.index("## ARTICLE_PLAIN_TEXT")


def test_build_prompt_cache_key_includes_version_and_source() -> None:
    key = build_prompt_cache_key(prompt_version="39", source_id="src-1")
    assert key == "ingest-classify:39:src-1"


def test_merge_stage_outputs_produces_full_classification() -> None:
    triage = TriageStageOutput(
        extraction_meta=ExtractionMeta(skip_recommended=False),
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
    )
    summary = SummaryStageOutput()
    entities = EntitiesStageOutput()
    merged = merge_stage_outputs(triage, summary, entities)
    assert isinstance(merged, LlmClassificationOutput)
    assert merged.source_type_detection.detected_source_type == "standard_article"


def test_should_skip_later_stages_when_skip_recommended() -> None:
    triage = TriageStageOutput(
        extraction_meta=ExtractionMeta(skip_recommended=True),
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
    )
    assert should_skip_later_stages(triage) is True


def test_should_not_skip_list_roundup_when_skip_recommended() -> None:
    triage = TriageStageOutput(
        extraction_meta=ExtractionMeta(skip_recommended=True),
        source_type_detection=SourceTypeDetection(detected_source_type="ai_tools_roundup"),
    )
    assert should_skip_later_stages(triage) is False


def test_apply_source_type_override() -> None:
    triage = TriageStageOutput()
    updated = apply_source_type_override(triage, "how_to_roundup")
    assert updated.source_type_detection.detected_source_type == "how_to_roundup"
    assert updated.source_type_detection.confidence == 1.0


def test_entities_prompt_suffix_excludes_topics_for_tools_roundup(tmp_path: Path) -> None:
    """Stage 3 tools route must not include TOPICS_RUBRIC."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "route-tools"
    (raw / f"{stem}.html").write_text("<p>x</p>", encoding="utf-8")
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
    from src.ingest_review.classification_prompts import ClassificationAllowlists

    triage = TriageStageOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="ai_tools_roundup"),
    )
    suffix = build_entities_prompt_suffix(
        "ai_tools_roundup",
        triage,
        "{}",
        wiki=wiki,
        allowlists=ClassificationAllowlists(
            tool_types=["mcp-server"],
            howto_tags=[],
            impl_study_tags=[],
            glossary_tags=[],
            topic_tags=[],
            trend_tags=[],
            model_types=[],
            tool_tags=[],
            model_tags=[],
        ),
        extraction_budgets=None,
        reviews_root=None,
        prompt_version="39",
    )
    assert "TOOLS_RUBRIC" in suffix
    assert "## TOPICS_RUBRIC" not in suffix
    _ = doc


def test_triage_suffix_has_no_entity_rubrics() -> None:
    suffix = build_triage_prompt_suffix(
        extraction_budgets=None,
        source_type_override=None,
        prompt_version="39",
    )
    assert "SOURCE_TYPE_DETECTION_RUBRIC" in suffix
    assert "GLOSSARY_RUBRIC" not in suffix
    assert "ROUNDUP_SIGNALS_RUBRIC" not in suffix


def _wiki() -> WikiSnapshot:
    return WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )


def test_staged_classification_three_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Staged pipeline issues triage, summary, and entities completions."""
    monkeypatch.setenv("INGEST_CLASSIFICATION_PIPELINE", "staged")
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "staged-3"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")

    triage = TriageStageOutput(
        extraction_meta=ExtractionMeta(skip_recommended=False),
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
    )
    summary = SummaryStageOutput()
    entities = empty_entities_stage_output()
    responses = [
        json.dumps(triage.model_dump()),
        json.dumps(summary.model_dump()),
        json.dumps(entities.model_dump()),
    ]

    class _Msg:
        def __init__(self, content: str) -> None:
            self.content = content

    class _Choice:
        def __init__(self, content: str) -> None:
            self.message = _Msg(content)

    class _Usage:
        def model_dump(self) -> dict:
            return {
                "prompt_tokens": 1000,
                "completion_tokens": 100,
                "total_tokens": 1100,
                "prompt_tokens_details": {"cached_tokens": 500},
            }

    class _Completion:
        def __init__(self, content: str, cid: str) -> None:
            self.id = cid
            self.choices = [_Choice(content)]
            self.usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.side_effect = [
        _Completion(responses[0], "cmpl-1"),
        _Completion(responses[1], "cmpl-2"),
        _Completion(responses[2], "cmpl-3"),
    ]

    prov = OpenAIIngestionProvider(client=fake_client)
    out, meta = run_staged_classification(
        prov,
        document=doc,
        wiki=_wiki(),
        tool_types_allowlist=[],
        howto_tags_allowlist=[],
        model="gpt-test",
        prompt_version="39",
        max_retries=1,
    )
    assert isinstance(out, LlmClassificationOutput)
    assert fake_client.chat.completions.create.call_count == 3
    pipeline = meta.get("classification_pipeline")
    assert pipeline is not None
    assert pipeline["mode"] == "staged"
    assert len(pipeline["stages"]) == 3
    for call in fake_client.chat.completions.create.call_args_list:
        kwargs = call.kwargs
        if "prompt_cache_key" in kwargs:
            assert kwargs["prompt_cache_key"] == build_prompt_cache_key(
                prompt_version="39",
                source_id=doc.source_id,
            )


def test_staged_skip_short_circuit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip gate skips summary and entities stages."""
    monkeypatch.setenv("INGEST_CLASSIFICATION_PIPELINE", "staged")
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "staged-skip"
    (raw / f"{stem}.html").write_text("<p>body</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: T\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    triage = TriageStageOutput(
        extraction_meta=ExtractionMeta(skip_recommended=True),
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
    )

    class _Msg:
        content = json.dumps(triage.model_dump())

    class _Choice:
        message = _Msg()

    class _Usage:
        def model_dump(self) -> dict:
            return {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}

    class _Completion:
        id = "cmpl-skip"
        choices = [_Choice()]
        usage = _Usage()

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _Completion()
    prov = OpenAIIngestionProvider(client=fake_client)
    out, meta = run_staged_classification(
        prov,
        document=doc,
        wiki=_wiki(),
        tool_types_allowlist=[],
        howto_tags_allowlist=[],
        model="gpt-test",
        prompt_version="39",
        max_retries=1,
    )
    assert fake_client.chat.completions.create.call_count == 1
    assert meta["classification_pipeline"]["skipped_stages"] == ["summary", "entities"]
    assert out.glossary == []
