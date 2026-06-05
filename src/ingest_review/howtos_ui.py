"""Streamlit rendering for how-to proposals (two-column read/edit + domain tags)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import format_proposal_meta_subtitle
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_tag_ui_to_node,
    effective_readonly_domain_tags,
    render_domain_tag_section,
)
from src.ingest_review.fast_review_ui import (
    CollapsedFieldSpec,
    read_fast_card_field_values,
    register_card_autosave,
    render_collapsed_fields,
    render_context_expander,
    render_fast_card_header,
    render_fast_card_reclassify,
    render_fast_card_save_row,
    render_inline_regenerate_title_controls,
    render_readonly_context_hint,
    render_source_evidence_expander,
)
from src.ingest_review.proposal_columns_ui import (
    build_proposal_expander_label,
    render_two_column_proposal_review,
)
from src.ingest_review.proposal_decision_ui import set_proposal_save_message
from src.ingest_review.proposal_regen_ui import (
    pop_proposal_regen_msg,
    proposal_edit_key_prefix,
    regen_count_from_node,
    render_proposal_regen_meta_caption,
)
from src.ingest_review.schema import HOWTO_REVIEWABLE_LIST_KEYS, HOWTO_REVIEWABLE_SCALAR_KEYS
from src.ingest_review.tags import normalize_tag

VALUE_LEVEL_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}

VALUE_LEVEL_BADGES: dict[str, str] = {
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

VALUE_LEVEL_TIER_HEADERS: dict[str, str] = {
    "high": "### High value",
    "medium": "### Medium value",
    "low": "### Low value",
}

HOWTO_FIELD_LABELS: dict[str, str] = {
    "question_title": "Page title",
    "what_and_problem": "What is it and what problem does it solve?",
    "answer_summary": "Answer summary",
    "caveats": "Caveats",
    "implementation_steps": "Implementation steps",
    "prerequisites": "Prerequisites",
}

HOWTO_SCALAR_BEFORE_TAGS: tuple[str, ...] = (
    "question_title",
    "what_and_problem",
    "answer_summary",
)
HOWTO_SCALAR_AFTER_TAGS: tuple[str, ...] = ("caveats",)

HOWTO_MORE_FIELD_SPECS: tuple[CollapsedFieldSpec, ...] = (
    CollapsedFieldSpec("caveats", "Caveats"),
    CollapsedFieldSpec(
        "implementation_steps",
        "Implementation steps",
        is_list=True,
        help_text="One bullet per line.",
    ),
    CollapsedFieldSpec(
        "prerequisites",
        "Prerequisites",
        is_list=True,
        help_text="One bullet per line.",
    ),
)
HOWTO_TALL_SCALAR_KEYS: frozenset[str] = frozenset({"what_and_problem", "answer_summary"})


def _sort_key(node: dict[str, Any]) -> tuple[int, float]:
    llm = node.get("llm_item") or {}
    level = str(llm.get("value_level") or "medium")
    conf = float(llm.get("confidence") or 0)
    return (VALUE_LEVEL_ORDER.get(level, 1), -conf)


def _value_level(node: dict[str, Any]) -> str:
    return str((node.get("llm_item") or {}).get("value_level") or "medium")


def _section_node(sections: dict[str, Any], section_key: str) -> dict[str, Any]:
    node = sections.get(section_key)
    return node if isinstance(node, dict) else {}


def effective_howto_scalar(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Return reviewer-final scalar text, else the LLM draft."""
    node = _section_node(sections, section_key)
    final = node.get("final_text")
    if isinstance(final, str) and final.strip():
        return final.strip()
    return str(llm_item.get(section_key) or "").strip()


