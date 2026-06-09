"""Tests for human-like pacing and bot-challenge detection."""

from __future__ import annotations

import pytest

from src.medium_to_readwise.human_guard import (
    HourlyRateLimiter,
    HumanVerificationRequired,
    RateLimitReached,
    jittered_delay_seconds,
    page_text_indicates_human_verification,
)


def test_page_text_indicates_human_verification_matches_medium_prompt() -> None:
    """Medium's human verification prompt is detected from visible text."""
    text = "Verify you are human to continue reading on Medium."
    assert page_text_indicates_human_verification(text) is True


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
