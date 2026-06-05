"""Tests for atomic evidence items."""

from __future__ import annotations

from src.wiki_render.evidence import evidence_set_hash, make_evidence_item, stance_for_field


def test_evidence_id_and_set_hash_are_stable() -> None:
    """Equivalent evidence produces equivalent ids and set hashes."""
    item = make_evidence_item(
        text="Open-weight models are improving.",
        source_id="source-a",
        source_title="Source A",
        source_date="2026-01-01",
        published_date="2026-01-01",
        assessed_as_of="2026-01-02",
        ingested_at="2026-01-03T00:00:00+00:00",
        category="trend",
        entity_slug="open-model-pressure",
        confidence=0.9,
        value_level="high",
        provenance="stated",
        evidence_type="expert_opinion",
        field="evidence_from_source",
    )
    same = make_evidence_item(
        text="Open-weight models are improving.",
        source_id="source-a",
        source_title="Source A",
        source_date="2026-01-01",
        published_date="2026-01-01",
        assessed_as_of="2026-01-02",
        ingested_at="2026-01-03T00:00:00+00:00",
        category="trend",
        entity_slug="open-model-pressure",
        confidence=0.9,
        value_level="high",
        provenance="stated",
        evidence_type="expert_opinion",
        field="evidence_from_source",
    )

    assert item is not None
    assert same is not None
    assert item.evidence_id == same.evidence_id
    assert item.stance == "supporting"
    assert evidence_set_hash([item]) == evidence_set_hash([same])


def test_stance_assignment_from_fields() -> None:
    """Fields deterministically map to synthesis stances."""
    assert stance_for_field("uncertainty_note") == "uncertainty"
    assert stance_for_field("contrarian_or_speculative_claims[0]") == "counter"
    assert stance_for_field("supporting_data_points[0]") == "supporting"
    assert stance_for_field("summary") == "neutral"
