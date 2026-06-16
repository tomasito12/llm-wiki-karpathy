"""Tests for Medium Reading List removal helpers."""

from __future__ import annotations

import asyncio
import re
from typing import Any, cast

import pytest

from src.medium_to_readwise.reading_list_remove import (
    REMOVE_ACTION_PATTERN,
    article_href_fragment,
    click_remove_action,
    list_entry_is_present,
    open_entry_menu,
    remove_article_from_reading_list,
)


class FakeRemoveLocator:
    """Minimal locator for removal tests."""

    def __init__(
        self,
        page: FakeRemovePage,
        selector: str = "",
        *,
        match_count: int = 0,
        visible: bool = False,
        text: str = "",
        is_row: bool = False,
    ) -> None:
        """Initialize locator state."""
        self.page = page
        self.selector = selector
        self.match_count = match_count
        self.visible = visible
        self.text = text
        self.is_row = is_row

    @property
    def first(self) -> FakeRemoveLocator:
        """Return the first matching locator."""
        return self

    def locator(self, selector: str) -> FakeRemoveLocator:
        """Return a child locator or ancestor row for list-entry lookup."""
        if selector.startswith("xpath=ancestor::"):
            return FakeRemoveLocator(self.page, selector, match_count=1, visible=True, is_row=True)
        return self.page.locator(selector)

    def get_by_role(self, role: str, *, name: str | re.Pattern[str]) -> FakeRemoveLocator:
        """Return a role locator scoped to this row when applicable."""
        return self.page.get_by_role(role, name=name)

    def filter(self, *, has_text: str | re.Pattern[str]) -> FakeRemoveLocator:
        """Return a filtered locator."""
        if isinstance(has_text, re.Pattern):
            if has_text.search(self.text):
                return FakeRemoveLocator(self.page, self.selector, match_count=1, visible=True)
        elif has_text in self.text:
            return FakeRemoveLocator(self.page, self.selector, match_count=1, visible=True)
        return FakeRemoveLocator(self.page, self.selector)

    async def count(self) -> int:
        """Return how many elements match."""
        return self.match_count

    async def is_visible(self) -> bool:
        """Return whether the element is visible."""
        return self.visible and self.match_count > 0

    async def click(self, *, timeout: int) -> None:
        """Record a click."""
        assert timeout > 0
        self.page.clicked.append(self.selector or self.text)

    async def wait_for(self, *, state: str, timeout: int) -> None:
        """Pretend the element reached ``state``."""
        del state
        assert timeout > 0

    async def scroll_into_view_if_needed(self, *, timeout: int) -> None:
        """Pretend the element was scrolled into view."""
        assert timeout > 0


class FakeRemovePage:
    """Minimal page object for removal tests."""

    def __init__(
        self,
        *,
        article_url: str,
        present: bool = True,
        menu_visible: bool = True,
        remove_visible: bool = True,
    ) -> None:
        """Initialize fake page behavior."""
        self.article_url = article_url
        self.present = present
        self.menu_visible = menu_visible
        self.remove_visible = remove_visible
        self.clicked: list[str] = []
        self.urls: list[str] = []

    def locator(self, selector: str) -> FakeRemoveLocator:
        """Return a fake locator for ``selector``."""
        fragment = article_href_fragment(self.article_url)
        if f'href*="{fragment}"' in selector:
            return FakeRemoveLocator(
                self,
                selector,
                match_count=1 if self.present else 0,
                visible=self.present,
            )
        if "aria-haspopup" in selector and self.menu_visible:
            return FakeRemoveLocator(self, selector, match_count=1, visible=True)
        if 'role="menuitem"' in selector:
            return FakeRemoveLocator(
                self,
                selector,
                match_count=1 if self.remove_visible else 0,
                visible=self.remove_visible,
                text="Remove item",
            )
        return FakeRemoveLocator(self, selector)

    def get_by_role(self, role: str, *, name: str | re.Pattern[str]) -> FakeRemoveLocator:
        """Return a fake role locator."""
        if role in {"menuitem", "button"} and (
            name == "Remove item" or (isinstance(name, re.Pattern) and name.search("Remove item"))
        ):
            return FakeRemoveLocator(
                self,
                f"role={role}",
                match_count=1 if self.remove_visible else 0,
                visible=self.remove_visible,
                text="Remove item",
            )
        if role == "button" and isinstance(name, re.Pattern) and name.search("more"):
            return FakeRemoveLocator(
                self,
                "menu-button",
                match_count=1 if self.menu_visible else 0,
                visible=self.menu_visible,
            )
        return FakeRemoveLocator(self, f"role={role}")

    def get_by_text(self, text: str, *, exact: bool = False) -> FakeRemoveLocator:
        """Return a fake text locator."""
        del exact
        if text == "Remove item" and self.remove_visible:
            return FakeRemoveLocator(self, text, match_count=1, visible=True, text=text)
        return FakeRemoveLocator(self, text)

    async def goto(self, url: str, *, wait_until: str) -> None:
        """Record navigation."""
        self.urls.append(url)
        assert wait_until == "load"

    async def wait_for_selector(self, selector: str, *, timeout: int) -> None:
        """Pretend the selector appeared."""
        assert selector == "body"
        assert timeout > 0


def test_article_href_fragment_uses_article_slug() -> None:
    """List entry lookup uses the article slug with Medium id suffix."""
    url = "https://medium.com/@user/story-abc12345?utm_source=list"
    assert article_href_fragment(url) == "story-abc12345"


def test_remove_action_pattern_matches_remove_item_label() -> None:
    """Medium's current Reading List action label is supported."""
    assert REMOVE_ACTION_PATTERN.search("Remove item") is not None


def test_click_remove_action_clicks_visible_remove_item() -> None:
    """The remove helper clicks the visible Remove item action."""
    page = FakeRemovePage(
        article_url="https://medium.com/@user/story-abc12345",
        remove_visible=True,
    )
    asyncio.run(click_remove_action(cast(Any, page)))
    assert page.clicked


def test_remove_article_from_reading_list_verifies_entry_is_gone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Removal succeeds only when the article disappears from the list."""
    page = FakeRemovePage(
        article_url="https://medium.com/@user/story-abc12345",
        present=True,
        menu_visible=True,
        remove_visible=True,
    )

    async def fake_sleep(_seconds: float) -> None:
        page.present = False

    monkeypatch.setattr(
        "src.medium_to_readwise.reading_list_remove.asyncio.sleep",
        fake_sleep,
    )
    asyncio.run(
        remove_article_from_reading_list(
            cast(Any, page),
            reading_list_url="https://medium.com/@plischke81/list/reading-list",
            article_url="https://medium.com/@user/story-abc12345",
        )
    )
    assert page.present is False


def test_list_entry_is_present_checks_href_fragment() -> None:
    """Presence checks use the article slug fragment."""
    page = FakeRemovePage(
        article_url="https://medium.com/@user/story-abc12345",
        present=True,
    )
    assert asyncio.run(
        list_entry_is_present(
            cast(Any, page),
            article_url="https://medium.com/@user/story-abc12345",
        )
    )


def test_open_entry_menu_raises_when_menu_button_missing() -> None:
    """Missing menu buttons surface a clear error."""
    page = FakeRemovePage(
        article_url="https://medium.com/@user/story-abc12345",
        menu_visible=False,
    )
    row = page.locator('a[href*="story-abc12345"]')
    with pytest.raises(RuntimeError, match="menu button"):
        asyncio.run(open_entry_menu(cast(Any, page), cast(Any, row)))
