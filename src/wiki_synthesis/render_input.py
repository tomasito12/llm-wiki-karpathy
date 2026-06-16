"""Bridge in-memory render pages to Stage 2 synthesis input hashes."""

from __future__ import annotations

from typing import Any

from src.wiki_render.models import KnowledgePage
from src.wiki_synthesis.input_hash import synthesis_input_hash


def page_payload_from_knowledge_page(page: KnowledgePage) -> dict[str, Any]:
    """Return the graph-export-compatible payload for one knowledge page."""
    return {
        "entity_id": page.entity_id,
        "category": page.category,
        "slug": page.slug,
        "title": page.title,
        "path": page.path,
        "aliases": page.aliases,
        "tags": page.tags,
        "types": page.types,
        "first_seen": page.first_seen,
        "last_seen": page.last_seen,
        "source_count": page.source_count,
        "source_ids": page.source_ids,
        "evidence_count": page.evidence_count,
        "supporting_count": page.stance_counts.get("supporting", 0),
        "counter_count": page.stance_counts.get("counter", 0),
        "uncertainty_count": page.stance_counts.get("uncertainty", 0),
        "neutral_count": page.stance_counts.get("neutral", 0),
        "value_level": page.value_level,
        "confidence": page.confidence,
        "synthesis_state": page.synthesis_state,
        "evidence_set_hash": page.evidence_set_hash,
        "evidence": [item.to_dict() for item in page.evidence],
        "duplicate_candidates": page.duplicate_candidates,
    }


def synthesis_input_hash_for_knowledge_page(page: KnowledgePage) -> str:
    """Return the Stage 2 input hash for one in-memory knowledge page."""
    return synthesis_input_hash(page_payload_from_knowledge_page(page))
