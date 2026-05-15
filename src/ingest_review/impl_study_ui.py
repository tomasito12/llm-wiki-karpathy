"""Streamlit rendering for implementation-study proposals (proposal-level review)."""

from __future__ import annotations

import logging
from typing import Any

from src.ingest_review.dashboard_ui import (
    human_evidence_type_label,
    render_proposal_evidence_type_editor,
    render_proposal_tag_review,
)
from src.ingest_review.impl_study_gate import (
    format_impl_study_evidence_caption,
    impl_study_likely_misclassified,
)
from src.ingest_review.schema import (
    IMPL_STUDY_REVIEWABLE_LIST_KEYS,
    IMPL_STUDY_REVIEWABLE_SCALAR_KEYS,
)

logger = logging.getLogger(__name__)

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")
STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

_VALUE_LEVEL_SORT: dict[str, int] = {"high": 0, "medium": 1, "low": 2}
_VALUE_LEVEL_BADGE: dict[str, str] = {"high": "H", "medium": "M", "low": "L"}

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


def _proposal_status_index(current: str) -> int:
    """Return index into PROPOSAL_STATUS_OPTIONS."""
    if current in PROPOSAL_STATUS_OPTIONS:
        return PROPOSAL_STATUS_OPTIONS.index(current)
    return 0


def _status_index(current: str) -> int:
    """Return index into STATUS_OPTIONS."""
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _sort_key(node: dict[str, Any]) -> tuple[int, int, float]:
    """Sort by ignore-last, value_level (high first), then confidence descending."""
    llm = node.get("llm_item") or {}
    vl = str(llm.get("value_level", "medium"))
    conf = llm.get("confidence", 0)
    if not isinstance(conf, (int, float)):
        conf = 0.0
    action = str(llm.get("suggested_action") or "")
    ignore_rank = 1 if action == "ignore" else 0
    return (ignore_rank, _VALUE_LEVEL_SORT.get(vl, 1), -float(conf))


def _render_card_header(
    st: Any,
    llm_item: dict[str, Any],
    node: dict[str, Any],
    *,
    index: int,
) -> None:
    """Render compact proposal card header with value badge and key metrics."""
    vl = str(llm_item.get("value_level", "medium"))
    badge = _VALUE_LEVEL_BADGE.get(vl, "M")
    title = llm_item.get("title") or llm_item.get("company_name") or f"Study #{index + 1}"
    company = llm_item.get("company") or llm_item.get("company_name") or ""
    conf = llm_item.get("confidence", 0)
    if isinstance(conf, (int, float)):
        conf_display = f"{conf:.0%}"
    else:
        conf_display = str(conf)
    industry = llm_item.get("industry") or "\u2014"
    action = llm_item.get("suggested_action") or "\u2014"
    status = node.get("proposal_status", "pending")
    ev_lbl = human_evidence_type_label(llm_item.get("evidence_type"))

    header = f"**[{badge}] {title}**"
    if company:
        header += f" \u2014 {company}"
    header += f" \u00b7 confidence: {conf_display}"
    st.markdown(header)
    st.caption(
        f"Industry: {industry} \u00b7 Action: {action} \u00b7 Evidence: {ev_lbl} "
        f"\u00b7 Status: `{status}`"
    )
    st.caption(format_impl_study_evidence_caption(llm_item))
    if impl_study_likely_misclassified(llm_item):
        st.warning(
            "No stated deployment evidence — likely misclassified. "
            "Consider Reject or route to topics/how-to."
        )


