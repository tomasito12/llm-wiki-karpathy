"""Streamlit-oriented review widgets (pass ``st`` for testability)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.schema import (
    EVIDENCE_TYPE_VALUES,
    REGENERATABLE_SOURCE_SECTION_KEYS,
    SOURCE_SUMMARY_SCALAR_KEYS,
    normalize_evidence_type,
)
from src.ingest_review.tags import (
    build_tag_select_options,
    find_similar_tags,
    normalize_tag,
)

EntityKind = str  # "domain" | "tool" | "model"

TAG_ROLE_HINTS: dict[str, tuple[str, str]] = {
    "domain": (
        "Main strategic domain",
        "Cross-cutting relationship (optional)",
    ),
    "tool": (
        "Main tool category",
        "Operational role or adjacent classification (optional)",
    ),
    "model": (
        "Deployment / openness class",
        "Capability specialization (optional)",
    ),
}

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")


def human_evidence_type_label(raw: object) -> str:
    """Title-case evidence type for display (e.g. ``vendor_claim`` → Vendor Claim)."""
    return normalize_evidence_type(raw).replace("_", " ").title()


def format_proposed_tags_caption(
    llm_item: dict[str, Any],
    tag_node: dict[str, Any] | None,
    allowlist: list[str],
) -> str | None:
    """Compact caption for primary/secondary tags with allowlist vs proposed-new provenance."""
    allow_set = {normalize_tag(t) for t in allowlist}
    shown: set[str] = set()
    parts: list[str] = []
    for llm_key, final_key in (
        ("primary_tag", "final_primary_tag"),
        ("secondary_tag", "final_secondary_tag"),
    ):
        raw = ""
        if tag_node:
            raw = str(tag_node.get(final_key) or "")
        if not raw:
            raw = str(llm_item.get(llm_key) or "")
        norm = normalize_tag(raw)
        if not norm or norm in shown:
            continue
        shown.add(norm)
        provenance = "allowlist" if norm in allow_set else "outside allowlist"
        parts.append(f"{norm} ({provenance})")
    suggested = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
    if suggested and suggested not in shown:
        parts.append(f"{suggested} (suggested new)")
    if not parts:
        return None
    return "Tags: " + " · ".join(parts)


def render_similar_tags_warning(
    st: Any,
    candidate: str,
    allowlist: list[str],
    *,
    key_prefix: str,
) -> None:
    """Warn when a suggested new tag may duplicate an existing allowlist entry."""
    norm = normalize_tag(candidate)
    if not norm:
        return
    similar = find_similar_tags(norm, allowlist)
    if similar:
        st.warning(
            "Similar existing tags: "
            + ", ".join(f"`{t}`" for t in similar)
            + " — prefer reusing an allowlist tag if one fits."
        )


def render_proposal_tag_review(
    st: Any,
    llm_item: dict[str, Any],
    tag_node: dict[str, Any],
    allowlist: list[str],
    *,
    key_prefix: str,
    entity_kind: EntityKind = "domain",
) -> None:
    """Shared allowlist selectboxes for primary/secondary + new-tag approval."""
    st.markdown("**Tags**")
    primary_hint, secondary_hint = TAG_ROLE_HINTS.get(entity_kind, TAG_ROLE_HINTS["domain"])
    options = build_tag_select_options(allowlist, llm_item)

    llm_primary = normalize_tag(str(llm_item.get("primary_tag") or ""))
    llm_secondary = normalize_tag(str(llm_item.get("secondary_tag") or ""))
    suggested_new = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))

    primary_default = normalize_tag(str(tag_node.get("final_primary_tag") or "")) or llm_primary
    secondary_default = (
        normalize_tag(str(tag_node.get("final_secondary_tag") or "")) or llm_secondary
    )

    primary_idx = options.index(primary_default) if primary_default in options else 0
    secondary_idx = options.index(secondary_default) if secondary_default in options else 0

    tag_node["final_primary_tag"] = (
        st.selectbox(
            f"Primary tag — {primary_hint}",
            options=options,
            index=primary_idx,
            key=f"{key_prefix}_tag_primary",
        )
        or None
    )

    tag_node["final_secondary_tag"] = (
        st.selectbox(
            f"Secondary tag — {secondary_hint}",
            options=options,
            index=secondary_idx,
            key=f"{key_prefix}_tag_secondary",
        )
        or None
    )

    if suggested_new:
        render_similar_tags_warning(st, suggested_new, allowlist, key_prefix=key_prefix)
        st.caption(f"LLM suggested new tag: `{suggested_new}`")
        tag_node["new_tag_approved"] = st.checkbox(
            f"Approve new tag: `{suggested_new}`",
            value=bool(tag_node.get("new_tag_approved")),
            key=f"{key_prefix}_tag_new_approve",
        )
    else:
        st.caption("No new tag suggested by LLM.")


def render_proposal_evidence_type_editor(
    st: Any,
    llm_item: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Selectbox to override ``evidence_type`` on the proposal dict (edit / advanced mode)."""
    st.markdown("#### Evidence type")
    opts = list(EVIDENCE_TYPE_VALUES)
    cur = normalize_evidence_type(llm_item.get("evidence_type"))
    idx = opts.index(cur) if cur in opts else opts.index("unknown")

    def _fmt(o: str) -> str:
        return o.replace("_", " ").title()

    llm_item["evidence_type"] = st.selectbox(
        "What kind of evidence supports this proposal?",
        opts,
        index=idx,
        format_func=_fmt,
        key=f"{key_prefix}_evidence_type",
        help="Calibration only: vendor vs independent vs benchmark, etc. Does not auto-reject.",
    )


