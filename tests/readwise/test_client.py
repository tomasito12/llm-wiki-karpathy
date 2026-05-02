"""Tests for Readwise Reader API client (mocked HTTP)."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from src.readwise.client import (
    ReadwiseClientError,
    fetch_list_page,
    iter_archive_processed_documents,
)
from src.readwise.models import ReaderDocument


def _article_row(
    doc_id: str,
    *,
    parent_id: str | None = None,
    title: str = "Sample",
) -> dict[str, Any]:
    """Build a minimal list API row resembling Reader documents."""
    return {
        "id": doc_id,
        "title": title,
        "author": "Author One",
        "source_url": "https://example.com/post",
        "category": "article",
        "location": "archive",
        "published_date": "2024-01-01",
        "saved_at": "2024-01-01T10:00:00+00:00",
        "updated_at": "2024-01-02T10:00:00+00:00",
        "summary": "Short summary.",
        "html_content": "<article><p>Body</p></article>",
        "parent_id": parent_id,
        "tags": {"processed": True},
    }


def test_fetch_list_page_retries_on_429(monkeypatch) -> None:
    """429 responses wait and retry until success."""
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, text="slow")
        payload = {"count": 1, "nextPageCursor": None, "results": [_article_row("id-a")]}
        return httpx.Response(200, json=payload)

    monkeypatch.setattr("src.readwise.client.time.sleep", lambda _s: None)
    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        data = fetch_list_page(client)
    assert calls["n"] == 2
    assert len(data["results"]) == 1


def test_fetch_list_page_raises_on_http_error() -> None:
    """Non-retryable HTTP errors surface as ReadwiseClientError."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="error")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        with pytest.raises(ReadwiseClientError, match="HTTP 500"):
            fetch_list_page(client)


def test_iter_skips_child_documents_with_parent_id() -> None:
    """Rows with parent_id are highlights/notes and must not be yielded."""

    payload = {
        "count": 2,
        "nextPageCursor": None,
        "results": [
            _article_row("child", parent_id="parent"),
            _article_row("top", parent_id=None),
        ],
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        docs = list(iter_archive_processed_documents(client))
    assert [d.id for d in docs] == ["top"]


def test_iter_pagination_follows_next_page_cursor() -> None:
    """All pages are consumed until nextPageCursor is absent."""

    page1 = {
        "count": 2,
        "nextPageCursor": "cursor2",
        "results": [_article_row("one", title="First")],
    }
    page2 = {"count": 1, "nextPageCursor": None, "results": [_article_row("two", title="Second")]}

    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if params.get("pageCursor") == "cursor2":
            return httpx.Response(200, json=page2)
        return httpx.Response(200, json=page1)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        docs = list(iter_archive_processed_documents(client))
    assert [d.id for d in docs] == ["one", "two"]


def test_reader_document_from_api_row_parses_tags_dict() -> None:
    """Tags object is normalized to a dict even when API sends odd types."""
    row = _article_row("x")
    row["tags"] = ["should", "become", "dict"]
    doc = ReaderDocument.from_api_row(row)
    assert doc.tags == {}
