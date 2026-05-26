"""High-level classification analysis orchestration."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.artifact import build_new_artifact, default_analysis_meta
from src.ingest_review.canonical_titles import (
    align_parsed_classification_titles,
    build_canonical_index,
)
from src.ingest_review.evidence import apply_evidence_hierarchy
from src.ingest_review.extract import SourceDocument
from src.ingest_review.foundation_model_name_backfill import backfill_foundation_model_names
from src.ingest_review.glossary_related_terms_align import align_glossary_related_terms
from src.ingest_review.howto_title_normalize import normalize_howto_proposal
from src.ingest_review.impl_study_gate import filter_impl_study_proposals
from src.ingest_review.providers.base import IngestionProvider
from src.ingest_review.schema import (
    LIST_ROUNDUP_SOURCE_TYPES,
    PROMPT_VERSION,
    LlmClassificationOutput,
    TopicContribution,
    normalize_source_summary,
)
from src.ingest_review.tags import MAX_PROPOSED_TAGS, normalize_tag, normalize_tag_list
from src.ingest_review.tools_roundup_model_routing import (
    route_ai_tools_roundup_tools_to_foundation_models,
)
from src.ingest_review.topic_related_topics import sanitize_topics_related_topics
from src.ingest_review.topic_related_topics_suggest import (
    build_topic_slug_catalog_from_topics,
    suggest_related_topics,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot, build_wiki_snapshot


def _validate_proposal_tags(
    proposed_tags: list[str],
    suggested_new_tags: list[str],
    *,
    primary: str,
    secondary: str,
    suggested_new: str,
    allowlist: set[str],
) -> dict[str, object]:
    """Validate tag lists against *allowlist*; demote off-list tags to suggested_new_tags."""
    norm_allow = {normalize_tag(t) for t in allowlist}
    merged_proposed = list(proposed_tags)
    if not merged_proposed:
        for legacy in (primary, secondary):
            t = normalize_tag(legacy)
            if t and t not in merged_proposed:
                merged_proposed.append(t)
    on_list: list[str] = []
    off_list: list[str] = []
    for t in normalize_tag_list(merged_proposed, cap=0):
        if t in norm_allow:
            if t not in on_list:
                on_list.append(t)
        elif t not in off_list:
            off_list.append(t)
    on_list = normalize_tag_list(on_list, cap=MAX_PROPOSED_TAGS)

    snt = normalize_tag_list(suggested_new_tags, cap=0)
    sn_legacy = normalize_tag(suggested_new)
    if sn_legacy and sn_legacy not in snt:
        snt.insert(0, sn_legacy)
    for t in off_list:
        if t not in on_list and t not in snt:
            snt.append(t)

    return {
        "proposed_tags": on_list,
        "suggested_new_tags": snt,
        "primary_tag": on_list[0] if on_list else "",
        "secondary_tag": on_list[1] if len(on_list) > 1 else "",
        "suggested_new_tag": snt[0] if snt else "",
    }


def apply_tag_allowlists(
    parsed: LlmClassificationOutput,
    tool_types: set[str],
    howto_tags: set[str],
    glossary_tags: set[str] | None = None,
    topic_tags: set[str] | None = None,
    trend_tags: set[str] | None = None,
    model_types: set[str] | None = None,
    impl_study_tags: set[str] | None = None,
    tool_tags: set[str] | None = None,
    model_tags: set[str] | None = None,
) -> LlmClassificationOutput:
    """Validate proposal tags against allowlists; demote unknown tags to suggested_new_tags."""
    ttg = tool_tags or set()
    new_tools = [
        tp.model_copy(
            update={
                "proposed_types": [
                    normalize_tag(x) for x in tp.proposed_types if normalize_tag(x) in tool_types
                ][:MAX_PROPOSED_TAGS],
                **_validate_proposal_tags(
                    tp.proposed_tags,
                    tp.suggested_new_tags,
                    primary="",
                    secondary="",
                    suggested_new="",
                    allowlist=ttg,
                ),
            }
        )
        for tp in parsed.tools
    ]
    gt = glossary_tags or set()
    new_glossary = [
        gp.model_copy(
            update=_validate_proposal_tags(
                gp.proposed_tags,
                gp.suggested_new_tags,
                primary=gp.primary_tag,
                secondary=gp.secondary_tag,
                suggested_new=gp.suggested_new_tag,
                allowlist=gt,
            )
        )
        for gp in parsed.glossary
    ]
    tt = topic_tags or set()
    new_topics = [
        tc.model_copy(
            update=_validate_proposal_tags(
                tc.proposed_tags,
                tc.suggested_new_tags,
                primary=tc.primary_tag,
                secondary=tc.secondary_tag,
                suggested_new=tc.suggested_new_tag,
                allowlist=tt,
            )
        )
        for tc in parsed.topics
    ]
    ht = howto_tags
    new_how = [
        normalize_howto_proposal(
            hp.model_copy(
                update=_validate_proposal_tags(
                    hp.proposed_tags,
                    hp.suggested_new_tags,
                    primary=hp.primary_tag,
                    secondary=hp.secondary_tag,
                    suggested_new=hp.suggested_new_tag,
                    allowlist=ht,
                )
            )
        )
        for hp in parsed.how_to
    ]
    trt = trend_tags or set()
    new_trends = [
        tr.model_copy(
            update=_validate_proposal_tags(
                tr.proposed_tags,
                tr.suggested_new_tags,
                primary=tr.primary_tag,
                secondary=tr.secondary_tag,
                suggested_new=tr.suggested_new_tag,
                allowlist=trt,
            )
        )
        for tr in parsed.industry_trends
    ]
    mt = model_types or set()
    mtg = model_tags or set()
    new_models = [
        mp.model_copy(
            update={
                "proposed_types": [
                    normalize_tag(x) for x in mp.proposed_types if normalize_tag(x) in mt
                ][:MAX_PROPOSED_TAGS],
                **_validate_proposal_tags(
                    mp.proposed_tags,
                    mp.suggested_new_tags,
                    primary="",
                    secondary="",
                    suggested_new="",
                    allowlist=mtg,
                ),
            }
        )
        for mp in parsed.foundation_models
    ]
    new_signals = [
        sig.model_copy(
            update=_validate_proposal_tags(
                sig.proposed_tags,
                sig.suggested_new_tags,
                primary=sig.primary_tag,
                secondary=sig.secondary_tag,
                suggested_new=sig.suggested_new_tag,
                allowlist=trt,
            )
        )
        for sig in parsed.roundup_signals
    ]
    new_insights = [
        ins.model_copy(
            update=_validate_proposal_tags(
                ins.proposed_tags,
                ins.suggested_new_tags,
                primary=ins.primary_tag,
                secondary=ins.secondary_tag,
                suggested_new=ins.suggested_new_tag,
                allowlist=tt,
            )
        )
        for ins in parsed.interview_insights
    ]
    ist = impl_study_tags or set()
    new_impl = [
        ip.model_copy(
            update=_validate_proposal_tags(
                ip.proposed_tags,
                ip.suggested_new_tags,
                primary=ip.primary_tag,
                secondary=ip.secondary_tag,
                suggested_new=ip.suggested_new_tag,
                allowlist=ist,
            )
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


def apply_howto_roundup_entity_strip(parsed: LlmClassificationOutput) -> LlmClassificationOutput:
    """Force how-to-only extraction when source type is how_to_roundup."""
    if parsed.source_type_detection.detected_source_type != "how_to_roundup":
        return parsed
    return parsed.model_copy(
        update={
            "glossary": [],
            "topics": [],
            "tools": [],
            "foundation_models": [],
            "industry_trends": [],
            "roundup_signals": [],
            "implementation_studies": [],
            "interview_insights": [],
        }
    )


def enforce_list_roundup_extraction_policy(
    parsed: LlmClassificationOutput,
) -> LlmClassificationOutput:
    """Never recommend skip for list-style roundup sources (human curates in dashboard)."""
    detected = parsed.source_type_detection.detected_source_type
    if detected not in LIST_ROUNDUP_SOURCE_TYPES:
        return parsed
    emeta = parsed.extraction_meta
    if not emeta.skip_recommended:
        return parsed
    prior = (emeta.skip_reason or "").strip()
    cleared = "Cleared skip for list roundup review."
    new_reason = f"{prior} ({cleared})" if prior else cleared
    return parsed.model_copy(
        update={
            "extraction_meta": emeta.model_copy(
                update={"skip_recommended": False, "skip_reason": new_reason}
            )
        }
    )


def _backfill_empty_topic_related_topics(
    parsed: LlmClassificationOutput,
    wiki: WikiSnapshot,
    reviews_root: Path | None,
) -> LlmClassificationOutput:
    """Fill empty ``related_topics`` with heuristic suggestions (wiki + reviews + batch)."""
    if not parsed.topics:
        return parsed
    new_topics: list[TopicContribution] = []
    changed = False
    for tc in parsed.topics:
        if tc.related_topics:
            new_topics.append(tc)
            continue
        catalog = build_topic_slug_catalog_from_topics(
            wiki,
            reviews_root,
            parsed.topics,
            exclude_slug=tc.topic_slug,
        )
        suggestions = suggest_related_topics(
            tc.topic_slug,
            tc.topic_title or "",
            tc.knowledge_summary or "",
            catalog,
        )
        slugs = [s.slug for s in suggestions]
        if slugs:
            new_topics.append(tc.model_copy(update={"related_topics": slugs}))
            changed = True
        else:
            new_topics.append(tc)
    if not changed:
        return parsed
    return parsed.model_copy(update={"topics": new_topics})


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
    tool_tags: list[str] | None = None,
    model_tags: list[str] | None = None,
    source_type_override: str | None = None,
    extraction_budgets: dict[str, int] | None = None,
    model: str,
    prompt_version: str | None = None,
    reviews_root: Path | None = None,
) -> tuple[dict[str, object], LlmClassificationOutput]:
    """Run provider analysis and return ``(artifact_dict, parsed_output)``."""
    pv = prompt_version or PROMPT_VERSION
    wiki = build_wiki_snapshot(wiki_root)
    reviews_path = reviews_root
    if reviews_path is None:
        reviews_path = wiki_root.parent / "state" / "reviews"
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
        tool_tags_allowlist=tool_tags,
        model_tags_allowlist=model_tags,
        source_type_override=source_type_override,
        extraction_budgets=extraction_budgets,
        reviews_root=reviews_path,
        model=model,
        prompt_version=pv,
    )
    parsed = enforce_list_roundup_extraction_policy(parsed)
    canonical_index = build_canonical_index(wiki, reviews_path)
    parsed = align_parsed_classification_titles(parsed, canonical_index)
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
    parsed = backfill_foundation_model_names(parsed, wiki.foundation_model_names)
    parsed = apply_tag_allowlists(
        parsed,
        set(tool_types),
        set(howto_tags),
        set(glossary_tags or []),
        set(topic_tags or []),
        set(trend_tags or []),
        set(model_types or []),
        set(impl_study_tags or []),
        set(tool_tags or []),
        set(model_tags or []),
    )
    parsed = sanitize_topics_related_topics(parsed, set(topic_tags or []), wiki)
    parsed = _backfill_empty_topic_related_topics(parsed, wiki, reviews_path)
    parsed = apply_tools_roundup_entity_strip(parsed)
    parsed = apply_howto_roundup_entity_strip(parsed)
    parsed = parsed.model_copy(
        update={
            "implementation_studies": filter_impl_study_proposals(parsed.implementation_studies),
        }
    )
    parsed = apply_evidence_hierarchy(parsed)
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
