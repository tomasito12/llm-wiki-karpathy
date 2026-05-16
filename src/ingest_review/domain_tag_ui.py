"""Shared Streamlit UI for multi-tag proposal routing (glossary, topics, etc.)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import render_similar_tags_warning
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.tags import normalize_tag, normalize_tag_list

DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY = "domain_tag_suggest_allowlist"

_DEFAULT_TAGS_NODE: dict[str, Any] = {
    "final_tags": [],
    "approved_new_tags": [],
}


def default_tags_node() -> dict[str, Any]:
    """Fresh review ``tags`` sub-object for multi-tag routing."""
    return {"final_tags": [], "approved_new_tags": []}


def _llm_proposed_tags(llm_item: dict[str, Any]) -> list[str]:
    raw = llm_item.get("proposed_tags")
    if isinstance(raw, list) and raw:
        return normalize_tag_list(raw, cap=0)
    legacy: list[str] = []
    for key in ("primary_tag", "secondary_tag"):
        t = normalize_tag(str(llm_item.get(key) or ""))
        if t and t not in legacy:
            legacy.append(t)
    return legacy


def _llm_suggested_new_tags(llm_item: dict[str, Any]) -> list[str]:
    raw = llm_item.get("suggested_new_tags")
    if isinstance(raw, list) and raw:
        tags = normalize_tag_list(raw, cap=0)
    else:
        tags = []
    legacy = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
    if legacy and legacy not in tags:
        tags.insert(0, legacy)
    return tags


def _stored_final_tags(tag_node: dict[str, Any]) -> list[str]:
    raw = tag_node.get("final_tags")
    if isinstance(raw, list) and raw:
        return normalize_tag_list(raw, cap=0)
    legacy: list[str] = []
    for key in ("final_primary_tag", "final_secondary_tag"):
        t = normalize_tag(str(tag_node.get(key) or ""))
        if t and t not in legacy:
            legacy.append(t)
    return legacy


def _stored_approved_new_tags(tag_node: dict[str, Any], llm_item: dict[str, Any]) -> list[str]:
    raw = tag_node.get("approved_new_tags")
    if isinstance(raw, list):
        approved = normalize_tag_list(raw, cap=0)
    elif tag_node.get("new_tag_approved"):
        approved = _llm_suggested_new_tags(llm_item)
    else:
        approved = []
    return approved


def effective_readonly_tags(
    llm_item: dict[str, Any],
    tag_node: dict[str, Any] | None,
    allowlist: list[str],
) -> list[str]:
    """Tags for read-only markdown: finals, else allowlisted LLM proposals."""
    allow = {normalize_tag(str(t)) for t in allowlist if str(t).strip()}
    tag_node = tag_node or {}
    out: list[str] = []
    for t in _stored_final_tags(tag_node):
        if t and t not in out:
            out.append(t)
    if out:
        return out
    for t in _llm_proposed_tags(llm_item):
        if t in allow and t not in out:
            out.append(t)
    return out


effective_readonly_domain_tags = effective_readonly_tags


def apply_tag_ui_to_node(
    node: dict[str, Any],
    llm_item: dict[str, Any],
    tag_ui: dict[str, Any],
    allow: set[str],
) -> None:
    """Persist tag widget values (from this script run) onto the proposal."""
    tag_node = node.setdefault("tags", default_tags_node())
    selected = normalize_tag_list(tag_ui.get("selected_allowlist") or [], cap=0)
    manual = normalize_tag_list(
        [x.strip() for x in str(tag_ui.get("manual_csv") or "").split(",") if x.strip()],
        cap=0,
    )
    final: list[str] = []
    for t in selected + manual:
        if t and t not in final:
            final.append(t)
    tag_node["final_tags"] = final

    approved_new: list[str] = []
    for t, checked in (tag_ui.get("approve_new_map") or {}).items():
        nt = normalize_tag(str(t))
        if checked and nt and nt not in approved_new:
            approved_new.append(nt)
    off_list_manual = [t for t in final if t not in allow]
    for t in off_list_manual:
        if tag_ui.get("approve_offlist") and t not in approved_new:
            approved_new.append(t)
    tag_node["approved_new_tags"] = approved_new

    if approved_new:
        existing = _llm_suggested_new_tags(llm_item)
        for t in approved_new:
            if t not in existing:
                existing.append(t)
        llm_item["suggested_new_tags"] = existing
        llm_item["suggested_new_tag"] = existing[0]


def find_review_node(
    artifact: dict[str, Any],
    proposal_id: str,
    review_list_key: str,
) -> dict[str, Any] | None:
    """Return the review node with matching proposal_id under review[review_list_key]."""
    for node in (artifact.get("review") or {}).get(review_list_key) or []:
        if isinstance(node, dict) and node.get("proposal_id") == proposal_id:
            return node
    return None


def on_suggest_domain_review_tag(
    proposal_id: str,
    key_prefix: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    label_widget_key: str,
    summary_widget_key: str,
    review_list_key: str,
    llm_fallback_label_key: str,
    llm_fallback_summary_key: str,
) -> None:
    """Streamlit on_click: LLM tag suggestion appended to suggested_new_tags."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    streamlit_runtime.session_state.pop(f"{key_prefix}_suggest_err", None)
    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    node = find_review_node(artifact, proposal_id, review_list_key)
    if not node:
        return
    llm_item = node.setdefault("llm_item", {})
    allowlist = list(streamlit_runtime.session_state.get(DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY) or [])
    label = str(streamlit_runtime.session_state.get(label_widget_key, "")).strip()
    summary = str(streamlit_runtime.session_state.get(summary_widget_key, "")).strip()
    label_eff = label or str(llm_item.get(llm_fallback_label_key) or "").strip()
    summary_eff = summary or str(llm_item.get(llm_fallback_summary_key) or "").strip()
    try:
        provider = OpenAIIngestionProvider()
        suggestions, _meta = provider.suggest_domain_review_tag(
            entity_label=label_eff,
            context_summary=summary_eff,
            allowlist=allowlist,
            model=model,
            prompt_version=prompt_version,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        streamlit_runtime.session_state[f"{key_prefix}_suggest_err"] = str(exc)
        return
    except Exception as exc:  # noqa: BLE001
        streamlit_runtime.session_state[f"{key_prefix}_suggest_err"] = str(exc)
        return

    existing = _llm_suggested_new_tags(llm_item)
    added: list[str] = []
    for s in suggestions:
        nt = normalize_tag(s)
        if nt and nt not in existing and nt not in added:
            existing.append(nt)
            added.append(nt)
    llm_item["suggested_new_tags"] = existing
    if existing:
        llm_item["suggested_new_tag"] = existing[0]
    if review_list_key == "foundation_models" and added:
        llm_item["proposed_new_type"] = added[0]
        types_node = node.setdefault("types", {})
        types_node["proposed_new_type"] = added[0]
    if added:
        streamlit_runtime.session_state[f"{key_prefix}_suggest_msg"] = (
            "Suggested tag(s): " + ", ".join(f"`{t}`" for t in added) + "."
        )
    else:
        streamlit_runtime.session_state[f"{key_prefix}_suggest_msg"] = (
            "Model returned no new tag (try manual slug or pick from allowlist)."
        )
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)


