"""Tests for full source text in generated source pages."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_render import cli as render_cli
from src.wiki_render.collect import collect_items
from src.wiki_render.merge import build_knowledge_graph
from src.wiki_render.models import SourceRecord
from src.wiki_render.render import render_graph
from src.wiki_render.render.source import render_source_page
from src.wiki_render.source_text import load_raw_source_markdown


def test_source_page_includes_full_source_text_when_raw_markdown_exists(
    tmp_path: Path,
) -> None:
    """Source page includes ## Full source text when raw Markdown exists."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source-a.md").write_text(
        "# Article\n\nThis is the full article body.\n",
        encoding="utf-8",
    )
    source = _source_record("source-a")

    rendered = render_source_page(source, wiki_dir=tmp_path / "wiki", raw_dir=raw_dir)

    assert rendered.relative_path == "sources/source-a.md"
    assert "## Full source text" in rendered.text
    assert "This is the full article body." in rendered.text


def test_source_page_frontmatter_marks_full_text_available(tmp_path: Path) -> None:
    """Source page frontmatter has source_text_available: true."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source-a.md").write_text("Body text.\n", encoding="utf-8")
    source = _source_record("source-a")

    rendered = render_source_page(source, wiki_dir=tmp_path / "wiki", raw_dir=raw_dir)

    assert "source_text_available: true" in rendered.text
    assert "source_text_mode: full" in rendered.text
    assert "source_text_source: raw_markdown" in rendered.text


def test_missing_raw_markdown_renders_placeholder_and_false_frontmatter(
    tmp_path: Path,
) -> None:
    """Missing raw Markdown renders source_text_available: false and a clear placeholder."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    source = _source_record("source-a", raw_md_rel_path="")

    rendered = render_source_page(source, wiki_dir=tmp_path / "wiki", raw_dir=raw_dir)

    assert "source_text_available: false" in rendered.text
    assert "source_text_mode: missing" in rendered.text
    assert "source_text_source: none" in rendered.text
    assert "## Full source text" in rendered.text
    assert "Full source text is not available locally." in rendered.text


def test_existing_derived_page_links_remain_present(tmp_path: Path) -> None:
    """Existing derived-page links remain present."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source-a.md").write_text("Body.\n", encoding="utf-8")
    source = _source_record("source-a")
    source.derived_paths["derived_topics"] = {"topics/local-models.md"}

    rendered = render_source_page(source, wiki_dir=tmp_path / "wiki", raw_dir=raw_dir)

    assert "[[topics/local-models" in rendered.text
    assert "derived_topics:" in rendered.text


def test_existing_source_metadata_remains_present(tmp_path: Path) -> None:
    """Existing source metadata remains present."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source-a.md").write_text("Body.\n", encoding="utf-8")
    source = _source_record("source-a")

    rendered = render_source_page(source, wiki_dir=tmp_path / "wiki", raw_dir=raw_dir)

    assert "## Source metadata" in rendered.text
    assert "Canonical URL: https://example.com" in rendered.text
    assert "`raw/readwise/source-a.md`" in rendered.text
    assert "`raw/readwise/source-a.html`" in rendered.text


def test_renderer_respects_configured_raw_dir(tmp_path: Path) -> None:
    """Renderer respects configured raw_dir."""
    external_raw = tmp_path / "external-raw"
    external_raw.mkdir()
    (external_raw / "source-a.md").write_text(
        "External raw body.\n",
        encoding="utf-8",
    )
    graph = _graph_with_source("source-a", tmp_path / "wiki")

    rendered = render_graph(graph, wiki_dir=tmp_path / "wiki", raw_dir=external_raw)
    source_page = next(file for file in rendered if file.relative_path == "sources/source-a.md")

    assert "External raw body." in source_page.text


def test_explicit_raw_dir_override_wins_over_default_path(tmp_path: Path) -> None:
    """Explicit raw_dir override wins over repo-local raw_md_rel_path fallback."""
    default_raw = tmp_path / "raw" / "readwise"
    override_raw = tmp_path / "override-raw"
    default_raw.mkdir(parents=True)
    override_raw.mkdir()
    (default_raw / "source-a.md").write_text("Default body.\n", encoding="utf-8")
    (override_raw / "source-a.md").write_text("Override body.\n", encoding="utf-8")
    source = _source_record("source-a")

    rendered = render_source_page(
        source,
        wiki_dir=tmp_path / "wiki",
        raw_dir=override_raw,
        repo_root=tmp_path,
    )

    assert "Override body." in rendered.text
    assert "Default body." not in rendered.text


def test_configured_wiki_dir_writes_sources_not_sources_full(tmp_path: Path) -> None:
    """Configured wiki_dir still renders source pages to sources/<source_id>.md."""
    raw_dir = tmp_path / "raw" / "readwise"
    wiki_dir = tmp_path / "external-wiki"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source-a.md").write_text("Body.\n", encoding="utf-8")
    graph = _graph_with_source("source-a", wiki_dir)

    rendered = render_graph(graph, wiki_dir=wiki_dir, raw_dir=raw_dir)

    assert any(file.relative_path == "sources/source-a.md" for file in rendered)
    assert not any(file.relative_path.startswith("sources/full/") for file in rendered)


