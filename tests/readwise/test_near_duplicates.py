"""Tests for near-duplicate Readwise export cleanup."""

from __future__ import annotations

from pathlib import Path

from src.readwise.library_index import ExportedRecord, LibraryIndex
from src.readwise.near_duplicates import (
    DuplicatePair,
    choose_shorter_stem,
    delete_export,
    extract_doc_id,
    extract_text,
    find_duplicate_pairs,
    jaccard,
    load_documents,
    run_dedupe,
    word_shingles,
)


def _similar_html_pair() -> tuple[str, str]:
    """Return long/short HTML exports with high shingle overlap."""
    body = " ".join(f"word{i}" for i in range(30))
    long_html = f"<p>{body} extra padding words for length</p>"
    short_html = f"<p>{body}</p>"
    return long_html, short_html


def test_extract_text_strips_tags_and_normalizes_whitespace() -> None:
    """HTML tags are removed and whitespace is collapsed."""
    html = "<html><body><p>Hello</p>   <p>World</p></body></html>"
    assert extract_text(html) == "hello world"


def test_jaccard_identical_sets() -> None:
    """Identical shingle sets score 1.0."""
    shingles = word_shingles("one two three four five six")
    assert jaccard(shingles, shingles) == 1.0


def test_jaccard_disjoint_sets() -> None:
    """Disjoint shingle sets score 0.0."""
    a = word_shingles("alpha beta gamma delta epsilon zeta")
    b = word_shingles("one two three four five six")
    assert jaccard(a, b) == 0.0


def test_extract_doc_id_from_readwise_stem() -> None:
    """Readwise id is parsed from the trailing filename segment."""
    stem = "my-article-01kqh0vjnrvxfjbkwye8cmrtyv"
    assert extract_doc_id(stem) == "01kqh0vjnrvxfjbkwye8cmrtyv"


def test_extract_doc_id_returns_none_for_invalid_stem() -> None:
    """Non-Readwise stems do not produce a doc id."""
    assert extract_doc_id("plain-article") is None


def test_find_duplicate_pairs_detects_similar_documents(tmp_path: Path) -> None:
    """Similar HTML exports are reported as duplicate pairs."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    long_html, short_html = _similar_html_pair()
    (raw_dir / "long-doc-01kqh0vjnrvxfjbkwye8cmrtyv.html").write_text(long_html, encoding="utf-8")
    (raw_dir / "short-doc-01kqh0vjnrvxfjbkwye8cmrtyw.html").write_text(short_html, encoding="utf-8")

    docs = load_documents(raw_dir)
    pairs = find_duplicate_pairs(docs, threshold=0.50)

    assert len(pairs) == 1
    assert pairs[0].similarity >= 0.50


def test_choose_shorter_stem_prefers_less_text() -> None:
    """The shorter plain-text export is chosen for deletion."""
    pair = DuplicatePair(
        stem_a="long-doc-01kqh0vjnrvxfjbkwye8cmrtyv",
        stem_b="short-doc-01kqh0vjnrvxfjbkwye8cmrtyw",
        similarity=0.9,
        text_len_a=100,
        text_len_b=40,
    )
    assert choose_shorter_stem(pair, raw_dir=Path("/tmp")) == pair.stem_b


def test_delete_export_removes_files_and_suppresses_index(tmp_path: Path) -> None:
    """Deleting an export removes files and updates the library index."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    stem = "article-01kqh0vjnrvxfjbkwye8cmrtyv"
    (raw_dir / f"{stem}.html").write_text("<p>x</p>", encoding="utf-8")
    (raw_dir / f"{stem}.md").write_text("---\n---\n", encoding="utf-8")
    index = LibraryIndex(
        documents={
            "01kqh0vjnrvxfjbkwye8cmrtyv": ExportedRecord(
                html_path=f"raw/readwise/{stem}.html",
                md_path=f"raw/readwise/{stem}.md",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            )
        },
        last_updated_after=None,
    )

    delete_export(stem, raw_dir=raw_dir, index=index)

    assert not (raw_dir / f"{stem}.html").exists()
    assert not (raw_dir / f"{stem}.md").exists()
    assert "01kqh0vjnrvxfjbkwye8cmrtyv" in index.suppressed_ids
    assert "01kqh0vjnrvxfjbkwye8cmrtyv" not in index.documents