SOURCE_CHAPTER_DISPLAY_ORDER: tuple[str, ...] = (
    "summary",
    "accessible_overview",
    "key_insights",
    "why_it_matters",
    "limitations_and_open_questions",
    "contradictions_and_skepticism",
    "sources",
)

CHAPTER_LABELS: dict[str, str] = {
    "summary": "Summary",
    "accessible_overview": "Easy read",
    "key_insights": "Key insights",
    "why_it_matters": "Why it matters",
    "limitations_and_open_questions": "Limitations and open questions",
    "contradictions_and_skepticism": "Contradictions / skepticism",
    "sources": "Sources",
}

VALUE_LEVEL_EMOJI: dict[str, str] = {
    "high": "H",
    "medium": "M",
    "low": "L",
}

VALUE_LEVEL_COLOR: dict[str, str] = {
    "high": "green",
    "medium": "orange",
    "low": "red",
}


def normalize_sources_list(raw: Any) -> list[str]:
    """Return trimmed source URL/reference strings from LLM output."""
    if not isinstance(raw, list):
        return []
    return [str(s).strip() for s in raw if str(s).strip()]


def format_source_link_markdown(url: str) -> str:
    """Format one source entry as a markdown bullet (clickable when http(s))."""
    text = url.strip()
    if not text:
        return ""
    lower = text.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return f"- [{text}]({text})"
    return f"- {text}"


def _llm_list_from_summary(llm_ss: dict[str, Any], section_key: str) -> list[str]:
    raw = llm_ss.get(section_key) or []
    if not isinstance(raw, list):
        return []
    return [str(s).strip() for s in raw if str(s).strip()]


