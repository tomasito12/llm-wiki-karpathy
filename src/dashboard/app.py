"""Streamlit dashboard: ingest review (classification + human approval)."""

from __future__ import annotations

import sys
from pathlib import Path

# Streamlit adds ``src/dashboard`` to ``sys.path``, not the repo root — ensure ``src`` imports work.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import os
import traceback

import streamlit as st

from src.ingest_queue.queue import list_ingest_items
from src.ingest_review.analyze import run_classification
from src.ingest_review.artifact import (
    aggregate_review_status,
    apply_regenerated_source_section,
    attach_error,
    backup_artifact,
    load_artifact,
    review_artifact_path,
    save_artifact,
    touch_review_session,
)
from src.ingest_review.dashboard_ui import (
    render_source_summary_review,
    render_source_type_detection,
)
from src.ingest_review.extract import (
    list_readwise_html_sources,
    load_readwise_pair,
    readwise_source_status,
)
from src.ingest_review.feedback_store import default_feedback_db_path, record_events_from_artifact
from src.ingest_review.glossary_ui import (
    collect_glossary_approved_new_tags,
    render_glossary_proposals,
)
from src.ingest_review.howtos_ui import (
    collect_howto_approved_new_tags,
    render_howto_proposals,
)
from src.ingest_review.impl_study_ui import (
    collect_approved_new_tags,
    render_implementation_studies,
)
from src.ingest_review.insights_ui import render_interview_insights
from src.ingest_review.models_ui import (
    collect_model_approved_new_types,
    render_model_proposals,
)
from src.ingest_review.paths import load_repo_dotenv
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.schema import PROMPT_VERSION
from src.ingest_review.signals_ui import render_roundup_signals
from src.ingest_review.tags import (
    append_tags_to_yaml,
    default_glossary_tags_path,
    default_howto_tags_path,
    default_impl_study_tags_path,
    default_model_types_path,
    default_tool_types_path,
    default_topic_tags_path,
    default_trend_tags_path,
    load_glossary_tags,
    load_howto_tags,
    load_impl_study_tags,
    load_model_types,
    load_tool_types,
    load_topic_tags,
    load_trend_tags,
)
from src.ingest_review.tools_ui import (
    collect_tool_approved_new_types,
    render_tool_proposals,
)
from src.ingest_review.topics_ui import (
    collect_topic_approved_new_tags,
    render_topic_contributions,
)
from src.ingest_review.trends_ui import (
    collect_trend_approved_new_tags,
    render_trend_proposals,
)


