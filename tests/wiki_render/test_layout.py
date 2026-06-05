"""Tests for generated wiki layout."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render import layout


def test_layout_uses_lowercase_hyphenated_folders() -> None:
    """Generated paths use canonical lowercase folder names."""
    wiki_dir = Path("wiki")

    assert layout.page_path(wiki_dir, "trend", "Open Model Pressure").relative == (
        "industry-trends/open-model-pressure.md"
    )
    assert (
        layout.monthly_item_path(
            wiki_dir,
            "signal",
            source_id="Source A",
            slug="Browser Prompts",
            date_text="2026-04-15",
        ).relative
        == "signals/2026-04/source-a-browser-prompts.md"
    )


def test_unknown_month_bucket_for_missing_dates() -> None:
    """Undated chronological items go to an unknown bucket."""
    assert layout.month_bucket("") == "unknown"
    assert layout.month_bucket("2026-04-15") == "2026-04"


def test_monthly_item_paths_are_truncated_for_filesystem_limits() -> None:
    """Long source/title combinations keep provenance shape without oversized basenames."""
    path = layout.monthly_item_path(
        Path("wiki"),
        "insight",
        source_id="source-" * 40,
        slug="insight-" * 40,
        date_text="2026-04-15",
    )

    assert path.relative.startswith("interview-insights/2026-04/source-")
    assert len(Path(path.relative).name.removesuffix(".md")) <= layout.MAX_MONTHLY_BASENAME_LENGTH
