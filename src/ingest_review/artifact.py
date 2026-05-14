"""Merge LLM output with review state; load/save review JSON artifacts."""

from __future__ import annotations

import copy
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
    SOURCE_SUMMARY_SCALAR_KEYS,
    TOPIC_LIST_KEYS,
    TOPIC_SCALAR_KEYS,
    TREND_LIST_KEYS,
    TREND_SCALAR_KEYS,
    LlmClassificationOutput,
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
        "status": "pending",
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
                "notes": None,
                "llm_item": copy.deepcopy(item),
                "sections": sections,
                "tags": {
                    "approved_allowlist_tags": [],
                    "reviewer_tags_added": [],
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
                "notes": None,
                "llm_item": copy.deepcopy(item),
                "sections": g_sections,
                "tags": {
                    "approved_allowlist_tags": [],
                    "reviewer_tags_added": [],
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
                    "notes": None,
                    "llm_item": copy.deepcopy(item),
                    "sections": sections,
                    "tags": {
                        "approved_allowlist_tags": [],
                        "reviewer_tags_added": [],
                    },
                }
            )
        return result

    topics_review = build_per_section(llm.get("topics") or [], TOPIC_SCALAR_KEYS, TOPIC_LIST_KEYS)
    howto_review = build_per_section(llm.get("how_to") or [], HOWTO_SCALAR_KEYS, HOWTO_LIST_KEYS)
    trends_review = build_per_section(
        llm.get("industry_trends") or [], TREND_SCALAR_KEYS, TREND_LIST_KEYS
    )

    roundup = llm.get("roundup") or {}
    return {
        "source_summary": review_summary,
        "glossary": glossary_review,
        "tools": wrap_list(llm.get("tools") or [], "tools"),
        "foundation_models": wrap_list(llm.get("foundation_models") or [], "foundation_models"),
        "how_to": howto_review,
        "topics": topics_review,
        "implementation_studies": impl_review,
        "industry_trends": trends_review,
        "roundup": {
            "status": "pending",
            "notes": None,
            "llm_item": copy.deepcopy(roundup),
            "final_item": None,
        },
    }


def rel_from_repo(path: Path, root: Path) -> str:
    """Return POSIX path relative to repo root, or absolute if outside."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


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
            "publication": doc.frontmatter.get("publication"),
            "published_date": doc.published_date,
        },
        "analysis_meta": analysis_meta,
        "llm_output": llm_dict,
        "review": default_review_for_llm_output(llm_dict),
        "review_session": {"last_saved_at": None, "saved_by": None},
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


def migrate_llm_source_summary_dict(ss: dict[str, Any]) -> dict[str, Any]:
    """Map legacy ``source_summary`` keys into v2 field names."""
    if not isinstance(ss, dict):
        return {}
    out = dict(ss)
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
    out["practical_relevance"] = str(out.get("practical_relevance") or "").strip()
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
    if ver >= ARTIFACT_SCHEMA_VERSION:
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

    artifact["artifact_schema_version"] = ARTIFACT_SCHEMA_VERSION
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


def load_artifact(path: Path) -> dict[str, Any] | None:
    """Load artifact JSON or return None if missing."""
    if not path.is_file():
        return None
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    data = migrate_artifact_to_v2(data)
    data = migrate_artifact_to_v3(data)
    return migrate_artifact_to_v4(data)


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
    for _k, v in ss.items():
        if isinstance(v, dict) and "status" in v:
            collect(str(v["status"]))
    roundup = review.get("roundup")
    if isinstance(roundup, dict) and "status" in roundup:
        collect(str(roundup["status"]))
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
    for key in (
        "tools",
        "foundation_models",
    ):
        for item in review.get(key) or []:
            if isinstance(item, dict) and "status" in item:
                collect(str(item["status"]))
    for per_section_key in ("topics", "how_to", "industry_trends"):
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
