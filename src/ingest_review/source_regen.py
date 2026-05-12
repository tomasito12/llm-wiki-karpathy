"""Merge per-chapter LLM regeneration into review artifacts (kept separate from artifact I/O)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.ingest_review.schema import SOURCE_SUMMARY_SCALAR_KEYS


def _utc_now_iso() -> str:
    """Return UTC timestamp without microseconds."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _fresh_scalar_review_node() -> dict[str, Any]:
    return {
        "status": "pending",
        "final_text": None,
        "notes": None,
        "section_regeneration_meta": None,
    }


def apply_regenerated_source_section(
    artifact: dict[str, Any],
    section_key: str,
    content: str | list[str],
    *,
    model: str,
    prompt_version: str,
) -> None:
    """Merge one regenerated chapter into ``llm_output`` and ``review``; sets status pending."""
    utc = _utc_now_iso()
    llm_ss = artifact.setdefault("llm_output", {}).setdefault("source_summary", {})
    rev_ss = artifact.setdefault("review", {}).setdefault("source_summary", {})

    def _bump_regen_meta(node: dict[str, Any]) -> None:
        prev = node.get("section_regeneration_meta")
        count = 0
        if isinstance(prev, dict):
            count = int(prev.get("regen_count") or 0)
        node["section_regeneration_meta"] = {
            "regen_count": count + 1,
            "last_regen_at": utc,
            "model": model,
            "prompt_version": prompt_version,
        }

    if section_key == "key_insights":
        if isinstance(content, str):
            lines = [ln.strip() for ln in content.splitlines() if ln.strip()] or (
                [] if not content.strip() else [content.strip()]
            )
            new_list = lines[:5]
        else:
            new_list = [str(x).strip() for x in content if str(x).strip()][:5]
        llm_ss["key_insights"] = new_list
        node = rev_ss.setdefault(
            "key_insights",
            {
                "status": "pending",
                "final_list": None,
                "notes": None,
                "llm_list": [],
                "section_regeneration_meta": None,
            },
        )
        node["llm_list"] = list(new_list)
        node["status"] = "pending"
        node["final_list"] = None
        _bump_regen_meta(node)
        return
    if section_key == "sources":
        if isinstance(content, str):
            lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
            new_list = lines or ([] if not content.strip() else [content.strip()])
        else:
            new_list = [str(x).strip() for x in content if str(x).strip()]
        llm_ss["sources"] = new_list
        node = rev_ss.setdefault(
            "sources",
            {
                "status": "pending",
                "final_list": None,
                "notes": None,
                "llm_list": [],
                "section_regeneration_meta": None,
            },
        )
        node["llm_list"] = list(new_list)
        node["status"] = "pending"
        node["final_list"] = None
        _bump_regen_meta(node)
        return
    if section_key not in SOURCE_SUMMARY_SCALAR_KEYS:
        raise ValueError(f"Unknown source section: {section_key}")
    text = content if isinstance(content, str) else "\n".join(str(x) for x in content)
    llm_ss[section_key] = text.strip()
    node = rev_ss.setdefault(section_key, _fresh_scalar_review_node())
    node["status"] = "pending"
    node["final_text"] = None
    _bump_regen_meta(node)
