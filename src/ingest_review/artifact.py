"""Merge LLM output with review state; load/save review JSON artifacts."""

from __future__ import annotations

import copy
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.ingest_review.evidence import (
    compact_evidence_in_llm_dict,
    source_evidence_profile_from_llm,
)
from src.ingest_review.extract import SourceDocument
from src.ingest_review.paths import repo_root
from src.ingest_review.schema import (
    ARTIFACT_SCHEMA_VERSION,
    GLOSSARY_LIST_KEYS,
    GLOSSARY_SCALAR_KEYS,
    HOWTO_LIST_KEYS,
    HOWTO_SCALAR_KEYS,
    IMPL_STUDY_LIST_KEYS,
    IMPL_STUDY_SCALAR_KEYS,
    INSIGHT_LIST_KEYS,
    INSIGHT_SCALAR_KEYS,
    MODEL_LIST_KEYS,
    MODEL_SCALAR_KEYS,
    SIGNAL_LIST_KEYS,
    SIGNAL_SCALAR_KEYS,
    SOURCE_SUMMARY_SCALAR_KEYS,
    TOOL_LIST_KEYS,
    TOOL_SCALAR_KEYS,
    TOPIC_LIST_KEYS,
    TOPIC_SCALAR_KEYS,
    TREND_LIST_KEYS,
    TREND_SCALAR_KEYS,
    LlmClassificationOutput,
    normalize_evidence_type,
)
from src.ingest_review.source_regen import apply_regenerated_source_section  # noqa: F401
from src.pipeline.atomic import atomic_write_json


def _utc_now_iso() -> str:
    """Return UTC timestamp without microseconds."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _new_proposal_id() -> str:
    """Return a new UUID string for stable proposal identity."""
    return str(uuid.uuid4())


def _empty_scalar_review_node() -> dict[str, Any]:
    return {
        "status": "pending",
        "final_text": None,
        "notes": None,
        "section_regeneration_meta": None,
    }


def _empty_review_analytics() -> dict[str, Any]:
    return {
        "review_started_at": None,
        "review_finished_at": None,
        "review_duration_seconds": None,
        "proposals_total": 0,
        "proposals_approved": 0,
        "proposals_rejected": 0,
        "proposals_deferred": 0,
        "proposals_modified": 0,
        "fields_modified": 0,
        "batch_actions_used": [],
        "evidence_type_counts": {},
    }


def default_review_for_llm_output(llm: dict[str, Any]) -> dict[str, Any]:
    """Build initial ``review`` subtree with every node ``pending``."""
    summary = llm.get("source_summary") or {}
    review_summary: dict[str, Any] = {}
    for key in SOURCE_SUMMARY_SCALAR_KEYS:
        review_summary[key] = _empty_scalar_review_node()
    insights_list = summary.get("key_insights") or []
    if not isinstance(insights_list, list):
        insights_list = []
    review_summary["key_insights"] = {
        "status": "pending",
        "final_list": None,
        "notes": None,
        "llm_list": copy.deepcopy(insights_list),
        "section_regeneration_meta": None,
    }
    sources_list = summary.get("sources") or []
    review_summary["sources"] = {
        "status": "approved",
        "final_list": None,
        "notes": None,
        "llm_list": copy.deepcopy(sources_list),
        "section_regeneration_meta": None,
    }

    def wrap_list(items: list[Any], _list_key: str) -> list[dict[str, Any]]:
        wrapped: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                item = {}
            entry: dict[str, Any] = {
                "proposal_id": _new_proposal_id(),
                "proposal_status": "approved",
                "status": "pending",
                "notes": None,
                "llm_item": copy.deepcopy(item),
                "final_item": None,
                "reviewer_tags_added": [],
            }
            wrapped.append(entry)
        return wrapped

    impl_studies = llm.get("implementation_studies") or llm.get("enterprise_studies") or []
    impl_review: list[dict[str, Any]] = []
    for item in impl_studies:
        if not isinstance(item, dict):
            item = {}
        sections: dict[str, Any] = {}
        for sk in IMPL_STUDY_SCALAR_KEYS:
            sections[sk] = {
                "status": "pending",
                "final_text": None,
                "notes": None,
            }
        for lk in IMPL_STUDY_LIST_KEYS:
            llm_list_val = item.get(lk) or []
            if not isinstance(llm_list_val, list):
                llm_list_val = []
            sections[lk] = {
                "status": "pending",
                "final_list": None,
                "notes": None,
                "llm_list": copy.deepcopy(llm_list_val),
            }
        impl_review.append(
            {
                "proposal_id": _new_proposal_id(),
                "proposal_status": "approved",
                "notes": None,
                "llm_item": copy.deepcopy(item),
                "sections": sections,
                "tags": {
                    "final_tags": [],
                    "approved_new_tags": [],
                },
            }
        )

    glossary_items = llm.get("glossary") or []
    glossary_review: list[dict[str, Any]] = []
    for item in glossary_items:
        if not isinstance(item, dict):
            item = {}
        g_sections: dict[str, Any] = {}
        for sk in GLOSSARY_SCALAR_KEYS:
            g_sections[sk] = {
                "status": "pending",
                "final_text": None,
                "notes": None,
            }
        for lk in GLOSSARY_LIST_KEYS:
            llm_list_val = item.get(lk) or []
            if not isinstance(llm_list_val, list):
                llm_list_val = []
            g_sections[lk] = {
                "status": "pending",
                "final_list": None,
                "notes": None,
                "llm_list": copy.deepcopy(llm_list_val),
            }
        glossary_review.append(
            {
                "proposal_id": _new_proposal_id(),
                "proposal_status": "approved",
                "notes": None,
                "llm_item": copy.deepcopy(item),
                "sections": g_sections,
                "tags": {
                    "final_tags": [],
                    "approved_new_tags": [],
                },
            }
        )

    def build_per_section(
        items: list[Any],
        scalar_keys: tuple[str, ...],
        list_keys: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                item = {}
            sections: dict[str, Any] = {}
            for sk in scalar_keys:
                sections[sk] = {
                    "status": "pending",
                    "final_text": None,
                    "notes": None,
                }
            for lk in list_keys:
                llm_list_val = item.get(lk) or []
                if not isinstance(llm_list_val, list):
                    llm_list_val = []
                sections[lk] = {
                    "status": "pending",
                    "final_list": None,
                    "notes": None,
                    "llm_list": copy.deepcopy(llm_list_val),
                }
            result.append(
                {
                    "proposal_id": _new_proposal_id(),
                    "proposal_status": "approved",
                    "notes": None,
                    "llm_item": copy.deepcopy(item),
                    "sections": sections,
                    "tags": {
                        "final_tags": [],
                        "approved_new_tags": [],
                    },
                }
            )
        return result

    topics_review = build_per_section(llm.get("topics") or [], TOPIC_SCALAR_KEYS, TOPIC_LIST_KEYS)
    howto_review = build_per_section(llm.get("how_to") or [], HOWTO_SCALAR_KEYS, HOWTO_LIST_KEYS)
    trends_review = build_per_section(
        llm.get("industry_trends") or [], TREND_SCALAR_KEYS, TREND_LIST_KEYS
    )
    tools_review = build_per_section(llm.get("tools") or [], TOOL_SCALAR_KEYS, TOOL_LIST_KEYS)
    models_review = build_per_section(
        llm.get("foundation_models") or [], MODEL_SCALAR_KEYS, MODEL_LIST_KEYS
    )
    signals_review = build_per_section(
        llm.get("roundup_signals") or [], SIGNAL_SCALAR_KEYS, SIGNAL_LIST_KEYS
    )
    insights_review = build_per_section(
        llm.get("interview_insights") or [], INSIGHT_SCALAR_KEYS, INSIGHT_LIST_KEYS
    )

    source_type = llm.get("source_type_detection") or {}
    evidence_profile = source_evidence_profile_from_llm(llm)
    return {
        "source_summary": review_summary,
        "source_type_detection": {
            "status": "pending",
            "notes": None,
            "llm_item": copy.deepcopy(source_type),
            "final_item": None,
        },
        "source_evidence_profile": {
            "status": "pending",
            "notes": None,
            "llm_item": copy.deepcopy(evidence_profile),
            "final_item": None,
        },
        "glossary": glossary_review,
        "tools": tools_review,
        "foundation_models": models_review,
        "how_to": howto_review,
        "topics": topics_review,
        "implementation_studies": impl_review,
        "industry_trends": trends_review,
        "roundup_signals": signals_review,
        "interview_insights": insights_review,
    }


def rel_from_repo(path: Path, root: Path) -> str:
    """Return POSIX path relative to repo root, or absolute if outside."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