def _review_node(rev_ss: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = rev_ss.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_scalar_chapter_text(
    llm_ss: dict[str, Any],
    node: dict[str, Any],
    section_key: str,
) -> str:
    """Return reviewer-final scalar text, else the LLM draft."""
    final = node.get("final_text")
    if isinstance(final, str) and final.strip():
        return final.strip()
    return str(llm_ss.get(section_key) or "").strip()


def effective_list_chapter_lines(
    llm_ss: dict[str, Any],
    node: dict[str, Any],
    section_key: str,
) -> list[str]:
    """Return reviewer-final list lines, else ``llm_list`` or LLM draft."""
    final = node.get("final_list")
    if isinstance(final, list):
        return [str(x).strip() for x in final if str(x).strip()]
    llm_list = node.get("llm_list")
    if isinstance(llm_list, list) and llm_list:
        return [str(x).strip() for x in llm_list if str(x).strip()]
    return _llm_list_from_summary(llm_ss, section_key)


def format_chapter_body_markdown(section_key: str, body: str | list[str]) -> str:
    """Format chapter body for the read-only column."""
    if section_key == "key_insights":
        lines = body if isinstance(body, list) else []
        if not lines:
            return "*(No key insights.)*"
        return "\n".join(f"- {line}" for line in lines)
    text = body if isinstance(body, str) else ""
    return text if text else "*(empty)*"


def format_sources_chapter_markdown(urls: list[str]) -> str:
    """Format sources as markdown bullets."""
    if not urls:
        return "*(No source links extracted.)*"
    lines = [format_source_link_markdown(u) for u in urls]
    return "\n".join(line for line in lines if line)


def build_readonly_chapters_markdown(artifact: dict[str, Any]) -> str:
    """Concatenate all source chapters for uninterrupted read-only display."""
    llm_ss = (artifact.get("llm_output") or {}).get("source_summary") or {}
    rev_ss = (artifact.get("review") or {}).get("source_summary") or {}
    parts: list[str] = []
    for section_key in SOURCE_CHAPTER_DISPLAY_ORDER:
        label = CHAPTER_LABELS.get(section_key, section_key.replace("_", " ").title())
        node = _review_node(rev_ss, section_key)
        if section_key == "sources":
            urls = effective_list_chapter_lines(llm_ss, node, "sources")
            body = format_sources_chapter_markdown(urls)
        elif section_key == "key_insights":
            lines = effective_list_chapter_lines(llm_ss, node, section_key)
            body = format_chapter_body_markdown(section_key, lines)
        elif section_key in SOURCE_SUMMARY_SCALAR_KEYS:
            text = effective_scalar_chapter_text(llm_ss, node, section_key)
            body = format_chapter_body_markdown(section_key, text)
        else:
            continue
        parts.append(f"## {label}\n\n{body}")
    return "\n\n".join(parts)


def chapter_edit_textarea_value(artifact: dict[str, Any], section_key: str) -> str:
    """Default text for the per-chapter edit box."""
    llm_ss = (artifact.get("llm_output") or {}).get("source_summary") or {}
    rev_ss = (artifact.get("review") or {}).get("source_summary") or {}
    node = _review_node(rev_ss, section_key)
    if section_key == "key_insights":
        lines = effective_list_chapter_lines(llm_ss, node, section_key)
        return "\n".join(lines)
    if section_key in SOURCE_SUMMARY_SCALAR_KEYS:
        return effective_scalar_chapter_text(llm_ss, node, section_key)
    return ""


def apply_chapter_edit(artifact: dict[str, Any], section_key: str, raw_text: str) -> None:
    """Persist a chapter edit; infer ``approved`` vs ``modified`` from LLM draft."""
    llm_ss = (artifact.get("llm_output") or {}).get("source_summary") or {}
    rev_ss = artifact.setdefault("review", {}).setdefault("source_summary", {})

    if section_key == "key_insights":
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()][:5]
        llm_lines = _llm_list_from_summary(llm_ss, "key_insights")
        node = rev_ss.setdefault(
            "key_insights",
            {
                "status": "pending",
                "final_list": None,
                "notes": None,
                "llm_list": list(llm_lines),
                "section_regeneration_meta": None,
            },
        )
        if not node.get("llm_list"):
            node["llm_list"] = list(llm_lines)
        if lines == llm_lines:
            node["status"] = "approved"
            node["final_list"] = None
        else:
            node["status"] = "modified"
            node["final_list"] = lines
        return

    if section_key in SOURCE_SUMMARY_SCALAR_KEYS:
        text = raw_text.strip()
        llm_text = str(llm_ss.get(section_key) or "").strip()
        node = rev_ss.setdefault(
            section_key,
            {
                "status": "pending",
                "final_text": None,
                "notes": None,
                "section_regeneration_meta": None,
            },
        )
        if text == llm_text:
            node["status"] = "approved"
            node["final_text"] = None
        else:
            node["status"] = "modified"
            node["final_text"] = text
        return

    raise ValueError(f"Chapter not editable: {section_key}")


