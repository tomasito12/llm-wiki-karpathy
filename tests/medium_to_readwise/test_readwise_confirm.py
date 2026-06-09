"""Tests for Readwise save confirmation detection."""

from __future__ import annotations

from src.medium_to_readwise.readwise_confirm import page_text_indicates_readwise_save


def test_page_text_indicates_readwise_save_matches_reader_confirmation() -> None:
    """Visible Reader confirmation text is treated as a successful save."""
    text = "Saved to Reader\nOpen in Readwise"
    assert page_text_indicates_readwise_save(text) is True


def test_page_text_indicates_readwise_save_rejects_unrelated_text() -> None:
    """Unrelated page text does not count as a Readwise confirmation."""
    assert page_text_indicates_readwise_save("Follow for more stories") is False
