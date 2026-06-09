"""Progress formatting for Medium to Readwise runs."""

from __future__ import annotations


def estimated_remaining_seconds(
    *,
    processed_count: int,
    total_count: int,
    elapsed_seconds: float,
) -> int | None:
    """Estimate remaining seconds from current throughput."""
    if processed_count <= 0 or total_count <= processed_count or elapsed_seconds <= 0:
        return None
    seconds_per_item = elapsed_seconds / processed_count
    return round(seconds_per_item * (total_count - processed_count))


def format_duration(seconds: int | float) -> str:
    """Format a duration as compact human-readable text."""
    whole_seconds = max(0, round(seconds))
    if whole_seconds < 60:
        return f"{whole_seconds} sec"
    minutes, remainder = divmod(whole_seconds, 60)
    if minutes < 60:
        return f"{minutes} min {remainder} sec" if remainder else f"{minutes} min"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} hr {minutes} min" if minutes else f"{hours} hr"


def format_progress_line(
    *,
    processed_count: int,
    total_count: int,
    elapsed_seconds: float,
) -> str:
    """Return a progress line with an ETA when enough data is available."""
    eta = estimated_remaining_seconds(
        processed_count=processed_count,
        total_count=total_count,
        elapsed_seconds=elapsed_seconds,
    )
    base = f"Processed {processed_count} / {total_count} articles"
    if eta is None:
        return base
    return f"{base} (estimated remaining: {format_duration(eta)})"
