"""Detect Readwise Reader save confirmation in the browser."""

from __future__ import annotations

import asyncio
from time import monotonic

from playwright.async_api import Page

READWISE_SUCCESS_PHRASES: tuple[str, ...] = (
    "saved to reader",
    "saved to readwise",
    "added to reader",
    "added to readwise",
    "successfully saved",
    "saved!",
)


def page_text_indicates_readwise_save(text: str) -> bool:
    """Return whether visible page text indicates a successful Readwise save."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in READWISE_SUCCESS_PHRASES)


async def wait_for_readwise_save(page: Page, *, timeout_seconds: float = 15.0) -> bool:
    """Poll the page until Readwise save confirmation becomes visible."""
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        for phrase in READWISE_SUCCESS_PHRASES:
            locator = page.get_by_text(phrase, exact=False)
            try:
                if await locator.count() > 0 and await locator.first.is_visible():
                    return True
            except Exception:
                continue
        try:
            body_text = await page.locator("body").inner_text()
        except Exception:
            body_text = ""
        if page_text_indicates_readwise_save(body_text):
            return True
        await asyncio.sleep(0.5)
    return False
