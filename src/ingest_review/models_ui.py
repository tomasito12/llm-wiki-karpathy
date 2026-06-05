"""Streamlit rendering for foundation model proposals (two-column read/edit layout)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    format_proposal_meta_subtitle,
    render_proposal_evidence_type_editor,
)
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_registry_types_ui_to_node,
    apply_tag_ui_to_node,
    collect_approved_new_tags_from_review,
    effective_registry_types,
    registry_types_ui_from_session,
    render_domain_tag_section,
    render_registry_types_section,
)
from src.ingest_review.fast_review_ui import (
    CollapsedFieldSpec,
    read_fast_card_field_values,
    register_card_autosave,
    render_collapsed_fields,
    render_context_expander,
    render_fast_card_header,
    render_fast_card_save_row,
    render_inline_regenerate_title_controls,
    render_readonly_context_hint,
    render_source_evidence_expander,
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
from src.ingest_review.schema import MODEL_REVIEWABLE_LIST_KEYS, MODEL_REVIEWABLE_SCALAR_KEYS
from src.ingest_review.tags import normalize_tag

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
    "operational_profile": "Operational profile",
    "deployment_implications": "Deployment implications",
    "weaknesses_limitations": "Weaknesses / limitations",
    "service_automation_implications": "Service automation implications",
    "maturity_signals": "Maturity / adoption signals",
    "pricing_inference_implications": "Pricing / inference implications",
    "core_capabilities": "Core capabilities",
    "benchmark_observations": "Benchmark observations",
    "comparative_observations": "Comparative observations",
}

MODEL_TALL_SCALAR_KEYS: frozenset[str] = frozenset(
    {
        "operational_profile",
        "deployment_implications",
        "weaknesses_limitations",
        "service_automation_implications",
    }
)

MODEL_MORE_SCALAR_SPECS: tuple[CollapsedFieldSpec, ...] = (
    CollapsedFieldSpec("provider", "Provider"),
    CollapsedFieldSpec("deployment_implications", "Deployment implications", tall=True),
    CollapsedFieldSpec("weaknesses_limitations", "Weaknesses / limitations", tall=True),
    CollapsedFieldSpec(
        "service_automation_implications",
        "Service automation implications",
        tall=True,
    ),
    CollapsedFieldSpec("maturity_signals", "Maturity / adoption signals"),
    CollapsedFieldSpec("pricing_inference_implications", "Pricing / inference implications"),
)

MODEL_MORE_LIST_SPECS: tuple[CollapsedFieldSpec, ...] = (
    CollapsedFieldSpec(
        "core_capabilities",
        "Core capabilities",
        is_list=True,
        help_text="One bullet per line.",
    ),
    CollapsedFieldSpec(
        "benchmark_observations",
        "Benchmark observations",
        is_list=True,
        help_text="One bullet per line.",
    ),
    CollapsedFieldSpec(
        "comparative_observations",
        "Comparative observations",
        is_list=True,
        help_text="One bullet per line.",
    ),
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


def format_model_readonly_markdown(
    node: dict[str, Any],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Format one model proposal as markdown for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    name = effective_model_scalar(llm_item, sections, "model_name") or "Untitled model"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}

    lines = [
        f"## {name}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    provider = effective_model_scalar(llm_item, sections, "provider")
    if provider:
        lines.extend(["**Provider**", "", provider, ""])
    profile = effective_model_scalar(llm_item, sections, "operational_profile")
    if profile:
        lines.extend(["**Operational profile**", "", profile, ""])
    for sk in MODEL_REVIEWABLE_SCALAR_KEYS:
        if sk in ("model_name", "provider", "operational_profile"):
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
    types_node = node.get("types") or {}
    display_types = effective_registry_types(llm_item, types_node)
    if display_types:
        lines.extend(["**Types**", "", ", ".join(f"`{t}`" for t in display_types), ""])
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    return "\n".join(lines).rstrip()


def build_readonly_models_markdown(
    sorted_nodes: list[dict[str, Any]],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
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
        parts.append(format_model_readonly_markdown(node, artifact=artifact))
    return "\n\n---\n\n".join(parts)


def _model_expander_label(node: dict[str, Any], index: int) -> str:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    name = effective_model_scalar(llm_item, sections, "model_name") or f"Model {index + 1}"
    badge = VALUE_LEVEL_BADGES.get(_value_level(node), "Medium")
    return build_proposal_expander_label(node, name, badge=badge)


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


def _persist_model_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    *,
    type_ui: dict[str, Any],
    type_allow: set[str],
    tag_ui: dict[str, Any],
    tag_allow: set[str],
    key_prefix: str,
) -> None:
    """Apply widget edits, types, tags, and persist the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    merged = read_fast_card_field_values(
        key_prefix,
        title_keys=("model_name",),
        context_keys=("operational_profile",),
        more_scalar_keys=tuple(s.key for s in MODEL_MORE_SCALAR_SPECS if not s.is_list),
        more_list_keys=MODEL_REVIEWABLE_LIST_KEYS,
        field_values=field_values,
    )
    scalar_values = {sk: merged[sk] for sk in MODEL_REVIEWABLE_SCALAR_KEYS if sk in merged}
    list_raw = {lk: merged[lk] for lk in MODEL_REVIEWABLE_LIST_KEYS if lk in merged}
    apply_model_proposal_edits(node, scalar_values, list_raw)
    llm_item = node.setdefault("llm_item", {})
    fresh_type_ui = registry_types_ui_from_session(key_prefix, type_ui)
    apply_registry_types_ui_to_node(
        node,
        llm_item,
        fresh_type_ui,
        type_allow,
        key_prefix=key_prefix,
    )
    apply_tag_ui_to_node(node, llm_item, tag_ui, tag_allow, key_prefix=key_prefix)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    sections = node.get("sections") or {}
    label = (
        merged.get("model_name")
        or effective_model_scalar(llm_item, sections, "model_name")
        or "model"
    )
    set_proposal_save_message(key_prefix, f"Saved **{label}**.")


