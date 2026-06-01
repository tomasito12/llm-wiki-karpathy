"""Staged classification prompt builders (prefix caching + route packs)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.ingest_review.canonical_titles import build_canonical_title_prompt_blocks
from src.ingest_review.extract import SourceDocument
from src.ingest_review.providers import openai_provider as op
from src.ingest_review.schema import (
    ENTITY_FIELDS_BY_SOURCE_TYPE,
    PROMPT_VERSION,
    SourceType,
    TriageStageOutput,
    llm_output_json_schema_for_entities,
    llm_output_json_schema_for_summary,
    llm_output_json_schema_for_triage,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot

_SCHEMA_HINT_MAX = 24_000


@dataclass(frozen=True)
class ClassificationAllowlists:
    """Tag/type allowlists injected into entity-stage prompts."""

    tool_types: list[str]
    howto_tags: list[str]
    impl_study_tags: list[str]
    glossary_tags: list[str]
    topic_tags: list[str]
    trend_tags: list[str]
    model_types: list[str]
    tool_tags: list[str]
    model_tags: list[str]


def build_prompt_cache_key(*, prompt_version: str, source_id: str) -> str:
    """Stable cache key for all stages of one classification run."""
    return f"ingest-classify:{prompt_version}:{source_id}"


def build_cached_classification_prefix(
    doc: SourceDocument,
    *,
    prompt_version: str,
) -> str:
    """Stable user-message prefix: metadata + article (identical across stages)."""
    meta_lines = [
        f"prompt_version: {prompt_version}",
        f"source_id: {doc.source_id}",
        f"title: {doc.title or ''}",
        f"author: {doc.author or ''}",
        f"publication: {doc.publication or ''}",
        f"published_date: {doc.published_date or ''}",
        f"canonical_url: {doc.canonical_url or ''}",
    ]
    return "\n\n".join(
        [
            "## Metadata\n" + "\n".join(meta_lines),
            "## ARTICLE_PLAIN_TEXT\n" + doc.plain_text,
        ]
    )


def _schema_hint(schema: dict[str, Any]) -> str:
    return json.dumps(schema, indent=2)[:_SCHEMA_HINT_MAX]


def build_extraction_budget_block(extraction_budgets: dict[str, int] | None) -> str:
    """Format EXTRACTION_BUDGET_RUBRIC with per-entity limits."""
    budgets = extraction_budgets or {}
    budget_labels = {
        "glossary": "glossary",
        "topics": "topics",
        "how_to": "how_to",
        "industry_trends": "industry_trends",
        "tools": "tools (only if substantially discussed)",
        "foundation_models": "foundation_models (only if substantially discussed)",
        "implementation_studies": (
            "implementation_studies (only if worthiness gate passes; else [])"
        ),
        "roundup_signals": "roundup_signals",
        "interview_insights": "interview_insights",
    }
    lines: list[str] = []
    for bk, label in budget_labels.items():
        mx = budgets.get(bk, 3)
        note = ""
        if bk == "tools":
            note = " (uncapped when detected type is ai_tools_roundup)"
        elif bk == "how_to":
            note = " (uncapped when detected type is how_to_roundup)"
        elif bk == "foundation_models":
            note = " (uncapped when detected type is ai_tools_roundup)"
        lines.append(f"- {label}: max {mx} proposals{note}")
    return op.EXTRACTION_BUDGET_RUBRIC.format(budget_lines="\n".join(lines))


def _allowlist_section(header: str, items: list[str]) -> str:
    return f"{header}\n" + "\n".join(f"- {t}" for t in items)


def _allowlist_blocks(
    allowlists: ClassificationAllowlists,
    *,
    include_tool_types: bool = False,
    include_model_types: bool = False,
    include_howto: bool = False,
    include_impl_study: bool = False,
    include_glossary: bool = False,
    include_topic: bool = False,
    include_trend: bool = False,
    include_tool_tags: bool = False,
    include_model_tags: bool = False,
) -> list[str]:
    blocks: list[str] = []
    if include_tool_types:
        blocks.append(_allowlist_section("## TOOL_TYPES_ALLOWLIST", allowlists.tool_types))
    if include_tool_tags:
        blocks.append(_allowlist_section("## TOOL_TAGS_ALLOWLIST", allowlists.tool_tags))
    if include_model_types:
        blocks.append(_allowlist_section("## MODEL_TYPES_ALLOWLIST", allowlists.model_types))
    if include_model_tags:
        blocks.append(_allowlist_section("## MODEL_TAGS_ALLOWLIST", allowlists.model_tags))
    if include_howto:
        blocks.append(_allowlist_section("## HOWTO_TAGS_ALLOWLIST", allowlists.howto_tags))
    if include_impl_study:
        blocks.append(
            _allowlist_section("## IMPL_STUDY_TAGS_ALLOWLIST", allowlists.impl_study_tags)
        )
    if include_glossary:
        blocks.append(_allowlist_section("## GLOSSARY_TAGS_ALLOWLIST", allowlists.glossary_tags))
    if include_topic:
        blocks.append(_allowlist_section("## TOPIC_TAGS_ALLOWLIST", allowlists.topic_tags))
    if include_trend:
        blocks.append(_allowlist_section("## TREND_TAGS_ALLOWLIST", allowlists.trend_tags))
    return blocks


def _canonical_blocks(
    wiki: WikiSnapshot,
    reviews_root: Path | None,
    *,
    glossary: bool = False,
    tools: bool = False,
    models: bool = False,
    impl_study: bool = False,
    topics: bool = False,
    howto: bool = False,
    trends: bool = False,
) -> list[str]:
    canonical = build_canonical_title_prompt_blocks(wiki, reviews_root)
    blocks: list[str] = []
    if glossary:
        blocks.append("## CANONICAL_GLOSSARY_TERMS\n" + canonical["CANONICAL_GLOSSARY_TERMS"])
    if tools:
        blocks.append("## CANONICAL_TOOL_NAMES\n" + canonical["CANONICAL_TOOL_NAMES"])
    if models:
        blocks.append(
            "## CANONICAL_FOUNDATION_MODEL_NAMES\n" + canonical["CANONICAL_FOUNDATION_MODEL_NAMES"]
        )
    if impl_study:
        blocks.append("## CANONICAL_IMPL_STUDY_TITLES\n" + canonical["CANONICAL_IMPL_STUDY_TITLES"])
    if topics:
        blocks.append("## CANONICAL_TOPIC_TITLES\n" + canonical["CANONICAL_TOPIC_TITLES"])
        topic_slugs = wiki.topic_slugs[:100] if wiki.topic_slugs else []
        blocks.append(
            "## EXISTING_TOPIC_SLUGS\n" + ("\n".join(f"- {s}" for s in topic_slugs) or "(none)")
        )
    if howto:
        blocks.append("## CANONICAL_HOWTO_TITLES\n" + canonical["CANONICAL_HOWTO_TITLES"])
    if trends:
        blocks.append("## CANONICAL_TREND_TITLES\n" + canonical["CANONICAL_TREND_TITLES"])
        trend_slugs = wiki.trend_slugs[:100] if wiki.trend_slugs else []
        blocks.append(
            "## EXISTING_TREND_SLUGS\n" + ("\n".join(f"- {s}" for s in trend_slugs) or "(none)")
        )
    return blocks


def build_triage_prompt_suffix(
    *,
    extraction_budgets: dict[str, int] | None,
    source_type_override: str | None,
    prompt_version: str,
) -> str:
    """Stage 1 suffix: routing rubrics and triage-only instructions."""
    blocks = [
        op.TEMPORAL_ANCHORING_RULE,
        build_extraction_budget_block(extraction_budgets),
        "## SOURCE_TYPE_DETECTION_RUBRIC\n" + op.SOURCE_TYPE_DETECTION_RUBRIC,
        "## SOURCE_EVIDENCE_PROFILE_RUBRIC\n" + op.SOURCE_EVIDENCE_PROFILE_RUBRIC,
        "## JSON_SCHEMA_HINT\n" + _schema_hint(llm_output_json_schema_for_triage()),
        "## Instructions\n"
        "Output one JSON object with keys: extraction_meta, source_type_detection, "
        "source_evidence_profile only. "
        "FIRST: fill extraction_meta (skip_recommended, skip_reason, "
        "total_candidates_considered, review_burden_estimate). "
        "NEVER set skip_recommended=true when the source is clearly ai_tools_roundup or "
        "how_to_roundup (those require full list extraction in a later stage). "
        "THEN: fill source_type_detection per SOURCE_TYPE_DETECTION_RUBRIC. "
        "THEN: fill source_evidence_profile per SOURCE_EVIDENCE_PROFILE_RUBRIC. "
        "Do NOT extract glossary, tools, topics, or any entity arrays in this stage.",
    ]
    if source_type_override:
        blocks.append(
            f"## SOURCE_TYPE_OVERRIDE\nTreat this source as: {source_type_override}. "
            "Set source_type_detection.detected_source_type accordingly with high confidence."
        )
    blocks.append(f"stage_prompt_version: {prompt_version}-triage")
    return "\n\n".join(blocks)


def build_summary_prompt_suffix(
    triage: TriageStageOutput,
    *,
    prompt_version: str,
) -> str:
    """Stage 2 suffix: source chapters only."""
    triage_json = json.dumps(triage.model_dump(mode="json"), indent=2)
    detected = triage.source_type_detection.detected_source_type
    blocks = [
        op.TEMPORAL_ANCHORING_RULE,
        "## STAGE_1_TRIAGE_RESULT\n" + triage_json,
        "## SOURCE_CHAPTERS_RUBRIC\n" + op.SOURCE_CHAPTERS_RUBRIC,
        "## JSON_SCHEMA_HINT\n" + _schema_hint(llm_output_json_schema_for_summary()),
        "## Instructions\n"
        f"The detected source type is {detected!r} — do not change it in this stage. "
        "Output one JSON object with key source_summary only, per SOURCE_CHAPTERS_RUBRIC. "
        "If extraction_meta.skip_recommended is true and the type is not a list-roundup, "
        "return minimal empty chapter strings. "
        "Do NOT extract entity proposal arrays.",
        f"stage_prompt_version: {prompt_version}-summary",
    ]
    return "\n\n".join(blocks)


def _standard_entity_rubric_blocks(allowlists: ClassificationAllowlists) -> list[str]:
    return [
        op.VALUE_RANKING_RUBRIC,
        op.ABSTRACTION_SELECTION_RUBRIC,
        op.COMPRESSION_PRESSURE_RUBRIC,
        op.MINIMUM_NOVELTY_THRESHOLD_RUBRIC,
        op.TAG_ONTOLOGY_RUBRIC,
        op.GLOBAL_NAMESPACES_RUBRIC,
        op.REGISTRY_TYPES_SEMANTICS,
        "## TITLE_GENERATION_RUBRIC\n" + op.TITLE_GENERATION_RUBRIC,
        "## TITLE_CANONICALIZATION_RUBRIC\n" + op.TITLE_CANONICALIZATION_RUBRIC,
        "## PAGE_MATCHING_RUBRIC\n" + op.PAGE_MATCHING_RUBRIC,
        "## GLOSSARY_RUBRIC\n" + op.GLOSSARY_RUBRIC,
        "## IMPL_STUDY_RUBRIC\n" + op.IMPL_STUDY_RUBRIC,
        "## TOPICS_RUBRIC\n" + op.TOPICS_RUBRIC,
        "## HOWTOS_RUBRIC\n" + op.HOWTOS_RUBRIC,
        "## TRENDS_RUBRIC\n" + op.TRENDS_RUBRIC,
        "## TOOLS_RUBRIC\n" + op.TOOLS_RUBRIC,
        "## MODELS_RUBRIC\n" + op.MODELS_RUBRIC,
        *_allowlist_blocks(
            allowlists,
            include_tool_types=True,
            include_model_types=True,
            include_howto=True,
            include_impl_study=True,
            include_glossary=True,
            include_topic=True,
            include_trend=True,
            include_tool_tags=True,
            include_model_tags=True,
        ),
    ]


def build_entities_prompt_suffix(
    route: SourceType,
    triage: TriageStageOutput,
    summary_json: str,
    *,
    wiki: WikiSnapshot,
    allowlists: ClassificationAllowlists,
    extraction_budgets: dict[str, int] | None,
    reviews_root: Path | None,
    prompt_version: str,
) -> str:
    """Stage 3 suffix: route-specific entity extraction."""
    triage_json = json.dumps(triage.model_dump(mode="json"), indent=2)
    entity_keys = ENTITY_FIELDS_BY_SOURCE_TYPE.get(route, ENTITY_FIELDS_BY_SOURCE_TYPE["unknown"])
    blocks: list[str] = [
        op.TEMPORAL_ANCHORING_RULE,
        build_extraction_budget_block(extraction_budgets),
        "## STAGE_1_TRIAGE_RESULT\n" + triage_json,
        "## STAGE_2_SOURCE_SUMMARY\n" + summary_json,
        f"## ROUTE\nYou are extracting entities for detected_source_type={route!r}. "
        f"Populate only these JSON keys: {', '.join(entity_keys)}. "
        "All other entity keys must be empty arrays [].",
    ]

    if route == "ai_tools_roundup":
        blocks.extend(
            [
                op.AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC,
                op.VALUE_RANKING_RUBRIC,
                op.TAG_ONTOLOGY_RUBRIC,
                op.REGISTRY_TYPES_SEMANTICS,
                "## TOOLS_RUBRIC\n" + op.TOOLS_RUBRIC,
                "## MODELS_RUBRIC\n" + op.MODELS_RUBRIC,
                *_allowlist_blocks(
                    allowlists,
                    include_tool_types=True,
                    include_model_types=True,
                    include_tool_tags=True,
                    include_model_tags=True,
                ),
                *_canonical_blocks(wiki, reviews_root, tools=True, models=True),
            ]
        )
    elif route == "how_to_roundup":
        blocks.extend(
            [
                op.HOW_TO_ROUNDUP_EXTRACTION_RUBRIC,
                op.VALUE_RANKING_RUBRIC,
                op.TAG_ONTOLOGY_RUBRIC,
                "## HOWTOS_RUBRIC\n" + op.HOWTOS_RUBRIC,
                *_allowlist_blocks(allowlists, include_howto=True),
                *_canonical_blocks(wiki, reviews_root, howto=True),
            ]
        )
    elif route == "ai_industry_roundup":
        blocks.extend(
            [
                op.VALUE_RANKING_RUBRIC,
                op.TAG_ONTOLOGY_RUBRIC,
                "## ROUNDUP_SIGNALS_RUBRIC\n" + op.ROUNDUP_SIGNALS_RUBRIC,
                "## TRENDS_RUBRIC\n" + op.TRENDS_RUBRIC,
                *_allowlist_blocks(allowlists, include_trend=True),
                *_canonical_blocks(wiki, reviews_root, trends=True),
            ]
        )
    elif route == "interview_or_transcript":
        blocks.extend(
            [
                op.VALUE_RANKING_RUBRIC,
                op.TAG_ONTOLOGY_RUBRIC,
                "## INTERVIEW_INSIGHTS_RUBRIC\n" + op.INTERVIEW_INSIGHTS_RUBRIC,
                *_allowlist_blocks(allowlists, include_topic=True),
                *_canonical_blocks(wiki, reviews_root, topics=True),
            ]
        )
    else:
        blocks.extend(_standard_entity_rubric_blocks(allowlists))
        blocks.extend(
            _canonical_blocks(
                wiki,
                reviews_root,
                glossary=True,
                tools=True,
                models=True,
                impl_study=True,
                topics=True,
                howto=True,
                trends=True,
            )
        )

    entity_schema = llm_output_json_schema_for_entities(route)
    blocks.append("## JSON_SCHEMA_HINT\n" + _schema_hint(entity_schema))
    blocks.append(
        "## Instructions\n"
        f"Output one JSON object with entity keys for route {route!r} only. "
        "Apply PAGE_MATCHING_RUBRIC before reusing CANONICAL_* titles. "
        "Every proposal MUST include value_level. "
        "Respect EXTRACTION BUDGETS unless this route is ai_tools_roundup or how_to_roundup. "
        "Use empty arrays for keys outside this route."
    )
    blocks.append(f"stage_prompt_version: {prompt_version}-entities-{route}")
    return "\n\n".join(blocks)


def build_monolithic_prompt_suffix(
    doc: SourceDocument,
    wiki: WikiSnapshot,
    allowlists: ClassificationAllowlists,
    *,
    source_type_override: str | None,
    extraction_budgets: dict[str, int] | None,
    reviews_root: Path | None,
    prompt_version: str,
) -> str:
    """Full rubric suffix for monolithic fallback (prefix + suffix layout)."""
    from src.ingest_review.schema import llm_output_json_schema_for_classification

    canonical = build_canonical_title_prompt_blocks(wiki, reviews_root)
    trend_slugs = wiki.trend_slugs[:100] if wiki.trend_slugs else []
    blocks = [
        op.TEMPORAL_ANCHORING_RULE,
        build_extraction_budget_block(extraction_budgets),
        op.AI_TOOLS_ROUNDUP_EXTRACTION_RUBRIC,
        op.HOW_TO_ROUNDUP_EXTRACTION_RUBRIC,
        op.VALUE_RANKING_RUBRIC,
        op.ABSTRACTION_SELECTION_RUBRIC,
        op.COMPRESSION_PRESSURE_RUBRIC,
        op.MINIMUM_NOVELTY_THRESHOLD_RUBRIC,
        op.SOURCE_EVIDENCE_PROFILE_RUBRIC,
        op.TAG_ONTOLOGY_RUBRIC,
        op.GLOBAL_NAMESPACES_RUBRIC,
        op.REGISTRY_TYPES_SEMANTICS,
        "## TITLE_GENERATION_RUBRIC\n" + op.TITLE_GENERATION_RUBRIC,
        "## TITLE_CANONICALIZATION_RUBRIC\n" + op.TITLE_CANONICALIZATION_RUBRIC,
        "## PAGE_MATCHING_RUBRIC\n" + op.PAGE_MATCHING_RUBRIC,
        "## CANONICAL_GLOSSARY_TERMS\n" + canonical["CANONICAL_GLOSSARY_TERMS"],
        "## CANONICAL_TOOL_NAMES\n" + canonical["CANONICAL_TOOL_NAMES"],
        "## CANONICAL_FOUNDATION_MODEL_NAMES\n" + canonical["CANONICAL_FOUNDATION_MODEL_NAMES"],
        "## CANONICAL_IMPL_STUDY_TITLES\n" + canonical["CANONICAL_IMPL_STUDY_TITLES"],
        "## CANONICAL_TOPIC_TITLES\n" + canonical["CANONICAL_TOPIC_TITLES"],
        "## CANONICAL_HOWTO_TITLES\n" + canonical["CANONICAL_HOWTO_TITLES"],
        "## CANONICAL_TREND_TITLES\n" + canonical["CANONICAL_TREND_TITLES"],
        "## EXISTING_TOPIC_SLUGS\n"
        + ("\n".join(f"- {s}" for s in wiki.topic_slugs[:100]) or "(none)"),
        "## EXISTING_TREND_SLUGS\n" + ("\n".join(f"- {s}" for s in trend_slugs) or "(none)"),
        *_allowlist_blocks(
            allowlists,
            include_tool_types=True,
            include_model_types=True,
            include_howto=True,
            include_impl_study=True,
            include_glossary=True,
            include_topic=True,
            include_trend=True,
            include_tool_tags=True,
            include_model_tags=True,
        ),
        "## SOURCE_TYPE_DETECTION_RUBRIC\n" + op.SOURCE_TYPE_DETECTION_RUBRIC,
        "## SOURCE_CHAPTERS_RUBRIC\n" + op.SOURCE_CHAPTERS_RUBRIC,
        "## GLOSSARY_RUBRIC\n" + op.GLOSSARY_RUBRIC,
        "## IMPL_STUDY_RUBRIC\n" + op.IMPL_STUDY_RUBRIC,
        "## TOPICS_RUBRIC\n" + op.TOPICS_RUBRIC,
        "## HOWTOS_RUBRIC\n" + op.HOWTOS_RUBRIC,
        "## TRENDS_RUBRIC\n" + op.TRENDS_RUBRIC,
        "## TOOLS_RUBRIC\n" + op.TOOLS_RUBRIC,
        "## MODELS_RUBRIC\n" + op.MODELS_RUBRIC,
        "## ROUNDUP_SIGNALS_RUBRIC\n" + op.ROUNDUP_SIGNALS_RUBRIC,
        "## INTERVIEW_INSIGHTS_RUBRIC\n" + op.INTERVIEW_INSIGHTS_RUBRIC,
        "## JSON_SCHEMA_HINT\n" + _schema_hint(llm_output_json_schema_for_classification()),
    ]
    if source_type_override:
        blocks.append(
            f"## SOURCE_TYPE_OVERRIDE\nTreat this source as: {source_type_override}. "
            "Set source_type_detection.detected_source_type accordingly."
        )
    blocks.append(
        "## Instructions\n"
        "Output one JSON object matching the schema keys: extraction_meta, "
        "source_evidence_profile, source_type_detection, source_summary, glossary, "
        "tools, foundation_models, how_to, topics, implementation_studies, industry_trends, "
        "roundup_signals, interview_insights. "
        "Follow detected_source_type routing rules in the rubrics above."
    )
    blocks.append(f"stage_prompt_version: {prompt_version}-monolithic")
    _ = doc  # prefix holds article; suffix references rubrics only
    return "\n\n".join(blocks)


def classification_allowlists_from_kwargs(
    *,
    tool_types_allowlist: list[str],
    howto_tags_allowlist: list[str],
    impl_study_tags_allowlist: list[str] | None = None,
    glossary_tags_allowlist: list[str] | None = None,
    topic_tags_allowlist: list[str] | None = None,
    trend_tags_allowlist: list[str] | None = None,
    model_types_allowlist: list[str] | None = None,
    tool_tags_allowlist: list[str] | None = None,
    model_tags_allowlist: list[str] | None = None,
) -> ClassificationAllowlists:
    """Build allowlist bundle from provider kwargs."""
    return ClassificationAllowlists(
        tool_types=tool_types_allowlist,
        howto_tags=howto_tags_allowlist,
        impl_study_tags=impl_study_tags_allowlist or [],
        glossary_tags=glossary_tags_allowlist or [],
        topic_tags=topic_tags_allowlist or [],
        trend_tags=trend_tags_allowlist or [],
        model_types=model_types_allowlist or [],
        tool_tags=tool_tags_allowlist or [],
        model_tags=model_tags_allowlist or [],
    )


def default_prompt_version() -> str:
    """Current classification prompt version."""
    return PROMPT_VERSION
