"""Streamlit-oriented review widgets (pass ``st`` for testability)."""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.evidence import (
    collect_effective_evidence_counts,
    proposal_evidence_override_raw,
    source_primary_evidence_type,
)
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

TAG_SELECT_HELP: dict[str, tuple[str, str]] = {
    "domain": (
        "Pick the main wiki routing bucket for this entry (one allowlist tag). This is the "
        "primary strategic domain—e.g. safety, orchestration, evaluation—not a narrow phrasing "
        "of the term itself.",
        "Optional second allowlist tag only when the entry clearly belongs to another "
        "cross-cutting theme as well (not a synonym or minor variant of primary).",
    ),
    "tool": (
        "Primary category from the tool types allowlist.",
        "Optional adjacent operational or classification tag from the allowlist.",
    ),
    "model": (
        "Deployment or openness class from the model types allowlist.",
        "Optional capability focus from the allowlist.",
    ),
}


def google_search_markdown(query: str) -> str:
    """Markdown link that opens a Google search for *query* (empty if query is blank)."""
    if not query.strip():
        return ""
    url = "https://www.google.com/search?" + urllib.parse.urlencode({"q": query.strip()})
    label = query.strip()
    return f'[Google: "{label}"]({url})'


STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

PROPOSAL_STATUS_OPTIONS = ("pending", "approved", "rejected", "deferred")
INHERIT_EVIDENCE_VALUE = "__inherit__"


def human_evidence_type_label(raw: object) -> str:
    """Title-case evidence type for display (e.g. ``vendor_claim`` → Vendor Claim)."""
    return normalize_evidence_type(raw).replace("_", " ").title()


def _caption_tag_list(tag_node: dict[str, Any], llm_item: dict[str, Any]) -> list[str]:
    raw = tag_node.get("final_tags")
    if isinstance(raw, list) and raw:
        return [normalize_tag(str(t)) for t in raw if normalize_tag(str(t))]
    legacy: list[str] = []
    for key in ("final_primary_tag", "final_secondary_tag"):
        t = normalize_tag(str(tag_node.get(key) or ""))
        if t and t not in legacy:
            legacy.append(t)
    if legacy:
        return legacy
    proposed = llm_item.get("proposed_tags")
    if isinstance(proposed, list) and proposed:
        return [normalize_tag(str(t)) for t in proposed if normalize_tag(str(t))]
    for key in ("primary_tag", "secondary_tag"):
        t = normalize_tag(str(llm_item.get(key) or ""))
        if t and t not in legacy:
            legacy.append(t)
    return legacy


def _caption_suggested_new(llm_item: dict[str, Any]) -> list[str]:
    raw = llm_item.get("suggested_new_tags")
    if isinstance(raw, list) and raw:
        out = [normalize_tag(str(t)) for t in raw if normalize_tag(str(t))]
    else:
        out = []
    legacy = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
    if legacy and legacy not in out:
        out.insert(0, legacy)
    return out


