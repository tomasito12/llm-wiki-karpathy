"""Per-article browser automation for saving Medium articles to Readwise."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from time import monotonic
from typing import Any

from playwright.async_api import Page

from src.medium_to_readwise.human_guard import (
    HumanVerificationRequired,
    ensure_no_human_verification,
    sleep_with_jitter,
)
from src.medium_to_readwise.reading_list_remove import remove_article_from_reading_list
from src.medium_to_readwise.readwise_confirm import wait_for_readwise_save
from src.medium_to_readwise.shortcut import (
    DEFAULT_BROWSER_APP_NAME,
    DEFAULT_READWISE_SHORTCUT,
    default_shortcut_mode,
    playwright_shortcut_expression,
    trigger_system_shortcut,
)
from src.medium_to_readwise.state import screenshot_path, utc_now_iso
from src.medium_to_readwise.urls import normalize_article_url

LogCallback = Callable[[str], None]


async def wait_for_article_content(page: Page, *, timeout_ms: int = 60_000) -> None:
    """Wait until Medium has rendered a substantial article body."""
    await page.wait_for_selector("article", timeout=min(timeout_ms, 30_000))
    await page.wait_for_function(
        """
        () => {
          const article = document.querySelector("article");
          return article && article.innerText && article.innerText.trim().length > 400;
        }
        """,
        timeout=timeout_ms,
    )


async def dismiss_page_overlays(page: Page) -> None:
    """Close Medium image zoom/lightbox overlays before sending shortcuts."""
    for _ in range(2):
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.2)


async def focus_article_text(page: Page) -> None:
    """Focus readable article text instead of hero images that open Medium zoom."""
    selectors = (
        "article h1",
        "article p",
        "article section p",
        "[role='main'] h1",
        "[role='main'] p",
        "body",
    )
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            await locator.scroll_into_view_if_needed(timeout=3_000)
            await locator.click(timeout=3_000)
            return
        except Exception:
            continue


async def trigger_readwise_save(
    page: Page,
    *,
    shortcut: str,
    shortcut_mode: str,
    browser_app_name: str,
) -> None:
    """Trigger the configured Readwise save shortcut."""
    await page.bring_to_front()
    if shortcut_mode == "system":
        trigger_system_shortcut(shortcut, browser_app_name=browser_app_name)
        return
    if shortcut_mode == "playwright":
        await page.keyboard.press(playwright_shortcut_expression(shortcut))
        return
    msg = f"Unsupported shortcut mode: {shortcut_mode}"
    raise ValueError(msg)


async def capture_failure_screenshot(page: Page, state_dir: Path, *, url: str) -> str | None:
    """Save a failure screenshot and return its path, or ``None`` if capture fails."""
    path = screenshot_path(state_dir, url=url)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=path, full_page=True)
    except Exception:
        return None
    return str(path)


async def process_article_once(
    page: Page,
    *,
    url: str,
    delay_seconds: float,
    jitter_seconds: float = 0.0,
    dry_run: bool,
    reading_list_url: str,
    remove_from_list: bool = True,
    readwise_confirm_timeout: float = 15.0,
    readwise_shortcut: str = DEFAULT_READWISE_SHORTCUT,
    shortcut_mode: str = default_shortcut_mode(),
    browser_app_name: str = DEFAULT_BROWSER_APP_NAME,
) -> dict[str, Any]:
    """Visit one article URL, save to Readwise, and optionally remove it from the list."""
    started = monotonic()
    await page.goto(url, wait_until="domcontentloaded")
    await ensure_no_human_verification(page)
    await wait_for_article_content(page)
    await dismiss_page_overlays(page)
    await focus_article_text(page)
    final_url = page.url
    readwise_saved = False
    removed_from_list = False
    removal_error: str | None = None
    if not dry_run:
        await trigger_readwise_save(
            page,
            shortcut=readwise_shortcut,
            shortcut_mode=shortcut_mode,
            browser_app_name=browser_app_name,
        )
        await sleep_with_jitter(delay_seconds, jitter_seconds=jitter_seconds)
        readwise_saved = await wait_for_readwise_save(
            page,
            timeout_seconds=readwise_confirm_timeout,
        )
        if not readwise_saved:
            elapsed = monotonic() - started
            return {
                "url": url,
                "canonical_url": normalize_article_url(url),
                "final_url": final_url,
                "status": "failed",
                "processed_at": utc_now_iso(),
                "attempts": 1,
                "elapsed_seconds": round(elapsed, 3),
                "readwise_saved": False,
                "removed_from_list": False,
                "error": "Readwise save confirmation not detected",
            }
        if remove_from_list:
            try:
                await remove_article_from_reading_list(
                    page,
                    reading_list_url=reading_list_url,
                    article_url=url,
                )
                await ensure_no_human_verification(page)
                removed_from_list = True
            except HumanVerificationRequired:
                raise
            except Exception as exc:
                removal_error = f"{type(exc).__name__}: {exc}"
    elapsed = monotonic() - started
    return {
        "url": url,
        "canonical_url": normalize_article_url(url),
        "final_url": final_url,
        "status": "ok",
        "processed_at": utc_now_iso(),
        "attempts": 1,
        "elapsed_seconds": round(elapsed, 3),
        "readwise_saved": readwise_saved or dry_run,
        "removed_from_list": removed_from_list,
        "error": removal_error,
    }


async def process_article_with_retries(
    page: Page,
    *,
    url: str,
    state_dir: Path,
    reading_list_url: str,
    delay_seconds: float,
    jitter_seconds: float = 0.0,
    dry_run: bool,
    max_retries: int,
    retry_delay_seconds: float,
    remove_from_list: bool = True,
    readwise_confirm_timeout: float = 15.0,
    readwise_shortcut: str = DEFAULT_READWISE_SHORTCUT,
    shortcut_mode: str = default_shortcut_mode(),
    browser_app_name: str = DEFAULT_BROWSER_APP_NAME,
    log: LogCallback | None = None,
) -> dict[str, Any]:
    """Process one article with retry and screenshot handling."""
    started = monotonic()
    attempts = 0
    last_error: str | None = None
    for attempt in range(max_retries + 1):
        attempts = attempt + 1
        try:
            if log is not None:
                log(f"processing {url} attempt={attempts}")
            result = await process_article_once(
                page,
                url=url,
                delay_seconds=delay_seconds,
                jitter_seconds=jitter_seconds,
                dry_run=dry_run,
                reading_list_url=reading_list_url,
                remove_from_list=remove_from_list,
                readwise_confirm_timeout=readwise_confirm_timeout,
                readwise_shortcut=readwise_shortcut,
                shortcut_mode=shortcut_mode,
                browser_app_name=browser_app_name,
            )
            result["attempts"] = attempts
            if result["status"] == "ok":
                return result
            last_error = str(result.get("error") or "processing failed")
            if log is not None:
                log(f"failed {url} attempt={attempts} error={last_error}")
            if attempt < max_retries:
                await asyncio.sleep(retry_delay_seconds)
                continue
            return result
        except HumanVerificationRequired:
            raise
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if log is not None:
                log(f"failed {url} attempt={attempts} error={last_error}")
            if attempt < max_retries:
                await asyncio.sleep(retry_delay_seconds)

    screenshot = await capture_failure_screenshot(page, state_dir, url=url)
    elapsed = monotonic() - started
    return {
        "url": url,
        "canonical_url": normalize_article_url(url),
        "final_url": page.url,
        "status": "failed",
        "processed_at": utc_now_iso(),
        "attempts": attempts,
        "elapsed_seconds": round(elapsed, 3),
        "error": last_error,
        "screenshot": screenshot,
    }
