"""Streamlit rendering for glossary proposals (two-column read/edit layout)."""

from __future__ import annotations

import logging
import urllib.parse
import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    format_proposed_tags_caption,
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_proposal_tag_review,
)
from src.ingest_review.schema import GLOSSARY_REVIEWABLE_SCALAR_KEYS

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
        return final.strip()
    return str(llm_item.get(section_key) or "").strip()


def apply_glossary_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one glossary field edit; infer section status from LLM draft."""
    text = raw_text.strip()
    llm_text = str(llm_item.get(section_key) or "").strip()
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    if text == llm_text:
        node["status"] = "approved"
        node["final_text"] = None
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


def _google_search_markdown(term: str) -> str:
    if not term.strip():
        return ""
    url = "https://www.google.com/search?" + urllib.parse.urlencode({"q": term})
    return f"[Google: \"{term}\"]({url})"


def format_glossary_term_readonly_markdown(
    node: dict[str, Any],
    glossary_tags: list[str],
) -> str:
    """Format one glossary proposal as markdown for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    term = effective_glossary_scalar(llm_item, sections, "term") or "Untitled"
    value_level = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(value_level, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    proposal_status = str(node.get("proposal_status") or "pending")
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    suggested_action = llm_item.get("suggested_action") or "—"

    definition = effective_glossary_scalar(llm_item, sections, "proposed_definition")
    extended = effective_glossary_scalar(llm_item, sections, "extended_explanation")
    relevance = effective_glossary_scalar(llm_item, sections, "relevance_note")
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    related = llm_item.get("related_terms") or []
    if not isinstance(related, list):
        related = []

    tag_node = node.get("tags") or {}
    tag_caption = format_proposed_tags_caption(llm_item, tag_node, glossary_tags)

    lines = [
        f"## {term}",
        "",
        f"*{badge} · {proposal_status} · {ev_lbl} · {confidence:.0%} · "
        f"suggested: `{suggested_action}`*",
        "",
    ]
    google = _google_search_markdown(term)
    if google:
        lines.extend([google, ""])
    if definition:
        lines.extend(["**Definition**", "", definition, ""])
    if extended:
        lines.extend(["**Extended explanation**", "", extended, ""])
    if relevance:
        lines.extend(["**Relevance**", "", relevance, ""])
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    if tag_caption:
        lines.extend([f"*{tag_caption}*", ""])
    if related:
        lines.extend([f"*Related terms: {', '.join(str(t) for t in related)}*", ""])

    candidates = llm_item.get("match_candidates") or []
    if isinstance(candidates, list) and candidates:
        match_bits: list[str] = []
        for mc in candidates:
            if not isinstance(mc, dict):
                continue
            title = mc.get("title_or_slug", "?")
            kind = mc.get("match_kind", "?")
            conf = mc.get("confidence", 0)
            match_bits.append(f"{title} ({kind}, {conf:.0%})")
        if match_bits:
            lines.extend([f"*Possible matches: {'; '.join(match_bits)}*", ""])

    return "\n".join(lines).rstrip()


def build_readonly_glossary_markdown(
    sorted_nodes: list[dict[str, Any]],
    glossary_tags: list[str],
) -> str:
    """Concatenate all glossary proposals for uninterrupted read-only display."""
    if not sorted_nodes:
        return "*(No glossary proposals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_glossary_term_readonly_markdown(node, glossary_tags))
    return "\n\n---\n\n".join(parts)


def _find_glossary_node(artifact: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    for node in (artifact.get("review") or {}).get("glossary") or []:
        if isinstance(node, dict) and node.get("proposal_id") == proposal_id:
            return node
    return None


def _prepare_glossary_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    glossary_nodes = review.setdefault("glossary", [])
    llm_items = artifact.get("llm_output", {}).get("glossary") or []
    for i, node in enumerate(glossary_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(glossary_nodes, key=_proposal_sort_key)


def _on_save_glossary_proposal(
    proposal_id: str,
    key_prefix: str,
    artifact_path: Path,
) -> None:
    """Streamlit on_click: apply field edits and persist artifact immediately."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    node = _find_glossary_node(artifact, proposal_id)
    if not node:
        return
    field_values = {
        sk: str(streamlit_runtime.session_state.get(f"{key_prefix}_edit_{sk}", ""))
        for sk in GLOSSARY_REVIEWABLE_SCALAR_KEYS
    }
    apply_glossary_proposal_edits(node, field_values)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    llm_item = node.get("llm_item") or {}
    term = field_values.get("term") or llm_item.get("term") or "proposal"
    streamlit_runtime.session_state["_glossary_save_msg"] = f"Saved **{term}**."


def _on_set_glossary_proposal_status(
    proposal_id: str,
    status: str,
    artifact_path: Path,
) -> None:
    """Streamlit on_click: set proposal_status and persist immediately."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    node = _find_glossary_node(artifact, proposal_id)
    if not node:
        return
    node["proposal_status"] = status
    node.pop("_edit_mode", None)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)


def _render_proposal_action_row(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
    artifact_path: Path,
) -> None:
    """Approve / Reject / Defer with immediate persistence."""
    proposal_id = str(node.get("proposal_id") or "")
    current = str(node.get("proposal_status") or "pending")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button(
            "Approve",
            key=f"{key_prefix}_approve",
            disabled=(current == "approved"),
            on_click=_on_set_glossary_proposal_status,
            args=(proposal_id, "approved", artifact_path),
            use_container_width=True,
        )
    with c2:
        st.button(
            "Reject",
            key=f"{key_prefix}_reject",
            disabled=(current == "rejected"),
            on_click=_on_set_glossary_proposal_status,
            args=(proposal_id, "rejected", artifact_path),
            use_container_width=True,
        )
    with c3:
        st.button(
            "Defer",
            key=f"{key_prefix}_defer",
            disabled=(current == "deferred"),
            on_click=_on_set_glossary_proposal_status,
            args=(proposal_id, "deferred", artifact_path),
            use_container_width=True,
        )


def _render_glossary_edit_box(
    st: Any,
    node: dict[str, Any],
    glossary_tags: list[str],
    *,
    key_prefix: str,
    artifact_path: Path,
) -> None:
    """One bordered edit box per glossary proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    term = effective_glossary_scalar(llm_item, sections, "term") or "Untitled"
    value_level = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(value_level, "Medium")
    proposal_status = str(node.get("proposal_status") or "pending")

    with st.container(border=True):
        st.markdown(f"**{term}** · {badge} · `{proposal_status}`")
        _render_proposal_action_row(st, node, key_prefix=key_prefix, artifact_path=artifact_path)

        for sk in GLOSSARY_REVIEWABLE_SCALAR_KEYS:
            label = SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            tall = sk in ("proposed_definition", "extended_explanation")
            st.text_area(
                label,
                value=glossary_field_edit_value(llm_item, sections, sk),
                height=120 if tall else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        tag_node = node.setdefault(
            "tags",
            {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
        )
        render_proposal_tag_review(
            st, llm_item, tag_node, glossary_tags, key_prefix=key_prefix, entity_kind="domain"
        )
        render_proposal_evidence_type_editor(st, llm_item, key_prefix=key_prefix)

        snippet = str(llm_item.get("supporting_snippet") or "").strip()
        if snippet:
            with st.expander("Source evidence (read-only)", expanded=False):
                st.text(snippet[:4000] + ("…" if len(snippet) > 4000 else ""))

        st.button(
            "Save edit",
            key=f"{key_prefix}_save",
            on_click=_on_save_glossary_proposal,
            args=(str(node.get("proposal_id") or ""), key_prefix, artifact_path),
            use_container_width=True,
        )


def render_glossary_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    glossary_tags: list[str],
    artifact_path: Path,
) -> None:
    """Two-column glossary review: read-only catalog left, per-term edit boxes right."""
    st.subheader("Glossary")
    sorted_nodes = _prepare_glossary_nodes(artifact)
    llm_items = artifact.get("llm_output", {}).get("glossary") or []

    if not sorted_nodes and not llm_items:
        st.caption("No glossary proposals.")
        return

    pending = sum(
        1 for n in sorted_nodes if str(n.get("proposal_status") or "pending") == "pending"
    )
    st.caption(f"{len(sorted_nodes)} proposal(s) · {pending} pending")

    save_msg = streamlit_runtime.session_state.pop("_glossary_save_msg", None)
    if save_msg:
        st.success(str(save_msg))

    read_col, edit_col = st.columns(2)
    with read_col:
        st.markdown(build_readonly_glossary_markdown(sorted_nodes, glossary_tags))
    with edit_col:
        edit_nodes = sorted_nodes
        if len(sorted_nodes) > 6:
            labels = [
                effective_glossary_scalar(
                    n.get("llm_item") or {},
                    n.get("sections") or {},
                    "term",
                )
                or f"Proposal {i + 1}"
                for i, n in enumerate(sorted_nodes)
            ]
            pick = st.selectbox(
                "Edit term",
                options=labels,
                key=f"{key_prefix}_glossary_jump",
            )
            idx = labels.index(pick) if pick in labels else 0
            edit_nodes = [sorted_nodes[idx]]
            st.caption("Showing one edit panel — use the selector to switch terms.")

        for i, node in enumerate(edit_nodes):
            pid = str(node.get("proposal_id") or f"idx{i}")
            pfx = f"{key_prefix}_g_{pid[:8]}"
            _render_glossary_edit_box(
                st,
                node,
                glossary_tags,
                key_prefix=pfx,
                artifact_path=artifact_path,
            )


def collect_glossary_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags from glossary proposals."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("glossary") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        if not tag_node.get("new_tag_approved"):
            continue
        llm_item = node.get("llm_item") or {}
        suggested = llm_item.get("suggested_new_tag") or ""
        if suggested and suggested not in tags:
            tags.append(suggested)
    return tags
