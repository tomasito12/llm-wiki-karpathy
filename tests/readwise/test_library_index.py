"""Tests for Readwise library index persistence."""

from __future__ import annotations

from pathlib import Path

from src.readwise.library_index import ExportedRecord, LibraryIndex


def test_library_index_roundtrip_save_and_load(tmp_path: Path) -> None:
    """Saved index reloads with identical document records."""
    path = tmp_path / "idx.json"
    original = LibraryIndex(
        documents={
            "id1": ExportedRecord(
                html_path="raw/readwise/a.html",
                md_path="raw/readwise/a.md",
                source_url="https://example.com",
                updated_at="2024-01-01T00:00:00+00:00",
                content_sha256="deadbeef",
            )
        },
        last_updated_after="2024-01-02T00:00:00+00:00",
    )
    original.save(path)
    loaded = LibraryIndex.load(path)
    assert loaded.last_updated_after == original.last_updated_after
    assert loaded.documents["id1"].html_path == "raw/readwise/a.html"
    assert loaded.documents["id1"].content_sha256 == "deadbeef"


def test_library_index_load_missing_file_returns_empty() -> None:
    """Missing path behaves like an empty index."""
    idx = LibraryIndex.load(Path("/nonexistent/readwise.json"))
    assert idx.documents == {}
    assert idx.last_updated_after is None
