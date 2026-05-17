"""Source-level evidence profile with optional per-proposal overrides."""

from __future__ import annotations

from collections import Counter
from typing import Any

from src.ingest_review.schema import (
    EVIDENCE_TYPE_SET,
    LlmClassificationOutput,
    normalize_evidence_type,
)

ENTITY_LLM_KEYS: tuple[str, ...] = (
    "glossary",
    "tools",
    "foundation_models",
    "how_to",
    "topics",
    "implementation_studies",
    "industry_trends",
    "roundup_signals",
    "interview_insights",
)


def _iter_proposal_dicts(llm: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in ENTITY_LLM_KEYS:
        items = llm.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                out.append(item)
    return out


def infer_primary_evidence_type_from_proposals(llm: dict[str, Any]) -> str:
    """Pick the modal ``evidence_type`` across proposals; tie-break toward non-unknown."""
    counts: Counter[str] = Counter()
    for item in _iter_proposal_dicts(llm):
        et = item.get("evidence_type")
        if et is None:
            continue
        norm = normalize_evidence_type(et)
        if norm != "unknown":
            counts[norm] += 1
    if not counts:
        return "unknown"
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[0][0]


def source_evidence_profile_from_llm(llm: dict[str, Any]) -> dict[str, Any]:
    """Return ``source_evidence_profile`` dict from *llm*, with sensible defaults."""
    raw = llm.get("source_evidence_profile")
    if isinstance(raw, dict):
        primary = normalize_evidence_type(raw.get("primary_evidence_type"))
        reasoning = raw.get("reasoning")
        if not isinstance(reasoning, list):
            reasoning = []
        reasoning_out = [str(r).strip() for r in reasoning if str(r).strip()]
        if primary != "unknown":
            return {
                "primary_evidence_type": primary,
                "reasoning": reasoning_out,
            }
    inferred = infer_primary_evidence_type_from_proposals(llm)
    return {
        "primary_evidence_type": inferred,
        "reasoning": [],
    }


def source_primary_evidence_type(artifact: dict[str, Any]) -> str:
    """Effective source-level evidence type (review override > llm_output)."""
    review = artifact.get("review") or {}
    rev_node = review.get("source_evidence_profile")
    if isinstance(rev_node, dict):
        final = rev_node.get("final_item")
        if isinstance(final, dict) and final.get("primary_evidence_type"):
            return normalize_evidence_type(final["primary_evidence_type"])
        llm_item = rev_node.get("llm_item")
        if isinstance(llm_item, dict) and llm_item.get("primary_evidence_type"):
            return normalize_evidence_type(llm_item["primary_evidence_type"])
    llm = artifact.get("llm_output") or {}
    return normalize_evidence_type(
        source_evidence_profile_from_llm(llm).get("primary_evidence_type")
    )


def proposal_evidence_override_raw(llm_item: dict[str, Any]) -> str | None:
    """Return stored override if present and valid, else ``None`` (inherit source)."""
    if "evidence_type" not in llm_item:
        return None
    raw = llm_item.get("evidence_type")
    if raw is None:
        return None
    norm = normalize_evidence_type(raw)
    return norm if norm in EVIDENCE_TYPE_SET else None


def effective_proposal_evidence_type(
    source_primary: str,
    llm_item: dict[str, Any],
) -> str:
    """Resolved evidence type for a proposal (override or source default)."""
    override = proposal_evidence_override_raw(llm_item)
    if override is not None and override != source_primary:
        return override
    return source_primary


def proposal_evidence_subtitle_part(
    artifact: dict[str, Any],
    llm_item: dict[str, Any],
) -> str:
    """Subtitle fragment: empty when inheriting; label when overridden."""
    primary = source_primary_evidence_type(artifact)
    override = proposal_evidence_override_raw(llm_item)
    if override is None or override == primary:
        return ""
    label = override.replace("_", " ").title()
    return f"Override: {label}"


def compact_proposal_evidence_types(llm: dict[str, Any], primary: str) -> None:
    """Drop per-proposal ``evidence_type`` when it matches *primary* (in place)."""
    for item in _iter_proposal_dicts(llm):
        if "evidence_type" not in item:
            continue
        norm = normalize_evidence_type(item.get("evidence_type"))
        if norm == primary or norm == "unknown":
            item.pop("evidence_type", None)


def compact_evidence_in_llm_dict(llm: dict[str, Any]) -> dict[str, Any]:
    """Ensure profile exists and strip redundant per-proposal evidence types."""
    profile = source_evidence_profile_from_llm(llm)
    llm["source_evidence_profile"] = profile
    primary = normalize_evidence_type(profile["primary_evidence_type"])
    compact_proposal_evidence_types(llm, primary)
    return llm


def apply_evidence_hierarchy(parsed: LlmClassificationOutput) -> LlmClassificationOutput:
    """Normalize source profile and compact per-proposal evidence overrides."""
    llm_dict = parsed.model_dump(mode="json")
    compact_evidence_in_llm_dict(llm_dict)
    return LlmClassificationOutput.model_validate(llm_dict)


def collect_effective_evidence_counts(artifact: dict[str, Any]) -> dict[str, int]:
    """Count resolved evidence types across all proposals."""
    primary = source_primary_evidence_type(artifact)
    counts: dict[str, int] = {primary: 0}
    review = artifact.get("review") or {}
    for key in ENTITY_LLM_KEYS:
        nodes = review.get(key) or []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            lit = node.get("llm_item")
            if not isinstance(lit, dict):
                continue
            et = effective_proposal_evidence_type(primary, lit)
            counts[et] = counts.get(et, 0) + 1
    return counts