def render_domain_tag_section(
    st: Any,
    node: dict[str, Any],
    allowlist: list[str],
    *,
    key_prefix: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    review_list_key: str,
    label_widget_key: str,
    summary_widget_key: str,
    llm_fallback_label_key: str,
    llm_fallback_summary_key: str,
    section_title: str = "Tags",
) -> dict[str, Any]:
    """Multi-tag UI; returns values collected this run for :func:`apply_tag_ui_to_node`."""
    llm_item = node.setdefault("llm_item", {})
    tag_node = node.setdefault("tags", default_tags_node())
    allow_full = {normalize_tag(str(t)) for t in allowlist if str(t).strip()}
    options = sorted(allow_full)

    stored_final = _stored_final_tags(tag_node)
    llm_proposed = [t for t in _llm_proposed_tags(llm_item) if t in allow_full]
    default_sel = stored_final if stored_final else llm_proposed

    st.markdown(f"#### {section_title}")
    st.caption(
        "Add every routing tag that fits this proposal; skip weak or redundant tags. "
        "Off-list slugs can be added manually and approved for YAML export."
    )

    err = streamlit_runtime.session_state.pop(f"{key_prefix}_suggest_err", None)
    if err:
        st.warning(str(err))
    msg = streamlit_runtime.session_state.pop(f"{key_prefix}_suggest_msg", None)
    if msg:
        st.success(str(msg))

    llm_draft = _llm_proposed_tags(llm_item)
    if llm_draft:
        st.caption("LLM proposed: " + ", ".join(f"`{t}`" for t in llm_draft))

    selected = []
    if options:
        selected = st.multiselect(
            "Routing tags (from registry)",
            options=options,
            default=[t for t in default_sel if t in options],
            key=f"{key_prefix}_tags_multiselect",
            help="Select all allowlist tags that fit; no primary/secondary ordering.",
        )
    else:
        st.caption("Tag registry is empty.")

    manual_csv = st.text_input(
        "Additional tags (comma-separated, kebab-case)",
        value=", ".join(t for t in stored_final if t not in allow_full),
        key=f"{key_prefix}_tags_manual",
        help="Merged with multiselect; off-list values can be exported if approved below.",
    )

    suggested_new = _llm_suggested_new_tags(llm_item)
    approved_new = set(_stored_approved_new_tags(tag_node, llm_item))
    approve_new_map: dict[str, bool] = {}
    if suggested_new:
        st.markdown("**Suggested new registry tags**")
        for i, sug in enumerate(suggested_new):
            render_similar_tags_warning(st, sug, allowlist, key_prefix=f"{key_prefix}_sug_{i}")
            approve_new_map[sug] = st.checkbox(
                f"Include `{sug}` in YAML export",
                value=sug in approved_new,
                key=f"{key_prefix}_approve_new_{sug}",
            )

    offlist_in_manual = [
        normalize_tag(x)
        for x in manual_csv.split(",")
        if normalize_tag(x) and normalize_tag(x) not in allow_full
    ]
    approve_offlist = False
    if offlist_in_manual:
        approve_offlist = st.checkbox(
            "Include manual off-list tag(s) in YAML export",
            value=any(t in approved_new for t in offlist_in_manual),
            key=f"{key_prefix}_approve_offlist_manual",
        )

    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    st.button(
        "Suggest new registry tag (LLM)",
        key=f"{key_prefix}_suggest_tag",
        help="Appends one kebab-case tag not on the allowlist to suggested_new_tags.",
        disabled=not has_key,
        on_click=on_suggest_domain_review_tag,
        args=(
            str(node.get("proposal_id") or ""),
            key_prefix,
            artifact_path,
            model,
            prompt_version,
            label_widget_key,
            summary_widget_key,
            review_list_key,
            llm_fallback_label_key,
            llm_fallback_summary_key,
        ),
        use_container_width=True,
    )
    if not has_key:
        st.caption("Set OPENAI_API_KEY to enable LLM tag suggestion.")

    return {
        "selected_allowlist": selected,
        "manual_csv": manual_csv,
        "approve_new_map": approve_new_map,
        "approve_offlist": approve_offlist,
    }


