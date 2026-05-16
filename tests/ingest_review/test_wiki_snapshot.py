"""Tests for wiki snapshot parsing."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.wiki_snapshot import (
    build_wiki_snapshot,
    parse_foundation_model_names,
    parse_glossary_terms,
    parse_howto_titles,
    parse_topic_slugs,
    parse_topic_titles,
    parse_trend_slugs,
    parse_trend_titles,
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


def test_parse_foundation_model_names_table(tmp_path: Path) -> None:
    """Foundation model index rows become names."""
    idx = tmp_path / "fm.md"
    idx.write_text(
        "| Model | Page |\n|-------|------|\n| GPT 5 | [[foundation-models/gpt-5]] |\n",
        encoding="utf-8",
    )
    names = parse_foundation_model_names(idx)
    assert any("gpt 5" in n.lower() for n in names)


def test_parse_topic_titles_reads_table(tmp_path: Path) -> None:
    """Topic titles are parsed from index table."""
    idx = tmp_path / "topics_index.md"
    idx.write_text(
        "| Topic | Page |\n|-------|------|\n"
        "| Context Engineering | [[topics/context-engineering]] |\n",
        encoding="utf-8",
    )
    titles = parse_topic_titles(idx)
    assert "Context Engineering" in titles


def test_parse_topic_slugs_from_wikilink(tmp_path: Path) -> None:
    """Topic slugs keep kebab-case from wikilink paths."""
    idx = tmp_path / "topics_index.md"
    idx.write_text(
        "| Topic | Page |\n|-------|------|\n"
        "| Context Engineering | [[topics/context-engineering]] |\n",
        encoding="utf-8",
    )
    slugs = parse_topic_slugs(idx)
    assert slugs == ["context-engineering"]


def test_parse_topic_titles_plain_text_cell(tmp_path: Path) -> None:
    """Topic titles without wikilinks are captured as-is."""
    idx = tmp_path / "topics_index.md"
    idx.write_text(
        "| Topic | Notes |\n|-------|-------|\n| Agent Memory | important |\n",
        encoding="utf-8",
    )
    titles = parse_topic_titles(idx)
    assert "Agent Memory" in titles


def test_parse_howto_titles_reads_table(tmp_path: Path) -> None:
    """How-to titles are parsed from index table."""
    idx = tmp_path / "howtos_index.md"
    idx.write_text(
        "| How-to | Page |\n|--------|------|\n"
        "| Build eval pipelines | [[howtos/build-eval-pipelines]] |\n",
        encoding="utf-8",
    )
    titles = parse_howto_titles(idx)
    assert "Build eval pipelines" in titles


def test_parse_trend_titles_reads_table(tmp_path: Path) -> None:
    """Trend titles are parsed from index table."""
    idx = tmp_path / "trends_index.md"
    idx.write_text(
        "| Trend | Page |\n|-------|------|\n"
        "| Inference cost collapse | [[trends/inference-cost-collapse]] |\n",
        encoding="utf-8",
    )
    titles = parse_trend_titles(idx)
    assert "Inference cost collapse" in titles


def test_parse_trend_slugs_reads_table(tmp_path: Path) -> None:
    """Trend slugs are parsed as kebab-case ids from index wikilinks."""
    idx = tmp_path / "trends_index.md"
    idx.write_text(
        "| Trend | Page |\n|-------|------|\n"
        "| Inference cost collapse | [[trends/inference-cost-collapse]] |\n",
        encoding="utf-8",
    )
    slugs = parse_trend_slugs(idx)
    assert slugs == ["inference-cost-collapse"]


def test_parse_topic_titles_missing_file(tmp_path: Path) -> None:
    """Missing topic index returns empty list."""
    titles = parse_topic_titles(tmp_path / "nonexistent.md")
    assert titles == []


def test_build_wiki_snapshot_empty_dirs(tmp_path: Path) -> None:
    """Missing wiki files yield empty lists without error."""
    wiki = tmp_path / "wiki"
    (wiki / "glossary").mkdir(parents=True)
    (wiki / "tools").mkdir(parents=True)
    (wiki / "foundation-models").mkdir(parents=True)
    snap = build_wiki_snapshot(wiki)
    assert snap.glossary_terms == []
    assert snap.tool_names == []
    assert snap.topic_titles == []
    assert snap.howto_titles == []
    assert snap.trend_titles == []
    assert snap.trend_slugs == []


def test_wiki_snapshot_no_question_hints_field() -> None:
    """WikiSnapshot no longer has the question_hints field."""
    from dataclasses import fields as dc_fields

    from src.ingest_review.wiki_snapshot import WikiSnapshot

    field_names = {f.name for f in dc_fields(WikiSnapshot)}
    assert "question_hints" not in field_names
