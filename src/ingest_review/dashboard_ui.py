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


def _status_index(current: str) -> int:
    """Return index of ``current`` in STATUS_OPTIONS."""
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
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


def _render_regen_meta_caption(st: Any, node: dict[str, Any]) -> None:
    meta = node.get("section_regeneration_meta")
    if isinstance(meta, dict) and meta.get("last_regen_at"):
        cnt = meta.get("regen_count", 0)
        when = meta["last_regen_at"]
        mdl = meta.get("model", "")
        pv = meta.get("prompt_version", "")
        st.caption(f"Section regen: **{cnt}×** · last **{when}** · `{mdl}` · prompt `{pv}`")


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
    if section_key == "key_insights":
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
    else:
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
    """Render review controls for ``source_summary`` chapters."""
    st.subheader("Source chapters")
    _render_analysis_meta_banner(st, artifact)
    for sk in SOURCE_CHAPTER_DISPLAY_ORDER:
        if sk in SOURCE_SUMMARY_SCALAR_KEYS:
            _render_scalar_chapter(
                st, artifact, section_key=sk, key_prefix=key_prefix, source_id=source_id
            )
        elif sk in ("key_insights", "sources"):
            _render_list_chapter(
                st, artifact, section_key=sk, key_prefix=key_prefix, source_id=source_id
            )
        st.divider()


def render_roundup_review(st: Any, artifact: dict[str, Any], *, key_prefix: str) -> None:
    """Render roundup detection review."""
    rev = artifact.setdefault("review", {}).setdefault(
        "roundup",
        {"status": "pending", "notes": None, "llm_item": {}, "final_item": None},
    )
    llm_item = rev.get("llm_item") or artifact.get("llm_output", {}).get("roundup") or {}
    if not rev.get("llm_item"):
        rev["llm_item"] = dict(llm_item)
    st.subheader("Roundup detection")
    st.json(llm_item)
    rev["status"] = st.selectbox(
        "Roundup — status",
        STATUS_OPTIONS,
        index=_status_index(str(rev.get("status") or "pending")),
        key=f"{key_prefix}_roundup_st",
    )
    if rev["status"] == "modified":
        raw_json = st.text_area(
            "Roundup — JSON override",
            value=json.dumps(llm_item, indent=2),
            height=160,
            key=f"{key_prefix}_roundup_json",
        )
        try:
            rev["final_item"] = json.loads(raw_json)
        except json.JSONDecodeError:
            st.error("Invalid JSON for roundup")
            rev["final_item"] = None
    else:
        rev["final_item"] = None
    rev["notes"] = st.text_input(
        "Roundup — notes",
        value=str(rev.get("notes") or ""),
        key=f"{key_prefix}_roundup_notes",
    )


def _render_proposal_list(
    st: Any,
    artifact: dict[str, Any],
    *,
    review_key: str,
    title: str,
    key_prefix: str,
    tag_allowlist: list[str] | None,
) -> None:
    """Generic list renderer for glossary, tools, models, etc."""
    items = artifact.setdefault("review", {}).setdefault(review_key, [])
    llm_items = artifact.get("llm_output", {}).get(review_key) or []
    st.subheader(title)
    if not items:
        st.caption("No proposals.")
        return
    for i, node in enumerate(items):
        llm_item = llm_items[i] if i < len(llm_items) else {}
        with st.expander(f"{title} #{i + 1}", expanded=False):
            st.json(llm_item)
            node["status"] = st.selectbox(
                f"Item {i + 1} status",
                STATUS_OPTIONS,
                index=_status_index(str(node.get("status") or "pending")),
                key=f"{key_prefix}_{review_key}_{i}_st",
            )
            if tag_allowlist is not None and isinstance(llm_item, dict):
                current = [t for t in (llm_item.get("proposed_tags") or []) if t in tag_allowlist]
                chosen = st.multiselect(
                    "Tags (allowlist)",
                    options=tag_allowlist,
                    default=current,
                    key=f"{key_prefix}_{review_key}_{i}_tags",
                )
                extra = st.text_input(
                    "Reviewer tags (comma-separated, not validated)",
                    value=", ".join(node.get("reviewer_tags_added") or []),
                    key=f"{key_prefix}_{review_key}_{i}_extra",
                )
                node["reviewer_tags_added"] = [x.strip() for x in extra.split(",") if x.strip()]
                node["approved_allowlist_tags"] = chosen
                base = dict(llm_item)
                base["proposed_tags"] = chosen + node["reviewer_tags_added"]
            else:
                base = dict(llm_item) if isinstance(llm_item, dict) else {}
                node.setdefault("reviewer_tags_added", [])

            if node["status"] == "modified":
                raw = st.text_area(
                    "Full item JSON (edit as needed)",
                    value=json.dumps(base, indent=2),
                    height=220,
                    key=f"{key_prefix}_{review_key}_{i}_json",
                )
                try:
                    node["final_item"] = json.loads(raw)
                except json.JSONDecodeError:
                    st.error("Invalid JSON")
            elif node["status"] == "approved":
                node["final_item"] = base if tag_allowlist is not None else None
            else:
                node["final_item"] = None
            node["notes"] = st.text_input(
                "Notes",
                value=str(node.get("notes") or ""),
                key=f"{key_prefix}_{review_key}_{i}_notes",
            )


def render_all_proposal_sections(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    tool_tags: list[str],
    howto_tags: list[str],
) -> None:
    """Render all classification list sections."""
    _render_proposal_list(
        st,
        artifact,
        review_key="tools",
        title="Tools",
        key_prefix=key_prefix,
        tag_allowlist=tool_tags,
    )
    _render_proposal_list(
        st,
        artifact,
        review_key="foundation_models",
        title="Foundation models",
        key_prefix=key_prefix,
        tag_allowlist=None,
    )
    _render_proposal_list(
        st,
        artifact,
        review_key="how_to",
        title="How-to",
        key_prefix=key_prefix,
        tag_allowlist=howto_tags,
    )
    _render_proposal_list(
        st,
        artifact,
        review_key="industry_trends",
        title="Industry trends",
        key_prefix=key_prefix,
        tag_allowlist=None,
    )