ENTITY_REVIEW_LIST_KEYS: tuple[str, ...] = (
    "glossary",
    "topics",
    "how_to",
    "industry_trends",
    "tools",
    "foundation_models",
    "implementation_studies",
    "roundup_signals",
    "interview_insights",
)


def merge_source_summary_into_artifact(
    artifact: dict[str, Any],
    source_summary: dict[str, Any],
) -> None:
    """Replace ``llm_output.source_summary`` and rebuild the review subtree for it."""
    llm = artifact.setdefault("llm_output", {})
    llm["source_summary"] = copy.deepcopy(source_summary)
    fresh_review = default_review_for_llm_output(llm)
    artifact.setdefault("review", {})["source_summary"] = fresh_review["source_summary"]


def merge_entity_proposals_into_artifact(
    artifact: dict[str, Any],
    llm_output: dict[str, Any],
) -> None:
    """Replace entity proposal arrays in ``llm_output`` and matching ``review`` lists."""
    llm = artifact.setdefault("llm_output", {})
    for key in ENTITY_REVIEW_LIST_KEYS:
        if key in llm_output:
            llm[key] = copy.deepcopy(llm_output[key])
    fresh_review = default_review_for_llm_output(llm)
    review = artifact.setdefault("review", {})
    for key in ENTITY_REVIEW_LIST_KEYS:
        review[key] = fresh_review[key]


def build_new_artifact(
    doc: SourceDocument,
    llm_output: LlmClassificationOutput,
    *,
    analysis_meta: dict[str, Any],
    root: Path | None = None,
) -> dict[str, Any]:
    """Assemble a full review artifact dict from a validated LLM output."""
    root = root or repo_root()
    llm_dict = llm_output.model_dump(mode="json")
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "source": {
            "source_id": doc.source_id,
            "raw_html_rel_path": rel_from_repo(doc.raw_html_path, root),
            "raw_md_rel_path": rel_from_repo(doc.raw_md_path, root),
            "content_sha256": doc.content_sha256,
            "canonical_url": doc.canonical_url,
            "title": doc.title,
            "author": doc.author,
            "publication": doc.publication,
            "published_date": doc.published_date,
        },
        "analysis_meta": analysis_meta,
        "llm_output": llm_dict,
        "review": default_review_for_llm_output(llm_dict),
        "review_session": {"last_saved_at": None, "saved_by": None},
        "review_analytics": _empty_review_analytics(),
        "errors": [],
    }


def default_analysis_meta(*, provider: str, model: str, prompt_version: str) -> dict[str, Any]:
    """Build ``analysis_meta`` for a successful analysis run."""
    return {
        "provider": provider,
        "model": model,
        "prompt_version": prompt_version,
        "analysis_timestamp_utc": _utc_now_iso(),
        "request_id": None,
        "token_usage": None,
    }


def review_artifact_path(source_id: str, *, state_reviews: Path | None = None) -> Path:
    """Return path to ``review.json`` for ``source_id``."""
    root = repo_root()
    base = state_reviews if state_reviews is not None else root / "state" / "reviews"
    return base / source_id / "review.json"


def delete_review_artifact(source_id: str, *, state_reviews: Path | None = None) -> bool:
    """Remove on-disk ``review.json`` for *source_id* when present."""
    path = review_artifact_path(source_id, state_reviews=state_reviews)
    if not path.is_file():
        return False
    path.unlink()
    return True


