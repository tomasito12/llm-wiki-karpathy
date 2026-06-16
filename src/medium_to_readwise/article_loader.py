"""Wait for Medium articles to fully render before Readwise captures them."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from time import monotonic

from playwright.async_api import Page

PAYWALL_GATE_PHRASES: tuple[str, ...] = (
    "continue reading this story",
    "continue reading for free",
    "this member-only story",
    "story is for members",
    "member-only story",
    "upgrade to read the full story",
    "become a member to read",
    "read this story for free",
)

DEFAULT_MIN_ARTICLE_CHARS = 1200
DEFAULT_SCROLL_STEPS = 6
DEFAULT_SCROLL_PAUSE_SECONDS = 0.35
DEFAULT_STABLE_ROUNDS = 2
DEFAULT_MAX_SCROLL_PASSES = 4

LogCallback = Callable[[str], None]


class PartialArticleContent(RuntimeError):
    """Raised when Medium still shows a paywall gate or a thin article body."""

    def __init__(
        self,
        message: str = (
            "Medium article body still looks truncated (paywall gate or lazy-load). "
            "Sign in, open the article manually once, then retry."
        ),
    ) -> None:
        """Initialize with a user-facing message."""
        super().__init__(message)


def _emit_log(log: LogCallback | None, message: str) -> None:
    """Write one loader log line when logging is enabled."""
    if log is not None:
        log(message)


def page_text_indicates_paywall_gate(text: str) -> bool:
    """Return whether visible page text still looks like a Medium paywall gate."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in PAYWALL_GATE_PHRASES)


async def article_text_length(page: Page) -> int:
    """Return the rendered character length of the main Medium article body."""
    try:
        text = await page.locator("article").first.inner_text()
    except Exception:
        return 0
    return len(text.strip())


async def detect_visible_paywall_gate(
    page: Page,
    *,
    min_chars: int = DEFAULT_MIN_ARTICLE_CHARS,
) -> bool:
    """Return whether a paywall gate is visible while the article body is still thin."""
    current_length = await article_text_length(page)
    if current_length >= min_chars:
        return False
    for phrase in PAYWALL_GATE_PHRASES:
        locator = page.get_by_text(phrase, exact=False)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    return False


async def scroll_article_down(
    page: Page,
    *,
    scroll_steps: int = DEFAULT_SCROLL_STEPS,
    scroll_pause_seconds: float = DEFAULT_SCROLL_PAUSE_SECONDS,
) -> None:
    """Scroll progressively down the page without jumping back to the top."""
    for _ in range(max(scroll_steps, 1)):
        await page.evaluate(
            """
            () => {
              window.scrollBy(0, Math.max(window.innerHeight * 0.9, 500));
            }
            """
        )
        await asyncio.sleep(scroll_pause_seconds)


async def scroll_article_to_top(page: Page) -> None:
    """Return the viewport to the top once loading is complete."""
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.2)


async def wait_for_full_article_content(
    page: Page,
    *,
    timeout_ms: int = 90_000,
    min_chars: int = DEFAULT_MIN_ARTICLE_CHARS,
    scroll_steps: int = DEFAULT_SCROLL_STEPS,
    scroll_pause_seconds: float = DEFAULT_SCROLL_PAUSE_SECONDS,
    stable_rounds: int = DEFAULT_STABLE_ROUNDS,
    max_scroll_passes: int = DEFAULT_MAX_SCROLL_PASSES,
    log: LogCallback | None = None,
) -> int:
    """Scroll down in passes until the article body is long enough and stable."""
    await page.wait_for_selector("article", timeout=min(timeout_ms, 30_000))
    deadline = monotonic() + (timeout_ms / 1000.0)
    previous_length = -1
    stable_count = 0
    final_length = await article_text_length(page)
    _emit_log(log, f"article initial length: {final_length} chars")

    for pass_index in range(1, max(max_scroll_passes, 1) + 1):
        if monotonic() >= deadline:
            break
        if await detect_visible_paywall_gate(page, min_chars=min_chars):
            raise PartialArticleContent(
                f"Visible Medium paywall gate with only {final_length} chars rendered."
            )
        _emit_log(log, f"article scroll pass {pass_index}/{max_scroll_passes}")
        await scroll_article_down(
            page,
            scroll_steps=scroll_steps,
            scroll_pause_seconds=scroll_pause_seconds,
        )
        final_length = await article_text_length(page)
        _emit_log(log, f"article length after scroll pass {pass_index}: {final_length} chars")
        if final_length >= min_chars:
            if final_length == previous_length:
                stable_count += 1
            else:
                stable_count = 0
            previous_length = final_length
            if stable_count >= stable_rounds:
                await scroll_article_to_top(page)
                _emit_log(log, f"article body stable at {final_length} chars")
                return final_length
        await asyncio.sleep(0.25)

    if final_length >= min_chars and not await detect_visible_paywall_gate(
        page, min_chars=min_chars
    ):
        await scroll_article_to_top(page)
        _emit_log(
            log,
            f"article body accepted after {max_scroll_passes} scroll passes ({final_length} chars)",
        )
        return final_length

    raise PartialArticleContent(
        f"Article body length={final_length} chars; expected at least {min_chars} "
        "without a visible paywall gate."
    )
