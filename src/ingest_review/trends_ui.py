"""Streamlit rendering for industry trend proposals (per-section review)."""

from __future__ import annotations

from typing import Any

from src.ingest_review.artifact import aggregate_impl_study_section_status
from src.ingest_review.schema import TREND_LIST_KEYS, TREND_SCALAR_KEYS

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

TREND_SECTION_LABELS: dict[str, str] = {
    "trend_name": "Trend name",
    "trend_description": "Trend description",
    "evidence_from_source": "Evidence from source",
    "time_sensitivity": "Time sensitivity",
    "uncertainty_note": "Uncertainty note",
    "supporting_snippet": "Supporting snippet",
    "supporting_data_points": "Supporting data points",
    "related_trends": "Related trends",
}

TREND_DISPLAY_ORDER: tuple[str, ...] = (
    *TREND_SCALAR_KEYS,
    *TREND_LIST_KEYS,
)


def _status_index(current: str) -> int:
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _render_trend_scalar_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = TREND_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"#### {label}")
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    st.markdown("**Model draft**")
    tall = section_key in ("trend_description", "evidence_from_source", "uncertainty_note")
    st.text(llm_text[:6000] + ("\u2026" if len(llm_text) > 6000 else ""))
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_tr_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        node["final_text"] = st.text_area(
            f"{label} \u2014 final text",
            value=default,
            height=160 if tall else 100,
            key=f"{key_prefix}_tr_{section_key}_txt",
        )
    elif node["status"] == "approved":
        node["final_text"] = None
    else:
        node["final_text"] = None
    node["notes"] = st.text_input(
        f"{label} \u2014 notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_tr_{section_key}_notes",
    )


def _render_trend_list_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = TREND_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
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
        key=f"{key_prefix}_tr_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} \u2014 final list (one item per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_tr_{section_key}_txt",
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
        key=f"{key_prefix}_tr_{section_key}_notes",
    )


def _render_trend_tag_panel(
    st: Any,
    tag_node: dict[str, Any],
    trend_tags: list[str],
    *,
    key_prefix: str,
) -> None:
    st.markdown("#### Tags")
    current_approved = tag_node.get("approved_allowlist_tags") or []
    if trend_tags:
        chosen = st.multiselect(
            "Approved tags (from allowlist)",
            options=trend_tags,
            default=[t for t in current_approved if t in trend_tags],
            key=f"{key_prefix}_tr_tags_select",
        )
    else:
        st.caption("Trend tag allowlist is empty \u2014 add tags via the reviewer field below.")
        chosen = []
    tag_node["approved_allowlist_tags"] = chosen
    extra = st.text_input(
        "Add new tags (comma-separated)",
        value=", ".join(tag_node.get("reviewer_tags_added") or []),
        key=f"{key_prefix}_tr_tags_extra",
    )
    tag_node["reviewer_tags_added"] = [x.strip() for x in extra.split(",") if x.strip()]


def _render_trend_match_candidates(
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


def render_trend_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    trend_tags: list[str],
) -> None:
    """Render per-section review for all industry trend proposals."""
    review = artifact.setdefault("review", {})
    trend_nodes = review.setdefault("industry_trends", [])
    llm_items = artifact.get("llm_output", {}).get("industry_trends") or []
    st.subheader("Trends")
    if not trend_nodes and not llm_items:
        st.caption("No trend proposals.")
        return

    for i, node in enumerate(trend_nodes):
        llm_item = node.get("llm_item") or (llm_items[i] if i < len(llm_items) else {})
        name = llm_item.get("trend_name") or f"Trend #{i + 1}"
        sections = node.setdefault("sections", {})
        agg_status = aggregate_impl_study_section_status(sections)
        header = f"Trend #{i + 1}: {name} [{agg_status}]"
        expanded = len(trend_nodes) == 1
        pfx = f"{key_prefix}_tr{i}"
        with st.expander(header, expanded=expanded):
            action = llm_item.get("suggested_action") or "\u2014"
            st.caption(f"Confidence: {llm_item.get('confidence', 0):.0%} \u00b7 Action: {action}")
            for sk in TREND_SCALAR_KEYS:
                _render_trend_scalar_section(st, llm_item, sections, section_key=sk, key_prefix=pfx)
            for lk in TREND_LIST_KEYS:
                _render_trend_list_section(st, llm_item, sections, section_key=lk, key_prefix=pfx)
            st.divider()
            tag_node = node.setdefault(
                "tags",
                {
                    "approved_allowlist_tags": [],
                    "reviewer_tags_added": [],
                },
            )
            _render_trend_tag_panel(st, tag_node, trend_tags, key_prefix=pfx)
            _render_trend_match_candidates(st, llm_item, key_prefix=pfx)
            node["notes"] = st.text_input(
                "Proposal notes",
                value=str(node.get("notes") or ""),
                key=f"{pfx}_tr_notes",
            )
            with st.expander("Raw JSON (debug)", expanded=False):
                st.json(llm_item)


def collect_trend_approved_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return all reviewer_tags_added across trend proposals."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("industry_trends") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        for t in tag_node.get("reviewer_tags_added") or []:
            if t and t not in tags:
                tags.append(t)
    return tags
