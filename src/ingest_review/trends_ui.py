"""Streamlit rendering for industry trend proposals (two-column read/edit + domain tags)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import format_proposal_meta_subtitle, google_search_markdown
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_tag_ui_to_node,
    effective_readonly_domain_tags,
    render_domain_tag_section,
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
from src.ingest_review.schema import TREND_REVIEWABLE_LIST_KEYS, TREND_REVIEWABLE_SCALAR_KEYS
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

TREND_FIELD_LABELS: dict[str, str] = {
    "trend_slug": "Page slug",
    "trend_title": "Page title",
    "trend_description": "Trend description",
    "evidence_from_source": "Evidence from source",
    "time_sensitivity": "Time sensitivity",
    "uncertainty_note": "Uncertainty note",
    "supporting_data_points": "Supporting data points",
}

TREND_SCALAR_BEFORE_TAGS: tuple[str, ...] = ("trend_slug", "trend_title", "trend_description")
TREND_SCALAR_AFTER_TAGS: tuple[str, ...] = (
    "evidence_from_source",
    "time_sensitivity",
    "uncertainty_note",
)
TREND_TALL_SCALAR_KEYS: frozenset[str] = frozenset({"trend_description", "evidence_from_source"})


def _sort_key(node: dict[str, Any]) -> tuple[int, float]:
    llm = node.get("llm_item") or {}
    level = str(llm.get("value_level") or "medium")
    conf = float(llm.get("confidence") or 0)
    return (VALUE_LEVEL_ORDER.get(level, 1), -conf)


def _value_level(node: dict[str, Any]) -> str:
    return str((node.get("llm_item") or {}).get("value_level") or "medium")


def _section_node(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_trend_scalar(
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


def effective_trend_list(
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


def apply_trend_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one trend field edit; infer section status from LLM draft."""
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


def apply_trend_list_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    list_key: str,
    raw_text: str,
) -> None:
    """Persist list field (one item per line); infer section status from LLM list."""
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


def apply_trend_proposal_edits(
    node: dict[str, Any],
    field_values: dict[str, str],
) -> None:
    """Apply all editable scalar and list fields for one trend proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in TREND_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_trend_scalar_edit(sections, llm_item, sk, field_values[sk])
    for lk in TREND_REVIEWABLE_LIST_KEYS:
        if lk in field_values:
            apply_trend_list_edit(sections, llm_item, lk, field_values[lk])


def trend_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one trend scalar field."""
    return effective_trend_scalar(llm_item, sections, section_key)


def trend_list_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Default textarea value for list fields (one bullet per line)."""
    return "\n".join(effective_trend_list(llm_item, sections, list_key))


def format_trend_proposal_readonly_markdown(
    node: dict[str, Any],
    trend_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Single trend card for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = (
        effective_trend_scalar(llm_item, sections, "trend_title")
        or effective_trend_scalar(llm_item, sections, "trend_slug")
        or "Untitled trend"
    )
    slug = effective_trend_scalar(llm_item, sections, "trend_slug")
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}
    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, trend_tags)

    lines = [
        f"## {title}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    google = google_search_markdown(title)
    if google:
        lines.extend([google, ""])
    if slug:
        lines.extend(["**Slug**", "", slug, ""])
    desc = effective_trend_scalar(llm_item, sections, "trend_description")
    if desc:
        lines.extend(["**Description**", "", desc, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    for sk in TREND_SCALAR_AFTER_TAGS:
        val = effective_trend_scalar(llm_item, sections, sk)
        if val:
            label = TREND_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            lines.extend([f"**{label}**", "", val, ""])
    for lk in TREND_REVIEWABLE_LIST_KEYS:
        items = effective_trend_list(llm_item, sections, lk)
        if items:
            label = TREND_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            lines.extend([f"**{label}**", ""] + [f"- {p}" for p in items] + [""])
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    related = llm_item.get("related_trends") or []
    if isinstance(related, list) and related:
        lines.extend([f"*Related trends: {', '.join(str(r) for r in related)}*", ""])
    return "\n".join(lines).rstrip()


def build_readonly_trends_markdown(
    sorted_nodes: list[dict[str, Any]],
    trend_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Build full read-only column markdown for all trend proposals."""
    if not sorted_nodes:
        return "*(No trend proposals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_trend_proposal_readonly_markdown(node, trend_tags, artifact=artifact))
    return "\n\n---\n\n".join(parts)


def _trend_expander_label(node: dict[str, Any], index: int) -> str:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = (
        effective_trend_scalar(llm_item, sections, "trend_title")
        or effective_trend_scalar(llm_item, sections, "trend_slug")
        or f"Trend {index + 1}"
    )
    badge = VALUE_LEVEL_BADGES.get(_value_level(node), "Medium")
    return build_proposal_expander_label(node, title, badge=badge)


