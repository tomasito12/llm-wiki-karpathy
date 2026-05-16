"""Streamlit rendering for foundation model proposals (two-column read/edit layout)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_similar_tags_warning,
)
from src.ingest_review.proposal_decision_ui import (
    proposal_status_label,
    render_proposal_decision_bar,
)
from src.ingest_review.proposal_regen_ui import (
    pop_proposal_regen_msg,
    proposal_edit_key_prefix,
    regen_count_from_node,
    render_proposal_regen_meta_caption,
    render_regenerate_with_new_title_controls,
)
from src.ingest_review.schema import MODEL_REVIEWABLE_LIST_KEYS, MODEL_REVIEWABLE_SCALAR_KEYS

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

MODEL_FIELD_LABELS: dict[str, str] = {
    "model_name": "Model name",
    "provider": "Provider",
    "operational_summary": "Operational summary",
    "strengths": "Strengths",
    "weaknesses_limitations": "Weaknesses / limitations",
    "workflow_implications": "Workflow implications",
    "service_automation_implications": "Service automation implications",
    "maturity_signals": "Maturity / adoption signals",
    "pricing_inference_implications": "Pricing / inference implications",
    "core_capabilities": "Core capabilities",
    "benchmark_observations": "Benchmark observations",
    "comparative_observations": "Comparative observations",
}

MODEL_TALL_SCALAR_KEYS: frozenset[str] = frozenset(
    {
        "operational_summary",
        "strengths",
        "weaknesses_limitations",
        "workflow_implications",
        "service_automation_implications",
    }
)


def _section_scalar(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def _section_list(sections: dict[str, Any], list_key: str) -> dict[str, Any]:
    node = sections.get(list_key)
    return node if isinstance(node, dict) else {}


def effective_model_scalar(
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


def apply_model_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one scalar edit; infer section status from LLM draft."""
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


