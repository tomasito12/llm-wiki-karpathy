"""Tests for Medium URL cleanup and filtering."""

from __future__ import annotations

from src.medium_to_readwise.urls import (
    article_slug_from_path,
    dedupe_urls,
    filter_article_urls,
    has_article_slug,
    is_medium_article_url,
    normalize_article_url,
)


def test_normalize_article_url_strips_tracking_and_fragment() -> None:
    """Tracking query params and fragments do not affect article identity."""
    url = "HTTPS://Medium.com/@user/story-abc12345?utm_source=x&sk=abc&ok=1#footer"
    assert normalize_article_url(url) == "https://medium.com/@user/story-abc12345?ok=1"


def test_normalize_article_url_resolves_relative_links() -> None:
    """Relative links from the Reading List resolve against the current page."""
    assert (
        normalize_article_url(
            "/@user/story-abc12345?source=list",
            base_url="https://medium.com/@plischke81/list/reading-list",
        )
        == "https://medium.com/@user/story-abc12345"
    )


def test_has_article_slug_requires_medium_hash_suffix() -> None:
    """Article slugs must end with Medium's hex article id suffix."""
    assert has_article_slug("gatori-fishing-in-america-c63152d79ba1")
    assert not has_article_slug("story")
    assert not has_article_slug("@plischke81")


def test_is_medium_article_url_accepts_real_reading_list_articles() -> None:
    """Reading List article URLs with hash suffixes are accepted."""
    assert is_medium_article_url(
        "https://medium.com/@youandyourband/gatori-fishing-in-america-c63152d79ba1"
    )
    assert is_medium_article_url(
        "https://johndevore.medium.com/cigarettes-are-bad-i-miss-them-3e00ad67018b"
    )
    assert is_medium_article_url(
        "https://medium.com/design-bootcamp/i-sat-in-engineering-meetings-for-two-years-without-understanding-what-a-branch-was-c106ce7cadf8"
    )


def test_is_medium_article_url_rejects_profiles_publications_and_external_links() -> None:
    """Profiles, publications, sitemap, and external links are excluded."""
    assert not is_medium_article_url("https://medium.com/sitemap/sitemap.xml")
    assert not is_medium_article_url(
        "https://play.google.com/store/apps/details?id=com.medium.reader"
    )
    assert not is_medium_article_url("https://medium.com/@plischke81")
    assert not is_medium_article_url("https://medium.com/@youandyourband")
    assert not is_medium_article_url("https://medium.com/design-bootcamp")
    assert not is_medium_article_url("https://medium.com/@plischke81/list/reading-list")
    assert not is_medium_article_url("https://medium.com/search?q=agents")


def test_article_slug_from_path_returns_last_segment() -> None:
    """The article slug is taken from the final URL path segment."""
    assert article_slug_from_path("/@user/story-abc12345") == "story-abc12345"


def test_filter_article_urls_drops_stale_navigation_links() -> None:
    """Cached or merged URL lists lose profiles, sitemaps, and external links."""
    urls = [
        "https://medium.com/sitemap/sitemap.xml",
        "https://medium.com/@plischke81",
        "https://medium.com/@youandyourband/gatori-fishing-in-america-c63152d79ba1",
        "https://play.google.com/store/apps/details?id=com.medium.reader",
    ]
    assert filter_article_urls(urls) == [
        "https://medium.com/@youandyourband/gatori-fishing-in-america-c63152d79ba1"
    ]


def test_dedupe_urls_preserves_first_seen_order() -> None:
    """Duplicate article URLs are removed without sorting."""
    urls = [
        "https://medium.com/@a/one-abc12345?utm_source=x",
        "https://medium.com/@b/two-def67890",
        "https://medium.com/@a/one-abc12345",
    ]
    assert dedupe_urls(urls) == [
        "https://medium.com/@a/one-abc12345",
        "https://medium.com/@b/two-def67890",
    ]