def _concat_why_it_matters_parts(*parts: str) -> str:
    """Join non-empty prose blocks with blank lines."""
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def migrate_llm_source_summary_dict(ss: dict[str, Any]) -> dict[str, Any]:
    """Map legacy ``source_summary`` keys into v2 field names."""
    if not isinstance(ss, dict):
        return {}
    out = dict(ss)
    legacy_impl = str(out.get("implications_automation") or "").strip()
    legacy_practical = str(out.get("practical_relevance") or "").strip()
    legacy_why = str(out.get("why_it_matters") or "").strip()
    if legacy_impl or legacy_practical:
        out["why_it_matters"] = _concat_why_it_matters_parts(
            legacy_why, legacy_impl, legacy_practical
        )
    out.pop("implications_automation", None)
    out.pop("practical_relevance", None)
    out["summary"] = str(out.get("summary") or "").strip()
    ki = out.get("key_insights")
    if isinstance(ki, str):
        lines: list[str] = []
        for ln in ki.splitlines():
            t = ln.strip().lstrip("-•* ").strip()
            if t:
                lines.append(t)
        if not lines and ki.strip():
            lines = [ki.strip()]
        out["key_insights"] = lines[:5]
    elif isinstance(ki, list):
        out["key_insights"] = [str(x).strip() for x in ki if str(x).strip()][:5]
    else:
        out["key_insights"] = []
    lim_new = out.get("limitations_and_open_questions")
    if not (isinstance(lim_new, str) and lim_new.strip()):
        legacy_ctx = out.get("context_limitations")
        out["limitations_and_open_questions"] = (
            str(legacy_ctx).strip() if isinstance(legacy_ctx, str) else ""
        )
    else:
        out["limitations_and_open_questions"] = str(lim_new).strip()
    out.pop("context_limitations", None)
    skep_new = out.get("contradictions_and_skepticism")
    if not (isinstance(skep_new, str) and skep_new.strip()):
        legacy_c = out.get("contradictions")
        out["contradictions_and_skepticism"] = (
            str(legacy_c).strip() if isinstance(legacy_c, str) else ""
        )
    else:
        out["contradictions_and_skepticism"] = str(skep_new).strip()
    out.pop("contradictions", None)
    for sk in SOURCE_SUMMARY_SCALAR_KEYS:
        if sk in ("limitations_and_open_questions", "contradictions_and_skepticism"):
            continue
        val = out.get(sk)
        out[sk] = str(val).strip() if val is not None else ""
    src = out.get("sources")
    if isinstance(src, list):
        out["sources"] = [str(s).strip() for s in src if str(s).strip()]
    else:
        out["sources"] = []
    return out


def _merge_scalar_review(
    fresh: dict[str, Any],
    old_node: dict[str, Any] | None,
    *,
    legacy_final_text: str | None = None,
) -> dict[str, Any]:
    """Prefer preserved reviewer state from ``old_node`` when present."""
    if not isinstance(old_node, dict) or "status" not in old_node:
        if legacy_final_text and legacy_final_text.strip():
            return {
                "status": "modified",
                "final_text": legacy_final_text.strip(),
                "notes": None,
                "section_regeneration_meta": None,
            }
        return dict(fresh)
    merged = dict(fresh)
    merged["status"] = old_node.get("status", fresh["status"])
    merged["final_text"] = old_node.get("final_text")
    merged["notes"] = old_node.get("notes")
    merged["section_regeneration_meta"] = old_node.get("section_regeneration_meta")
    return merged


def _merge_list_review(
    fresh: dict[str, Any],
    old_node: dict[str, Any] | None,
    *,
    legacy_final_text: str | None = None,
) -> dict[str, Any]:
    if not isinstance(old_node, dict) or "status" not in old_node:
        if legacy_final_text and legacy_final_text.strip():
            lines = [ln.strip() for ln in legacy_final_text.splitlines() if ln.strip()]
            return {
                "status": "modified",
                "final_list": lines,
                "notes": None,
                "llm_list": list(fresh["llm_list"]),
                "section_regeneration_meta": None,
            }
        return dict(fresh)
    merged = dict(fresh)
    merged["status"] = old_node.get("status", fresh["status"])
    merged["notes"] = old_node.get("notes")
    merged["section_regeneration_meta"] = old_node.get("section_regeneration_meta")
    if old_node.get("final_list") is not None:
        merged["final_list"] = old_node.get("final_list")
    elif isinstance(old_node.get("final_text"), str) and old_node["final_text"].strip():
        merged["final_list"] = [
            ln.strip() for ln in str(old_node["final_text"]).splitlines() if ln.strip()
        ]
    else:
        merged["final_list"] = old_node.get("final_list")
    merged["llm_list"] = list(fresh["llm_list"])
    return merged


