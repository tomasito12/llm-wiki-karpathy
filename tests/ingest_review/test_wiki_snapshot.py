"""Tests for wiki snapshot parsing."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.wiki_snapshot import (
    build_wiki_snapshot,
    parse_foundation_model_names,
    parse_glossary_terms,
    parse_wikilink_titles_from_bullets,
)


def test_parse_glossary_terms_reads_table(tmp_path: Path) -> None:
    """First column term text is extracted from glossary index table."""
    idx = tmp_path / "index.md"
    idx.write_text(
        "| Term | Page |\n|------|------|\n| Foo bar | [[glossary/terms/foo-bar]] |\n",
        encoding="utf-8",
    )
    terms = parse_glossary_terms(idx)
    assert "Foo bar" in terms


def test_parse_wikilink_titles_from_bullets(tmp_path: Path) -> None:
    """Question wikilinks yield slug-derived title hints."""
    cat = tmp_path / "qc.md"
    cat.write_text(
        "## ai-engineering\n\n- [[questions/q-what-determines-rag-effectiveness]]\n",
        encoding="utf-8",
    )
    hints = parse_wikilink_titles_from_bullets(cat)
    assert any("what determines rag effectiveness" in h.lower() for h in hints)


def test_parse_foundation_model_names_table(tmp_path: Path) -> None:
    """Foundation model index rows become names."""
    idx = tmp_path / "fm.md"
    idx.write_text(
        "| Model | Page |\n|-------|------|\n| GPT 5 | [[foundation-models/gpt-5]] |\n",
        encoding="utf-8",
    )
    names = parse_foundation_model_names(idx)
    assert any("gpt 5" in n.lower() for n in names)


def test_build_wiki_snapshot_empty_dirs(tmp_path: Path) -> None:
    """Missing wiki files yield empty lists without error."""
    wiki = tmp_path / "wiki"
    (wiki / "glossary").mkdir(parents=True)
    (wiki / "questions").mkdir(parents=True)
    (wiki / "tools").mkdir(parents=True)
    (wiki / "foundation-models").mkdir(parents=True)
    snap = build_wiki_snapshot(wiki)
    assert snap.glossary_terms == []
    assert snap.tool_names == []
