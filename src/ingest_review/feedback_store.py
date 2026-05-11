"""Append-only SQLite store for human review feedback events (future learning loop)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.ingest_review.paths import repo_root


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
    for key in (
        "why_it_matters",
        "key_insights",
        "implications_automation",
        "context_limitations",
        "contradictions",
    ):
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

    src_sources = review.get("source_summary", {}).get("sources")
    if isinstance(src_sources, dict):
        st = str(src_sources.get("status") or "pending")
        if st != "pending":
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=None,
                    path_in_json="source_summary.sources",
                    decision=st,
                    llm_value_snapshot=src_sources.get("llm_list"),
                    final_value_snapshot=src_sources.get("final_list"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1

    roundup_r = review.get("roundup")
    if isinstance(roundup_r, dict):
        st = str(roundup_r.get("status") or "pending")
        if st != "pending":
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=None,
                    path_in_json="roundup",
                    decision=st,
                    llm_value_snapshot=roundup_r.get("llm_item"),
                    final_value_snapshot=roundup_r.get("final_item"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1

    list_pairs = [
        ("glossary", "glossary"),
        ("tools", "tools"),
        ("foundation_models", "foundation_models"),
        ("how_to", "how_to"),
        ("enterprise_studies", "enterprise_studies"),
        ("industry_trends", "industry_trends"),
    ]
    for review_key, llm_key in list_pairs:
        items_r = review.get(review_key) or []
        items_l = llm.get(llm_key) or []
        for idx, item_r in enumerate(items_r):
            if not isinstance(item_r, dict):
                continue
            st = str(item_r.get("status") or "pending")
            if st == "pending":
                continue
            pid = item_r.get("proposal_id")
            llm_item = items_l[idx] if idx < len(items_l) else None
            append_feedback_event(
                path,
                FeedbackEvent(
                    source_id=source_id,
                    source_hash=str(source_hash) if source_hash else None,
                    proposal_id=str(pid) if pid else None,
                    path_in_json=f"{review_key}[{idx}]",
                    decision=st,
                    llm_value_snapshot=llm_item,
                    final_value_snapshot=item_r.get("final_item"),
                    provider=str(provider) if provider else None,
                    model=str(model) if model else None,
                    prompt_version=str(prompt_version) if prompt_version else None,
                ),
            )
            count += 1
    return count
