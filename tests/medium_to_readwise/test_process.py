"""Tests for article processing helpers."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, cast

import pytest

from src.medium_to_readwise.process import (
    capture_failure_screenshot,
    dismiss_page_overlays,
    focus_article_text,
    process_article_once,
    process_article_with_retries,
    trigger_readwise_save,
    wait_for_article_content,
)


class FakeKeyboard:
    """Minimal keyboard object for process tests."""

    def __init__(self) -> None:
        """Initialize pressed key storage."""
        self.pressed: list[str] = []

    async def press(self, key: str) -> None:
        """Record a key press."""
        self.pressed.append(key)


class FakeLocator:
    """Minimal Playwright locator for focus tests."""

    def __init__(
        self,
        page: FakeProcessPage,
        selector: str,
        *,
        match_count: int = 1,
        visible: bool = True,
        inner_text_value: str | None = None,
    ) -> None:
        """Initialize locator state."""
        self.page = page
        self.selector = selector
        self.match_count = match_count
        self.visible = visible
        self.inner_text_value = inner_text_value

    @property
    def first(self) -> FakeLocator:
        """Return the first matching locator."""
        return self

    async def count(self) -> int:
        """Return how many elements match this locator."""
        return self.match_count

    async def is_visible(self) -> bool:
        """Return whether the first matched element is visible."""
        return self.visible and self.match_count > 0

    async def inner_text(self) -> str:
        """Return configured inner text or a generic body placeholder."""
        if self.inner_text_value is not None:
            return self.inner_text_value
        if self.selector == "body":
            return self.page.body_text
        return ""

    async def scroll_into_view_if_needed(self, *, timeout: int) -> None:
        """Pretend the element was scrolled into view."""
        assert timeout > 0
        if self.selector in self.page.fail_selectors:
            raise RuntimeError(f"scroll failed for {self.selector}")

    async def click(self, *, timeout: int) -> None:
        """Record clicks and optionally fail for configured selectors."""
        assert timeout > 0
        if self.selector in self.page.fail_selectors:
            raise RuntimeError(f"click failed for {self.selector}")
        self.page.clicked.append(self.selector)


class FakeProcessPage:
    """Minimal page object for process tests."""

    def __init__(
        self,
        *,
        fail_goto: bool = False,
        fail_selectors: set[str] | None = None,
        body_text: str = "Sample article body text.",
        verification_phrases: set[str] | None = None,
    ) -> None:
        """Initialize fake page behavior."""
        self.url = "about:blank"
        self.keyboard = FakeKeyboard()
        self.fail_goto = fail_goto
        self.fail_selectors = fail_selectors or set()
        self.body_text = body_text
        self.verification_phrases = verification_phrases or set()
        self.clicked: list[str] = []
        self.screenshots: list[Path] = []
        self.brought_to_front = False

    def locator(self, selector: str) -> FakeLocator:
        """Return a fake locator for ``selector``."""
        inner_text_value = self.body_text if selector == "body" else None
        return FakeLocator(self, selector, inner_text_value=inner_text_value)

    def get_by_text(self, phrase: str, *, exact: bool = False) -> FakeLocator:
        """Return a fake text locator for human-verification detection."""
        del exact
        if phrase in self.verification_phrases:
            return FakeLocator(self, f"text={phrase}", match_count=1, visible=True)
        return FakeLocator(self, f"text={phrase}", match_count=0, visible=False)

    async def bring_to_front(self) -> None:
        """Record that the tab was focused."""
        self.brought_to_front = True

    async def goto(self, url: str, *, wait_until: str) -> None:
        """Record navigation or raise a configured failure."""
        if self.fail_goto:
            raise RuntimeError("navigation failed")
        self.url = f"{url}?redirected=1"
        assert wait_until == "domcontentloaded"

    async def wait_for_selector(self, selector: str, *, timeout: int) -> None:
        """Pretend the article selector appeared."""
        assert selector == "article"
        assert timeout > 0

    async def wait_for_function(self, script: str, *, timeout: int) -> None:
        """Pretend the content-length heuristic passed."""
        assert "innerText" in script
        assert timeout > 0

    async def screenshot(self, *, path: Path, full_page: bool) -> None:
        """Record screenshot requests and create a placeholder file."""
        assert full_page is True
        self.screenshots.append(path)
        path.write_text("image", encoding="utf-8")


def test_wait_for_article_content_uses_article_heuristic() -> None:
    """Article readiness waits for both selector and rendered text."""
    asyncio.run(wait_for_article_content(cast(Any, FakeProcessPage())))


def test_dismiss_page_overlays_presses_escape_twice() -> None:
    """Medium image zoom overlays are dismissed before shortcuts fire."""
    page = FakeProcessPage()
    asyncio.run(dismiss_page_overlays(cast(Any, page)))
    assert page.keyboard.pressed == ["Escape", "Escape"]


def test_focus_article_text_prefers_heading_over_body() -> None:
    """Readable text is focused instead of clicking the whole article container."""
    page = FakeProcessPage()
    asyncio.run(focus_article_text(cast(Any, page)))
    assert page.clicked == ["article h1"]


def test_focus_article_text_falls_back_to_body() -> None:
    """Body receives focus when earlier text selectors are unavailable."""
    page = FakeProcessPage(
        fail_selectors={
            "article h1",
            "article p",
            "article section p",
            "[role='main'] h1",
            "[role='main'] p",
        }
    )
    asyncio.run(focus_article_text(cast(Any, page)))
    assert page.clicked == ["body"]


def test_trigger_readwise_save_uses_system_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """System shortcut mode delegates to macOS keystroke delivery."""
    calls: list[str] = []

    def fake_trigger(shortcut: str, *, browser_app_name: str) -> None:
        calls.append(f"{shortcut}|{browser_app_name}")

    monkeypatch.setattr("src.medium_to_readwise.process.trigger_system_shortcut", fake_trigger)
    page = FakeProcessPage()
    asyncio.run(
        trigger_readwise_save(
            cast(Any, page),
            shortcut="Alt+KeyR",
            shortcut_mode="system",
            browser_app_name="Brave Browser",
        )
    )
    assert page.brought_to_front is True
    assert calls == ["Alt+KeyR|Brave Browser"]


def test_capture_failure_screenshot_writes_debug_image(tmp_path: Path) -> None:
    """Failure screenshots are saved below the requested state directory."""
    page = FakeProcessPage()
    path = asyncio.run(
        capture_failure_screenshot(cast(Any, page), tmp_path, url="https://medium.com/@a/one")
    )
    assert path is not None
    assert Path(path).exists()


def test_process_article_once_triggers_playwright_shortcut_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Playwright shortcut mode still sends Alt+KeyR for non-macOS testing."""

    async def fake_wait(*_args: Any, **_kwargs: Any) -> bool:
        return True

    async def fake_remove(*_args: Any, **_kwargs: Any) -> None:
        return None

    monkeypatch.setattr("src.medium_to_readwise.process.wait_for_readwise_save", fake_wait)
    monkeypatch.setattr(
        "src.medium_to_readwise.process.remove_article_from_reading_list",
        fake_remove,
    )
    page = FakeProcessPage()
    result = asyncio.run(
        process_article_once(
            cast(Any, page),
            url="https://medium.com/@a/one-abc12345",
            delay_seconds=0,
            dry_run=False,
            reading_list_url="https://medium.com/@plischke81/list/reading-list",
            shortcut_mode="playwright",
        )
    )
    assert page.keyboard.pressed.count("Escape") == 2
    assert "Alt+KeyR" in page.keyboard.pressed
    assert result["status"] == "ok"
    assert result["readwise_saved"] is True
    assert result["removed_from_list"] is True
    assert result["final_url"] == "https://medium.com/@a/one-abc12345?redirected=1"


