"""Merge per-proposal LLM regeneration into review artifacts (all entity types)."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.ingest_review.domain_tag_ui import find_review_node
from src.ingest_review.schema import (
    GLOSSARY_LIST_KEYS,
    GLOSSARY_REVIEWABLE_LIST_KEYS,
    GLOSSARY_REVIEWABLE_SCALAR_KEYS,
    GLOSSARY_SCALAR_KEYS,
    HOWTO_LIST_KEYS,
    HOWTO_REVIEWABLE_LIST_KEYS,
    HOWTO_REVIEWABLE_SCALAR_KEYS,
    HOWTO_SCALAR_KEYS,
    IMPL_STUDY_LIST_KEYS,
    IMPL_STUDY_REVIEWABLE_LIST_KEYS,
    IMPL_STUDY_REVIEWABLE_SCALAR_KEYS,
    IMPL_STUDY_SCALAR_KEYS,
    MODEL_LIST_KEYS,
    MODEL_REVIEWABLE_LIST_KEYS,
    MODEL_REVIEWABLE_SCALAR_KEYS,
    MODEL_SCALAR_KEYS,
    TOOL_LIST_KEYS,
    TOOL_REVIEWABLE_LIST_KEYS,
    TOOL_REVIEWABLE_SCALAR_KEYS,
    TOOL_SCALAR_KEYS,
    TOPIC_LIST_KEYS,
    TOPIC_REVIEWABLE_LIST_KEYS,
    TOPIC_REVIEWABLE_SCALAR_KEYS,
    TOPIC_SCALAR_KEYS,
    TREND_LIST_KEYS,
    TREND_REVIEWABLE_LIST_KEYS,
    TREND_REVIEWABLE_SCALAR_KEYS,
    TREND_SCALAR_KEYS,
    normalize_glossary_term_capitalization,
)
from src.pipeline.slug import slugify


def _utc_now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class ProposalRegenSpec:
    """Configuration for applying regeneration to one proposal entity type."""

    entity_key: str
    review_list_key: str
    llm_output_key: str
    title_field: str
    slug_field: str | None
    scalar_keys: tuple[str, ...]
    list_keys: tuple[str, ...]
    reviewable_scalar_keys: tuple[str, ...]
    reviewable_list_keys: tuple[str, ...]
    content_merge_keys: tuple[str, ...]
    normalize_title: Callable[[str], str] | None = None
    entity_label: str = ""


def _fresh_sections(
    llm_item: dict[str, Any],
    reviewable_scalar_keys: tuple[str, ...],
    reviewable_list_keys: tuple[str, ...],
) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    for sk in reviewable_scalar_keys:
        sections[sk] = {"status": "pending", "final_text": None, "notes": None}
    for lk in reviewable_list_keys:
        llm_list_val = llm_item.get(lk) or []
        if not isinstance(llm_list_val, list):
            llm_list_val = []
        sections[lk] = {
            "status": "pending",
            "final_list": None,
            "notes": None,
            "llm_list": copy.deepcopy(llm_list_val),
        }
    return sections


def _review_index(artifact: dict[str, Any], proposal_id: str, review_list_key: str) -> int | None:
    for i, node in enumerate((artifact.get("review") or {}).get(review_list_key) or []):
        if isinstance(node, dict) and node.get("proposal_id") == proposal_id:
            return i
    return None


def apply_regenerated_proposal(
    artifact: dict[str, Any],
    proposal_id: str,
    spec: ProposalRegenSpec,
    *,
    new_title: str,
    regenerated: dict[str, Any],
    model: str,
    prompt_version: str,
) -> None:
    """Merge regenerated content under *new_title* into review + llm_output."""
    title = new_title.strip()
    if not title:
        raise ValueError("new_title must be non-empty")
    if spec.normalize_title:
        title = spec.normalize_title(title)

    node = find_review_node(artifact, proposal_id, spec.review_list_key)
    if not node:
        raise ValueError(f"Unknown {spec.entity_key} proposal_id: {proposal_id}")

    idx = _review_index(artifact, proposal_id, spec.review_list_key)
    llm_item = node.setdefault("llm_item", {})

    llm_item[spec.title_field] = title
    if spec.slug_field:
        llm_item[spec.slug_field] = slugify(title)

    for key in spec.content_merge_keys:
        if key in regenerated:
            llm_item[key] = regenerated[key]

    node["sections"] = _fresh_sections(
        llm_item, spec.reviewable_scalar_keys, spec.reviewable_list_keys
    )

    prev = node.get("proposal_regeneration_meta")
    count = 0
    if isinstance(prev, dict):
        count = int(prev.get("regen_count") or 0)
    node["proposal_regeneration_meta"] = {
        "regen_count": count + 1,
        "last_regen_at": _utc_now_iso(),
        "model": model,
        "prompt_version": prompt_version,
    }

    if idx is not None:
        llm_items = artifact.setdefault("llm_output", {}).setdefault(spec.llm_output_key, [])
        if isinstance(llm_items, list) and idx < len(llm_items):
            if not isinstance(llm_items[idx], dict):
                llm_items[idx] = {}
            out_item = copy.deepcopy(llm_item)
            for sk in spec.scalar_keys:
                if sk not in out_item and sk in spec.reviewable_scalar_keys:
                    out_item[sk] = ""
            for lk in spec.list_keys:
                if lk not in out_item:
                    out_item[lk] = []
            llm_items[idx] = out_item


_TOPIC_MERGE_KEYS: tuple[str, ...] = (
    "knowledge_summary",
    "examples",
    "operational_insight",
    "relevance_note",
    "supporting_snippet",
    "key_points",
    "related_topics",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)

_GLOSSARY_MERGE_KEYS: tuple[str, ...] = (
    "proposed_definition",
    "extended_explanation",
    "relevance_note",
    "supporting_snippet",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)

_HOWTO_MERGE_KEYS: tuple[str, ...] = (
    "what_and_problem",
    "answer_summary",
    "caveats",
    "implementation_steps",
    "prerequisites",
    "related_howtos",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)

_TREND_MERGE_KEYS: tuple[str, ...] = (
    "trend_description",
    "evidence_from_source",
    "time_sensitivity",
    "uncertainty_note",
    "assessed_as_of",
    "supporting_snippet",
    "supporting_data_points",
    "related_trends",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)

_TOOL_MERGE_KEYS: tuple[str, ...] = (
    "short_description",
    "operational_relevance",
    "strengths",
    "weaknesses_limitations",
    "maturity_signals",
    "supporting_snippet",
    "core_capabilities",
    "integration_ecosystem",
    "related_tools",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)

_MODEL_MERGE_KEYS: tuple[str, ...] = (
    "provider",
    "operational_summary",
    "strengths",
    "weaknesses_limitations",
    "workflow_implications",
    "service_automation_implications",
    "maturity_signals",
    "pricing_inference_implications",
    "supporting_snippet",
    "core_capabilities",
    "benchmark_observations",
    "comparative_observations",
    "related_models",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)

_IMPL_MERGE_KEYS: tuple[str, ...] = tuple(
    k for k in IMPL_STUDY_REVIEWABLE_SCALAR_KEYS if k != "title"
) + (
    "key_lessons",
    "open_questions",
    "related_sources",
    "match_candidates",
    "confidence",
    "suggested_action",
    "value_level",
    "evidence_type",
)


REGEN_SPECS: dict[str, ProposalRegenSpec] = {
    "topic": ProposalRegenSpec(
        entity_key="topic",
        review_list_key="topics",
        llm_output_key="topics",
        title_field="topic_title",
        slug_field="topic_slug",
        scalar_keys=TOPIC_SCALAR_KEYS,
        list_keys=TOPIC_LIST_KEYS,
        reviewable_scalar_keys=TOPIC_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=TOPIC_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_TOPIC_MERGE_KEYS,
        entity_label="Topic",
    ),
    "glossary": ProposalRegenSpec(
        entity_key="glossary",
        review_list_key="glossary",
        llm_output_key="glossary",
        title_field="term",
        slug_field=None,
        scalar_keys=GLOSSARY_SCALAR_KEYS,
        list_keys=GLOSSARY_LIST_KEYS,
        reviewable_scalar_keys=GLOSSARY_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=GLOSSARY_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_GLOSSARY_MERGE_KEYS,
        normalize_title=normalize_glossary_term_capitalization,
        entity_label="Glossary term",
    ),
    "how_to": ProposalRegenSpec(
        entity_key="how_to",
        review_list_key="how_to",
        llm_output_key="how_to",
        title_field="question_title",
        slug_field=None,
        scalar_keys=HOWTO_SCALAR_KEYS,
        list_keys=HOWTO_LIST_KEYS,
        reviewable_scalar_keys=HOWTO_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=HOWTO_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_HOWTO_MERGE_KEYS,
        entity_label="How-to",
    ),
    "trend": ProposalRegenSpec(
        entity_key="trend",
        review_list_key="industry_trends",
        llm_output_key="industry_trends",
        title_field="trend_title",
        slug_field="trend_slug",
        scalar_keys=TREND_SCALAR_KEYS,
        list_keys=TREND_LIST_KEYS,
        reviewable_scalar_keys=TREND_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=TREND_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_TREND_MERGE_KEYS,
        entity_label="Trend",
    ),
    "tool": ProposalRegenSpec(
        entity_key="tool",
        review_list_key="tools",
        llm_output_key="tools",
        title_field="name",
        slug_field=None,
        scalar_keys=TOOL_SCALAR_KEYS,
        list_keys=TOOL_LIST_KEYS,
        reviewable_scalar_keys=TOOL_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=TOOL_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_TOOL_MERGE_KEYS,
        entity_label="Tool",
    ),
    "model": ProposalRegenSpec(
        entity_key="model",
        review_list_key="foundation_models",
        llm_output_key="foundation_models",
        title_field="model_name",
        slug_field=None,
        scalar_keys=MODEL_SCALAR_KEYS,
        list_keys=MODEL_LIST_KEYS,
        reviewable_scalar_keys=MODEL_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=MODEL_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_MODEL_MERGE_KEYS,
        entity_label="Model",
    ),
    "impl_study": ProposalRegenSpec(
        entity_key="impl_study",
        review_list_key="implementation_studies",
        llm_output_key="implementation_studies",
        title_field="title",
        slug_field=None,
        scalar_keys=IMPL_STUDY_SCALAR_KEYS,
        list_keys=IMPL_STUDY_LIST_KEYS,
        reviewable_scalar_keys=IMPL_STUDY_REVIEWABLE_SCALAR_KEYS,
        reviewable_list_keys=IMPL_STUDY_REVIEWABLE_LIST_KEYS,
        content_merge_keys=_IMPL_MERGE_KEYS,
        entity_label="Implementation study",
    ),
}
