"""Data models for Stage 2 synthesis planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PlanEntry:
    """One Stage 2 planning decision for a generated page."""

    entity_id: str
    category: str
    slug: str
    title: str
    path: str
    state: str
    reason: str
    source_count: int
    evidence_count: int
    current_input_hash: str
    cached_input_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class PlanSummary:
    """Summary counts for a Stage 2 synthesis plan."""

    total: int
    shown: int
    unchanged: int
    new: int
    stale: int
    skipped_single_source: int
    skipped_evidence_object: int
    skipped_in_progress_source: int
    error: int

    def to_dict(self) -> dict[str, int]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class SynthesisPlan:
    """A Stage 2 plan and its summary."""

    entries: list[PlanEntry]
    summary: PlanSummary

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "summary": self.summary.to_dict(),
            "entries": [entry.to_dict() for entry in self.entries],
        }
