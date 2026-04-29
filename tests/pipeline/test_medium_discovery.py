from __future__ import annotations

from datetime import date

from src.pipeline.discovery import medium
from src.pipeline.models import SourceConfig


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_discover_medium_items_includes_archive_page_links(monkeypatch) -> None:
    archive_html = b"""
<html><body>
  <a href="https://medium.com/autocomplete-real-world-ai/wcag-compliance-for-ai-chatbots-074c2370d8a8">Post</a>
</body></html>
"""
    article_html = b"""
<html><head>
  <meta property="article:published_time" content="2026-04-26T10:00:00Z" />
</head></html>
"""
    call_index = {"value": 0}

    def fake_urlopen(_request, timeout: int) -> _FakeResponse:
        call_index["value"] += 1
        assert timeout in {10, 20}
        if call_index["value"] == 1:
            return _FakeResponse(archive_html)
        return _FakeResponse(article_html)

    monkeypatch.setattr(medium, "urlopen", fake_urlopen)
    source = SourceConfig(
        name="tag-source",
        kind="medium",
        url="https://medium.com/tag/chatbots",
    )
    items = medium.discover_medium_items(source)
    assert len(items) == 1
    assert "wcag-compliance-for-ai-chatbots" in items[0].url
    assert items[0].published_at == "2026-04-26T10:00:00Z"


def test_crawl_archive_pages_follows_nested_archive_pages(monkeypatch) -> None:
    first_archive = b"""
<html><body>
  <a href="/tag/chatbots/archive/2026/04">April 2026</a>
  <a href="https://medium.com/some-pub/article-one-aaaabbbb">A1</a>
</body></html>
"""
    second_archive = b"""
<html><body>
  <a href="/tag/chatbots/archive/2026/03">March 2026</a>
  <a href="https://medium.com/some-pub/article-two-bbbbcccc">A2</a>
</body></html>
"""
    third_archive = b"""
<html><body>
  <a href="https://medium.com/some-pub/article-three-ccccdddd">A3</a>
</body></html>
"""
    pages = [first_archive, second_archive, third_archive]
    idx = {"value": 0}

    def fake_urlopen(_request, timeout: int) -> _FakeResponse:
        assert timeout == 20
        current = pages[min(idx["value"], len(pages) - 1)]
        idx["value"] += 1
        return _FakeResponse(current)

    monkeypatch.setattr(medium, "urlopen", fake_urlopen)
    links = medium._crawl_archive_pages(
        archive_root="https://medium.com/tag/chatbots/archive",
        max_links=10,
        max_archive_pages=5,
    )
    assert "https://medium.com/some-pub/article-one-aaaabbbb" in links
    assert "https://medium.com/some-pub/article-two-bbbbcccc" in links
    assert "https://medium.com/some-pub/article-three-ccccdddd" in links


def test_is_article_link_filters_non_story_urls() -> None:
    assert medium._is_article_link("https://medium.com/some-pub/title-1234abcd")
    assert not medium._is_article_link("https://medium.com")
    assert not medium._is_article_link("https://medium.com/@author")
    assert not medium._is_article_link("https://medium.com/tag/chatbots")
    assert not medium._is_article_link("https://medium.com/search")
    assert not medium._is_article_link("https://help.medium.com/hc/en-us")


def test_published_at_to_utc_date_parses_iso_z() -> None:
    assert medium.published_at_to_utc_date("2026-04-27T18:06:50.278Z") == date(2026, 4, 27)


def test_archive_scroll_stops_when_content_older_than_window_start() -> None:
    assert medium.archive_scroll_should_stop(
        min_published_date=date(2026, 4, 23),
        window_start_date=date(2026, 4, 24),
        stall_scrolls=0,
        scroll_index=0,
        max_scrolls=150,
    )


def test_archive_scroll_continues_when_min_date_equals_window_start() -> None:
    assert not medium.archive_scroll_should_stop(
        min_published_date=date(2026, 4, 24),
        window_start_date=date(2026, 4, 24),
        stall_scrolls=0,
        scroll_index=0,
        max_scrolls=150,
    )


def test_archive_scroll_stops_at_max_scrolls() -> None:
    assert medium.archive_scroll_should_stop(
        min_published_date=None,
        window_start_date=date(2026, 4, 24),
        stall_scrolls=0,
        scroll_index=150,
        max_scrolls=150,
    )
