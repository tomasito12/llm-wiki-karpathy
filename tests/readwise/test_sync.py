"""Tests for Readwise sync orchestration."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from src.readwise.export import sha256_hex
from src.readwise.library_index import ExportedRecord, LibraryIndex
from src.readwise.sync import (
    INITIAL_LOOKBACK_DAYS,
    _needs_export,
    resolved_updated_after_for_list,
    run_sync,
)


def _row(doc_id: str, updated_at: str, *, html: str = "<p>x</p>") -> dict[str, Any]:
    return {
        "id": doc_id,
        "title": "Title",
        "author": None,
        "source_url": "https://example.com/x",
        "category": "article",
        "location": "archive",
        "published_date": None,
        "saved_at": None,
        "updated_at": updated_at,
        "summary": "",
        "html_content": html,
        "parent_id": None,
        "tags": {},
    }


def test_needs_export_true_when_id_missing() -> None:
    idx = LibraryIndex.empty()
    assert _needs_export(
        doc_id="new",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html="<p></p>",
        index=idx,
        repo_root=Path("/tmp"),
        prune_missing=False,
    )


def test_needs_export_false_when_updated_at_matches(tmp_path: Path) -> None:
    idx = LibraryIndex.empty()
    html = "<p>same</p>"
    idx.documents["a"] = ExportedRecord(
        html_path="raw/readwise/x.html",
        md_path="raw/readwise/x.md",
        source_url=None,
        updated_at="2024-01-01T00:00:00+00:00",
        content_sha256=sha256_hex(html),
    )
    assert not _needs_export(
        doc_id="a",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html=html,
        index=idx,
        repo_root=tmp_path,
        prune_missing=False,
    )


def test_needs_export_true_when_html_hash_differs_at_same_updated_at() -> None:
    """Content hash mismatch forces re-export even if ``updated_at`` is unchanged."""
    idx = LibraryIndex.empty()
    old_html = "<p>old</p>"
    idx.documents["a"] = ExportedRecord(
        html_path="raw/readwise/x.html",
        md_path="raw/readwise/x.md",
        source_url=None,
        updated_at="2024-01-01T00:00:00+00:00",
        content_sha256=sha256_hex(old_html),
    )
    assert _needs_export(
        doc_id="a",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html="<p>new</p>",
        index=idx,
        repo_root=Path("/tmp"),
        prune_missing=False,
    )


def test_needs_export_true_when_prune_missing_and_files_gone(tmp_path: Path) -> None:
    idx = LibraryIndex.empty()
    idx.documents["a"] = ExportedRecord(
        html_path="raw/readwise/missing.html",
        md_path="raw/readwise/missing.md",
        source_url=None,
        updated_at="2024-01-01T00:00:00+00:00",
        content_sha256=None,
    )
    assert _needs_export(
        doc_id="a",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html="<p>x</p>",
        index=idx,
        repo_root=tmp_path,
        prune_missing=True,
    )


def test_run_sync_writes_files_and_index(tmp_path: Path) -> None:
    payload = {
        "count": 1,
        "nextPageCursor": None,
        "results": [_row("doc1", "2024-01-03T00:00:00+00:00", html="<p>Hi</p>")],
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    index_path = tmp_path / "readwise_library.json"
    out_dir = tmp_path / "raw" / "readwise"
    with httpx.Client(transport=transport) as client:
        result = run_sync(
            "token",
            index_path=index_path,
            output_dir=out_dir,
            repo_root=tmp_path,
            client=client,
        )
    assert result.examined == 1
    assert result.exported == 1
    assert result.skipped == 0
    assert result.incremental_filter_active is True
    assert result.incremental_watermark is not None
    assert any(out_dir.glob("*.html"))
    assert any(out_dir.glob("*.md"))
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert "doc1" in data["documents"]


def test_run_sync_skips_unchanged(tmp_path: Path) -> None:
    index_path = tmp_path / "readwise_library.json"
    out_dir = tmp_path / "raw" / "readwise"
    out_dir.mkdir(parents=True)
    (out_dir / "title-doc1.html").write_text("<p>Hi</p>", encoding="utf-8")
    (out_dir / "title-doc1.md").write_text("---\n---\n", encoding="utf-8")
    LibraryIndex(
        documents={
            "doc1": ExportedRecord(
                html_path="raw/readwise/title-doc1.html",
                md_path="raw/readwise/title-doc1.md",
                source_url=None,
                updated_at="2024-01-03T00:00:00+00:00",
                content_sha256=None,
            )
        },
        last_updated_after=None,
    ).save(index_path)

    payload = {
        "count": 1,
        "nextPageCursor": None,
        "results": [_row("doc1", "2024-01-03T00:00:00+00:00", html="<p>Hi</p>")],
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        result = run_sync(
            "token",
            index_path=index_path,
            output_dir=out_dir,
            repo_root=tmp_path,
            client=client,
        )
    assert result.exported == 0
    assert result.skipped == 1


def test_run_sync_dry_run_does_not_write_index(tmp_path: Path) -> None:
    payload = {
        "count": 1,
        "nextPageCursor": None,
        "results": [_row("doc1", "2024-01-03T00:00:00+00:00")],
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    index_path = tmp_path / "readwise_library.json"
    out_dir = tmp_path / "raw" / "readwise"
    with httpx.Client(transport=transport) as client:
        result = run_sync(
            "token",
            index_path=index_path,
            output_dir=out_dir,
            repo_root=tmp_path,
            dry_run=True,
            client=client,
        )
    assert result.exported == 1
    assert not index_path.exists()
    assert not out_dir.exists()


def test_run_sync_incremental_metadata_when_watermark_set(tmp_path: Path) -> None:
    """Stored ``last_updated_after`` is passed as ``updatedAfter`` to the API."""
    index_path = tmp_path / "readwise_library.json"
    LibraryIndex(documents={}, last_updated_after="2024-06-01T12:00:00+00:00").save(index_path)

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"count": 0, "results": [], "nextPageCursor": None})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        result = run_sync(
            "token",
            index_path=index_path,
            repo_root=tmp_path,
            client=client,
        )
    assert result.examined == 0
    assert result.incremental_filter_active is True
    assert result.incremental_watermark == "2024-06-01T12:00:00+00:00"


def test_resolved_updated_after_uses_lookback_without_watermark() -> None:
    """Fresh index uses ``now`` minus ``INITIAL_LOOKBACK_DAYS``."""
    idx = LibraryIndex.empty()
    fixed = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)
    got = resolved_updated_after_for_list(idx, now=fixed)
    assert got == (fixed - timedelta(days=INITIAL_LOOKBACK_DAYS)).isoformat()


def test_resolved_updated_after_prefers_stored_watermark() -> None:
    """When set, ``last_updated_after`` overrides the default lookback."""
    idx = LibraryIndex(documents={}, last_updated_after="2024-01-02T00:00:00+00:00")
    fixed = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)
    got = resolved_updated_after_for_list(idx, now=fixed)
    assert got == "2024-01-02T00:00:00+00:00"


def test_reset_watermark_persists_null_when_api_returns_nothing(tmp_path: Path) -> None:
    """Clearing the watermark is saved even when the list response is empty."""

    index_path = tmp_path / "readwise_library.json"
    LibraryIndex(documents={}, last_updated_after="2020-01-01T00:00:00+00:00").save(
        index_path
    )

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"count": 0, "results": [], "nextPageCursor": None})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        run_sync(
            "token",
            index_path=index_path,
            repo_root=tmp_path,
            reset_watermark=True,
            client=client,
        )
    loaded = LibraryIndex.load(index_path)
    assert loaded.last_updated_after is None
