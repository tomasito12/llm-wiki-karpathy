"""Streamlit rendering for topic proposals (proposal-level review)."""

from __future__ import annotations

import logging
from typing import Any

from src.ingest_review.dashboard_ui import (
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
)
from src.ingest_review.schema import TOPIC_REVIEWABLE_LIST_KEYS, TOPIC_REVIEWABLE_SCALAR_KEYS

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")
FIELD_STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

VALUE_LEVEL_ORDER = {"high": 0, "medium": 1, "low": 2}

TOPIC_FIELD_LABELS: dict[str, str] = {
    "topic_slug": "Topic slug",
    "topic_title": "Topic title",
    "knowledge_summary": "Knowledge summary",
    "operational_insight": "Operational insight",
    "relevance_note": "Relevance note",
    "key_points": "Key points",
}


def _proposal_status_index(current: str) -> int:
    """Return index of *current* in proposal status options, defaulting to 0."""
    if current in PROPOSAL_STATUS_OPTIONS:
        return PROPOSAL_STATUS_OPTIONS.index(current)
    return 0


def _field_status_index(current: str) -> int:
    """Return index of *current* in field status options, defaulting to 0."""
    if current in FIELD_STATUS_OPTIONS:
        return FIELD_STATUS_OPTIONS.index(current)
    return 0


def _sort_key(node: dict[str, Any]) -> tuple[int, float]:
    """Sort proposals: high value first, then descending confidence."""
    llm = node.get("llm_item") or {}
    level = str(llm.get("value_level") or "medium")
    conf = float(llm.get("confidence") or 0)
    return (VALUE_LEVEL_ORDER.get(level, 1), -conf)


def _render_compact_card(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    idx: int,
    *,
    key_prefix: str,
) -> None:
    """Render a compact read-only proposal card with action buttons."""
    value_level = str(llm_item.get("value_level") or "medium").upper()
    title = llm_item.get("topic_title") or llm_item.get("topic_slug") or f"Topic #{idx + 1}"
    conf = float(llm_item.get("confidence") or 0)
    status = str(node.get("proposal_status") or "pending")

    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    st.markdown(f"**[{value_level}] {title}** — evidence: _{ev_lbl}_ — confidence: {conf:.0%}")

    summary = str(llm_item.get("knowledge_summary") or "")
    if summary:
        st.text(summary[:2000] + ("\u2026" if len(summary) > 2000 else ""))

    primary = str(llm_item.get("primary_tag") or "")
    secondary = str(llm_item.get("secondary_tag") or "")
    tag_parts = [t for t in (primary, secondary) if t]
    if tag_parts:
        st.caption(f"Tags: {', '.join(tag_parts)}")

    cols = st.columns(4)
    pfx = f"{key_prefix}_act"
    if cols[0].button("Approve", key=f"{pfx}_approve"):
        node["proposal_status"] = "approved"
    if cols[1].button("Reject", key=f"{pfx}_reject"):
        node["proposal_status"] = "rejected"
    if cols[2].button("Edit", key=f"{pfx}_edit"):
        st.session_state[f"{pfx}_editing"] = True
    if cols[3].button("Defer", key=f"{pfx}_defer"):
        node["proposal_status"] = "deferred"

    if status != str(node.get("proposal_status") or "pending"):
        st.rerun()

    st.caption(f"Status: **{node.get('proposal_status', 'pending')}**")