def _on_save_chapter_edit(section_key: str, key_prefix: str, artifact_path: Path) -> None:
    """Streamlit on_click: apply edit and persist artifact immediately."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    edit_key = f"{key_prefix}_edit_{section_key}"
    raw = str(streamlit_runtime.session_state.get(edit_key, ""))
    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    apply_chapter_edit(artifact, section_key, raw)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    label = CHAPTER_LABELS.get(section_key, section_key)
    streamlit_runtime.session_state["_chapter_save_msg"] = f"Saved **{label}**."


def _status_index(current: str) -> int:
    """Return index of ``current`` in STATUS_OPTIONS."""
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def _proposal_status_index(current: str) -> int:
    if current in PROPOSAL_STATUS_OPTIONS:
        return PROPOSAL_STATUS_OPTIONS.index(current)
    return 0


def _queue_section_regen(source_id: str, key_prefix: str, section_key: str) -> None:
    """Streamlit on_click: store pending regeneration for the app loop."""
    note_key = f"{key_prefix}_regen_note_{section_key}"
    streamlit_runtime.session_state["_pending_section_regen"] = {
        "source_id": source_id,
        "section": section_key,
        "note": str(streamlit_runtime.session_state.get(note_key, "")),
    }


def _render_analysis_meta_banner(st: Any, artifact: dict[str, Any]) -> None:
    meta = artifact.get("analysis_meta") or {}
    ts = meta.get("analysis_timestamp_utc") or "—"
    model = meta.get("model") or "—"
    pv = meta.get("prompt_version") or "—"
    st.caption(f"Full analysis: **{ts}** UTC · model `{model}` · prompt `{pv}`")


def _render_regen_meta_caption(st: Any, node: dict[str, Any]) -> None:
    meta = node.get("section_regeneration_meta")
    if isinstance(meta, dict) and meta.get("last_regen_at"):
        cnt = meta.get("regen_count", 0)
        when = meta["last_regen_at"]
        mdl = meta.get("model", "")
        pv = meta.get("prompt_version", "")
        st.caption(f"Section regen: **{cnt}×** · last **{when}** · `{mdl}` · prompt `{pv}`")


def _sync_sources_review_node(artifact: dict[str, Any]) -> None:
    """Keep sources review node auto-approved and synced with LLM list."""
    from src.ingest_review.artifact import ensure_sources_review_auto_approved

    llm_ss = (artifact.get("llm_output") or {}).get("source_summary") or {}
    rev = artifact.setdefault("review", {}).setdefault("source_summary", {})
    urls = normalize_sources_list(llm_ss.get("sources"))
    node = rev.setdefault(
        "sources",
        {
            "status": "approved",
            "final_list": None,
            "notes": None,
            "llm_list": list(urls),
            "section_regeneration_meta": None,
        },
    )
    node["llm_list"] = list(urls)
    ensure_sources_review_auto_approved(artifact)


def _render_chapter_edit_box(
    st: Any,
    artifact: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
) -> None:
    """One bordered edit box: textarea, save, regen note, regenerate."""
    rev_ss = artifact.setdefault("review", {}).setdefault("source_summary", {})
    label = CHAPTER_LABELS.get(section_key, section_key.replace("_", " ").title())
    node = _review_node(rev_ss, section_key)

    with st.container(border=True):
        st.markdown(f"**{label}**")
        _render_regen_meta_caption(st, node)
        height = 200 if section_key in ("summary", "accessible_overview", "why_it_matters") else 140
        st.text_area(
            label,
            value=chapter_edit_textarea_value(artifact, section_key),
            height=height,
            key=f"{key_prefix}_edit_{section_key}",
            label_visibility="collapsed",
        )
        save_col, regen_col = st.columns(2)
        save_col.button(
            "Save edit",
            key=f"{key_prefix}_save_{section_key}",
            on_click=_on_save_chapter_edit,
            args=(section_key, key_prefix, artifact_path),
            use_container_width=True,
        )
        if section_key in REGENERATABLE_SOURCE_SECTION_KEYS:
            st.text_input(
                "Optional note for regeneration",
                key=f"{key_prefix}_regen_note_{section_key}",
                placeholder="e.g. shorter, more skeptical",
            )
            regen_col.button(
                "Regenerate section",
                key=f"{key_prefix}_btn_regen_{section_key}",
                on_click=_queue_section_regen,
                args=(source_id, key_prefix, section_key),
                use_container_width=True,
            )


def render_source_summary_review(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
) -> None:
    """Two-column source chapters: read-only prose left, per-chapter edit boxes right."""
    st.subheader("Source chapters")
    _render_analysis_meta_banner(st, artifact)
    _sync_sources_review_node(artifact)

    save_msg = streamlit_runtime.session_state.pop("_chapter_save_msg", None)
    if save_msg:
        st.success(str(save_msg))

    read_col, edit_col = st.columns(2)
    with read_col:
        st.markdown(build_readonly_chapters_markdown(artifact))
    with edit_col:
        for sk in SOURCE_CHAPTER_DISPLAY_ORDER:
            if sk == "sources":
                continue
            _render_chapter_edit_box(
                st,
                artifact,
                section_key=sk,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
            )


def render_source_type_detection(st: Any, artifact: dict[str, Any], *, key_prefix: str) -> None:
    """Render source-type detection review."""
    rev = artifact.setdefault("review", {}).setdefault(
        "source_type_detection",
        {"status": "pending", "notes": None, "llm_item": {}, "final_item": None},
    )
    llm_item = (
        rev.get("llm_item") or artifact.get("llm_output", {}).get("source_type_detection") or {}
    )
    if not rev.get("llm_item"):
        rev["llm_item"] = dict(llm_item)
    st.subheader("Source type detection")
    detected = llm_item.get("detected_source_type") or "unknown"
    confidence = llm_item.get("confidence") or 0
    reasoning = llm_item.get("reasoning") or []
    st.metric("Detected source type", detected)
    st.caption(f"Confidence: {confidence:.0%}")
    if reasoning:
        for r in reasoning:
            st.markdown(f"- {r}")
    rev["status"] = st.selectbox(
        "Source type \u2014 status",
        STATUS_OPTIONS,
        index=_status_index(str(rev.get("status") or "pending")),
        key=f"{key_prefix}_srctype_st",
    )
    if rev["status"] == "modified":
        raw_json = st.text_area(
            "Source type \u2014 JSON override",
            value=json.dumps(llm_item, indent=2),
            height=160,
            key=f"{key_prefix}_srctype_json",
        )
        try:
            rev["final_item"] = json.loads(raw_json)
        except json.JSONDecodeError:
            st.error("Invalid JSON for source type detection")
            rev["final_item"] = None
    else:
        rev["final_item"] = None


def render_skip_extraction_screen(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> bool:
    """Show a lightweight skip-extraction confirmation when recommended.

    Returns True if the reviewer accepted the skip.
    """
    llm = artifact.get("llm_output", {})
    emeta = llm.get("extraction_meta") or {}
    if not emeta.get("skip_recommended"):
        return False

    st.warning("The LLM recommends skipping durable extraction for this article.")
    st.markdown(f"**Reason:** {emeta.get('skip_reason', '(none)')}")
    st.caption(
        f"Review burden: {emeta.get('review_burden_estimate', 'N/A')} · "
        f"Candidates considered: {emeta.get('total_candidates_considered', 0)}"
    )
    c1, c2 = st.columns(2)
    accept = c1.button("Accept skip", key=f"{key_prefix}_accept_skip")
    review_anyway = c2.button("Review anyway", key=f"{key_prefix}_review_anyway")

    if accept:
        st.session_state[f"{key_prefix}_skip_accepted"] = True
    if review_anyway:
        st.session_state[f"{key_prefix}_skip_accepted"] = False

    return bool(st.session_state.get(f"{key_prefix}_skip_accepted", False))


def render_review_summary_panel(
    st: Any,
    artifact: dict[str, Any],
) -> None:
    """Show a top-level overview of the extraction for quick orientation."""
    llm = artifact.get("llm_output") or {}
    review = artifact.get("review") or {}
    emeta = llm.get("extraction_meta") or {}

    entity_keys = [
        ("glossary", "Glossary"),
        ("topics", "Topics"),
        ("how_to", "How-tos"),
        ("industry_trends", "Trends"),
        ("tools", "Tools"),
        ("foundation_models", "Models"),
        ("implementation_studies", "Impl. studies"),
        ("roundup_signals", "Roundup signals"),
        ("interview_insights", "Interview insights"),
    ]

    total = 0
    high = 0
    medium = 0
    low = 0
    type_counts: list[str] = []

    for key, label in entity_keys:
        items = llm.get(key) or []
        if not items:
            continue
        n = len(items)
        total += n
        for item in items:
            vl = item.get("value_level", "medium") if isinstance(item, dict) else "medium"
            if vl == "high":
                high += 1
            elif vl == "low":
                low += 1
            else:
                medium += 1
        type_counts.append(f"{n} {label.lower()}")

    burden = emeta.get("review_burden_estimate", "moderate")
    st.subheader("Review overview")
    cols = st.columns(4)
    cols[0].metric("Total proposals", total)
    cols[1].metric("High value", high)
    cols[2].metric("Medium value", medium)
    cols[3].metric("Low value", low)

    ev_counts: dict[str, int] = {}
    for key, _label in entity_keys:
        items = llm.get(key) or []
        for item in items:
            if not isinstance(item, dict):
                continue
            et = normalize_evidence_type(item.get("evidence_type"))
            ev_counts[et] = ev_counts.get(et, 0) + 1
    if ev_counts and total > 0:
        parts = [f"{human_evidence_type_label(k)}: {v}" for k, v in sorted(ev_counts.items())]
        st.caption("Evidence types (LLM draft): " + " · ".join(parts))

    if type_counts:
        st.caption(f"Breakdown: {', '.join(type_counts)} · burden: {burden}")

    pending_count = 0
    for key, _ in entity_keys:
        nodes = review.get(key) or []
        for node in nodes:
            if isinstance(node, dict) and node.get("proposal_status", "pending") == "pending":
                pending_count += 1
    if pending_count > 0:
        st.info(f"{pending_count} proposal(s) still pending review")


def render_batch_actions(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Batch action buttons for fast review."""
    review = artifact.setdefault("review", {})
    entity_keys = [
        "glossary",
        "topics",
        "how_to",
        "industry_trends",
        "tools",
        "foundation_models",
        "implementation_studies",
        "roundup_signals",
        "interview_insights",
    ]

    st.markdown("#### Batch actions")
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("Approve all high-value", key=f"{key_prefix}_batch_approve_high"):
        _batch_set_proposal_status(review, entity_keys, "approved", value_filter="high")
        artifact.setdefault("review_analytics", {}).setdefault("batch_actions_used", []).append(
            "approve_all_high"
        )

    if c2.button("Reject all low-value", key=f"{key_prefix}_batch_reject_low"):
        _batch_set_proposal_status(review, entity_keys, "rejected", value_filter="low")
        artifact.setdefault("review_analytics", {}).setdefault("batch_actions_used", []).append(
            "reject_all_low"
        )

    if c3.button("Defer remaining", key=f"{key_prefix}_batch_defer"):
        _batch_set_proposal_status(review, entity_keys, "deferred", current_status_filter="pending")
        artifact.setdefault("review_analytics", {}).setdefault("batch_actions_used", []).append(
            "defer_remaining"
        )

    if c4.button("Approve all unchanged", key=f"{key_prefix}_batch_approve_unchanged"):
        _batch_set_proposal_status(review, entity_keys, "approved", current_status_filter="pending")
        artifact.setdefault("review_analytics", {}).setdefault("batch_actions_used", []).append(
            "approve_all_unchanged"
        )


def _batch_set_proposal_status(
    review: dict[str, Any],
    entity_keys: list[str],
    target_status: str,
    *,
    value_filter: str | None = None,
    current_status_filter: str | None = None,
) -> None:
    """Set proposal_status on matching nodes."""
    for key in entity_keys:
        nodes = review.get(key)
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if current_status_filter and node.get("proposal_status") != current_status_filter:
                continue
            if value_filter:
                llm_item = node.get("llm_item") or {}
                vl = llm_item.get("value_level", "medium")
                if vl != value_filter:
                    continue
            node["proposal_status"] = target_status


def render_review_timer(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Show review timer and analytics."""
    analytics = artifact.setdefault("review_analytics", {})
    started = analytics.get("review_started_at")

    if not started:
        from datetime import UTC, datetime

        analytics["review_started_at"] = datetime.now(tz=UTC).isoformat()

    duration = analytics.get("review_duration_seconds")
    if duration is not None:
        mins = int(duration) // 60
        secs = int(duration) % 60
        st.caption(f"Review time: {mins}m {secs}s")
    else:
        st.caption("Review in progress...")
