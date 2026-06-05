"""Streamlit dashboard: ingest review (classification + human approval)."""

from __future__ import annotations

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import os
import random
import traceback
from datetime import UTC, datetime
from typing import Any

import streamlit as st

from src.ingest_queue.queue import list_ingest_items
from src.ingest_review.analyze import (
    run_classification,
    run_entity_extraction_for_artifact,
    run_source_summary_refresh,
)
from src.ingest_review.artifact import (
    aggregate_review_status,
    apply_regenerated_source_section,
    attach_error,
    backup_artifact,
    ensure_review_started,
    load_artifact,
    review_artifact_path,
    save_artifact,
    touch_review_session,
)
from src.ingest_review.dashboard_ui import (
    ENTITY_TABS_WITH_PROPOSAL_AUTOSAVE,
    build_review_entity_tab_options,
    normalize_review_entity_tab,
    render_compact_review_stats,
    render_skip_extraction_screen,
    render_source_evidence_profile,
    render_source_summary_review,
    render_source_type_detection,
    render_source_type_override_panel,
)
from src.ingest_review.evidence import (
    effective_proposal_evidence_type,
    source_primary_evidence_type,
)
from src.ingest_review.extract import (
    list_readwise_html_sources,
    load_readwise_pair,
    readwise_source_status,
)
from src.ingest_review.fast_review_ui import run_proposal_autosave
from src.ingest_review.feedback_store import (
    default_feedback_db_path,
    record_events_from_artifact,
    record_review_session,
)
from src.ingest_review.force_extract_ui import render_force_extract_panel, source_summary_is_empty
from src.ingest_review.glossary_ui import (
    collect_glossary_new_tags,
    render_glossary_proposals,
)
from src.ingest_review.howtos_ui import (
    collect_howto_new_tags,
    render_howto_proposals,
)
from src.ingest_review.impl_study_ui import (
    collect_impl_study_new_tags,
    render_implementation_studies,
)
from src.ingest_review.insights_ui import (
    collect_insight_new_tags,
    render_interview_insights,
)
from src.ingest_review.layout_ui import reading_width_column
from src.ingest_review.models_ui import (
    collect_model_new_tags,
    collect_model_new_types,
    render_model_proposals,
)
from src.ingest_review.paths import load_repo_dotenv
from src.ingest_review.proposal_force_extract_handler import process_pending_forced_extract
from src.ingest_review.proposal_regen_handler import process_pending_proposal_regen
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.review_queue_status import (
    DEFAULT_SOURCE_REVIEW_FILTER,
    SOURCE_REVIEW_FILTER_OPTIONS,
    artifact_title_for_source,
    build_source_status_map,
    count_by_status,
    filter_source_ids,
    filter_statuses_for_label,
    status_label,
    unfinished_source_ids,
)
from src.ingest_review.schema import PROMPT_VERSION
from src.ingest_review.signals_ui import (
    collect_signal_new_tags,
    render_roundup_signals,
)
from src.ingest_review.skipped_sources import (
    is_source_skipped,
    skip_entry_for_source,
    skip_source_for_extraction,
    unskip_source,
)
from src.ingest_review.tags import (
    append_tags_to_yaml,
    default_glossary_tags_path,
    default_howto_tags_path,
    default_impl_study_tags_path,
    default_model_tags_path,
    default_model_types_path,
    default_tool_tags_path,
    default_tool_types_path,
    default_topic_tags_path,
    default_trend_tags_path,
    load_extraction_budgets,
    load_glossary_tags,
    load_howto_tags,
    load_impl_study_tags,
    load_model_tags,
    load_model_types,
    load_tool_tags,
    load_tool_types,
    load_topic_tags,
    load_trend_tags,
)
from src.ingest_review.tools_ui import (
    collect_tool_new_tags,
    collect_tool_new_types,
    render_tool_proposals,
)
from src.ingest_review.topics_ui import (
    collect_topic_new_tags,
    render_topic_proposals,
)
from src.ingest_review.trends_ui import (
    collect_trend_new_tags,
    render_trend_proposals,
)
from src.ingest_review.wiki_snapshot import parse_glossary_terms

