"""Human-like pacing and Medium bot-challenge detection."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Callable
from time import monotonic

from playwright.async_api import Page

# Medium / Cloudflare challenge prompts — avoid generic words that appear in articles.
STRICT_CHALLENGE_PHRASES: tuple[str, ...] = (
    "verify you are human",
    "verify you're human",
    "confirm you are human",
    "confirm you're human",
    "checking your browser before accessing",
    "unusual traffic from your computer network",
    "unusual traffic from your network",
    "unusual traffic",
    "needs to review the security of your connection",
)

CHALLENGE_UI_SELECTORS: tuple[str, ...] = (
    'iframe[src*="recaptcha/api2/anchor"]',
    'iframe[src*="recaptcha/enterprise/anchor"]',
    'iframe[src*="challenges.cloudflare.com"]',
    'iframe[title*="recaptcha" i]',
    "div.g-recaptcha",
    "div.h-captcha",
    "#challenge-running",
    "#challenge-stage",
)

CHALLENGE_CONTEXT_SELECTORS: tuple[str, ...] = (
    '[role="dialog"]',
    '[role="alertdialog"]',
    "#challenge-running",
    "#challenge-stage",
)

NON_ARTICLE_TEXT_JS = """
() => {
  const clone = document.body.cloneNode(true);
  for (const el of clone.querySelectorAll('article, [role="article"]')) {
    el.remove();
  }
  return (clone.innerText || '').slice(0, 50000);
}
"""

IS_INSIDE_ARTICLE_JS = """
(el) => !!el.closest('article, [role="article"]')
"""

DEFAULT_VERIFICATION_WAIT_SECONDS = 600.0
VERIFICATION_POLL_SECONDS = 3.0

LogCallback = Callable[[str], None]


class HumanVerificationRequired(RuntimeError):
    """Raised when Medium presents a human-verification challenge."""

    def __init__(self, message: str = "Medium human verification challenge detected") -> None:
        """Initialize with a user-facing message."""
        super().__init__(message)


class RateLimitReached(RuntimeError):
    """Raised when the configured hourly processing cap is reached."""

    def __init__(self, *, max_per_hour: int, retry_after_seconds: float) -> None:
        """Initialize with the configured cap and retry delay."""
        self.max_per_hour = max_per_hour
        self.retry_after_seconds = retry_after_seconds
        minutes = max(1, round(retry_after_seconds / 60))
        super().__init__(
            f"Hourly processing cap reached ({max_per_hour} articles/hour). "
            f"Try again in about {minutes} min."
        )


class HourlyRateLimiter:
    """Track recent article starts and enforce a per-hour cap."""

    def __init__(self, *, max_per_hour: int | None) -> None:
        """Initialize the limiter; ``None`` or ``0`` disables rate limiting."""
        self.max_per_hour = max_per_hour if max_per_hour and max_per_hour > 0 else None
        self._started_at: list[float] = []

    def _prune(self, *, now: float) -> None:
        """Drop article starts older than one hour."""
        cutoff = now - 3600.0
        self._started_at = [stamp for stamp in self._started_at if stamp >= cutoff]

    def can_start(self, *, now: float | None = None) -> bool:
        """Return whether another article can start under the hourly cap."""
        if self.max_per_hour is None:
            return True
        current = monotonic() if now is None else now
        self._prune(now=current)
        return len(self._started_at) < self.max_per_hour

    def seconds_until_available(self, *, now: float | None = None) -> float:
        """Return seconds until the next slot opens."""
        if self.max_per_hour is None:
            return 0.0
        current = monotonic() if now is None else now
        self._prune(now=current)
        if len(self._started_at) < self.max_per_hour:
            return 0.0
        oldest = min(self._started_at)
        return max(0.0, 3600.0 - (current - oldest))

    def record_start(self, *, now: float | None = None) -> None:
        """Record that one article processing started."""
        if self.max_per_hour is None:
            return
        current = monotonic() if now is None else now
        self._prune(now=current)
        self._started_at.append(current)

    def ensure_can_start(self, *, now: float | None = None) -> None:
        """Raise ``RateLimitReached`` when the hourly cap has been exhausted."""
        if self.can_start(now=now):
            return
        retry_after = self.seconds_until_available(now=now)
        assert self.max_per_hour is not None
        raise RateLimitReached(max_per_hour=self.max_per_hour, retry_after_seconds=retry_after)


def page_text_indicates_human_verification(text: str) -> bool:
    """Return whether text looks like a Medium/Cloudflare challenge prompt."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in STRICT_CHALLENGE_PHRASES)


def jittered_delay_seconds(base_seconds: float, *, jitter_seconds: float) -> float:
    """Return a randomized delay around ``base_seconds``."""
    if base_seconds < 0:
        raise ValueError("base_seconds must be zero or greater")
    if jitter_seconds < 0:
        raise ValueError("jitter_seconds must be zero or greater")
    if jitter_seconds == 0:
        return base_seconds
    low = max(0.5, base_seconds - jitter_seconds)
    high = base_seconds + jitter_seconds
    return random.uniform(low, high)


