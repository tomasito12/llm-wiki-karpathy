"""Streamlit rendering for tool proposals (proposal-level review)."""

from __future__ import annotations

import logging
from typing import Any

from src.ingest_review.dashboard_ui import (
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_similar_tags_warning,
)
from src.ingest_review.schema import TOOL_REVIEWABLE_LIST_KEYS, TOOL_REVIEWABLE_SCALAR_KEYS

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")
FIELD_STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

VALUE_LEVEL_ORDER = {"high": 0, "medium": 1, "low": 2}

TOOL_FIELD_LABELS: dict[str, str] = {
    "name": "Tool name",
    "short_description": "Short description",
    "operational_relevance": "Operational relevance",
    "strengths": "Strengths",
    "weaknesses_limitations": "Weaknesses / limitations",
    "maturity_signals": "Maturity / adoption signals",
    "core_capabilities": "Core capabilities",
    "integration_ecosystem": "Integration ecosystem",
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
    name = llm_item.get("name") or f"Tool #{idx + 1}"
    conf = float(llm_item.get("confidence") or 0)
    status = str(node.get("proposal_status") or "pending")

    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    st.markdown(f"**[{value_level}] {name}** — evidence: _{ev_lbl}_ — confidence: {conf:.0%}")

    description = str(llm_item.get("short_description") or "")
    if description:
        st.text(description[:2000] + ("\u2026" if len(description) > 2000 else ""))

    proposed_types = llm_item.get("proposed_types") or []
    if proposed_types:
        primary = str(proposed_types[0])
        cap = f"Types: `{primary}` (primary)"
        if len(proposed_types) > 1:
            cap += f" · `{proposed_types[1]}` (secondary)"
        if len(proposed_types) > 2:
            cap += f" +{len(proposed_types) - 2} more"
        st.caption(cap)

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


def _render_type_panel(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    tool_types: list[str],
    *,
    key_prefix: str,
) -> None:
    """Render the tool types editing panel (types system, not tags)."""
    types_node = node.setdefault(
        "types",
        {
            "approved_types": [],
            "proposed_new_type": None,
            "approved_new_type": False,
        },
    )
    current_approved = types_node.get("approved_types") or []
    proposed = llm_item.get("proposed_types") or []
    default_sel = [t for t in (current_approved or proposed) if t in tool_types]
    if tool_types:
        chosen = st.multiselect(
            "Approved types (from registry) — first = primary category, second = adjacent role",
            options=tool_types,
            default=default_sel,
            key=f"{key_prefix}_types_select",
        )
    else:
        st.caption("Tool type registry is empty.")
        chosen = []
    types_node["approved_types"] = chosen

    llm_new_type = llm_item.get("proposed_new_type") or ""
    existing_proposed = types_node.get("proposed_new_type") or llm_new_type
    if existing_proposed:
        render_similar_tags_warning(
            st, str(existing_proposed), tool_types, key_prefix=f"{key_prefix}_type"
        )
        st.info(f"LLM proposed new type: **{existing_proposed}**")
        approved = st.checkbox(
            "Approve this new type",
            value=bool(types_node.get("approved_new_type")),
            key=f"{key_prefix}_new_type_approve",
        )
        types_node["proposed_new_type"] = existing_proposed
        types_node["approved_new_type"] = approved
    else:
        types_node["proposed_new_type"] = None
        types_node["approved_new_type"] = False

    extra = st.text_input(
        "Manually add types (comma-separated)",
        value=", ".join(types_node.get("reviewer_types_added") or []),
        key=f"{key_prefix}_types_extra",
    )
    types_node["reviewer_types_added"] = [x.strip() for x in extra.split(",") if x.strip()]


def _render_edit_mode(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
    tool_types: list[str],
) -> None:
    """Render the full edit expander with per-field review controls and type editing."""
    sections = node.setdefault("sections", {})

    for sk in TOOL_REVIEWABLE_SCALAR_KEYS:
        label = TOOL_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
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

    for lk in TOOL_REVIEWABLE_LIST_KEYS:
        label = TOOL_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
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

    related = llm_item.get("related_tools") or []
    if related:
        st.caption(f"Related tools: {', '.join(str(r) for r in related)}")

    st.markdown("#### Tool types")
    _render_type_panel(st, node, llm_item, tool_types, key_prefix=key_prefix)

    render_proposal_evidence_type_editor(st, llm_item, key_prefix=key_prefix)

    node["notes"] = st.text_input(
        "Proposal notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_notes",
    )

    with st.expander("Raw JSON (debug)", expanded=False):
        st.json(llm_item)


def render_tool_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    tool_types: list[str] | None = None,
) -> None:
    """Render proposal-level review for all tool proposals.

    Args:
        st: Streamlit module reference.
        artifact: The full review artifact dict (mutated in place).
        key_prefix: Unique Streamlit key prefix for this render pass.
        tool_types: Optional type registry list.
    """
    types_list = tool_types or []
    review = artifact.setdefault("review", {})
    tool_nodes = review.setdefault("tools", [])
    st.subheader("Tools")

    if not tool_nodes:
        st.caption("No tool proposals.")
        return

    sorted_nodes = sorted(tool_nodes, key=_sort_key)

    high_medium = [n for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") != "low"]
    low = [n for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") == "low"]

    for i, node in enumerate(high_medium):
        llm_item = node.get("llm_item") or {}
        value_level = str(llm_item.get("value_level") or "medium")
        name = llm_item.get("name") or f"Tool #{i + 1}"
        pfx = f"{key_prefix}_tl{i}"

        auto_expand = value_level == "high"
        with st.expander(f"Tool: {name}", expanded=auto_expand):
            _render_compact_card(st, node, llm_item, i, key_prefix=pfx)
            editing = st.session_state.get(f"{pfx}_act_editing", False)
            if editing:
                _render_edit_mode(st, node, llm_item, key_prefix=pfx, tool_types=types_list)

    if low:
        with st.expander(f"Low-value items ({len(low)})", expanded=False):
            for j, node in enumerate(low):
                llm_item = node.get("llm_item") or {}
                name = llm_item.get("name") or f"Low tool #{j + 1}"
                pfx = f"{key_prefix}_tl_low{j}"
                st.markdown("---")
                _render_compact_card(st, node, llm_item, j, key_prefix=pfx)
                editing = st.session_state.get(f"{pfx}_act_editing", False)
                if editing:
                    _render_edit_mode(st, node, llm_item, key_prefix=pfx, tool_types=types_list)


def collect_tool_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return empty list — tools use the types system, not tags.

    Args:
        artifact: The full review artifact dict.

    Returns:
        Always an empty list.
    """
    return []


def collect_tool_new_types(artifact: dict[str, Any]) -> list[str]:
    """Return all approved new types + manually added types across tool proposals.

    Args:
        artifact: The full review artifact dict.

    Returns:
        List of unique approved type strings.
    """
    review = artifact.get("review") or {}
    types: list[str] = []
    for node in review.get("tools") or []:
        if not isinstance(node, dict):
            continue
        types_node = node.get("types") or {}
        if types_node.get("approved_new_type") and types_node.get("proposed_new_type"):
            t = str(types_node["proposed_new_type"]).strip()
            if t and t not in types:
                types.append(t)
        for t in types_node.get("reviewer_types_added") or []:
            if t and t not in types:
                types.append(t)
    return types


# Backwards-compatible alias
collect_tool_approved_new_types = collect_tool_new_types
