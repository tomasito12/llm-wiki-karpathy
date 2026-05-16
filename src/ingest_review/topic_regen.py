"""Merge per-topic LLM regeneration into review artifacts (wrapper)."""

from __future__ import annotations

from typing import Any

from src.ingest_review.proposal_regen import REGEN_SPECS, apply_regenerated_proposal
from src.ingest_review.schema import TopicRegenerateOutput


def apply_regenerated_topic_proposal(
    artifact: dict[str, Any],
    proposal_id: str,
    *,
    new_title: str,
    regenerated: TopicRegenerateOutput,
    model: str,
    prompt_version: str,
) -> None:
    """Merge regenerated topic content under *new_title* into review + llm_output."""
    apply_regenerated_proposal(
        artifact,
        proposal_id,
        REGEN_SPECS["topic"],
        new_title=new_title,
        regenerated=regenerated.model_dump(mode="json"),
        model=model,
        prompt_version=prompt_version,
    )