def effective_howto_list(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> list[str]:
    """Return reviewer-final list or LLM list."""
    sec = _section_node(sections, list_key)
    if str(sec.get("status") or "pending") == "modified" and sec.get("final_list") is not None:
        fl = sec.get("final_list")
        if isinstance(fl, list):
            return [str(x) for x in fl]
    raw = llm_item.get(list_key) or []
    if not isinstance(raw, list):
        return []
    return [str(x) for x in raw]


def apply_howto_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one how-to field edit; infer section status from LLM draft."""
    text = raw_text.strip()
    llm_text = str(llm_item.get(section_key) or "").strip()
    node = sections.setdefault(
        section_key,
        {"status": "pending", "final_text": None, "notes": None},
    )
    if text == llm_text:
        node["status"] = "approved"
        node["final_text"] = None
    else:
        node["status"] = "modified"
        node["final_text"] = text


def apply_howto_list_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    list_key: str,
    raw_text: str,
) -> None:
    """Persist list field (one item per line); infer section status from LLM list."""
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    llm_list = llm_item.get(list_key) or []
    if not isinstance(llm_list, list):
        llm_list = []
    llm_norm = [str(x) for x in llm_list]
    node = sections.setdefault(
        list_key,
        {"status": "pending", "final_list": None, "notes": None, "llm_list": list(llm_norm)},
    )
    if not node.get("llm_list"):
        node["llm_list"] = list(llm_norm)
    if lines == llm_norm:
        node["status"] = "approved"
        node["final_list"] = None
    else:
        node["status"] = "modified"
        node["final_list"] = lines


def apply_howto_proposal_edits(
    node: dict[str, Any],
    field_values: dict[str, str],
) -> None:
    """Apply all editable scalar and list fields for one how-to proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in HOWTO_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_howto_scalar_edit(sections, llm_item, sk, field_values[sk])
    for lk in HOWTO_REVIEWABLE_LIST_KEYS:
        if lk in field_values:
            apply_howto_list_edit(sections, llm_item, lk, field_values[lk])


def howto_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one how-to scalar field."""
    return effective_howto_scalar(llm_item, sections, section_key)


def howto_list_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Default textarea value for list fields (one bullet per line)."""
    return "\n".join(effective_howto_list(llm_item, sections, list_key))


def format_howto_proposal_readonly_markdown(
    node: dict[str, Any],
    howto_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Single how-to card for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = effective_howto_scalar(llm_item, sections, "question_title") or "Untitled how-to"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}
    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, howto_tags)

    lines = [
        f"## {title}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    what = effective_howto_scalar(llm_item, sections, "what_and_problem")
    if what:
        lines.extend(
            [
                "**What is it and what problem does it solve?**",
                "",
                what,
                "",
            ]
        )
    summary = effective_howto_scalar(llm_item, sections, "answer_summary")
    if summary:
        lines.extend(["**Answer summary**", "", summary, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    caveats = effective_howto_scalar(llm_item, sections, "caveats")
    if caveats:
        lines.extend(["**Caveats**", "", caveats, ""])
    for lk in HOWTO_REVIEWABLE_LIST_KEYS:
        items = effective_howto_list(llm_item, sections, lk)
        if items:
            label = HOWTO_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            lines.extend([f"**{label}**", ""] + [f"- {p}" for p in items] + [""])
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    related = llm_item.get("related_howtos") or []
    if isinstance(related, list) and related:
        lines.extend([f"*Related how-tos: {', '.join(str(r) for r in related)}*", ""])
    return "\n".join(lines).rstrip()


def build_readonly_howtos_markdown(
    sorted_nodes: list[dict[str, Any]],
    howto_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
) -> str:
    """Build full read-only column markdown for all how-to proposals."""
    if not sorted_nodes:
        return "*(No how-to proposals.)*"
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        parts.append(format_howto_proposal_readonly_markdown(node, howto_tags, artifact=artifact))
    return "\n\n---\n\n".join(parts)


def _howto_expander_label(node: dict[str, Any], index: int) -> str:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = effective_howto_scalar(llm_item, sections, "question_title") or f"How-to {index + 1}"
    badge = VALUE_LEVEL_BADGES.get(_value_level(node), "Medium")
    return build_proposal_expander_label(node, title, badge=badge)


def _prepare_howto_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    howto_nodes = review.setdefault("how_to", [])
    llm_items = artifact.get("llm_output", {}).get("how_to") or []
    for i, node in enumerate(howto_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(howto_nodes, key=_sort_key)


def _persist_howto_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    tag_ui: dict[str, Any],
    allow: set[str],
    *,
    key_prefix: str,
) -> None:
    """Apply textarea + tag edits from this run and write the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    merged = read_fast_card_field_values(
        key_prefix,
        title_keys=("question_title",),
        context_keys=("answer_summary",),
        context_companion_fields=(("what_and_problem", "answer_summary"),),
        more_scalar_keys=tuple(s.key for s in HOWTO_MORE_FIELD_SPECS if not s.is_list),
        more_list_keys=HOWTO_REVIEWABLE_LIST_KEYS,
        field_values=field_values,
    )
    apply_howto_proposal_edits(node, merged)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow, key_prefix=key_prefix)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    title = merged.get("question_title") or llm_item.get("question_title") or "how-to"
    set_proposal_save_message(key_prefix, f"Saved **{title}**.")


def _render_howto_edit_box(
    st: Any,
    node: dict[str, Any],
    howto_tags: list[str],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
    autosave_registry_key: str,
) -> None:
    """Fast-review card for one how-to proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    title = effective_howto_scalar(llm_item, sections, "question_title") or "Untitled"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    proposal_id = str(node.get("proposal_id") or "")

    with st.container(border=True):
        render_fast_card_header(
            st,
            node,
            badge=badge,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="how_to",
        )
        render_proposal_regen_meta_caption(st, node, "How-to")

        field_values: dict[str, str] = {}
        field_values["question_title"] = st.text_area(
            "Question title",
            value=howto_field_edit_value(llm_item, sections, "question_title"),
            height=72,
            key=f"{key_prefix}_edit_question_title",
        )
        render_readonly_context_hint(
            st,
            label="Answer summary",
            value=howto_field_edit_value(llm_item, sections, "answer_summary"),
        )

        render_inline_regenerate_title_controls(
            st,
            entity_key="how_to",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
            title_label="New how-to title",
        )

        tag_ui = render_domain_tag_section(
            st,
            node,
            howto_tags,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="how_to",
            label_widget_key=f"{key_prefix}_edit_question_title",
            summary_widget_key=f"{key_prefix}_edit_answer_summary",
            llm_fallback_label_key="question_title",
            llm_fallback_summary_key="answer_summary",
        )

        def _save() -> None:
            _persist_howto_proposal_from_widgets(
                node,
                artifact_path,
                field_values,
                tag_ui,
                tag_allow,
                key_prefix=key_prefix,
            )

        render_fast_card_save_row(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="how_to",
            on_save_callback=_save,
        )

        render_context_expander(
            st,
            label="Answer / context",
            field_key="answer_summary",
            field_label="Answer summary",
            value=howto_field_edit_value(llm_item, sections, "answer_summary"),
            widget_key=f"{key_prefix}_ctx_answer_summary",
            field_values=field_values,
            extra_fields=[
                (
                    "what_and_problem",
                    "What and problem",
                    howto_field_edit_value(llm_item, sections, "what_and_problem"),
                    True,
                ),
            ],
        )

        def _related_caption() -> None:
            related = llm_item.get("related_howtos") or []
            if related:
                st.caption(f"Related how-tos (LLM): {', '.join(str(r) for r in related)}")

        render_collapsed_fields(
            st,
            specs=list(HOWTO_MORE_FIELD_SPECS),
            get_value=lambda li, sec, k: (
                howto_list_edit_value(li, sec, k)
                if k in HOWTO_REVIEWABLE_LIST_KEYS
                else howto_field_edit_value(li, sec, k)
            ),
            llm_item=llm_item,
            sections=sections,
            key_prefix=key_prefix,
            field_values=field_values,
            extra_content=_related_caption,
        )
        render_source_evidence_expander(st, llm_item)
        render_fast_card_reclassify(
            st,
            node,
            reclassify_entity_key="how_to",
            source_id=source_id,
            current_title=title,
            key_prefix=key_prefix,
        )
        register_card_autosave(autosave_registry_key, node, _save)


def render_howto_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str = "",
    artifact_path: Path,
    howto_tags: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
) -> None:
    """Two-column how-to review: read-only catalog left, edit panel right."""
    tags_list = list(howto_tags or [])
    tag_allow = {normalize_tag(str(t)) for t in tags_list if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = tags_list

    st.subheader("How-tos")
    sorted_nodes = _prepare_howto_nodes(artifact)
    llm_howtos = artifact.get("llm_output", {}).get("how_to") or []

    if not sorted_nodes and not llm_howtos:
        st.caption("No how-to proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected")

    regen_msg = pop_proposal_regen_msg("how_to")
    if regen_msg:
        st.success(regen_msg)

    def _readonly_md(node: dict[str, Any]) -> str:
        if len(sorted_nodes) == 1:
            return build_readonly_howtos_markdown([node], tags_list, artifact=artifact)
        return format_howto_proposal_readonly_markdown(node, tags_list, artifact=artifact)

    def _render_edit(node: dict[str, Any], index: int) -> None:
        pid = str(node.get("proposal_id") or f"idx{index}")
        pfx = proposal_edit_key_prefix(
            key_prefix, pid, "h", regen_count=regen_count_from_node(node)
        )
        _render_howto_edit_box(
            st,
            node,
            tags_list,
            key_prefix=pfx,
            source_id=source_id,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            tag_allow=tag_allow,
            autosave_registry_key=key_prefix,
        )

    render_two_column_proposal_review(
        st,
        sorted_nodes,
        key_prefix=key_prefix,
        empty_readonly_text="*(No how-to proposals.)*",
        label_for_node=_howto_expander_label,
        readonly_markdown_for_node=_readonly_md,
        render_edit_for_node=_render_edit,
    )


def collect_howto_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across how-to proposals."""
    from src.ingest_review.domain_tag_ui import collect_approved_new_tags_from_review

    return collect_approved_new_tags_from_review(artifact, "how_to")


collect_howto_approved_new_tags = collect_howto_new_tags
