"""Tests for Stage 2 synthesis input hashing."""

from __future__ import annotations

from src.wiki_synthesis.input_hash import synthesis_input_hash


def test_synthesis_input_hash_is_stable_for_evidence_order() -> None:
    """Evidence ordering should not change the synthesis input hash."""
    page = _page(
        evidence=[
            {"evidence_id": "b", "text": "Second claim", "source_id": "source-b"},
            {"evidence_id": "a", "text": "First claim", "source_id": "source-a"},
        ]
    )
    reordered = _page(
        evidence=[
            {"evidence_id": "a", "text": "First claim", "source_id": "source-a"},
            {"evidence_id": "b", "text": "Second claim", "source_id": "source-b"},
        ]
    )

    assert synthesis_input_hash(page) == synthesis_input_hash(reordered)


def test_synthesis_input_hash_changes_when_evidence_text_changes() -> None:
    """Changing semantic evidence text should invalidate the synthesis hash."""
    original = _page(evidence=[{"evidence_id": "a", "text": "First claim"}])
    changed = _page(evidence=[{"evidence_id": "a", "text": "Changed claim"}])

    assert synthesis_input_hash(original) != synthesis_input_hash(changed)


def test_synthesis_input_hash_ignores_float_representation_noise() -> None:
    """Tiny float representation differences should not force resynthesis."""
    original = _page(evidence=[{"evidence_id": "a", "text": "First claim"}])
    changed = _page(evidence=[{"evidence_id": "a", "text": "First claim"}])
    original["confidence"] = 0.927857142857143
    changed["confidence"] = 0.9278571428571428

    assert synthesis_input_hash(original) == synthesis_input_hash(changed)


def _page(*, evidence: list[dict[str, object]]) -> dict[str, object]:
    """Return a minimal graph-export page."""
    return {
        "entity_id": "topic:agentic-coding-workflows",
        "category": "topic",
        "slug": "agentic-coding-workflows",
        "title": "Agentic Coding Workflows",
        "aliases": [],
        "tags": ["coding-agents"],
        "types": [],
        "source_ids": ["source-a", "source-b"],
        "source_count": 2,
        "evidence_count": len(evidence),
        "value_level": "high",
        "confidence": 0.9,
        "supporting_count": 1,
        "counter_count": 0,
        "uncertainty_count": 0,
        "neutral_count": 0,
        "evidence": evidence,
    }