def format_proposed_tags_caption(
    llm_item: dict[str, Any],
    tag_node: dict[str, Any] | None,
    allowlist: list[str],
) -> str | None:
    """Compact caption for multi-tag routing with allowlist vs proposed-new provenance."""
    allow_set = {normalize_tag(t) for t in allowlist}
    tag_node = tag_node or {}
    shown: set[str] = set()
    parts: list[str] = []
    for t in _caption_tag_list(tag_node, llm_item):
        if not t or t in shown:
            continue
        shown.add(t)
        provenance = "allowlist" if t in allow_set else "outside allowlist"
        parts.append(f"{t} ({provenance})")
    for sug in _caption_suggested_new(llm_item):
        if sug and sug not in shown:
            shown.add(sug)
            parts.append(f"{sug} (suggested new)")
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
    help_primary, help_secondary = TAG_SELECT_HELP.get(entity_kind, TAG_SELECT_HELP["domain"])
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
            help=help_primary,
        )
        or None
    )

    tag_node["final_secondary_tag"] = (
        st.selectbox(
            f"Secondary tag — {secondary_hint}",
            options=options,
            index=secondary_idx,
            key=f"{key_prefix}_tag_secondary",
            help=help_secondary,
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


def format_proposal_meta_subtitle(
    artifact: dict[str, Any],
    node: dict[str, Any],
    llm_item: dict[str, Any],
    *,
    badge: str,
    confidence: float | None = None,
    extra_parts: list[str] | None = None,
) -> str:
    """Build italic subtitle line (value tier, status, optional override, confidence)."""
    from src.ingest_review.evidence import proposal_evidence_subtitle_part
    from src.ingest_review.proposal_decision_ui import proposal_status_label

    parts = [badge, proposal_status_label(node)]
    if extra_parts:
        parts.extend(extra_parts)
    ev_part = proposal_evidence_subtitle_part(artifact, llm_item)
    if ev_part:
        parts.append(ev_part)
    if confidence is not None:
        parts.append(f"{confidence:.0%}")
    return "*" + " · ".join(parts) + "*"


def render_proposal_evidence_type_editor(
    st: Any,
    llm_item: dict[str, Any],
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Selectbox to inherit source evidence profile or set a per-proposal override."""
    primary = source_primary_evidence_type(artifact)
    inherit_label = f"Inherit from source ({human_evidence_type_label(primary)})"
    opts = [INHERIT_EVIDENCE_VALUE, *EVIDENCE_TYPE_VALUES]
    cur_override = proposal_evidence_override_raw(llm_item)
    cur = cur_override if cur_override is not None else INHERIT_EVIDENCE_VALUE
    idx = opts.index(cur) if cur in opts else 0

    def _fmt(o: str) -> str:
        if o == INHERIT_EVIDENCE_VALUE:
            return inherit_label
        return o.replace("_", " ").title()

    selected = st.selectbox(
        "Evidence basis for this proposal",
        opts,
        index=idx,
        format_func=_fmt,
        key=f"{key_prefix}_evidence_type",
        help="Most proposals inherit the source-level evidence profile. Override only "
        "when this extraction clearly differs.",
    )
    if selected == INHERIT_EVIDENCE_VALUE:
        llm_item.pop("evidence_type", None)
    else:
        llm_item["evidence_type"] = selected


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


SOURCE_CHAPTER_OTHER_KEYS: tuple[str, ...] = tuple(
    sk for sk in SOURCE_CHAPTER_DISPLAY_ORDER if sk not in ("accessible_overview", "sources")
)


def render_source_summary_review(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
) -> None:
    """Fast source-chapter review: Easy read primary; other chapters collapsed."""
    st.subheader("Source chapters")
    _render_analysis_meta_banner(st, artifact)
    _sync_sources_review_node(artifact)

    save_msg = streamlit_runtime.session_state.pop("_chapter_save_msg", None)
    if save_msg:
        st.success(str(save_msg))

    st.markdown(f"## {CHAPTER_LABELS['accessible_overview']}")
    _render_chapter_edit_box(
        st,
        artifact,
        section_key="accessible_overview",
        key_prefix=key_prefix,
        source_id=source_id,
        artifact_path=artifact_path,
    )

    with st.expander("Other chapters", expanded=False):
        for sk in SOURCE_CHAPTER_OTHER_KEYS:
            _render_chapter_edit_box(
                st,
                artifact,
                section_key=sk,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
            )


def render_source_evidence_profile(st: Any, artifact: dict[str, Any], *, key_prefix: str) -> None:
    """Render source-level evidence profile (dominant basis for the whole source)."""
    rev = artifact.setdefault("review", {}).setdefault(
        "source_evidence_profile",
        {"status": "pending", "notes": None, "llm_item": {}, "final_item": None},
    )
    llm_out = artifact.get("llm_output") or {}
    llm_item = rev.get("llm_item") or llm_out.get("source_evidence_profile") or {}
    if not rev.get("llm_item"):
        rev["llm_item"] = dict(llm_item)
    if not llm_out.get("source_evidence_profile"):
        llm_out["source_evidence_profile"] = dict(llm_item)

    primary = normalize_evidence_type(llm_item.get("primary_evidence_type"))
    reasoning = llm_item.get("reasoning") or []

    st.subheader("Source evidence profile")
    st.caption(
        "Dominant evidence basis for this source. Individual proposals inherit this "
        "unless given an explicit override."
    )
    opts = list(EVIDENCE_TYPE_VALUES)

    def _fmt(o: str) -> str:
        return o.replace("_", " ").title()

    new_primary = st.selectbox(
        "Primary evidence type",
        opts,
        index=opts.index(primary) if primary in opts else opts.index("unknown"),
        format_func=_fmt,
        key=f"{key_prefix}_src_evidence_primary",
    )
    llm_item["primary_evidence_type"] = new_primary
    llm_out["source_evidence_profile"] = dict(llm_item)
    rev["llm_item"] = dict(llm_item)

    if reasoning:
        st.markdown("**LLM reasoning**")
        for r in reasoning:
            st.markdown(f"- {r}")

    rev["status"] = st.selectbox(
        "Source evidence \u2014 review status",
        STATUS_OPTIONS,
        index=_status_index(str(rev.get("status") or "pending")),
        key=f"{key_prefix}_src_evidence_st",
    )
    rev["notes"] = st.text_area(
        "Source evidence \u2014 notes",
        value=str(rev.get("notes") or ""),
        key=f"{key_prefix}_src_evidence_notes",
    )
    if rev["status"] == "modified":
        raw_json = st.text_area(
            "Source evidence \u2014 JSON override",
            value=json.dumps(llm_item, indent=2),
            height=120,
            key=f"{key_prefix}_src_evidence_json",
        )
        try:
            rev["final_item"] = json.loads(raw_json)
        except json.JSONDecodeError:
            st.error("Invalid JSON for source evidence profile")
            rev["final_item"] = None
    else:
        rev["final_item"] = None


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
    source_title: str = "",
) -> str | None:
    """Show skip-gate choices when entity extraction was skipped or declined.

    Returns:
    - ``None``: not in skip state, or reviewer has not chosen yet
    - ``\"source_only\"``: keep source chapters; optional forced single-item extracts
    - ``\"full\"``: run / show full entity extraction workflow
    """
    llm = artifact.get("llm_output", {})
    detection = llm.get("source_type_detection") or {}
    detected_type = str(detection.get("detected_source_type") or "")
    from src.ingest_review.schema import LIST_ROUNDUP_SOURCE_TYPES

    if detected_type in LIST_ROUNDUP_SOURCE_TYPES:
        st.info(
            "List roundup: extract every tool or practice and reject unwanted items in the "
            "Tools or How-tos tab—skip is not applied for this source type."
        )
        return None

    emeta = llm.get("extraction_meta") or {}
    if not emeta.get("skip_recommended"):
        return None

    mode_key = f"{key_prefix}_review_mode"
    # Legacy session key from older dashboard builds
    if f"{key_prefix}_skip_accepted" in st.session_state and mode_key not in st.session_state:
        legacy = st.session_state.pop(f"{key_prefix}_skip_accepted")
        st.session_state[mode_key] = "source_only" if legacy else "full"

    st.warning("The LLM recommends skipping durable extraction for this article.")
    st.markdown(f"**Reason:** {emeta.get('skip_reason', '(none)')}")
    st.caption(
        f"Review burden: {emeta.get('review_burden_estimate', 'N/A')} · "
        f"Candidates considered: {emeta.get('total_candidates_considered', 0)}"
    )

    chosen = st.session_state.get(mode_key)
    if chosen in ("source_only", "full"):
        if chosen == "source_only":
            st.info(
                "**Source-only mode** — review source chapters below. Use **Force extract** "
                "to add individual topics, trends, or tools without re-running full extraction."
            )
        return str(chosen)

    st.markdown(
        "You can still keep this article in your knowledge base (source summary only), "
        "force individual extractions, or run full entity extraction."
    )
    c1, c2, c3 = st.columns(3)
    if c1.button("Keep source only", key=f"{key_prefix}_mode_source_only", type="primary"):
        st.session_state[mode_key] = "source_only"
        from src.ingest_review.force_extract_ui import source_summary_is_empty

        if source_summary_is_empty(artifact):
            st.session_state["_pending_source_summary_refresh"] = str(
                (artifact.get("source") or {}).get("source_id") or key_prefix
            )
        st.rerun()
    if c2.button("Extract all entities", key=f"{key_prefix}_mode_full"):
        st.session_state[mode_key] = "full"
        st.rerun()
    if c3.button("Decide later", key=f"{key_prefix}_mode_later"):
        st.session_state[mode_key] = "source_only"
        from src.ingest_review.force_extract_ui import source_summary_is_empty

        if source_summary_is_empty(artifact):
            st.session_state["_pending_source_summary_refresh"] = str(
                (artifact.get("source") or {}).get("source_id") or key_prefix
            )
        st.rerun()

    from src.ingest_review.force_extract_ui import render_force_extract_panel

    default_title = source_title
    if ":" in default_title:
        default_title = default_title.split(":", 1)[-1].strip()
    render_force_extract_panel(
        st,
        source_id=str((artifact.get("source") or {}).get("source_id") or key_prefix),
        key_prefix=f"{key_prefix}_skip_gate",
        default_entity_key="topic",
        default_title=default_title,
        compact=True,
    )
    return None


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

    profile = llm.get("source_evidence_profile") or {}
    primary = normalize_evidence_type(profile.get("primary_evidence_type"))
    if primary != "unknown":
        st.caption(f"Source evidence profile: **{human_evidence_type_label(primary)}**")
    ev_counts = collect_effective_evidence_counts(artifact)
    override_n = sum(
        1
        for key, _ in entity_keys
        for node in (review.get(key) or [])
        if isinstance(node, dict)
        and isinstance(node.get("llm_item"), dict)
        and proposal_evidence_override_raw(node["llm_item"]) is not None
    )
    if override_n:
        st.caption(f"{override_n} proposal(s) with evidence override")
    if ev_counts and total > 0 and len(ev_counts) > 1:
        parts = [f"{human_evidence_type_label(k)}: {v}" for k, v in sorted(ev_counts.items())]
        st.caption("Effective evidence mix: " + " · ".join(parts))

    if type_counts:
        st.caption(f"Breakdown: {', '.join(type_counts)} · burden: {burden}")

    rejected_count = 0
    for key, _ in entity_keys:
        nodes = review.get(key) or []
        for node in nodes:
            if isinstance(node, dict) and node.get("proposal_status") == "rejected":
                rejected_count += 1
    if rejected_count > 0:
        st.info(f"{rejected_count} proposal(s) rejected — edit or approve from each card.")


def render_review_timer(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Show review timer and analytics."""
    from src.ingest_review.artifact import ensure_review_started

    ensure_review_started(artifact)
    analytics = artifact.setdefault("review_analytics", {})

    duration = analytics.get("review_duration_seconds")
    if duration is not None:
        mins = int(duration) // 60
        secs = int(duration) % 60
        st.caption(f"Review time: {mins}m {secs}s")
    else:
        st.caption("Review in progress...")


def review_timer_caption(artifact: dict[str, Any]) -> str:
    """One-line review timer for compact chrome."""
    from src.ingest_review.artifact import ensure_review_started

    ensure_review_started(artifact)
    analytics = artifact.setdefault("review_analytics", {})
    duration = analytics.get("review_duration_seconds")
    if duration is not None:
        mins = int(duration) // 60
        secs = int(duration) % 60
        return f"Review time: {mins}m {secs}s"
    return "Review in progress…"


def review_overview_caption(artifact: dict[str, Any]) -> str:
    """One-line proposal count summary for compact chrome."""
    llm = artifact.get("llm_output") or {}
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
    total = sum(len(llm.get(key) or []) for key in entity_keys)
    high = sum(
        1
        for key in entity_keys
        for item in (llm.get(key) or [])
        if isinstance(item, dict) and item.get("value_level") == "high"
    )
    rejected = sum(
        1
        for key in entity_keys
        for node in ((artifact.get("review") or {}).get(key) or [])
        if isinstance(node, dict) and node.get("proposal_status") == "rejected"
    )
    parts = [f"{total} proposals", f"{high} high value"]
    if rejected:
        parts.append(f"{rejected} rejected")
    return " · ".join(parts)


def render_compact_review_stats(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Collapsed review timer + overview metrics (replaces full-width panels)."""
    with st.expander("Review stats", expanded=False):
        st.caption(review_overview_caption(artifact))
        render_review_timer(st, artifact, key_prefix=key_prefix)


ENTITY_TABS_WITH_PROPOSAL_AUTOSAVE: frozenset[str] = frozenset(
    {
        "Glossary",
        "Topics",
        "How-tos",
        "Trends",
        "Tools",
        "Models",
        "Impl studies",
        "Signals",
        "Insights",
    }
)


REVIEW_TAB_COUNTS: dict[str, str | None] = {
    "Source chapters": None,
    "Glossary": "glossary",
    "Topics": "topics",
    "How-tos": "how_to",
    "Trends": "industry_trends",
    "Tools": "tools",
    "Models": "foundation_models",
    "Impl studies": "implementation_studies",
    "Signals": "roundup_signals",
    "Insights": "interview_insights",
    "Source type": None,
    "Debug": None,
}


def format_review_entity_tab_label(tab: str, artifact: dict[str, Any]) -> str:
    """Tab label with pending proposal count when cheap to compute."""
    review_key = REVIEW_TAB_COUNTS.get(tab)
    if not review_key:
        return tab
    count = len((artifact.get("review") or {}).get(review_key) or [])
    if count <= 0:
        return tab
    return f"{tab} ({count})"


def normalize_review_entity_tab(label: str) -> str:
    """Strip `` (N)`` suffix from radio option labels."""
    if " (" in label and label.endswith(")"):
        return label.rsplit(" (", 1)[0]
    return label


def build_review_entity_tab_options(artifact: dict[str, Any], tabs: tuple[str, ...]) -> list[str]:
    """Build radio options with optional proposal counts."""
    return [format_review_entity_tab_label(tab, artifact) for tab in tabs]


def render_source_type_override_panel(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    doc: Any,
    wiki_root: Path,
    reviews_root: Path,
    tool_types: list[str],
    howto_tags: list[str],
    impl_study_tags: list[str],
    glossary_tags: list[str],
    topic_tags: list[str],
    trend_tags: list[str],
    model_types: list[str],
    tool_tags: list[str],
    model_tags: list[str],
    extraction_budgets: dict[str, Any],
    model: str,
    prompt_version: str,
) -> None:
    """Source-type override and re-analyze (shown on Source type tab only)."""
    import os
    import traceback

    from src.ingest_review.analyze import run_classification
    from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider

    llm_detection = (artifact.get("llm_output") or {}).get("source_type_detection") or {}
    detected_type = llm_detection.get("detected_source_type") or "unknown"
    detection_conf = llm_detection.get("confidence") or 0
    detection_reasons = llm_detection.get("reasoning") or []
    source_type_options: list[str] = [
        "standard_article",
        "ai_industry_roundup",
        "ai_tools_roundup",
        "how_to_roundup",
        "interview_or_transcript",
        "technical_howto",
        "research_paper_or_report",
        "unknown",
    ]
    st.markdown(f"**Detected source type:** `{detected_type}` (confidence: {detection_conf:.0%})")
    if detection_reasons:
        for r in detection_reasons:
            st.caption(f"- {r}")
    override_val = st.selectbox(
        "Override source type",
        options=["(keep detected)"] + source_type_options,
        index=0,
        key=f"{key_prefix}_srctype_override",
    )
    if override_val != "(keep detected)" and st.button(
        "Re-analyze with override",
        key=f"{key_prefix}_reanalyze_override",
    ):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY is not set.")
        else:
            try:
                provider = OpenAIIngestionProvider()
                artifact_new, _parsed = run_classification(
                    provider,
                    doc,
                    wiki_root=wiki_root,
                    tool_types=tool_types,
                    howto_tags=howto_tags,
                    impl_study_tags=impl_study_tags,
                    glossary_tags=glossary_tags,
                    topic_tags=topic_tags,
                    trend_tags=trend_tags,
                    model_types=model_types,
                    tool_tags=tool_tags,
                    model_tags=model_tags,
                    extraction_budgets=extraction_budgets,
                    source_type_override=str(override_val),
                    model=model,
                    prompt_version=prompt_version,
                    reviews_root=reviews_root,
                )
                streamlit_runtime.session_state["artifact"] = artifact_new
                source_id = str((artifact.get("source") or {}).get("source_id") or "")
                if source_id:
                    streamlit_runtime.session_state["artifact_source_id"] = source_id
                st.success(f"Re-analysis complete (override: {override_val}).")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Re-analysis failed: {exc}")
                with st.expander("Traceback"):
                    st.text(traceback.format_exc())