def _prepare_trend_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    trend_nodes = review.setdefault("industry_trends", [])
    llm_items = artifact.get("llm_output", {}).get("industry_trends") or []
    for i, node in enumerate(trend_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(trend_nodes, key=_sort_key)


def _persist_trend_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    tag_ui: dict[str, Any],
    allow: set[str],
    *,
    key_prefix: str,
) -> None:
    """Apply textarea + tag edits from this run and write the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    apply_trend_proposal_edits(node, field_values)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    title = (
        field_values.get("trend_title")
        or llm_item.get("trend_title")
        or field_values.get("trend_slug")
        or llm_item.get("trend_slug")
        or "trend"
    )
    set_proposal_save_message(key_prefix, f"Saved **{title}**.")


def _render_trend_edit_box(
    st: Any,
    node: dict[str, Any],
    trend_tags: list[str],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
) -> None:
    """One bordered edit box per trend proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    title = (
        effective_trend_scalar(llm_item, sections, "trend_title")
        or effective_trend_scalar(llm_item, sections, "trend_slug")
        or "Untitled"
    )
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    status_lbl = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{title}** · {badge} · **{status_lbl}**")
        render_proposal_regen_meta_caption(st, node, "Trend")

        field_values: dict[str, str] = {}
        for sk in TREND_SCALAR_BEFORE_TAGS:
            label = TREND_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=trend_field_edit_value(llm_item, sections, sk),
                height=120 if sk in TREND_TALL_SCALAR_KEYS else 72,
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
            review_list_key="industry_trends",
            label_widget_key=f"{key_prefix}_edit_trend_title",
            summary_widget_key=f"{key_prefix}_edit_trend_description",
            llm_fallback_label_key="trend_title",
            llm_fallback_summary_key="trend_description",
        )

        for sk in TREND_SCALAR_AFTER_TAGS:
            label = TREND_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=trend_field_edit_value(llm_item, sections, sk),
                height=120 if sk in TREND_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in TREND_REVIEWABLE_LIST_KEYS:
            label = TREND_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            field_values[lk] = st.text_area(
                label,
                value=trend_list_edit_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
                help="One bullet per line.",
            )

        snippet = str(llm_item.get("supporting_snippet") or "").strip()
        if snippet:
            with st.expander("Source evidence (read-only)", expanded=False):
                st.text(snippet[:4000] + ("…" if len(snippet) > 4000 else ""))

        related = llm_item.get("related_trends") or []
        if related:
            st.caption(f"Related trends (LLM): {', '.join(str(r) for r in related)}")

        proposal_id = str(node.get("proposal_id") or "")
        render_regenerate_with_new_title_controls(
            st,
            entity_key="trend",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
            title_label="New trend title",
        )
        render_reclassify_to_section_controls(
            st,
            source_entity_key="trend",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
            title_label="Title in target section",
        )

        def _save() -> None:
            _persist_trend_proposal_from_widgets(
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
            review_list_key="industry_trends",
            on_save_callback=_save,
        )


def render_trend_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    artifact_path: Path,
    trend_tags: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column trend review: read-only catalog left, edit panel right."""
    tags_list = list(trend_tags or [])
    tag_allow = {normalize_tag(str(t)) for t in tags_list if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = tags_list

    st.subheader("Industry trends")
    sorted_nodes = _prepare_trend_nodes(artifact)
    llm_trends = artifact.get("llm_output", {}).get("industry_trends") or []

    if not sorted_nodes and not llm_trends:
        st.caption("No trend proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    regen_msg = pop_proposal_regen_msg("trend")
    if regen_msg:
        st.success(regen_msg)

    def _readonly_md(node: dict[str, Any]) -> str:
        if len(sorted_nodes) == 1:
            return build_readonly_trends_markdown([node], tags_list, artifact=artifact)
        return format_trend_proposal_readonly_markdown(node, tags_list, artifact=artifact)

    def _render_edit(node: dict[str, Any], index: int) -> None:
        pid = str(node.get("proposal_id") or f"idx{index}")
        pfx = proposal_edit_key_prefix(
            key_prefix, pid, "tr", regen_count=regen_count_from_node(node)
        )
        _render_trend_edit_box(
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
        empty_readonly_text="*(No trend proposals.)*",
        label_for_node=_trend_expander_label,
        readonly_markdown_for_node=_readonly_md,
        render_edit_for_node=_render_edit,
    )


def collect_trend_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across trend proposals."""
    from src.ingest_review.domain_tag_ui import collect_approved_new_tags_from_review

    return collect_approved_new_tags_from_review(artifact, "industry_trends")


collect_trend_approved_new_tags = collect_trend_new_tags
