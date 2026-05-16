"""Tests for regeneration prompt context sections."""

from __future__ import annotations

from src.ingest_review.proposal_regen_context import build_regen_context_sections
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_build_regen_context_topic_includes_slugs_and_tags() -> None:
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        howto_titles=[],
        trend_titles=[],
        topic_slugs=["existing-slug"],
        trend_slugs=[],
    )
    artifact = {
        "review": {
            "topics": [
                {"llm_item": {"topic_slug": "from-artifact"}},
            ],
        },
    }
    ctx = build_regen_context_sections(
        "topic",
        artifact=artifact,
        wiki=wiki,
        topic_tags_allowlist=["ai-infrastructure"],
    )
    assert "existing-slug" in ctx["EXISTING_TOPIC_SLUGS"]
    assert "from-artifact" in ctx["EXISTING_TOPIC_SLUGS"]
    assert "ai-infrastructure" in ctx["TOPIC_TAGS_ALLOWLIST"]
