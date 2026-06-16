"""Tests for Medium login-session detection."""

from __future__ import annotations

import asyncio
from typing import Any, cast

import pytest

from src.medium_to_readwise.medium_session import (
    MediumLoginRequired,
    article_body_is_thin,
    ensure_medium_logged_in,
    page_text_indicates_medium_logged_out,
    page_url_indicates_medium_login,
)


class FakeSessionLocator:
    """Minimal locator for session detection tests."""

    def __init__(
        self,
        page: FakeSessionPage,
        selector: str,
        *,
        match_count: int = 0,
        visible: bool = False,
        inner_text_value: str = "",
    ) -> None:
        """Initialize locator state."""
        self.page = page
        self.selector = selector
        self.match_count = match_count
        self.visible = visible
        self.inner_text_value = inner_text_value

    @property
    def first(self) -> FakeSessionLocator:
        """Return the first matching locator."""
        return self

    async def count(self) -> int:
        """Return how many elements match."""
        return self.match_count

    async def is_visible(self) -> bool:
        """Return whether the element is visible."""
        return self.visible and self.match_count > 0

    async def inner_text(self) -> str:
        """Return configured inner text."""
        return self.inner_text_value


class FakeSessionPage:
    """Minimal page object for Medium session tests."""

    def __init__(
        self,
        *,
        url: str = "https://medium.com/@author/sample-abc12345",
        body_text: str = "Full article body with enough content.",
        article_text: str = "x" * 500,
        logged_out_phrases: set[str] | None = None,
        show_sign_in_controls: bool = False,
    ) -> None:
        """Initialize fake page behavior."""
        self.url = url
        self.body_text = body_text
        self.article_text = article_text
        self.logged_out_phrases = logged_out_phrases or set()
        self.show_sign_in_controls = show_sign_in_controls

    def locator(self, selector: str) -> FakeSessionLocator:
        """Return a fake locator for ``selector``."""
        if selector == "body":
            return FakeSessionLocator(
                self, selector, match_count=1, inner_text_value=self.body_text
            )
        if selector == "article":
            return FakeSessionLocator(
                self,
                selector,
                match_count=1,
                inner_text_value=self.article_text,
            )
        if self.show_sign_in_controls and (
            "accounts.medium.com" in selector or "/m/signin" in selector
        ):
            return FakeSessionLocator(self, selector, match_count=1, visible=True)
        return FakeSessionLocator(self, selector)

    def get_by_text(self, phrase: str, *, exact: bool = False) -> FakeSessionLocator:
        """Return a fake text locator."""
        del exact
        if phrase in self.logged_out_phrases:
            return FakeSessionLocator(self, f"text={phrase}", match_count=1, visible=True)
        return FakeSessionLocator(self, f"text={phrase}")

    def get_by_role(self, role: str, *, name: str) -> FakeSessionLocator:
        """Return a fake role locator."""
        if self.show_sign_in_controls and role == "link" and name in {"Sign in", "Sign up"}:
            return FakeSessionLocator(self, f"role={role}:{name}", match_count=1, visible=True)
        return FakeSessionLocator(self, f"role={role}:{name}")


def test_page_url_indicates_medium_login_matches_signin_paths() -> None:
    """Medium account and sign-in URLs are treated as logged-out gates."""
    assert page_url_indicates_medium_login("https://accounts.medium.com/sign-in") is True
    assert page_url_indicates_medium_login("https://medium.com/m/signin") is True
    assert page_url_indicates_medium_login("https://medium.com/@author/post-abc12345") is False


def test_page_text_indicates_medium_logged_out_matches_paywall_copy() -> None:
    """Common Medium paywall copy is detected."""
    text = "Sign in to read this member-only story."
    assert page_text_indicates_medium_logged_out(text) is True


def test_article_body_is_thin_detects_short_article() -> None:
    """Thin article bodies indicate a paywall or preview state."""
    page = FakeSessionPage(article_text="short")
    assert asyncio.run(article_body_is_thin(cast(Any, page))) is True


def test_ensure_medium_logged_in_raises_on_sign_in_url() -> None:
    """Login enforcement stops before Readwise automation on sign-in pages."""
    page = FakeSessionPage(url="https://accounts.medium.com/sign-in")
    with pytest.raises(MediumLoginRequired):
        asyncio.run(ensure_medium_logged_in(cast(Any, page)))


def test_ensure_medium_logged_in_allows_full_article_even_with_login_phrase_in_body() -> None:
    """Long article bodies avoid false positives from quoted login phrases."""
    page = FakeSessionPage(
        body_text="Sign in with Google is discussed at length in this tutorial.",
        article_text="x" * 500,
        logged_out_phrases=set(),
    )
    asyncio.run(ensure_medium_logged_in(cast(Any, page)))


def test_ensure_medium_logged_in_raises_on_visible_sign_in_control() -> None:
    """Visible Medium sign-in controls stop the run immediately."""
    page = FakeSessionPage(show_sign_in_controls=True, article_text="short")
    with pytest.raises(MediumLoginRequired):
        asyncio.run(ensure_medium_logged_in(cast(Any, page)))
