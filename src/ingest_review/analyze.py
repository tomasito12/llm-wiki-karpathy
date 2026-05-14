"""High-level classification analysis orchestration."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.artifact import build_new_artifact, default_analysis_meta
from src.ingest_review.extract import SourceDocument
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import (
    PROMPT_VERSION,
    LlmClassificationOutput,
    normalize_source_summary,
)
from src.ingest_review.wiki_snapshot import build_wiki_snapshot


def apply_tag_allowlists(
    parsed: LlmClassificationOutput,
    tool_types: set[str],
    howto_tags: set[str],
    glossary_tags: set[str] | None = None,
    topic_tags: set[str] | None = None,
    trend_tags: set[str] | None = None,
    model_types: set[str] | None = None,
) -> LlmClassificationOutput:
    """Drop LLM-proposed tags/types that are not on the allowlists."""
    new_tools = [
        tp.model_copy(update={"proposed_types": [x for x in tp.proposed_types if x in tool_types]})
        for tp in parsed.tools
    ]
    new_how = [
        hp.model_copy(update={"proposed_tags": [x for x in hp.proposed_tags if x in howto_tags]})
        for hp in parsed.how_to
    ]
    gt = glossary_tags or set()
    new_glossary = [
        gp.model_copy(update={"proposed_tags": [x for x in gp.proposed_tags if x in gt]})
        for gp in parsed.glossary
    ]
    tt = topic_tags or set()
    new_topics = [
        tc.model_copy(update={"proposed_tags": [x for x in tc.proposed_tags if x in tt]})
        for tc in parsed.topics
    ]
    trt = trend_tags or set()
    new_trends = [
        tr.model_copy(update={"proposed_tags": [x for x in tr.proposed_tags if x in trt]})
        for tr in parsed.industry_trends
    ]
    mt = model_types or set()
    new_models = [
        mp.model_copy(update={"proposed_types": [x for x in mp.proposed_types if x in mt]})
        for mp in parsed.foundation_models
    ]
    return parsed.model_copy(
        update={
            "tools": new_tools,
            "how_to": new_how,
            "glossary": new_glossary,
            "topics": new_topics,
            "industry_trends": new_trends,
            "foundation_models": new_models,
        }
    )


def run_classification(
    provider: IngestionProvider,
    document: SourceDocument,
    *,
    wiki_root: Path,
    tool_types: list[str],
    howto_tags: list[str],
    impl_study_tags: list[str] | None = None,
    glossary_tags: list[str] | None = None,
    topic_tags: list[str] | None = None,
    trend_tags: list[str] | None = None,
    model_types: list[str] | None = None,
    source_type_override: str | None = None,
    model: str,
    prompt_version: str | None = None,
) -> tuple[dict[str, object], LlmClassificationOutput]:
    """Run provider analysis and return ``(artifact_dict, parsed_output)``."""
    pv = prompt_version or PROMPT_VERSION
    wiki = build_wiki_snapshot(wiki_root)
    parsed, meta = provider.analyze_classification(
        document=document,
        wiki=wiki,
        tool_types_allowlist=tool_types,
        howto_tags_allowlist=howto_tags,
        impl_study_tags_allowlist=impl_study_tags,
        glossary_tags_allowlist=glossary_tags,
        topic_tags_allowlist=topic_tags,
        trend_tags_allowlist=trend_tags,
        model_types_allowlist=model_types,
        source_type_override=source_type_override,
        model=model,
        prompt_version=pv,
    )
    parsed = parsed.model_copy(
        update={"source_summary": normalize_source_summary(parsed.source_summary)}
    )
    parsed = apply_tag_allowlists(
        parsed,
        set(tool_types),
        set(howto_tags),
        set(glossary_tags or []),
        set(topic_tags or []),
        set(trend_tags or []),
        set(model_types or []),
    )
    analysis_meta = default_analysis_meta(
        provider=provider.provider_name,
        model=model,
        prompt_version=pv,
    )
    analysis_meta["request_id"] = meta.get("request_id")
    analysis_meta["token_usage"] = meta.get("token_usage")
    artifact = build_new_artifact(document, parsed, analysis_meta=analysis_meta)
    return artifact, parsed


def validate_llm_dict(data: dict[str, object]) -> LlmClassificationOutput:
    """Validate a dict against :class:`LlmClassificationOutput`; raise on failure."""
    return LlmClassificationOutput.model_validate(data)