async def sleep_with_jitter(base_seconds: float, *, jitter_seconds: float) -> float:
    """Sleep for a jittered delay and return the actual seconds slept."""
    delay = jittered_delay_seconds(base_seconds, jitter_seconds=jitter_seconds)
    await asyncio.sleep(delay)
    return delay


async def _visible_challenge_ui(page: Page) -> str | None:
    """Return a selector label when a known challenge widget is visible."""
    for selector in CHALLENGE_UI_SELECTORS:
        locator = page.locator(selector)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return f"challenge widget: {selector}"
        except Exception:
            continue
    return None


async def _visible_strict_phrase_outside_article(page: Page) -> str | None:
    """Return a phrase when a strict challenge prompt is visible outside article body."""
    for phrase in STRICT_CHALLENGE_PHRASES:
        locator = page.get_by_text(phrase, exact=False)
        try:
            if await locator.count() == 0 or not await locator.first.is_visible():
                continue
            inside_article = await locator.first.evaluate(IS_INSIDE_ARTICLE_JS)
            if not inside_article:
                return f"prompt text: {phrase!r}"
        except Exception:
            continue
    return None


async def _non_article_page_text(page: Page) -> str:
    """Return visible page text with article bodies removed."""
    try:
        text = await page.evaluate(NON_ARTICLE_TEXT_JS)
    except Exception:
        text = ""
    return str(text)


async def _strict_phrase_in_challenge_context(page: Page) -> str | None:
    """Return a phrase when challenge copy appears in a dialog or challenge shell."""
    for container_selector in CHALLENGE_CONTEXT_SELECTORS:
        for phrase in STRICT_CHALLENGE_PHRASES:
            try:
                locator = page.locator(container_selector).get_by_text(phrase, exact=False)
                if await locator.count() == 0 or not await locator.first.is_visible():
                    continue
                inside_article = await locator.first.evaluate(IS_INSIDE_ARTICLE_JS)
                if inside_article:
                    continue
                return f"context {container_selector!r}: {phrase!r}"
            except Exception:
                continue
    return None


async def human_verification_match_reason(page: Page) -> str | None:
    """Return why a page looks like a human-verification challenge, if at all."""
    ui_match = await _visible_challenge_ui(page)
    if ui_match is not None:
        return ui_match
    phrase_match = await _visible_strict_phrase_outside_article(page)
    if phrase_match is not None:
        return phrase_match
    context_match = await _strict_phrase_in_challenge_context(page)
    if context_match is not None:
        return context_match
    non_article_text = await _non_article_page_text(page)
    if page_text_indicates_human_verification(non_article_text):
        return "non-article page text matched a challenge prompt"
    return None


async def detect_human_verification(page: Page) -> bool:
    """Return whether the current page shows a human-verification challenge."""
    return await human_verification_match_reason(page) is not None


def _emit_log(log: LogCallback | None, message: str) -> None:
    """Write one human-guard log line when logging is enabled."""
    if log is not None:
        log(message)


async def wait_for_manual_human_verification(
    page: Page,
    *,
    timeout_seconds: float,
    log: LogCallback | None = None,
) -> None:
    """Pause until the user clears a Medium challenge manually in Brave."""
    reason = await human_verification_match_reason(page)
    detail = f" ({reason})" if reason else ""
    _emit_log(
        log,
        (
            "Medium human verification detected — complete the challenge manually in Brave. "
            f"Automation will resume when it clears (up to {timeout_seconds:.0f}s)."
            f"{detail}"
        ),
    )
    deadline = monotonic() + timeout_seconds
    next_status_log = monotonic()
    while monotonic() < deadline:
        if not await detect_human_verification(page):
            _emit_log(log, "human verification cleared; continuing")
            return
        if monotonic() >= next_status_log:
            remaining = max(0.0, deadline - monotonic())
            _emit_log(log, f"waiting for manual human verification ({remaining:.0f}s left)")
            next_status_log = monotonic() + 15.0
        await asyncio.sleep(VERIFICATION_POLL_SECONDS)
    msg = f"Timed out after {timeout_seconds:.0f}s waiting for manual human verification."
    raise HumanVerificationRequired(msg)


async def ensure_no_human_verification(
    page: Page,
    *,
    verification_wait_seconds: float = DEFAULT_VERIFICATION_WAIT_SECONDS,
    log: LogCallback | None = None,
) -> None:
    """Wait for manual verification or raise when Medium shows a bot challenge."""
    if not await detect_human_verification(page):
        return
    if verification_wait_seconds <= 0:
        raise HumanVerificationRequired(
            "Medium requested human verification. Re-run with a positive "
            "--verification-wait to pause for manual completion in Brave."
        )
    await wait_for_manual_human_verification(
        page,
        timeout_seconds=verification_wait_seconds,
        log=log,
    )
