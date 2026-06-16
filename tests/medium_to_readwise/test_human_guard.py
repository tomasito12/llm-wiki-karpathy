"""Tests for human-like pacing and bot-challenge detection."""

from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest

from src.medium_to_readwise.human_guard import (
    HourlyRateLimiter,
    HumanVerificationRequired,
    RateLimitReached,
    detect_human_verification,
    ensure_no_human_verification,
    jittered_delay_seconds,
    page_text_indicates_human_verification,
    wait_for_manual_human_verification,
)


def test_page_text_indicates_human_verification_matches_medium_prompt() -> None:
    """Medium's human verification prompt is detected from visible text."""
    text = "Verify you are human to continue reading on Medium."
    assert page_text_indicates_human_verification(text) is True


def test_page_text_ignores_generic_ai_article_phrases() -> None:
    """Article copy about humans or bots must not trigger challenge detection."""
    article = (
        "Are you human? AI agents are not robots. "
        "Security checks and captcha systems are common in production."
    )
    assert page_text_indicates_human_verification(article) is False


class FakeChallengeLocator:
    """Minimal locator for challenge-detection tests."""

    def __init__(
        self,
        *,
        count: int = 0,
        visible: bool = False,
        inside_article: bool = False,
    ) -> None:
        """Initialize locator state."""
        self.count_value = count
        self.visible = visible
        self.inside_article = inside_article

    @property
    def first(self) -> FakeChallengeLocator:
        """Return the first matching locator."""
        return self

    async def count(self) -> int:
        """Return how many elements match."""
        return self.count_value

    async def is_visible(self) -> bool:
        """Return whether the element is visible."""
        return self.visible and self.count_value > 0

    async def evaluate(self, _script: str) -> bool:
        """Return whether the match sits inside article content."""
        return self.inside_article


class FakeChallengePage:
    """Minimal page object for challenge-detection tests."""

    def __init__(
        self,
        *,
        non_article_text: str = "",
        iframe_visible: bool = False,
        prompt_visible: bool = False,
        prompt_inside_article: bool = False,
    ) -> None:
        """Initialize fake page behavior."""
        self.non_article_text = non_article_text
        self.iframe_visible = iframe_visible
        self.prompt_visible = prompt_visible
        self.prompt_inside_article = prompt_inside_article

    def locator(self, selector: str) -> FakeChallengeLocator | FakeChallengeContainer:
        """Return a fake locator for challenge widgets."""
        if "recaptcha" in selector or "cloudflare" in selector or "g-recaptcha" in selector:
            return FakeChallengeLocator(
                count=1 if self.iframe_visible else 0,
                visible=self.iframe_visible,
            )
        if selector in {'[role="dialog"]', '[role="alertdialog"]'}:
            return FakeChallengeContainer(
                page=self,
                selector=selector,
                prompt_visible=self.prompt_visible and not self.prompt_inside_article,
            )
        return FakeChallengeLocator()

    def get_by_text(self, _phrase: str, *, exact: bool = False) -> FakeChallengeLocator:
        """Return a fake text locator."""
        del exact
        return FakeChallengeLocator(
            count=1 if self.prompt_visible else 0,
            visible=self.prompt_visible,
            inside_article=self.prompt_inside_article,
        )

    async def evaluate(self, script: str) -> str:
        """Return non-article page text."""
        del script
        return self.non_article_text


class FakeChallengeContainer:
    """Locator scoped to a challenge context container."""

    def __init__(self, *, page: FakeChallengePage, selector: str, prompt_visible: bool) -> None:
        """Initialize container locator state."""
        self.page = page
        self.selector = selector
        self.prompt_visible = prompt_visible

    def get_by_text(self, _phrase: str, *, exact: bool = False) -> FakeChallengeLocator:
        """Return prompt text inside the container."""
        del exact
        return FakeChallengeLocator(
            count=1 if self.prompt_visible else 0,
            visible=self.prompt_visible,
        )