REVIEW_ENTITY_TABS: tuple[str, ...] = (
    "Source chapters",
    "Glossary",
    "Topics",
    "How-tos",
    "Trends",
    "Tools",
    "Models",
    "Impl studies",
    "Signals",
    "Insights",
    "Source type",
    "Debug",
)


def _finalize_review_analytics(artifact: dict) -> None:
    """Record review duration on save."""
    analytics = artifact.setdefault("review_analytics", {})
    started = analytics.get("review_started_at")
    if started:
        try:
            start_dt = datetime.fromisoformat(started)
            now = datetime.now(tz=UTC)
            analytics["review_duration_seconds"] = round((now - start_dt).total_seconds(), 1)
            analytics["review_finished_at"] = now.isoformat()
        except (ValueError, TypeError):
            pass
    review = artifact.get("review") or {}
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
    total = approved = rejected = deferred = modified = 0
    evidence_counts: dict[str, int] = {}
    for key in entity_keys:
        nodes = review.get(key) or []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            total += 1
            ps = node.get("proposal_status", "pending")
            if ps == "approved":
                approved += 1
            elif ps == "rejected":
                rejected += 1
            elif ps == "deferred":
                deferred += 1
            if node.get("final_item") is not None:
                modified += 1
            lit = node.get("llm_item")
            if isinstance(lit, dict):
                primary = source_primary_evidence_type(artifact)
                et = effective_proposal_evidence_type(primary, lit)
                evidence_counts[et] = evidence_counts.get(et, 0) + 1
    analytics["proposals_total"] = total
    analytics["proposals_approved"] = approved
    analytics["proposals_rejected"] = rejected
    analytics["proposals_deferred"] = deferred
    analytics["proposals_modified"] = modified
    analytics["evidence_type_counts"] = evidence_counts


def _collect_and_persist_tags(st_ref: Any, artifact: dict, root: Path) -> None:
    """Collect all approved new tags and persist to allowlist YAML files."""
    tag_actions = [
        (collect_impl_study_new_tags, default_impl_study_tags_path, "impl-study"),
        (collect_glossary_new_tags, default_glossary_tags_path, "glossary"),
        (collect_topic_new_tags, default_topic_tags_path, "topic"),
        (collect_howto_new_tags, default_howto_tags_path, "how-to"),
        (collect_trend_new_tags, default_trend_tags_path, "trend"),
        (collect_signal_new_tags, default_trend_tags_path, "signal"),
        (collect_insight_new_tags, default_topic_tags_path, "insight"),
    ]
    for collector, path_fn, label in tag_actions:
        new_tags = collector(artifact)
        if new_tags:
            try:
                append_tags_to_yaml(path_fn(root), new_tags)
                st_ref.caption(f"Appended {len(new_tags)} {label} tag(s) to allowlist.")  # type: ignore[union-attr]
            except OSError as exc:
                st_ref.warning(f"{label.title()} tag allowlist update skipped: {exc}")  # type: ignore[union-attr]

    retrieval_tag_actions = [
        (collect_tool_new_tags, default_tool_tags_path, "tool retrieval tag"),
        (collect_model_new_tags, default_model_tags_path, "model retrieval tag"),
    ]
    for collector, path_fn, label in retrieval_tag_actions:
        new_tags = collector(artifact)
        if new_tags:
            try:
                append_tags_to_yaml(path_fn(root), new_tags)
                st_ref.caption(f"Appended {len(new_tags)} {label}(s) to allowlist.")  # type: ignore[union-attr]
            except OSError as exc:
                st_ref.warning(f"{label.title()} allowlist update skipped: {exc}")  # type: ignore[union-attr]

    type_actions = [
        (collect_tool_new_types, default_tool_types_path, "tool type"),
        (collect_model_new_types, default_model_types_path, "model type"),
    ]
    for collector, path_fn, label in type_actions:
        new_types = collector(artifact)
        if new_types:
            try:
                append_tags_to_yaml(path_fn(root), new_types)
                st_ref.caption(f"Appended {len(new_types)} {label}(s) to registry.")  # type: ignore[union-attr]
            except OSError as exc:
                st_ref.warning(f"{label.title()} registry update skipped: {exc}")  # type: ignore[union-attr]


