"""Dashboard handler for queued per-proposal title regeneration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.ingest_review.artifact import save_artifact, touch_review_session
from src.ingest_review.domain_tag_ui import find_review_node
from src.ingest_review.extract import SourceDocument
from src.ingest_review.proposal_regen import REGEN_SPECS, apply_regenerated_proposal
from src.ingest_review.proposal_regen_context import build_regen_context_sections
from src.ingest_review.proposal_transfer import (
    resolve_transfer_specs,
    transfer_proposal_to_entity,
    transfer_target_label,
)
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.schema import (
    GlossaryRegenerateOutput,
    HowToRegenerateOutput,
    ImplStudyRegenerateOutput,
    ModelRegenerateOutput,
    ToolRegenerateOutput,
    TopicRegenerateOutput,
    TrendRegenerateOutput,
)
from src.ingest_review.wiki_snapshot import build_wiki_snapshot

REGEN_OUTPUT_MODELS: dict[str, type[BaseModel]] = {
    "topic": TopicRegenerateOutput,
    "glossary": GlossaryRegenerateOutput,
    "how_to": HowToRegenerateOutput,
    "trend": TrendRegenerateOutput,
    "tool": ToolRegenerateOutput,
    "model": ModelRegenerateOutput,
    "impl_study": ImplStudyRegenerateOutput,
}


def _migrate_legacy_topic_pending(pending: Any) -> dict[str, Any] | None:
    if not isinstance(pending, dict):
        return None
    if pending.get("entity"):
        return pending
    if pending.get("proposal_id") and pending.get("source_id"):
        return {
            "entity": "topic",
            "source_id": pending["source_id"],
            "proposal_id": pending["proposal_id"],
            "new_title": pending.get("new_title", ""),
            "note": pending.get("note", ""),
        }
    return None


def process_pending_proposal_regen(
    st: Any,
    *,
    pending_raw: Any,
    source_id: str,
    artifact: dict[str, Any],
    artifact_path: Path,
    document: SourceDocument,
    wiki_root: Path,
    model: str,
    prompt_version: str,
    max_plain_text_chars: int,
    topic_tags: list[str],
    trend_tags: list[str],
    howto_tags: list[str],
    glossary_tags: list[str],
    model_types: list[str],
    tool_types: list[str],
    impl_study_tags: list[str],
) -> bool:
    """Run queued regeneration if valid. Returns True when a rerun was triggered."""
    pending = _migrate_legacy_topic_pending(pending_raw)
    if not pending or pending.get("source_id") != source_id:
        return False
    source_entity_key = str(pending.get("entity") or "")
    target_entity_key = str(pending.get("target_entity") or source_entity_key)
    proposal_id = pending.get("proposal_id")
    if not isinstance(proposal_id, str) or not proposal_id:
        return False

    is_transfer = target_entity_key != source_entity_key
    regen_entity_key = target_entity_key if is_transfer else source_entity_key

    spec = REGEN_SPECS.get(regen_entity_key)
    output_model = REGEN_OUTPUT_MODELS.get(regen_entity_key)
    if not spec or not output_model:
        st.error(f"Unknown regeneration entity: {regen_entity_key}")
        return False

    source_spec = REGEN_SPECS.get(source_entity_key)
    if not source_spec:
        st.error(f"Unknown source entity: {source_entity_key}")
        return False

    new_title = str(pending.get("new_title") or "").strip()
    note = str(pending.get("note") or "").strip()
    if not new_title:
        title_hint = spec.title_field.replace("_", " ").title()
        st.error(f"Enter a **{title_hint}** before regenerating.")
        return False
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set — cannot regenerate.")
        return False

    node = find_review_node(artifact, proposal_id, source_spec.review_list_key)
    if not node:
        st.error(f"{source_spec.entity_label} proposal not found.")
        return False

    if is_transfer:
        try:
            resolve_transfer_specs(source_entity_key, target_entity_key)
        except ValueError as exc:
            st.error(str(exc))
            return False

    current_item = node.get("llm_item") or {}
    wiki_snap = build_wiki_snapshot(wiki_root)
    context = build_regen_context_sections(
        regen_entity_key,
        artifact=artifact,
        wiki=wiki_snap,
        topic_tags_allowlist=topic_tags,
        trend_tags_allowlist=trend_tags,
        howto_tags_allowlist=howto_tags,
        glossary_tags_allowlist=glossary_tags,
        model_types_allowlist=model_types,
        tool_types_allowlist=tool_types,
        impl_study_tags_allowlist=impl_study_tags,
    )

    try:
        provider = OpenAIIngestionProvider()
        label = spec.entity_label or regen_entity_key
        if is_transfer:
            src_label = source_spec.entity_label or source_entity_key
            tgt_display = transfer_target_label(source_entity_key, target_entity_key)
            spinner = f"Moving **{new_title}** from {src_label} to {tgt_display}…"
        else:
            spinner = f"Regenerating {label.lower()} as **{new_title}**…"
        with st.spinner(spinner):
            regen_dict, regen_meta = provider.regenerate_proposal(
                entity_key=regen_entity_key,
                document=document,
                current_item=current_item,
                new_title=new_title,
                reviewer_instruction=note or None,
                context_sections=context,
                model=model,
                prompt_version=prompt_version,
                max_plain_text_chars=max_plain_text_chars,
                source_entity_key=source_entity_key if is_transfer else None,
            )
        regenerated = output_model.model_validate(regen_dict)
        regen_payload = regenerated.model_dump(mode="json")
        pv = str(regen_meta.get("prompt_version") or prompt_version)

        if is_transfer:
            src_spec, tgt_spec = resolve_transfer_specs(source_entity_key, target_entity_key)
            transfer_proposal_to_entity(
                artifact,
                proposal_id,
                src_spec,
                tgt_spec,
                new_title=new_title,
                regenerated=regen_payload,
                model=model,
                prompt_version=pv,
            )
            tgt_display = transfer_target_label(source_entity_key, target_entity_key)
            msg = (
                f"Moved **{new_title}** from {src_spec.entity_label} to "
                f"**{tgt_display}** — open that tab to review."
            )
            msg_entity = target_entity_key
        else:
            apply_regenerated_proposal(
                artifact,
                proposal_id,
                spec,
                new_title=new_title,
                regenerated=regen_payload,
                model=model,
                prompt_version=pv,
            )
            msg = f"Regenerated {label.lower()} as **{new_title}**."
            msg_entity = source_entity_key

        touch_review_session(artifact)
        save_artifact(artifact_path, artifact)
        st.session_state["artifact"] = artifact
        st.session_state["_proposal_regen_msg"] = {
            "entity": msg_entity,
            "text": msg,
        }
        st.rerun()
        return True
    except Exception as exc:  # noqa: BLE001
        from src.ingest_review.artifact import attach_error

        action = "transfer" if is_transfer else "regenerate"
        attach_error(artifact, f"{action} {source_entity_key} {proposal_id}: {exc}")
        st.session_state["artifact"] = artifact
        st.error(f"{source_spec.entity_label} {action} failed: {exc}")
        return False
