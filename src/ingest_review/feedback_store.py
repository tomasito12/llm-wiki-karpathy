"""Append-only SQLite store for human review feedback events (future learning loop)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.ingest_review.paths import repo_root
from src.ingest_review.schema import (
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
)


def default_feedback_db_path(root: Path | None = None) -> Path:
    """Return default path ``state/review_feedback.sqlite``."""
    return (root or repo_root()) / "state" / "review_feedback.sqlite"


def _utc_now_iso() -> str:
    """Return UTC timestamp string."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


DDL = """
CREATE TABLE IF NOT EXISTS feedback_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_hash TEXT,
    proposal_id TEXT,
    path_in_json TEXT,
    decision TEXT NOT NULL,
    llm_value_snapshot TEXT,
    final_value_snapshot TEXT,
    provider TEXT,
    model TEXT,
    prompt_version TEXT
);
"""


def init_feedback_db(path: Path) -> None:
    """Create parent directory and apply schema if missing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(DDL)
        conn.commit()


@dataclass(frozen=True)
class FeedbackEvent:
    """One recorded reviewer decision."""

    source_id: str
    source_hash: str | None
    proposal_id: str | None
    path_in_json: str | None
    decision: str
    llm_value_snapshot: Any
    final_value_snapshot: Any
    provider: str | None
    model: str | None
    prompt_version: str | None


def append_feedback_event(
    path: Path,
    event: FeedbackEvent,
) -> int:
    """Insert one row and return SQLite row id."""
    init_feedback_db(path)
    with sqlite3.connect(path) as conn:
        cur = conn.execute(
            """
            INSERT INTO feedback_events (
                created_at, source_id, source_hash, proposal_id, path_in_json,
                decision, llm_value_snapshot, final_value_snapshot,
                provider, model, prompt_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _utc_now_iso(),
                event.source_id,
                event.source_hash,
                event.proposal_id,
                event.path_in_json,
                event.decision,
                json.dumps(event.llm_value_snapshot, ensure_ascii=False),
                json.dumps(event.final_value_snapshot, ensure_ascii=False),
                event.provider,
                event.model,
                event.prompt_version,
            ),
        )
        conn.commit()
        return int(cur.lastrowid or 0)


