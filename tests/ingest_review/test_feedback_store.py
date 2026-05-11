"""Tests for feedback SQLite store."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.feedback_store import (
    FeedbackEvent,
    append_feedback_event,
    init_feedback_db,
    record_events_from_artifact,
)


def test_init_feedback_db_creates_file(tmp_path: Path) -> None:
    """Schema application creates the sqlite file."""
    db = tmp_path / "fb.sqlite"
    init_feedback_db(db)
    assert db.is_file()


def test_append_feedback_event_inserts_row(tmp_path: Path) -> None:
    """One event produces one retrievable row."""
    db = tmp_path / "fb.sqlite"
    rid = append_feedback_event(
        db,
        FeedbackEvent(
            source_id="s1",
            source_hash="abc",
            proposal_id="p1",
            path_in_json="tools[0]",
            decision="approved",
            llm_value_snapshot={"x": 1},
            final_value_snapshot=None,
            provider="openai",
            model="gpt-test",
            prompt_version="1",
        ),
    )
    assert rid > 0


def test_record_events_from_artifact_skips_all_pending(tmp_path: Path) -> None:
    """No rows when every review node is still pending."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "1"},
        "llm_output": {"glossary": []},
        "review": {"glossary": []},
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 0


def test_record_events_records_approved_summary_field(tmp_path: Path) -> None:
    """Approved source_summary field emits one feedback row."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "1"},
        "llm_output": {"source_summary": {"why_it_matters": "A"}},
        "review": {
            "source_summary": {
                "why_it_matters": {"status": "approved", "final_text": None, "notes": ""},
            },
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 1
