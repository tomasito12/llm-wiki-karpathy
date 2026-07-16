"""Tests for management web workflow output parsers."""

from __future__ import annotations

from src.management_web.workflow_parsers import (
    parse_batch_progress_message,
    parse_render_summary_text,
    parse_synthesis_batch_json,
    parse_synthesis_select_json,
    parse_wiki_lint_output,
    render_changes_pending,
)


def test_parse_synthesis_select_json_builds_candidate_summary() -> None:
    """Selection JSON should become readable candidate lines."""
    lines = parse_synthesis_select_json(
        {
            "total_changed": 42,
            "shown": 2,
            "entries": [
                {
                    "title": "Context Engineering",
                    "category": "topic",
                    "source_count": 14,
                    "state": "stale",
                    "score": 140,
                }
            ],
        }
    )

    assert lines[0] == "42 candidates found · 2 selected for this run"
    assert "Context Engineering" in lines[1]
    assert "score 140" in lines[1]


def test_parse_synthesis_batch_json_builds_completion_summary() -> None:
    """Batch JSON should summarize attempted and written counts."""
    lines = parse_synthesis_batch_json(
        {"selected": 5, "attempted": 5, "written": 5, "failed": 0, "dry_run": False}
    )

    assert lines[0] == "Synthesis batch completed"
    assert "5 selected · 5 attempted · 5 written · 0 failed" in lines[1]


def test_parse_batch_progress_message_builds_processing_summary() -> None:
    """Processing progress lines should become UI-friendly progress fields."""
    parsed = parse_batch_progress_message("processing topic:one index=1 total=5")

    assert parsed == {
        "current": 1,
        "total": 5,
        "display_message": "Synthesizing topic:one (1/5)",
    }


def test_parse_batch_progress_message_builds_waiting_summary() -> None:
    """Waiting progress lines should expose countdown messaging."""
    parsed = parse_batch_progress_message(
        "waiting topic:one index=1 total=5 seconds=300 remaining=299"
    )

    assert parsed == {
        "current": 1,
        "total": 5,
        "display_message": "Waiting 299s before next synthesis (1/5 done, after topic:one)",
    }


def test_parse_render_summary_text_detects_dry_run_changes() -> None:
    """Render dry-run stdout should expose would-write counts."""
    text = "\n".join(
        [
            "Wiki Render Summary (dry-run — no files changed)",
            "- output files: 1070",
            "- would write: 23",
            "- unchanged: 1047",
            "- would prune: 0",
            "- 295 of 295 source pages would include embedded raw text (100.0%)",
        ]
    )

    lines = parse_render_summary_text(text)

    assert lines[0] == "Render preview completed"
    assert "23 would write" in lines[1]
    assert render_changes_pending(text) is True


def test_parse_wiki_lint_output_builds_health_summary() -> None:
    """Lint stdout should summarize hygiene counts."""
    text = "\n".join(
        [
            "Vault hygiene",
            "- safe delete candidates: 0",
            "- manual review items: 0",
            "- exact duplicate groups: 0",
        ]
    )

    lines = parse_wiki_lint_output(text)

    assert lines[0] == "Wiki health check completed"
    assert "0 safe delete candidates" in lines[1]
