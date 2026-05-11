"""Streamlit-oriented review widgets (pass ``st`` for testability)."""

from __future__ import annotations

import json
from typing import Any

STATUS_OPTIONS = ("pending", "approved", "rejected", "modified")

SUMMARY_TEXT_KEYS = (
    "why_it_matters",
    "key_insights",
    "implications_automation",
    "context_limitations",
    "contradictions",
)


def _status_index(current: str) -> int:
    """Return index of ``current`` in STATUS_OPTIONS."""
    if current in STATUS_OPTIONS:
        return STATUS_OPTIONS.index(current)
    return 0


def render_source_summary_review(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
) -> None:
    """Render review controls for ``source_summary`` text fields."""
    llm = artifact.get("llm_output", {}).get("source_summary") or {}
    rev = artifact.setdefault("review", {}).setdefault("source_summary", {})
    st.subheader("Source summary")
    for key in SUMMARY_TEXT_KEYS:
        label = key.replace("_", " ").title()
        node = rev.setdefault(
            key,
            {"status": "pending", "final_text": None, "notes": None},
        )
        llm_text = str(llm.get(key) or "")
        st.markdown(f"**{label}** (LLM)")
        st.text(llm_text[:4000] + ("…" if len(llm_text) > 4000 else ""))
        node["status"] = st.selectbox(
            f"{label} — status",
            STATUS_OPTIONS,
            index=_status_index(str(node.get("status") or "pending")),
            key=f"{key_prefix}_sum_{key}_st",
        )
        if node["status"] in ("modified", "pending"):
            default = node.get("final_text") if node.get("final_text") else llm_text
            node["final_text"] = st.text_area(
                f"{label} — final text",
                value=default,
                height=120,
                key=f"{key_prefix}_sum_{key}_txt",
            )
        elif node["status"] == "approved":
            node["final_text"] = None
        else:
            node["final_text"] = None
        node["notes"] = st.text_input(
            f"{label} — notes",
            value=str(node.get("notes") or ""),
            key=f"{key_prefix}_sum_{key}_notes",
        )

    src_node = rev.setdefault(
        "sources",
        {"status": "pending", "final_list": None, "notes": None, "llm_list": []},
    )
    llm_sources = llm.get("sources") or []
    if not src_node.get("llm_list"):
        src_node["llm_list"] = list(llm_sources)
    st.markdown("**Sources (list)**")
    st.json(src_node["llm_list"])
    src_node["status"] = st.selectbox(
        "Sources — status",
        STATUS_OPTIONS,
        index=_status_index(str(src_node.get("status") or "pending")),
        key=f"{key_prefix}_sum_sources_st",
    )
    raw_list = st.text_area(
        "Sources — final list (one URL per line)",
        value="\n".join(src_node.get("final_list") or src_node["llm_list"] or []),
        height=80,
        key=f"{key_prefix}_sum_sources_txt",
    )
    lines = [ln.strip() for ln in raw_list.splitlines() if ln.strip()]
    if src_node["status"] == "modified":
        src_node["final_list"] = lines
    elif src_node["status"] == "approved":
        src_node["final_list"] = None
    else:
        src_node["final_list"] = None
    src_node["notes"] = st.text_input(
        "Sources — notes",
        value=str(src_node.get("notes") or ""),
        key=f"{key_prefix}_sum_sources_notes",
    )


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
        review_key="glossary",
        title="Glossary",
        key_prefix=key_prefix,
        tag_allowlist=None,
    )
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
        review_key="enterprise_studies",
        title="Enterprise implementation",
        key_prefix=key_prefix,
        tag_allowlist=None,
    )
    _render_proposal_list(
        st,
        artifact,
        review_key="industry_trends",
        title="Industry trends",
        key_prefix=key_prefix,
        tag_allowlist=None,
    )
