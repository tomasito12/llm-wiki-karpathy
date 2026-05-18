"""Streamlit rendering for implementation-study proposals (two-column read/edit)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import format_proposal_meta_subtitle
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_tag_ui_to_node,
    effective_readonly_domain_tags,
    render_domain_tag_section,
)
from src.ingest_review.impl_study_gate import (
    format_impl_study_evidence_caption,
    impl_study_likely_misclassified,
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
    render_reclassify_to_section_controls,
    render_regenerate_with_new_title_controls,
)
from src.ingest_review.schema import (
    IMPL_STUDY_REVIEWABLE_LIST_KEYS,
    IMPL_STUDY_REVIEWABLE_SCALAR_KEYS,
)
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

IMPL_STUDY_SECTION_LABELS: dict[str, str] = {
    "title": "Title",
    "company": "Company / organization",
    "industry": "Industry / domain",
    "overview": "Overview",
    "what_was_implemented": "What was implemented?",
    "business_objective": "Business objective",
    "technical_approach": "Technical approach",
    "deployment_context": "Deployment context",
    "outcome_status": "Outcome / current status",
    "success_or_failure_factors": "Why it succeeded or struggled",
    "operational_constraints": "Operational constraints",
    "ai_model_observations": "AI / model observations",
    "implications_for_service_automation": "Implications for service automation",
    "strategic_signals": "Strategic signals",
    "key_lessons": "Key lessons",
    "open_questions": "Open questions",
}

IMPL_SCALAR_BEFORE_TAGS: tuple[str, ...] = ("title", "company", "industry", "overview")
IMPL_SCALAR_MID: tuple[str, ...] = (
    "what_was_implemented",
    "business_objective",
    "technical_approach",
    "deployment_context",
    "outcome_status",
)
IMPL_SCALAR_AFTER_TAGS: tuple[str, ...] = (
    "success_or_failure_factors",
    "operational_constraints",
    "ai_model_observations",
    "implications_for_service_automation",
    "strategic_signals",
)
IMPL_TALL_SCALAR_KEYS: frozenset[str] = frozenset(
    {
        "overview",
        "what_was_implemented",
        "technical_approach",
        "implications_for_service_automation",
    }
)


def _sort_key(node: dict[str, Any]) -> tuple[int, int, float]:
    llm = node.get("llm_item") or {}
    vl = str(llm.get("value_level", "medium"))
    conf = float(llm.get("confidence") or 0)
    ignore_rank = 1 if str(llm.get("value_level") or "") == "low" and conf < 0.35 else 0
    return (ignore_rank, VALUE_LEVEL_ORDER.get(vl, 1), -conf)


def _value_level(node: dict[str, Any]) -> str:
    return str((node.get("llm_item") or {}).get("value_level") or "medium")


def _section_node(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_impl_scalar(
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


def effective_impl_list(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> list[str]:
    """Return reviewer-final list or LLM list."""
    sec = _section_node(sections, list_key)
    if str(sec.get("status") or "pending") == "modified" and sec.get("final_list") is not None:
        fl = sec.get("final_list")
        if isinstance(fl, list):
            return [str(x) for x in fl]
    raw = llm_item.get(list_key) or []
    if not isinstance(raw, list):
        return []
    return [str(x) for x in raw]


def apply_impl_scalar_edit(
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


def apply_impl_list_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    list_key: str,
    raw_text: str,
) -> None:
    """Persist list field (one item per line)."""
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    llm_list = llm_item.get(list_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    llm_norm = [str(x) for x in llm_list]
    node = sections.setdefault(
        list_key,
        {"status": "pending", "final_list": None, "notes": None, "llm_list": list(llm_norm)},
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_norm)
    if lines == llm_norm:
        node["status"] = "approved"
        node["final_list"] = None
    else:
        node["status"] = "modified"
        node["final_list"] = lines


def apply_impl_proposal_edits(node: dict[str, Any], field_values: dict[str, str]) -> None:
    """Apply all editable scalar and list fields for one impl-study proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in IMPL_STUDY_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_impl_scalar_edit(sections, llm_item, sk, field_values[sk])
    for lk in IMPL_STUDY_REVIEWABLE_LIST_KEYS:
        if lk in field_values:
            apply_impl_list_edit(sections, llm_item, lk, field_values[lk])


def impl_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one scalar field."""
    return effective_impl_scalar(llm_item, sections, section_key)


def impl_list_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Default textarea value for list fields."""
    return "\n".join(effective_impl_list(llm_item, sections, list_key))


