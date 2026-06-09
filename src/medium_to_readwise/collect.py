"""Medium Reading List URL discovery."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from src.medium_to_readwise.urls import dedupe_urls, is_medium_article_url, normalize_article_url

LogCallback = Callable[[str], None]


def extract_article_urls_from_html(html: str, *, base_url: str) -> list[str]:
    """Extract normalized article-like links from a Reading List HTML snapshot."""
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", "")).strip()
        if not href:
            continue
        normalized = normalize_article_url(href, base_url=base_url)
        if is_medium_article_url(normalized):
            urls.append(normalized)
    return dedupe_urls(urls)


async def extract_article_urls_from_page(page: Any, *, base_url: str) -> list[str]:
    """Extract normalized article-like links from the current browser page."""
    html = await page.content()
    return extract_article_urls_from_html(html, base_url=base_url)


async def collect_reading_list_urls(
    page: Any,
    *,
    reading_list_url: str,
    stable_rounds: int = 3,
    scroll_delay_seconds: float = 1.0,
    log: LogCallback | None = None,
) -> list[str]:
    """Scroll the Reading List until discoveries stabilize and return article URLs."""
    await page.goto(reading_list_url, wait_until="domcontentloaded")
    await page.wait_for_selector("body", timeout=30_000)
    seen: list[str] = []
    stable_count = 0
    previous_count = 0

    while stable_count < stable_rounds:
        current = await extract_article_urls_from_page(page, base_url=reading_list_url)
        merged = dedupe_urls([*seen, *current])
        if len(merged) == previous_count:
            stable_count += 1
        else:
            stable_count = 0
            previous_count = len(merged)
            for url in merged:
                if url not in seen and log is not None:
                    log(f"discovered {url}")
        seen = merged
        await page.mouse.wheel(0, 3000)
        await asyncio.sleep(scroll_delay_seconds)

    return seen
