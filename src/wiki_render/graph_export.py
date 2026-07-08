"""Machine-readable graph export for Stage 2 synthesis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest_review.schema import ARTIFACT_SCHEMA_VERSION
from src.pipeline.atomic import atomic_write_json
from src.wiki_render import TOOL_VERSION
from src.wiki_render.models import IndividualPage, KnowledgeGraph, KnowledgePage, SourceRecord


def graph_export_payload(graph: KnowledgeGraph) -> dict[str, Any]:
    """Return deterministic JSON payload for the in-memory graph."""
    return {
        "tool_version": TOOL_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "taxonomy_version": graph.taxonomy_version,
        "sources": [_source_payload(source) for source in graph.sources],
        "knowledge_pages": [_page_payload(page) for page in graph.knowledge_pages],
        "signals": [_individual_payload(item) for item in graph.signals],
        "interview_insights": [_individual_payload(item) for item in graph.insights],
        "implementation_studies": [
            _individual_payload(item) for item in graph.implementation_studies
        ],
        "alias_map": graph.alias_map,
    }


def write_graph_export(path: Path, graph: KnowledgeGraph, *, dry_run: bool = False) -> None:
    """Write the graph export unless ``dry_run`` is set."""
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(path, graph_export_payload(graph))


def _source_payload(source: SourceRecord) -> dict[str, Any]:
    """Return source JSON payload."""
    return {
        "source_id": source.source_id,
        "title": source.title,
        "published_date": source.published_date,
        "assessed_as_of": source.assessed_as_of,
        "ingested_at": source.ingested_at,
        "tags": sorted(source.source_tags),
        "derived_paths": {
            key: sorted(values) for key, values in sorted(source.derived_paths.items())
        },
        "derived_pages": sorted(
            {path for paths in source.derived_paths.values() for path in paths}
        ),
    }


def _page_payload(page: KnowledgePage) -> dict[str, Any]:
    """Return knowledge-page JSON payload."""
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
        "values": page.values,
        "evidence_set_hash": page.evidence_set_hash,
        "evidence": [item.to_dict() for item in page.evidence],
        "duplicate_candidates": page.duplicate_candidates,
    }


def _individual_payload(item: IndividualPage) -> dict[str, Any]:
    """Return individual signal/insight JSON payload."""
    return {
        "category": item.category,
        "slug": item.slug,
        "title": item.title,
        "path": item.path,
        "source_id": item.source_id,
        "source_date": item.source_date,
        "month": item.month,
        "tags": item.tags,
        "values": item.values,
        "evidence_count": item.evidence_count,
        "evidence_set_hash": item.evidence_set_hash,
        "evidence": [entry.to_dict() for entry in item.evidence],
    }
