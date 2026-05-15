"""Tests for source_summary block and accessible_overview (Easy read)."""

from __future__ import annotations

from src.ingest_review.schema import (
    SourceSummaryBlock,
    normalize_source_summary,
)


def test_source_summary_block_has_accessible_overview() -> None:
    """SourceSummaryBlock includes accessible_overview with default empty string."""
    block = SourceSummaryBlock()
    assert block.accessible_overview == ""
    roundtrip = SourceSummaryBlock.model_validate(
        {"summary": "s", "accessible_overview": "easy text"}
    )
    assert roundtrip.accessible_overview == "easy text"


def test_normalize_source_summary_strips_accessible_overview() -> None:
    """normalize_source_summary trims accessible_overview whitespace."""
    block = SourceSummaryBlock(accessible_overview="  hello  \n")
    out = normalize_source_summary(block)
    assert out.accessible_overview == "hello"
