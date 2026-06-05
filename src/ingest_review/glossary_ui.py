"""Streamlit rendering for glossary proposals (two-column read/edit layout)."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    format_proposal_meta_subtitle,
    google_search_markdown,
)
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_tag_ui_to_node,
    effective_readonly_domain_tags,
    find_review_node,
    render_domain_tag_section,
)
from src.ingest_review.fast_review_ui import (
    CollapsedFieldSpec,
    read_fast_card_field_values,
    register_card_autosave,
    render_collapsed_fields,
    render_context_expander,
    render_fast_card_header,
    render_fast_card_reclassify,
    render_fast_card_save_row,
    render_inline_regenerate_title_controls,
    render_readonly_context_hint,
    render_source_evidence_expander,
)
from src.ingest_review.glossary_related_terms_align import (
    build_related_term_resolution_maps,
    related_term_matches_known_label,
)
from src.ingest_review.proposal_columns_ui import (
    build_proposal_expander_label,
    render_two_column_proposal_review,
)
from src.ingest_review.proposal_decision_ui import set_proposal_save_message
from src.ingest_review.proposal_regen_ui import (
    pop_proposal_regen_msg,
    proposal_edit_key_prefix,
    regen_count_from_node,
    render_proposal_regen_meta_caption,
)
from src.ingest_review.schema import (
    GLOSSARY_REVIEWABLE_SCALAR_KEYS,
    normalize_glossary_term_capitalization,
)
from src.ingest_review.tags import normalize_tag

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")

VALUE_LEVEL_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}

VALUE_LEVEL_BADGES: dict[str, str] = {
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

VALUE_LEVEL_TIER_HEADERS: dict[str, str] = {
    "high": "### High value",
    "medium": "### Medium value",
    "low": "### Low value",
}

SECTION_LABELS: dict[str, str] = {
    "term": "Term",
    "proposed_definition": "Proposed definition",
    "extended_explanation": "Extended explanation",
    "relevance_note": "Relevance note",
}


def _proposal_sort_key(node: dict[str, Any]) -> tuple[int, float]:
    """Sort key: value_level priority ascending, confidence descending."""
    llm_item = node.get("llm_item") or {}
    level = str(llm_item.get("value_level") or "medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    return (VALUE_LEVEL_ORDER.get(level, 1), -confidence)


def _value_level(node: dict[str, Any]) -> str:
    llm_item = node.get("llm_item") or {}
    return str(llm_item.get("value_level") or "medium")


def _section_node(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_glossary_scalar(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Return reviewer-final scalar text, else the LLM draft."""
    node = _section_node(sections, section_key)
    final = node.get("final_text")
    if isinstance(final, str) and final.strip():
        raw = final.strip()
    else:
        raw = str(llm_item.get(section_key) or "").strip()
    if section_key == "term" and raw:
        return normalize_glossary_term_capitalization(raw)
    return raw


def apply_glossary_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one glossary field edit; infer section status from LLM draft."""
    text = raw_text.strip()
    llm_text = str(llm_item.get(section_key) or "").strip()
    if section_key == "term":
        text = normalize_glossary_term_capitalization(text)
        llm_text = normalize_glossary_term_capitalization(llm_text)
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    if text == llm_text:
        node["status"] = "approved"
        node["final_text"] = None
        if section_key == "term":
            llm_item["term"] = text
    else:
        node["status"] = "modified"
        node["final_text"] = text


def apply_glossary_proposal_edits(
    node: dict[str, Any],
    field_values: dict[str, str],
) -> None:
    """Apply all editable scalar fields for one glossary proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in GLOSSARY_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_glossary_scalar_edit(sections, llm_item, sk, field_values[sk])