def collect_approved_new_tags_from_review(
    artifact: dict[str, Any],
    review_list_key: str,
) -> list[str]:
    """Return approved new registry tags for YAML export from one review list."""
    tags: list[str] = []
    for node in (artifact.get("review") or {}).get(review_list_key) or []:
        if not isinstance(node, dict):
            continue
        tag_node = node.get("tags") or {}
        llm_item = node.get("llm_item") or {}
        for t in _stored_approved_new_tags(tag_node, llm_item):
            if t and t not in tags:
                tags.append(t)
    return tags


def apply_registry_types_ui_to_node(
    node: dict[str, Any],
    llm_item: dict[str, Any],
    type_ui: dict[str, Any],
    allow: set[str],
) -> None:
    """Persist model/tool type multiselect UI onto the proposal."""
    types_node = node.setdefault(
        "types",
        {"approved_types": [], "approved_new_types": [], "reviewer_types_added": []},
    )
    selected = normalize_tag_list(type_ui.get("selected_allowlist") or [], cap=0)
    manual = normalize_tag_list(
        [x.strip() for x in str(type_ui.get("manual_csv") or "").split(",") if x.strip()],
        cap=0,
    )
    final: list[str] = []
    for t in selected + manual:
        if t and t not in final:
            final.append(t)
    types_node["approved_types"] = final

    approved_new: list[str] = []
    for t, checked in (type_ui.get("approve_new_map") or {}).items():
        nt = normalize_tag(str(t))
        if checked and nt and nt not in approved_new:
            approved_new.append(nt)
    types_node["approved_new_types"] = approved_new
    if approved_new:
        llm_item["proposed_new_type"] = approved_new[0]


