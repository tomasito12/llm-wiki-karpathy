"""Tests for page-matching post-LLM guardrails and heuristics."""

from __future__ import annotations

from src.ingest_review.canonical_titles import (
    CANONICAL_FUZZY_ALIGN_MIN_SCORE,
    CanonicalTitleEntry,
    align_parsed_classification_titles,
    build_canonical_index,
    find_canonical_match,
    format_canonical_block,
)
from src.ingest_review.schema import LlmClassificationOutput, TopicContribution
from src.ingest_review.topic_related_topics import sanitize_topics_related_topics
from src.ingest_review.topic_related_topics_suggest import (
    RELATED_TOPIC_SUGGEST_MIN_SCORE,
    RelatedTopicCandidate,
    suggest_related_topics,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_find_canonical_match_rejects_adjacent_titles() -> None:
    """Adjacent security topics must not fuzzy-match at default threshold."""
    entries = [
        CanonicalTitleEntry(
            title="Privacy Controls for AI Products",
            slug="privacy-controls-for-ai-products",
        ),
    ]
    assert find_canonical_match("Cybersecurity Operations", entries) is None
    assert find_canonical_match("Trusted Access and Zero Trust", entries) is None


def test_find_canonical_match_still_aligns_typo_variants() -> None:
    """High-threshold fuzzy match still corrects near-identical titles."""
    entries = [CanonicalTitleEntry(title="Harness Decay", slug="harness-decay")]
    match = find_canonical_match("Harness decay", entries)
    assert match is not None
    assert match.title == "Harness Decay"
    assert CANONICAL_FUZZY_ALIGN_MIN_SCORE >= 0.95


def test_format_canonical_block_includes_page_matching_preamble() -> None:
    """Non-empty canonical lists warn that entries are not default append targets."""
    body = format_canonical_block(
        [CanonicalTitleEntry(title="Privacy Controls for AI Products", slug="privacy-controls")]
    )
    assert "PAGE_MATCHING_RUBRIC" in body
    assert "not** default append targets" in body


def test_suggest_related_topics_excludes_weak_privacy_match_for_cyber_defense() -> None:
    """Cyber-defense topic must not backfill privacy-controls as related."""
    catalog = [
        RelatedTopicCandidate(
            slug="privacy-controls-for-ai-products",
            title="Privacy Controls for AI Products",
            source="wiki",
        ),
        RelatedTopicCandidate(
            slug="identity-and-access-management",
            title="Identity and Access Management",
            source="wiki",
        ),
    ]
    suggestions = suggest_related_topics(
        "zero-trust-access",
        "Zero Trust Access",
        "Trusted access and cyber defense for enterprise environments.",
        catalog,
        min_score=RELATED_TOPIC_SUGGEST_MIN_SCORE,
    )
    slugs = {s.slug for s in suggestions}
    assert "privacy-controls-for-ai-products" not in slugs


def test_align_parsed_classification_keeps_new_topic_when_no_strong_match() -> None:
    """Post-LLM align must not remap a distinct topic onto an adjacent canonical page."""
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=["Privacy Controls for AI Products"],
        topic_slugs=["privacy-controls-for-ai-products"],
        howto_titles=[],
        trend_titles=[],
    )
    index = build_canonical_index(wiki, None)
    parsed = LlmClassificationOutput(
        topics=[
            TopicContribution(
                topic_slug="zero-trust-access",
                topic_title="Zero Trust Access",
                knowledge_summary="Enterprise trusted access and cyber defense patterns.",
                value_level="high",
                confidence=0.85,
            ),
        ],
    )
    aligned = align_parsed_classification_titles(parsed, index)
    topic = aligned.topics[0]
    assert topic.topic_slug == "zero-trust-access"
    assert topic.topic_title == "Zero Trust Access"


def test_sanitize_topics_related_topics_still_strips_tags() -> None:
    """Tag allowlist slugs must not appear in related_topics after sanitization."""
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    parsed = LlmClassificationOutput(
        topics=[
            TopicContribution(
                topic_slug="zero-trust",
                topic_title="Zero Trust",
                related_topics=["ai-engineering", "context-engineering"],
            ),
        ],
    )
    out = sanitize_topics_related_topics(parsed, {"ai-engineering"}, wiki)
    assert out.topics[0].related_topics == ["context-engineering"]