def finish_review_session(
    st_ref: Any,
    artifact: dict[str, Any],
    artifact_path: Path,
    root: Path,
) -> str:
    """Finalize review: analytics, artifact save, feedback DB, tag/type YAML updates."""
    ensure_review_started(artifact)
    touch_review_session(artifact)
    _finalize_review_analytics(artifact)
    save_artifact(artifact_path, artifact)
    fb_path = default_feedback_db_path(root)
    try:
        record_events_from_artifact(fb_path, artifact)
        record_review_session(fb_path, artifact)
    except OSError as exc:
        st_ref.warning(f"Feedback DB write skipped: {exc}")
    _collect_and_persist_tags(st_ref, artifact, root)
    return f"Review finished — saved to {artifact_path}"


def main() -> None:
    """Run the ingest review Streamlit app."""
    root = load_repo_dotenv()
    st.set_page_config(
        page_title="LLM Wiki",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    app_view = st.radio(
        "View",
        ["Ingest review", "Tag registry"],
        horizontal=True,
        key="dashboard_app_view",
    )

    if app_view == "Tag registry":
        from src.dashboard.tag_registry_ui import render_tag_registry

        st.title("Tag registry")
        with st.sidebar:
            st.header("Settings")
            st.caption(f"Repo root: `{root}`")
        render_tag_registry(st, root=root)
        return

    st.title("LLM Wiki — ingest review")

    with st.sidebar:
        st.header("Settings")
        raw_dir = Path(
            st.text_input("Raw readwise dir", value=str(root / "raw" / "readwise"))
        ).expanduser()
        wiki_root = Path(st.text_input("Wiki root", value=str(root / "wiki"))).expanduser()
        reviews_root = Path(
            st.text_input("Reviews state dir", value=str(root / "state" / "reviews"))
        ).expanduser()
        model = st.text_input(
            "OpenAI model", value=os.environ.get("INGEST_OPENAI_MODEL", "gpt-4o-mini")
        )
        prompt_version = st.text_input("Prompt version", value=PROMPT_VERSION)
        max_chars = st.number_input(
            "Max plain-text chars", min_value=5000, value=120_000, step=1000
        )
        overwrite = st.checkbox("Overwrite existing analysis (backs up file)", value=False)
        has_key = bool(os.environ.get("OPENAI_API_KEY"))
        st.caption(
            "API key: **loaded** from environment or `.env`."
            if has_key
            else "API key: **not set** — add `OPENAI_API_KEY` to `.env` at repo root."
        )

    tool_types = load_tool_types(root)
    tool_tags = load_tool_tags(root)
    model_types = load_model_types(root)
    model_tags = load_model_tags(root)
    howto_tags = load_howto_tags(root)
    impl_study_tags = load_impl_study_tags(root)
    glossary_tags = load_glossary_tags(root)
    topic_tags = load_topic_tags(root)
    trend_tags = load_trend_tags(root)
    extraction_budgets = load_extraction_budgets(root)
    if not tool_types:
        st.warning("No tool types loaded — check ``config/review_tool_types.yaml``.")
    if not model_types:
        st.warning("No model types loaded — check ``config/review_model_types.yaml``.")
    if not howto_tags:
        st.warning("No how-to tags loaded — check ``config/review_tags_howto.yaml``.")
    if not impl_study_tags:
        st.warning("No impl-study tags loaded — check ``config/review_tags_impl_study.yaml``.")

    html_paths = list_readwise_html_sources(raw_dir)
    if not html_paths:
        st.info("No ``*.html`` sources found under the raw directory.")
        return

    source_ids = [p.stem for p in html_paths]
    status_map = build_source_status_map(reviews_root, source_ids)
    counts = count_by_status(status_map)
    finish_flash = st.session_state.pop("_finish_review_flash", None)
    if finish_flash:
        st.success(finish_flash)
    skip_flash = st.session_state.pop("_skip_extraction_flash", None)
    if skip_flash:
        st.success(f"Skipped **{skip_flash}** — no review artifact saved.")
    st.caption(
        f"{counts['in_progress']} in progress · "
        f"{counts['not_started']} not started · "
        f"{counts['finished']} finished · "
        f"{counts['skipped']} skipped "
        f"(of {len(html_paths)} total)"
    )

    filter_labels = [label for label, _ in SOURCE_REVIEW_FILTER_OPTIONS]
    if "review_queue_filter_radio" not in st.session_state:
        st.session_state["review_queue_filter_radio"] = DEFAULT_SOURCE_REVIEW_FILTER

    pick_col, _filter_col = st.columns([1, 3])
    with pick_col:
        if st.button("Random unfinished", help="Pick a random source that is not finished yet."):
            pool_ids = unfinished_source_ids(source_ids, status_map)
            id_to_path_all = {p.stem: p for p in html_paths}
            pool_paths = [
                id_to_path_all[sid]
                for sid in pool_ids
                if sid in id_to_path_all
                and readwise_source_status(id_to_path_all[sid]) != "incomplete"
            ]
            if not pool_paths:
                st.warning("No unfinished sources available (or only incomplete exports).")
            else:
                picked = random.choice(pool_paths)
                st.session_state["review_queue_filter_radio"] = "Needs work"
                st.session_state["review_source_pick_id"] = picked.stem
                st.session_state["review_source_id"] = picked.stem
                st.rerun()

    queue_filter = st.radio(
        "Show sources",
        filter_labels,
        horizontal=True,
        key="review_queue_filter_radio",
    )
    allowed = filter_statuses_for_label(queue_filter)
    visible_ids = filter_source_ids(source_ids, status_map, allowed)
    id_to_path = {p.stem: p for p in html_paths}
    visible_paths = [id_to_path[sid] for sid in visible_ids if sid in id_to_path]

    if not visible_paths:
        st.info(f"No sources match **{queue_filter}**. Try another filter.")
        return

    pick_id = st.session_state.pop("review_source_pick_id", None)
    if pick_id and pick_id in visible_ids:
        st.session_state["review_source_id"] = pick_id
    current_source_id = st.session_state.get("review_source_id")
    if not isinstance(current_source_id, str) or current_source_id not in visible_ids:
        st.session_state["review_source_id"] = visible_ids[0]

    def _format_source_id(sid: str) -> str:
        path = id_to_path[sid]
        prefix = status_label(status_map[sid])
        incom = " (incomplete)" if readwise_source_status(path) == "incomplete" else ""
        title = artifact_title_for_source(reviews_root, sid)
        if title:
            return f"{prefix} — {title}{incom}"
        return f"{prefix} — {path.name}{incom}"

    source_id = st.selectbox(
        "Source",
        visible_ids,
        format_func=_format_source_id,
        key="review_source_id",
    )
    selected = id_to_path[source_id]
    source_review_status = status_map[source_id]

    if readwise_source_status(selected) == "incomplete":
        st.error("Missing sibling ``.md`` — export incomplete.")
        return

    try:
        doc = load_readwise_pair(selected, max_plain_text_chars=int(max_chars))
    except OSError as exc:
        st.error(f"Failed to load source: {exc}")
        return

    wiki_sources = wiki_root / "sources"
    ingest_items = {i.basename: i for i in list_ingest_items(raw_dir, wiki_sources)}
    item = ingest_items.get(source_id)
    wiki_ingested = item is not None and item.status == "ingested"

    st.subheader("Source metadata")
    st.caption(f"Review queue: **{status_label(source_review_status)}**")
    if is_source_skipped(reviews_root, source_id):
        skip_meta = skip_entry_for_source(reviews_root, source_id) or {}
        skipped_at = str(skip_meta.get("skipped_at") or "").strip() or "unknown time"
        st.info(
            "This source is **skipped for extraction** (marked "
            f"{skipped_at}). Use **Analyze source** to run extraction anyway, "
            "or pick another article from the queue."
        )
    c1, c2, c3 = st.columns(3)
    c1.metric("Wiki source page exists", "yes" if wiki_ingested else "no")
    c2.text(f"SHA256\n{doc.content_sha256[:16]}…")
    c3.text(f"URL\n{doc.canonical_url or '—'}")
    st.json(
        {
            "title": doc.title,
            "author": doc.author,
            "publication": doc.publication,
            "published_date": doc.published_date,
            "canonical_url": doc.canonical_url,
            "category": doc.frontmatter.get("category"),
            "readwise_id": doc.frontmatter.get("readwise_id"),
            "raw_html": str(doc.raw_html_path),
            "raw_md": str(doc.raw_md_path),
        }
    )

    artifact_path = review_artifact_path(source_id, state_reviews=reviews_root)
    existing = load_artifact(artifact_path)

    if existing:
        st.caption(
            f"Existing review artifact — last saved: "
            f"{(existing.get('review_session') or {}).get('last_saved_at') or 'never'}; "
            f"status mix: {aggregate_review_status(existing)}"
        )
        if existing.get("source", {}).get("content_sha256") != doc.content_sha256:
            st.warning("Stored analysis hash does not match current export — stale analysis.")

    if "artifact" not in st.session_state:
        st.session_state["artifact"] = None
    if "artifact_source_id" not in st.session_state:
        st.session_state["artifact_source_id"] = None

    if st.session_state["artifact_source_id"] != source_id:
        st.session_state["artifact"] = existing
        st.session_state["artifact_source_id"] = source_id

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Analyze source", type="primary"):
            if not os.environ.get("OPENAI_API_KEY"):
                st.error("OPENAI_API_KEY is not set.")
            elif (
                existing
                and not overwrite
                and (existing.get("source") or {}).get("content_sha256") == doc.content_sha256
            ):
                st.warning(
                    "Artifact already exists for this content hash — enable **Overwrite** "
                    "in the sidebar to replace (a backup is written first)."
                )
            else:
                if existing and overwrite:
                    backup_artifact(artifact_path)
                unskip_source(reviews_root, source_id)
                try:
                    provider = OpenAIIngestionProvider()
                    artifact, _parsed = run_classification(
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
                        model=model,
                        prompt_version=prompt_version,
                        reviews_root=reviews_root,
                    )
                    st.session_state["artifact"] = artifact
                    st.session_state["artifact_source_id"] = source_id
                    st.session_state.pop(f"{source_id[:40]}_review_mode", None)
                    st.success("Analysis complete.")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Analysis failed: {exc}")
                    with st.expander("Traceback"):
                        st.text(traceback.format_exc())

    with col_b:
        if st.button(
            "Skip extraction",
            help="Skip this article: no LLM extraction and no review.json is written.",
        ):
            skip_source_for_extraction(
                reviews_root,
                source_id,
                title=doc.title or "",
                content_sha256=doc.content_sha256,
            )
            st.session_state["artifact"] = None
            st.session_state["artifact_source_id"] = None
            st.session_state.pop(f"{source_id[:40]}_review_mode", None)
            refreshed_status = build_source_status_map(reviews_root, source_ids)
            next_pool = unfinished_source_ids(source_ids, refreshed_status)
            if next_pool:
                st.session_state["review_source_pick_id"] = next_pool[0]
            st.session_state["_skip_extraction_flash"] = doc.title or source_id
            st.rerun()

    artifact_early = st.session_state.get("artifact")
    with col_c:
        if artifact_early and st.button("Finish review", type="primary"):
            msg = finish_review_session(st, artifact_early, artifact_path, root)
            st.session_state["artifact"] = artifact_early
            st.session_state["_finish_review_flash"] = msg
            st.rerun()

    artifact = st.session_state.get("artifact")
    if not artifact:
        if is_source_skipped(reviews_root, source_id):
            st.caption("Skipped — nothing to review until you run **Analyze source**.")
        else:
            st.info("Run **Analyze source** to continue.")
        return

    pending_regen = st.session_state.pop("_pending_section_regen", None)
    if (
        pending_regen
        and pending_regen.get("source_id") == source_id
        and isinstance(pending_regen.get("section"), str)
    ):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY is not set — cannot regenerate a section.")
        else:
            sk = str(pending_regen["section"])
            note = str(pending_regen.get("note") or "")
            llm_ss = (artifact.get("llm_output") or {}).get("source_summary") or {}
            if sk == "key_insights":
                cur_val: str | list[str] | None = llm_ss.get("key_insights") or []
            elif sk == "sources":
                cur_val = llm_ss.get("sources") or []
            else:
                cur_val = llm_ss.get(sk)
            try:
                provider = OpenAIIngestionProvider()
                with st.spinner(f"Regenerating {sk}…"):
                    fragment, regen_meta = provider.regenerate_source_section(
                        document=doc,
                        section_key=sk,
                        current_value=cur_val,
                        reviewer_instruction=note or None,
                        model=model,
                        prompt_version=prompt_version,
                        max_plain_text_chars=int(max_chars),
                    )
                apply_regenerated_source_section(
                    artifact,
                    str(fragment["section_key"]),
                    fragment["content"],
                    model=model,
                    prompt_version=str(regen_meta.get("prompt_version") or prompt_version),
                )
                st.session_state["artifact"] = artifact
                touch_review_session(artifact)
                save_artifact(artifact_path, artifact)
                st.success(f"Regenerated **{sk}**.")
            except Exception as exc:  # noqa: BLE001
                attach_error(artifact, f"regenerate {sk}: {exc}")
                st.session_state["artifact"] = artifact
                st.error(f"Regeneration failed: {exc}")

    pending_source_summary = st.session_state.pop("_pending_source_summary_refresh", None)
    if pending_source_summary == source_id and source_summary_is_empty(artifact):
        if not os.environ.get("OPENAI_API_KEY"):
            st.warning("Source summary is empty. Set OPENAI_API_KEY to generate it.")
        else:
            try:
                provider = OpenAIIngestionProvider()
                with st.spinner("Generating source chapters…"):
                    run_source_summary_refresh(
                        provider,
                        doc,
                        artifact,
                        model=model,
                        prompt_version=prompt_version,
                    )
                touch_review_session(artifact)
                save_artifact(artifact_path, artifact)
                st.success("Source summary generated.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Source summary failed: {exc}")

    pending_forced_extract = st.session_state.pop("_pending_forced_extract", None)
    if pending_forced_extract:
        st.session_state["artifact"] = artifact
        process_pending_forced_extract(
            st,
            pending_raw=pending_forced_extract,
            source_id=source_id,
            artifact=artifact,
            artifact_path=artifact_path,
            document=doc,
            wiki_root=wiki_root,
            model=model,
            prompt_version=prompt_version,
            max_plain_text_chars=int(max_chars),
            topic_tags=topic_tags,
            trend_tags=trend_tags,
            howto_tags=howto_tags,
            glossary_tags=glossary_tags,
            model_types=model_types,
            tool_types=tool_types,
            impl_study_tags=impl_study_tags,
            tool_tags=tool_tags,
            model_tags=model_tags,
            reviews_root=reviews_root,
        )

    pending_proposal_regen = st.session_state.pop("_pending_proposal_regen", None)
    legacy_topic_regen = st.session_state.pop("_pending_topic_regen", None)
    if pending_proposal_regen or legacy_topic_regen:
        st.session_state["artifact"] = artifact
        process_pending_proposal_regen(
            st,
            pending_raw=pending_proposal_regen or legacy_topic_regen,
            source_id=source_id,
            artifact=artifact,
            artifact_path=artifact_path,
            document=doc,
            wiki_root=wiki_root,
            model=model,
            prompt_version=prompt_version,
            max_plain_text_chars=int(max_chars),
            topic_tags=topic_tags,
            trend_tags=trend_tags,
            howto_tags=howto_tags,
            glossary_tags=glossary_tags,
            model_types=model_types,
            tool_types=tool_types,
            impl_study_tags=impl_study_tags,
            reviews_root=reviews_root,
        )

    key_prefix = source_id[:40]
    wiki_glossary_seed = parse_glossary_terms(wiki_root / "glossary" / "index.md", cap=200)
    st.caption(
        f"Artifact schema v{artifact.get('artifact_schema_version', '?')} · "
        f"Review mix: **{aggregate_review_status(artifact)}**"
    )

    review_mode = render_skip_extraction_screen(
        st,
        artifact,
        key_prefix=key_prefix,
        source_title=doc.title or "",
    )
    if review_mode is None and (
        (artifact.get("llm_output") or {}).get("extraction_meta") or {}
    ).get("skip_recommended"):
        st.info("Choose how to handle this article above to continue.")
        return

    if review_mode == "full":
        emeta = (artifact.get("llm_output") or {}).setdefault("extraction_meta", {})
        if isinstance(emeta, dict):
            emeta["skip_recommended"] = False
        has_entities = any(
            (artifact.get("review") or {}).get(k)
            for k in (
                "topics",
                "glossary",
                "how_to",
                "industry_trends",
                "tools",
                "foundation_models",
            )
        )
        if not has_entities:
            if not os.environ.get("OPENAI_API_KEY"):
                st.error("OPENAI_API_KEY is not set.")
            elif st.button(
                "Run full entity extraction",
                key=f"{key_prefix}_run_entity_extract",
                type="primary",
            ):
                try:
                    provider = OpenAIIngestionProvider()
                    with st.spinner("Extracting entities…"):
                        run_entity_extraction_for_artifact(
                            provider,
                            doc,
                            artifact,
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
                            model=model,
                            prompt_version=prompt_version,
                            reviews_root=reviews_root,
                        )
                    st.session_state["artifact"] = artifact
                    touch_review_session(artifact)
                    save_artifact(artifact_path, artifact)
                    st.success("Entity extraction complete.")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Entity extraction failed: {exc}")

    if review_mode == "source_only" and source_summary_is_empty(artifact):
        if not os.environ.get("OPENAI_API_KEY"):
            st.warning("Source summary is empty. Set OPENAI_API_KEY to generate it.")
        elif st.button(
            "Generate source summary",
            key=f"{key_prefix}_gen_source_summary",
            type="primary",
        ):
            try:
                provider = OpenAIIngestionProvider()
                with st.spinner("Generating source chapters…"):
                    run_source_summary_refresh(
                        provider,
                        doc,
                        artifact,
                        model=model,
                        prompt_version=prompt_version,
                    )
                st.session_state["artifact"] = artifact
                touch_review_session(artifact)
                save_artifact(artifact_path, artifact)
                st.success("Source summary generated.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Source summary failed: {exc}")

    default_force_title = doc.title or ""
    if ":" in default_force_title:
        default_force_title = default_force_title.split(":", 1)[-1].strip()
    render_force_extract_panel(
        st,
        source_id=source_id,
        key_prefix=key_prefix,
        default_entity_key="topic",
        default_title=default_force_title,
        compact=review_mode != "source_only",
    )

    render_compact_review_stats(st, artifact, key_prefix=key_prefix)

    tab_options = build_review_entity_tab_options(artifact, REVIEW_ENTITY_TABS)
    stored_tab = st.session_state.get("review_entity_tab", REVIEW_ENTITY_TABS[0])
    normalized_tab = normalize_review_entity_tab(str(stored_tab))
    if normalized_tab not in REVIEW_ENTITY_TABS:
        normalized_tab = REVIEW_ENTITY_TABS[0]
    st.session_state["review_entity_tab"] = tab_options[REVIEW_ENTITY_TABS.index(normalized_tab)]

    prev_entity_tab_key = f"{key_prefix}_review_entity_tab_prev"
    prev_entity_tab = st.session_state.get(prev_entity_tab_key)

    entity_tab_display = st.radio(
        "Review section",
        tab_options,
        horizontal=True,
        key="review_entity_tab",
        label_visibility="collapsed",
    )
    entity_tab = normalize_review_entity_tab(str(entity_tab_display))

    if (
        isinstance(prev_entity_tab, str)
        and prev_entity_tab != entity_tab
        and prev_entity_tab in ENTITY_TABS_WITH_PROPOSAL_AUTOSAVE
    ):
        run_proposal_autosave(key_prefix)
    st.session_state[prev_entity_tab_key] = entity_tab

    with reading_width_column(st):
        if entity_tab == "Source chapters":
            render_source_summary_review(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
            )
        elif entity_tab == "Glossary":
            render_glossary_proposals(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                glossary_tags=glossary_tags,
                artifact_path=artifact_path,
                wiki_glossary_terms=wiki_glossary_seed,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Topics":
            render_topic_proposals(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
                topic_tags=topic_tags,
                model=model,
                prompt_version=prompt_version,
                wiki_root=wiki_root,
                reviews_root=reviews_root,
            )
        elif entity_tab == "How-tos":
            render_howto_proposals(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
                howto_tags=howto_tags,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Trends":
            render_trend_proposals(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
                trend_tags=trend_tags,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Tools":
            render_tool_proposals(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
                tool_types=tool_types,
                tool_tags=tool_tags,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Models":
            render_model_proposals(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
                model_types=model_types,
                model_tags=model_tags,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Impl studies":
            render_implementation_studies(
                st,
                artifact,
                key_prefix=key_prefix,
                source_id=source_id,
                artifact_path=artifact_path,
                impl_study_tags=impl_study_tags,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Signals":
            render_roundup_signals(
                st,
                artifact,
                trend_tags=trend_tags,
                key_prefix=key_prefix,
                artifact_path=artifact_path,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Insights":
            render_interview_insights(
                st,
                artifact,
                topic_tags=topic_tags,
                key_prefix=key_prefix,
                artifact_path=artifact_path,
                model=model,
                prompt_version=prompt_version,
            )
        elif entity_tab == "Source type":
            render_source_type_override_panel(
                st,
                artifact,
                key_prefix=key_prefix,
                doc=doc,
                wiki_root=wiki_root,
                reviews_root=reviews_root,
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
                model=model,
                prompt_version=prompt_version,
            )
            render_source_evidence_profile(st, artifact, key_prefix=key_prefix)
            render_source_type_detection(st, artifact, key_prefix=key_prefix)
        elif entity_tab == "Debug":
            st.json(artifact.get("llm_output"))

        if st.button("Save draft"):
            touch_review_session(artifact)
            save_artifact(artifact_path, artifact)
            st.success(f"Draft saved to {artifact_path}")

        st.caption(f"Artifact path: {artifact_path}")


if __name__ == "__main__":
    main()
