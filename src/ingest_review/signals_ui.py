"""Streamlit rendering for roundup signal proposals (per-section review)."""

from __future__ import annotations

from typing import Any

from src.ingest_review.artifact import aggregate_impl_study_section_status
from src.ingest_review.schema import SIGNAL_LIST_KEYS, SIGNAL_SCALAR_KEYS

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

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

SIGNAL_DISPLAY_ORDER: tuple[str, ...] = (
    *SIGNAL_SCALAR_KEYS,
    *SIGNAL_LIST_KEYS,
)


def _status_index(current: str) -> int:
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _render_signal_scalar_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = SIGNAL_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"#### {label}")
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    st.markdown("**Model draft**")
    tall = section_key in ("summary", "operational_relevance", "service_automation_relevance")
    st.text(llm_text[:6000] + ("\u2026" if len(llm_text) > 6000 else ""))
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_sig_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        node["final_text"] = st.text_area(
            f"{label} \u2014 final text",
            value=default,
            height=160 if tall else 100,
            key=f"{key_prefix}_sig_{section_key}_txt",
        )
    elif node["status"] == "approved":
        node["final_text"] = None
    else:
        node["final_text"] = None
    node["notes"] = st.text_input(
        f"{label} \u2014 notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_sig_{section_key}_notes",
    )


def _render_signal_list_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = SIGNAL_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
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
        key=f"{key_prefix}_sig_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} \u2014 final list (one item per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_sig_{section_key}_txt",
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
        key=f"{key_prefix}_sig_{section_key}_notes",
    )


def _render_signal_tag_panel(
    st: Any,
    llm_item: dict[str, Any],
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
            key=f"{key_prefix}_sig_tags_select",
        )
    else:
        st.caption("Tag allowlist is empty \u2014 add tags via the fields below.")
        chosen = []
    tag_node["approved_allowlist_tags"] = chosen
    extra = st.text_input(
        "Reviewer tags (comma-separated, not in allowlist)",
        value=", ".join(tag_node.get("reviewer_tags_added") or []),
        key=f"{key_prefix}_sig_tags_extra",
    )
    tag_node["reviewer_tags_added"] = [x.strip() for x in extra.split(",") if x.strip()]

    proposed_new = llm_item.get("proposed_new_tags") or []
    already_approved_new = set(tag_node.get("approved_new_tags") or [])
    if proposed_new:
        st.markdown("**LLM-proposed new tags** (not in allowlist)")
        newly_approved: list[str] = list(already_approved_new)
        for ptag in proposed_new:
            checked = st.checkbox(
                f"Approve: {ptag}",
                value=ptag in already_approved_new,
                key=f"{key_prefix}_sig_newtag_{ptag}",
            )
            if checked and ptag not in newly_approved:
                newly_approved.append(ptag)
            elif not checked and ptag in newly_approved:
                newly_approved.remove(ptag)
        tag_node["approved_new_tags"] = newly_approved


def render_roundup_signals(
    st: Any,
    artifact: dict[str, Any],
    *,
    trend_tags: list[str] | None = None,
    key_prefix: str,
) -> None:
    """Render per-section review for all roundup signal proposals."""
    review = artifact.setdefault("review", {})
    signal_nodes = review.setdefault("roundup_signals", [])
    llm_items = artifact.get("llm_output", {}).get("roundup_signals") or []
    st.subheader("Roundup signals")
    if not signal_nodes and not llm_items:
        st.caption("No roundup signals extracted (source is not an AI industry roundup).")
        return

    for i, node in enumerate(signal_nodes):
        llm_item = node.get("llm_item") or (llm_items[i] if i < len(llm_items) else {})
        title = llm_item.get("signal_title") or f"Signal #{i + 1}"
        sections = node.setdefault("sections", {})
        agg_status = aggregate_impl_study_section_status(sections)
        worthiness = llm_item.get("wiki_worthiness") or "?"
        header = f"Signal #{i + 1}: {title} [{agg_status}] \u00b7 {worthiness}"
        expanded = len(signal_nodes) == 1
        pfx = f"{key_prefix}_sig{i}"
        with st.expander(header, expanded=expanded):
            sig_type = llm_item.get("signal_type") or "\u2014"
            strength = llm_item.get("signal_strength") or "\u2014"
            horizon = llm_item.get("time_horizon") or "\u2014"
            st.caption(
                f"Type: {sig_type} \u00b7 Strength: {strength} "
                f"\u00b7 Horizon: {horizon} \u00b7 Worthiness: {worthiness}"
            )
            for sk in SIGNAL_SCALAR_KEYS:
                _render_signal_scalar_section(
                    st, llm_item, sections, section_key=sk, key_prefix=pfx
                )
            for lk in SIGNAL_LIST_KEYS:
                _render_signal_list_section(st, llm_item, sections, section_key=lk, key_prefix=pfx)
            tag_node = node.setdefault(
                "tags",
                {"approved_allowlist_tags": [], "reviewer_tags_added": [], "approved_new_tags": []},
            )
            _render_signal_tag_panel(st, llm_item, tag_node, trend_tags or [], key_prefix=pfx)
            st.divider()
            node["notes"] = st.text_input(
                "Signal notes",
                value=str(node.get("notes") or ""),
                key=f"{pfx}_sig_notes",
            )
            with st.expander("Raw JSON (debug)", expanded=False):
                st.json(llm_item)


def collect_signal_approved_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return reviewer_tags_added + approved_new_tags across roundup signals."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("roundup_signals") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        for t in tag_node.get("reviewer_tags_added") or []:
            if t and t not in tags:
                tags.append(t)
        for t in tag_node.get("approved_new_tags") or []:
            if t and t not in tags:
                tags.append(t)
    return tags
