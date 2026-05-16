"""High-level classification analysis orchestration."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.artifact import build_new_artifact, default_analysis_meta
from src.ingest_review.extract import SourceDocument
from src.ingest_review.glossary_related_terms_align import align_glossary_related_terms
from src.ingest_review.howto_title_normalize import normalize_howto_proposal
from src.ingest_review.impl_study_gate import filter_impl_study_proposals
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import (
    PROMPT_VERSION,
    LlmClassificationOutput,
    normalize_source_summary,
)
from src.ingest_review.tools_roundup_model_routing import (
    route_ai_tools_roundup_tools_to_foundation_models,
)
from src.ingest_review.topic_related_topics import sanitize_topics_related_topics
from src.ingest_review.wiki_snapshot import build_wiki_snapshot


def _validate_tag_pair(
    primary: str,
    secondary: str,
    suggested_new: str,
    allowlist: set[str],
) -> dict[str, str]:
    """Validate primary/secondary against *allowlist*; demote to suggested_new if invalid."""
    from src.ingest_review.tags import normalize_tag

    norm_allow = {normalize_tag(t) for t in allowlist}
    p_raw = normalize_tag(primary)
    s_raw = normalize_tag(secondary)
    new = normalize_tag(suggested_new)
    p = p_raw if p_raw in norm_allow else ""
    if p_raw and p_raw not in norm_allow and not new:
        new = p_raw
    s = s_raw if s_raw in norm_allow else ""
    if s_raw and s_raw not in norm_allow and not new:
        new = s_raw
    return {"primary_tag": p, "secondary_tag": s, "suggested_new_tag": new}


def apply_tag_allowlists(
    parsed: LlmClassificationOutput,
    tool_types: set[str],
    howto_tags: set[str],
    glossary_tags: set[str] | None = None,
    topic_tags: set[str] | None = None,
    trend_tags: set[str] | None = None,
    model_types: set[str] | None = None,
    impl_study_tags: set[str] | None = None,
) -> LlmClassificationOutput:
    """Validate proposal tags against allowlists; demote unknown tags to suggested_new_tag."""
    new_tools = [
        tp.model_copy(update={"proposed_types": [x for x in tp.proposed_types if x in tool_types]})
        for tp in parsed.tools
    ]
    gt = glossary_tags or set()
    new_glossary = [
        gp.model_copy(
            update=_validate_tag_pair(gp.primary_tag, gp.secondary_tag, gp.suggested_new_tag, gt)
        )
        for gp in parsed.glossary
    ]
    tt = topic_tags or set()
    new_topics = [
        tc.model_copy(
            update=_validate_tag_pair(tc.primary_tag, tc.secondary_tag, tc.suggested_new_tag, tt)
        )
        for tc in parsed.topics
    ]
    ht = howto_tags
    new_how = [
        normalize_howto_proposal(
            hp.model_copy(
                update=_validate_tag_pair(
                    hp.primary_tag, hp.secondary_tag, hp.suggested_new_tag, ht
                )
            )
        )
        for hp in parsed.how_to
    ]
    trt = trend_tags or set()
    new_trends = [
        tr.model_copy(
            update=_validate_tag_pair(tr.primary_tag, tr.secondary_tag, tr.suggested_new_tag, trt)
        )
        for tr in parsed.industry_trends
    ]
    mt = model_types or set()
    new_models = [
        mp.model_copy(update={"proposed_types": [x for x in mp.proposed_types if x in mt]})
        for mp in parsed.foundation_models
    ]
    new_signals = [
        sig.model_copy(
            update=_validate_tag_pair(
                sig.primary_tag, sig.secondary_tag, sig.suggested_new_tag, trt
            )
        )
        for sig in parsed.roundup_signals
    ]
    new_insights = [
        ins.model_copy(
            update=_validate_tag_pair(ins.primary_tag, ins.secondary_tag, ins.suggested_new_tag, tt)
        )
        for ins in parsed.interview_insights
    ]
    ist = impl_study_tags or set()
    new_impl = [
        ip.model_copy(
            update=_validate_tag_pair(ip.primary_tag, ip.secondary_tag, ip.suggested_new_tag, ist)
        )
        for ip in parsed.implementation_studies
    ]
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
            "implementation_studies": new_impl,
        }
    )


def apply_tools_roundup_entity_strip(parsed: LlmClassificationOutput) -> LlmClassificationOutput:
    """Force tools-only extraction when source type is ai_tools_roundup."""
    if parsed.source_type_detection.detected_source_type != "ai_tools_roundup":
        return parsed
    return parsed.model_copy(
        update={
            "glossary": [],
            "topics": [],
            "how_to": [],
            "industry_trends": [],
            "roundup_signals": [],
            "implementation_studies": [],
            "interview_insights": [],
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
    extraction_budgets: dict[str, int] | None = None,
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
        extraction_budgets=extraction_budgets,
        model=model,
        prompt_version=pv,
    )
    parsed = parsed.model_copy(
        update={"source_summary": normalize_source_summary(parsed.source_summary)}
    )
    parsed = align_glossary_related_terms(parsed, wiki)
    parsed = route_ai_tools_roundup_tools_to_foundation_models(
        parsed,
        wiki,
        tool_types,
        list(model_types or []),
    )
    parsed = apply_tag_allowlists(
        parsed,
        set(tool_types),
        set(howto_tags),
        set(glossary_tags or []),
        set(topic_tags or []),
        set(trend_tags or []),
        set(model_types or []),
        set(impl_study_tags or []),
    )
    parsed = sanitize_topics_related_topics(parsed, set(topic_tags or []), wiki)
    parsed = apply_tools_roundup_entity_strip(parsed)
    parsed = parsed.model_copy(
        update={
            "implementation_studies": filter_impl_study_proposals(parsed.implementation_studies),
        }
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
