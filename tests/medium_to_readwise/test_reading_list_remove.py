"""Tests for Medium Reading List removal helpers."""

from __future__ import annotations

from src.medium_to_readwise.reading_list_remove import (
    REMOVE_ACTION_PATTERN,
    article_href_fragment,
)


def test_article_href_fragment_uses_article_slug() -> None:
    """List entry lookup uses the article slug with Medium id suffix."""
    url = "https://medium.com/@user/story-abc12345?utm_source=list"
    assert article_href_fragment(url) == "story-abc12345"


def test_remove_action_pattern_matches_remove_item_label() -> None:
    """Medium's current Reading List action label is supported."""
    assert REMOVE_ACTION_PATTERN.search("Remove item") is not None
