"""Tests for topic related_topics sanitization (no Streamlit)."""

from __future__ import annotations

from src.ingest_review.schema import LlmClassificationOutput, TopicContribution
from src.ingest_review.topic_related_topics import (
    known_topic_slug_set,
    sanitize_topic_related_topics,
    sanitize_topics_related_topics,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_sanitize_topic_related_topics_strips_tag_allowlist() -> None:
    """Tag allowlist slugs must not appear in related_topics."""
    out = sanitize_topic_related_topics(
        ["ai-engineering", "workflow-automation"],
        topic_slug="live-preview-loops",
        tag_allowlist={"ai-engineering", "knowledge-management"},
        known_topic_slugs={"workflow-automation", "live-preview-loops"},
    )
    assert out == ["workflow-automation"]


def test_sanitize_topic_related_topics_strips_self_and_dedupes() -> None:
    out = sanitize_topic_related_topics(
        ["rag-patterns", "rag-patterns", "context-engineering"],
        topic_slug="rag-patterns",
        tag_allowlist=set(),
        known_topic_slugs={"rag-patterns", "context-engineering"},
    )
    assert out == ["context-engineering"]


def test_sanitize_topic_related_topics_drops_unknown_slugs() -> None:
    """Slugs not in wiki/batch known set are removed."""
    out = sanitize_topic_related_topics(
        ["orchestration", "context-engineering"],
        topic_slug="agent-memory",
        tag_allowlist=set(),
        known_topic_slugs={"context-engineering", "agent-memory"},
    )
    assert out == ["context-engineering"]


def test_sanitize_topics_related_topics_on_parsed_output() -> None:
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        topic_slugs=["context-engineering"],
    )
    parsed = LlmClassificationOutput(
        topics=[
            TopicContribution(
                topic_slug="agent-memory",
                primary_tag="ai-engineering",
                related_topics=["ai-engineering", "context-engineering"],
            ),
            TopicContribution(
                topic_slug="context-engineering",
                related_topics=["agent-memory"],
            ),
        ],
    )
    out = sanitize_topics_related_topics(parsed, {"ai-engineering"}, wiki)
    assert out.topics[0].related_topics == ["context-engineering"]
    assert out.topics[1].related_topics == ["agent-memory"]


def test_known_topic_slug_set_unions_wiki_and_batch() -> None:
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        topic_slugs=["wiki-topic"],
    )
    batch = [TopicContribution(topic_slug="batch-topic")]
    known = known_topic_slug_set(wiki, batch)
    assert "wiki-topic" in known
    assert "batch-topic" in known
