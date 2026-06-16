"""Tests for Medium article lazy-load helpers."""

from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest

from src.medium_to_readwise.article_loader import (
    PartialArticleContent,
    article_text_length,
    page_text_indicates_paywall_gate,
    scroll_article_down,
    wait_for_full_article_content,
)


class FakeArticleLocator:
    """Minimal locator for article loader tests."""

    def __init__(self, text: str, *, match_count: int = 1) -> None:
        """Initialize locator state."""
        self.text = text
        self.match_count = match_count

    @property
    def first(self) -> FakeArticleLocator:
        """Return the first matching locator."""
        return self

    async def count(self) -> int:
        """Return how many elements match."""
        return self.match_count

    async def inner_text(self) -> str:
        """Return configured article text."""
        return self.text


class FakeArticlePage:
    """Minimal page object for article loader tests."""

    def __init__(
        self,
        *,
        article_text: str = "x" * 1500,
        paywall_phrases: set[str] | None = None,
    ) -> None:
        """Initialize fake page behavior."""
        self.article_text = article_text
        self.paywall_phrases = paywall_phrases or set()
        self.evaluated: list[str] = []

    def locator(self, selector: str) -> FakeArticleLocator:
        """Return a fake locator for ``selector``."""
        if selector == "article":
            return FakeArticleLocator(self.article_text)
        return FakeArticleLocator("", match_count=0)

    def get_by_text(self, phrase: str, *, exact: bool = False) -> FakeArticleLocator:
        """Return a fake text locator."""
        del exact
        if phrase in self.paywall_phrases:
            return FakeArticleLocator(phrase, match_count=1)
        return FakeArticleLocator("", match_count=0)

    async def evaluate(self, script: str) -> None:
        """Record scroll scripts."""
        self.evaluated.append(script)

    async def wait_for_selector(self, selector: str, *, timeout: int) -> None:
        """Pretend the article selector appeared."""
        assert selector == "article"
        assert timeout > 0


def test_page_text_indicates_paywall_gate_matches_member_story_copy() -> None:
    """Medium member-story gates are detected from visible text."""
    text = "This member-only story is for members."
    assert page_text_indicates_paywall_gate(text) is True


def test_article_text_length_reads_article_inner_text() -> None:
    """Article length is measured from the rendered article body."""
    page = FakeArticlePage(article_text="hello world")
    assert asyncio.run(article_text_length(cast(Any, page))) == 11


def test_scroll_article_down_only_scrolls_down() -> None:
    """Scrolling down does not jump back to the top between steps."""
    page = FakeArticlePage()
    asyncio.run(scroll_article_down(cast(Any, page), scroll_steps=3, scroll_pause_seconds=0.01))
    assert all("scrollBy" in script for script in page.evaluated)
    assert not any("scrollTo(0, 0)" in script for script in page.evaluated)


def test_wait_for_full_article_content_completes_in_one_pass() -> None:
    """A long article is accepted after a single downward scroll pass."""
    page = FakeArticlePage(article_text="x" * 1500)
    logs: list[str] = []
    length = asyncio.run(
        wait_for_full_article_content(
            cast(Any, page),
            timeout_ms=5_000,
            min_chars=1200,
            scroll_steps=2,
            scroll_pause_seconds=0.01,
            stable_rounds=2,
            max_scroll_passes=3,
            log=logs.append,
        )
    )
    assert length == 1500
    assert any("article scroll pass 1/3" in line for line in logs)
    assert any("article body stable" in line for line in logs)
    assert any("scrollTo(0, 0)" in script for script in page.evaluated)


def test_wait_for_full_article_content_raises_when_paywall_remains() -> None:
    """A visible paywall gate stops the loader before Readwise can save."""
    page = FakeArticlePage(
        article_text="short preview",
        paywall_phrases={"continue reading this story"},
    )
    with pytest.raises(PartialArticleContent):
        asyncio.run(
            wait_for_full_article_content(
                cast(Any, page),
                timeout_ms=1_000,
                min_chars=1200,
                scroll_steps=1,
                scroll_pause_seconds=0.01,
                stable_rounds=1,
                max_scroll_passes=1,
            )
        )