def render_registry_types_section(
    st: Any,
    node: dict[str, Any],
    allowlist: list[str],
    *,
    key_prefix: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    review_list_key: str,
    label_widget_key: str,
    summary_widget_key: str,
    llm_fallback_label_key: str,
    llm_fallback_summary_key: str,
    llm_proposed_key: str = "proposed_types",
    section_title: str = "Model types",
) -> dict[str, Any]:
    """Multi-select registry types (foundation models / tools pattern)."""
    llm_item = node.setdefault("llm_item", {})
    types_node = node.setdefault(
        "types",
        {"approved_types": [], "approved_new_types": [], "reviewer_types_added": []},
    )
    allow_full = {normalize_tag(str(t)) for t in allowlist if str(t).strip()}
    options = sorted(allow_full)

    stored = normalize_tag_list(types_node.get("approved_types") or [], cap=0)
    proposed_raw = llm_item.get(llm_proposed_key) or []
    proposed = normalize_tag_list(proposed_raw, cap=0) if isinstance(proposed_raw, list) else []
    default_sel = stored if stored else [t for t in proposed if t in allow_full]

    st.markdown(f"#### {section_title}")
    st.caption(
        "Select every registry type that fits; skip weak matches. "
        "Approve new types for YAML export when the registry lacks a label."
    )

    if proposed:
        st.caption("LLM proposed: " + ", ".join(f"`{t}`" for t in proposed))

    selected: list[str] = []
    if options:
        selected = st.multiselect(
            "Types (from registry)",
            options=options,
            default=[t for t in default_sel if t in options],
            key=f"{key_prefix}_types_multiselect",
        )
    else:
        st.caption("Type registry is empty.")

    manual_csv = st.text_input(
        "Additional types (comma-separated)",
        value=", ".join(t for t in stored if t not in allow_full),
        key=f"{key_prefix}_types_manual",
    )

    llm_new = normalize_tag(str(llm_item.get("proposed_new_type") or ""))
    snt = _llm_suggested_new_tags(llm_item)
    existing = types_node.get("proposed_new_type") or llm_new or (snt[0] if snt else "")
    suggested_new = normalize_tag(str(existing)) if existing else ""
    approved_new = set(normalize_tag_list(types_node.get("approved_new_types") or [], cap=0))
    approve_new_map: dict[str, bool] = {}
    if suggested_new:
        render_similar_tags_warning(
            st, suggested_new, allowlist, key_prefix=f"{key_prefix}_type_sug"
        )
        approve_new_map[suggested_new] = st.checkbox(
            f"Include new type `{suggested_new}` in YAML export",
            value=suggested_new in approved_new,
            key=f"{key_prefix}_approve_new_type",
        )

    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    st.button(
        "Suggest new registry type (LLM)",
        key=f"{key_prefix}_suggest_type",
        disabled=not has_key,
        on_click=on_suggest_domain_review_tag,
        args=(
            str(node.get("proposal_id") or ""),
            key_prefix,
            artifact_path,
            model,
            prompt_version,
            label_widget_key,
            summary_widget_key,
            review_list_key,
            llm_fallback_label_key,
            llm_fallback_summary_key,
        ),
        use_container_width=True,
    )

    return {
        "selected_allowlist": selected,
        "manual_csv": manual_csv,
        "approve_new_map": approve_new_map,
        "approve_offlist": False,
    }
