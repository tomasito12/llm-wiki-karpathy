"""Dashboard handler for reviewer-forced single-entity extraction."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.ingest_review.artifact import save_artifact, touch_review_session
from src.ingest_review.domain_tag_ui import seed_review_tags_on_artifact
from src.ingest_review.extract import SourceDocument
from src.ingest_review.proposal_regen import REGEN_SPECS, append_forced_proposal
from src.ingest_review.proposal_regen_context import build_regen_context_sections
from src.ingest_review.proposal_regen_provider import regen_payload_for_apply
from src.ingest_review.proposal_regen_ui import preserve_review_entity_tab_for_regen
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

FORCE_EXTRACT_OUTPUT_MODELS: dict[str, type[BaseModel]] = {
    "topic": TopicRegenerateOutput,
    "glossary": GlossaryRegenerateOutput,
    "how_to": HowToRegenerateOutput,
    "trend": TrendRegenerateOutput,
    "tool": ToolRegenerateOutput,
    "model": ModelRegenerateOutput,
    "impl_study": ImplStudyRegenerateOutput,
}

FORCE_EXTRACT_TAG_ALLOWLISTS: dict[str, str] = {
    "topic": "topics",
    "glossary": "glossary",
    "how_to": "how_to",
    "trend": "industry_trends",
    "tool": "tools",
    "model": "foundation_models",
    "impl_study": "implementation_studies",
}


def process_pending_forced_extract(
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
    tool_tags: list[str],
    model_tags: list[str],
    reviews_root: Path | None = None,
) -> bool:
    """Run queued forced extraction. Returns True when a rerun was triggered."""
    if not isinstance(pending_raw, dict):
        return False
    if pending_raw.get("source_id") != source_id:
        return False
    entity_key = str(pending_raw.get("entity") or "")
    title = str(pending_raw.get("title") or "").strip()
    note = str(pending_raw.get("note") or "").strip()
    if not title:
        st.error("Enter a **title or term** before forcing extraction.")
        return False
    spec = REGEN_SPECS.get(entity_key)
    output_model = FORCE_EXTRACT_OUTPUT_MODELS.get(entity_key)
    if not spec or not output_model:
        st.error(f"Forced extraction is not supported for: {entity_key}")
        return False
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set — cannot force extraction.")
        return False

    wiki_snap = build_wiki_snapshot(wiki_root)
    context = build_regen_context_sections(
        entity_key,
        artifact=artifact,
        wiki=wiki_snap,
        topic_tags_allowlist=topic_tags,
        trend_tags_allowlist=trend_tags,
        howto_tags_allowlist=howto_tags,
        glossary_tags_allowlist=glossary_tags,
        model_types_allowlist=model_types,
        tool_types_allowlist=tool_types,
        impl_study_tags_allowlist=impl_study_tags,
        reviews_root=reviews_root,
    )
    label = spec.entity_label or entity_key
    try:
        provider = OpenAIIngestionProvider()
        with st.spinner(f"Forcing {label.lower()} extraction for **{title}**…"):
            regen_dict, regen_meta = provider.regenerate_proposal(
                entity_key=entity_key,
                document=document,
                current_item={},
                new_title=title,
                reviewer_instruction=note or None,
                context_sections=context,
                model=model,
                prompt_version=prompt_version,
                max_plain_text_chars=max_plain_text_chars,
            )
        regenerated = output_model.model_validate(regen_dict)
        regen_payload = regen_payload_for_apply(regenerated.model_dump(mode="json"))
        pv = str(regen_meta.get("prompt_version") or prompt_version)
        append_forced_proposal(
            artifact,
            spec,
            new_title=title,
            regenerated=regen_payload,
            model=model,
            prompt_version=pv,
        )
        review_key = FORCE_EXTRACT_TAG_ALLOWLISTS.get(entity_key, "")
        allow_map = {
            "glossary": set(glossary_tags),
            "topics": set(topic_tags),
            "how_to": set(howto_tags),
            "industry_trends": set(trend_tags),
            "tools": set(tool_tags),
            "foundation_models": set(model_tags),
            "implementation_studies": set(impl_study_tags),
        }
        if review_key and review_key in allow_map:
            seed_review_tags_on_artifact(
                artifact,
                allowlists_by_review_key={review_key: allow_map[review_key]},
            )
        touch_review_session(artifact)
        save_artifact(artifact_path, artifact)
        st.session_state["artifact"] = artifact
        st.session_state["_proposal_regen_msg"] = {
            "entity": entity_key,
            "text": f"Forced {label.lower()} **{title}** — review it in the {label} tab.",
        }
        preserve_review_entity_tab_for_regen(entity_key)
        st.rerun()
        return True
    except Exception as exc:  # noqa: BLE001
        from src.ingest_review.artifact import attach_error

        attach_error(artifact, f"force extract {entity_key}: {exc}")
        st.session_state["artifact"] = artifact
        st.error(f"Forced {label.lower()} extraction failed: {exc}")
        return False
