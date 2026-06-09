"""Human-like pacing and Medium bot-challenge detection."""

from __future__ import annotations

import asyncio
import random
from time import monotonic

from playwright.async_api import Page

HUMAN_VERIFICATION_PHRASES: tuple[str, ...] = (
    "verify you are human",
    "verify you're human",
    "confirm you are human",
    "confirm you're human",
    "are you a human",
    "are you human",
    "unusual traffic",
    "security check",
    "captcha",
    "recaptcha",
    "robot check",
    "not a robot",
)


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
    """Return whether visible page text looks like a human-verification challenge."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in HUMAN_VERIFICATION_PHRASES)


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


async def detect_human_verification(page: Page) -> bool:
    """Return whether the current page shows a human-verification challenge."""
    for phrase in HUMAN_VERIFICATION_PHRASES:
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
    return page_text_indicates_human_verification(body_text)


async def ensure_no_human_verification(page: Page) -> None:
    """Raise ``HumanVerificationRequired`` when Medium shows a bot challenge."""
    if await detect_human_verification(page):
        raise HumanVerificationRequired(
            "Medium requested human verification. Stop the run, complete the challenge "
            "manually in Brave, then resume later with a smaller --limit."
        )
