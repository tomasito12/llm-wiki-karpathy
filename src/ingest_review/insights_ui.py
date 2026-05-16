"""Streamlit rendering for interview insight proposals (two-column read/edit)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import human_evidence_type_label
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_tag_ui_to_node,
    effective_readonly_domain_tags,
    render_domain_tag_section,
)
from src.ingest_review.proposal_decision_ui import (
    proposal_status_label,
    render_proposal_decision_bar,
)
from src.ingest_review.schema import INSIGHT_REVIEWABLE_LIST_KEYS, INSIGHT_REVIEWABLE_SCALAR_KEYS
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

INSIGHT_SCALAR_BEFORE_TAGS: tuple[str, ...] = ("insight_title", "insight_type", "summary")
INSIGHT_SCALAR_MID: tuple[str, ...] = (
    "why_it_matters",
    "operational_relevance",
    "service_automation_relevance",
)
INSIGHT_SCALAR_AFTER_TAGS: tuple[str, ...] = (
    "confidence",
    "durability_estimate",
    "wiki_worthiness",
)
INSIGHT_TALL_SCALAR_KEYS: frozenset[str] = frozenset(
    {"summary", "why_it_matters", "operational_relevance", "service_automation_relevance"}
)


def _sort_key(node: dict[str, Any]) -> tuple[int, float]:
    llm = node.get("llm_item") or {}
    vl = str(llm.get("value_level", "medium"))
    raw_conf = llm.get("confidence")
    conf = float(raw_conf) if isinstance(raw_conf, (int, float)) else 0.0
    return (VALUE_LEVEL_ORDER.get(vl, 1), -conf)


def _value_level(node: dict[str, Any]) -> str:
    return str((node.get("llm_item") or {}).get("value_level") or "medium")


def _section_node(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_insight_scalar(
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


def effective_insight_list(
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


def apply_insight_scalar_edit(
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


def apply_insight_list_edit(
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


def apply_insight_proposal_edits(node: dict[str, Any], field_values: dict[str, str]) -> None:
    """Apply all editable scalar and list fields."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in INSIGHT_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_insight_scalar_edit(sections, llm_item, sk, field_values[sk])
    for lk in INSIGHT_REVIEWABLE_LIST_KEYS:
        if lk in field_values:
            apply_insight_list_edit(sections, llm_item, lk, field_values[lk])


def insight_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one scalar field."""
    return effective_insight_scalar(llm_item, sections, section_key)


def insight_list_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Default textarea value for list fields."""
    return "\n".join(effective_insight_list(llm_item, sections, list_key))


def format_insight_readonly_markdown(node: dict[str, Any], topic_tags: list[str]) -> str:
    """Single insight card for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = effective_insight_scalar(llm_item, sections, "insight_title") or "Untitled insight"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    proposal_status = proposal_status_label(node)
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, topic_tags)

    lines = [
        f"## {title}",
        "",
        f"*{badge} · {proposal_status} · {ev_lbl} · "
        f"worthiness: {llm_item.get('wiki_worthiness', '—')}*",
        "",
    ]
    summary = effective_insight_scalar(llm_item, sections, "summary")
    if summary:
        lines.extend(["**Summary**", "", summary, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    for sk in INSIGHT_SCALAR_MID + INSIGHT_SCALAR_AFTER_TAGS:
        val = effective_insight_scalar(llm_item, sections, sk)
        if val:
            label = INSIGHT_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            lines.extend([f"**{label}**", "", val, ""])
    for lk in INSIGHT_REVIEWABLE_LIST_KEYS:
        items = effective_insight_list(llm_item, sections, lk)
        if items:
            label = INSIGHT_SECTION_LABELS.get(lk, lk.replace("_", " ").title())
            lines.extend([f"**{label}**", ""] + [f"- {p}" for p in items] + [""])
    return "\n".join(lines).rstrip()


def build_readonly_insights_markdown(
    sorted_nodes: list[dict[str, Any]],
    topic_tags: list[str],
) -> str:
    """Build full read-only column markdown."""
    if not sorted_nodes:
        return "*(No interview insights.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_insight_readonly_markdown(node, topic_tags))
    return "\n\n---\n\n".join(parts)


def _prepare_insight_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    insight_nodes = review.setdefault("interview_insights", [])
    llm_items = artifact.get("llm_output", {}).get("interview_insights") or []
    for i, node in enumerate(insight_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(insight_nodes, key=_sort_key)


def _persist_insight_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    tag_ui: dict[str, Any],
    allow: set[str],
) -> None:
    """Apply edits and write the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    apply_insight_proposal_edits(node, field_values)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    title = field_values.get("insight_title") or llm_item.get("insight_title") or "insight"
    streamlit_runtime.session_state["_insight_save_msg"] = f"Saved **{title}**."


