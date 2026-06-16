"""Remove saved articles from a Medium Reading List."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from urllib.parse import urlsplit

from playwright.async_api import Locator, Page

from src.medium_to_readwise.urls import article_slug_from_path, normalize_article_url

LogCallback = Callable[[str], None]

MENU_BUTTON_PATTERN = re.compile(r"more|option|menu", re.IGNORECASE)
REMOVE_ITEM_LABEL = "Remove item"
REMOVE_ACTION_PATTERN = re.compile(
    r"^Remove item$|^Remove from (reading )?list$|^Delete story$",
    re.IGNORECASE,
)
CONFIRM_REMOVE_PATTERN = re.compile(r"^Remove$|^Delete$|^Confirm$", re.IGNORECASE)


def article_href_fragment(article_url: str) -> str:
    """Return a stable href fragment for locating a list entry."""
    canonical = normalize_article_url(article_url)
    slug = article_slug_from_path(urlsplit(canonical).path)
    if slug:
        return slug
    return urlsplit(canonical).path.rstrip("/").split("/")[-1]


def _emit_log(log: LogCallback | None, message: str) -> None:
    """Write one removal log line when logging is enabled."""
    if log is not None:
        log(message)


async def list_entry_is_present(page: Page, *, article_url: str) -> bool:
    """Return whether the Reading List still contains ``article_url``."""
    fragment = article_href_fragment(article_url)
    locator = page.locator(f'a[href*="{fragment}"]')
    try:
        return await locator.count() > 0
    except Exception:
        return False


async def find_list_entry_for_article(page: Page, *, article_url: str) -> Locator:
    """Locate the Reading List row that links to ``article_url``."""
    fragment = article_href_fragment(article_url)
    link = page.locator(f'a[href*="{fragment}"]').first
    await link.wait_for(state="attached", timeout=15_000)
    await link.scroll_into_view_if_needed(timeout=15_000)
    for xpath in (
        "xpath=ancestor::article[1]",
        "xpath=ancestor::li[1]",
        "xpath=ancestor::div[@role='article'][1]",
        "xpath=ancestor::div[contains(@class,'stream')][1]",
    ):
        row = link.locator(xpath)
        if await row.count() > 0:
            return row
    return link.locator("xpath=ancestor::div[1]")


async def open_entry_menu(page: Page, row: Locator, *, log: LogCallback | None = None) -> None:
    """Open the three-dot menu for one Reading List entry."""
    selectors = (
        'button[aria-label*="more" i]',
        'button[aria-label*="option" i]',
        'button[aria-haspopup="menu"]',
        'button[aria-haspopup="true"]',
    )
    menu = row.get_by_role("button", name=MENU_BUTTON_PATTERN)
    if await menu.count() == 0:
        for selector in selectors:
            candidate = row.locator(selector)
            if await candidate.count() > 0:
                menu = candidate
                break
    if await menu.count() == 0:
        msg = "Could not find the Reading List entry menu button"
        raise RuntimeError(msg)
    _emit_log(log, "opening Reading List entry menu")
    await menu.first.click(timeout=5_000)
    await asyncio.sleep(0.4)


async def click_remove_action(page: Page, *, log: LogCallback | None = None) -> None:
    """Click the remove/delete action in the open entry menu."""
    candidates: list[Locator] = [
        page.get_by_role("menuitem", name=REMOVE_ACTION_PATTERN),
        page.get_by_role("button", name=REMOVE_ACTION_PATTERN),
        page.get_by_text(REMOVE_ITEM_LABEL, exact=False),
        page.locator('[role="menuitem"]').filter(has_text=REMOVE_ITEM_LABEL),
        page.locator("button, a, div").filter(has_text=re.compile(r"^Remove item$", re.I)),
    ]
    for candidate in candidates:
        try:
            if await candidate.count() == 0:
                continue
            target = candidate.first
            if not await target.is_visible():
                continue
            _emit_log(log, "clicking Reading List action: Remove item")
            await target.click(timeout=5_000)
            return
        except Exception:
            continue
    msg = "Could not find the Reading List action 'Remove item'"
    raise RuntimeError(msg)


async def confirm_remove_if_needed(page: Page, *, log: LogCallback | None = None) -> None:
    """Confirm a Medium remove/delete dialog when one appears."""
    confirm = page.get_by_role("button", name=CONFIRM_REMOVE_PATTERN)
    if await confirm.count() == 0:
        return
    try:
        if await confirm.first.is_visible():
            _emit_log(log, "confirming Reading List removal dialog")
            await confirm.first.click(timeout=2_000)
    except Exception:
        return


async def remove_article_from_reading_list(
    page: Page,
    *,
    reading_list_url: str,
    article_url: str,
    log: LogCallback | None = None,
) -> None:
    """Delete one article from the configured Medium Reading List."""
    _emit_log(log, f"navigating to Reading List to remove {article_href_fragment(article_url)}")
    await page.goto(reading_list_url, wait_until="load")
    await page.wait_for_selector("body", timeout=30_000)
    if not await list_entry_is_present(page, article_url=article_url):
        _emit_log(log, "article already absent from Reading List")
        return
    row = await find_list_entry_for_article(page, article_url=article_url)
    await open_entry_menu(page, row, log=log)
    await click_remove_action(page, log=log)
    await confirm_remove_if_needed(page, log=log)
    await asyncio.sleep(0.8)
    await page.goto(reading_list_url, wait_until="load")
    await page.wait_for_selector("body", timeout=30_000)
    if await list_entry_is_present(page, article_url=article_url):
        msg = "Reading List entry still present after clicking Remove item"
        raise RuntimeError(msg)
    _emit_log(log, "confirmed article removed from Reading List")
