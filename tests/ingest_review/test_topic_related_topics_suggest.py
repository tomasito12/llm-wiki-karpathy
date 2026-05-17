"""Tests for related-topic suggestion heuristics."""

from __future__ import annotations

from src.ingest_review.schema import TopicContribution
from src.ingest_review.topic_related_topics_suggest import (
    RelatedTopicCandidate,
    build_topic_slug_catalog,
    build_topic_slug_catalog_from_topics,
    format_suggestion_line,
    suggest_related_topics,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def _empty_wiki(
    *,
    topic_titles: list[str] | None = None,
    topic_slugs: list[str] | None = None,
) -> WikiSnapshot:
    return WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        topic_titles=topic_titles or [],
        topic_slugs=topic_slugs or [],
    )


def test_build_topic_slug_catalog_includes_wiki_topics() -> None:
    wiki = _empty_wiki(topic_titles=["Context Engineering"], topic_slugs=["context-engineering"])
    catalog = build_topic_slug_catalog(wiki, None, None, exclude_slug="")
    slugs = {c.slug for c in catalog}
    assert "context-engineering" in slugs
    by_slug = {c.slug: c for c in catalog}
    assert by_slug["context-engineering"].source == "wiki"


def test_build_topic_slug_catalog_batch_from_artifact_llm_output() -> None:
    wiki = _empty_wiki()
    artifact = {
        "llm_output": {
            "topics": [
                {
                    "topic_slug": "rag-patterns",
                    "topic_title": "RAG patterns",
                    "primary_tag": "x",
                },
            ],
        },
        "review": {"topics": []},
    }
    catalog = build_topic_slug_catalog(wiki, None, artifact, exclude_slug="")
    assert any(c.slug == "rag-patterns" and c.source == "batch" for c in catalog)


def test_build_topic_slug_catalog_excludes_self_slug() -> None:
    wiki = _empty_wiki(topic_slugs=["agent-memory", "context-engineering"])
    catalog = build_topic_slug_catalog(wiki, None, None, exclude_slug="agent-memory")
    assert "agent-memory" not in {c.slug for c in catalog}


def test_suggest_related_topics_caps_at_three_and_excludes_self() -> None:
    catalog = [
        RelatedTopicCandidate("context-engineering", "Context Engineering", "wiki"),
        RelatedTopicCandidate("rag-patterns", "RAG patterns", "batch"),
        RelatedTopicCandidate("prompt-engineering", "Prompt engineering", "review"),
        RelatedTopicCandidate("agent-memory", "Agent memory", "wiki"),
    ]
    out = suggest_related_topics(
        "agent-memory",
        "Agent memory systems",
        "How agents retain context across turns.",
        catalog,
        cap=3,
    )
    assert len(out) <= 3
    assert all(c.slug != "agent-memory" for c in out)


def test_suggest_related_topics_prefers_similar_titles() -> None:
    catalog = [
        RelatedTopicCandidate("unrelated-topic", "Cooking recipes", "wiki"),
        RelatedTopicCandidate("context-engineering", "Context Engineering", "wiki"),
    ]
    out = suggest_related_topics(
        "rag-patterns",
        "RAG patterns",
        "Retrieval augments generation with context engineering techniques.",
        catalog,
        cap=1,
    )
    assert len(out) == 1
    assert out[0].slug == "context-engineering"


def test_build_topic_slug_catalog_from_topics_for_analyze() -> None:
    wiki = _empty_wiki(topic_slugs=["wiki-only"])
    batch = [
        TopicContribution(topic_slug="batch-a", topic_title="Batch A"),
        TopicContribution(topic_slug="batch-b", topic_title="Batch B"),
    ]
    catalog = build_topic_slug_catalog_from_topics(wiki, None, batch)
    slugs = {c.slug for c in catalog}
    assert "wiki-only" in slugs
    assert "batch-a" in slugs
    assert "batch-b" in slugs


def test_format_suggestion_line_includes_source() -> None:
    line = format_suggestion_line(
        RelatedTopicCandidate("rag-patterns", "RAG patterns", "batch"),
    )
    assert "rag-patterns" in line
    assert "this review" in line


def test_batch_source_wins_over_wiki_on_duplicate_slug() -> None:
    wiki = _empty_wiki(topic_titles=["Wiki title"], topic_slugs=["shared-slug"])
    artifact = {
        "llm_output": {
            "topics": [
                {"topic_slug": "shared-slug", "topic_title": "Batch title", "primary_tag": "x"},
            ],
        },
    }
    catalog = build_topic_slug_catalog(wiki, None, artifact)
    entry = next(c for c in catalog if c.slug == "shared-slug")
    assert entry.source == "batch"
    assert entry.title == "Batch title"