def _render_action_row(
    st: Any,
    node: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render Approve | Reject | Defer action buttons."""
    c1, c2, c3 = st.columns(3)
    if c1.button("\u2713 Approve", key=f"{key_prefix}_approve"):
        node["proposal_status"] = "approved"
    if c2.button("\u2717 Reject", key=f"{key_prefix}_reject"):
        node["proposal_status"] = "rejected"
    if c3.button("\u23f3 Defer", key=f"{key_prefix}_defer"):
        node["proposal_status"] = "deferred"


def _render_scalar_field(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    """Render a reviewable scalar field inside the edit expander."""
    label = IMPL_STUDY_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"##### {label}")
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    st.text(llm_text[:6000] + ("\u2026" if len(llm_text) > 6000 else ""))
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_impl_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        node["final_text"] = st.text_area(
            f"{label} \u2014 final text",
            value=default,
            height=120,
            key=f"{key_prefix}_impl_{section_key}_txt",
        )
    else:
        node["final_text"] = None


def _render_list_field(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    """Render a reviewable list field inside the edit expander."""
    label = IMPL_STUDY_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"##### {label}")
    llm_list = llm_item.get(section_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_list": None, "notes": None, "llm_list": list(llm_list)},
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_list)
    st.json(node["llm_list"])
    node["status"] = st.selectbox(
        f"{label} \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_impl_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} \u2014 final list (one per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_impl_{section_key}_txt",
    )
    lines = [ln.strip() for ln in raw_list.splitlines() if ln.strip()]
    if node["status"] == "modified":
        node["final_list"] = lines
    else:
        node["final_list"] = None


def _render_evidence_panel(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render evidence snippets as a collapsible panel."""
    snippets = llm_item.get("evidence_snippets") or []
    if not snippets:
        return
    with st.expander(f"Evidence snippets ({len(snippets)})", expanded=False):
        for j, ev in enumerate(snippets):
            if not isinstance(ev, dict):
                continue
            prov = ev.get("provenance", "stated")
            badge = {"stated": "direct", "inferred": "inferred", "interpretation": "interp"}.get(
                prov, prov
            )
            st.markdown(f"**[{badge}]** {ev.get('claim', '')}")
            st.caption(ev.get("snippet", ""))
            if j < len(snippets) - 1:
                st.divider()


def _render_tag_panel(
    st: Any,
    llm_item: dict[str, Any],
    tag_node: dict[str, Any],
    impl_study_tags: list[str],
    *,
    key_prefix: str,
) -> None:
    """Render tag review panel with final_primary_tag / final_secondary_tag."""
    render_proposal_tag_review(
        st,
        llm_item,
        tag_node,
        impl_study_tags,
        key_prefix=key_prefix,
        entity_kind="domain",
    )


def _render_match_candidates(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render possible duplicate matches from the LLM."""
    candidates = llm_item.get("match_candidates") or []
    if not candidates:
        return
    with st.expander("Possible duplicates (from LLM)", expanded=False):
        for mc in candidates:
            if not isinstance(mc, dict):
                continue
            title = mc.get("title_or_slug", "?")
            kind = mc.get("match_kind", "?")
            conf = mc.get("confidence", 0)
            st.warning(f"**{title}** \u2014 match: {kind}, confidence: {conf:.0%}")


def render_implementation_studies(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    impl_study_tags: list[str],
) -> None:
    """Render proposal-level review for all implementation-study proposals.

    Each study is shown as a compact card with value_level badge,
    title, company, and confidence, followed by an action row and
    an edit expander for field-level editing. Sorted by value_level
    then confidence (high first).
    """
    review = artifact.setdefault("review", {})
    impl_nodes = review.setdefault("implementation_studies", [])
    st.subheader("Implementation studies")
    if not impl_nodes:
        st.caption("No implementation-study proposals.")
        return

    sorted_nodes = sorted(impl_nodes, key=_sort_key)

    for i, node in enumerate(sorted_nodes):
        llm_item = node.get("llm_item") or {}
        pid = node.get("proposal_id") or f"anon{i}"
        pfx = f"{key_prefix}_is_{pid[:8]}"

        _render_card_header(st, llm_item, node, index=i)
        _render_action_row(st, node, key_prefix=pfx)

        sections = node.setdefault("sections", {})
        tag_node = node.setdefault(
            "tags",
            {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
        )
        title = llm_item.get("title") or llm_item.get("company_name") or f"Study #{i + 1}"
        with st.expander(f"Edit: {title}", expanded=False):
            for sk in IMPL_STUDY_REVIEWABLE_SCALAR_KEYS:
                _render_scalar_field(st, llm_item, sections, section_key=sk, key_prefix=pfx)
            for lk in IMPL_STUDY_REVIEWABLE_LIST_KEYS:
                _render_list_field(st, llm_item, sections, section_key=lk, key_prefix=pfx)
            st.divider()
            _render_evidence_panel(st, llm_item, key_prefix=pfx)
            _render_tag_panel(st, llm_item, tag_node, impl_study_tags, key_prefix=pfx)
            _render_match_candidates(st, llm_item, key_prefix=pfx)
            render_proposal_evidence_type_editor(st, llm_item, key_prefix=pfx)
            with st.expander("Raw JSON (debug)", expanded=False):
                st.json(llm_item)
        st.divider()


def collect_impl_study_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags where new_tag_approved is True across impl studies."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("implementation_studies") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        if not tag_node.get("new_tag_approved"):
            continue
        llm_item = node.get("llm_item") or {}
        new_tag = llm_item.get("suggested_new_tag") or ""
        if new_tag and new_tag not in tags:
            tags.append(new_tag)
    return tags
