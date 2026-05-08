"""Tests for rebuilding Readwise library index from disk."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from src.readwise.library_index import ExportedRecord, LibraryIndex
from src.readwise.rebuild import (
    main as rebuild_main,
)
from src.readwise.rebuild import (
    read_readwise_fields_from_md,
    rebuild_library_index_from_disk,
)


def test_read_readwise_fields_from_frontmatter() -> None:
    md = (
        '---\nreadwise_id: "01abc"\nsource_url: "https://ex.test/p"\n'
        'updated_at: "2024-01-02T00:00:00+00:00"\n---\n\nbody\n'
    )
    doc_id, url, updated = read_readwise_fields_from_md(md, stem="ignored")
    assert doc_id == "01abc"
    assert url == "https://ex.test/p"
    assert updated == "2024-01-02T00:00:00+00:00"


def test_read_readwise_id_fallback_from_stem() -> None:
    stem = "my-title-01kqkv211fd31ce6qv924evxhr"
    md = '---\ntitle: "T"\n---\n'
    doc_id, _, _ = read_readwise_fields_from_md(md, stem=stem)
    assert doc_id == "01kqkv211fd31ce6qv924evxhr"


def test_rebuild_empty_raw_dir(tmp_path: Path) -> None:
    raw = tmp_path / "rw"
    raw.mkdir()
    idx = tmp_path / "lib.json"
    result = rebuild_library_index_from_disk(raw, idx)
    assert result.scanned_html == 0
    assert result.indexed == 0
    loaded = LibraryIndex.load(idx)
    assert loaded.documents == {}
    assert loaded.last_updated_after is None


def test_rebuild_indexes_pair_and_watermark(tmp_path: Path) -> None:
    raw = tmp_path / "rw"
    raw.mkdir()
    idx = tmp_path / "lib.json"
    stem = "post-01aaa"
    html = "<p>hello</p>"
    md = (
        '---\nreadwise_id: "01aaa"\nsource_url: "https://example.com/x"\n'
        'updated_at: "2024-03-01T12:00:00+00:00"\n---\n\nx\n'
    )
    (raw / f"{stem}.html").write_text(html, encoding="utf-8")
    (raw / f"{stem}.md").write_text(md, encoding="utf-8")

    result = rebuild_library_index_from_disk(raw, idx)
    assert result.indexed == 1
    assert result.watermark == "2024-03-01T12:00:00+00:00"
    loaded = LibraryIndex.load(idx)
    assert "01aaa" in loaded.documents
    rec = loaded.documents["01aaa"]
    assert rec.md_path == f"raw/readwise/{stem}.md"
    assert rec.html_path == f"raw/readwise/{stem}.html"
    assert rec.source_url == "https://example.com/x"


def test_rebuild_skips_html_without_md(tmp_path: Path) -> None:
    raw = tmp_path / "rw"
    raw.mkdir()
    idx = tmp_path / "lib.json"
    (raw / "orphan.html").write_text("<p>x</p>", encoding="utf-8")
    result = rebuild_library_index_from_disk(raw, idx)
    assert result.indexed == 0
    assert result.skipped == [("orphan.html", "missing_md_sidecar")]


def test_rebuild_refuses_nonempty_index_without_force(tmp_path: Path) -> None:
    raw = tmp_path / "rw"
    raw.mkdir()
    idx = tmp_path / "lib.json"
    LibraryIndex(
        documents={
            "x": ExportedRecord(
                html_path="a.html",
                md_path="a.md",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            )
        },
        last_updated_after=None,
    ).save(idx)
    with pytest.raises(ValueError, match="Refusing to overwrite"):
        rebuild_library_index_from_disk(raw, idx, force=False)


def test_rebuild_dry_run_does_not_write(tmp_path: Path) -> None:
    raw = tmp_path / "rw"
    raw.mkdir()
    idx = tmp_path / "lib.json"
    stem = "post-01bbb"
    (raw / f"{stem}.html").write_text("<p>x</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text(
        '---\nreadwise_id: "01bbb"\nupdated_at: "2024-01-01T00:00:00+00:00"\n---\n',
        encoding="utf-8",
    )
    rebuild_library_index_from_disk(raw, idx, dry_run=True)
    assert not idx.exists()


def test_rebuild_cli_dry_run(tmp_path: Path) -> None:
    raw = tmp_path / "rw"
    raw.mkdir()
    idx = tmp_path / "lib.json"
    argv = ["rebuild", "--raw-dir", str(raw), "--index", str(idx), "--dry-run"]
    with mock.patch("sys.argv", argv):
        assert rebuild_main() == 0
