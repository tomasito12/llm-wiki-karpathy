"""Streamlit rendering for tool proposals (two-column read/edit layout, glossary-style)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    format_proposal_meta_subtitle,
    render_proposal_evidence_type_editor,
    render_similar_tags_warning,
)
from src.ingest_review.domain_tag_ui import (
    effective_registry_types,
    init_widget_session_value,
    queue_widget_session_resync,
)
from src.ingest_review.proposal_columns_ui import (
    build_proposal_expander_label,
    render_two_column_proposal_review,
)
from src.ingest_review.proposal_decision_ui import (
    proposal_status_label,
    render_proposal_decision_bar,
    set_proposal_save_message,
)
from src.ingest_review.proposal_regen_ui import (
    pop_proposal_regen_msg,
    proposal_edit_key_prefix,
    regen_count_from_node,
    render_proposal_regen_meta_caption,
    render_regenerate_with_new_title_controls,
)
from src.ingest_review.schema import TOOL_REVIEWABLE_LIST_KEYS, TOOL_REVIEWABLE_SCALAR_KEYS
from src.ingest_review.tags import normalize_tag_list

VALUE_LEVEL_ORDER = {"high": 0, "medium": 1, "low": 2}

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


def _section_scalar(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def _section_list(sections: dict[str, Any], list_key: str) -> dict[str, Any]:
    node = sections.get(list_key)
    return node if isinstance(node, dict) else {}


def effective_tool_scalar(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Return reviewer-final scalar text, else the LLM draft."""
    node = _section_scalar(sections, section_key)
    final = node.get("final_text")
    if isinstance(final, str) and final.strip():
        return final.strip()
    return str(llm_item.get(section_key) or "").strip()


def tool_scalar_field_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default text_area value for one scalar (matches glossary ``glossary_field_edit_value``)."""
    return effective_tool_scalar(llm_item, sections, section_key)


def apply_tool_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one scalar edit; infer section status from LLM draft (glossary-style)."""
    text = raw_text.strip()
    llm_text = str(llm_item.get(section_key) or "").strip()
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    if text == llm_text:
        node["status"] = "approved"
        node["final_text"] = None
        if section_key == "name":
            llm_item["name"] = text
    else:
        node["status"] = "modified"
        node["final_text"] = text


def tool_list_field_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Multiline text for list fields (one item per line)."""
    llm_list = llm_item.get(list_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    sec = _section_list(sections, list_key)
    if not sec.get("llm_list"):
        base_list = list(llm_list)
    else:
        base_list = list(sec["llm_list"])
    lines_source = sec.get("final_list")
    if isinstance(lines_source, list):
        return "\n".join(str(x) for x in lines_source)
    return "\n".join(str(x) for x in base_list)


def effective_tool_list_items(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> list[str]:
    """Return the list to show in read-only markdown."""
    raw = tool_list_field_value(llm_item, sections, list_key).splitlines()
    return [ln.strip() for ln in raw if ln.strip()]


def apply_tool_list_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    list_key: str,
    raw_lines: list[str],
) -> None:
    """Persist list edits from split textarea lines."""
    llm_list = llm_item.get(list_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    normalized_llm = [str(x).strip() for x in llm_list if str(x).strip()]
    normalized_new = [ln.strip() for ln in raw_lines if ln.strip()]
    sec = sections.setdefault(
        list_key,
        {
            "status": "pending",
            "final_list": None,
            "notes": None,
            "llm_list": list(llm_list),
        },
    )
    sec["llm_list"] = list(llm_list)
    if normalized_new == normalized_llm:
        sec["status"] = "approved"
        sec["final_list"] = None
    else:
        sec["status"] = "modified"
        sec["final_list"] = normalized_new


def apply_tool_proposal_edits(
    node: dict[str, Any],
    scalar_values: dict[str, str],
    list_raw: dict[str, str],
) -> None:
    """Apply all editable tool fields from save callback inputs."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in TOOL_REVIEWABLE_SCALAR_KEYS:
        if sk in scalar_values:
            apply_tool_scalar_edit(sections, llm_item, sk, scalar_values[sk])
    for lk in TOOL_REVIEWABLE_LIST_KEYS:
        if lk in list_raw:
            lines = list_raw[lk].splitlines()
            apply_tool_list_edit(sections, llm_item, lk, lines)


def _sort_key(node: dict[str, Any]) -> tuple[int, float]:
    """Sort proposals: high value first, then descending confidence."""
    llm = node.get("llm_item") or {}
    level = str(llm.get("value_level") or "medium")
    conf = float(llm.get("confidence") or 0)
    return (VALUE_LEVEL_ORDER.get(level, 1), -conf)


def _value_level(node: dict[str, Any]) -> str:
    llm_item = node.get("llm_item") or {}
    return str(llm_item.get("value_level") or "medium")


