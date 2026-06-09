"""Tests for Medium to Readwise progress formatting."""

from __future__ import annotations

from src.medium_to_readwise.progress import (
    estimated_remaining_seconds,
    format_duration,
    format_progress_line,
)


def test_estimated_remaining_seconds_returns_none_without_throughput() -> None:
    """ETA is unavailable before at least one item has completed."""
    assert estimated_remaining_seconds(processed_count=0, total_count=10, elapsed_seconds=5) is None


def test_estimated_remaining_seconds_uses_average_item_time() -> None:
    """ETA uses elapsed time per processed item."""
    assert (
        estimated_remaining_seconds(processed_count=5, total_count=10, elapsed_seconds=100) == 100
    )


def test_format_duration_handles_seconds_minutes_and_hours() -> None:
    """Durations are displayed compactly across common ranges."""
    assert format_duration(12) == "12 sec"
    assert format_duration(120) == "2 min"
    assert format_duration(3660) == "1 hr 1 min"


def test_format_progress_line_includes_eta_when_available() -> None:
    """Progress lines include an ETA once throughput is known."""
    assert (
        format_progress_line(processed_count=5, total_count=10, elapsed_seconds=100)
        == "Processed 5 / 10 articles (estimated remaining: 1 min 40 sec)"
    )