def migrate_artifact_to_v2(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact dict from schema v1 to v2 in place; no-op if already v2+."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 2:
        llm = artifact.get("llm_output") or {}
        ss = llm.get("source_summary")
        if isinstance(ss, dict):
            llm["source_summary"] = migrate_llm_source_summary_dict(ss)
        return artifact
    llm = artifact.setdefault("llm_output", {})
    raw_ss = llm.get("source_summary") or {}
    new_ss = migrate_llm_source_summary_dict(raw_ss if isinstance(raw_ss, dict) else {})
    llm["source_summary"] = new_ss
    old_review_ss = artifact.get("review", {}).get("source_summary") or {}
    if not isinstance(old_review_ss, dict):
        old_review_ss = {}
    fresh_ss = default_review_for_llm_output(llm)["source_summary"]
    merged_ss: dict[str, Any] = {}
    for key in SOURCE_SUMMARY_SCALAR_KEYS:
        legacy_ft: str | None = None
        if key == "limitations_and_open_questions":
            old_node = old_review_ss.get("limitations_and_open_questions") or old_review_ss.get(
                "context_limitations"
            )
        elif key == "contradictions_and_skepticism":
            old_node = old_review_ss.get("contradictions_and_skepticism") or old_review_ss.get(
                "contradictions"
            )
        else:
            old_node = old_review_ss.get(key)
        if isinstance(old_node, dict):
            legacy_ft = (
                old_node.get("final_text") if isinstance(old_node.get("final_text"), str) else None
            )
        merged_ss[key] = _merge_scalar_review(fresh_ss[key], old_node, legacy_final_text=legacy_ft)
    merged_ss["key_insights"] = _merge_list_review(
        fresh_ss["key_insights"],
        old_review_ss.get("key_insights")
        if isinstance(old_review_ss.get("key_insights"), dict)
        else None,
        legacy_final_text=(
            str(old_review_ss["key_insights"]["final_text"])
            if isinstance(old_review_ss.get("key_insights"), dict)
            and isinstance(old_review_ss["key_insights"].get("final_text"), str)
            else None
        ),
    )
    merged_ss["sources"] = _merge_list_review(
        fresh_ss["sources"],
        old_review_ss.get("sources") if isinstance(old_review_ss.get("sources"), dict) else None,
    )
    artifact.setdefault("review", {})["source_summary"] = merged_ss
    artifact["artifact_schema_version"] = 2
    return artifact


def migrate_artifact_to_v3(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact from v2 to v3: rename enterprise_studies -> implementation_studies.

    Rebuilds per-section review nodes for implementation studies.
    """
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 3:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})

    if "enterprise_studies" in llm and "implementation_studies" not in llm:
        llm["implementation_studies"] = llm.pop("enterprise_studies")
    llm.pop("enterprise_studies", None)

    had_old_enterprise = "enterprise_studies" in review
    review.pop("enterprise_studies", None)

    needs_rebuild = False
    if had_old_enterprise or "implementation_studies" not in review:
        needs_rebuild = True
    else:
        items = review.get("implementation_studies") or []
        if isinstance(items, list) and items and isinstance(items[0], dict):
            if "sections" not in items[0] and "status" in items[0]:
                needs_rebuild = True

    if needs_rebuild:
        fresh = default_review_for_llm_output(llm)
        review["implementation_studies"] = fresh.get("implementation_studies", [])

    _migrate_glossary_to_per_section(llm, review)

    artifact["artifact_schema_version"] = 3
    return artifact


def _migrate_glossary_to_per_section(
    llm: dict[str, Any],
    review: dict[str, Any],
) -> None:
    """Upgrade glossary review nodes from flat wrap_list to per-section format."""
    glossary_nodes = review.get("glossary") or []
    if not isinstance(glossary_nodes, list) or not glossary_nodes:
        fresh = default_review_for_llm_output(llm)
        review["glossary"] = fresh.get("glossary", [])
        return
    first = glossary_nodes[0]
    if isinstance(first, dict) and "sections" in first:
        return
    if isinstance(first, dict) and "status" in first and "sections" not in first:
        fresh = default_review_for_llm_output(llm)
        review["glossary"] = fresh.get("glossary", [])


def _migrate_flat_to_per_section(
    llm: dict[str, Any],
    review: dict[str, Any],
    review_key: str,
    llm_key: str,
    scalar_keys: tuple[str, ...],
    list_keys: tuple[str, ...],
) -> None:
    """Convert flat wrap_list review nodes to per-section format for a given type."""
    nodes = review.get(review_key) or []
    if not isinstance(nodes, list) or not nodes:
        fresh = default_review_for_llm_output(llm)
        review[review_key] = fresh.get(review_key, [])
        return
    first = nodes[0]
    if isinstance(first, dict) and "sections" in first:
        return
    if isinstance(first, dict) and "status" in first and "sections" not in first:
        fresh = default_review_for_llm_output(llm)
        review[review_key] = fresh.get(review_key, [])


def migrate_artifact_to_v4(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact from v3 to v4: per-section for howto/trends, add topics."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 4:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})

    _migrate_flat_to_per_section(
        llm, review, "how_to", "how_to", HOWTO_SCALAR_KEYS, HOWTO_LIST_KEYS
    )
    _migrate_flat_to_per_section(
        llm, review, "industry_trends", "industry_trends", TREND_SCALAR_KEYS, TREND_LIST_KEYS
    )

    if "topics" not in review:
        fresh = default_review_for_llm_output(llm)
        review["topics"] = fresh.get("topics", [])

    artifact["artifact_schema_version"] = 4
    return artifact


def migrate_artifact_to_v5(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact from v4 to v5: per-section tools, proposed_tags → proposed_types."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 5:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})

    for tool_item in llm.get("tools") or []:
        if not isinstance(tool_item, dict):
            continue
        if "proposed_tags" in tool_item and "proposed_types" not in tool_item:
            tool_item["proposed_types"] = tool_item.pop("proposed_tags")
        if "tool_type" in tool_item and "proposed_types" not in tool_item:
            old_type = tool_item.pop("tool_type")
            tool_item["proposed_types"] = [old_type] if old_type else []

    _migrate_flat_to_per_section(llm, review, "tools", "tools", TOOL_SCALAR_KEYS, TOOL_LIST_KEYS)

    artifact["artifact_schema_version"] = 5
    return artifact


def migrate_artifact_to_v6(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact from v5 to v6: per-section foundation_models, enriched schema."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 6:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})

    _migrate_flat_to_per_section(
        llm,
        review,
        "foundation_models",
        "foundation_models",
        MODEL_SCALAR_KEYS,
        MODEL_LIST_KEYS,
    )

    artifact["artifact_schema_version"] = 6
    return artifact


def migrate_artifact_to_v7(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact from v6 to v7: replace roundup with source_type_detection.

    Converts old ``RoundupDetection`` (``is_roundup`` boolean) into
    ``SourceTypeDetection`` and initialises empty ``roundup_signals`` /
    ``interview_insights`` arrays.
    """
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 7:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})

    old_roundup = llm.pop("roundup", None) or {}
    if "source_type_detection" not in llm:
        detected = "unknown"
        if isinstance(old_roundup, dict) and old_roundup.get("is_roundup"):
            detected = "ai_industry_roundup"
        reasoning_raw = old_roundup.get("reasoning", "") if isinstance(old_roundup, dict) else ""
        reasoning_list = [reasoning_raw] if reasoning_raw else []
        llm["source_type_detection"] = {
            "detected_source_type": detected,
            "confidence": old_roundup.get("confidence", 0.0)
            if isinstance(old_roundup, dict)
            else 0.0,
            "reasoning": reasoning_list,
        }

    llm.setdefault("roundup_signals", [])
    llm.setdefault("interview_insights", [])

    old_roundup_review = review.pop("roundup", None)
    if "source_type_detection" not in review:
        review["source_type_detection"] = {
            "status": old_roundup_review.get("status", "pending")
            if isinstance(old_roundup_review, dict)
            else "pending",
            "notes": old_roundup_review.get("notes")
            if isinstance(old_roundup_review, dict)
            else None,
            "llm_item": copy.deepcopy(llm["source_type_detection"]),
            "final_item": None,
        }

    if "roundup_signals" not in review:
        fresh = default_review_for_llm_output(llm)
        review["roundup_signals"] = fresh.get("roundup_signals", [])
    if "interview_insights" not in review:
        fresh = default_review_for_llm_output(llm)
        review["interview_insights"] = fresh.get("interview_insights", [])

    artifact["artifact_schema_version"] = 7
    return artifact


