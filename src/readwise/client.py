"""HTTP client for Readwise Reader API v3 document list."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import httpx

from src.readwise.models import ReaderDocument

LIST_URL = "https://readwise.io/api/v3/list/"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES_429 = 8


class ReadwiseClientError(RuntimeError):
    """Raised when the Reader API returns an unexpected or repeated error."""


def _auth_headers(token: str) -> dict[str, str]:
    """Return Authorization headers for Reader API."""
    trimmed = token.strip()
    if not trimmed:
        raise ReadwiseClientError("READWISE_TOKEN is empty.")
    return {"Authorization": f"Token {trimmed}"}


def fetch_list_page(
    client: httpx.Client,
    *,
    location: str = "archive",
    tag: str = "processed",
    with_html_content: bool = True,
    limit: int = 100,
    page_cursor: str | None = None,
    updated_after: str | None = None,
) -> dict[str, Any]:
    """Fetch one page of document list results."""
    params: dict[str, str | int] = {
        "location": location,
        "tag": tag,
        "withHtmlContent": str(with_html_content).lower(),
        "limit": limit,
    }
    if page_cursor:
        params["pageCursor"] = page_cursor
    if updated_after:
        params["updatedAfter"] = updated_after

    attempt = 0
    while True:
        response = client.get(LIST_URL, params=params)
        if response.status_code == 429:
            wait = _retry_after_seconds(response)
            attempt += 1
            if attempt > MAX_RETRIES_429:
                raise ReadwiseClientError("Too many 429 responses from Readwise API.")
            time.sleep(wait)
            continue
        if response.status_code != 200:
            raise ReadwiseClientError(
                f"Readwise list failed: HTTP {response.status_code} {response.text[:500]}"
            )
        return response.json()


def _retry_after_seconds(response: httpx.Response) -> float:
    """Parse Retry-After header; default to a short backoff."""
    header = response.headers.get("Retry-After")
    if header is None:
        return 2.0
    try:
        return float(header)
    except ValueError:
        return 2.0


def iter_archive_processed_documents(
    client: httpx.Client,
    *,
    updated_after: str | None = None,
) -> Iterator[ReaderDocument]:
    """Yield top-level documents in archive with tag ``processed`` (paginated).

    Skips child rows (highlights/notes) where ``parent_id`` is set.
    """
    cursor: str | None = None
    while True:
        payload = fetch_list_page(
            client,
            page_cursor=cursor,
            updated_after=updated_after,
        )
        results = payload.get("results")
        if not isinstance(results, list):
            raise ReadwiseClientError("Invalid list response: missing results array.")
        for row in results:
            if not isinstance(row, dict):
                continue
            doc = ReaderDocument.from_api_row(row)
            if doc.parent_id is not None:
                continue
            yield doc
        next_cursor = payload.get("nextPageCursor")
        if not next_cursor:
            break
        cursor = str(next_cursor)


def reader_client(token: str, *, timeout: float = DEFAULT_TIMEOUT) -> httpx.Client:
    """Construct an ``httpx.Client`` with Reader API auth headers."""
    return httpx.Client(headers=_auth_headers(token), timeout=timeout)
