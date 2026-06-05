"""Atomic source-attributed evidence items."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

CONFIDENCE_LABELS: dict[str, float] = {
    "low": 0.33,
    "medium": 0.66,
    "high": 1.0,
}

STANCE_BY_FIELD_FRAGMENT: tuple[tuple[str, str], ...] = (
    ("contradiction", "counter"),
    ("counter", "counter"),
    ("contrarian", "counter"),
    ("uncertainty", "uncertainty"),
    ("limitation", "uncertainty"),
    ("weakness", "uncertainty"),
    ("caveat", "uncertainty"),
    ("time_sensitivity", "uncertainty"),
    ("supporting", "supporting"),
    ("evidence", "supporting"),
    ("key_points", "supporting"),
    ("data_points", "supporting"),
    ("benchmark", "supporting"),
    ("capabilities", "supporting"),
    ("lessons", "supporting"),
    ("snippets", "supporting"),
    ("snippet", "supporting"),
)


@dataclass(frozen=True)
class EvidenceItem:
    """One atomic claim or support item with explicit provenance."""

    evidence_id: str
    text: str
    source_id: str
    source_title: str
    source_date: str
    published_date: str
    assessed_as_of: str
    ingested_at: str
    category: str
    entity_slug: str
    confidence: float | None
    value_level: str
    provenance: str
    stance: str
    evidence_type: str
    field: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def normalize_confidence(raw: object) -> float | None:
    """Return a numeric confidence when available."""
    if isinstance(raw, int | float):
        value = float(raw)
        return max(0.0, min(1.0, value))
    text = str(raw or "").strip().lower()
    if text in CONFIDENCE_LABELS:
        return CONFIDENCE_LABELS[text]
    return None


def evidence_id_for(
    *,
    source_id: str,
    entity_slug: str,
    field: str,
    text: str,
) -> str:
    """Return a stable short evidence id."""
    payload = "|".join((source_id, entity_slug, field, text.strip()))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def stance_for_field(field: str) -> str:
    """Return deterministic stance inferred from the originating field name."""
    normalized = field.lower()
    for fragment, stance in STANCE_BY_FIELD_FRAGMENT:
        if fragment in normalized:
            return stance
    return "neutral"


def evidence_set_hash(evidence: list[EvidenceItem]) -> str:
    """Return a stable hash for a page evidence set."""
    parts = [
        f"{item.evidence_id}|{item.text}|{item.source_id}|{item.field}|{item.stance}"
        for item in sorted(evidence, key=lambda entry: entry.evidence_id)
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def make_evidence_item(
    *,
    text: str,
    source_id: str,
    source_title: str,
    source_date: str,
    published_date: str,
    assessed_as_of: str,
    ingested_at: str,
    category: str,
    entity_slug: str,
    confidence: object,
    value_level: str,
    provenance: str,
    evidence_type: str,
    field: str,
) -> EvidenceItem | None:
    """Build an evidence item, returning None for empty text."""
    clean = str(text or "").strip()
    if not clean:
        return None
    stance = stance_for_field(field)
    if provenance in {"contradiction"}:
        stance = "counter"
    elif provenance in {"limitation"} and stance == "neutral":
        stance = "uncertainty"
    return EvidenceItem(
        evidence_id=evidence_id_for(
            source_id=source_id,
            entity_slug=entity_slug,
            field=field,
            text=clean,
        ),
        text=clean,
        source_id=source_id,
        source_title=source_title,
        source_date=source_date,
        published_date=published_date,
        assessed_as_of=assessed_as_of,
        ingested_at=ingested_at,
        category=category,
        entity_slug=entity_slug,
        confidence=normalize_confidence(confidence),
        value_level=str(value_level or "medium"),
        provenance=provenance,
        stance=stance,
        evidence_type=str(evidence_type or "unknown"),
        field=field,
    )