def test_wiki_render_require_source_text_fails_on_low_coverage(
    tmp_path: Path,
    caplog,
) -> None:
    """wiki-render --require-source-text should fail when raw exports are missing."""
    repo = tmp_path / "repo"
    reviews_dir = repo / "state" / "reviews"
    wiki_dir = repo / "wiki"
    raw_dir = repo / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    reviews_dir.mkdir(parents=True)
    wiki_dir.mkdir()
    review_dir = reviews_dir / "source-a"
    review_dir.mkdir()
    review_dir.joinpath("review.json").write_text(
        json.dumps(_review_artifact("source-a")),
        encoding="utf-8",
    )

    exit_code = render_cli.main(
        [
            "--reviews-dir",
            str(reviews_dir),
            "--out-dir",
            str(wiki_dir),
            "--graph-path",
            str(repo / "state" / "wiki_render_graph.json"),
            "--manifest-path",
            str(repo / "state" / "wiki_render_manifest.json"),
            "--raw-dir",
            str(raw_dir),
            "--dry-run",
            "--require-source-text",
        ]
    )

    assert exit_code == 2
    assert "Low source full-text coverage" in caplog.text


def test_wiki_render_dry_run_completes_with_full_text(tmp_path: Path) -> None:
    """wiki-render --dry-run still works with full source text enabled."""
    repo = tmp_path / "repo"
    raw_dir = repo / "raw" / "readwise"
    reviews_dir = repo / "state" / "reviews"
    wiki_dir = repo / "wiki"
    raw_dir.mkdir(parents=True)
    reviews_dir.mkdir(parents=True)
    wiki_dir.mkdir()
    (raw_dir / "source-a.md").write_text("Dry-run body.\n", encoding="utf-8")
    review_dir = reviews_dir / "source-a"
    review_dir.mkdir()
    review_dir.joinpath("review.json").write_text(
        json.dumps(_review_artifact("source-a")),
        encoding="utf-8",
    )

    exit_code = render_cli.main(
        [
            "--reviews-dir",
            str(reviews_dir),
            "--out-dir",
            str(wiki_dir),
            "--graph-path",
            str(repo / "state" / "wiki_render_graph.json"),
            "--manifest-path",
            str(repo / "state" / "wiki_render_manifest.json"),
            "--raw-dir",
            str(raw_dir),
            "--dry-run",
        ]
    )

    assert exit_code == 0


def test_load_raw_source_markdown_falls_back_to_raw_md_rel_path(tmp_path: Path) -> None:
    """load_raw_source_markdown can resolve raw_md_rel_path relative to repo root."""
    repo = tmp_path / "repo"
    raw_dir = repo / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    rel_path = Path("raw/readwise/source-a.md")
    (repo / rel_path).write_text("Fallback body.\n", encoding="utf-8")
    source = _source_record("source-a")

    loaded = load_raw_source_markdown(
        source,
        raw_dir=tmp_path / "missing-raw",
        repo_root=repo,
    )

    assert loaded.available is True
    assert loaded.text == "Fallback body.\n"


def _source_record(source_id: str, *, raw_md_rel_path: str | None = None) -> SourceRecord:
    """Build a minimal source record for renderer tests."""
    md_rel = raw_md_rel_path if raw_md_rel_path is not None else f"raw/readwise/{source_id}.md"
    return SourceRecord(
        source_id=source_id,
        title="Example Source",
        author="Author",
        publication="Publication",
        canonical_url="https://example.com",
        published_date="2026-01-01",
        assessed_as_of="2026-01-01",
        ingested_at="2026-01-02T00:00:00+00:00",
        content_sha256="abc",
        raw_md_rel_path=md_rel,
        raw_html_rel_path=f"raw/readwise/{source_id}.html",
        summary="Summary.",
        accessible_overview="Overview.",
        key_insights=["Insight."],
        why_it_matters="It matters.",
        limitations_and_open_questions="Open questions.",
        contradictions_and_skepticism="None.",
    )


def _graph_with_source(source_id: str, wiki_dir: Path):
    """Build a minimal graph containing one source."""
    artifacts = [_review_artifact(source_id)]
    collected = collect_items(artifacts, wiki_dir)
    return build_knowledge_graph(collected, wiki_dir=wiki_dir, taxonomy_version="tax-test")


def _review_artifact(source_id: str) -> dict:
    """Return a minimal review artifact for collection tests."""
    return {
        "source": {
            "source_id": source_id,
            "title": "Example Source",
            "author": "Author",
            "publication": "Publication",
            "published_date": "2026-01-01",
            "canonical_url": "https://example.com",
            "content_sha256": "abc",
            "raw_md_rel_path": f"raw/readwise/{source_id}.md",
            "raw_html_rel_path": f"raw/readwise/{source_id}.html",
        },
        "analysis_meta": {"analysis_timestamp_utc": "2026-01-02T00:00:00+00:00"},
        "llm_output": {
            "source_summary": {
                "summary": "Summary.",
                "accessible_overview": "Overview.",
                "key_insights": ["Insight."],
                "why_it_matters": "It matters.",
                "limitations_and_open_questions": "Open questions.",
                "contradictions_and_skepticism": "None.",
                "assessed_as_of": "2026-01-01",
            },
            "source_evidence_profile": {"primary_evidence_type": "expert_opinion"},
        },
        "review": {
            "source_summary": {},
            "source_evidence_profile": {
                "llm_item": {"primary_evidence_type": "expert_opinion"},
                "final_item": None,
            },
            "topics": [
                {
                    "proposal_status": "approved",
                    "llm_item": {
                        "topic_slug": "local-models",
                        "topic_title": "Local Models",
                        "knowledge_summary": "Local models run near users.",
                        "operational_insight": "Treat local inference as infrastructure.",
                        "key_points": ["Hardware constraints shape reliability."],
                        "related_topics": [],
                        "related_terms": [],
                        "proposed_tags": ["infrastructure"],
                        "confidence": 0.9,
                        "value_level": "high",
                    },
                    "sections": {},
                    "tags": {"final_tags": ["infrastructure"]},
                }
            ],
        },
        "review_analytics": {"review_finished_at": "2026-01-03T00:00:00+00:00"},
    }