def record_events_from_artifact(path: Path, artifact: dict[str, Any]) -> int:
    """Flatten ``artifact`` review decisions and append feedback rows.

    Returns:
        Number of rows inserted.
    """
    source = artifact.get("source") or {}
    source_id = str(source.get("source_id") or "")
    source_hash = source.get("content_sha256")
    meta = artifact.get("analysis_meta") or {}
    provider = meta.get("provider")
    model = meta.get("model")
    prompt_version = meta.get("prompt_version")
    review = artifact.get("review") or {}
    llm = artifact.get("llm_output") or {}

    count = 0
    ss = review.get("source_summary") or {}
    llm_ss = llm.get("source_summary") or {}
    for key in SOURCE_SUMMARY_SCALAR_KEYS:
        node = ss.get(key)
        if not isinstance(node, dict):
            continue
        st = str(node.get("status") or "pending")
        if st == "pending":
            continue
        append_feedback_event(
            path,
            FeedbackEvent(
                source_id=source_id,
                source_hash=str(source_hash) if source_hash else None,
                proposal_id=None,
                path_in_json=f"source_summary.{key}",
                decision=st,
                llm_value_snapshot=llm_ss.get(key),
                final_value_snapshot=node.get("final_text"),
                provider=str(provider) if provider else None,
                model=str(model) if model else None,
                prompt_version=str(prompt_version) if prompt_version else None,
            ),
        )
        count += 1

    for list_key in ("key_insights", "sources"):
        list_node = ss.get(list_key)
        if not isinstance(list_node, dict):
            continue
        st = str(list_node.get("status") or "pending")
        if st == "pending":
            continue
        append_feedback_event(
            path,
            FeedbackEvent(
                source_id=source_id,
                source_hash=str(source_hash) if source_hash else None,
                proposal_id=None,
                path_in_json=f"source_summary.{list_key}",
                decision=st,
                llm_value_snapshot=llm_ss.get(list_key),
                final_value_snapshot=list_node.get("final_list"),
                provider=str(provider) if provider else None,
                model=str(model) if model else None,
                prompt_version=str(prompt_version) if prompt_version else None,
            ),
        )
        count += 1

    src_type_r = review.get("source_type_detection")
    if isinstance(src_type_r, dict):
        st = str(src_type_r.get("status") or "pending")
        if st != "pending":
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=None,
                    path_in_json="source_type_detection",
                    decision=st,
                    llm_value_snapshot=src_type_r.get("llm_item"),
                    final_value_snapshot=src_type_r.get("final_item"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1

    for idx, g_node in enumerate(review.get("glossary") or []):
        if not isinstance(g_node, dict):
            continue
        pid = g_node.get("proposal_id")
        g_sections = g_node.get("sections") or {}
        g_llm_item = g_node.get("llm_item") or {}
        for sk in GLOSSARY_SCALAR_KEYS:
            sec = g_sections.get(sk)
            if not isinstance(sec, dict):
                continue
            st = str(sec.get("status") or "pending")
            if st == "pending":
                continue
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=str(pid) if pid else None,
                    path_in_json=f"glossary[{idx}].sections.{sk}",
                    decision=st,
                    llm_value_snapshot=g_llm_item.get(sk),
                    final_value_snapshot=sec.get("final_text"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1
        for lk in GLOSSARY_LIST_KEYS:
            sec = g_sections.get(lk)
            if not isinstance(sec, dict):
                continue
            st = str(sec.get("status") or "pending")
            if st == "pending":
                continue
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=str(pid) if pid else None,
                    path_in_json=f"glossary[{idx}].sections.{lk}",
                    decision=st,
                    llm_value_snapshot=g_llm_item.get(lk),
                    final_value_snapshot=sec.get("final_list"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1

    per_section_types: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = [
        ("foundation_models", MODEL_SCALAR_KEYS, MODEL_LIST_KEYS),
        ("tools", TOOL_SCALAR_KEYS, TOOL_LIST_KEYS),
        ("topics", TOPIC_SCALAR_KEYS, TOPIC_LIST_KEYS),
        ("how_to", HOWTO_SCALAR_KEYS, HOWTO_LIST_KEYS),
        ("industry_trends", TREND_SCALAR_KEYS, TREND_LIST_KEYS),
        ("roundup_signals", SIGNAL_SCALAR_KEYS, SIGNAL_LIST_KEYS),
        ("interview_insights", INSIGHT_SCALAR_KEYS, INSIGHT_LIST_KEYS),
    ]
    for ps_key, ps_scalar, ps_list in per_section_types:
        for idx, ps_node in enumerate(review.get(ps_key) or []):
            if not isinstance(ps_node, dict):
                continue
            pid = ps_node.get("proposal_id")
            ps_sections = ps_node.get("sections") or {}
            ps_llm_item = ps_node.get("llm_item") or {}
            for sk in ps_scalar:
                sec = ps_sections.get(sk)
                if not isinstance(sec, dict):
                    continue
                st = str(sec.get("status") or "pending")
                if st == "pending":
                    continue
                append_feedback_event(
                    path,
                    FeedbackEvent(
                        source_id=source_id,
                        source_hash=str(source_hash) if source_hash else None,
                        proposal_id=str(pid) if pid else None,
                        path_in_json=f"{ps_key}[{idx}].sections.{sk}",
                        decision=st,
                        llm_value_snapshot=ps_llm_item.get(sk),
                        final_value_snapshot=sec.get("final_text"),
                        provider=str(provider) if provider else None,
                        model=str(model) if model else None,
                        prompt_version=str(prompt_version) if prompt_version else None,
                    ),
                )
                count += 1
            for lk in ps_list:
                sec = ps_sections.get(lk)
                if not isinstance(sec, dict):
                    continue
                st = str(sec.get("status") or "pending")
                if st == "pending":
                    continue
                append_feedback_event(
                    path,
                    FeedbackEvent(
                        source_id=source_id,
                        source_hash=str(source_hash) if source_hash else None,
                        proposal_id=str(pid) if pid else None,
                        path_in_json=f"{ps_key}[{idx}].sections.{lk}",
                        decision=st,
                        llm_value_snapshot=ps_llm_item.get(lk),
                        final_value_snapshot=sec.get("final_list"),
                        provider=str(provider) if provider else None,
                        model=str(model) if model else None,
                        prompt_version=str(prompt_version) if prompt_version else None,
                    ),
                )
                count += 1

    for idx, impl_node in enumerate(review.get("implementation_studies") or []):
        if not isinstance(impl_node, dict):
            continue
        pid = impl_node.get("proposal_id")
        sections = impl_node.get("sections") or {}
        llm_item = impl_node.get("llm_item") or {}
        for sk in IMPL_STUDY_SCALAR_KEYS:
            sec = sections.get(sk)
            if not isinstance(sec, dict):
                continue
            st = str(sec.get("status") or "pending")
            if st == "pending":
                continue
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=str(pid) if pid else None,
                    path_in_json=f"implementation_studies[{idx}].sections.{sk}",
                    decision=st,
                    llm_value_snapshot=llm_item.get(sk),
                    final_value_snapshot=sec.get("final_text"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1
        for lk in IMPL_STUDY_LIST_KEYS:
            sec = sections.get(lk)
            if not isinstance(sec, dict):
                continue
            st = str(sec.get("status") or "pending")
            if st == "pending":
                continue
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=str(pid) if pid else None,
                    path_in_json=f"implementation_studies[{idx}].sections.{lk}",
                    decision=st,
                    llm_value_snapshot=llm_item.get(lk),
                    final_value_snapshot=sec.get("final_list"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1

    return count
