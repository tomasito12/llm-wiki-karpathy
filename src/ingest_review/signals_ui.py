"""Streamlit rendering for roundup signal proposals (two-column read/edit)."""

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
from src.ingest_review.schema import SIGNAL_REVIEWABLE_LIST_KEYS, SIGNAL_REVIEWABLE_SCALAR_KEYS
from src.ingest_review.tags import normalize_tag

VALUE_LEVEL_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}
STRENGTH_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}

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

SIGNAL_SECTION_LABELS: dict[str, str] = {
    "signal_title": "Signal title",
    "signal_type": "Signal type",
    "summary": "Summary",
    "why_it_matters": "Why it matters",
    "operational_relevance": "Operational relevance",
    "service_automation_relevance": "Service automation relevance",
    "signal_strength": "Signal strength",
    "time_horizon": "Time horizon",
    "wiki_worthiness": "Wiki-worthiness",
    "suggested_destinations": "Suggested destinations",
    "mentioned_entities": "Mentioned entities",
    "evidence_snippets": "Evidence snippets",
}

SIGNAL_SCALAR_BEFORE_TAGS: tuple[str, ...] = ("signal_title", "signal_type", "summary")
SIGNAL_SCALAR_MID: tuple[str, ...] = (
    "why_it_matters",
    "operational_relevance",
    "service_automation_relevance",
)
SIGNAL_SCALAR_AFTER_TAGS: tuple[str, ...] = (
    "signal_strength",
    "time_horizon",
    "wiki_worthiness",
)
SIGNAL_TALL_SCALAR_KEYS: frozenset[str] = frozenset(
    {"summary", "why_it_matters", "operational_relevance", "service_automation_relevance"}
)


def _sort_key(node: dict[str, Any]) -> tuple[int, int]:
    llm = node.get("llm_item") or {}
    vl = str(llm.get("value_level", "medium"))
    strength = str(llm.get("signal_strength", "low"))
    return (VALUE_LEVEL_ORDER.get(vl, 1), STRENGTH_ORDER.get(strength, 2))


def _value_level(node: dict[str, Any]) -> str:
    return str((node.get("llm_item") or {}).get("value_level") or "medium")


