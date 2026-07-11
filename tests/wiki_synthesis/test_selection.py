"""Tests for Stage 2 synthesis candidate selection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.wiki_synthesis.models import PlanEntry
from src.wiki_synthesis.selection import (
    format_workflow_commands,
    score_candidate,
    select_synthesis_candidates,
)


def test_selection_ranks_role_relevant_topic_above_model(tmp_path: Path) -> None:
    """Role-relevant topics should rank above lower-priority model pages."""
    graph = _graph_with_candidates(
        [
            _page(
                entity_id="model:gpt-5",
                category="model",
                slug="gpt-5",
                title="GPT-5",
                tags=["ai-engineering"],
            ),
            _page(
                entity_id="topic:service-chatbot-governance",
                category="topic",
                slug="service-chatbot-governance",
                title="Service Chatbot Governance",
                tags=["chatbot", "governance"],
            ),
        ]
    )

    result = select_synthesis_candidates(graph, cache_dir=tmp_path / "cache", limit=2)

    assert result.total_changed == 2
    assert result.entries[0].entity_id == "topic:service-chatbot-governance"
    assert result.entries[0].score > result.entries[1].score
    assert "role_relevant" in result.entries[0].notes


def test_selection_is_deterministic_for_equal_scores(tmp_path: Path) -> None:
    """Equal scores should tie-break deterministically by entity id."""
    graph = _graph_with_candidates(
        [
            _page(
                entity_id="topic:zebra-topic",
                category="topic",
                slug="zebra-topic",
                title="Zebra Topic",
            ),
            _page(
                entity_id="topic:alpha-topic",
                category="topic",
                slug="alpha-topic",
                title="Alpha Topic",
            ),
        ]
    )

    result = select_synthesis_candidates(graph, cache_dir=tmp_path / "cache", limit=2)

    assert [entry.entity_id for entry in result.entries] == [
        "topic:alpha-topic",
        "topic:zebra-topic",
    ]


def test_selection_respects_category_filter(tmp_path: Path) -> None:
    """Category filters should limit changed candidates."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="glossary:two", category="glossary", slug="two", title="Two"),
        ]
    )

    result = select_synthesis_candidates(
        graph,
        cache_dir=tmp_path / "cache",
        category="glossary",
        limit=10,
    )

    assert result.total_changed == 1
    assert result.entries[0].entity_id == "glossary:two"


def test_selection_respects_entity_filter(tmp_path: Path) -> None:
    """Entity filters should return only the requested entity when eligible."""
    graph = _graph_with_candidates(
        [
            _page(entity_id="topic:one", category="topic", slug="one", title="One"),
            _page(entity_id="topic:two", category="topic", slug="two", title="Two"),
        ]
    )

    result = select_synthesis_candidates(
        graph,
        cache_dir=tmp_path / "cache",
        entity="topic:two",
        limit=10,
    )

    assert result.total_changed == 1
    assert result.entries[0].entity_id == "topic:two"


def test_selection_marks_possible_duplicates_without_excluding(tmp_path: Path) -> None:
    """Possible duplicates should remain visible with a note and lower score."""
    graph = _graph_with_candidates(
        [
            _page(
                entity_id="topic:cross-source-knowledge-compilation",
                category="topic",
                slug="cross-source-knowledge-compilation",
                title="Cross Source Knowledge Compilation",
            ),
            _page(
                entity_id="topic:multi-source-knowledge-compilation",
                category="topic",
                slug="multi-source-knowledge-compilation",
                title="Multi Source Knowledge Compilation",
            ),
        ]
    )

    result = select_synthesis_candidates(graph, cache_dir=tmp_path / "cache", limit=2)

    assert result.shown == 2
    assert all("possible_duplicate" in entry.notes for entry in result.entries)


def test_score_candidate_applies_model_penalty() -> None:
    """Model pages should receive the configured category penalty."""
    entry = PlanEntry(
        entity_id="model:gpt-5",
        category="model",
        slug="gpt-5",
        title="GPT-5",
        path="foundation-models/gpt-5.md",
        state="new",
        reason="no synthesis cache entry exists",
        source_count=2,
        evidence_count=5,
        current_input_hash="hash-a",
        cached_input_hash="",
    )
    topic_entry = PlanEntry(
        entity_id="topic:plain-topic",
        category="topic",
        slug="plain-topic",
        title="Plain Topic",
        path="topics/plain-topic.md",
        state="new",
        reason="no synthesis cache entry exists",
        source_count=2,
        evidence_count=5,
        current_input_hash="hash-b",
        cached_input_hash="",
    )
    graph = _graph_with_candidates(
        [
            _page(entity_id="model:gpt-5", category="model", slug="gpt-5", title="GPT-5"),
            _page(
                entity_id="topic:plain-topic",
                category="topic",
                slug="plain-topic",
                title="Plain Topic",
            ),
        ]
    )

    model_score, _ = score_candidate(graph, entry)
    topic_score, _ = score_candidate(graph, topic_entry)

    assert topic_score > model_score


def test_format_workflow_commands() -> None:
    """Command output should include entity-specific workflow invocations."""
    from src.wiki_synthesis.selection import SelectedEntry

    commands = format_workflow_commands(
        [
            SelectedEntry(
                rank=1,
                score=90,
                entity_id="topic:example",
                category="topic",
                slug="example",
                title="Example",
                source_count=2,
                evidence_count=3,
                state="new",
                notes=["topic"],
            )
        ]
    )

    assert commands == "hatch run wiki-synthesis-workflow --entity topic:example --yes"


def _graph_with_candidates(pages: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a graph export with executable multi-source pages."""
    return {
        "sources": [
            {"source_id": "source-a", "title": "Source A"},
            {"source_id": "source-b", "title": "Source B"},
        ],
        "knowledge_pages": [
            {
                **page,
                "path": page.get("path", f"{page['category']}s/{page['slug']}.md"),
                "aliases": [],
                "tags": page.get("tags", []),
                "types": [],
                "source_ids": ["source-a", "source-b"],
                "source_count": 2,
                "evidence_count": page.get("evidence_count", 3),
                "value_level": "high",
                "confidence": 0.9,
                "evidence": page.get(
                    "evidence",
                    [
                        {
                            "evidence_id": f"evidence-{page['slug']}",
                            "text": "Example evidence.",
                            "source_id": "source-a",
                            "field": "knowledge_summary",
                            "stance": "supporting",
                        }
                    ],
                ),
            }
            for page in pages
        ],
    }


def _page(
    *,
    entity_id: str,
    category: str,
    slug: str,
    title: str,
    tags: list[str] | None = None,
    evidence: list[dict[str, Any]] | None = None,
    evidence_count: int = 3,
) -> dict[str, Any]:
    """Return one knowledge page payload."""
    return {
        "entity_id": entity_id,
        "category": category,
        "slug": slug,
        "title": title,
        "tags": tags or [],
        "evidence": evidence,
        "evidence_count": evidence_count,
    }
