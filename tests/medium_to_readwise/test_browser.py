"""Tests for Brave CDP browser helpers."""

from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest

from src.medium_to_readwise.browser import (
    ConnectedBrowser,
    cdp_connection_error,
    cdp_reachable,
    connect_over_cdp,
    select_context,
    select_page,
)


class FakeContext:
    """Minimal browser context for CDP helper tests."""

    def __init__(self, pages: list[object] | None = None) -> None:
        """Initialize with optional pages."""
        self.pages = pages or []
        self.created_pages = 0

    async def new_page(self) -> object:
        """Create a fake page."""
        self.created_pages += 1
        page = object()
        self.pages.append(page)
        return page


class FakeBrowser:
    """Minimal browser object for CDP helper tests."""

    def __init__(self, contexts: list[FakeContext] | None = None) -> None:
        """Initialize with optional contexts."""
        self.contexts = contexts or []


class FakeChromium:
    """Minimal Chromium launcher for CDP helper tests."""

    def __init__(self, browser: FakeBrowser) -> None:
        """Initialize with a browser to return."""
        self.browser = browser
        self.cdp_url = ""

    async def connect_over_cdp(self, cdp_url: str) -> FakeBrowser:
        """Record the CDP URL and return the fake browser."""
        self.cdp_url = cdp_url
        return self.browser


class FakePlaywright:
    """Minimal Playwright object for CDP helper tests."""

    def __init__(self, browser: FakeBrowser) -> None:
        """Initialize fake Chromium API."""
        self.chromium = FakeChromium(browser)


def test_connected_browser_holds_session_objects() -> None:
    """The session dataclass stores browser, context, and page handles."""
    browser = FakeBrowser()
    context = FakeContext()
    page = object()
    session = ConnectedBrowser(cast(Any, browser), cast(Any, context), cast(Any, page))
    assert session.browser is browser
    assert session.context is context
    assert session.page is page


def test_select_context_prefers_context_with_pages() -> None:
    """A context that already has a tab is preferred."""
    empty = FakeContext()
    with_page = FakeContext([object()])
    assert select_context(cast(Any, FakeBrowser([empty, with_page]))) is with_page


def test_select_context_raises_when_cdp_has_no_contexts() -> None:
    """A CDP connection without browser contexts is treated as unusable."""
    with pytest.raises(RuntimeError, match="no contexts"):
        select_context(cast(Any, FakeBrowser()))


def test_select_page_reuses_existing_page() -> None:
    """Existing tabs are reused for automation."""
    page = object()
    context = FakeContext([page])
    assert asyncio.run(select_page(cast(Any, context))) is page


def test_select_page_creates_page_when_empty() -> None:
    """An empty context gets a new tab."""
    context = FakeContext()
    assert asyncio.run(select_page(cast(Any, context))) in context.pages


def test_cdp_connection_error_includes_macos_startup_instructions() -> None:
    """CDP failures explain how to restart Brave with debugging enabled."""
    message = str(cdp_connection_error("http://127.0.0.1:9222"))
    assert "Quit Brave completely" in message
    assert "--remote-debugging-port=9222" in message


def test_cdp_reachable_returns_false_for_invalid_host() -> None:
    """Unreachable CDP endpoints are reported as unavailable."""
    assert cdp_reachable("http://127.0.0.1:1", timeout_seconds=0.2) is False


def test_connect_over_cdp_returns_connected_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    """Connecting over CDP selects a context and page."""
    monkeypatch.setattr(
        "src.medium_to_readwise.browser.cdp_reachable", lambda *_args, **_kwargs: True
    )
    browser = FakeBrowser([FakeContext([object()])])
    playwright = FakePlaywright(browser)
    session = asyncio.run(connect_over_cdp(cast(Any, playwright), cdp_url="http://localhost:9222"))
    assert session.browser is browser
    assert playwright.chromium.cdp_url == "http://localhost:9222"


def test_connect_over_cdp_raises_when_cdp_is_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Connecting over CDP fails fast when the endpoint is unavailable."""
    monkeypatch.setattr(
        "src.medium_to_readwise.browser.cdp_reachable", lambda *_args, **_kwargs: False
    )
    with pytest.raises(RuntimeError, match="Quit Brave completely"):
        asyncio.run(
            connect_over_cdp(
                cast(Any, FakePlaywright(FakeBrowser())), cdp_url="http://127.0.0.1:9222"
            )
        )