def model_list_field_value(
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


def effective_model_list_items(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> list[str]:
    """Return the list to show in read-only markdown."""
    raw = model_list_field_value(llm_item, sections, list_key).splitlines()
    return [ln.strip() for ln in raw if ln.strip()]


def apply_model_list_edit(
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


def apply_model_proposal_edits(
    node: dict[str, Any],
    scalar_values: dict[str, str],
    list_raw: dict[str, str],
) -> None:
    """Apply all editable model fields from save callback inputs."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in MODEL_REVIEWABLE_SCALAR_KEYS:
        if sk in scalar_values:
            apply_model_scalar_edit(sections, llm_item, sk, scalar_values[sk])
    for lk in MODEL_REVIEWABLE_LIST_KEYS:
        if lk in list_raw:
            lines = list_raw[lk].splitlines()
            apply_model_list_edit(sections, llm_item, lk, lines)


def _sort_key(node: dict[str, Any]) -> tuple[int, float]:
    llm = node.get("llm_item") or {}
    level = str(llm.get("value_level") or "medium")
    conf = float(llm.get("confidence") or 0)
    return (VALUE_LEVEL_ORDER.get(level, 1), -conf)


def _value_level(node: dict[str, Any]) -> str:
    return str((node.get("llm_item") or {}).get("value_level") or "medium")


def format_model_readonly_markdown(node: dict[str, Any]) -> str:
    """Format one model proposal as markdown for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    name = effective_model_scalar(llm_item, sections, "model_name") or "Untitled model"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    proposal_status = proposal_status_label(node)
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    confidence = float(llm_item.get("confidence") or 0.0)

    lines = [
        f"## {name}",
        "",
        f"*{badge} · {proposal_status} · {ev_lbl} · {confidence:.0%}*",
        "",
    ]
    provider = effective_model_scalar(llm_item, sections, "provider")
    if provider:
        lines.extend(["**Provider**", "", provider, ""])
    summary = effective_model_scalar(llm_item, sections, "operational_summary")
    if summary:
        lines.extend(["**Operational summary**", "", summary, ""])
    for sk in MODEL_REVIEWABLE_SCALAR_KEYS:
        if sk in ("model_name", "provider", "operational_summary"):
            continue
        val = effective_model_scalar(llm_item, sections, sk)
        if val:
            label = MODEL_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            lines.extend([f"**{label}**", "", val, ""])
    for lk in MODEL_REVIEWABLE_LIST_KEYS:
        items = effective_model_list_items(llm_item, sections, lk)
        if items:
            label = MODEL_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            lines.extend([f"**{label}**", ""] + [f"- {p}" for p in items] + [""])
    proposed_types = llm_item.get("proposed_types") or []
    if proposed_types:
        lines.extend(["**Proposed types**", "", ", ".join(str(t) for t in proposed_types), ""])
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    return "\n".join(lines).rstrip()


def build_readonly_models_markdown(sorted_nodes: list[dict[str, Any]]) -> str:
    """Build full read-only column markdown for all model proposals."""
    if not sorted_nodes:
        return "*(No model proposals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_model_readonly_markdown(node))
    return "\n\n---\n\n".join(parts)


def _prepare_model_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    model_nodes = review.setdefault("foundation_models", [])
    llm_items = artifact.get("llm_output", {}).get("foundation_models") or []
    for i, node in enumerate(model_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(model_nodes, key=_sort_key)


def _render_type_panel(
    st: Any,
    node: dict[str, Any],
    llm_item: dict[str, Any],
    model_types: list[str],
    *,
    key_prefix: str,
) -> None:
    """Render the model types editing panel (types system, not tags)."""
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
    default_sel = [t for t in (current_approved or proposed) if t in model_types]
    if model_types:
        chosen = st.multiselect(
            "Approved types — first = deployment/openness, second = capability focus",
            options=model_types,
            default=default_sel,
            key=f"{key_prefix}_types_select",
        )
    else:
        st.caption("Model type registry is empty.")
        chosen = []
    types_node["approved_types"] = chosen

    llm_new_type = llm_item.get("proposed_new_type") or ""
    existing_proposed = types_node.get("proposed_new_type") or llm_new_type
    if existing_proposed:
        render_similar_tags_warning(
            st, str(existing_proposed), model_types, key_prefix=f"{key_prefix}_type"
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


def _on_save_model_proposal(
    proposal_id: str,
    key_prefix: str,
    artifact_path: Path,
) -> None:
    """Read widget state and persist model proposal edits."""
    from src.ingest_review.artifact import save_artifact, touch_review_session
    from src.ingest_review.domain_tag_ui import find_review_node

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    node = find_review_node(artifact, proposal_id, "foundation_models")
    if not node:
        return
    scalar_values = {
        sk: str(streamlit_runtime.session_state.get(f"{key_prefix}_edit_{sk}", ""))
        for sk in MODEL_REVIEWABLE_SCALAR_KEYS
    }
    list_raw = {
        lk: str(streamlit_runtime.session_state.get(f"{key_prefix}_edit_{lk}", ""))
        for lk in MODEL_REVIEWABLE_LIST_KEYS
    }
    apply_model_proposal_edits(node, scalar_values, list_raw)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    label = effective_model_scalar(llm_item, sections, "model_name") or "model"
    streamlit_runtime.session_state["_models_save_msg"] = f"Saved **{label}**."


def _render_model_edit_box(
    st: Any,
    node: dict[str, Any],
    model_types: list[str],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
) -> None:
    """One bordered edit box per model proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    name = effective_model_scalar(llm_item, sections, "model_name") or "Untitled model"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    status_lbl = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{name}** · {badge} · **{status_lbl}**")
        render_proposal_regen_meta_caption(st, node, "Model")

        for sk in MODEL_REVIEWABLE_SCALAR_KEYS:
            label = MODEL_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            st.text_area(
                label,
                value=effective_model_scalar(llm_item, sections, sk),
                height=120 if sk in MODEL_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in MODEL_REVIEWABLE_LIST_KEYS:
            label = MODEL_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            st.text_area(
                f"{label} (one per line)",
                value=model_list_field_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
            )

        snippet = str(llm_item.get("supporting_snippet") or "").strip()
        if snippet:
            with st.expander("Source evidence (read-only)", expanded=False):
                st.text(snippet[:4000] + ("…" if len(snippet) > 4000 else ""))

        related = llm_item.get("related_models") or []
        if related:
            st.caption(f"Related models: {', '.join(str(r) for r in related)}")

        st.markdown("#### Model types")
        _render_type_panel(st, node, llm_item, model_types, key_prefix=key_prefix)
        render_proposal_evidence_type_editor(st, llm_item, key_prefix=key_prefix)

        proposal_id = str(node.get("proposal_id") or "")
        render_regenerate_with_new_title_controls(
            st,
            entity_key="model",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=name,
            title_label="New model name",
        )

        def _save() -> None:
            _on_save_model_proposal(str(node.get("proposal_id") or ""), key_prefix, artifact_path)

        render_proposal_decision_bar(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="foundation_models",
            on_save_callback=_save,
        )


def render_model_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    artifact_path: Path,
    model_types: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column model review: read-only catalog left, edit panel right."""
    types_list = model_types or []
    st.subheader("Foundation models")
    sorted_nodes = _prepare_model_nodes(artifact)
    if not sorted_nodes:
        st.caption("No model proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    save_msg = streamlit_runtime.session_state.pop("_models_save_msg", None)
    if save_msg:
        st.success(str(save_msg))
    regen_msg = pop_proposal_regen_msg("model")
    if regen_msg:
        st.success(regen_msg)

    read_col, edit_col = st.columns(2)
    with read_col:
        st.markdown(build_readonly_models_markdown(sorted_nodes))
    with edit_col:
        edit_nodes = sorted_nodes
        if len(sorted_nodes) > 6:
            labels = [
                effective_model_scalar(
                    n.get("llm_item") or {},
                    n.get("sections") or {},
                    "model_name",
                )
                or f"Model {i + 1}"
                for i, n in enumerate(sorted_nodes)
            ]
            pick = st.selectbox(
                "Edit model",
                options=labels,
                key=f"{key_prefix}_model_jump",
            )
            idx = labels.index(pick) if pick in labels else 0
            edit_nodes = [sorted_nodes[idx]]
            st.caption("Showing one edit panel — use the selector to switch models.")

        for i, node in enumerate(edit_nodes):
            pid = str(node.get("proposal_id") or f"idx{i}")
            pfx = proposal_edit_key_prefix(
                key_prefix, pid, "mdl", regen_count=regen_count_from_node(node)
            )
            _render_model_edit_box(
                st,
                node,
                types_list,
                key_prefix=pfx,
                source_id=source_id,
                artifact_path=artifact_path,
            )


def collect_model_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Models use the types system, not tags."""
    return []


def collect_model_new_types(artifact: dict[str, Any]) -> list[str]:
    """Return all approved new types + manually added types across model proposals."""
    review = artifact.get("review") or {}
    types: list[str] = []
    for node in review.get("foundation_models") or []:
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


collect_model_approved_new_tags = collect_model_new_types
