"""Tests for Medium Reading List URL extraction."""

from __future__ import annotations

import asyncio

from src.medium_to_readwise.collect import (
    collect_reading_list_urls,
    extract_article_urls_from_html,
    extract_article_urls_from_page,
)


class FakeMouse:
    """Minimal async-compatible mouse for scroll-loop tests."""

    def __init__(self) -> None:
        """Initialize scroll counter."""
        self.scrolls = 0

    async def wheel(self, _x: int, _y: int) -> None:
        """Record one scroll call."""
        self.scrolls += 1


class FakePage:
    """Minimal async-compatible page for collection tests."""

    def __init__(self, html: str) -> None:
        """Initialize the fake page with static HTML."""
        self.html = html
        self.mouse = FakeMouse()
        self.goto_url = ""

    async def goto(self, url: str, *, wait_until: str) -> None:
        """Record navigation arguments."""
        self.goto_url = f"{url}|{wait_until}"

    async def wait_for_selector(self, _selector: str, *, timeout: int) -> None:
        """Pretend the selector appeared."""
        assert timeout > 0

    async def content(self) -> str:
        """Return the static page HTML."""
        return self.html


def test_extract_article_urls_from_html_filters_navigation_links() -> None:
    """Only article-like links are returned from Reading List markup."""
    html = """
    <a href="/@user/story-abc12345?utm_source=list">Story</a>
    <a href="/@user">Profile</a>
    <a href="/search?q=agents">Search</a>
    <a href="https://medium.com/@user/story-abc12345">Duplicate</a>
    <a href="https://johndevore.medium.com/cigarettes-are-bad-i-miss-them-3e00ad67018b">Subdomain</a>
    """
    assert extract_article_urls_from_html(
        html, base_url="https://medium.com/@plischke81/list/reading-list"
    ) == [
        "https://medium.com/@user/story-abc12345",
        "https://johndevore.medium.com/cigarettes-are-bad-i-miss-them-3e00ad67018b",
    ]


def test_extract_article_urls_from_page_uses_current_html() -> None:
    """Page extraction reads the browser HTML snapshot."""
    page = FakePage('<a href="/@user/story-abc12345">Story</a>')
    urls = asyncio.run(
        extract_article_urls_from_page(
            page, base_url="https://medium.com/@plischke81/list/reading-list"
        )
    )
    assert urls == ["https://medium.com/@user/story-abc12345"]


def test_collect_reading_list_urls_scrolls_until_stable() -> None:
    """The collection loop stops after repeated stable URL counts."""
    page = FakePage('<a href="/@user/story-abc12345">Story</a>')
    logs: list[str] = []
    urls = asyncio.run(
        collect_reading_list_urls(
            page,
            reading_list_url="https://medium.com/@plischke81/list/reading-list",
            stable_rounds=1,
            scroll_delay_seconds=0,
            log=logs.append,
        )
    )
    assert urls == ["https://medium.com/@user/story-abc12345"]
    assert logs == ["discovered https://medium.com/@user/story-abc12345"]
    assert page.goto_url == "https://medium.com/@plischke81/list/reading-list|domcontentloaded"
    assert page.mouse.scrolls >= 2
