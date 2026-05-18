"""Route misclassified foundation models out of ``tools`` for ``ai_tools_roundup`` sources."""

from __future__ import annotations

import re
from collections.abc import Sequence

from src.ingest_review.schema import (
    FoundationModelProposal,
    LlmClassificationOutput,
    ToolProposal,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def _compact_alnum(s: str) -> str:
    """Lowercase alphanumeric only (for fuzzy name matching)."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _wiki_name_suggests_foundation_model(tool_name: str, wiki_names: Sequence[str]) -> bool:
    """True if *tool_name* likely refers to a wiki-indexed foundation model."""
    tn = _compact_alnum(tool_name)
    if len(tn) < 4:
        return False
    for raw in wiki_names:
        wn = _compact_alnum(raw)
        if len(wn) < 4:
            continue
        if tn == wn:
            return True
        longer, shorter = (tn, wn) if len(tn) >= len(wn) else (wn, tn)
        if len(shorter) >= 5 and shorter in longer:
            return True
    return False


def _proposed_types_are_model_only(
    proposed_types: list[str],
    tool_types: set[str],
    model_types: set[str],
) -> bool:
    """True when every non-empty proposed type is a model type and none are tool types."""
    props = {p for p in proposed_types if p}
    if not props:
        return False
    if props & tool_types:
        return False
    if not (props & model_types):
        return False
    return props <= model_types


def tool_should_be_routed_to_foundation_model(
    tool: ToolProposal,
    wiki_names: Sequence[str],
    tool_types: set[str],
    model_types: set[str],
) -> bool:
    """Decide whether a *tools* entry is really a foundation model for roundup routing."""
    if _wiki_name_suggests_foundation_model(tool.name, wiki_names):
        return True
    return _proposed_types_are_model_only(tool.proposed_types, tool_types, model_types)


def convert_tool_proposal_to_foundation_model(tool: ToolProposal) -> FoundationModelProposal:
    """Map a :class:`ToolProposal` to :class:`FoundationModelProposal` (field alignment)."""
    return FoundationModelProposal(
        model_name=tool.name,
        provider="",
        operational_profile=tool.short_description,
        deployment_implications=tool.operational_relevance,
        weaknesses_limitations=tool.weaknesses_limitations,
        service_automation_implications=tool.operational_relevance,
        maturity_signals=tool.maturity_signals,
        pricing_inference_implications="",
        supporting_snippet=tool.supporting_snippet,
        core_capabilities=list(tool.core_capabilities),
        benchmark_observations=[],
        comparative_observations=list(tool.integration_ecosystem),
        related_models=list(tool.related_tools),
        proposed_types=list(tool.proposed_types),
        proposed_new_type=tool.proposed_new_type,
        match_candidates=list(tool.match_candidates),
        confidence=tool.confidence,
        suggested_action=tool.suggested_action,
        value_level=tool.value_level,
        evidence_type=tool.evidence_type,
    )


def route_ai_tools_roundup_tools_to_foundation_models(
    parsed: LlmClassificationOutput,
    wiki: WikiSnapshot,
    tool_types: Sequence[str],
    model_types: Sequence[str],
) -> LlmClassificationOutput:
    """Move roundup *tools* that are foundation models into ``foundation_models``.

    Runs on raw LLM ``proposed_types`` (before tag allowlists strip cross-registry types).
    """
    if parsed.source_type_detection.detected_source_type != "ai_tools_roundup":
        return parsed

    tt = set(tool_types)
    mt = set(model_types)
    kept: list[ToolProposal] = []
    extras: list[FoundationModelProposal] = []
    for tp in parsed.tools:
        if tool_should_be_routed_to_foundation_model(tp, wiki.foundation_model_names, tt, mt):
            extras.append(convert_tool_proposal_to_foundation_model(tp))
        else:
            kept.append(tp)

    if not extras:
        return parsed

    return parsed.model_copy(
        update={
            "tools": kept,
            "foundation_models": list(parsed.foundation_models) + extras,
        }
    )