def glossary_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one glossary field."""
    return effective_glossary_scalar(llm_item, sections, section_key)


def format_glossary_term_readonly_markdown(
    node: dict[str, Any],
    glossary_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
    norm_to: dict[str, str] | None = None,
    acr_to: dict[str, str] | None = None,
) -> str:
    """Format one glossary proposal as markdown for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    term = effective_glossary_scalar(llm_item, sections, "term") or "Untitled"
    value_level = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(value_level, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}
    definition = effective_glossary_scalar(llm_item, sections, "proposed_definition")
    extended = effective_glossary_scalar(llm_item, sections, "extended_explanation")
    relevance = effective_glossary_scalar(llm_item, sections, "relevance_note")
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    related = llm_item.get("related_terms") or []
    if not isinstance(related, list):
        related = []

    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, glossary_tags)

    lines = [
        f"## {term}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    google = google_search_markdown(term)
    if google:
        lines.extend([google, ""])
    if definition:
        lines.extend(["**Definition**", "", definition, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    if extended:
        lines.extend(["**Extended explanation**", "", extended, ""])
    if relevance:
        lines.extend(["**Relevance**", "", relevance, ""])
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    if related:
        lines.extend([f"*Related terms: {', '.join(str(t) for t in related)}*", ""])
        if norm_to is not None and acr_to is not None:
            unresolved = [
                str(t)
                for t in related
                if not related_term_matches_known_label(str(t), norm_to, acr_to)
            ]
            if unresolved:
                lines.append(
                    "*Related terms not matching any sibling or wiki glossary label: "
                    f"{', '.join(unresolved)}*"
                )
                lines.append("")

    return "\n".join(lines).rstrip()


def build_readonly_glossary_markdown(
    sorted_nodes: list[dict[str, Any]],
    glossary_tags: list[str],
    wiki_glossary_terms: list[str] | None = None,
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Concatenate all glossary proposals for uninterrupted read-only display."""
    if not sorted_nodes:
        return "*(No glossary proposals.)*"
    wiki = list(wiki_glossary_terms or [])
    batch_terms: list[str] = []
    for n in sorted_nodes:
        t = (
            effective_glossary_scalar(
                n.get("llm_item") or {},
                n.get("sections") or {},
                "term",
            )
            or ""
        ).strip()
        if t:
            batch_terms.append(t)
    norm_to, acr_to = build_related_term_resolution_maps(batch_terms, wiki)
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(
            format_glossary_term_readonly_markdown(
                node,
                glossary_tags,
                artifact=artifact,
                norm_to=norm_to,
                acr_to=acr_to,
            )
        )
    return "\n\n---\n\n".join(parts)


def _glossary_expander_label(node: dict[str, Any], index: int) -> str:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    term = effective_glossary_scalar(llm_item, sections, "term") or f"Proposal {index + 1}"
    badge = VALUE_LEVEL_BADGES.get(_value_level(node), "Medium")
    return build_proposal_expander_label(node, term, badge=badge)


def _glossary_related_maps(
    sorted_nodes: list[dict[str, Any]],
    wiki_glossary_terms: list[str] | None,
) -> tuple[dict[str, str], dict[str, str]]:
    wiki = list(wiki_glossary_terms or [])
    batch_terms: list[str] = []
    for n in sorted_nodes:
        t = (
            effective_glossary_scalar(
                n.get("llm_item") or {},
                n.get("sections") or {},
                "term",
            )
            or ""
        ).strip()
        if t:
            batch_terms.append(t)
    return build_related_term_resolution_maps(batch_terms, wiki)


def _find_glossary_node(artifact: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    return find_review_node(artifact, proposal_id, "glossary")


def _sync_llm_term_capitalization(node: dict[str, Any]) -> None:
    """Normalize ``term`` on the embedded LLM item so storage matches display."""
    li = node.get("llm_item")
    if not isinstance(li, dict):
        return
    t = li.get("term")
    if not isinstance(t, str) or not t.strip():
        return
    nt = normalize_glossary_term_capitalization(t)
    if nt != t:
        li["term"] = nt


def _prepare_glossary_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    glossary_nodes = review.setdefault("glossary", [])
    llm_items = artifact.get("llm_output", {}).get("glossary") or []
    for i, node in enumerate(glossary_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
        _sync_llm_term_capitalization(node)
    for item in llm_items:
        if isinstance(item, dict) and isinstance(item.get("term"), str):
            nt = normalize_glossary_term_capitalization(item["term"])
            if nt != item["term"]:
                item["term"] = nt
    return sorted(glossary_nodes, key=_proposal_sort_key)


def _persist_glossary_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    tag_ui: dict[str, Any],
    allow: set[str],
    *,
    key_prefix: str,
) -> None:
    """Apply textarea + tag edits from this run and write the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    merged = read_fast_card_field_values(
        key_prefix,
        title_keys=("term",),
        context_keys=("proposed_definition",),
        more_scalar_keys=tuple(s.key for s in GLOSSARY_MORE_FIELD_SPECS if not s.is_list),
        field_values=field_values,
    )
    apply_glossary_proposal_edits(node, merged)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow, key_prefix=key_prefix)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    term = merged.get("term") or llm_item.get("term") or "proposal"
    set_proposal_save_message(key_prefix, f"Saved **{term}**.")


GLOSSARY_MORE_FIELD_SPECS: tuple[CollapsedFieldSpec, ...] = (
    CollapsedFieldSpec("extended_explanation", "Extended explanation", tall=True),
    CollapsedFieldSpec("relevance_note", "Relevance note"),
)


def _render_glossary_edit_box(
    st: Any,
    node: dict[str, Any],
    glossary_tags: list[str],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
    autosave_registry_key: str,
) -> None:
    """Fast-review card for one glossary proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    term = effective_glossary_scalar(llm_item, sections, "term") or "Untitled"
    value_level = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(value_level, "Medium")
    proposal_id = str(node.get("proposal_id") or "")

    with st.container(border=True):
        render_fast_card_header(
            st,
            node,
            badge=badge,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="glossary",
        )
        render_proposal_regen_meta_caption(st, node, "Glossary term")

        field_values: dict[str, str] = {}
        field_values["term"] = st.text_area(
            "Term",
            value=glossary_field_edit_value(llm_item, sections, "term"),
            height=72,
            key=f"{key_prefix}_edit_term",
        )
        render_readonly_context_hint(
            st,
            label="Proposed definition",
            value=glossary_field_edit_value(llm_item, sections, "proposed_definition"),
        )

        render_inline_regenerate_title_controls(
            st,
            entity_key="glossary",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=term,
            title_label="New term",
        )

        tag_ui = render_domain_tag_section(
            st,
            node,
            glossary_tags,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="glossary",
            label_widget_key=f"{key_prefix}_edit_term",
            summary_widget_key=f"{key_prefix}_edit_proposed_definition",
            llm_fallback_label_key="term",
            llm_fallback_summary_key="proposed_definition",
        )

        def _save() -> None:
            _persist_glossary_proposal_from_widgets(
                node,
                artifact_path,
                field_values,
                tag_ui,
                tag_allow,
                key_prefix=key_prefix,
            )

        render_fast_card_save_row(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="glossary",
            on_save_callback=_save,
        )

        render_context_expander(
            st,
            label="Definition / context",
            field_key="proposed_definition",
            field_label="Proposed definition",
            value=glossary_field_edit_value(llm_item, sections, "proposed_definition"),
            widget_key=f"{key_prefix}_ctx_proposed_definition",
            field_values=field_values,
        )
        render_collapsed_fields(
            st,
            specs=list(GLOSSARY_MORE_FIELD_SPECS),
            get_value=glossary_field_edit_value,
            llm_item=llm_item,
            sections=sections,
            key_prefix=key_prefix,
            field_values=field_values,
        )
        render_source_evidence_expander(st, llm_item)
        render_fast_card_reclassify(
            st,
            node,
            reclassify_entity_key="glossary",
            source_id=source_id,
            current_title=term,
            key_prefix=key_prefix,
        )
        register_card_autosave(autosave_registry_key, node, _save)


def render_glossary_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    glossary_tags: list[str],
    artifact_path: Path,
    wiki_glossary_terms: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column glossary review: read-only catalog left, edit panel right."""
    tag_allow = {normalize_tag(str(t)) for t in glossary_tags if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = list(glossary_tags)
    st.subheader("Glossary")
    sorted_nodes = _prepare_glossary_nodes(artifact)
    llm_items = artifact.get("llm_output", {}).get("glossary") or []

    if not sorted_nodes and not llm_items:
        st.caption("No glossary proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    regen_msg = pop_proposal_regen_msg("glossary")
    if regen_msg:
        st.success(regen_msg)

    norm_to, acr_to = _glossary_related_maps(sorted_nodes, wiki_glossary_terms)

    def _readonly_md(node: dict[str, Any]) -> str:
        if len(sorted_nodes) == 1:
            return build_readonly_glossary_markdown(
                [node], glossary_tags, wiki_glossary_terms, artifact=artifact
            )
        return format_glossary_term_readonly_markdown(
            node,
            glossary_tags,
            artifact=artifact,
            norm_to=norm_to,
            acr_to=acr_to,
        )

    def _render_edit(node: dict[str, Any], index: int) -> None:
        pid = str(node.get("proposal_id") or f"idx{index}")
        pfx = proposal_edit_key_prefix(
            key_prefix, pid, "g", regen_count=regen_count_from_node(node)
        )
        _render_glossary_edit_box(
            st,
            node,
            glossary_tags,
            key_prefix=pfx,
            source_id=source_id,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            tag_allow=tag_allow,
            autosave_registry_key=key_prefix,
        )

    render_two_column_proposal_review(
        st,
        sorted_nodes,
        key_prefix=key_prefix,
        empty_readonly_text="*(No glossary proposals.)*",
        label_for_node=_glossary_expander_label,
        readonly_markdown_for_node=_readonly_md,
        render_edit_for_node=_render_edit,
    )


def collect_glossary_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags from glossary proposals."""
    from src.ingest_review.domain_tag_ui import collect_approved_new_tags_from_review

    return collect_approved_new_tags_from_review(artifact, "glossary")
