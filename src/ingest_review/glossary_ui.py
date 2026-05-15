"""Streamlit rendering for glossary proposals (proposal-level review)."""

from __future__ import annotations

import logging
import urllib.parse
from typing import Any

from src.ingest_review.artifact import aggregate_impl_study_section_status
from src.ingest_review.dashboard_ui import (
    format_proposed_tags_caption,
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_proposal_tag_review,
)
from src.ingest_review.schema import (
    GLOSSARY_REVIEWABLE_LIST_KEYS,
    GLOSSARY_REVIEWABLE_SCALAR_KEYS,
)

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")

VALUE_LEVEL_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}

VALUE_LEVEL_BADGES: dict[str, str] = {
    "high": "🔴 High",
    "medium": "🟡 Medium",
    "low": "⚪ Low",
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


def _status_index(current: str) -> int:
    """Return index of current status in PROPOSAL_STATUS_OPTIONS."""
    if current in PROPOSAL_STATUS_OPTIONS:
        return PROPOSAL_STATUS_OPTIONS.index(current)
    return 0


def _render_proposal_card(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    glossary_tags: list[str],
    *,
    key_prefix: str,
    auto_expand: bool,
) -> None:
    """Render a single glossary proposal as a compact card with action buttons."""
    term = llm_item.get("term") or "Untitled"
    value_level = str(llm_item.get("value_level") or "medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    suggested_action = llm_item.get("suggested_action") or "—"
    definition = str(llm_item.get("proposed_definition") or "")
    proposal_status = str(node.get("proposal_status") or "pending")

    badge = VALUE_LEVEL_BADGES.get(value_level, "⚪ Low")
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    sections = node.setdefault("sections", {})
    agg = aggregate_impl_study_section_status(sections)

    header = f"{badge} · **{term}** · {ev_lbl} · {confidence:.0%} · {proposal_status}"
    with st.expander(header, expanded=auto_expand):
        col_info, col_action = st.columns([3, 1])
        with col_info:
            st.caption(f"Suggested action: `{suggested_action}` · Section status: {agg}")
            search_url = "https://www.google.com/search?" + urllib.parse.urlencode({"q": term})
            st.markdown(f'[Google: "{term}"]({search_url})')
        with col_action:
            st.caption("Proposal decision")

        st.markdown("**Proposed definition**")
        st.text(definition[:4000] + ("…" if len(definition) > 4000 else ""))

        _render_tag_summary(st, llm_item, node, glossary_tags)

        _render_action_buttons(st, node, key_prefix=key_prefix)

        if node.get("proposal_status") == "pending" or node.get("_edit_mode"):
            _render_edit_panel(st, llm_item, node, glossary_tags, key_prefix=key_prefix)

        _render_source_evidence(st, llm_item, key_prefix=key_prefix)
        _render_related_terms(st, llm_item)

        node["notes"] = st.text_input(
            "Proposal notes",
            value=str(node.get("notes") or ""),
            key=f"{key_prefix}_notes",
        )


def _render_tag_summary(
    st: Any,
    llm_item: dict[str, Any],
    node: dict[str, Any],
    glossary_tags: list[str],
) -> None:
    """Show tags as read-only text in the default card view."""
    tag_node = node.get("tags") or {}
    caption = format_proposed_tags_caption(llm_item, tag_node, glossary_tags)
    if caption:
        st.caption(caption)


def _render_action_buttons(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render 4 action buttons: Approve / Reject / Edit / Defer."""
    col_approve, col_reject, col_edit, col_defer = st.columns(4)
    current = str(node.get("proposal_status") or "pending")

    with col_approve:
        if st.button(
            "✅ Approve" if current != "approved" else "✅ Approved",
            key=f"{key_prefix}_approve",
            disabled=(current == "approved"),
        ):
            node["proposal_status"] = "approved"
            node.pop("_edit_mode", None)
            st.rerun()

    with col_reject:
        if st.button(
            "❌ Reject" if current != "rejected" else "❌ Rejected",
            key=f"{key_prefix}_reject",
            disabled=(current == "rejected"),
        ):
            node["proposal_status"] = "rejected"
            node.pop("_edit_mode", None)
            st.rerun()

    with col_edit:
        if st.button("✏️ Edit", key=f"{key_prefix}_edit"):
            node["_edit_mode"] = True
            node["proposal_status"] = "pending"
            st.rerun()

    with col_defer:
        if st.button(
            "⏸️ Defer" if current != "deferred" else "⏸️ Deferred",
            key=f"{key_prefix}_defer",
            disabled=(current == "deferred"),
        ):
            node["proposal_status"] = "deferred"
            node.pop("_edit_mode", None)
            st.rerun()


def _render_edit_panel(
    st: Any,
    llm_item: dict[str, Any],
    node: dict[str, Any],
    glossary_tags: list[str],
    *,
    key_prefix: str,
) -> None:
    """Render field-level editing for reviewable scalar fields and tags."""
    with st.expander("✏️ Edit fields", expanded=bool(node.get("_edit_mode"))):
        sections = node.setdefault("sections", {})

        for sk in GLOSSARY_REVIEWABLE_SCALAR_KEYS:
            _render_editable_scalar(st, llm_item, sections, section_key=sk, key_prefix=key_prefix)

        for lk in GLOSSARY_REVIEWABLE_LIST_KEYS:
            _render_editable_list(st, llm_item, sections, section_key=lk, key_prefix=key_prefix)

        st.divider()
        tag_node = node.setdefault(
            "tags",
            {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
        )
        render_proposal_tag_review(
            st, llm_item, tag_node, glossary_tags, key_prefix=key_prefix, entity_kind="domain"
        )
        render_proposal_evidence_type_editor(st, llm_item, key_prefix=key_prefix)


def _render_editable_scalar(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    """Render an editable text area for a scalar review field."""
    label = SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    tall = section_key in ("extended_explanation", "proposed_definition")

    current_text = node.get("final_text") if node.get("final_text") else llm_text
    node["final_text"] = st.text_area(
        label,
        value=current_text,
        height=160 if tall else 100,
        key=f"{key_prefix}_{section_key}_txt",
    )
    if node["final_text"] != llm_text:
        node["status"] = "modified"
    else:
        node["final_text"] = None
        if node["status"] == "modified":
            node["status"] = "pending"


def _render_editable_list(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    """Render an editable text area for a list review field."""
    label = SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    llm_list = llm_item.get(section_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_list": None, "notes": None, "llm_list": list(llm_list)},
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_list)

    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw = st.text_area(
        f"{label} (one per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_{section_key}_txt",
    )
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if lines != node["llm_list"]:
        node["final_list"] = lines
        node["status"] = "modified"
    else:
        node["final_list"] = None
        if node["status"] == "modified":
            node["status"] = "pending"


def _render_source_evidence(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render supporting_snippet as read-only in a collapsible expander."""
    snippet = str(llm_item.get("supporting_snippet") or "")
    if not snippet.strip():
        return
    with st.expander("📄 Source evidence", expanded=False):
        st.text(snippet[:6000] + ("…" if len(snippet) > 6000 else ""))


def _render_related_terms(st: Any, llm_item: dict[str, Any]) -> None:
    """Render related_terms as a read-only informational note."""
    related = llm_item.get("related_terms") or []
    if not isinstance(related, list) or not related:
        return
    st.info(f"**Related terms:** {', '.join(str(t) for t in related)}")


def _render_match_candidates(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render possible existing matches from the LLM."""
    candidates = llm_item.get("match_candidates") or []
    if not candidates:
        return
    with st.expander("Possible existing matches (from LLM)", expanded=False):
        for mc in candidates:
            if not isinstance(mc, dict):
                continue
            title = mc.get("title_or_slug", "?")
            kind = mc.get("match_kind", "?")
            conf = mc.get("confidence", 0)
            st.warning(f"**{title}** — match: {kind}, confidence: {conf:.0%}")


def render_glossary_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    glossary_tags: list[str],
) -> None:
    """Render proposal-level review for all glossary proposals.

    Proposals are sorted by value_level (high first) then confidence descending.
    High-value proposals are auto-expanded; medium collapsed; low hidden in a
    separate section.
    """
    review = artifact.setdefault("review", {})
    glossary_nodes = review.setdefault("glossary", [])
    llm_items = artifact.get("llm_output", {}).get("glossary") or []
    st.subheader("Glossary")

    if not glossary_nodes and not llm_items:
        st.caption("No glossary proposals.")
        return

    for i, node in enumerate(glossary_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]

    sorted_nodes = sorted(glossary_nodes, key=_proposal_sort_key)

    high_nodes = [n for n in sorted_nodes if _value_level(n) == "high"]
    medium_nodes = [n for n in sorted_nodes if _value_level(n) == "medium"]
    low_nodes = [n for n in sorted_nodes if _value_level(n) == "low"]

    if high_nodes:
        st.markdown("#### High value")
        for i, node in enumerate(high_nodes):
            llm_item = node.get("llm_item") or {}
            pfx = f"{key_prefix}_gh{i}"
            _render_proposal_card(
                st,
                node,
                llm_item,
                glossary_tags,
                key_prefix=pfx,
                auto_expand=True,
            )
            _render_match_candidates(st, llm_item, key_prefix=pfx)

    if medium_nodes:
        st.markdown("#### Medium value")
        for i, node in enumerate(medium_nodes):
            llm_item = node.get("llm_item") or {}
            pfx = f"{key_prefix}_gm{i}"
            _render_proposal_card(
                st,
                node,
                llm_item,
                glossary_tags,
                key_prefix=pfx,
                auto_expand=False,
            )
            _render_match_candidates(st, llm_item, key_prefix=pfx)

    if low_nodes:
        with st.expander(f"⚪ Low value ({len(low_nodes)} proposals)", expanded=False):
            for i, node in enumerate(low_nodes):
                llm_item = node.get("llm_item") or {}
                pfx = f"{key_prefix}_gl{i}"
                _render_proposal_card(
                    st,
                    node,
                    llm_item,
                    glossary_tags,
                    key_prefix=pfx,
                    auto_expand=False,
                )
                _render_match_candidates(st, llm_item, key_prefix=pfx)


def _value_level(node: dict[str, Any]) -> str:
    """Extract value_level from a glossary review node."""
    llm_item = node.get("llm_item") or {}
    return str(llm_item.get("value_level") or "medium")


def collect_glossary_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags from glossary proposals.

    Collects `suggested_new_tag` where `new_tag_approved` is True across all
    glossary review nodes.

    Args:
        artifact: The full review artifact dict.

    Returns:
        Deduplicated list of approved new tag strings.
    """
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
