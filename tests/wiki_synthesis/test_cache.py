"""Tests for Stage 2 synthesis cache validation."""

from __future__ import annotations

from src.wiki_synthesis.cache import (
    VALIDATION_FRESH,
    VALIDATION_INVALID,
    VALIDATION_STALE,
    validate_cache_entry,
)


def test_validate_cache_entry_marks_matching_entry_fresh() -> None:
    """A complete cache entry with a matching hash should be fresh."""
    result = validate_cache_entry(_cache_entry("abc"), current_input_hash="abc")

    assert result.state == VALIDATION_FRESH
    assert result.is_usable


def test_validate_cache_entry_marks_mismatched_entry_stale_but_usable() -> None:
    """A complete cache entry with an old hash should still render as stale."""
    result = validate_cache_entry(_cache_entry("old"), current_input_hash="new")

    assert result.state == VALIDATION_STALE
    assert result.is_usable


def test_validate_cache_entry_rejects_incomplete_entry() -> None:
    """An incomplete cache entry should not render as synthesis."""
    result = validate_cache_entry({"synthesis_input_hash": "abc"}, current_input_hash="abc")

    assert result.state == VALIDATION_INVALID
    assert not result.is_usable


def _cache_entry(input_hash: str) -> dict[str, object]:
    """Return a complete minimal synthesis cache entry."""
    return {
        "entity_id": "topic:local-models",
        "category": "topic",
        "slug": "local-models",
        "title": "Local Models",
        "synthesis_input_hash": input_hash,
        "executive_synthesis": "Local models run near users.",
        "what_to_remember": ["They reduce dependency on hosted APIs."],
        "consensus": ["Useful when latency or privacy matters."],
        "tensions": ["Operational burden can outweigh benefits."],
        "evidence_quality": ["Two sources, mostly practitioner observations."],
        "practical_takeaway": "Use them when control matters more than convenience.",
    }