def _render_edit_mode(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
    topic_tags: list[str],
) -> None:
    """Render the full edit expander with per-field review controls and tag editing."""
    sections = node.setdefault("sections", {})

    for sk in TOPIC_REVIEWABLE_SCALAR_KEYS:
        label = TOPIC_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
        st.markdown(f"#### {label}")
        sec = sections.setdefault(sk, {"status": "pending", "final_text": None, "notes": None})
        llm_text = str(llm_item.get(sk) or "")
        st.text(llm_text[:6000] + ("\u2026" if len(llm_text) > 6000 else ""))
        sec["status"] = st.selectbox(
            f"{label} \u2014 status",
            FIELD_STATUS_OPTIONS,
            index=_field_status_index(str(sec.get("status") or "pending")),
            key=f"{key_prefix}_f_{sk}_st",
        )
        if sec["status"] == "modified":
            default = sec.get("final_text") if sec.get("final_text") else llm_text
            sec["final_text"] = st.text_area(
                f"{label} \u2014 final text",
                value=default,
                height=140,
                key=f"{key_prefix}_f_{sk}_txt",
            )
        else:
            sec["final_text"] = None

    for lk in TOPIC_REVIEWABLE_LIST_KEYS:
        label = TOPIC_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
        st.markdown(f"#### {label}")
        llm_list = llm_item.get(lk) or []
        if not isinstance(llm_list, list):
            llm_list = []
        sec = sections.setdefault(
            lk,
            {"status": "pending", "final_list": None, "notes": None, "llm_list": list(llm_list)},
        )
        if not sec.get("llm_list"):
            sec["llm_list"] = list(llm_list)
        st.json(sec["llm_list"])
        sec["status"] = st.selectbox(
            f"{label} \u2014 status",
            FIELD_STATUS_OPTIONS,
            index=_field_status_index(str(sec.get("status") or "pending")),
            key=f"{key_prefix}_f_{lk}_st",
        )
        if sec["status"] == "modified":
            default_lines = sec.get("final_list") or sec["llm_list"]
            raw = st.text_area(
                f"{label} \u2014 final list (one per line)",
                value="\n".join(str(x) for x in (default_lines or [])),
                height=100,
                key=f"{key_prefix}_f_{lk}_txt",
            )
            sec["final_list"] = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        else:
            sec["final_list"] = None

    snippet = str(llm_item.get("supporting_snippet") or "")
    if snippet:
        with st.expander("Source evidence", expanded=False):
            st.text(snippet[:4000])

    related = llm_item.get("related_topics") or []
    if related:
        st.caption(f"Related topics: {', '.join(str(r) for r in related)}")

    st.markdown("#### Tags")
    tag_node = node.setdefault(
        "tags",
        {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
    )
    llm_primary = str(llm_item.get("primary_tag") or "")
    llm_secondary = str(llm_item.get("secondary_tag") or "")
    tag_node["final_primary_tag"] = st.text_input(
        "Primary tag",
        value=str(tag_node.get("final_primary_tag") or llm_primary),
        key=f"{key_prefix}_tag_primary",
    )
    tag_node["final_secondary_tag"] = st.text_input(
        "Secondary tag",
        value=str(tag_node.get("final_secondary_tag") or llm_secondary),
        key=f"{key_prefix}_tag_secondary",
    )
    llm_new_tag = str(llm_item.get("suggested_new_tag") or "")
    suggested = st.text_input(
        "Suggested new tag",
        value=llm_new_tag,
        key=f"{key_prefix}_tag_new",
        disabled=True,
    )
    if suggested:
        tag_node["new_tag_approved"] = st.checkbox(
            f"Approve new tag: {suggested}",
            value=bool(tag_node.get("new_tag_approved")),
            key=f"{key_prefix}_tag_new_approve",
        )

    render_proposal_evidence_type_editor(st, llm_item, key_prefix=key_prefix)

    node["notes"] = st.text_input(
        "Proposal notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_notes",
    )

    with st.expander("Raw JSON (debug)", expanded=False):
        st.json(llm_item)


def render_topic_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    topic_tags: list[str] | None = None,
) -> None:
    """Render proposal-level review for all topic contributions.

    Args:
        st: Streamlit module reference.
        artifact: The full review artifact dict (mutated in place).
        key_prefix: Unique Streamlit key prefix for this render pass.
        topic_tags: Optional tag allowlist (kept for API compatibility).
    """
    tags_list = topic_tags or []
    review = artifact.setdefault("review", {})
    topic_nodes = review.setdefault("topics", [])
    st.subheader("Topics")

    if not topic_nodes:
        st.caption("No topic proposals.")
        return

    sorted_nodes = sorted(topic_nodes, key=_sort_key)

    high_medium = [n for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") != "low"]
    low = [n for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") == "low"]

    for i, node in enumerate(high_medium):
        llm_item = node.get("llm_item") or {}
        value_level = str(llm_item.get("value_level") or "medium")
        title = llm_item.get("topic_title") or llm_item.get("topic_slug") or f"Topic #{i + 1}"
        pfx = f"{key_prefix}_tp{i}"

        auto_expand = value_level == "high"
        with st.expander(f"Topic: {title}", expanded=auto_expand):
            _render_compact_card(st, node, llm_item, i, key_prefix=pfx)
            editing = st.session_state.get(f"{pfx}_act_editing", False)
            if editing:
                _render_edit_mode(st, node, llm_item, key_prefix=pfx, topic_tags=tags_list)

    if low:
        with st.expander(f"Low-value items ({len(low)})", expanded=False):
            for j, node in enumerate(low):
                llm_item = node.get("llm_item") or {}
                title = (
                    llm_item.get("topic_title")
                    or llm_item.get("topic_slug")
                    or f"Low topic #{j + 1}"
                )
                pfx = f"{key_prefix}_tp_low{j}"
                st.markdown("---")
                _render_compact_card(st, node, llm_item, j, key_prefix=pfx)
                editing = st.session_state.get(f"{pfx}_act_editing", False)
                if editing:
                    _render_edit_mode(st, node, llm_item, key_prefix=pfx, topic_tags=tags_list)


def collect_topic_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across topic proposals.

    Args:
        artifact: The full review artifact dict.

    Returns:
        List of unique approved new tag strings.
    """
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("topics") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        if tag_node.get("new_tag_approved"):
            llm_item = node.get("llm_item") or {}
            new_tag = str(llm_item.get("suggested_new_tag") or "").strip()
            if new_tag and new_tag not in tags:
                tags.append(new_tag)
    return tags


# Backwards-compatible alias
collect_topic_approved_new_tags = collect_topic_new_tags
render_topic_contributions = render_topic_proposals