def test_process_article_once_fails_when_readwise_confirmation_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Articles are not marked successful when Readwise confirmation never appears."""

    async def fake_wait(*_args: Any, **_kwargs: Any) -> bool:
        return False

    monkeypatch.setattr("src.medium_to_readwise.process.wait_for_readwise_save", fake_wait)
    page = FakeProcessPage()
    result = asyncio.run(
        process_article_once(
            cast(Any, page),
            url="https://medium.com/@a/one-abc12345",
            delay_seconds=0,
            dry_run=False,
            reading_list_url="https://medium.com/@plischke81/list/reading-list",
            shortcut_mode="playwright",
        )
    )
    assert result["status"] == "failed"
    assert result["readwise_saved"] is False
    assert "confirmation" in str(result["error"]).lower()


def test_process_article_with_retries_records_failure(tmp_path: Path) -> None:
    """Failed processing returns a failed entry with attempts and screenshot."""
    page = FakeProcessPage(fail_goto=True)
    logs: list[str] = []
    result = asyncio.run(
        process_article_with_retries(
            cast(Any, page),
            url="https://medium.com/@a/one-abc12345",
            state_dir=tmp_path,
            reading_list_url="https://medium.com/@plischke81/list/reading-list",
            delay_seconds=0,
            dry_run=False,
            max_retries=1,
            retry_delay_seconds=0,
            shortcut_mode="playwright",
            log=logs.append,
        )
    )
    assert result["status"] == "failed"
    assert result["attempts"] == 2
    assert result["screenshot"] is not None
    assert len(logs) == 4