_ENTITY_REVIEW_KEYS = (
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


def migrate_artifact_to_v8(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v8: add proposal_status, review_analytics, extraction_meta."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 8:
        return artifact

    review = artifact.setdefault("review", {})
    for entity_key in _ENTITY_REVIEW_KEYS:
        nodes = review.get(entity_key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if "proposal_status" not in node:
                node["proposal_status"] = "pending"
            tags = node.get("tags")
            if isinstance(tags, dict) and "approved_allowlist_tags" in tags:
                tags.clear()
                tags["final_primary_tag"] = None
                tags["final_secondary_tag"] = None
                tags["new_tag_approved"] = False

    llm = artifact.setdefault("llm_output", {})
    if "extraction_meta" not in llm:
        llm["extraction_meta"] = {
            "skip_recommended": False,
            "skip_reason": "",
            "total_candidates_considered": 0,
            "review_burden_estimate": "moderate",
        }

    if "review_analytics" not in artifact:
        artifact["review_analytics"] = _empty_review_analytics()

    artifact["artifact_schema_version"] = 8
    return artifact


def _merge_review_statuses(statuses: list[str]) -> str:
    """Pick the most advanced review status from legacy section nodes."""
    if not statuses:
        return "pending"
    if "modified" in statuses:
        return "modified"
    if "rejected" in statuses:
        return "rejected"
    if all(s == "approved" for s in statuses):
        return "approved"
    if "approved" in statuses:
        return "modified"
    return "pending"


def migrate_review_source_summary_unified_why(artifact: dict[str, Any]) -> dict[str, Any]:
    """Merge legacy automation/relevance review nodes into why_it_matters."""
    review = artifact.setdefault("review", {})
    rev_ss = review.get("source_summary")
    if not isinstance(rev_ss, dict):
        return artifact
    legacy_keys = ("implications_automation", "practical_relevance")
    if not any(k in rev_ss for k in legacy_keys):
        return artifact

    llm_raw = (artifact.get("llm_output") or {}).get("source_summary") or {}
    llm_ss = migrate_llm_source_summary_dict(llm_raw if isinstance(llm_raw, dict) else {})

    def _text_for(key: str) -> str:
        node = rev_ss.get(key)
        if isinstance(node, dict):
            ft = node.get("final_text")
            if isinstance(ft, str) and ft.strip():
                return ft.strip()
        return str(llm_ss.get(key) or "").strip()

    legacy_why_key = "why_it_matters"
    parts = [_text_for(legacy_why_key)]
    for lk in legacy_keys:
        parts.append(_text_for(lk))
    merged_text = _concat_why_it_matters_parts(*parts)

    statuses: list[str] = []
    notes_parts: list[str] = []
    regen_meta = None
    for key in (legacy_why_key, *legacy_keys):
        node = rev_ss.get(key)
        if isinstance(node, dict):
            statuses.append(str(node.get("status") or "pending"))
            n = node.get("notes")
            if isinstance(n, str) and n.strip():
                notes_parts.append(n.strip())
            if regen_meta is None and node.get("section_regeneration_meta"):
                regen_meta = node.get("section_regeneration_meta")

    had_final = any(
        isinstance(rev_ss.get(k), dict) and rev_ss.get(k, {}).get("final_text")
        for k in (legacy_why_key, *legacy_keys)
    )
    why_node = rev_ss.get(legacy_why_key) if isinstance(rev_ss.get(legacy_why_key), dict) else {}

    rev_ss[legacy_why_key] = {
        "status": _merge_review_statuses(statuses),
        "final_text": merged_text if had_final else why_node.get("final_text"),
        "notes": "\n".join(notes_parts) if notes_parts else why_node.get("notes"),
        "section_regeneration_meta": regen_meta,
    }
    for lk in legacy_keys:
        rev_ss.pop(lk, None)
    return artifact


def migrate_artifact_to_v9(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v9: evidence_type on proposal dicts (default unknown)."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 9:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    for entity_key in _ENTITY_REVIEW_KEYS:
        items = llm.get(entity_key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item["evidence_type"] = normalize_evidence_type(item.get("evidence_type"))

    review = artifact.setdefault("review", {})
    for entity_key in _ENTITY_REVIEW_KEYS:
        nodes = review.get(entity_key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            lit = node.get("llm_item")
            if isinstance(lit, dict):
                lit["evidence_type"] = normalize_evidence_type(lit.get("evidence_type"))

    analytics = artifact.setdefault("review_analytics", _empty_review_analytics())
    if "evidence_type_counts" not in analytics:
        analytics["evidence_type_counts"] = {}

    artifact["artifact_schema_version"] = 9
    return artifact


def migrate_artifact_to_v10(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v10: optional ``examples`` on topic contributions and review sections."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 10:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    topics = llm.get("topics")
    if isinstance(topics, list):
        for item in topics:
            if isinstance(item, dict) and "examples" not in item:
                item["examples"] = ""

    review = artifact.setdefault("review", {})
    topic_nodes = review.get("topics")
    if isinstance(topic_nodes, list):
        empty_scalar = _empty_scalar_review_node()
        for node in topic_nodes:
            if not isinstance(node, dict):
                continue
            lit = node.get("llm_item")
            if isinstance(lit, dict) and "examples" not in lit:
                lit["examples"] = ""
            sections = node.get("sections")
            if not isinstance(sections, dict):
                continue
            if "examples" not in sections:
                sections["examples"] = {**empty_scalar}

    artifact["artifact_schema_version"] = 10
    return artifact


def migrate_artifact_to_v11(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v11: default-approved proposals (pending → approved)."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 11:
        return artifact

    review = artifact.setdefault("review", {})
    for entity_key in _ENTITY_REVIEW_KEYS:
        nodes = review.get(entity_key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if node.get("proposal_status") == "pending":
                node["proposal_status"] = "approved"

    artifact["artifact_schema_version"] = 11
    return artifact


def _migrate_howto_relevance_to_what_and_problem(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
) -> None:
    """Move legacy relevance_note into what_and_problem on one how-to node."""
    rel_text = ""
    if isinstance(llm_item.get("relevance_note"), str):
        rel_text = str(llm_item.pop("relevance_note")).strip()
    what = str(llm_item.get("what_and_problem") or "").strip()
    if not what and rel_text:
        llm_item["what_and_problem"] = rel_text

    rel_sec = sections.pop("relevance_note", None)
    what_sec = sections.get("what_and_problem")
    if not isinstance(what_sec, dict):
        what_sec = {**_empty_scalar_review_node()}
        sections["what_and_problem"] = what_sec

    if isinstance(rel_sec, dict):
        rel_final = rel_sec.get("final_text")
        if isinstance(rel_final, str) and rel_final.strip():
            existing_final = what_sec.get("final_text")
            if not (isinstance(existing_final, str) and existing_final.strip()):
                what_sec["final_text"] = rel_final.strip()
                what_sec["status"] = rel_sec.get("status") or what_sec.get("status") or "pending"


def migrate_artifact_to_v12(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v12: how_to relevance_note → what_and_problem."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 12:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})
    howto_llm = llm.get("how_to") or []
    howto_review = review.get("how_to") or []

    if isinstance(howto_llm, list):
        for item in howto_llm:
            if isinstance(item, dict):
                _migrate_howto_relevance_to_what_and_problem(item, {})

    if isinstance(howto_review, list):
        for node in howto_review:
            if not isinstance(node, dict):
                continue
            _migrate_howto_relevance_to_what_and_problem(
                node.setdefault("llm_item", {}),
                node.setdefault("sections", {}),
            )

    artifact["artifact_schema_version"] = 12
    return artifact


def _looks_like_kebab_slug(value: str) -> bool:
    s = value.strip()
    if not s or " " in s:
        return False
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s))


def _title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").split()
    return " ".join(w.capitalize() for w in words) if words else slug


def _migrate_trend_name_to_slug_and_title(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
) -> None:
    """Split legacy trend_name into trend_slug + trend_title."""
    from src.pipeline.slug import slugify

    old_raw = llm_item.pop("trend_name", None)
    old = str(old_raw).strip() if old_raw is not None else ""
    slug = str(llm_item.get("trend_slug") or "").strip()
    title = str(llm_item.get("trend_title") or "").strip()

    if old and not slug and not title:
        if _looks_like_kebab_slug(old):
            slug = old
            title = _title_from_slug(old)
        else:
            title = old
            slug = slugify(old)

    if slug and not title:
        title = _title_from_slug(slug)
    if title and not slug:
        slug = slugify(title)

    if slug:
        llm_item["trend_slug"] = slug
    if title:
        llm_item["trend_title"] = title

    name_sec = sections.pop("trend_name", None)
    if not isinstance(name_sec, dict):
        return

    empty = _empty_scalar_review_node()
    slug_sec = sections.get("trend_slug")
    if not isinstance(slug_sec, dict):
        slug_sec = {**empty}
        sections["trend_slug"] = slug_sec
    title_sec = sections.get("trend_title")
    if not isinstance(title_sec, dict):
        title_sec = {**empty}
        sections["trend_title"] = title_sec

    final = name_sec.get("final_text")
    if not isinstance(final, str) or not final.strip():
        return
    final = final.strip()
    status = name_sec.get("status") or "pending"
    slug_final = slug_sec.get("final_text")
    title_final = title_sec.get("final_text")
    slug_has_final = isinstance(slug_final, str) and slug_final.strip()
    title_has_final = isinstance(title_final, str) and title_final.strip()
    if _looks_like_kebab_slug(final):
        if not slug_has_final:
            slug_sec["final_text"] = final
            slug_sec["status"] = status
        if not title_has_final:
            title_sec["final_text"] = _title_from_slug(final)
            title_sec["status"] = status
    else:
        if not title_has_final:
            title_sec["final_text"] = final
            title_sec["status"] = status
        if not slug_has_final:
            slug_sec["final_text"] = slugify(final)
            slug_sec["status"] = status


def migrate_artifact_to_v13(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v13: trend_name → trend_slug + trend_title."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 13:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    review = artifact.setdefault("review", {})
    trend_llm = llm.get("industry_trends") or []
    trend_review = review.get("industry_trends") or []

    if isinstance(trend_llm, list):
        for item in trend_llm:
            if isinstance(item, dict):
                _migrate_trend_name_to_slug_and_title(item, {})

    if isinstance(trend_review, list):
        for node in trend_review:
            if not isinstance(node, dict):
                continue
            _migrate_trend_name_to_slug_and_title(
                node.setdefault("llm_item", {}),
                node.setdefault("sections", {}),
            )

    artifact["artifact_schema_version"] = 13
    return artifact


def _migrate_node_tags_to_multitag(node: dict[str, Any]) -> None:
    """In-place: primary/secondary → final_tags / proposed_tags lists."""
    from src.ingest_review.tags import normalize_tag

    llm_item = node.get("llm_item")
    if not isinstance(llm_item, dict):
        llm_item = {}
        node["llm_item"] = llm_item

    tag_node = node.get("tags")
    if not isinstance(tag_node, dict):
        tag_node = {}
        node["tags"] = tag_node

    final_legacy: list[str] = []
    for key in ("final_primary_tag", "final_secondary_tag"):
        t = normalize_tag(str(tag_node.get(key) or ""))
        if t and t not in final_legacy:
            final_legacy.append(t)
    if "final_tags" not in tag_node or not tag_node.get("final_tags"):
        tag_node["final_tags"] = final_legacy

    proposed_legacy: list[str] = []
    for key in ("primary_tag", "secondary_tag"):
        t = normalize_tag(str(llm_item.get(key) or ""))
        if t and t not in proposed_legacy:
            proposed_legacy.append(t)
    if "proposed_tags" not in llm_item or not llm_item.get("proposed_tags"):
        llm_item["proposed_tags"] = proposed_legacy

    sn = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
    snt = llm_item.get("suggested_new_tags")
    if not isinstance(snt, list) or not snt:
        llm_item["suggested_new_tags"] = [sn] if sn else []
    if tag_node.get("new_tag_approved") and sn:
        existing = tag_node.get("approved_new_tags")
        if not isinstance(existing, list) or not existing:
            tag_node["approved_new_tags"] = [sn]
    elif "approved_new_tags" not in tag_node:
        tag_node["approved_new_tags"] = []


def migrate_artifact_to_v14(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v14: multi-tag routing (final_tags / proposed_tags)."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 14:
        return artifact

    review = artifact.setdefault("review", {})
    tag_entity_keys = (
        "glossary",
        "topics",
        "how_to",
        "industry_trends",
        "implementation_studies",
        "roundup_signals",
        "interview_insights",
    )
    for key in tag_entity_keys:
        for node in review.get(key) or []:
            if isinstance(node, dict):
                _migrate_node_tags_to_multitag(node)

    llm = artifact.setdefault("llm_output", {})
    for llm_key in tag_entity_keys:
        for item in llm.get(llm_key) or []:
            if not isinstance(item, dict):
                continue
            proposed: list[str] = []
            for pk in ("primary_tag", "secondary_tag"):
                t = str(item.get(pk) or "").strip()
                if t:
                    from src.ingest_review.tags import normalize_tag

                    nt = normalize_tag(t)
                    if nt and nt not in proposed:
                        proposed.append(nt)
            if proposed and not item.get("proposed_tags"):
                item["proposed_tags"] = proposed
            sn = str(item.get("suggested_new_tag") or "").strip()
            if sn and not item.get("suggested_new_tags"):
                from src.ingest_review.tags import normalize_tag

                item["suggested_new_tags"] = [normalize_tag(sn)]

    artifact["artifact_schema_version"] = 14
    return artifact


_ENTITY_LLM_KEYS_V15: tuple[str, ...] = (
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


def _join_nonempty_text_parts(parts: list[str], *, separator: str = "\n\n") -> str:
    """Join stripped non-empty strings for field consolidation migrations."""
    cleaned = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
    return separator.join(cleaned)


def _section_final_text(sections: dict[str, Any], key: str) -> str:
    """Return reviewer-final text for a scalar section key, if any."""
    sec = sections.get(key)
    if not isinstance(sec, dict):
        return ""
    final = sec.get("final_text")
    return final.strip() if isinstance(final, str) and final.strip() else ""


def _migrate_foundation_model_llm_fields(item: dict[str, Any]) -> None:
    """Collapse legacy model prose fields into operational_profile / deployment_implications."""
    if not isinstance(item, dict):
        return
    has_legacy = any(
        k in item for k in ("operational_summary", "strengths", "workflow_implications")
    )
    if not has_legacy and "operational_profile" in item:
        return

    profile_parts = [
        str(item.get("operational_profile") or "").strip(),
        str(item.pop("operational_summary", "") or "").strip(),
        str(item.pop("strengths", "") or "").strip(),
    ]
    item["operational_profile"] = _join_nonempty_text_parts(profile_parts)

    deploy_parts = [
        str(item.get("deployment_implications") or "").strip(),
        str(item.pop("workflow_implications", "") or "").strip(),
    ]
    item["deployment_implications"] = _join_nonempty_text_parts(deploy_parts)


def _migrate_foundation_model_review_sections(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
) -> None:
    """Rename and merge per-section review nodes for foundation model field compression."""
    if not isinstance(sections, dict):
        return

    profile_parts = [
        _section_final_text(sections, "operational_profile"),
        _section_final_text(sections, "operational_summary"),
        _section_final_text(sections, "strengths"),
    ]
    deploy_parts = [
        _section_final_text(sections, "deployment_implications"),
        _section_final_text(sections, "workflow_implications"),
    ]

    for old_key in (
        "operational_summary",
        "strengths",
        "workflow_implications",
    ):
        sections.pop(old_key, None)

    if isinstance(llm_item, dict):
        item_profile = str(llm_item.get("operational_profile") or "").strip()
        item_deploy = str(llm_item.get("deployment_implications") or "").strip()
        if item_profile and item_profile not in profile_parts:
            profile_parts.insert(0, item_profile)
        if item_deploy and item_deploy not in deploy_parts:
            deploy_parts.insert(0, item_deploy)

    merged_profile = _join_nonempty_text_parts(profile_parts)
    merged_deploy = _join_nonempty_text_parts(deploy_parts)

    if merged_profile:
        prof_sec = sections.setdefault("operational_profile", _empty_scalar_review_node())
        if isinstance(prof_sec, dict):
            prof_sec["final_text"] = merged_profile
            prof_sec["status"] = "modified"
    else:
        sections.setdefault("operational_profile", _empty_scalar_review_node())

    if merged_deploy:
        dep_sec = sections.setdefault("deployment_implications", _empty_scalar_review_node())
        if isinstance(dep_sec, dict):
            dep_sec["final_text"] = merged_deploy
            dep_sec["status"] = "modified"
    else:
        sections.setdefault("deployment_implications", _empty_scalar_review_node())

    for sk in MODEL_SCALAR_KEYS:
        if sk not in sections:
            sections[sk] = _empty_scalar_review_node()


def migrate_artifact_to_v16(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v16: compress foundation model prose fields."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 16:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    models = llm.get("foundation_models")
    if isinstance(models, list):
        for item in models:
            _migrate_foundation_model_llm_fields(item)

    review = artifact.setdefault("review", {})
    nodes = review.get("foundation_models")
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            llm_item = node.get("llm_item")
            if isinstance(llm_item, dict):
                _migrate_foundation_model_llm_fields(llm_item)
            sections = node.get("sections")
            if isinstance(sections, dict) and isinstance(llm_item, dict):
                _migrate_foundation_model_review_sections(sections, llm_item)

    artifact["artifact_schema_version"] = 16
    return artifact


def _ensure_proposal_tags_node(node: dict[str, Any]) -> None:
    """Ensure review node has a ``tags`` subtree for retrieval-tag UI."""
    tags = node.get("tags")
    if not isinstance(tags, dict):
        node["tags"] = {"final_tags": [], "approved_new_tags": []}
        return
    tags.setdefault("final_tags", [])
    tags.setdefault("approved_new_tags", [])


def migrate_artifact_to_v17(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v17: tool/model retrieval tags on proposals."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 17:
        return artifact

    review = artifact.setdefault("review", {})
    for key in ("tools", "foundation_models"):
        nodes = review.get(key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if isinstance(node, dict):
                _ensure_proposal_tags_node(node)

    llm = artifact.setdefault("llm_output", {})
    for key in ("tools", "foundation_models"):
        items = llm.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            item.setdefault("proposed_tags", [])
            item.setdefault("suggested_new_tags", [])

    artifact["artifact_schema_version"] = 17
    return artifact


def migrate_artifact_to_v15(artifact: dict[str, Any]) -> dict[str, Any]:
    """Upgrade artifact to v15: source_evidence_profile; compact per-proposal evidence_type."""
    ver = int(artifact.get("artifact_schema_version") or 1)
    if ver >= 15:
        return artifact

    llm = artifact.setdefault("llm_output", {})
    compact_evidence_in_llm_dict(llm)

    review = artifact.setdefault("review", {})
    profile = llm.get("source_evidence_profile") or {}
    if not isinstance(profile, dict):
        profile = source_evidence_profile_from_llm(llm)
        llm["source_evidence_profile"] = profile

    if "source_evidence_profile" not in review:
        review["source_evidence_profile"] = {
            "status": "pending",
            "notes": None,
            "llm_item": copy.deepcopy(profile),
            "final_item": None,
        }
    else:
        rev_prof = review["source_evidence_profile"]
        if isinstance(rev_prof, dict) and not rev_prof.get("llm_item"):
            rev_prof["llm_item"] = copy.deepcopy(profile)

    for key in _ENTITY_LLM_KEYS_V15:
        nodes = review.get(key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            lit = node.get("llm_item")
            if not isinstance(lit, dict):
                continue
            primary = normalize_evidence_type((profile or {}).get("primary_evidence_type"))
            et = lit.get("evidence_type")
            if et is None:
                continue
            if normalize_evidence_type(et) == primary:
                lit.pop("evidence_type", None)

    artifact["artifact_schema_version"] = 15
    return artifact


def aggregate_impl_study_section_status(sections: dict[str, Any]) -> str:
    """Derive a proposal-level status from per-section review nodes."""
    statuses: set[str] = set()
    for _k, node in sections.items():
        if isinstance(node, dict) and "status" in node:
            statuses.add(str(node["status"]))
    if not statuses:
        return "pending"
    if statuses == {"pending"}:
        return "pending"
    if statuses == {"approved"}:
        return "approved"
    if statuses <= {"approved", "rejected"}:
        return "resolved"
    return "mixed"


def ensure_sources_review_auto_approved(artifact: dict[str, Any]) -> None:
    """Sources links are informational only; mark review node approved in place."""
    rev_ss = (artifact.get("review") or {}).get("source_summary")
    if not isinstance(rev_ss, dict):
        return
    node = rev_ss.get("sources")
    if not isinstance(node, dict):
        return
    node["status"] = "approved"
    node["final_list"] = None


def load_artifact(path: Path) -> dict[str, Any] | None:
    """Load artifact JSON or return None if missing."""
    if not path.is_file():
        return None
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    data = migrate_artifact_to_v2(data)
    data = migrate_artifact_to_v3(data)
    data = migrate_artifact_to_v4(data)
    data = migrate_artifact_to_v5(data)
    data = migrate_artifact_to_v6(data)
    data = migrate_artifact_to_v7(data)
    data = migrate_artifact_to_v8(data)
    data = migrate_artifact_to_v9(data)
    data = migrate_artifact_to_v10(data)
    data = migrate_artifact_to_v11(data)
    data = migrate_artifact_to_v12(data)
    data = migrate_artifact_to_v13(data)
    data = migrate_artifact_to_v14(data)
    data = migrate_artifact_to_v15(data)
    data = migrate_artifact_to_v16(data)
    data = migrate_artifact_to_v17(data)
    data = migrate_review_source_summary_unified_why(data)
    ensure_sources_review_auto_approved(data)
    return data


def save_artifact(path: Path, payload: dict[str, Any]) -> None:
    """Write artifact atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, payload)


def attach_error(artifact: dict[str, Any], message: str) -> None:
    """Append a string to ``errors`` list."""
    errors = artifact.setdefault("errors", [])
    if isinstance(errors, list):
        errors.append(message)


def merge_llm_output_preserving_review(
    artifact: dict[str, Any],
    new_llm: LlmClassificationOutput,
) -> dict[str, Any]:
    """Replace ``llm_output`` and reset ``review`` to match new structure.

    Used when user explicitly overwrites analysis. Review state is rebuilt
    (all pending) — for finer merge, extend later.
    """
    new_dict = new_llm.model_dump(mode="json")
    artifact["llm_output"] = new_dict
    artifact["review"] = default_review_for_llm_output(new_dict)
    return artifact


def backup_artifact(path: Path) -> Path | None:
    """Copy existing artifact to ``review.prev.<timestamp>.json`` sibling."""
    if not path.is_file():
        return None
    import shutil

    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    backup = path.parent / f"review.prev.{stamp}.json"
    shutil.copy2(path, backup)
    return backup


def ensure_review_started(artifact: dict[str, Any]) -> None:
    """Set ``review_analytics.review_started_at`` if the review timer has not run yet."""
    analytics = artifact.setdefault("review_analytics", {})
    started = analytics.get("review_started_at")
    if started is None or not str(started).strip():
        analytics["review_started_at"] = _utc_now_iso()


def touch_review_session(artifact: dict[str, Any]) -> None:
    """Set ``review_session.last_saved_at`` to now."""
    session = artifact.setdefault("review_session", {})
    session["last_saved_at"] = _utc_now_iso()


def filter_tags(tags: list[str], allowlist: set[str]) -> tuple[list[str], list[str]]:
    """Return ``(allowed, stripped_unknown)``."""
    allowed: list[str] = []
    unknown: list[str] = []
    for t in tags:
        if t in allowlist:
            allowed.append(t)
        else:
            unknown.append(t)
    return allowed, unknown


def aggregate_review_status(artifact: dict[str, Any]) -> str:
    """Return a coarse summary: ``mixed``, ``all_pending``, ``all_approved``, etc."""
    review = artifact.get("review") or {}
    statuses: list[str] = []

    def collect(s: str) -> None:
        statuses.append(s)

    ss = review.get("source_summary") or {}
    for key, v in ss.items():
        if key == "sources":
            continue
        if isinstance(v, dict) and "status" in v:
            collect(str(v["status"]))
    src_type = review.get("source_type_detection")
    if isinstance(src_type, dict) and "status" in src_type:
        collect(str(src_type["status"]))
    for glossary_node in review.get("glossary") or []:
        if not isinstance(glossary_node, dict):
            continue
        g_sections = glossary_node.get("sections") or {}
        if g_sections:
            for _gk, gv in g_sections.items():
                if isinstance(gv, dict) and "status" in gv:
                    collect(str(gv["status"]))
        elif "status" in glossary_node:
            collect(str(glossary_node["status"]))
    per_section_keys = (
        "foundation_models",
        "tools",
        "topics",
        "how_to",
        "industry_trends",
        "roundup_signals",
        "interview_insights",
    )
    for per_section_key in per_section_keys:
        for ps_node in review.get(per_section_key) or []:
            if not isinstance(ps_node, dict):
                continue
            ps_sections = ps_node.get("sections") or {}
            if ps_sections:
                for _psk, psv in ps_sections.items():
                    if isinstance(psv, dict) and "status" in psv:
                        collect(str(psv["status"]))
            elif "status" in ps_node:
                collect(str(ps_node["status"]))
    for impl_node in review.get("implementation_studies") or []:
        if not isinstance(impl_node, dict):
            continue
        sections = impl_node.get("sections") or {}
        for _sk, sv in sections.items():
            if isinstance(sv, dict) and "status" in sv:
                collect(str(sv["status"]))
    if not statuses:
        return "empty"
    unique = set(statuses)
    if unique == {"pending"}:
        return "all_pending"
    if unique == {"approved"}:
        return "all_approved"
    if unique <= {"approved", "rejected"}:
        return "resolved_no_mod"
    return "mixed"
