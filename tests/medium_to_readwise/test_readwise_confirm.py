"""Tests for Readwise save confirmation detection."""

from __future__ import annotations

import asyncio
from typing import Any, cast

from src.medium_to_readwise.readwise_confirm import (
    normalize_readwise_confirm_mode,
    page_text_indicates_readwise_save,
    wait_for_readwise_save,
)


class FakeConfirmLocator:
    """Minimal locator for Readwise confirmation tests."""

    def __init__(self, *, visible: bool) -> None:
        """Initialize locator state."""
        self.visible = visible

    @property
    def first(self) -> FakeConfirmLocator:
        """Return the first matching locator."""
        return self

    async def count(self) -> int:
        """Return whether a match exists."""
        return 1 if self.visible else 0

    async def is_visible(self) -> bool:
        """Return whether the match is visible."""
        return self.visible


class FakeConfirmPage:
    """Minimal page object for Readwise confirmation tests."""

    def __init__(self, *, body_text: str = "") -> None:
        """Initialize fake page behavior."""
        self.body_text = body_text

    def get_by_text(self, phrase: str, *, exact: bool = False) -> FakeConfirmLocator:
        """Return a fake text locator."""
        del exact
        return FakeConfirmLocator(visible=False)

    def locator(self, selector: str) -> FakeConfirmLocator:
        """Return a fake selector locator."""
        del selector
        return FakeConfirmLocator(visible=False)


def test_page_text_indicates_readwise_save_matches_reader_confirmation() -> None:
    """Visible Reader confirmation text is treated as a successful save."""
    text = "Saved to Reader\nOpen in Readwise"
    assert page_text_indicates_readwise_save(text) is True


def test_page_text_indicates_readwise_save_matches_extension_bar_copy() -> None:
    """Readwise extension bar copy counts as a successful save."""
    text = "Open in Reader\nHide the extension bar"
    assert page_text_indicates_readwise_save(text) is True


def test_page_text_indicates_readwise_save_rejects_unrelated_text() -> None:
    """Unrelated page text does not count as a Readwise confirmation."""
    assert page_text_indicates_readwise_save("Follow for more stories") is False


def test_normalize_readwise_confirm_mode_accepts_relaxed() -> None:
    """Relaxed confirmation mode is supported."""
    assert normalize_readwise_confirm_mode("relaxed") == "relaxed"


def test_wait_for_readwise_save_relaxed_mode_trusts_after_timeout() -> None:
    """Relaxed mode accepts toolbar-only saves after the wait elapses."""
    saved, method = asyncio.run(
        wait_for_readwise_save(
            cast(Any, FakeConfirmPage()),
            timeout_seconds=0.1,
            mode="relaxed",
        )
    )
    assert saved is True
    assert method == "relaxed_timeout"


def test_wait_for_readwise_save_text_mode_fails_without_visible_confirmation() -> None:
    """Strict text mode does not trust toolbar-only saves."""
    saved, method = asyncio.run(
        wait_for_readwise_save(
            cast(Any, FakeConfirmPage()),
            timeout_seconds=0.1,
            mode="text",
        )
    )
    assert saved is False
    assert method == "none"
