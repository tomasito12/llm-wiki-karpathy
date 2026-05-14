"""Streamlit rendering for tool proposals (per-section review)."""

from __future__ import annotations

import urllib.parse
from typing import Any

from src.ingest_review.artifact import aggregate_impl_study_section_status
from src.ingest_review.schema import TOOL_LIST_KEYS, TOOL_SCALAR_KEYS

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

TOOL_SECTION_LABELS: dict[str, str] = {
    "name": "Tool name",
    "short_description": "Short description",
    "operational_relevance": "Operational relevance",
    "strengths": "Strengths",
    "weaknesses_limitations": "Weaknesses / limitations",
    "maturity_signals": "Maturity / adoption signals",
    "supporting_snippet": "Supporting snippet",
    "core_capabilities": "Core capabilities",
    "integration_ecosystem": "Integration ecosystem",
    "related_tools": "Related tools",
}

TOOL_DISPLAY_ORDER: tuple[str, ...] = (
    *TOOL_SCALAR_KEYS,
    *TOOL_LIST_KEYS,
)


def _status_index(current: str) -> int:
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _render_tool_scalar_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = TOOL_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"#### {label}")
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    st.markdown("**Model draft**")
    tall = section_key in ("operational_relevance", "strengths", "weaknesses_limitations")
    st.text(llm_text[:6000] + ("\u2026" if len(llm_text) > 6000 else ""))
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_tl_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        node["final_text"] = st.text_area(
            f"{label} \u2014 final text",
            value=default,
            height=160 if tall else 100,
            key=f"{key_prefix}_tl_{section_key}_txt",
        )
    elif node["status"] == "approved":
        node["final_text"] = None
    else:
        node["final_text"] = None
    node["notes"] = st.text_input(
        f"{label} \u2014 notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_tl_{section_key}_notes",
    )


def _render_tool_list_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = TOOL_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"#### {label}")
    llm_list = llm_item.get(section_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    node = sections.setdefault(
        section_key,
        {
            "status": "pending",
            "final_list": None,
            "notes": None,
            "llm_list": list(llm_list),
        },
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_list)
    st.markdown("**Model draft (list)**")
    st.json(node["llm_list"])
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_tl_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} \u2014 final list (one item per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_tl_{section_key}_txt",
    )
    lines = [ln.strip() for ln in raw_list.splitlines() if ln.strip()]
    if node["status"] == "modified":
        node["final_list"] = lines
    elif node["status"] == "approved":
        node["final_list"] = None
    else:
        node["final_list"] = None
    node["notes"] = st.text_input(
        f"{label} \u2014 notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_tl_{section_key}_notes",
    )


def _render_tool_type_panel(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    tool_types: list[str],
    *,
    key_prefix: str,
) -> None:
    st.markdown("#### Tool types")
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
            "Approved types (from registry)",
            options=tool_types,
            default=default_sel,
            key=f"{key_prefix}_tl_types_select",
        )
    else:
        st.caption("Tool type registry is empty.")
        chosen = []
    types_node["approved_types"] = chosen

    llm_new_type = llm_item.get("proposed_new_type") or ""
    existing_proposed = types_node.get("proposed_new_type") or llm_new_type
    if existing_proposed:
        st.info(f"LLM proposed new type: **{existing_proposed}**")
        approved = st.checkbox(
            "Approve this new type",
            value=bool(types_node.get("approved_new_type")),
            key=f"{key_prefix}_tl_new_type_approve",
        )
        types_node["proposed_new_type"] = existing_proposed
        types_node["approved_new_type"] = approved
    else:
        types_node["proposed_new_type"] = None
        types_node["approved_new_type"] = False

    extra = st.text_input(
        "Manually add types (comma-separated)",
        value=", ".join(types_node.get("reviewer_types_added") or []),
        key=f"{key_prefix}_tl_types_extra",
    )
    types_node["reviewer_types_added"] = [x.strip() for x in extra.split(",") if x.strip()]


def _render_tool_match_candidates(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
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
            st.warning(f"**{title}** \u2014 match: {kind}, confidence: {conf:.0%}")


def render_tool_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    tool_types: list[str],
) -> None:
    """Render per-section review for all tool proposals."""
    review = artifact.setdefault("review", {})
    tool_nodes = review.setdefault("tools", [])
    llm_items = artifact.get("llm_output", {}).get("tools") or []
    st.subheader("Tools")
    if not tool_nodes and not llm_items:
        st.caption("No tool proposals.")
        return

    for i, node in enumerate(tool_nodes):
        llm_item = node.get("llm_item") or (llm_items[i] if i < len(llm_items) else {})
        name = llm_item.get("name") or f"Tool #{i + 1}"
        sections = node.setdefault("sections", {})
        agg_status = aggregate_impl_study_section_status(sections)
        header = f"Tool #{i + 1}: {name} [{agg_status}]"
        expanded = len(tool_nodes) == 1
        pfx = f"{key_prefix}_tool{i}"
        with st.expander(header, expanded=expanded):
            action = llm_item.get("suggested_action") or "\u2014"
            conf = llm_item.get("confidence", 0)
            st.caption(f"Confidence: {conf:.0%} \u00b7 Action: {action}")
            if name and name != f"Tool #{i + 1}":
                search_url = "https://www.google.com/search?" + urllib.parse.urlencode(
                    {"q": f"{name} AI tool"}
                )
                st.markdown(f'[Google: "{name}"]({search_url})')
            for sk in TOOL_SCALAR_KEYS:
                _render_tool_scalar_section(st, llm_item, sections, section_key=sk, key_prefix=pfx)
            for lk in TOOL_LIST_KEYS:
                _render_tool_list_section(st, llm_item, sections, section_key=lk, key_prefix=pfx)
            st.divider()
            _render_tool_type_panel(st, node, llm_item, tool_types, key_prefix=pfx)
            _render_tool_match_candidates(st, llm_item, key_prefix=pfx)
            node["notes"] = st.text_input(
                "Proposal notes",
                value=str(node.get("notes") or ""),
                key=f"{pfx}_tl_notes",
            )
            with st.expander("Raw JSON (debug)", expanded=False):
                st.json(llm_item)


def collect_tool_approved_new_types(artifact: dict[str, Any]) -> list[str]:
    """Return all approved new types + manually added types across tool proposals."""
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
