"""Tests for canonical title collection and alignment."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_review.canonical_titles import (
    ENTITY_CANONICAL_CONFIGS,
    CanonicalTitleEntry,
    align_title_on_proposal,
    build_canonical_index,
    collect_approved_titles_from_reviews,
    effective_title_from_node,
    find_canonical_match,
    format_canonical_block,
    merge_canonical_entries,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_effective_title_from_node_prefers_final_text() -> None:
    node = {
        "llm_item": {"topic_title": "Draft Title"},
        "sections": {"topic_title": {"final_text": "Canonical Title", "status": "modified"}},
    }
    assert effective_title_from_node(node, "topic_title") == "Canonical Title"


def test_collect_approved_titles_skips_rejected(tmp_path: Path) -> None:
    reviews = tmp_path / "reviews"
    src = reviews / "article-a"
    src.mkdir(parents=True)
    (src / "review.json").write_text(
        json.dumps(
            {
                "review": {
                    "topics": [
                        {
                            "proposal_status": "approved",
                            "llm_item": {
                                "topic_title": "Harness Decay",
                                "topic_slug": "harness-decay",
                            },
                        },
                        {
                            "proposal_status": "rejected",
                            "llm_item": {
                                "topic_title": "Rejected Topic",
                                "topic_slug": "rejected-topic",
                            },
                        },
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    cfg = ENTITY_CANONICAL_CONFIGS["topic"]
    titles = collect_approved_titles_from_reviews(reviews, cfg)
    assert len(titles) == 1
    assert titles[0].title == "Harness Decay"
    assert titles[0].slug == "harness-decay"


def test_merge_canonical_entries_preserves_first_spelling() -> None:
    merged = merge_canonical_entries(
        [CanonicalTitleEntry(title="Harness Decay", slug="harness-decay")],
        [CanonicalTitleEntry(title="harness decay", slug="harness-decay-2")],
    )
    assert len(merged) == 1
    assert merged[0].title == "Harness Decay"


def test_find_canonical_match_fuzzy() -> None:
    entries = [CanonicalTitleEntry(title="Harness Decay", slug="harness-decay")]
    match = find_canonical_match("Harness decay", entries)
    assert match is not None
    assert match.title == "Harness Decay"


def test_align_title_on_proposal_overwrites_near_match() -> None:
    entries = [CanonicalTitleEntry(title="Harness Decay", slug="harness-decay")]
    out = align_title_on_proposal(
        {"topic_title": "harness decay", "topic_slug": "wrong-slug"},
        title_field="topic_title",
        slug_field="topic_slug",
        entries=entries,
    )
    assert out["topic_title"] == "Harness Decay"
    assert out["topic_slug"] == "harness-decay"


def test_format_canonical_block_empty() -> None:
    assert "none" in format_canonical_block([]).lower()


def test_build_canonical_index_merges_wiki_and_reviews(tmp_path: Path) -> None:
    wiki = WikiSnapshot(
        glossary_terms=["Frontmatter"],
        tool_names=[],
        foundation_model_names=[],
        topic_titles=["Wiki Topic"],
        topic_slugs=["wiki-topic"],
    )
    reviews = tmp_path / "reviews"
    src = reviews / "src-1"
    src.mkdir(parents=True)
    (src / "review.json").write_text(
        json.dumps(
            {
                "review": {
                    "topics": [
                        {
                            "proposal_status": "approved",
                            "llm_item": {
                                "topic_title": "Review Topic",
                                "topic_slug": "review-topic",
                            },
                        },
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    index = build_canonical_index(wiki, reviews)
    titles = {e.title for e in index["topic"]}
    assert "Wiki Topic" in titles
    assert "Review Topic" in titles
