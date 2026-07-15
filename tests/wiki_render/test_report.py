"""Tests for wiki-render human-readable summaries."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_render.report import (
    PreviousRenderSnapshot,
    RenderRunSummary,
    format_render_summary_text,
    load_previous_render_snapshot,
)
from src.wiki_render.source_text import SourceTextCoverage
from src.wiki_render.writer import WriteReport


def test_load_previous_render_snapshot_reads_manifest_counts(tmp_path: Path) -> None:
    """Previous render counts should be read from the advisory manifest."""
    manifest = tmp_path / "wiki_render_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "source_count": 360,
                "knowledge_page_count": 700,
                "files": [{"path": "topics/a.md"}, {"path": "sources/a.md"}],
            }
        ),
        encoding="utf-8",
    )

    snapshot = load_previous_render_snapshot(manifest)

    assert snapshot is not None
    assert snapshot.source_count == 360
    assert snapshot.knowledge_page_count == 700
    assert snapshot.file_count == 2


def test_load_previous_render_snapshot_returns_none_for_missing_file(tmp_path: Path) -> None:
    """Missing manifests should not produce a previous snapshot."""
    snapshot = load_previous_render_snapshot(tmp_path / "missing.json")

    assert snapshot is None


def test_format_render_summary_text_explains_dry_run_metrics() -> None:
    """Dry-run output should explain would-write vs unchanged and show deltas."""
    summary = RenderRunSummary(
        dry_run=True,
        source_count=460,
        knowledge_page_count=745,
        write_report=WriteReport(
            planned=1582,
            written=430,
            unchanged=1152,
            pruned=4,
            skipped_prune=False,
            protected_from_prune=0,
        ),
        coverage=SourceTextCoverage(total=460, available=460, missing=0),
        previous=PreviousRenderSnapshot(
            source_count=360,
            knowledge_page_count=700,
            file_count=1500,
        ),
    )

    report = format_render_summary_text(summary)

    assert "Wiki Render Summary (dry-run — no files changed)" in report
    assert "sources: 460 (+100 vs last render: 360)" in report
    assert "knowledge pages: 745 (+45 vs last render: 700)" in report
    assert "output files: 1582 (+82 vs last render: 1500)" in report
    assert "would write: 430" in report
    assert "unchanged: 1152" in report
    assert "would prune: 4" in report
    assert "460 of 460 source pages would include embedded raw text (100.0%)" in report
    assert "run wiki-render without --dry-run" in report


def test_format_render_summary_text_lists_write_paths_when_requested() -> None:
    """Show-writes should list paths and folder counts in the summary."""
    summary = RenderRunSummary(
        dry_run=True,
        source_count=2,
        knowledge_page_count=1,
        write_report=WriteReport(
            planned=3,
            written=2,
            unchanged=1,
            pruned=0,
            skipped_prune=True,
            write_paths=("sources/a.md", "topics/example.md"),
            prune_paths=(),
        ),
        coverage=SourceTextCoverage(total=1, available=1, missing=0),
    )

    report = format_render_summary_text(summary, show_writes=True)

    assert "Files that would write" in report
    assert "- sources/a.md" in report
    assert "- topics/example.md" in report
    assert "sources/: 1" in report
    assert "topics/: 1" in report


def test_format_render_summary_text_uses_written_labels_for_real_run() -> None:
    """Real runs should use past-tense write/prune labels."""
    summary = RenderRunSummary(
        dry_run=False,
        source_count=1,
        knowledge_page_count=2,
        write_report=WriteReport(
            planned=3,
            written=1,
            unchanged=2,
            pruned=0,
            skipped_prune=True,
            protected_from_prune=0,
        ),
        coverage=SourceTextCoverage(total=0, available=0, missing=0),
    )

    report = format_render_summary_text(summary)

    assert "Wiki Render Summary (write)" in report
    assert "written: 1" in report
    assert "pruned: 0" in report
    assert "prune: skipped (no previous manifest to compare)" in report
    assert "no source pages planned" in report
