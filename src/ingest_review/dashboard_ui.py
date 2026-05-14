"""Streamlit-oriented review widgets (pass ``st`` for testability)."""

from __future__ import annotations

import json
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.schema import (
    REGENERATABLE_SOURCE_SECTION_KEYS,
    SOURCE_SUMMARY_SCALAR_KEYS,
)

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")

SOURCE_CHAPTER_DISPLAY_ORDER: tuple[str, ...] = (
    "summary",
    "key_insights",
    "why_it_matters",
    "implications_automation",
    "practical_relevance",
    "limitations_and_open_questions",
    "contradictions_and_skepticism",
    "sources",
)

PRIMARY_CHAPTERS: tuple[str, ...] = ("summary", "key_insights")

CHAPTER_LABELS: dict[str, str] = {
    "summary": "Summary",
    "key_insights": "Key insights",
    "why_it_matters": "Why it matters",
    "implications_automation": "Implications for service automation",
    "practical_relevance": "Practical relevance",
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


def _render_scalar_chapter(
    st: Any,
    artifact: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
    source_id: str,
) -> None:
    llm = artifact.get("llm_output", {}).get("source_summary") or {}
    rev = artifact.setdefault("review", {}).setdefault("source_summary", {})
    label = CHAPTER_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"### {label}")
    node = rev.setdefault(
        section_key,
        {
            "status": "pending",
            "final_text": None,
            "notes": None,
            "section_regeneration_meta": None,
        },
    )
    _render_regen_meta_caption(st, node)
    llm_text = str(llm.get(section_key) or "")
    st.markdown("**Model draft**")
    st.text(llm_text[:8000] + ("…" if len(llm_text) > 8000 else ""))
    st.text_input(
        "Optional note for regeneration",
        key=f"{key_prefix}_regen_note_{section_key}",
        placeholder="e.g. shorter, more skeptical, focus on voicebots",
    )
    if section_key in REGENERATABLE_SOURCE_SECTION_KEYS:
        st.button(
            "Regenerate section",
            key=f"{key_prefix}_btn_regen_{section_key}",
            on_click=_queue_section_regen,
            args=(source_id, key_prefix, section_key),
        )
    node["status"] = st.selectbox(
        f"{label} — status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_sum_{section_key}_st",
    )
    if node["status"] in ("modified", "pending"):
        default = node.get("final_text") if node.get("final_text") else llm_text
        node["final_text"] = st.text_area(
            f"{label} — final text",
            value=default,
            height=140,
            key=f"{key_prefix}_sum_{section_key}_txt",
        )
    elif node["status"] == "approved":
        node["final_text"] = None
    else:
        node["final_text"] = None
    node["notes"] = st.text_input(
        f"{label} — notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_sum_{section_key}_notes",
    )


def _render_list_chapter(
    st: Any,
    artifact: dict[str, Any],
    *,
    section_key: str,
    key_prefix: str,
    source_id: str,
) -> None:
    llm = artifact.get("llm_output", {}).get("source_summary") or {}
    rev = artifact.setdefault("review", {}).setdefault("source_summary", {})
    label = CHAPTER_LABELS.get(section_key, section_key.replace("_", " ").title())
    st.markdown(f"### {label}")
    llm_list = llm.get(section_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    node = rev.setdefault(
        section_key,
        {
            "status": "pending",
            "final_list": None,
            "notes": None,
            "llm_list": list(llm_list),
            "section_regeneration_meta": None,
        },
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_list)
    _render_regen_meta_caption(st, node)
    st.markdown("**Model draft (list)**")
    st.json(node["llm_list"])
    st.text_input(
        "Optional note for regeneration",
        key=f"{key_prefix}_regen_note_{section_key}",
        placeholder="e.g. fewer bullets, more operational",
    )
    if section_key in REGENERATABLE_SOURCE_SECTION_KEYS:
        st.button(
            "Regenerate section",
            key=f"{key_prefix}_btn_regen_{section_key}",
            on_click=_queue_section_regen,
            args=(source_id, key_prefix, section_key),
        )
    node["status"] = st.selectbox(
        f"{label} — status",
        STATUS_OPTIONS,
        index=_status_index(str(node.get("status") or "pending")),
        key=f"{key_prefix}_sum_{section_key}_st",
    )
    default_lines = (
        node.get("final_list") if node.get("final_list") is not None else node["llm_list"]
    )
    raw_list = st.text_area(
        f"{label} — final list (one item per line)",
        value="\n".join(str(x) for x in (default_lines or [])),
        height=120,
        key=f"{key_prefix}_sum_{section_key}_txt",
    )
    lines = [ln.strip() for ln in raw_list.splitlines() if ln.strip()]
    if section_key == "key_insights":
        lines = lines[:5]
    if node["status"] == "modified":
        node["final_list"] = lines
    elif node["status"] == "approved":
        node["final_list"] = None
    else:
        node["final_list"] = None
    node["notes"] = st.text_input(
        f"{label} — notes",
        value=str(node.get("notes") or ""),
        key=f"{key_prefix}_sum_{section_key}_notes",
    )


def render_source_summary_review(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str,
) -> None:
    """Render source summary with progressive disclosure.

    Summary and key_insights are always visible. All other chapters
    are collapsed behind an expander.
    """
    st.subheader("Source chapters")
    _render_analysis_meta_banner(st, artifact)

    for sk in PRIMARY_CHAPTERS:
        if sk in SOURCE_SUMMARY_SCALAR_KEYS:
            _render_scalar_chapter(
                st, artifact, section_key=sk, key_prefix=key_prefix, source_id=source_id
            )
        elif sk in ("key_insights", "sources"):
            _render_list_chapter(
                st, artifact, section_key=sk, key_prefix=key_prefix, source_id=source_id
            )
        st.divider()

    secondary = [sk for sk in SOURCE_CHAPTER_DISPLAY_ORDER if sk not in PRIMARY_CHAPTERS]
    with st.expander("Additional source analysis", expanded=False):
        for sk in secondary:
            if sk in SOURCE_SUMMARY_SCALAR_KEYS:
                _render_scalar_chapter(
                    st, artifact, section_key=sk, key_prefix=key_prefix, source_id=source_id
                )
            elif sk in ("key_insights", "sources"):
                _render_list_chapter(
                    st, artifact, section_key=sk, key_prefix=key_prefix, source_id=source_id
                )
            st.divider()


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
    rev["notes"] = st.text_input(
        "Source type \u2014 notes",
        value=str(rev.get("notes") or ""),
        key=f"{key_prefix}_srctype_notes",
    )


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
