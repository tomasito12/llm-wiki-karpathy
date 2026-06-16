"""Tests for rendering knowledge pages from Stage 2 synthesis cache entries."""

from __future__ import annotations

from pathlib import Path

from src.pipeline.atomic import atomic_write_json
from src.wiki_render.evidence import EvidenceItem
from src.wiki_render.models import KnowledgePage
from src.wiki_render.render.knowledge import render_knowledge_page
from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.render_input import synthesis_input_hash_for_knowledge_page


def test_render_knowledge_page_uses_fresh_synthesis_cache(tmp_path: Path) -> None:
    """A fresh cache entry should render the Stage 2 synthesis shape."""
    page = _knowledge_page()
    _write_cache(tmp_path, page, input_hash=synthesis_input_hash_for_knowledge_page(page))

    rendered = render_knowledge_page(page, synthesis_cache_dir=tmp_path)

    assert "synthesis_state: synthesized" in rendered.text
    assert "## Executive synthesis" in rendered.text
    assert "Local models make inference controllable." in rendered.text
    assert "## Evidence index" in rendered.text
    assert "Current input hash:" in rendered.text


def test_render_knowledge_page_marks_stale_synthesis_cache(tmp_path: Path) -> None:
    """A stale but complete cache entry should be visible as stale."""
    page = _knowledge_page()
    _write_cache(tmp_path, page, input_hash="oldhash")

    rendered = render_knowledge_page(page, synthesis_cache_dir=tmp_path)

    assert "synthesis_state: stale" in rendered.text
    assert "synthesis_stale: true" in rendered.text
    assert "[!warning] Synthesis may be stale" in rendered.text
    assert "Cached input hash: `oldhash`" in rendered.text


def test_render_knowledge_page_falls_back_without_cache(tmp_path: Path) -> None:
    """A missing cache entry should keep the existing Stage 1 render."""
    rendered = render_knowledge_page(_knowledge_page(), synthesis_cache_dir=tmp_path)

    assert "synthesis_state: stage1-placeholder" in rendered.text
    assert "stage1-placeholder" in rendered.text
    assert "## Evidence / supporting sources" in rendered.text


def _write_cache(cache_dir: Path, page: KnowledgePage, *, input_hash: str) -> None:
    """Write one complete synthesis cache fixture."""
    cache_path = cache_file_path(cache_dir, category=page.category, slug=page.slug)
    atomic_write_json(
        cache_path,
        {
            "entity_id": page.entity_id,
            "category": page.category,
            "slug": page.slug,
            "title": page.title,
            "synthesis_schema_version": 1,
            "synthesis_prompt_version": 1,
            "synthesis_input_hash": input_hash,
            "last_synthesized_at": "2026-06-16T00:00:00Z",
            "executive_synthesis": "Local models make inference controllable.",
            "what_to_remember": ["Use them when privacy or latency matters."],
            "consensus": ["They trade hosted convenience for control."],
            "tensions": ["They add operational work."],
            "evidence_quality": ["Two sources with consistent practitioner claims."],
            "practical_takeaway": "Start with narrow workloads before broad rollout.",
            "context_card": {
                "use_this_page_when": "Answering local deployment questions.",
                "best_for_questions_about": ["privacy", "latency"],
                "not_enough_for": ["benchmark selection"],
                "strongest_sources": ["Source A"],
                "related_tags": ["ai-engineering"],
            },
        },
    )


def _knowledge_page() -> KnowledgePage:
    """Return a minimal knowledge page with two sources."""
    evidence = [
        EvidenceItem(
            evidence_id="abc",
            text="Local models run near users.",
            source_id="source-a",
            source_title="Source A",
            source_date="2026-01-01",
            published_date="2026-01-01",
            assessed_as_of="2026-06-16",
            ingested_at="2026-06-16T00:00:00Z",
            category="topic",
            entity_slug="local-models",
            confidence=0.9,
            value_level="high",
            provenance="summary",
            stance="supporting",
            evidence_type="claim",
            field="knowledge_summary",
        )
    ]
    return KnowledgePage(
        category="topic",
        slug="local-models",
        title="Local Models",
        path="topics/local-models.md",
        entity_id="topic:local-models",
        aliases=[],
        tags=["ai-engineering"],
        types=[],
        values={"knowledge_summary": "Local models run near users."},
        evidence=evidence,
        source_ids=["source-a", "source-b"],
        source_titles={"source-a": "Source A", "source-b": "Source B"},
        first_seen="2026-01-01",
        last_seen="2026-06-16",
        source_count=2,
        evidence_count=1,
        evidence_set_hash="hash",
        stance_counts={"supporting": 1, "counter": 0, "uncertainty": 0, "neutral": 0},
        confidence=0.9,
        value_level="high",
    )
