"""Tests for Stage 2 synthesis doctor checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pytest import MonkeyPatch

from src.wiki_synthesis.doctor import DoctorCheck, DoctorReport, run_doctor


def test_doctor_ready_with_api_key_warning(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Doctor should be ready for dry-run style checks when only API key is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    graph_path = tmp_path / "graph.json"
    graph_path.write_text("{}", encoding="utf-8")

    report = run_doctor(
        _graph(),
        graph_path=graph_path,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        model="test-model",
        entity="topic:local-models",
    )

    assert report.ready
    assert report.exit_code == 0
    assert report.plan.entries[0].state == "new"
    assert _check(report, "openai_api_key").status == "warning"


def test_doctor_fails_when_api_key_required(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Doctor should fail when a real run requires a missing API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    graph_path = tmp_path / "graph.json"
    graph_path.write_text("{}", encoding="utf-8")

    report = run_doctor(
        _graph(),
        graph_path=graph_path,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        model="test-model",
        entity="topic:local-models",
        require_api_key=True,
    )

    assert not report.ready
    assert report.exit_code == 1
    assert _check(report, "openai_api_key").status == "error"


def test_doctor_fails_for_empty_model(tmp_path: Path) -> None:
    """Doctor should fail when model configuration is empty."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text("{}", encoding="utf-8")

    report = run_doctor(
        _graph(),
        graph_path=graph_path,
        cache_dir=tmp_path / "cache",
        preview_dir=tmp_path / "previews",
        report_dir=tmp_path / "runs",
        model="",
        entity="topic:local-models",
    )

    assert not report.ready
    assert _check(report, "model").status == "error"


def _check(report: DoctorReport, name: str) -> DoctorCheck:
    """Return one check by name."""
    for check in report.checks:
        if check.name == name:
            return check
    msg = f"missing check: {name}"
    raise AssertionError(msg)


def _graph() -> dict[str, Any]:
    """Return a minimal graph export with one executable knowledge page."""
    return {
        "knowledge_pages": [
            {
                "entity_id": "topic:local-models",
                "category": "topic",
                "slug": "local-models",
                "title": "Local Models",
                "path": "topics/local-models.md",
                "aliases": [],
                "tags": ["ai-engineering"],
                "types": [],
                "source_ids": ["source-a", "source-b"],
                "source_count": 2,
                "evidence_count": 1,
                "value_level": "high",
                "confidence": 0.9,
                "supporting_count": 1,
                "counter_count": 0,
                "uncertainty_count": 0,
                "neutral_count": 0,
                "evidence": [
                    {
                        "evidence_id": "evidence-a",
                        "text": "Local models run near users.",
                        "source_id": "source-a",
                        "field": "knowledge_summary",
                        "stance": "supporting",
                    }
                ],
            }
        ]
    }
