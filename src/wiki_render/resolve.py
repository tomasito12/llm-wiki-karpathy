"""Resolve human-reviewed values without importing Streamlit UI modules."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from src.ingest_review.tags import normalize_tag

TAXONOMY_FILES: tuple[str, ...] = (
    "config/review_tags_topics.yaml",
    "config/review_tags_howto.yaml",
    "config/review_tags_trends.yaml",
    "config/review_tags_glossary.yaml",
    "config/review_tags_impl_study.yaml",
    "config/review_tags_tools.yaml",
    "config/review_tags_models.yaml",
    "config/review_tool_types.yaml",
    "config/review_model_types.yaml",
)


def proposal_is_included(node: dict[str, Any]) -> bool:
    """Return True for non-rejected review proposal nodes."""
    status = str(node.get("proposal_status") or "approved")
    if status == "pending":
        status = "approved"
    return status != "rejected"


def llm_item(node: dict[str, Any]) -> dict[str, Any]:
    """Return the raw proposal item from a review node."""
    raw = node.get("llm_item")
    return raw if isinstance(raw, dict) else {}


def sections(node: dict[str, Any]) -> dict[str, Any]:
    """Return per-field review sections from a review node."""
    raw = node.get("sections")
    return raw if isinstance(raw, dict) else {}


def scalar_value(node: dict[str, Any], key: str) -> str:
    """Return final reviewed scalar text for ``key``."""
    sec = sections(node).get(key)
    if isinstance(sec, dict):
        final = sec.get("final_text")
        if isinstance(final, str) and final.strip():
            return final.strip()
    raw = llm_item(node).get(key)
    return str(raw or "").strip()


def list_value(node: dict[str, Any], key: str) -> list[str]:
    """Return final reviewed list value for ``key``."""
    sec = sections(node).get(key)
    if isinstance(sec, dict):
        final = sec.get("final_list")
        if isinstance(final, list):
            return [str(item).strip() for item in final if str(item).strip()]
        llm_list = sec.get("llm_list")
        if isinstance(llm_list, list) and llm_list:
            return [str(item).strip() for item in llm_list if str(item).strip()]
    raw = llm_item(node).get(key)
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


def reviewed_tags(node: dict[str, Any]) -> list[str]:
    """Return effective retrieval tags from a proposal node."""
    tag_node = node.get("tags")
    result: list[str] = []
    if isinstance(tag_node, dict):
        final_tags = tag_node.get("final_tags")
        if isinstance(final_tags, list):
            result.extend(str(item) for item in final_tags)
        approved_new = tag_node.get("approved_new_tags")
        if isinstance(approved_new, list):
            result.extend(str(item) for item in approved_new)
    if not result:
        raw = llm_item(node)
        proposed = raw.get("proposed_tags")
        if isinstance(proposed, list):
            result.extend(str(item) for item in proposed)
        for key in ("primary_tag", "secondary_tag", "suggested_new_tag"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                result.append(value)
        suggested_new = raw.get("suggested_new_tags")
        if isinstance(suggested_new, list):
            result.extend(str(item) for item in suggested_new)
    return _dedupe_normalized(result)


def reviewed_types(node: dict[str, Any]) -> list[str]:
    """Return effective tool/model type slugs from a proposal node."""
    type_node = node.get("types")
    result: list[str] = []
    if isinstance(type_node, dict):
        for key in ("approved_types", "reviewer_types_added"):
            values = type_node.get(key)
            if isinstance(values, list):
                result.extend(str(item) for item in values)
    if not result:
        proposed = llm_item(node).get("proposed_types")
        if isinstance(proposed, list):
            result.extend(str(item) for item in proposed)
        proposed_new = llm_item(node).get("proposed_new_type")
        if isinstance(proposed_new, str) and proposed_new.strip():
            result.append(proposed_new)
    return _dedupe_normalized(result)


def source_summary_scalar(artifact: dict[str, Any], key: str) -> str:
    """Return final reviewed source summary scalar."""
    review = artifact.get("review") or {}
    node = (review.get("source_summary") or {}).get(key)
    if isinstance(node, dict):
        final = node.get("final_text")
        if isinstance(final, str) and final.strip():
            return final.strip()
    llm = artifact.get("llm_output") or {}
    source_summary = llm.get("source_summary") or {}
    return str(source_summary.get(key) or "").strip()


def source_summary_list(artifact: dict[str, Any], key: str) -> list[str]:
    """Return final reviewed source summary list."""
    review = artifact.get("review") or {}
    node = (review.get("source_summary") or {}).get(key)
    if isinstance(node, dict):
        final = node.get("final_list")
        if isinstance(final, list):
            return [str(item).strip() for item in final if str(item).strip()]
        llm_list = node.get("llm_list")
        if isinstance(llm_list, list) and llm_list:
            return [str(item).strip() for item in llm_list if str(item).strip()]
    llm = artifact.get("llm_output") or {}
    source_summary = llm.get("source_summary") or {}
    raw = source_summary.get(key)
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


def artifact_ingested_at(artifact: dict[str, Any]) -> str:
    """Return deterministic persisted ingestion/review timestamp."""
    analytics = artifact.get("review_analytics") or {}
    finished = analytics.get("review_finished_at")
    if isinstance(finished, str) and finished.strip():
        return finished.strip()
    meta = artifact.get("analysis_meta") or {}
    analyzed = meta.get("analysis_timestamp_utc")
    return str(analyzed or "").strip()


def artifact_assessed_as_of(artifact: dict[str, Any]) -> str:
    """Return source-summary assessed-as-of when available."""
    llm = artifact.get("llm_output") or {}
    source_summary = llm.get("source_summary") or {}
    return str(source_summary.get("assessed_as_of") or "").strip()


def taxonomy_version(root: Path) -> str:
    """Return a deterministic hash of the current review taxonomy files."""
    payload: list[str] = []
    for rel in TAXONOMY_FILES:
        path = root / rel
        payload.append(rel)
        if path.is_file():
            payload.append(path.read_text(encoding="utf-8"))
    return hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()[:12]


def _dedupe_normalized(values: list[str]) -> list[str]:
    """Normalize and dedupe slugs preserving first occurrence order."""
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        normalized = normalize_tag(str(value))
        if normalized and normalized not in seen:
            seen.add(normalized)
            out.append(normalized)
    return out
