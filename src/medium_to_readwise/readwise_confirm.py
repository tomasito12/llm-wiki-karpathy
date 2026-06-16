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
    "already saved",
    "already in reader",
    "already in your library",
    "in your library",
)

READWISE_EXTENSION_BAR_PHRASES: tuple[str, ...] = (
    "open in reader",
    "open in readwise",
    "hide the extension bar",
    "move the document",
)

READWISE_EXTENSION_SELECTORS: tuple[str, ...] = (
    '[class*="readwise"]',
    '[class*="Readwise"]',
    '[id*="readwise"]',
    '[class*="rwreader"]',
    "[data-rw]",
)

VALID_READWISE_CONFIRM_MODES: frozenset[str] = frozenset(
    {"text", "extension", "relaxed"},
)
DEFAULT_READWISE_CONFIRM_MODE = "relaxed"


def normalize_readwise_confirm_mode(mode: str) -> str:
    """Return a supported Readwise confirmation mode."""
    normalized = mode.strip().lower()
    if normalized not in VALID_READWISE_CONFIRM_MODES:
        supported = ", ".join(sorted(VALID_READWISE_CONFIRM_MODES))
        msg = f"Unsupported Readwise confirm mode: {mode}. Use one of: {supported}"
        raise ValueError(msg)
    return normalized


def page_text_indicates_readwise_save(text: str) -> bool:
    """Return whether visible page text indicates a successful Readwise save."""
    lowered = text.lower()
    if any(phrase in lowered for phrase in READWISE_SUCCESS_PHRASES):
        return True
    return any(phrase in lowered for phrase in READWISE_EXTENSION_BAR_PHRASES)


async def detect_readwise_extension_ui(page: Page) -> bool:
    """Return whether Readwise extension UI is visible inside the page."""
    for selector in READWISE_EXTENSION_SELECTORS:
        locator = page.locator(selector)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    return False


async def detect_readwise_save_confirmation(
    page: Page,
    *,
    mode: str = DEFAULT_READWISE_CONFIRM_MODE,
) -> bool:
    """Return whether the current page indicates a successful Readwise save."""
    confirm_mode = normalize_readwise_confirm_mode(mode)
    for phrase in (*READWISE_SUCCESS_PHRASES, *READWISE_EXTENSION_BAR_PHRASES):
        locator = page.get_by_text(phrase, exact=False)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    if confirm_mode in {"extension", "relaxed"}:
        if await detect_readwise_extension_ui(page):
            return True
    try:
        body_text = await page.locator("body").inner_text()
    except Exception:
        body_text = ""
    return page_text_indicates_readwise_save(body_text)


async def wait_for_readwise_save(
    page: Page,
    *,
    timeout_seconds: float = 15.0,
    mode: str = DEFAULT_READWISE_CONFIRM_MODE,
    trust_after_timeout: bool = False,
) -> tuple[bool, str]:
    """Poll until Readwise save confirmation is visible or relaxed mode times out."""
    confirm_mode = normalize_readwise_confirm_mode(mode)
    allow_trust = trust_after_timeout or confirm_mode == "relaxed"
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        if await detect_readwise_save_confirmation(page, mode=confirm_mode):
            return True, "visible"
        await asyncio.sleep(0.5)
    if allow_trust:
        return True, "relaxed_timeout"
    return False, "none"
