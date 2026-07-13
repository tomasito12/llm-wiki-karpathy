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
    ReadwiseIndexSafetyError,
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
        out_dir=Path("/tmp/out"),
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
        out_dir=tmp_path,
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
        out_dir=Path("/tmp/out"),
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
    out_dir = tmp_path / "external" / "raw" / "readwise"
    out_dir.mkdir(parents=True)
    assert _needs_export(
        doc_id="a",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html="<p>x</p>",
        index=idx,
        out_dir=out_dir,
        prune_missing=True,
    )


def test_needs_export_false_when_prune_missing_and_files_present_in_out_dir(
    tmp_path: Path,
) -> None:
    """Prune-missing should check the configured output dir, not the code repo."""
    html = "<p>same</p>"
    idx = LibraryIndex.empty()
    idx.documents["a"] = ExportedRecord(
        html_path="raw/readwise/file.html",
        md_path="raw/readwise/file.md",
        source_url=None,
        updated_at="2024-01-01T00:00:00+00:00",
        content_sha256=sha256_hex(html),
    )
    out_dir = tmp_path / "external" / "raw" / "readwise"
    out_dir.mkdir(parents=True)
    (out_dir / "file.html").write_text(html, encoding="utf-8")
    (out_dir / "file.md").write_text("---\n---\n", encoding="utf-8")

    assert not _needs_export(
        doc_id="a",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html=html,
        index=idx,
        out_dir=out_dir,
        prune_missing=True,
    )


def test_needs_export_true_when_prune_missing_files_only_in_repo_not_out_dir(
    tmp_path: Path,
) -> None:
    """Files present only under repo_root must not satisfy prune-missing checks."""
    html = "<p>same</p>"
    idx = LibraryIndex.empty()
    idx.documents["a"] = ExportedRecord(
        html_path="raw/readwise/file.html",
        md_path="raw/readwise/file.md",
        source_url=None,
        updated_at="2024-01-01T00:00:00+00:00",
        content_sha256=sha256_hex(html),
    )
    repo_raw = tmp_path / "repo" / "raw" / "readwise"
    repo_raw.mkdir(parents=True)
    (repo_raw / "file.html").write_text(html, encoding="utf-8")
    (repo_raw / "file.md").write_text("---\n---\n", encoding="utf-8")
    out_dir = tmp_path / "external" / "raw" / "readwise"
    out_dir.mkdir(parents=True)

    assert _needs_export(
        doc_id="a",
        doc_updated_at="2024-01-01T00:00:00+00:00",
        doc_html=html,
        index=idx,
        out_dir=out_dir,
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


def test_run_sync_blocks_empty_index_with_existing_raw_exports(tmp_path: Path) -> None:
    """Real sync must not bootstrap an empty index over populated raw exports."""
    index_path = tmp_path / "readwise_library.json"
    out_dir = tmp_path / "raw" / "readwise"
    out_dir.mkdir(parents=True)
    (out_dir / "existing.html").write_text("<p>old</p>", encoding="utf-8")
    (out_dir / "existing.md").write_text("---\n---\n", encoding="utf-8")

    with httpx.Client(transport=httpx.MockTransport(lambda _r: httpx.Response(200))) as client:
        try:
            run_sync(
                "token",
                index_path=index_path,
                output_dir=out_dir,
                repo_root=tmp_path,
                client=client,
            )
        except ReadwiseIndexSafetyError as exc:
            assert "raw exports already exist" in str(exc)
        else:  # pragma: no cover - explicit failure branch
            raise AssertionError("expected ReadwiseIndexSafetyError")


def test_run_sync_allows_intentional_index_bootstrap(tmp_path: Path) -> None:
    """The bootstrap guard can be overridden for a deliberate first sync."""
    index_path = tmp_path / "readwise_library.json"
    out_dir = tmp_path / "raw" / "readwise"
    out_dir.mkdir(parents=True)
    (out_dir / "existing.html").write_text("<p>old</p>", encoding="utf-8")
    (out_dir / "existing.md").write_text("---\n---\n", encoding="utf-8")
    payload = {
        "count": 0,
        "nextPageCursor": None,
        "results": [],
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = run_sync(
            "token",
            index_path=index_path,
            output_dir=out_dir,
            repo_root=tmp_path,
            allow_index_bootstrap=True,
            client=client,
        )

    assert result.examined == 0


def test_run_sync_dry_run_allows_empty_index_with_existing_raw_exports(tmp_path: Path) -> None:
    """Dry-run can inspect the API without mutating the unsafe local state."""
    index_path = tmp_path / "readwise_library.json"
    out_dir = tmp_path / "raw" / "readwise"
    out_dir.mkdir(parents=True)
    (out_dir / "existing.html").write_text("<p>old</p>", encoding="utf-8")
    (out_dir / "existing.md").write_text("---\n---\n", encoding="utf-8")
    payload = {
        "count": 1,
        "nextPageCursor": None,
        "results": [_row("doc1", "2024-01-03T00:00:00+00:00", html="<p>Hi</p>")],
    }

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
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
    LibraryIndex(documents={}, last_updated_after="2020-01-01T00:00:00+00:00").save(index_path)

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
