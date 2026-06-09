"""Remove saved articles from a Medium Reading List."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from playwright.async_api import Locator, Page

from src.medium_to_readwise.urls import article_slug_from_path, normalize_article_url

MENU_BUTTON_PATTERN = re.compile(r"more|option|menu", re.IGNORECASE)
REMOVE_ITEM_LABEL = "Remove item"
REMOVE_ACTION_PATTERN = re.compile(
    r"remove item|remove from (reading )?list|delete story|delete",
    re.IGNORECASE,
)
CONFIRM_BUTTON_PATTERN = re.compile(r"remove|delete|confirm", re.IGNORECASE)


def article_href_fragment(article_url: str) -> str:
    """Return a stable href fragment for locating a list entry."""
    canonical = normalize_article_url(article_url)
    slug = article_slug_from_path(urlsplit(canonical).path)
    if slug:
        return slug
    return urlsplit(canonical).path.rstrip("/").split("/")[-1]


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
    ):
        row = link.locator(xpath)
        if await row.count() > 0:
            return row
    return link.locator("xpath=ancestor::div[1]")


async def open_entry_menu(page: Page, row: Locator) -> None:
    """Open the three-dot menu for one Reading List entry."""
    menu = row.get_by_role("button", name=MENU_BUTTON_PATTERN)
    if await menu.count() == 0:
        menu = row.locator('button[aria-label*="more" i], button[aria-label*="option" i]')
    await menu.first.click(timeout=5_000)


async def click_remove_action(page: Page) -> None:
    """Click the remove/delete action in the open entry menu."""
    action = page.get_by_text(REMOVE_ITEM_LABEL, exact=True)
    if await action.count() == 0:
        action = page.get_by_role("menuitem", name=REMOVE_ACTION_PATTERN)
    if await action.count() == 0:
        action = page.get_by_role("button", name=REMOVE_ACTION_PATTERN)
    await action.first.click(timeout=5_000)


async def confirm_remove_if_needed(page: Page) -> None:
    """Confirm a Medium remove/delete dialog when one appears."""
    confirm = page.get_by_role("button", name=CONFIRM_BUTTON_PATTERN)
    if await confirm.count() == 0:
        return
    try:
        await confirm.first.click(timeout=2_000)
    except Exception:
        return


async def remove_article_from_reading_list(
    page: Page,
    *,
    reading_list_url: str,
    article_url: str,
) -> None:
    """Delete one article from the configured Medium Reading List."""
    await page.goto(reading_list_url, wait_until="domcontentloaded")
    await page.wait_for_selector("body", timeout=30_000)
    row = await find_list_entry_for_article(page, article_url=article_url)
    await open_entry_menu(page, row)
    await click_remove_action(page)
    await confirm_remove_if_needed(page)
