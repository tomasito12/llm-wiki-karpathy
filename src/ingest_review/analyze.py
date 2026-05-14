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


def _split_tags(
    tags: list[str],
    existing_new: list[str],
    allowlist: set[str],
) -> tuple[list[str], list[str]]:
    """Split *tags* into (allowed, new). Items not in *allowlist* move to new."""
    allowed: list[str] = []
    new: list[str] = list(existing_new)
    for t in tags:
        if t in allowlist:
            allowed.append(t)
        elif t and t not in new:
            new.append(t)
    return allowed, new


def apply_tag_allowlists(
    parsed: LlmClassificationOutput,
    tool_types: set[str],
    howto_tags: set[str],
    glossary_tags: set[str] | None = None,
    topic_tags: set[str] | None = None,
    trend_tags: set[str] | None = None,
    model_types: set[str] | None = None,
) -> LlmClassificationOutput:
    """Split LLM-proposed tags into allowlist-approved and proposed-new buckets."""
    new_tools = [
        tp.model_copy(update={"proposed_types": [x for x in tp.proposed_types if x in tool_types]})
        for tp in parsed.tools
    ]
    gt = glossary_tags or set()
    new_glossary = []
    for gp in parsed.glossary:
        kept, new = _split_tags(gp.proposed_tags, gp.proposed_new_tags, gt)
        new_glossary.append(gp.model_copy(update={"proposed_tags": kept, "proposed_new_tags": new}))
    tt = topic_tags or set()
    new_topics = []
    for tc in parsed.topics:
        kept, new = _split_tags(tc.proposed_tags, tc.proposed_new_tags, tt)
        new_topics.append(tc.model_copy(update={"proposed_tags": kept, "proposed_new_tags": new}))
    ht = howto_tags
    new_how = []
    for hp in parsed.how_to:
        kept, new = _split_tags(hp.proposed_tags, hp.proposed_new_tags, ht)
        new_how.append(hp.model_copy(update={"proposed_tags": kept, "proposed_new_tags": new}))
    trt = trend_tags or set()
    new_trends = []
    for tr in parsed.industry_trends:
        kept, new = _split_tags(tr.proposed_tags, tr.proposed_new_tags, trt)
        new_trends.append(tr.model_copy(update={"proposed_tags": kept, "proposed_new_tags": new}))
    mt = model_types or set()
    new_models = [
        mp.model_copy(update={"proposed_types": [x for x in mp.proposed_types if x in mt]})
        for mp in parsed.foundation_models
    ]
    new_signals = []
    for sig in parsed.roundup_signals:
        kept, new = _split_tags(sig.proposed_tags, sig.proposed_new_tags, trt)
        new_signals.append(sig.model_copy(update={"proposed_tags": kept, "proposed_new_tags": new}))
    new_insights = []
    for ins in parsed.interview_insights:
        kept, new = _split_tags(ins.proposed_tags, ins.proposed_new_tags, tt)
        new_insights.append(
            ins.model_copy(update={"proposed_tags": kept, "proposed_new_tags": new})
        )
    return parsed.model_copy(
        update={
            "tools": new_tools,
            "how_to": new_how,
            "glossary": new_glossary,
            "topics": new_topics,
            "industry_trends": new_trends,
            "foundation_models": new_models,
            "roundup_signals": new_signals,
            "interview_insights": new_insights,
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
