"""Orchestrate staged ingest classification (triage → summary → entities)."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast, get_args

from src.ingest_review.classification_prompts import classification_allowlists_from_kwargs
from src.ingest_review.schema import (
    LIST_ROUNDUP_SOURCE_TYPES,
    LlmClassificationOutput,
    SourceType,
    SourceTypeDetection,
    TriageStageOutput,
    empty_entities_stage_output,
    merge_stage_outputs,
)

if TYPE_CHECKING:
    from src.ingest_review.extract import SourceDocument
    from src.ingest_review.providers.base import IngestionProvider
    from src.ingest_review.wiki_snapshot import WikiSnapshot

logger = logging.getLogger(__name__)

PipelineMode = Literal["staged", "monolithic"]


def classification_pipeline_mode() -> PipelineMode:
    """Return pipeline mode from ``INGEST_CLASSIFICATION_PIPELINE`` env var."""
    raw = os.environ.get("INGEST_CLASSIFICATION_PIPELINE", "staged").strip().lower()
    return "monolithic" if raw == "monolithic" else "staged"


def should_skip_later_stages(triage: TriageStageOutput) -> bool:
    """True when entity extraction (stage 3) should be skipped (skip gate, non-list-roundup).

    Stage 2 (source_summary) still runs so the article can be kept in the knowledge base
    without durable entity proposals.
    """
    if not triage.extraction_meta.skip_recommended:
        return False
    detected = triage.source_type_detection.detected_source_type
    return detected not in LIST_ROUNDUP_SOURCE_TYPES


def apply_source_type_override(
    triage: TriageStageOutput,
    override: str | None,
) -> TriageStageOutput:
    """Apply CLI/dashboard source type override after stage 1."""
    if not override or not override.strip():
        return triage
    st = override.strip()
    if st not in get_args(SourceType):
        logger.warning("Ignoring invalid source_type_override: %s", st)
        return triage
    detection = SourceTypeDetection(
        detected_source_type=cast(SourceType, st),
        confidence=1.0,
        reasoning=[f"source_type_override: {st}"],
    )
    return triage.model_copy(update={"source_type_detection": detection})


def _stage_cache_hit_rate(token_usage: dict[str, Any] | None) -> float | None:
    if not token_usage:
        return None
    prompt = int(token_usage.get("prompt_tokens") or 0)
    if prompt <= 0:
        return None
    details = token_usage.get("prompt_tokens_details") or {}
    cached = int(details.get("cached_tokens") or 0)
    return cached / prompt


def _log_cache_miss(stage_name: str, token_usage: dict[str, Any] | None) -> None:
    if not token_usage:
        return
    prompt = int(token_usage.get("prompt_tokens") or 0)
    details = token_usage.get("prompt_tokens_details") or {}
    cached = int(details.get("cached_tokens") or 0)
    if stage_name in ("summary", "entities") and prompt > 1024 and cached == 0:
        logger.warning(
            "Prompt cache miss on classification stage %s (prompt_tokens=%s)",
            stage_name,
            prompt,
        )


def run_staged_classification(
    provider: IngestionProvider,
    *,
    document: SourceDocument,
    wiki: WikiSnapshot,
    tool_types_allowlist: list[str],
    howto_tags_allowlist: list[str],
    impl_study_tags_allowlist: list[str] | None = None,
    glossary_tags_allowlist: list[str] | None = None,
    topic_tags_allowlist: list[str] | None = None,
    trend_tags_allowlist: list[str] | None = None,
    model_types_allowlist: list[str] | None = None,
    tool_tags_allowlist: list[str] | None = None,
    model_tags_allowlist: list[str] | None = None,
    source_type_override: str | None = None,
    extraction_budgets: dict[str, int] | None = None,
    reviews_root: Path | None = None,
    model: str,
    prompt_version: str,
    max_retries: int = 3,
) -> tuple[LlmClassificationOutput, dict[str, Any]]:
    """Run triage → summary → entities and merge into full classification output."""
    allowlists = classification_allowlists_from_kwargs(
        tool_types_allowlist=tool_types_allowlist,
        howto_tags_allowlist=howto_tags_allowlist,
        impl_study_tags_allowlist=impl_study_tags_allowlist,
        glossary_tags_allowlist=glossary_tags_allowlist,
        topic_tags_allowlist=topic_tags_allowlist,
        trend_tags_allowlist=trend_tags_allowlist,
        model_types_allowlist=model_types_allowlist,
        tool_tags_allowlist=tool_tags_allowlist,
        model_tags_allowlist=model_tags_allowlist,
    )
    stage_meta: list[dict[str, Any]] = []

    triage, triage_meta = provider.analyze_triage(
        document=document,
        wiki=wiki,
        allowlists=allowlists,
        source_type_override=source_type_override,
        extraction_budgets=extraction_budgets,
        reviews_root=reviews_root,
        model=model,
        prompt_version=prompt_version,
        max_retries=max_retries,
    )
    triage = apply_source_type_override(triage, source_type_override)
    stage_meta.append(
        {
            "name": "triage",
            "prompt_version": f"{prompt_version}-triage",
            "token_usage": triage_meta.get("token_usage"),
            "cache_hit_rate": _stage_cache_hit_rate(triage_meta.get("token_usage")),
            "request_id": triage_meta.get("request_id"),
        }
    )

    if should_skip_later_stages(triage):
        summary, summary_meta = provider.analyze_source_summary(
            document=document,
            triage=triage,
            model=model,
            prompt_version=prompt_version,
            max_retries=max_retries,
        )
        _log_cache_miss("summary", summary_meta.get("token_usage"))
        stage_meta.append(
            {
                "name": "summary",
                "prompt_version": f"{prompt_version}-summary",
                "token_usage": summary_meta.get("token_usage"),
                "cache_hit_rate": _stage_cache_hit_rate(summary_meta.get("token_usage")),
                "request_id": summary_meta.get("request_id"),
            }
        )
        entities = empty_entities_stage_output()
        parsed = merge_stage_outputs(triage, summary, entities)
        combined_usage = _combine_token_usage(
            triage_meta.get("token_usage"),
            summary_meta.get("token_usage"),
        )
        return parsed, {
            "request_id": summary_meta.get("request_id") or triage_meta.get("request_id"),
            "token_usage": combined_usage,
            "classification_pipeline": {
                "mode": "staged",
                "skipped_stages": ["entities"],
                "stages": stage_meta,
            },
        }

    summary, summary_meta = provider.analyze_source_summary(
        document=document,
        triage=triage,
        model=model,
        prompt_version=prompt_version,
        max_retries=max_retries,
    )
    _log_cache_miss("summary", summary_meta.get("token_usage"))
    stage_meta.append(
        {
            "name": "summary",
            "prompt_version": f"{prompt_version}-summary",
            "token_usage": summary_meta.get("token_usage"),
            "cache_hit_rate": _stage_cache_hit_rate(summary_meta.get("token_usage")),
            "request_id": summary_meta.get("request_id"),
        }
    )

    route: SourceType = triage.source_type_detection.detected_source_type
    entities, entities_meta = provider.analyze_entities(
        document=document,
        wiki=wiki,
        triage=triage,
        summary=summary,
        route=route,
        allowlists=allowlists,
        extraction_budgets=extraction_budgets,
        reviews_root=reviews_root,
        model=model,
        prompt_version=prompt_version,
        max_retries=max_retries,
    )
    _log_cache_miss("entities", entities_meta.get("token_usage"))
    stage_meta.append(
        {
            "name": "entities",
            "prompt_version": f"{prompt_version}-entities-{route}",
            "route": route,
            "token_usage": entities_meta.get("token_usage"),
            "cache_hit_rate": _stage_cache_hit_rate(entities_meta.get("token_usage")),
            "request_id": entities_meta.get("request_id"),
        }
    )

    parsed = merge_stage_outputs(triage, summary, entities)
    combined_usage = _combine_token_usage(
        triage_meta.get("token_usage"),
        summary_meta.get("token_usage"),
        entities_meta.get("token_usage"),
    )
    return parsed, {
        "request_id": entities_meta.get("request_id") or summary_meta.get("request_id"),
        "token_usage": combined_usage,
        "classification_pipeline": {"mode": "staged", "stages": stage_meta},
    }


def _combine_token_usage(
    *usages: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Sum token counts across pipeline stages for backward-compatible analysis_meta."""
    prompt = 0
    completion = 0
    cached = 0
    any_usage = False
    for usage in usages:
        if not usage:
            continue
        any_usage = True
        prompt += int(usage.get("prompt_tokens") or 0)
        completion += int(usage.get("completion_tokens") or 0)
        details = usage.get("prompt_tokens_details") or {}
        cached += int(details.get("cached_tokens") or 0)
    if not any_usage:
        return None
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": prompt + completion,
        "prompt_tokens_details": {"cached_tokens": cached},
    }
