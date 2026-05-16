"""Shared Streamlit UI for domain-entity primary/secondary tags (glossary, topics, etc.)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    TAG_ROLE_HINTS,
    TAG_SELECT_HELP,
    render_similar_tags_warning,
)
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.tags import normalize_tag

# Session key for allowlist used by LLM suggest callback (set by each entity tab).
DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY = "domain_tag_suggest_allowlist"


def allowlist_select_options(allowlist: list[str]) -> list[str]:
    """Select options: empty string plus each allowlist tag once (no off-list LLM slugs)."""
    options: list[str] = [""]
    seen: set[str] = set()
    for t in allowlist:
        nt = normalize_tag(str(t))
        if nt and nt not in seen:
            seen.add(nt)
            options.append(nt)
    return options


def split_dropdown_and_manual(
    stored: str,
    llm: str,
    allow: set[str],
) -> tuple[str, str]:
    """Return (dropdown value from allowlist, manual override) from stored final + LLM draft."""
    st_n = normalize_tag(stored)
    lm = normalize_tag(llm)
    if st_n:
        if st_n in allow:
            return st_n, ""
        return "", st_n
    if lm in allow:
        return lm, ""
    return "", ""


def effective_readonly_domain_tags(
    llm_item: dict[str, Any],
    tag_node: dict[str, Any] | None,
    allowlist: list[str],
) -> list[str]:
    """Tags for read-only markdown: finals, else LLM values only when on allowlist."""
    allow = {normalize_tag(str(t)) for t in allowlist if str(t).strip()}
    tag_node = tag_node or {}
    out: list[str] = []
    for fk, lk in (
        ("final_primary_tag", "primary_tag"),
        ("final_secondary_tag", "secondary_tag"),
    ):
        final_v = normalize_tag(str(tag_node.get(fk) or ""))
        llm_v = normalize_tag(str(llm_item.get(lk) or ""))
        chosen = final_v or (llm_v if llm_v in allow else "")
        if chosen and chosen not in out:
            out.append(chosen)
    return out


def apply_tag_ui_to_node(
    node: dict[str, Any],
    llm_item: dict[str, Any],
    tag_ui: dict[str, Any],
    allow: set[str],
) -> None:
    """Persist tag widget values (from this script run) onto the proposal."""
    tag_node = node.setdefault(
        "tags",
        {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
    )
    sel_p = normalize_tag(str(tag_ui.get("sel_p") or ""))
    man_p = normalize_tag(str(tag_ui.get("man_p") or ""))
    tag_node["final_primary_tag"] = (man_p or sel_p) or None
    sel_s = normalize_tag(str(tag_ui.get("sel_s") or ""))
    man_s = normalize_tag(str(tag_ui.get("man_s") or ""))
    tag_node["final_secondary_tag"] = (man_s or sel_s) or None

    fp = normalize_tag(str(tag_node.get("final_primary_tag") or ""))
    fs = normalize_tag(str(tag_node.get("final_secondary_tag") or ""))
    custom_reg = bool(tag_ui.get("custom_reg"))
    llm_sug = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
    llm_ok = bool(tag_ui.get("llm_suggested_approve"))

    off_list = [t for t in (fp, fs) if t and t not in allow]

    if custom_reg and off_list:
        llm_item["suggested_new_tag"] = off_list[0]
        tag_node["new_tag_approved"] = True
    elif llm_ok and llm_sug:
        tag_node["new_tag_approved"] = True
    else:
        tag_node["new_tag_approved"] = False


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
    """Streamlit on_click: LLM tag suggestion; reads widget text from session_state keys."""
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
        sug, _meta = provider.suggest_domain_review_tag(
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
    if sug:
        llm_item["suggested_new_tag"] = sug
        streamlit_runtime.session_state[f"{key_prefix}_suggest_msg"] = f"Suggested tag `{sug}`."
    else:
        streamlit_runtime.session_state[f"{key_prefix}_suggest_msg"] = (
            "Model returned no new tag (try manual custom slug or pick from allowlist)."
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
) -> dict[str, Any]:
    """Tags UI shared by glossary/topics; returns values for this run.

    *label_widget_key* / *summary_widget_key* must match st.text_area keys used elsewhere
    (for LLM suggest context).
    """
    llm_item = node.setdefault("llm_item", {})
    tag_node = node.setdefault(
        "tags",
        {"final_primary_tag": None, "final_secondary_tag": None, "new_tag_approved": False},
    )
    allow_full = {normalize_tag(str(t)) for t in allowlist if str(t).strip()}
    opts = allowlist_select_options(allowlist)
    llm_p = normalize_tag(str(llm_item.get("primary_tag") or ""))
    llm_s = normalize_tag(str(llm_item.get("secondary_tag") or ""))
    stored_p = normalize_tag(str(tag_node.get("final_primary_tag") or ""))
    stored_s = normalize_tag(str(tag_node.get("final_secondary_tag") or ""))
    dd_p, man_p0 = split_dropdown_and_manual(stored_p, llm_p, allow_full)
    dd_s, man_s0 = split_dropdown_and_manual(stored_s, llm_s, allow_full)

    primary_hint, secondary_hint = TAG_ROLE_HINTS["domain"]
    help_primary, help_secondary = TAG_SELECT_HELP["domain"]
    st.markdown("#### Tags")
    st.caption(
        "Primary = main strategic routing bucket on the allowlist. Secondary = optional "
        "second theme if clearly cross-cutting. Manual kebab-case overrides the dropdown when set."
    )

    err = streamlit_runtime.session_state.pop(f"{key_prefix}_suggest_err", None)
    if err:
        st.warning(str(err))
    msg = streamlit_runtime.session_state.pop(f"{key_prefix}_suggest_msg", None)
    if msg:
        st.success(str(msg))

    idx_p = opts.index(dd_p) if dd_p in opts else 0
    idx_s = opts.index(dd_s) if dd_s in opts else 0
    primary_col, primary_manual_col = st.columns(2)
    with primary_col:
        sel_p = st.selectbox(
            f"Primary tag — {primary_hint}",
            options=opts,
            index=idx_p,
            key=f"{key_prefix}_tag_primary",
            help=help_primary,
        )
    with primary_manual_col:
        man_p = st.text_input(
            "Custom primary (optional)",
            value=man_p0,
            key=f"{key_prefix}_manual_primary",
            help="Kebab-case slug; when non-empty, overrides the primary dropdown.",
        )
    secondary_col, secondary_manual_col = st.columns(2)
    with secondary_col:
        sel_s = st.selectbox(
            f"Secondary tag — {secondary_hint}",
            options=opts,
            index=idx_s,
            key=f"{key_prefix}_tag_secondary",
            help=help_secondary,
        )
    with secondary_manual_col:
        man_s = st.text_input(
            "Custom secondary (optional)",
            value=man_s0,
            key=f"{key_prefix}_manual_secondary",
            help="Kebab-case slug; when non-empty, overrides the secondary dropdown.",
        )

    custom_reg = st.checkbox(
        "Register custom off-list slug(s) in YAML export (sets suggested_new_tag to the first "
        "custom primary/secondary)",
        key=f"{key_prefix}_approve_registry_export",
        help="When checked and you typed a custom slug not on the allowlist, Save will store it "
        "as suggested_new_tag for append-to-YAML on finish.",
    )

    llm_sug = normalize_tag(str(llm_item.get("suggested_new_tag") or ""))
    if llm_sug:
        render_similar_tags_warning(st, llm_sug, allowlist, key_prefix=key_prefix)
        st.caption(f"Registry suggestion on artifact: `{llm_sug}`")
    llm_suggested_approve = st.checkbox(
        "Include LLM- or prior suggested_new_tag in YAML export",
        value=bool(tag_node.get("new_tag_approved")),
        key=f"{key_prefix}_tag_suggested_approve",
        help="Approves the current suggested_new_tag field for append when you finish review.",
    )
    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    st.button(
        "Suggest new registry tag (LLM)",
        key=f"{key_prefix}_suggest_tag",
        help="Proposes one kebab-case tag not in the allowlist; saves to suggested_new_tag.",
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
        "sel_p": sel_p,
        "man_p": man_p,
        "sel_s": sel_s,
        "man_s": man_s,
        "custom_reg": custom_reg,
        "llm_suggested_approve": llm_suggested_approve,
    }
