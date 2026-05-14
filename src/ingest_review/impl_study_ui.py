"""Streamlit rendering for implementation-study proposals (per-section review)."""

from __future__ import annotations

from typing import Any

from src.ingest_review.artifact import aggregate_impl_study_section_status
from src.ingest_review.schema import IMPL_STUDY_LIST_KEYS, IMPL_STUDY_SCALAR_KEYS

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

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
    "related_sources": "Related sources",
}

IMPL_STUDY_DISPLAY_ORDER: tuple[str, ...] = (
    *IMPL_STUDY_SCALAR_KEYS,
    *IMPL_STUDY_LIST_KEYS,
)


def _status_index(current: str) -> int:
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _render_impl_scalar_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = IMPL_STUDY_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"#### {label}")
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    llm_text = str(llm_item.get(section_key) or "")
    st.markdown("**Model draft**")
    st.text(llm_text[:6000] + ("…" if len(llm_text) > 6000 else ""))
    node["status"] = st.selectbox(
        f"{label} — status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_impl_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        node["final_text"] = st.text_area(
            f"{label} — final text",
            value=default,
            height=120,
            key=f"{key_prefix}_impl_{section_key}_txt",
        )
    elif node["status"] == "approved":
        node["final_text"] = None
    else:
        node["final_text"] = None
    node["notes"] = st.text_input(
        f"{label} — notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_impl_{section_key}_notes",
    )


def _render_impl_list_section(
    st: Any,
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
) -> None:
    label = IMPL_STUDY_SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
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
        f"{label} — status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_impl_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} — final list (one item per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=100,
        key=f"{key_prefix}_impl_{section_key}_txt",
    )
    lines = [ln.strip() for ln in raw_list.splitlines() if ln.strip()]
    if node["status"] == "modified":
        node["final_list"] = lines
    elif node["status"] == "approved":
        node["final_list"] = None
    else:
        node["final_list"] = None
    node["notes"] = st.text_input(
        f"{label} — notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_impl_{section_key}_notes",
    )


def _render_evidence_panel(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
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
    st.markdown("#### Tags")
    suggested = llm_item.get("suggested_existing_tags") or []
    current_approved = tag_node.get("approved_allowlist_tags") or []
    default_tags = (
        current_approved if current_approved else [t for t in suggested if t in impl_study_tags]
    )
    chosen = st.multiselect(
        "Approved tags (from allowlist)",
        options=impl_study_tags,
        default=[t for t in default_tags if t in impl_study_tags],
        key=f"{key_prefix}_impl_tags_select",
    )
    tag_node["approved_allowlist_tags"] = chosen

    extra = st.text_input(
        "Reviewer tags (comma-separated, not in allowlist)",
        value=", ".join(tag_node.get("reviewer_tags_added") or []),
        key=f"{key_prefix}_impl_tags_extra",
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
                key=f"{key_prefix}_impl_newtag_{ptag}",
            )
            if checked and ptag not in newly_approved:
                newly_approved.append(ptag)
            elif not checked and ptag in newly_approved:
                newly_approved.remove(ptag)
        tag_node["approved_new_tags"] = newly_approved


def _render_match_candidates(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
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
            st.warning(f"**{title}** — match: {kind}, confidence: {conf:.0%}")


def render_implementation_studies(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    impl_study_tags: list[str],
) -> None:
    """Render per-section review for all implementation-study proposals."""
    review = artifact.setdefault("review", {})
    impl_nodes = review.setdefault("implementation_studies", [])
    llm_items = (
        artifact.get("llm_output", {}).get("implementation_studies")
        or artifact.get("llm_output", {}).get("enterprise_studies")
        or []
    )
    st.subheader("Implementation studies")
    if not impl_nodes and not llm_items:
        st.caption("No implementation-study proposals.")
        return

    for i, node in enumerate(impl_nodes):
        llm_item = node.get("llm_item") or (llm_items[i] if i < len(llm_items) else {})
        title = llm_item.get("title") or llm_item.get("company_name") or f"Study #{i + 1}"
        company = llm_item.get("company") or llm_item.get("company_name") or ""
        sections = node.setdefault("sections", {})
        agg_status = aggregate_impl_study_section_status(sections)
        header = f"Impl study #{i + 1}: {title}"
        if company:
            header += f" — {company}"
        header += f" [{agg_status}]"
        expanded = len(impl_nodes) == 1
        pfx = f"{key_prefix}_is{i}"
        with st.expander(header, expanded=expanded):
            st.caption(
                f"Confidence: {llm_item.get('confidence', 0):.0%} · "
                f"Action: {llm_item.get('suggested_action', '—')}"
            )
            for sk in IMPL_STUDY_SCALAR_KEYS:
                _render_impl_scalar_section(st, llm_item, sections, section_key=sk, key_prefix=pfx)
            for lk in IMPL_STUDY_LIST_KEYS:
                _render_impl_list_section(st, llm_item, sections, section_key=lk, key_prefix=pfx)
            st.divider()
            _render_evidence_panel(st, llm_item, key_prefix=pfx)
            tag_node = node.setdefault(
                "tags",
                {
                    "approved_allowlist_tags": [],
                    "reviewer_tags_added": [],
                    "approved_new_tags": [],
                },
            )
            _render_tag_panel(st, llm_item, tag_node, impl_study_tags, key_prefix=pfx)
            _render_match_candidates(st, llm_item, key_prefix=pfx)
            node["notes"] = st.text_input(
                "Proposal notes",
                value=str(node.get("notes") or ""),
                key=f"{pfx}_impl_notes",
            )
            with st.expander("Raw JSON (debug)", expanded=False):
                st.json(llm_item)


def collect_approved_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return all approved_new_tags across implementation-study proposals."""
    review = artifact.get("review") or {}
    tags: list[str] = []
    for node in review.get("implementation_studies") or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        for t in tag_node.get("approved_new_tags") or []:
            if t and t not in tags:
                tags.append(t)
    return tags