def _render_model_edit_box(
    st: Any,
    node: dict[str, Any],
    model_types: list[str],
    model_tags: list[str],
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    model: str = "",
    prompt_version: str = "",
    autosave_registry_key: str = "",
) -> None:
    """Fast-review card for one model proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    name = effective_model_scalar(llm_item, sections, "model_name") or "Untitled model"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    proposal_id = str(node.get("proposal_id") or "")
    field_values: dict[str, str] = {}

    with st.container(border=True):
        render_fast_card_header(
            st,
            node,
            badge=badge,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="foundation_models",
        )
        render_proposal_regen_meta_caption(st, node, "Model")

        field_values["model_name"] = st.text_area(
            "Model name",
            value=effective_model_scalar(llm_item, sections, "model_name"),
            height=72,
            key=f"{key_prefix}_edit_model_name",
        )
        render_readonly_context_hint(
            st,
            label="Operational profile",
            value=effective_model_scalar(llm_item, sections, "operational_profile"),
        )

        render_inline_regenerate_title_controls(
            st,
            entity_key="model",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=name,
            title_label="New model name",
        )

        type_allow = {normalize_tag(str(t)) for t in model_types if str(t).strip()}
        type_ui = render_registry_types_section(
            st,
            node,
            model_types,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="foundation_models",
            label_widget_key=f"{key_prefix}_edit_model_name",
            summary_widget_key=f"{key_prefix}_ctx_operational_profile",
            llm_fallback_label_key="model_name",
            llm_fallback_summary_key="operational_profile",
            section_title="Model types (archetype)",
        )
        tag_allow = {normalize_tag(str(t)) for t in model_tags if str(t).strip()}
        tag_ui = render_domain_tag_section(
            st,
            node,
            model_tags,
            key_prefix=f"{key_prefix}_retrieval",
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="foundation_models",
            label_widget_key=f"{key_prefix}_edit_model_name",
            summary_widget_key=f"{key_prefix}_ctx_operational_profile",
            llm_fallback_label_key="model_name",
            llm_fallback_summary_key="operational_profile",
            section_title="Retrieval tags",
        )

        def _save() -> None:
            _persist_model_proposal_from_widgets(
                node,
                artifact_path,
                field_values,
                type_ui=type_ui,
                type_allow=type_allow,
                tag_ui=tag_ui,
                tag_allow=tag_allow,
                key_prefix=key_prefix,
            )

        render_fast_card_save_row(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="foundation_models",
            on_save_callback=_save,
        )

        render_context_expander(
            st,
            label="Operational profile / context",
            field_key="operational_profile",
            field_label="Operational profile",
            value=effective_model_scalar(llm_item, sections, "operational_profile"),
            widget_key=f"{key_prefix}_ctx_operational_profile",
            field_values=field_values,
        )

        def _more_model_fields() -> None:
            render_proposal_evidence_type_editor(st, llm_item, artifact, key_prefix=key_prefix)
            related = llm_item.get("related_models") or []
            if related:
                st.caption(f"Related models: {', '.join(str(r) for r in related)}")

        render_collapsed_fields(
            st,
            specs=[*MODEL_MORE_SCALAR_SPECS, *MODEL_MORE_LIST_SPECS],
            get_value=lambda li, sec, k: (
                model_list_field_value(li, sec, k)
                if k in MODEL_REVIEWABLE_LIST_KEYS
                else effective_model_scalar(li, sec, k)
            ),
            llm_item=llm_item,
            sections=sections,
            key_prefix=key_prefix,
            field_values=field_values,
            extra_content=_more_model_fields,
        )
        render_source_evidence_expander(st, llm_item)
        register_card_autosave(autosave_registry_key, node, _save)


def render_model_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    artifact_path: Path,
    model_types: list[str] | None = None,
    model_tags: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column model review: read-only catalog left, edit panel right."""
    types_list = model_types or []
    tags_list = model_tags or []
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = list(tags_list)
    st.subheader("Foundation models")
    sorted_nodes = _prepare_model_nodes(artifact)
    if not sorted_nodes:
        st.caption("No model proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    regen_msg = pop_proposal_regen_msg("model")
    if regen_msg:
        st.success(regen_msg)

    def _readonly_md(node: dict[str, Any]) -> str:
        if len(sorted_nodes) == 1:
            return build_readonly_models_markdown([node], artifact=artifact)
        return format_model_readonly_markdown(node, artifact=artifact)

    def _render_edit(node: dict[str, Any], index: int) -> None:
        pid = str(node.get("proposal_id") or f"idx{index}")
        pfx = proposal_edit_key_prefix(
            key_prefix, pid, "mdl", regen_count=regen_count_from_node(node)
        )
        _render_model_edit_box(
            st,
            node,
            types_list,
            tags_list,
            artifact,
            key_prefix=pfx,
            source_id=source_id,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            autosave_registry_key=key_prefix,
        )

    render_two_column_proposal_review(
        st,
        sorted_nodes,
        key_prefix=key_prefix,
        empty_readonly_text="*(No model proposals.)*",
        label_for_node=_model_expander_label,
        readonly_markdown_for_node=_readonly_md,
        render_edit_for_node=_render_edit,
    )


def collect_model_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new retrieval tags across model proposals."""
    return collect_approved_new_tags_from_review(artifact, "foundation_models")


def collect_model_new_types(artifact: dict[str, Any]) -> list[str]:
    """Return approved new model types for YAML export."""
    from src.ingest_review.tags import normalize_tag

    review = artifact.get("review") or {}
    types: list[str] = []
    for node in review.get("foundation_models") or []:
        if not isinstance(node, dict):
            continue
        types_node = node.get("types") or {}
        for raw in types_node.get("approved_new_types") or []:
            t = normalize_tag(str(raw))
            if t and t not in types:
                types.append(t)
        if types_node.get("approved_new_type") and types_node.get("proposed_new_type"):
            t = normalize_tag(str(types_node["proposed_new_type"]))
            if t and t not in types:
                types.append(t)
    return types


collect_model_approved_new_tags = collect_model_new_types