def format_tool_readonly_markdown(
    node: dict[str, Any],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Format one tool proposal as markdown for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    name = effective_tool_scalar(llm_item, sections, "name") or "Untitled tool"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}

    description = effective_tool_scalar(llm_item, sections, "short_description")
    op_rel = effective_tool_scalar(llm_item, sections, "operational_relevance")
    strengths = effective_tool_scalar(llm_item, sections, "strengths")
    weaknesses = effective_tool_scalar(llm_item, sections, "weaknesses_limitations")
    maturity = effective_tool_scalar(llm_item, sections, "maturity_signals")
    snippet = str(llm_item.get("supporting_snippet") or "").strip()

    types_node = node.get("types") or {}
    display_types = effective_registry_types(llm_item, types_node)

    related = llm_item.get("related_tools") or []
    if not isinstance(related, list):
        related = []

    lines = [
        f"## {name}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    if display_types:
        type_bits = ", ".join(f"`{t}`" for t in display_types if str(t).strip())
        if type_bits:
            lines.extend(["**Types**", "", type_bits, ""])
    if description:
        excerpt = description[:2000] + ("\u2026" if len(description) > 2000 else "")
        lines.extend(["**Summary**", "", excerpt, ""])
    if op_rel:
        orex = op_rel[:1200] + ("\u2026" if len(op_rel) > 1200 else "")
        lines.extend(["**Operational relevance**", "", orex, ""])
    if strengths:
        sex = strengths[:1200] + ("\u2026" if len(strengths) > 1200 else "")
        lines.extend(["**Strengths**", "", sex, ""])
    if weaknesses:
        wex = weaknesses[:1200] + ("\u2026" if len(weaknesses) > 1200 else "")
        lines.extend(["**Weaknesses / limitations**", "", wex, ""])
    if maturity:
        mex = maturity[:1200] + ("\u2026" if len(maturity) > 1200 else "")
        lines.extend(["**Maturity / adoption**", "", mex, ""])

    for lk, label_key in (
        ("core_capabilities", "**Core capabilities**"),
        ("integration_ecosystem", "**Integration ecosystem**"),
    ):
        items = effective_tool_list_items(llm_item, sections, lk)
        if items:
            lines.extend([label_key, "", "- " + "\n- ".join(items), ""])

    if snippet:
        ex = snippet[:2000] + ("\u2026" if len(snippet) > 2000 else "")
        lines.extend(["> " + ex.replace("\n", "\n> "), ""])
    if related:
        lines.extend([f"*Related tools: {', '.join(str(r) for r in related)}*", ""])

    return "\n".join(lines).rstrip()


def build_readonly_tools_markdown(
    sorted_nodes: list[dict[str, Any]],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Concatenate all tool proposals for uninterrupted read-only display."""
    if not sorted_nodes:
        return "*(No tool proposals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_tool_readonly_markdown(node, artifact=artifact))
    return "\n\n---\n\n".join(parts)


def _tool_expander_label(node: dict[str, Any], index: int) -> str:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    name = effective_tool_scalar(llm_item, sections, "name") or f"Tool {index + 1}"
    badge = VALUE_LEVEL_BADGES.get(_value_level(node), "Medium")
    return build_proposal_expander_label(node, name, badge=badge)


def _prepare_tool_nodes(
    artifact: dict[str, Any],
) -> list[dict[str, Any]]:
    """Ensure review tool nodes have ``llm_item`` and ``proposal_id``; return sorted list."""
    review = artifact.setdefault("review", {})
    tool_nodes = review.setdefault("tools", [])
    llm_items = artifact.get("llm_output", {}).get("tools") or []
    for i, node in enumerate(tool_nodes):
        if not isinstance(node, dict):
            continue
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    valid = [n for n in tool_nodes if isinstance(n, dict)]
    return sorted(valid, key=_sort_key)


def _find_tool_node(artifact: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    for node in (artifact.get("review") or {}).get("tools") or []:
        if isinstance(node, dict) and node.get("proposal_id") == proposal_id:
            return node
    return None


def _on_save_tool_proposal(
    proposal_id: str,
    key_prefix: str,
    artifact_path: Path,
) -> None:
    """Streamlit on_click: apply field edits and persist artifact immediately."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    node = _find_tool_node(artifact, proposal_id)
    if not node:
        return
    scalar_values = {
        sk: str(streamlit_runtime.session_state.get(f"{key_prefix}_edit_{sk}", ""))
        for sk in TOOL_REVIEWABLE_SCALAR_KEYS
    }
    list_raw = {
        lk: str(streamlit_runtime.session_state.get(f"{key_prefix}_edit_{lk}", ""))
        for lk in TOOL_REVIEWABLE_LIST_KEYS
    }
    apply_tool_proposal_edits(node, scalar_values, list_raw)
    types_node = node.get("types") or {}
    extra_key = f"{key_prefix}_types_extra"
    queue_widget_session_resync(
        extra_key,
        ", ".join(normalize_tag_list(types_node.get("reviewer_types_added") or [], cap=0)),
    )
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    label = effective_tool_scalar(llm_item, sections, "name") or "proposal"
    set_proposal_save_message(key_prefix, f"Saved **{label}**.")


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
    registry_chosen = normalize_tag_list(chosen, cap=0)

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

    extra_key = f"{key_prefix}_types_extra"
    stored_extra = ", ".join(
        normalize_tag_list(types_node.get("reviewer_types_added") or [], cap=0)
    )
    init_widget_session_value(extra_key, stored_extra)
    extra = st.text_input(
        "Manually add types (comma-separated)",
        key=extra_key,
        help="Kebab-case slugs merged with registry selections; saved with “Save edit & approve”.",
    )
    manual_types = normalize_tag_list(
        [x.strip() for x in extra.split(",") if x.strip()],
        cap=0,
    )
    types_node["reviewer_types_added"] = manual_types
    merged_types: list[str] = []
    for t in registry_chosen + manual_types:
        if t and t not in merged_types:
            merged_types.append(t)
    types_node["approved_types"] = merged_types


def _render_tool_edit_box(
    st: Any,
    node: dict[str, Any],
    tool_types: list[str],
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
) -> None:
    """One bordered edit box per tool proposal (glossary-style)."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    name = tool_scalar_field_value(llm_item, sections, "name") or "Untitled tool"
    value_level = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(value_level, "Medium")
    proposal_status = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{name}** · {badge} · **{proposal_status}**")
        render_proposal_regen_meta_caption(st, node, "Tool")

        for sk in TOOL_REVIEWABLE_SCALAR_KEYS:
            label = TOOL_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            tall = sk in (
                "short_description",
                "operational_relevance",
                "strengths",
                "weaknesses_limitations",
            )
            st.text_area(
                label,
                value=tool_scalar_field_value(llm_item, sections, sk),
                height=120 if tall else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in TOOL_REVIEWABLE_LIST_KEYS:
            label = TOOL_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            st.text_area(
                f"{label} (one per line)",
                value=tool_list_field_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
            )

        snippet = str(llm_item.get("supporting_snippet") or "").strip()
        if snippet:
            with st.expander("Source evidence (read-only)", expanded=False):
                st.text(snippet[:4000] + ("\u2026" if len(snippet) > 4000 else ""))

        related = llm_item.get("related_tools") or []
        if related:
            st.caption(f"Related tools: {', '.join(str(r) for r in related)}")

        st.markdown("#### Tool types")
        _render_type_panel(st, node, llm_item, tool_types, key_prefix=key_prefix)

        render_proposal_evidence_type_editor(st, llm_item, artifact, key_prefix=key_prefix)

        with st.expander("Raw JSON (debug)", expanded=False):
            st.json(llm_item)

        proposal_id = str(node.get("proposal_id") or "")
        render_regenerate_with_new_title_controls(
            st,
            entity_key="tool",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=name,
            title_label="New tool name",
        )

        def _save() -> None:
            _on_save_tool_proposal(str(node.get("proposal_id") or ""), key_prefix, artifact_path)

        render_proposal_decision_bar(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="tools",
            on_save_callback=_save,
        )


def render_tool_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    artifact_path: Path,
    tool_types: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column tool review: read-only catalog left, per-tool edit boxes right."""
    types_list = tool_types or []
    st.subheader("Tools")

    sorted_nodes = _prepare_tool_nodes(artifact)
    if not sorted_nodes:
        st.caption("No tool proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    regen_msg = pop_proposal_regen_msg("tool")
    if regen_msg:
        st.success(regen_msg)

    def _readonly_md(node: dict[str, Any]) -> str:
        if len(sorted_nodes) == 1:
            return build_readonly_tools_markdown([node], artifact=artifact)
        return format_tool_readonly_markdown(node, artifact=artifact)

    def _render_edit(node: dict[str, Any], index: int) -> None:
        pid = str(node.get("proposal_id") or f"idx{index}")
        pfx = proposal_edit_key_prefix(
            key_prefix, pid, "tool", regen_count=regen_count_from_node(node)
        )
        _render_tool_edit_box(
            st,
            node,
            types_list,
            artifact,
            key_prefix=pfx,
            source_id=source_id,
            artifact_path=artifact_path,
        )

    render_two_column_proposal_review(
        st,
        sorted_nodes,
        key_prefix=key_prefix,
        empty_readonly_text="*(No tool proposals.)*",
        label_for_node=_tool_expander_label,
        readonly_markdown_for_node=_readonly_md,
        render_edit_for_node=_render_edit,
    )


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