def _render_insight_edit_box(
    st: Any,
    node: dict[str, Any],
    topic_tags: list[str],
    *,
    key_prefix: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
) -> None:
    """One bordered edit box per insight proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    title = effective_insight_scalar(llm_item, sections, "insight_title") or "Untitled"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    status_lbl = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{title}** · {badge} · **{status_lbl}**")

        field_values: dict[str, str] = {}
        for sk in INSIGHT_SCALAR_BEFORE_TAGS:
            label = INSIGHT_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=insight_field_edit_value(llm_item, sections, sk),
                height=120 if sk in INSIGHT_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        tag_ui = render_domain_tag_section(
            st,
            node,
            topic_tags,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="interview_insights",
            label_widget_key=f"{key_prefix}_edit_insight_title",
            summary_widget_key=f"{key_prefix}_edit_summary",
            llm_fallback_label_key="insight_title",
            llm_fallback_summary_key="summary",
        )

        for sk in INSIGHT_SCALAR_MID + INSIGHT_SCALAR_AFTER_TAGS:
            label = INSIGHT_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=insight_field_edit_value(llm_item, sections, sk),
                height=120 if sk in INSIGHT_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in INSIGHT_REVIEWABLE_LIST_KEYS:
            label = INSIGHT_SECTION_LABELS.get(lk, lk.replace("_", " ").title())
            field_values[lk] = st.text_area(
                label,
                value=insight_list_edit_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
                help="One bullet per line.",
            )

        def _save() -> None:
            _persist_insight_proposal_from_widgets(
                node,
                artifact_path,
                field_values,
                tag_ui,
                tag_allow,
            )

        render_proposal_decision_bar(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="interview_insights",
            on_save_callback=_save,
        )


def render_interview_insights(
    st: Any,
    artifact: dict[str, Any],
    *,
    topic_tags: list[str] | None = None,
    key_prefix: str,
    artifact_path: Path,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column interview insight review."""
    tags_list = list(topic_tags or [])
    tag_allow = {normalize_tag(str(t)) for t in tags_list if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = tags_list

    st.subheader("Interview insights")
    sorted_nodes = _prepare_insight_nodes(artifact)
    if not sorted_nodes:
        st.caption("No interview insights extracted (source is not an interview/transcript).")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    save_msg = streamlit_runtime.session_state.pop("_insight_save_msg", None)
    if save_msg:
        st.success(str(save_msg))

    read_col, edit_col = st.columns(2)
    with read_col:
        st.markdown(build_readonly_insights_markdown(sorted_nodes, tags_list))
    with edit_col:
        edit_nodes = sorted_nodes
        if len(sorted_nodes) > 6:
            labels = [
                effective_insight_scalar(
                    n.get("llm_item") or {},
                    n.get("sections") or {},
                    "insight_title",
                )
                or f"Insight {i + 1}"
                for i, n in enumerate(sorted_nodes)
            ]
            pick = st.selectbox(
                "Edit insight",
                options=labels,
                key=f"{key_prefix}_insight_jump",
            )
            idx = labels.index(pick) if pick in labels else 0
            edit_nodes = [sorted_nodes[idx]]
            st.caption("Showing one edit panel — use the selector to switch insights.")

        for i, node in enumerate(edit_nodes):
            pid = str(node.get("proposal_id") or f"idx{i}")
            pfx = f"{key_prefix}_ins_{pid}"
            _render_insight_edit_box(
                st,
                node,
                tags_list,
                key_prefix=pfx,
                artifact_path=artifact_path,
                model=model,
                prompt_version=prompt_version,
                tag_allow=tag_allow,
            )


def collect_insight_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across insight proposals."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("interview_insights") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        if not tag_node.get("new_tag_approved"):
            continue
        llm_item = node.get("llm_item") or {}
        new_tag = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
        if new_tag and new_tag not in tags:
            tags.append(new_tag)
    return tags
