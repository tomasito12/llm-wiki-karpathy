"""Tests for publication resolution and sidecar backfill."""

from __future__ import annotations

from pathlib import Path

from src.pipeline.source_publication import (
    backfill_publication_in_md_file,
    backfill_publications_in_raw_dir,
    derive_publication_from_url,
    resolve_publication,
)
from src.readwise.export import build_markdown_sidecar
from src.readwise.models import ReaderDocument


def test_derive_publication_from_medium_url() -> None:
    assert (
        derive_publication_from_url(
            "https://medium.com/no-time/8-crazy-things-claude-ai-can-do-that-chatgpt-cant-ef383eeb16f4"
        )
        == "Medium"
    )


def test_resolve_publication_prefers_site_name_over_url() -> None:
    assert (
        resolve_publication(
            "Vanity Fair",
            "https://medium.com/foo",
            author="Darryn King",
        )
        == "Vanity Fair"
    )


def test_resolve_publication_skips_site_name_when_matches_author() -> None:
    assert (
        resolve_publication(
            "Pranit naik",
            "https://medium.com/post",
            author="Pranit naik",
        )
        == "Medium"
    )


def test_build_markdown_sidecar_includes_publication() -> None:
    doc = ReaderDocument(
        id="01abc",
        title="T",
        author="A",
        source_url="https://medium.com/x/y",
        category="article",
        location="archive",
        published_date="2024-01-01",
        saved_at=None,
        updated_at=None,
        summary="",
        html_content=None,
        parent_id=None,
        tags={},
        site_name="Medium",
    )
    md = build_markdown_sidecar(doc, excerpt="body")
    assert 'publication: "Medium"' in md or 'publication: "Medium"' in md


def test_backfill_publication_in_md_file_adds_field(tmp_path: Path) -> None:
    md = tmp_path / "article-01abc.md"
    md.write_text(
        "---\n"
        'title: "Test"\n'
        'author: "Ann"\n'
        'source_url: "https://medium.com/foo/bar"\n'
        "---\n\n"
        "Body\n",
        encoding="utf-8",
    )
    assert backfill_publication_in_md_file(md) is True
    text = md.read_text(encoding="utf-8")
    assert "publication: Medium" in text


def test_backfill_publication_idempotent_when_unchanged(tmp_path: Path) -> None:
    md = tmp_path / "article-01abc.md"
    md.write_text(
        '---\npublication: "Medium"\nsource_url: "https://medium.com/foo"\n---\n\n',
        encoding="utf-8",
    )
    assert backfill_publication_in_md_file(md) is False


def test_backfill_publications_in_raw_dir_counts(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "a.md").write_text(
        '---\nsource_url: "https://openai.com/blog/x"\n---\n',
        encoding="utf-8",
    )
    (raw / "b.md").write_text("no frontmatter\n", encoding="utf-8")
    updated, skipped = backfill_publications_in_raw_dir(raw)
    assert updated == 1
    assert skipped == 1