def test_run_dedupe_deletes_shorter_copy_by_default(tmp_path: Path) -> None:
    """Dedupe removes the shorter near-duplicate export automatically."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    index_path = tmp_path / "readwise_library.json"
    long_stem = "long-doc-01kqh0vjnrvxfjbkwye8cmrtyv"
    short_stem = "short-doc-01kqh0vjnrvxfjbkwye8cmrtyw"
    long_html, short_html = _similar_html_pair()
    (raw_dir / f"{long_stem}.html").write_text(long_html, encoding="utf-8")
    (raw_dir / f"{long_stem}.md").write_text("---\n---\n", encoding="utf-8")
    (raw_dir / f"{short_stem}.html").write_text(short_html, encoding="utf-8")
    (raw_dir / f"{short_stem}.md").write_text("---\n---\n", encoding="utf-8")
    LibraryIndex(
        documents={
            "01kqh0vjnrvxfjbkwye8cmrtyv": ExportedRecord(
                html_path=f"raw/readwise/{long_stem}.html",
                md_path=f"raw/readwise/{long_stem}.md",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            ),
            "01kqh0vjnrvxfjbkwye8cmrtyw": ExportedRecord(
                html_path=f"raw/readwise/{short_stem}.html",
                md_path=f"raw/readwise/{short_stem}.md",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            ),
        },
        last_updated_after=None,
    ).save(index_path)

    result = run_dedupe(raw_dir=raw_dir, index_path=index_path, threshold=0.50)

    assert result.pairs_found == 1
    assert result.deleted == (short_stem,)
    assert (raw_dir / f"{long_stem}.html").exists()
    assert not (raw_dir / f"{short_stem}.html").exists()
    loaded = LibraryIndex.load(index_path)
    assert "01kqh0vjnrvxfjbkwye8cmrtyw" in loaded.suppressed_ids


def test_run_dedupe_dry_run_does_not_delete_files(tmp_path: Path) -> None:
    """Dry-run reports deletions without touching disk."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    index_path = tmp_path / "readwise_library.json"
    long_stem = "long-doc-01kqh0vjnrvxfjbkwye8cmrtyv"
    short_stem = "short-doc-01kqh0vjnrvxfjbkwye8cmrtyw"
    long_html, short_html = _similar_html_pair()
    (raw_dir / f"{long_stem}.html").write_text(long_html, encoding="utf-8")
    (raw_dir / f"{short_stem}.html").write_text(short_html, encoding="utf-8")
    LibraryIndex.empty().save(index_path)

    result = run_dedupe(
        raw_dir=raw_dir,
        index_path=index_path,
        threshold=0.50,
        dry_run=True,
    )

    assert result.deleted == (short_stem,)
    assert (raw_dir / f"{long_stem}.html").exists()
    assert (raw_dir / f"{short_stem}.html").exists()


def test_run_dedupe_returns_empty_when_no_pairs(tmp_path: Path) -> None:
    """No duplicate pairs yields an empty deletion list."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    index_path = tmp_path / "readwise_library.json"
    (raw_dir / "alpha-01kqh0vjnrvxfjbkwye8cmrtyv.html").write_text(
        "<p>alpha beta gamma delta epsilon zeta eta theta iota kappa</p>",
        encoding="utf-8",
    )
    (raw_dir / "beta-01kqh0vjnrvxfjbkwye8cmrtyw.html").write_text(
        "<p>lambda mu nu xi omicron pi rho sigma tau upsilon phi</p>",
        encoding="utf-8",
    )
    LibraryIndex.empty().save(index_path)

    result = run_dedupe(raw_dir=raw_dir, index_path=index_path, threshold=0.50)

    assert result.pairs_found == 0
    assert result.deleted == ()


def test_run_dedupe_interactive_respects_skip(tmp_path: Path) -> None:
    """Interactive mode can skip a pair without deleting either export."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    index_path = tmp_path / "readwise_library.json"
    long_stem = "long-doc-01kqh0vjnrvxfjbkwye8cmrtyv"
    short_stem = "short-doc-01kqh0vjnrvxfjbkwye8cmrtyw"
    long_html, short_html = _similar_html_pair()
    (raw_dir / f"{long_stem}.html").write_text(long_html, encoding="utf-8")
    (raw_dir / f"{short_stem}.html").write_text(short_html, encoding="utf-8")
    LibraryIndex.empty().save(index_path)

    result = run_dedupe(
        raw_dir=raw_dir,
        index_path=index_path,
        threshold=0.50,
        interactive=True,
        input_fn=lambda _prompt: "s",
    )

    assert result.deleted == ()
    assert (raw_dir / f"{long_stem}.html").exists()
    assert (raw_dir / f"{short_stem}.html").exists()
