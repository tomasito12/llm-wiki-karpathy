"""Streamlit rendering for interview insight proposals (proposal-level review)."""

from __future__ import annotations

import logging
from typing import Any

from src.ingest_review.dashboard_ui import (
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_proposal_tag_review,
)
from src.ingest_review.schema import (
    INSIGHT_REVIEWABLE_LIST_KEYS,
    INSIGHT_REVIEWABLE_SCALAR_KEYS,
)

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")
STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

_VALUE_LEVEL_SORT: dict[str, int] = {"high": 0, "medium": 1, "low": 2}
_VALUE_LEVEL_BADGE: dict[str, str] = {"high": "H", "medium": "M", "low": "L"}
_CONFIDENCE_SORT: dict[str, int] = {"high": 0, "medium": 1, "low": 2}

INSIGHT_SECTION_LABELS: dict[str, str] = {
    "insight_title": "Insight title",
    "insight_type": "Insight type",
    "summary": "Summary",
    "why_it_matters": "Why it matters",
    "operational_relevance": "Operational relevance",
    "service_automation_relevance": "Service automation relevance",
    "confidence": "Confidence",
    "durability_estimate": "Durability estimate",
    "wiki_worthiness": "Wiki-worthiness",
    "suggested_destinations": "Suggested destinations",
    "mentioned_entities": "Mentioned entities",
    "contrarian_or_speculative_claims": "Contrarian / speculative claims",
    "evidence_snippets": "Evidence snippets",
}


def _proposal_status_index(current: str) -> int:
    """Return index into PROPOSAL_STATUS_OPTIONS."""
    if current in PROPOSAL_STATUS_OPTIONS:
        return PROPOSAL_STATUS_OPTIONS.index(current)
    return 0


def _status_index(current: str) -> int:
    """Return index into STATUS_OPTIONS."""
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _sort_key(node: dict[str, Any]) -> tuple[int, int]:
    """Sort by value_level (high first) then confidence (high first)."""
    llm = node.get("llm_item") or {}
    vl = str(llm.get("value_level", "medium"))
    conf = str(llm.get("confidence", "low"))
    return (_VALUE_LEVEL_SORT.get(vl, 1), _CONFIDENCE_SORT.get(conf, 2))


def _render_card_header(
    st: Any,
    llm_item: dict[str, Any],
    node: dict[str, Any],
    *,
    index: int,
) -> None:
    """Render compact proposal card header with value badge and key metrics."""
    vl = str(llm_item.get("value_level", "medium"))
    badge = _VALUE_LEVEL_BADGE.get(vl, "M")
    title = llm_item.get("insight_title") or f"Insight #{index + 1}"
    conf = llm_item.get("confidence") or "\u2014"
    durability = llm_item.get("durability_estimate") or "\u2014"
    worthiness = llm_item.get("wiki_worthiness") or "\u2014"
    ins_type = llm_item.get("insight_type") or "\u2014"
    status = node.get("proposal_status", "pending")
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))

    st.markdown(
        f"**[{badge}] {title}** \u00b7 "
        f"confidence: {conf} \u00b7 durability: {durability} \u00b7 worthiness: {worthiness}"
    )
    st.caption(f"Type: {ins_type} \u00b7 Evidence: {ev_lbl} \u00b7 Status: `{status}`")


