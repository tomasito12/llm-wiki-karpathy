"""Move a review proposal from one entity section to another via LLM regeneration."""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any

from src.ingest_review.domain_tag_ui import find_review_node
from src.ingest_review.proposal_regen import (
    REGEN_SPECS,
    ProposalRegenSpec,
    _fresh_sections,
    _review_index,
)
from src.pipeline.slug import slugify


def _utc_now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


# (target entity_key, human label) — shown in the reclassify UI per source entity.
TRANSFER_TARGET_OPTIONS: dict[str, list[tuple[str, str]]] = {
    "trend": [
        ("topic", "Topic"),
        ("glossary", "Glossary term"),
        ("how_to", "How-to"),
    ],
    "topic": [
        ("trend", "Trend"),
        ("glossary", "Glossary term"),
        ("how_to", "How-to"),
    ],
    "glossary": [
        ("topic", "Topic"),
        ("trend", "Trend"),
        ("how_to", "How-to"),
    ],
    "how_to": [
        ("topic", "Topic"),
        ("glossary", "Glossary term"),
        ("trend", "Trend"),
    ],
    "impl_study": [
        ("topic", "Topic"),
        ("trend", "Trend"),
    ],
}


def transfer_target_label(source_entity_key: str, target_entity_key: str) -> str:
    """Return the display label for *target_entity_key* from *source_entity_key* options."""
    for key, label in TRANSFER_TARGET_OPTIONS.get(source_entity_key, []):
        if key == target_entity_key:
            return label
    return target_entity_key.replace("_", " ").title()


def _build_llm_item(
    spec: ProposalRegenSpec,
    *,
    title: str,
    regenerated: dict[str, Any],
) -> dict[str, Any]:
    llm_item: dict[str, Any] = {spec.title_field: title}
    if spec.slug_field:
        llm_item[spec.slug_field] = slugify(title)
    for key in spec.content_merge_keys:
        if key in regenerated:
            llm_item[key] = regenerated[key]
    for sk in spec.scalar_keys:
        if sk not in llm_item:
            llm_item[sk] = ""
    for lk in spec.list_keys:
        if lk not in llm_item:
            llm_item[lk] = []
    return llm_item


def transfer_proposal_to_entity(
    artifact: dict[str, Any],
    proposal_id: str,
    source_spec: ProposalRegenSpec,
    target_spec: ProposalRegenSpec,
    *,
    new_title: str,
    regenerated: dict[str, Any],
    model: str,
    prompt_version: str,
) -> str:
    """Remove proposal from *source_spec* list and append under *target_spec*.

    Returns the ``proposal_id`` on the new review node (preserved when possible).
    """
    title = new_title.strip()
    if not title:
        raise ValueError("new_title must be non-empty")
    if target_spec.normalize_title:
        title = target_spec.normalize_title(title)

    source_node = find_review_node(artifact, proposal_id, source_spec.review_list_key)
    if not source_node:
        raise ValueError(f"Unknown {source_spec.entity_key} proposal_id: {proposal_id}")

    source_idx = _review_index(artifact, proposal_id, source_spec.review_list_key)
    if source_idx is None:
        raise ValueError(f"Review index missing for {proposal_id}")

    preserved_id = str(source_node.get("proposal_id") or proposal_id)
    proposal_status = str(source_node.get("proposal_status") or "pending")
    notes = source_node.get("notes")

    llm_item = _build_llm_item(target_spec, title=title, regenerated=regenerated)
    new_node: dict[str, Any] = {
        "proposal_id": preserved_id,
        "proposal_status": proposal_status,
        "notes": notes,
        "llm_item": llm_item,
        "sections": _fresh_sections(
            llm_item,
            target_spec.reviewable_scalar_keys,
            target_spec.reviewable_list_keys,
        ),
        "tags": {
            "final_tags": [],
            "approved_new_tags": [],
        },
    }

    prev_meta = source_node.get("proposal_regeneration_meta")
    regen_count = 0
    if isinstance(prev_meta, dict):
        regen_count = int(prev_meta.get("regen_count") or 0)
    new_node["proposal_regeneration_meta"] = {
        "regen_count": regen_count + 1,
        "last_regen_at": _utc_now_iso(),
        "model": model,
        "prompt_version": prompt_version,
        "transferred_from": {
            "entity": source_spec.entity_key,
            "review_list_key": source_spec.review_list_key,
            "title_field": source_spec.title_field,
            "at": _utc_now_iso(),
        },
    }

    review = artifact.setdefault("review", {})
    source_list = review.setdefault(source_spec.review_list_key, [])
    if not isinstance(source_list, list):
        raise ValueError(f"Invalid review.{source_spec.review_list_key}")
    source_list.pop(source_idx)

    target_list = review.setdefault(target_spec.review_list_key, [])
    if not isinstance(target_list, list):
        target_list = []
        review[target_spec.review_list_key] = target_list
    target_list.append(new_node)

    llm_out = artifact.setdefault("llm_output", {})
    source_llm = llm_out.setdefault(source_spec.llm_output_key, [])
    if isinstance(source_llm, list) and source_idx < len(source_llm):
        source_llm.pop(source_idx)

    target_llm = llm_out.setdefault(target_spec.llm_output_key, [])
    if not isinstance(target_llm, list):
        target_llm = []
        llm_out[target_spec.llm_output_key] = target_llm
    target_llm.append(copy.deepcopy(llm_item))

    return preserved_id


def resolve_transfer_specs(
    source_entity_key: str,
    target_entity_key: str,
) -> tuple[ProposalRegenSpec, ProposalRegenSpec]:
    """Return (source_spec, target_spec) or raise ``ValueError``."""
    if source_entity_key == target_entity_key:
        raise ValueError("source and target entity must differ")
    allowed = {k for k, _ in TRANSFER_TARGET_OPTIONS.get(source_entity_key, [])}
    if target_entity_key not in allowed:
        raise ValueError(f"Cannot transfer from {source_entity_key!r} to {target_entity_key!r}")
    source_spec = REGEN_SPECS.get(source_entity_key)
    target_spec = REGEN_SPECS.get(target_entity_key)
    if not source_spec or not target_spec:
        raise ValueError("Unknown entity for transfer")
    return source_spec, target_spec