def test_detect_human_verification_ignores_prompt_inside_article() -> None:
    """Challenge phrases inside article bodies are ignored."""
    page = FakeChallengePage(
        prompt_visible=True,
        prompt_inside_article=True,
    )
    assert asyncio.run(detect_human_verification(cast(Any, page))) is False


def test_detect_human_verification_matches_visible_challenge_widget() -> None:
    """Visible reCAPTCHA/Cloudflare widgets count as a challenge."""
    page = FakeChallengePage(iframe_visible=True)
    assert asyncio.run(detect_human_verification(cast(Any, page))) is True


def test_detect_human_verification_matches_prompt_outside_article() -> None:
    """Medium's verify prompt outside article content is detected."""
    page = FakeChallengePage(
        prompt_visible=True,
        prompt_inside_article=False,
    )
    assert asyncio.run(detect_human_verification(cast(Any, page))) is True


def test_jittered_delay_seconds_stays_within_bounds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Jittered delays stay inside the configured +/- window."""
    monkeypatch.setattr(
        "src.medium_to_readwise.human_guard.random.uniform",
        lambda low, high: (low + high) / 2,
    )
    assert jittered_delay_seconds(8.0, jitter_seconds=3.0) == 8.0


def test_hourly_rate_limiter_blocks_after_cap() -> None:
    """The hourly cap stops additional article starts."""
    limiter = HourlyRateLimiter(max_per_hour=2)
    limiter.record_start(now=100.0)
    limiter.record_start(now=200.0)
    assert limiter.can_start(now=300.0) is False
    with pytest.raises(RateLimitReached):
        limiter.ensure_can_start(now=300.0)


def test_hourly_rate_limiter_disabled_when_max_is_zero() -> None:
    """A max of zero disables hourly rate limiting."""
    limiter = HourlyRateLimiter(max_per_hour=0)
    for stamp in range(50):
        limiter.record_start(now=float(stamp))
    assert limiter.can_start(now=999.0) is True


def test_human_verification_required_has_actionable_message() -> None:
    """Human verification errors explain that the run should stop."""
    message = str(HumanVerificationRequired())
    assert "human verification" in message.lower()


def test_wait_for_manual_human_verification_resumes_when_challenge_clears(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Manual verification wait polls until the challenge disappears."""
    states = iter([True, True, False])

    async def fake_reason(_page: Any) -> str | None:
        return "challenge" if next(states, False) else None

    async def fake_detect(_page: Any) -> bool:
        return await fake_reason(_page) is not None

    monkeypatch.setattr(
        "src.medium_to_readwise.human_guard.human_verification_match_reason",
        fake_reason,
    )
    monkeypatch.setattr(
        "src.medium_to_readwise.human_guard.detect_human_verification",
        fake_detect,
    )

    async def fake_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(
        "src.medium_to_readwise.human_guard.asyncio.sleep",
        fake_sleep,
    )

    asyncio.run(
        wait_for_manual_human_verification(
            cast(Any, object()),
            timeout_seconds=5.0,
            log=None,
        )
    )


def test_ensure_no_human_verification_waits_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default behavior pauses for manual verification instead of stopping immediately."""
    calls: list[float] = []

    async def fake_wait(
        _page: Any,
        *,
        timeout_seconds: float,
        log: Any,
    ) -> None:
        calls.append(timeout_seconds)

    async def fake_detect(_page: Any) -> bool:
        return True

    monkeypatch.setattr(
        "src.medium_to_readwise.human_guard.detect_human_verification",
        fake_detect,
    )
    monkeypatch.setattr(
        "src.medium_to_readwise.human_guard.wait_for_manual_human_verification",
        fake_wait,
    )

    asyncio.run(
        ensure_no_human_verification(
            cast(Any, object()),
            verification_wait_seconds=120.0,
        )
    )
    assert calls == [120.0]
