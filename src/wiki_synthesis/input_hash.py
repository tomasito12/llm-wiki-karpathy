"""Stable Stage 2 synthesis input hashing."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.wiki_synthesis import SYNTHESIS_PROMPT_VERSION, SYNTHESIS_SCHEMA_VERSION

HASH_FIELDS: tuple[str, ...] = (
    "entity_id",
    "category",
    "slug",
    "title",
    "aliases",
    "tags",
    "types",
    "source_ids",
    "source_count",
    "evidence_count",
    "value_level",
    "confidence",
)

EVIDENCE_HASH_FIELDS: tuple[str, ...] = (
    "evidence_id",
    "text",
    "source_id",
    "source_title",
    "source_date",
    "published_date",
    "assessed_as_of",
    "category",
    "entity_slug",
    "confidence",
    "value_level",
    "provenance",
    "stance",
    "evidence_type",
    "field",
)


def synthesis_input_payload(page: dict[str, Any]) -> dict[str, Any]:
    """Return the normalized semantic input payload for one knowledge page."""
    evidence = page.get("evidence", [])
    evidence_items = evidence if isinstance(evidence, list) else []
    return {
        "schema_version": SYNTHESIS_SCHEMA_VERSION,
        "prompt_version": SYNTHESIS_PROMPT_VERSION,
        "page": {field: _normalize(page.get(field)) for field in HASH_FIELDS},
        "stance_counts": {
            "supporting": _normalize(page.get("supporting_count", 0)),
            "counter": _normalize(page.get("counter_count", 0)),
            "uncertainty": _normalize(page.get("uncertainty_count", 0)),
            "neutral": _normalize(page.get("neutral_count", 0)),
        },
        "evidence": [
            {field: _normalize(item.get(field)) for field in EVIDENCE_HASH_FIELDS}
            for item in sorted(
                (entry for entry in evidence_items if isinstance(entry, dict)),
                key=lambda entry: str(entry.get("evidence_id", "")),
            )
        ],
    }


def synthesis_input_hash(page: dict[str, Any]) -> str:
    """Return a stable hash for the Stage 2 synthesis input."""
    payload = synthesis_input_payload(page)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _normalize(value: Any) -> Any:
    """Return a JSON-stable normalized value."""
    if isinstance(value, dict):
        return {str(key): _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple | set):
        return sorted(_normalize(item) for item in value)
    return value
