"""Tests for Readwise HTML / markdown extraction."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.extract import (
    content_sha256_from_plain_text,
    html_body_to_plain_text,
    list_readwise_html_sources,
    load_readwise_pair,
    parse_markdown_frontmatter,
    readwise_source_status,
)


def test_parse_markdown_frontmatter_reads_yaml() -> None:
    """Frontmatter keys are parsed and body is split correctly."""
    md = '---\ntitle: "Hello"\nauthor: Ann\n---\n\nBody here\n'
    meta, body = parse_markdown_frontmatter(md)
    assert meta["title"] == "Hello"
    assert meta["author"] == "Ann"
    assert body.strip() == "Body here"


def test_parse_markdown_frontmatter_empty_when_absent() -> None:
    """Text without frontmatter returns empty meta."""
    meta, body = parse_markdown_frontmatter("no frontmatter")
    assert meta == {}
    assert body == "no frontmatter"


def test_html_body_to_plain_text_strips_tags() -> None:
    """HTML is reduced to visible text."""
    html = "<div><p>Hello</p><script>x</script></div>"
    text = html_body_to_plain_text(html)
    assert "Hello" in text
    assert "<div>" not in text


def test_content_sha256_stable() -> None:
    """Same text yields same digest."""
    a = content_sha256_from_plain_text("alpha\nbeta")
    b = content_sha256_from_plain_text("alpha\nbeta")
    assert a == b
    assert len(a) == 64


def test_load_readwise_pair_roundtrip(tmp_path: Path) -> None:
    """Paired html/md produce a SourceDocument with matching hash."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "article-01abc"
    html = raw / f"{stem}.html"
    md = raw / f"{stem}.md"
    html.write_text("<html><body><p>Unique content xyz</p></body></html>", encoding="utf-8")
    md.write_text('---\ntitle: T\nsource_url: "https://ex.test/a"\n---\n', encoding="utf-8")
    doc = load_readwise_pair(html, max_plain_text_chars=10_000)
    assert doc.source_id == stem
    assert doc.title == "T"
    assert doc.canonical_url == "https://ex.test/a"
    assert "Unique content" in doc.plain_text
    assert len(doc.content_sha256) == 64


def test_list_readwise_html_sources_sorted(tmp_path: Path) -> None:
    """Glob returns sorted html paths."""
    d = tmp_path / "r"
    d.mkdir()
    (d / "b.html").write_text("<p>b</p>")
    (d / "a.html").write_text("<p>a</p>")
    paths = list_readwise_html_sources(d)
    assert [p.name for p in paths] == ["a.html", "b.html"]


def test_readwise_source_status_complete(tmp_path: Path) -> None:
    """Sibling md marks source complete."""
    h = tmp_path / "x.html"
    h.write_text("<p>x</p>")
    (tmp_path / "x.md").write_text("---\n---\n", encoding="utf-8")
    assert readwise_source_status(h) == "complete"


def test_readwise_source_status_incomplete(tmp_path: Path) -> None:
    """Missing md sidecar is incomplete."""
    h = tmp_path / "only.html"
    h.write_text("<p>x</p>")
    assert readwise_source_status(h) == "incomplete"
