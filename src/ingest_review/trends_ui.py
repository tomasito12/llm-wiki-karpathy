"""Streamlit rendering for industry trend proposals (proposal-level review)."""

from __future__ import annotations

import logging
from typing import Any

from src.ingest_review.dashboard_ui import (
    format_proposed_tags_caption,
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_proposal_tag_review,
)
from src.ingest_review.schema import TREND_REVIEWABLE_LIST_KEYS, TREND_REVIEWABLE_SCALAR_KEYS

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")
FIELD_STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

VALUE_LEVEL_ORDER = {"high": 0, "medium": 1, "low": 2}

TREND_FIELD_LABELS: dict[str, str] = {
    "trend_name": "Trend name",
    "trend_description": "Trend description",
    "evidence_from_source": "Evidence from source",
    "time_sensitivity": "Time sensitivity",
    "uncertainty_note": "Uncertainty note",
    "supporting_data_points": "Supporting data points",
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
    trend_tags: list[str],
) -> None:
    """Render a compact read-only proposal card with action buttons."""
    value_level = str(llm_item.get("value_level") or "medium").upper()
    title = llm_item.get("trend_name") or f"Trend #{idx + 1}"
    conf = float(llm_item.get("confidence") or 0)
    status = str(node.get("proposal_status") or "pending")

    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    st.markdown(f"**[{value_level}] {title}** — evidence: _{ev_lbl}_ — confidence: {conf:.0%}")

    description = str(llm_item.get("trend_description") or "")
    if description:
        st.text(description[:2000] + ("\u2026" if len(description) > 2000 else ""))

    tag_caption = format_proposed_tags_caption(llm_item, node.get("tags") or {}, trend_tags)
    if tag_caption:
        st.caption(tag_caption)

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
    trend_tags: list[str],
) -> None:
    """Render the full edit expander with per-field review controls and tag editing."""
    sections = node.setdefault("sections", {})

    for sk in TREND_REVIEWABLE_SCALAR_KEYS:
        label = TREND_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
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

    for lk in TREND_REVIEWABLE_LIST_KEYS:
        label = TREND_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
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

    related = llm_item.get("related_trends") or []
    if related:
        st.caption(f"Related trends: {', '.join(str(r) for r in related)}")

    tag_node = node.setdefault(
        "tags",
        {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
    )
    render_proposal_tag_review(
        st, llm_item, tag_node, trend_tags, key_prefix=key_prefix, entity_kind="domain"
    )

    render_proposal_evidence_type_editor(st, llm_item, key_prefix=key_prefix)

    node["notes"] = st.text_input(
        "Proposal notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_notes",
    )

    with st.expander("Raw JSON (debug)", expanded=False):
        st.json(llm_item)


def render_trend_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    trend_tags: list[str] | None = None,
) -> None:
    """Render proposal-level review for all industry trend proposals.

    Args:
        st: Streamlit module reference.
        artifact: The full review artifact dict (mutated in place).
        key_prefix: Unique Streamlit key prefix for this render pass.
        trend_tags: Optional tag allowlist (kept for API compatibility).
    """
    tags_list = trend_tags or []
    review = artifact.setdefault("review", {})
    trend_nodes = review.setdefault("industry_trends", [])
    st.subheader("Trends")

    if not trend_nodes:
        st.caption("No trend proposals.")
        return

    sorted_nodes = sorted(trend_nodes, key=_sort_key)

    high_medium = [n for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") != "low"]
    low = [n for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") == "low"]

    for i, node in enumerate(high_medium):
        llm_item = node.get("llm_item") or {}
        value_level = str(llm_item.get("value_level") or "medium")
        title = llm_item.get("trend_name") or f"Trend #{i + 1}"
        pfx = f"{key_prefix}_tr{i}"

        auto_expand = value_level == "high"
        with st.expander(f"Trend: {title}", expanded=auto_expand):
            _render_compact_card(st, node, llm_item, i, key_prefix=pfx, trend_tags=tags_list)
            editing = st.session_state.get(f"{pfx}_act_editing", False)
            if editing:
                _render_edit_mode(st, node, llm_item, key_prefix=pfx, trend_tags=tags_list)

    if low:
        with st.expander(f"Low-value items ({len(low)})", expanded=False):
            for j, node in enumerate(low):
                llm_item = node.get("llm_item") or {}
                title = llm_item.get("trend_name") or f"Low trend #{j + 1}"
                pfx = f"{key_prefix}_tr_low{j}"
                st.markdown("---")
                _render_compact_card(st, node, llm_item, j, key_prefix=pfx, trend_tags=tags_list)
                editing = st.session_state.get(f"{pfx}_act_editing", False)
                if editing:
                    _render_edit_mode(st, node, llm_item, key_prefix=pfx, trend_tags=tags_list)


def collect_trend_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across trend proposals.

    Args:
        artifact: The full review artifact dict.

    Returns:
        List of unique approved new tag strings.
    """
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("industry_trends") or []:
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
collect_trend_approved_new_tags = collect_trend_new_tags