def _render_action_row(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render Approve | Reject | Defer action buttons."""
    c1, c2, c3 = st.columns(3)
    if c1.button("\u2713 Approve", key=f"{key_prefix}_approve"):
        node["proposal_status"] = "approved"
    if c2.button("\u2717 Reject", key=f"{key_prefix}_reject"):
        node["proposal_status"] = "rejected"
    if c3.button("\u23f3 Defer", key=f"{key_prefix}_defer"):
        node["proposal_status"] = "deferred"


def _render_scalar_field(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    """Render a reviewable scalar field inside the edit expander."""
    label = INSIGHT_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"##### {label}")
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    st.text(llm_text[:6000] + ("\u2026" if len(llm_text) > 6000 else ""))
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_ins_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        tall = section_key in ("summary", "operational_relevance", "service_automation_relevance")
        node["final_text"] = st.text_area(
            f"{label} \u2014 final text",
            value=default,
            height=160 if tall else 100,
            key=f"{key_prefix}_ins_{section_key}_txt",
        )
    else:
        node["final_text"] = None
    node["notes"] = st.text_input(
        f"{label} \u2014 notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_ins_{section_key}_notes",
    )


def _render_list_field(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    """Render a reviewable list field inside the edit expander."""
    label = INSIGHT_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"##### {label}")
    llm_list = llm_item.get(section_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_list": None, "notes": None, "llm_list": list(llm_list)},
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_list)
    st.json(node["llm_list"])
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_ins_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} \u2014 final list (one per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_ins_{section_key}_txt",
    )
    lines = [ln.strip() for ln in raw_list.splitlines() if ln.strip()]
    if node["status"] == "modified":
        node["final_list"] = lines
    else:
        node["final_list"] = None
    node["notes"] = st.text_input(
        f"{label} \u2014 notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_ins_{section_key}_notes",
    )


def _render_tag_panel(
    st: Any,
    llm_item: dict[str, Any],
    tag_node: dict[str, Any],
    topic_tags: list[str],
    *,
    key_prefix: str,
) -> None:
    """Render tag review panel with final_primary_tag / final_secondary_tag."""
    render_proposal_tag_review(
        st, llm_item, tag_node, topic_tags, key_prefix=key_prefix, entity_kind="domain"
    )


def render_interview_insights(
    st: Any,
    artifact: dict[str, Any],
    *,
    topic_tags: list[str] | None = None,
    key_prefix: str,
) -> None:
    """Render proposal-level review for all interview insight proposals.

    Each insight is shown as a compact card with value_level badge,
    title, and key metrics, followed by an action row and an edit
    expander for field-level editing. Sorted by value_level then
    confidence (high first).
    """
    review = artifact.setdefault("review", {})
    insight_nodes = review.setdefault("interview_insights", [])
    st.subheader("Interview insights")
    if not insight_nodes:
        st.caption("No interview insights extracted (source is not an interview/transcript).")
        return

    sorted_nodes = sorted(insight_nodes, key=_sort_key)

    for i, node in enumerate(sorted_nodes):
        llm_item = node.get("llm_item") or {}
        pid = node.get("proposal_id") or f"anon{i}"
        pfx = f"{key_prefix}_ins_{pid[:8]}"

        _render_card_header(st, llm_item, node, index=i)
        _render_action_row(st, node, key_prefix=pfx)

        sections = node.setdefault("sections", {})
        tag_node = node.setdefault(
            "tags",
            {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
        )
        title = llm_item.get("insight_title") or f"Insight #{i + 1}"
        with st.expander(f"Edit: {title}", expanded=False):
            for sk in INSIGHT_REVIEWABLE_SCALAR_KEYS:
                _render_scalar_field(st, llm_item, sections, section_key=sk, key_prefix=pfx)
            for lk in INSIGHT_REVIEWABLE_LIST_KEYS:
                _render_list_field(st, llm_item, sections, section_key=lk, key_prefix=pfx)
            st.divider()
            _render_tag_panel(st, llm_item, tag_node, topic_tags or [], key_prefix=pfx)
            render_proposal_evidence_type_editor(st, llm_item, key_prefix=pfx)
            node["notes"] = st.text_input(
                "Insight notes",
                value=str(node.get("notes") or ""),
                key=f"{pfx}_ins_notes",
            )
            with st.expander("Raw JSON (debug)", expanded=False):
                st.json(llm_item)
        st.divider()


def collect_insight_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags where new_tag_approved is True across insights."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("interview_insights") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        if not tag_node.get("new_tag_approved"):
            continue
        llm_item = node.get("llm_item") or {}
        new_tag = llm_item.get("suggested_new_tag") or ""
        if new_tag and new_tag not in tags:
            tags.append(new_tag)
    return tags
