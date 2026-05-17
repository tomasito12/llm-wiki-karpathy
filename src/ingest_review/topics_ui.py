"""Streamlit rendering for topic proposals (two-column read/edit + domain tags)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import format_proposal_meta_subtitle, google_search_markdown
from src.ingest_review.domain_tag_ui import (
    DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY,
    apply_tag_ui_to_node,
    effective_readonly_domain_tags,
    render_domain_tag_section,
)
from src.ingest_review.proposal_decision_ui import (
    proposal_status_label,
    render_proposal_decision_bar,
)
from src.ingest_review.proposal_regen_ui import (
    pop_proposal_regen_msg,
    proposal_edit_key_prefix,
    regen_count_from_node,
    render_proposal_regen_meta_caption,
    render_reclassify_to_section_controls,
    render_regenerate_with_new_title_controls,
)
from src.ingest_review.schema import TOPIC_REVIEWABLE_LIST_KEYS, TOPIC_REVIEWABLE_SCALAR_KEYS
from src.ingest_review.tags import normalize_tag
from src.ingest_review.topic_related_topics_suggest import (
    RelatedTopicCandidate,
    build_topic_slug_catalog,
    catalog_by_slug,
    format_suggestion_line,
    suggest_related_topics,
)
from src.ingest_review.wiki_snapshot import WikiSnapshot, build_wiki_snapshot

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

TOPIC_FIELD_LABELS: dict[str, str] = {
    "topic_slug": "Topic slug",
    "topic_title": "Topic title",
    "knowledge_summary": "Knowledge summary",
    "examples": "Examples",
    "operational_insight": "Operational insight",
    "relevance_note": "Relevance note",
    "key_points": "Key points",
    "related_topics": "Related topics",
}

TOPIC_TEXTAREA_LIST_KEYS: tuple[str, ...] = tuple(
    lk for lk in TOPIC_REVIEWABLE_LIST_KEYS if lk != "related_topics"
)

TOPIC_SCALAR_BEFORE_TAGS: tuple[str, ...] = (
    "topic_slug",
    "topic_title",
    "knowledge_summary",
    "examples",
)
TOPIC_SCALAR_AFTER_TAGS: tuple[str, ...] = ("operational_insight", "relevance_note")

TOPIC_TALL_SCALAR_KEYS: frozenset[str] = frozenset({"knowledge_summary", "examples"})


def topic_edit_key_prefix(
    source_key_prefix: str,
    proposal_id: str,
    *,
    regen_count: int = 0,
) -> str:
    """Stable Streamlit widget prefix; *regen_count* bumps after LLM regen to reset inputs."""
    return proposal_edit_key_prefix(source_key_prefix, proposal_id, "t", regen_count=regen_count)


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


def effective_topic_scalar(
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


def effective_topic_list(
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


def apply_topic_scalar_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    section_key: str,
    raw_text: str,
) -> None:
    """Persist one topic field edit; infer section status from LLM draft."""
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


def apply_topic_list_edit(
    sections: dict[str, Any],
    llm_item: dict[str, Any],
    list_key: str,
    raw_text: str,
) -> None:
    """Persist key_points (one bullet per line); infer section status from LLM list."""
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


def apply_topic_proposal_edits(
    node: dict[str, Any],
    field_values: dict[str, str],
) -> None:
    """Apply all editable scalar and list fields for one topic proposal."""
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    for sk in TOPIC_REVIEWABLE_SCALAR_KEYS:
        if sk in field_values:
            apply_topic_scalar_edit(sections, llm_item, sk, field_values[sk])
    for lk in TOPIC_REVIEWABLE_LIST_KEYS:
        if lk in field_values:
            apply_topic_list_edit(sections, llm_item, lk, field_values[lk])


def topic_field_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    section_key: str,
) -> str:
    """Default textarea value for one topic scalar field."""
    return effective_topic_scalar(llm_item, sections, section_key)


def topic_list_edit_value(
    llm_item: dict[str, Any],
    sections: dict[str, Any],
    list_key: str,
) -> str:
    """Default textarea value for key_points (one bullet per line)."""
    return "\n".join(effective_topic_list(llm_item, sections, list_key))


def _topic_related_suggestions(
    node: dict[str, Any],
    *,
    wiki: WikiSnapshot,
    reviews_root: Path | None,
    artifact: dict[str, Any],
) -> list[RelatedTopicCandidate]:
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    slug = effective_topic_scalar(llm_item, sections, "topic_slug")
    title = effective_topic_scalar(llm_item, sections, "topic_title")
    summary = effective_topic_scalar(llm_item, sections, "knowledge_summary")
    catalog = build_topic_slug_catalog(wiki, reviews_root, artifact, exclude_slug=slug)
    return suggest_related_topics(slug, title, summary, catalog)


def _format_related_topic_multiselect_label(
    slug: str,
    by_slug: dict[str, RelatedTopicCandidate],
) -> str:
    cand = by_slug.get(slug)
    if cand is None:
        return slug
    source_label = {
        "wiki": "wiki",
        "review": "other review",
        "batch": "this review",
    }.get(cand.source, cand.source)
    if cand.title:
        return f"{cand.title} ({source_label})"
    return f"{slug} ({source_label})"


def format_topic_proposal_readonly_markdown(
    node: dict[str, Any],
    topic_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
    related_suggestions: list[RelatedTopicCandidate] | None = None,
) -> str:
    """Single topic card for the read-only column."""
    llm_item = node.get("llm_item") or {}
    sections = node.get("sections") or {}
    title = (
        effective_topic_scalar(llm_item, sections, "topic_title")
        or effective_topic_scalar(llm_item, sections, "topic_slug")
        or "Untitled topic"
    )
    slug = effective_topic_scalar(llm_item, sections, "topic_slug")
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    confidence = float(llm_item.get("confidence") or 0.0)
    art = artifact if isinstance(artifact, dict) else {}
    tag_node = node.get("tags") if isinstance(node.get("tags"), dict) else {}
    tag_slugs = effective_readonly_domain_tags(llm_item, tag_node, topic_tags)

    lines = [
        f"## {title}",
        "",
        format_proposal_meta_subtitle(art, node, llm_item, badge=badge, confidence=confidence),
        "",
    ]
    google = google_search_markdown(title)
    if google:
        lines.extend([google, ""])
    if slug:
        lines.extend(["**Slug**", "", slug, ""])
    ksum = effective_topic_scalar(llm_item, sections, "knowledge_summary")
    if ksum:
        lines.extend(["**Knowledge summary**", "", ksum, ""])
    ex = effective_topic_scalar(llm_item, sections, "examples")
    if ex:
        lines.extend(["**Examples**", "", ex, ""])
    if tag_slugs:
        lines.extend(["**Tags**", "", ", ".join(tag_slugs), ""])
    stored_related = effective_topic_list(llm_item, sections, "related_topics")
    sugg = related_suggestions or []
    if sugg or stored_related:
        lines.extend(["**Related topics**", ""])
        if sugg:
            lines.append("*Suggested:*")
            lines.extend([f"- {format_suggestion_line(c)}" for c in sugg])
        if stored_related:
            lines.append("*Stored:*")
            lines.extend([f"- `{s}`" for s in stored_related])
        lines.append("")
    op = effective_topic_scalar(llm_item, sections, "operational_insight")
    if op:
        lines.extend(["**Operational insight**", "", op, ""])
    rel = effective_topic_scalar(llm_item, sections, "relevance_note")
    if rel:
        lines.extend(["**Relevance**", "", rel, ""])
    kpts = effective_topic_list(llm_item, sections, "key_points")
    if kpts:
        lines.extend(["**Key points**", ""] + [f"- {p}" for p in kpts] + [""])
    snippet = str(llm_item.get("supporting_snippet") or "").strip()
    if snippet:
        excerpt = snippet[:2000] + ("…" if len(snippet) > 2000 else "")
        lines.extend(["> " + excerpt.replace("\n", "\n> "), ""])
    return "\n".join(lines).rstrip()


def build_readonly_topics_markdown(
    sorted_nodes: list[dict[str, Any]],
    topic_tags: list[str],
    *,
    artifact: dict[str, Any] | None = None,
    wiki: WikiSnapshot | None = None,
    reviews_root: Path | None = None,
) -> str:
    if not sorted_nodes:
        return "*(No topic proposals.)*"
    art = artifact if isinstance(artifact, dict) else {}
    parts: list[str] = []
    prev_tier: str | None = None
    for node in sorted_nodes:
        tier = _value_level(node)
        if tier != prev_tier:
            header = VALUE_LEVEL_TIER_HEADERS.get(tier)
            if header:
                parts.append(header)
            prev_tier = tier
        sugg: list[RelatedTopicCandidate] | None = None
        if wiki is not None:
            sugg = _topic_related_suggestions(
                node,
                wiki=wiki,
                reviews_root=reviews_root,
                artifact=art,
            )
        parts.append(
            format_topic_proposal_readonly_markdown(
                node,
                topic_tags,
                artifact=artifact,
                related_suggestions=sugg,
            )
        )
    return "\n\n---\n\n".join(parts)


def _prepare_topic_nodes(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    review = artifact.setdefault("review", {})
    topic_nodes = review.setdefault("topics", [])
    llm_items = artifact.get("llm_output", {}).get("topics") or []
    for i, node in enumerate(topic_nodes):
        if "llm_item" not in node and i < len(llm_items):
            node["llm_item"] = llm_items[i]
        if not node.get("proposal_id"):
            node["proposal_id"] = uuid.uuid4().hex
    return sorted(topic_nodes, key=_sort_key)


def _persist_topic_proposal_from_widgets(
    node: dict[str, Any],
    artifact_path: Path,
    field_values: dict[str, str],
    tag_ui: dict[str, Any],
    allow: set[str],
) -> None:
    """Apply textarea + tag edits from this run and write the artifact."""
    from src.ingest_review.artifact import save_artifact, touch_review_session

    artifact = streamlit_runtime.session_state.get("artifact")
    if not isinstance(artifact, dict):
        return
    apply_topic_proposal_edits(node, field_values)
    llm_item = node.setdefault("llm_item", {})
    apply_tag_ui_to_node(node, llm_item, tag_ui, allow)
    touch_review_session(artifact)
    save_artifact(artifact_path, artifact)
    title = field_values.get("topic_title") or llm_item.get("topic_slug") or "topic"
    streamlit_runtime.session_state["_topic_save_msg"] = f"Saved **{title}**."


def _render_topic_edit_box(
    st: Any,
    node: dict[str, Any],
    topic_tags: list[str],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    model: str,
    prompt_version: str,
    tag_allow: set[str],
    artifact: dict[str, Any],
    wiki: WikiSnapshot,
    reviews_root: Path | None,
) -> None:
    llm_item = node.get("llm_item") or {}
    sections = node.setdefault("sections", {})
    title = effective_topic_scalar(llm_item, sections, "topic_title") or "Untitled"
    tier = _value_level(node)
    badge = VALUE_LEVEL_BADGES.get(tier, "Medium")
    proposal_status = proposal_status_label(node)

    with st.container(border=True):
        st.markdown(f"**{title}** · {badge} · **{proposal_status}**")
        render_proposal_regen_meta_caption(st, node, "Topic")

        field_values: dict[str, str] = {}
        for sk in TOPIC_SCALAR_BEFORE_TAGS:
            label = TOPIC_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=topic_field_edit_value(llm_item, sections, sk),
                height=120 if sk in TOPIC_TALL_SCALAR_KEYS else 72,
                key=f"{key_prefix}_edit_{sk}",
            )

        tag_ui = render_domain_tag_section(
            st,
            node,
            topic_tags,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            model=model,
            prompt_version=prompt_version,
            review_list_key="topics",
            label_widget_key=f"{key_prefix}_edit_topic_title",
            summary_widget_key=f"{key_prefix}_edit_knowledge_summary",
            llm_fallback_label_key="topic_title",
            llm_fallback_summary_key="knowledge_summary",
        )

        for sk in TOPIC_SCALAR_AFTER_TAGS:
            label = TOPIC_FIELD_LABELS.get(sk, sk.replace("_", " ").title())
            field_values[sk] = st.text_area(
                label,
                value=topic_field_edit_value(llm_item, sections, sk),
                height=72,
                key=f"{key_prefix}_edit_{sk}",
            )

        for lk in TOPIC_TEXTAREA_LIST_KEYS:
            label = TOPIC_FIELD_LABELS.get(lk, lk.replace("_", " ").title())
            field_values[lk] = st.text_area(
                label,
                value=topic_list_edit_value(llm_item, sections, lk),
                height=100,
                key=f"{key_prefix}_edit_{lk}",
                help="One bullet per line.",
            )

        suggestions = _topic_related_suggestions(
            node,
            wiki=wiki,
            reviews_root=reviews_root,
            artifact=artifact,
        )
        by_slug = catalog_by_slug(suggestions)
        current_related = [
            normalize_tag(s)
            for s in effective_topic_list(llm_item, sections, "related_topics")
            if normalize_tag(s)
        ]
        option_slugs = list(dict.fromkeys([c.slug for c in suggestions] + current_related))
        if option_slugs:
            selected = st.multiselect(
                TOPIC_FIELD_LABELS["related_topics"],
                options=option_slugs,
                default=[s for s in current_related if s in option_slugs],
                max_selections=3,
                format_func=lambda s, m=by_slug: _format_related_topic_multiselect_label(s, m),
                key=f"{key_prefix}_edit_related_topics",
                help="Up to 3 cross-links to other topic pages (kebab-case slugs).",
            )
            field_values["related_topics"] = "\n".join(selected)
        elif current_related:
            field_values["related_topics"] = "\n".join(current_related)

        snippet = str(llm_item.get("supporting_snippet") or "").strip()
        if snippet:
            with st.expander("Source evidence (read-only)", expanded=False):
                st.text(snippet[:4000] + ("…" if len(snippet) > 4000 else ""))

        proposal_id = str(node.get("proposal_id") or "")
        render_regenerate_with_new_title_controls(
            st,
            entity_key="topic",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
            title_label="New topic title",
        )
        render_reclassify_to_section_controls(
            st,
            source_entity_key="topic",
            source_id=source_id,
            proposal_id=proposal_id,
            widget_prefix=key_prefix,
            current_title=title,
        )

        def _save() -> None:
            _persist_topic_proposal_from_widgets(
                node,
                artifact_path,
                field_values,
                tag_ui,
                tag_allow,
            )

        render_proposal_decision_bar(
            st,
            node,
            key_prefix=key_prefix,
            artifact_path=artifact_path,
            review_list_key="topics",
            on_save_callback=_save,
        )


def render_topic_proposals(
    st: Any,
    artifact: dict[str, Any],
    *,
    key_prefix: str,
    source_id: str,
    artifact_path: Path,
    topic_tags: list[str] | None = None,
    model: str = "",
    prompt_version: str = "",
    wiki_root: Path | None = None,
    reviews_root: Path | None = None,
) -> None:
    """Two-column topics review: read-only catalog left, edit panel right."""
    tags_list = list(topic_tags or [])
    tag_allow = {normalize_tag(str(t)) for t in tags_list if str(t).strip()}
    streamlit_runtime.session_state[DOMAIN_TAG_SUGGEST_ALLOWLIST_KEY] = tags_list

    st.subheader("Topics")
    sorted_nodes = _prepare_topic_nodes(artifact)
    llm_topics = artifact.get("llm_output", {}).get("topics") or []

    if not sorted_nodes and not llm_topics:
        st.caption("No topic proposals.")
        return

    rejected = sum(1 for n in sorted_nodes if str(n.get("proposal_status") or "") == "rejected")
    low_ct = sum(1 for n in sorted_nodes if (n.get("llm_item") or {}).get("value_level") == "low")
    st.caption(f"{len(sorted_nodes)} proposal(s) · {rejected} rejected · {low_ct} low value")

    save_msg = streamlit_runtime.session_state.pop("_topic_save_msg", None)
    if save_msg:
        st.success(str(save_msg))
    regen_msg = pop_proposal_regen_msg("topic")
    if regen_msg:
        st.success(regen_msg)

    wiki: WikiSnapshot | None = None
    if wiki_root is not None:
        wiki = build_wiki_snapshot(wiki_root)

    read_col, edit_col = st.columns(2)
    with read_col:
        st.markdown(
            build_readonly_topics_markdown(
                sorted_nodes,
                tags_list,
                artifact=artifact,
                wiki=wiki,
                reviews_root=reviews_root,
            )
        )
    with edit_col:
        edit_nodes = sorted_nodes
        if len(sorted_nodes) > 6:
            labels = [
                effective_topic_scalar(
                    n.get("llm_item") or {},
                    n.get("sections") or {},
                    "topic_title",
                )
                or effective_topic_scalar(
                    n.get("llm_item") or {},
                    n.get("sections") or {},
                    "topic_slug",
                )
                or f"Topic {i + 1}"
                for i, n in enumerate(sorted_nodes)
            ]
            pick = st.selectbox(
                "Edit topic",
                options=labels,
                key=f"{key_prefix}_topic_jump",
            )
            idx = labels.index(pick) if pick in labels else 0
            edit_nodes = [sorted_nodes[idx]]
            st.caption("Showing one edit panel — use the selector to switch topics.")

        for i, node in enumerate(edit_nodes):
            pid = str(node.get("proposal_id") or f"idx{i}")
            pfx = topic_edit_key_prefix(key_prefix, pid, regen_count=regen_count_from_node(node))
            if wiki is None:
                st.warning("Wiki root required to edit related topics.")
                continue
            _render_topic_edit_box(
                st,
                node,
                tags_list,
                key_prefix=pfx,
                source_id=source_id,
                artifact_path=artifact_path,
                model=model,
                prompt_version=prompt_version,
                tag_allow=tag_allow,
                artifact=artifact,
                wiki=wiki,
                reviews_root=reviews_root,
            )


def collect_topic_new_tags(artifact: dict[str, Any]) -> list[str]:
    """Return approved new tags across topic proposals."""
    from src.ingest_review.domain_tag_ui import collect_approved_new_tags_from_review

    return collect_approved_new_tags_from_review(artifact, "topics")


collect_topic_approved_new_tags = collect_topic_new_tags
render_topic_contributions = render_topic_proposals
