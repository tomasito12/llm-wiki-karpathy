"""Tests for unattended synchronous pre-analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ingest_batch.preanalyze import (
    PreanalyzeProgress,
    preanalyze_pending,
    select_pending_items,
)
from src.ingest_review.review_queue_status import status_for_source
from src.ingest_review.skipped_sources import mark_source_skipped


def _write_raw_pair(raw_dir: Path, source_id: str) -> None:
    """Write a minimal Readwise HTML/Markdown pair."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{source_id}.html").write_text(
        "<html><body><article>Useful source text for testing.</article></body></html>",
        encoding="utf-8",
    )
    (raw_dir / f"{source_id}.md").write_text(
        "---\ntitle: Test Source\n---\n\nMarkdown body.",
        encoding="utf-8",
    )


def _artifact(source_id: str) -> dict[str, object]:
    """Return a minimal pre-analysis review artifact."""
    return {
        "source": {"id": source_id},
        "review_analytics": {"review_started_at": "2026-01-01T00:00:00+00:00"},
        "llm_output": {},
        "review": {},
    }


def test_select_pending_items_returns_first_n_and_ignores_skipped(tmp_path: Path) -> None:
    """Pending selection is deterministic and excludes reviewed, incomplete, and skipped IDs."""
    raw_dir = tmp_path / "raw"
    reviews_root = tmp_path / "reviews"
    for source_id in ("a", "b", "c", "d"):
        _write_raw_pair(raw_dir, source_id)
    (raw_dir / "incomplete.html").write_text("<html></html>", encoding="utf-8")
    reviewed_dir = reviews_root / "b"
    reviewed_dir.mkdir(parents=True)
    (reviewed_dir / "review.json").write_text(json.dumps(_artifact("b")), encoding="utf-8")
    mark_source_skipped(reviews_root, "c")

    items = select_pending_items(raw_dir, reviews_root, limit=2)

    assert [item.basename for item in items] == ["a", "d"]


def test_preanalyze_pending_processes_sources_and_reports_progress(tmp_path: Path) -> None:
    """The loop writes artifacts and emits progress for processed sources."""
    raw_dir = tmp_path / "raw"
    reviews_root = tmp_path / "reviews"
    wiki_root = tmp_path / "wiki"
    _write_raw_pair(raw_dir, "source-a")
    events: list[PreanalyzeProgress] = []

    def runner(provider: Any, document: Any, **_kwargs: Any) -> tuple[dict[str, object], None]:
        _ = provider
        return _artifact(document.source_id), None

    result = preanalyze_pending(
        raw_dir=raw_dir,
        reviews_root=reviews_root,
        wiki_root=wiki_root,
        tool_types=[],
        howto_tags=[],
        impl_study_tags=[],
        glossary_tags=[],
        topic_tags=[],
        trend_tags=[],
        model_types=[],
        tool_tags=[],
        model_tags=[],
        extraction_budgets={},
        model="test-model",
        limit=10,
        provider=object(),
        runner=runner,
        on_progress=events.append,
    )

    assert result.processed == ["source-a"]
    assert result.failed == []
    assert events[0].status == "processed"
    assert status_for_source(reviews_root, "source-a") == "in_progress"


def test_preanalyze_pending_continues_after_error(tmp_path: Path) -> None:
    """A failed source is recorded while later sources continue processing."""
    raw_dir = tmp_path / "raw"
    reviews_root = tmp_path / "reviews"
    wiki_root = tmp_path / "wiki"
    _write_raw_pair(raw_dir, "bad")
    _write_raw_pair(raw_dir, "good")

    def runner(provider: Any, document: Any, **_kwargs: Any) -> tuple[dict[str, object], None]:
        _ = provider
        if document.source_id == "bad":
            raise RuntimeError("boom")
        return _artifact(document.source_id), None

    result = preanalyze_pending(
        raw_dir=raw_dir,
        reviews_root=reviews_root,
        wiki_root=wiki_root,
        tool_types=[],
        howto_tags=[],
        impl_study_tags=[],
        glossary_tags=[],
        topic_tags=[],
        trend_tags=[],
        model_types=[],
        tool_tags=[],
        model_tags=[],
        extraction_budgets={},
        model="test-model",
        limit=10,
        provider=object(),
        runner=runner,
    )

    assert result.processed == ["good"]
    assert [(failure.source_id, failure.message) for failure in result.failed] == [("bad", "boom")]
    assert (reviews_root / "good" / "review.json").is_file()


def test_preanalyze_pending_skip_existing_is_idempotent(tmp_path: Path) -> None:
    """Existing review artifacts make a re-run a no-op for that source."""
    raw_dir = tmp_path / "raw"
    reviews_root = tmp_path / "reviews"
    _write_raw_pair(raw_dir, "already")
    existing_dir = reviews_root / "already"
    existing_dir.mkdir(parents=True)
    (existing_dir / "review.json").write_text(json.dumps(_artifact("already")), encoding="utf-8")

    result = preanalyze_pending(
        raw_dir=raw_dir,
        reviews_root=reviews_root,
        wiki_root=tmp_path / "wiki",
        tool_types=[],
        howto_tags=[],
        impl_study_tags=[],
        glossary_tags=[],
        topic_tags=[],
        trend_tags=[],
        model_types=[],
        tool_tags=[],
        model_tags=[],
        extraction_budgets={},
        model="test-model",
        limit=10,
        provider=object(),
        runner=lambda *_args, **_kwargs: (_artifact("already"), None),
    )

    assert result.selected == 0
    assert result.processed == []
