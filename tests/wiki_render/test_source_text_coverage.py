"""Tests for source full-text coverage helpers."""

from __future__ import annotations

from src.wiki_render.models import RenderedFile
from src.wiki_render.source_text import (
    evaluate_source_text_coverage,
    summarize_source_text_coverage,
)


def test_summarize_source_text_coverage_counts_available_and_missing() -> None:
    """Coverage summary should count source pages by source_text_available frontmatter."""
    files = [
        _source_page(source_text_available=True),
        _source_page(source_text_available=False, source_id="source-b"),
        RenderedFile(relative_path="topics/example.md", text="# Topic\n"),
    ]

    coverage = summarize_source_text_coverage(files)

    assert coverage.total == 2
    assert coverage.available == 1
    assert coverage.missing == 1
    assert coverage.available_ratio == 0.5


def test_evaluate_source_text_coverage_warns_when_most_sources_missing() -> None:
    """Low coverage should produce a warning message."""
    coverage = summarize_source_text_coverage(
        [
            _source_page(source_text_available=True),
            _source_page(source_text_available=False, source_id="source-b"),
            _source_page(source_text_available=False, source_id="source-c"),
        ]
    )

    message = evaluate_source_text_coverage(coverage, min_available_ratio=0.5)

    assert message is not None
    assert "Low source full-text coverage" in message
    assert "1/3" in message


def test_evaluate_source_text_coverage_is_silent_when_coverage_is_healthy() -> None:
    """Healthy coverage should not produce a warning."""
    coverage = summarize_source_text_coverage(
        [
            _source_page(source_text_available=True),
            _source_page(source_text_available=True, source_id="source-b"),
        ]
    )

    message = evaluate_source_text_coverage(coverage, min_available_ratio=0.5)

    assert message is None


def _source_page(*, source_text_available: bool, source_id: str = "source-a") -> RenderedFile:
    """Build a minimal rendered source page fixture."""
    flag = "true" if source_text_available else "false"
    return RenderedFile(
        relative_path=f"sources/{source_id}.md",
        text=(
            "---\n"
            f"title: Example\n"
            f"category: source\n"
            f"source_id: {source_id}\n"
            f"source_text_available: {flag}\n"
            "---\n\n"
            "# Example\n"
        ),
    )