def _section_node(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_signal_scalar(
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


def effective_signal_list(
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


def apply_signal_scalar_edit(
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


def apply_signal_list_edit(
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


def apply_signal_proposal_edits(node: dict[str, Any], field_values: dict[str, str]) -> None:
    """Apply all editable scalar and list fields."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in SIGNAL_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_signal_scalar_edit(sections, llm_item, sk, field_values[sk])
    for lk in SIGNAL_REVIEWABLE_LIST_KEYS:
        if lk in field_values:
            apply_signal_list_edit(sections, llm_item, lk, field_values[lk])


def signal_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one scalar field."""
    return effective_signal_scalar(llm_item, sections, section_key)


def signal_list_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Default textarea value for list fields."""
    return "\n".join(effective_signal_list(llm_item, sections, list_key))


def format_signal_readonly_markdown(node: dict[str, Any], trend_tags: list[str]) -> str:
    """Single signal card for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = effective_signal_scalar(llm_item, sections, "signal_title") or "Untitled signal"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    proposal_status = proposal_status_label(node)
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))
    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, trend_tags)

    lines = [
        f"## {title}",
        "",
        f"*{badge} · {proposal_status} · strength: {llm_item.get('signal_strength', '—')} · "
        f"worthiness: {llm_item.get('wiki_worthiness', '—')} · {ev_lbl}*",
        "",
    ]
    summary = effective_signal_scalar(llm_item, sections, "summary")
    if summary:
        lines.extend(["**Summary**", "", summary, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    for sk in SIGNAL_SCALAR_MID + SIGNAL_SCALAR_AFTER_TAGS:
        val = effective_signal_scalar(llm_item, sections, sk)
        if val:
            label = SIGNAL_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            lines.extend([f"**{label}**", "", val, ""])
    for lk in SIGNAL_REVIEWABLE_LIST_KEYS:
        items = effective_signal_list(llm_item, sections, lk)
        if items:
            label = SIGNAL_SECTION_LABELS.get(lk, lk.replace("_", " ").title())
            lines.extend([f"**{label}**", ""] + [f"- {p}" for p in items] + [""])
    return "\n".join(lines).rstrip()


def build_readonly_signals_markdown(
    sorted_nodes: list[dict[str, Any]],
    trend_tags: list[str],
) -> str:
    """Build full read-only column markdown."""
    if not sorted_nodes:
        return "*(No roundup signals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_signal_readonly_markdown(node, trend_tags))
    return "\n\n---\n\n".join(parts)


def _prepare_signal_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    signal_nodes = review.setdefault("roundup_signals", [])
    llm_items = artifact.get("llm_output", {}).get("roundup_signals") or []
    for i, node in enumerate(signal_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(signal_nodes, key=_sort_key)


def _persist_signal_proposal_from_widgets(
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
    apply_signal_proposal_edits(node, field_values)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    title = field_values.get("signal_title") or llm_item.get("signal_title") or "signal"
    streamlit_runtime.session_state["_signal_save_msg"] = f"Saved **{title}**."


def _render_signal_edit_box(
    st: Any,
    node: dict[str, Any],
    trend_tags: list[str],
    *,
    key_prefix: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
) -> None:
    """One bordered edit box per signal proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    title = effective_signal_scalar(llm_item, sections, "signal_title") or "Untitled"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    status_lbl = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{title}** · {badge} · **{status_lbl}**")

        field_values: dict[str, str] = {}
        for sk in SIGNAL_SCALAR_BEFORE_TAGS:
            label = SIGNAL_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=signal_field_edit_value(llm_item, sections, sk),
                height=120 if sk in SIGNAL_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        tag_ui = render_domain_tag_section(
            st,
            node,
            trend_tags,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="roundup_signals",
            label_widget_key=f"{key_prefix}_edit_signal_title",
            summary_widget_key=f"{key_prefix}_edit_summary",
            llm_fallback_label_key="signal_title",
            llm_fallback_summary_key="summary",
        )

        for sk in SIGNAL_SCALAR_MID + SIGNAL_SCALAR_AFTER_TAGS:
            label = SIGNAL_SECTION_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=signal_field_edit_value(llm_item, sections, sk),
                height=120 if sk in SIGNAL_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in SIGNAL_REVIEWABLE_LIST_KEYS:
            label = SIGNAL_SECTION_LABELS.get(lk, lk.replace("_", " ").title())
            field_values[lk] = st.text_area(
                label,
                value=signal_list_edit_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
                help="One bullet per line.",
            )

        def _save() -> None:
            _persist_signal_proposal_from_widgets(
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
            review_list_key="roundup_signals",
            on_save_callback=_save,
        )


def render_roundup_signals(
    st: Any,
    artifact: dict[str, Any],
    *,
    trend_tags: list[str] | None = None,
    key_prefix: str,
    artifact_path: Path,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column roundup signal review."""
    tags_list = list(trend_tags or [])
    tag_allow = {normalize_tag(str(t)) for t in tags_list if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = tags_list

    st.subheader("Roundup signals")
    sorted_nodes = _prepare_signal_nodes(artifact)
    if not sorted_nodes:
        st.caption("No roundup signals extracted (source is not an AI industry roundup).")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    save_msg = streamlit_runtime.session_state.pop("_signal_save_msg", None)
    if save_msg:
        st.success(str(save_msg))

    read_col, edit_col = st.columns(2)
    with read_col:
        st.markdown(build_readonly_signals_markdown(sorted_nodes, tags_list))
    with edit_col:
        edit_nodes = sorted_nodes
        if len(sorted_nodes) > 6:
            labels = [
                effective_signal_scalar(
                    n.get("llm_item") or {},
                    n.get("sections") or {},
                    "signal_title",
                )
                or f"Signal {i + 1}"
                for i, n in enumerate(sorted_nodes)
            ]
            pick = st.selectbox(
                "Edit signal",
                options=labels,
                key=f"{key_prefix}_signal_jump",
            )
            idx = labels.index(pick) if pick in labels else 0
            edit_nodes = [sorted_nodes[idx]]
            st.caption("Showing one edit panel — use the selector to switch signals.")

        for i, node in enumerate(edit_nodes):
            pid = str(node.get("proposal_id") or f"idx{i}")
            pfx = f"{key_prefix}_sig_{pid}"
            _render_signal_edit_box(
                st,
                node,
                tags_list,
                key_prefix=pfx,
                artifact_path=artifact_path,
                model=model,
                prompt_version=prompt_version,
                tag_allow=tag_allow,
            )


def collect_signal_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across signal proposals."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("roundup_signals") or []:
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