def format_impl_readonly_markdown(
    node: dict[str, Any],
    impl_study_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Single implementation-study card for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = effective_impl_scalar(llm_item, sections, "title") or "Untitled study"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}
    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, impl_study_tags)

    lines = [
        f"## {title}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    company = effective_impl_scalar(llm_item, sections, "company")
    if company:
        lines.extend([f"**Company:** {company}", ""])
    for sk in IMPL_STUDY_REVIEWABLE_SCALAR_KEYS:
        if sk in ("title", "company"):
            continue
        val = effective_impl_scalar(llm_item, sections, sk)
        if val:
            label = IMPL_STUDY_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            lines.extend([f"**{label}**", "", val, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    for lk in IMPL_STUDY_REVIEWABLE_LIST_KEYS:
        items = effective_impl_list(llm_item, sections, lk)
        if items:
            label = IMPL_STUDY_SECTION_LABELS.get(lk, lk.replace("_", " ").title())
            lines.extend([f"**{label}**", ""] + [f"- {p}" for p in items] + [""])
    cap = format_impl_study_evidence_caption(llm_item)
    if cap:
        lines.extend([f"*{cap}*", ""])
    return "\n".join(lines).rstrip()


def build_readonly_impl_studies_markdown(
    sorted_nodes: list[dict[str, Any]],
    impl_study_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Build full read-only column markdown."""
    if not sorted_nodes:
        return "*(No implementation-study proposals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_impl_readonly_markdown(node, impl_study_tags, artifact=artifact))
    return "\n\n---\n\n".join(parts)


def _impl_expander_label(node: dict[str, Any], index: int) -> str:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = effective_impl_scalar(llm_item, sections, "title") or f"Study {index + 1}"
    badge = VALUE_LEVEL_BADGES.get(_value_level(node), "Medium")
    return build_proposal_expander_label(node, title, badge=badge)


def _prepare_impl_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    impl_nodes = review.setdefault("implementation_studies", [])
    llm_items = artifact.get("llm_output", {}).get("implementation_studies") or []
    if not llm_items:
        llm_items = artifact.get("llm_output", {}).get("enterprise_studies") or []
    for i, node in enumerate(impl_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(impl_nodes, key=_sort_key)


def _persist_impl_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    tag_ui: dict[str, Any],
    allow: set[str],
    *,
    key_prefix: str,
) -> None:
    """Apply edits and write the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    apply_impl_proposal_edits(node, field_values)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    title = field_values.get("title") or llm_item.get("title") or "study"
    set_proposal_save_message(key_prefix, f"Saved **{title}**.")


def _render_impl_edit_box(
    st: Any,
    node: dict[str, Any],
    impl_study_tags: list[str],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
) -> None:
    """One bordered edit box per implementation-study proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    title = effective_impl_scalar(llm_item, sections, "title") or "Untitled"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    status_lbl = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{title}** · {badge} · **{status_lbl}**")
        render_proposal_regen_meta_caption(st, node, "Implementation study")
        if impl_study_likely_misclassified(llm_item):
            st.warning(
                "No stated deployment evidence — likely misclassified. "
                "Consider rejecting or routing to topics/how-to."
            )

        field_values: dict[str, str] = {}
        for sk in IMPL_SCALAR_BEFORE_TAGS:
            label = IMPL_STUDY_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=impl_field_edit_value(llm_item, sections, sk),
                height=120 if sk in IMPL_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        tag_ui = render_domain_tag_section(
            st,
            node,
            impl_study_tags,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="implementation_studies",
            label_widget_key=f"{key_prefix}_edit_title",
            summary_widget_key=f"{key_prefix}_edit_overview",
            llm_fallback_label_key="title",
            llm_fallback_summary_key="overview",
        )

        for sk in IMPL_SCALAR_MID + IMPL_SCALAR_AFTER_TAGS:
            label = IMPL_STUDY_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=impl_field_edit_value(llm_item, sections, sk),
                height=120 if sk in IMPL_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in IMPL_STUDY_REVIEWABLE_LIST_KEYS:
            label = IMPL_STUDY_SECTION_LABELS.get(lk, lk.replace("_", " ").title())
            field_values[lk] = st.text_area(
                label,
                value=impl_list_edit_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
                help="One bullet per line.",
            )

        snippets = llm_item.get("evidence_snippets") or []
        if snippets:
            with st.expander(f"Evidence snippets ({len(snippets)})", expanded=False):
                for ev in snippets:
                    if isinstance(ev, dict):
                        st.markdown(f"**{ev.get('claim', '')}**")
                        st.caption(str(ev.get("snippet") or ""))

        proposal_id = str(node.get("proposal_id") or "")
        render_regenerate_with_new_title_controls(
            st,
            entity_key="impl_study",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
            title_label="New study title",
        )
        render_reclassify_to_section_controls(
            st,
            source_entity_key="impl_study",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
        )

        def _save() -> None:
            _persist_impl_proposal_from_widgets(
                node,
                artifact_path,
                field_values,
                tag_ui,
                tag_allow,
                key_prefix=key_prefix,
            )

        render_proposal_decision_bar(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="implementation_studies",
            on_save_callback=_save,
        )


def render_implementation_studies(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    artifact_path: Path,
    impl_study_tags: list[str],
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column implementation-study review."""
    tags_list = list(impl_study_tags or [])
    tag_allow = {normalize_tag(str(t)) for t in tags_list if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = tags_list

    st.subheader("Implementation studies")
    sorted_nodes = _prepare_impl_nodes(artifact)
    if not sorted_nodes:
        st.caption("No implementation-study proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    regen_msg = pop_proposal_regen_msg("impl_study")
    if regen_msg:
        st.success(regen_msg)

    def _readonly_md(node: dict[str, Any]) -> str:
        if len(sorted_nodes) == 1:
            return build_readonly_impl_studies_markdown([node], tags_list, artifact=artifact)
        return format_impl_readonly_markdown(node, tags_list, artifact=artifact)

    def _render_edit(node: dict[str, Any], index: int) -> None:
        pid = str(node.get("proposal_id") or f"idx{index}")
        pfx = proposal_edit_key_prefix(
            key_prefix, pid, "impl", regen_count=regen_count_from_node(node)
        )
        _render_impl_edit_box(
            st,
            node,
            tags_list,
            key_prefix=pfx,
            source_id=source_id,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            tag_allow=tag_allow,
        )

    render_two_column_proposal_review(
        st,
        sorted_nodes,
        key_prefix=key_prefix,
        empty_readonly_text="*(No implementation-study proposals.)*",
        label_for_node=_impl_expander_label,
        readonly_markdown_for_node=_readonly_md,
        render_edit_for_node=_render_edit,
    )


def collect_impl_study_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across implementation-study proposals."""
    from src.ingest_review.domain_tag_ui import collect_approved_new_tags_from_review

    return collect_approved_new_tags_from_review(artifact, "implementation_studies")