def main() -> None:
    """Run the ingest review Streamlit app."""
    root = load_repo_dotenv()
    st.set_page_config(
        page_title="LLM Wiki — ingest review",
        layout="wide",
        initial_sidebar_state="expanded",
    )
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
    model_types = load_model_types(root)
    howto_tags = load_howto_tags(root)
    impl_study_tags = load_impl_study_tags(root)
    glossary_tags = load_glossary_tags(root)
    topic_tags = load_topic_tags(root)
    trend_tags = load_trend_tags(root)
    if not tool_types:
        st.warning("No tool types loaded — check ``config/review_tool_types.yaml``.")
    if not model_types:
        st.warning("No model types loaded — check ``config/review_model_types.yaml``.")
    if not howto_tags:
        st.warning("No how-to tags loaded — check ``config/review_tags_howto.yaml``.")
    if not impl_study_tags:
        st.warning("No impl-study tags loaded — check ``config/review_tags_impl_study.yaml``.")

    html_paths = list_readwise_html_sources(raw_dir)
    labels = []
    for p in html_paths:
        status = readwise_source_status(p)
        suffix = " (incomplete)" if status == "incomplete" else ""
        labels.append(f"{p.name}{suffix}")

    if not html_paths:
        st.info("No ``*.html`` sources found under the raw directory.")
        return

    choice = st.selectbox("Source", range(len(html_paths)), format_func=lambda i: labels[i])
    selected = html_paths[int(choice)]
    source_id = selected.stem

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
    c1, c2, c3 = st.columns(3)
    c1.metric("Wiki source page exists", "yes" if wiki_ingested else "no")
    c2.text(f"SHA256\n{doc.content_sha256[:16]}…")
    c3.text(f"URL\n{doc.canonical_url or '—'}")
    st.json(
        {
            "title": doc.title,
            "author": doc.author,
            "published_date": doc.published_date,
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

    col_a, col_b = st.columns(2)
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
                        model=model,
                        prompt_version=prompt_version,
                    )
                    st.session_state["artifact"] = artifact
                    st.session_state["artifact_source_id"] = source_id
                    st.success("Analysis complete.")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Analysis failed: {exc}")
                    with st.expander("Traceback"):
                        st.text(traceback.format_exc())

    with col_b:
        if existing and st.button("Load saved artifact"):
            st.session_state["artifact"] = existing
            st.session_state["artifact_source_id"] = source_id
            st.rerun()

    artifact = st.session_state.get("artifact")
    if not artifact:
        st.info("Run **Analyze source** or **Load saved artifact** to continue.")
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
                st.success(f"Regenerated **{sk}**.")
            except Exception as exc:  # noqa: BLE001
                attach_error(artifact, f"regenerate {sk}: {exc}")
                st.session_state["artifact"] = artifact
                st.error(f"Regeneration failed: {exc}")

    key_prefix = source_id[:40]
    st.caption(
        f"Artifact schema v{artifact.get('artifact_schema_version', '?')} · "
        f"Review mix: **{aggregate_review_status(artifact)}**"
    )

    llm_detection = (artifact.get("llm_output") or {}).get("source_type_detection") or {}
    detected_type = llm_detection.get("detected_source_type") or "unknown"
    detection_conf = llm_detection.get("confidence") or 0
    detection_reasons = llm_detection.get("reasoning") or []
    source_type_options: list[str] = [
        "standard_article",
        "ai_industry_roundup",
        "interview_or_transcript",
        "technical_howto",
        "research_paper_or_report",
        "unknown",
    ]
    with st.container():
        st.markdown("---")
        c_det, c_over = st.columns([2, 1])
        with c_det:
            st.markdown(
                f"**Detected source type:** `{detected_type}` (confidence: {detection_conf:.0%})"
            )
            if detection_reasons:
                for r in detection_reasons:
                    st.caption(f"- {r}")
        with c_over:
            override_val = st.selectbox(
                "Override source type",
                options=["(keep detected)"] + source_type_options,
                index=0,
                key=f"{key_prefix}_srctype_override",
            )
            if override_val != "(keep detected)" and st.button(
                "Re-analyze with override", key=f"{key_prefix}_reanalyze_override"
            ):
                if not os.environ.get("OPENAI_API_KEY"):
                    st.error("OPENAI_API_KEY is not set.")
                else:
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
                            source_type_override=str(override_val),
                            model=model,
                            prompt_version=prompt_version,
                        )
                        st.session_state["artifact"] = artifact
                        st.session_state["artifact_source_id"] = source_id
                        st.success(f"Re-analysis complete (override: {override_val}).")
                        st.rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Re-analysis failed: {exc}")
                        with st.expander("Traceback"):
                            st.text(traceback.format_exc())
        st.markdown("---")

    tabs = st.tabs(
        [
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
        ]
    )
    with tabs[0]:
        render_source_summary_review(st, artifact, key_prefix=key_prefix, source_id=source_id)
    with tabs[1]:
        render_glossary_proposals(
            st,
            artifact,
            key_prefix=key_prefix,
            glossary_tags=glossary_tags,
        )
    with tabs[2]:
        render_topic_contributions(
            st,
            artifact,
            key_prefix=key_prefix,
            topic_tags=topic_tags,
        )
    with tabs[3]:
        render_howto_proposals(
            st,
            artifact,
            key_prefix=key_prefix,
            howto_tags=howto_tags,
        )
    with tabs[4]:
        render_trend_proposals(
            st,
            artifact,
            key_prefix=key_prefix,
            trend_tags=trend_tags,
        )
    with tabs[5]:
        render_tool_proposals(
            st,
            artifact,
            key_prefix=key_prefix,
            tool_types=tool_types,
        )
    with tabs[6]:
        render_model_proposals(
            st,
            artifact,
            key_prefix=key_prefix,
            model_types=model_types,
        )
    with tabs[7]:
        render_implementation_studies(
            st,
            artifact,
            key_prefix=key_prefix,
            impl_study_tags=impl_study_tags,
        )
    with tabs[8]:
        render_roundup_signals(st, artifact, key_prefix=key_prefix)
    with tabs[9]:
        render_interview_insights(st, artifact, key_prefix=key_prefix)
    with tabs[10]:
        render_source_type_detection(st, artifact, key_prefix=key_prefix)
    with tabs[11]:
        st.json(artifact.get("llm_output"))

    if st.button("Save review artifact"):
        touch_review_session(artifact)
        save_artifact(artifact_path, artifact)
        fb_path = default_feedback_db_path(root)
        try:
            record_events_from_artifact(fb_path, artifact)
        except OSError as exc:
            st.warning(f"Feedback DB write skipped: {exc}")
        new_tags = collect_approved_new_tags(artifact)
        if new_tags:
            try:
                append_tags_to_yaml(default_impl_study_tags_path(root), new_tags)
                st.caption(f"Appended {len(new_tags)} impl-study tag(s) to allowlist.")
            except OSError as exc:
                st.warning(f"Impl-study tag allowlist update skipped: {exc}")
        new_glossary_tags = collect_glossary_approved_new_tags(artifact)
        if new_glossary_tags:
            try:
                append_tags_to_yaml(default_glossary_tags_path(root), new_glossary_tags)
                st.caption(f"Appended {len(new_glossary_tags)} glossary tag(s) to allowlist.")
            except OSError as exc:
                st.warning(f"Glossary tag allowlist update skipped: {exc}")
        new_topic_tags = collect_topic_approved_new_tags(artifact)
        if new_topic_tags:
            try:
                append_tags_to_yaml(default_topic_tags_path(root), new_topic_tags)
                st.caption(f"Appended {len(new_topic_tags)} topic tag(s) to allowlist.")
            except OSError as exc:
                st.warning(f"Topic tag allowlist update skipped: {exc}")
        new_howto_tags = collect_howto_approved_new_tags(artifact)
        if new_howto_tags:
            try:
                append_tags_to_yaml(default_howto_tags_path(root), new_howto_tags)
                st.caption(f"Appended {len(new_howto_tags)} how-to tag(s) to allowlist.")
            except OSError as exc:
                st.warning(f"How-to tag allowlist update skipped: {exc}")
        new_trend_tags = collect_trend_approved_new_tags(artifact)
        if new_trend_tags:
            try:
                append_tags_to_yaml(default_trend_tags_path(root), new_trend_tags)
                st.caption(f"Appended {len(new_trend_tags)} trend tag(s) to allowlist.")
            except OSError as exc:
                st.warning(f"Trend tag allowlist update skipped: {exc}")
        new_tool_types = collect_tool_approved_new_types(artifact)
        if new_tool_types:
            try:
                append_tags_to_yaml(default_tool_types_path(root), new_tool_types)
                st.caption(f"Appended {len(new_tool_types)} tool type(s) to registry.")
            except OSError as exc:
                st.warning(f"Tool type registry update skipped: {exc}")
        new_model_types = collect_model_approved_new_types(artifact)
        if new_model_types:
            try:
                append_tags_to_yaml(default_model_types_path(root), new_model_types)
                st.caption(f"Appended {len(new_model_types)} model type(s) to registry.")
            except OSError as exc:
                st.warning(f"Model type registry update skipped: {exc}")
        st.success(f"Saved to {artifact_path}")

    st.caption(f"Artifact path: {artifact_path}")


if __name__ == "__main__":
    main()
