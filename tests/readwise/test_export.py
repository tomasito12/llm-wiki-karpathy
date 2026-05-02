"""Tests for Readwise HTML/Markdown export helpers."""

from __future__ import annotations

from pathlib import Path

from src.readwise.export import (
    build_markdown_sidecar,
    export_paths_for,
    json_list_yaml,
    plaintext_excerpt_from_html,
    write_document_export,
)
from src.readwise.models import ReaderDocument


def test_plaintext_excerpt_from_html_strips_tags() -> None:
    html = "<div><p>Hello</p><script>x</script><p>World</p></div>"
    excerpt = plaintext_excerpt_from_html(html, max_chars=100)
    assert excerpt == "Hello World"


def test_plaintext_excerpt_truncates_long_text() -> None:
    long_inner = "word " * 2000
    html = f"<p>{long_inner}</p>"
    excerpt = plaintext_excerpt_from_html(html, max_chars=50)
    assert excerpt.endswith("…")
    assert len(excerpt) <= 50


def test_build_markdown_sidecar_prefers_summary_over_excerpt() -> None:
    doc = ReaderDocument(
        id="abc",
        title="T",
        author="A",
        source_url="https://example.com/u",
        category="article",
        location="archive",
        published_date="2024-01-01",
        saved_at=None,
        updated_at=None,
        summary="From Reader summary field.",
        html_content="<p>HTML only</p>",
        parent_id=None,
        tags={"processed": True},
    )
    md = build_markdown_sidecar(doc, excerpt="excerpt text")
    assert "From Reader summary field." in md
    assert "excerpt text" not in md
    assert "readwise_id:" in md


def test_build_markdown_sidecar_falls_back_to_excerpt_when_summary_empty() -> None:
    doc = ReaderDocument(
        id="abc",
        title="T",
        author=None,
        source_url=None,
        category="article",
        location="archive",
        published_date=None,
        saved_at=None,
        updated_at=None,
        summary="   ",
        html_content=None,
        parent_id=None,
        tags={},
    )
    md = build_markdown_sidecar(doc, excerpt="fallback excerpt")
    assert "fallback excerpt" in md


def test_json_list_yaml_formats_flow_sequence() -> None:
    assert json_list_yaml(["a", "b"]) == '["a", "b"]'


def test_write_document_export_creates_paired_files(tmp_path: Path) -> None:
    doc = ReaderDocument(
        id="01gwfvp9pyaabcdgmx14f6ha0",
        title="My Article Title",
        author=None,
        source_url="https://example.com/p",
        category="article",
        location="archive",
        published_date=None,
        saved_at=None,
        updated_at="2024-01-02T00:00:00+00:00",
        summary="",
        html_content="<p>Paragraph one.</p>",
        parent_id=None,
        tags={},
    )
    record, rel_h, rel_m = write_document_export(doc, tmp_path, relative_prefix="raw/readwise")
    assert record.html_path.startswith("raw/readwise/")
    assert record.md_path.startswith("raw/readwise/")
    assert rel_h == record.html_path
    paths = export_paths_for(doc, tmp_path)
    assert paths.html_path.read_text(encoding="utf-8") == "<p>Paragraph one.</p>"
    md_text = paths.md_path.read_text(encoding="utf-8")
    assert "Paragraph one." in md_text
