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
    LlmClassificationOutput,
)
from src.pipeline.atomic import atomic_write_json


def _utc_now_iso() -> str:
    """Return UTC timestamp without microseconds."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _new_proposal_id() -> str:
    """Return a new UUID string for stable proposal identity."""
    return str(uuid.uuid4())


def default_review_for_llm_output(llm: dict[str, Any]) -> dict[str, Any]:
    """Build initial ``review`` subtree with every node ``pending``."""
    summary = llm.get("source_summary") or {}
    review_summary: dict[str, Any] = {}
    for key in (
        "why_it_matters",
        "key_insights",
        "implications_automation",
        "context_limitations",
        "contradictions",
    ):
        review_summary[key] = {
            "status": "pending",
            "final_text": None,
            "notes": None,
        }
    sources_list = summary.get("sources") or []
    review_summary["sources"] = {
        "status": "pending",
        "final_list": None,
        "notes": None,
        "llm_list": copy.deepcopy(sources_list),
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

    roundup = llm.get("roundup") or {}
    return {
        "source_summary": review_summary,
        "glossary": wrap_list(llm.get("glossary") or [], "glossary"),
        "tools": wrap_list(llm.get("tools") or [], "tools"),
        "foundation_models": wrap_list(llm.get("foundation_models") or [], "foundation_models"),
        "how_to": wrap_list(llm.get("how_to") or [], "how_to"),
        "enterprise_studies": wrap_list(llm.get("enterprise_studies") or [], "enterprise_studies"),
        "industry_trends": wrap_list(llm.get("industry_trends") or [], "industry_trends"),
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


def load_artifact(path: Path) -> dict[str, Any] | None:
    """Load artifact JSON or return None if missing."""
    if not path.is_file():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


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
    for key in (
        "glossary",
        "tools",
        "foundation_models",
        "how_to",
        "enterprise_studies",
        "industry_trends",
    ):
        for item in review.get(key) or []:
            if isinstance(item, dict) and "status" in item:
                collect(str(item["status"]))
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
