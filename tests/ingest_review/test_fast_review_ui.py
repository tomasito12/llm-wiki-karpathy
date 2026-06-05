"""Tests for fast single-column proposal review helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import streamlit as streamlit_runtime

from src.ingest_review.dashboard_ui import (
    SOURCE_CHAPTER_OTHER_KEYS,
    build_review_entity_tab_options,
    format_review_entity_tab_label,
    normalize_review_entity_tab,
    render_source_summary_review,
    review_overview_caption,
)
from src.ingest_review.fast_review_ui import (
    clamp_proposal_index,
    context_companion_widget_key,
    fast_card_widget_key,
    format_navigator_label,
    navigator_session_key,
    proposal_autosave_session_key,
    read_fast_card_field_values,
    register_card_autosave,
    render_inline_regenerate_title_controls,
    render_readonly_context_hint,
    run_proposal_autosave,
)


def test_navigator_session_key_includes_prefix() -> None:
    assert navigator_session_key("trends_pfx") == "trends_pfx_proposal_idx"


def test_clamp_proposal_index_bounds() -> None:
    assert clamp_proposal_index(-1, 5) == 0
    assert clamp_proposal_index(3, 5) == 3
    assert clamp_proposal_index(9, 5) == 4
    assert clamp_proposal_index(0, 0) == 0


def test_format_navigator_label_truncates_long_titles() -> None:
    long_title = "x" * 100
    label = format_navigator_label(1, 4, long_title)
    assert label.startswith("Proposal 2 of 4:")
    assert len(label) < 120


def test_fast_card_widget_key_zones() -> None:
    assert fast_card_widget_key("pfx", "trend_title", zone="title") == "pfx_edit_trend_title"
    assert fast_card_widget_key("pfx", "summary", zone="context") == "pfx_ctx_summary"
    assert fast_card_widget_key("pfx", "slug", zone="more") == "pfx_more_slug"


def test_context_companion_widget_key() -> None:
    assert (
        context_companion_widget_key("pfx", "answer_summary", "what_and_problem")
        == "pfx_ctx_answer_summary_what_and_problem"
    )


def test_read_fast_card_field_values_merges_session_state() -> None:
    streamlit_runtime.session_state.clear()
    streamlit_runtime.session_state["pfx_edit_title"] = "Title"
    streamlit_runtime.session_state["pfx_ctx_summary"] = "Summary body"
    streamlit_runtime.session_state["pfx_more_slug"] = "my-slug"

    merged = read_fast_card_field_values(
        "pfx",
        title_keys=("title",),
        context_keys=("summary",),
        more_scalar_keys=("slug",),
        field_values={"title": "stale"},
    )
    assert merged["title"] == "Title"
    assert merged["summary"] == "Summary body"
    assert merged["slug"] == "my-slug"


def test_format_review_entity_tab_label_adds_count() -> None:
    artifact = {"review": {"industry_trends": [{"proposal_id": "a"}, {"proposal_id": "b"}]}}
    assert format_review_entity_tab_label("Trends", artifact) == "Trends (2)"
    assert format_review_entity_tab_label("Source type", artifact) == "Source type"


def test_normalize_review_entity_tab_strips_count_suffix() -> None:
    assert normalize_review_entity_tab("Trends (2)") == "Trends"
    assert normalize_review_entity_tab("Glossary") == "Glossary"


def test_build_review_entity_tab_options_preserves_order() -> None:
    tabs = ("Source chapters", "Trends", "Debug")
    artifact = {"review": {"industry_trends": [{}]}}
    assert build_review_entity_tab_options(artifact, tabs) == [
        "Source chapters",
        "Trends (1)",
        "Debug",
    ]


def test_review_overview_caption_summarizes_counts() -> None:
    artifact = {
        "llm_output": {
            "topics": [{"value_level": "high"}, {"value_level": "low"}],
            "tools": [{"value_level": "medium"}],
        },
        "review": {
            "topics": [{"proposal_status": "rejected"}],
        },
    }
    caption = review_overview_caption(artifact)
    assert "3 proposals" in caption
    assert "1 high value" in caption
    assert "1 rejected" in caption


def test_source_chapter_other_keys_excludes_easy_read_and_sources() -> None:
    assert "accessible_overview" not in SOURCE_CHAPTER_OTHER_KEYS
    assert "sources" not in SOURCE_CHAPTER_OTHER_KEYS
    assert "summary" in SOURCE_CHAPTER_OTHER_KEYS


def test_register_card_autosave_approves_non_rejected_node() -> None:
    streamlit_runtime.session_state.clear()
    node: dict[str, str] = {"proposal_status": "pending"}
    calls: list[str] = []

    def _persist() -> None:
        calls.append("saved")

    register_card_autosave("tab_pfx", node, _persist)
    assert run_proposal_autosave("tab_pfx") is True
    assert calls == ["saved"]
    assert node["proposal_status"] == "approved"


def test_register_card_autosave_keeps_rejected_status() -> None:
    streamlit_runtime.session_state.clear()
    node: dict[str, str] = {"proposal_status": "rejected"}
    register_card_autosave("tab_pfx", node, lambda: None)
    run_proposal_autosave("tab_pfx")
    assert node["proposal_status"] == "rejected"


def test_run_proposal_autosave_noop_without_registration() -> None:
    streamlit_runtime.session_state.clear()
    assert run_proposal_autosave("missing") is False


def test_render_proposal_navigator_next_triggers_autosave() -> None:
    streamlit_runtime.session_state.clear()
    calls: list[str] = []
    streamlit_runtime.session_state[proposal_autosave_session_key("pfx")] = lambda: calls.append(
        "autosaved"
    )
    nodes = [{"proposal_id": "a"}, {"proposal_id": "b"}]
    prev_col, label_col, next_col = MagicMock(), MagicMock(), MagicMock()
    mock_st = MagicMock()
    mock_st.columns.return_value = (prev_col, label_col, next_col)
    mock_st.button.side_effect = [False, True]

    from src.ingest_review.fast_review_ui import render_proposal_navigator

    with patch.object(streamlit_runtime, "rerun"):
        render_proposal_navigator(
            mock_st,
            nodes,
            key_prefix="pfx",
            label_for_node=lambda _n, _i: "Title",
        )
    assert calls == ["autosaved"]
    assert streamlit_runtime.session_state["pfx_proposal_idx"] == 1


def test_render_readonly_context_hint_skips_empty_value() -> None:
    mock_st = MagicMock()
    render_readonly_context_hint(mock_st, label="Knowledge summary", value="   ")
    mock_st.caption.assert_not_called()
    mock_st.markdown.assert_not_called()


def test_render_readonly_context_hint_renders_label_and_body() -> None:
    mock_st = MagicMock()
    render_readonly_context_hint(
        mock_st,
        label="Knowledge summary",
        value="What this topic covers.",
    )
    mock_st.caption.assert_called_once_with("Knowledge summary")
    mock_st.markdown.assert_called_once_with("What this topic covers.")


def test_render_inline_regenerate_title_controls_uses_two_row_layout() -> None:
    mock_st = MagicMock()
    note_col = MagicMock()
    btn_col = MagicMock()
    mock_st.columns.return_value = (note_col, btn_col)

    render_inline_regenerate_title_controls(
        mock_st,
        entity_key="topic",
        source_id="src",
        proposal_id="pid",
        widget_prefix="pfx",
        current_title="Old title",
        title_label="New topic title",
    )

    assert mock_st.text_input.call_count == 2
    mock_st.text_input.assert_any_call(
        "New topic title",
        key="pfx_regen_new_title",
        label_visibility="collapsed",
        placeholder="New title (empty = suggest; current: Old title)",
    )
    mock_st.columns.assert_called_once_with([4, 2], vertical_alignment="bottom")
    mock_st.button.assert_called_once()
    note_col.__enter__.assert_called_once()
    btn_col.__enter__.assert_called_once()


@patch("src.ingest_review.dashboard_ui._render_chapter_edit_box")
@patch("src.ingest_review.dashboard_ui._sync_sources_review_node")
@patch("src.ingest_review.dashboard_ui._render_analysis_meta_banner")
def test_render_source_summary_review_easy_read_primary(
    _banner: MagicMock,
    _sync: MagicMock,
    render_chapter: MagicMock,
) -> None:
    """Easy read renders outside expander; other chapters live in Other chapters."""
    mock_st = MagicMock()
    expander_ctx = MagicMock()
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=expander_ctx)
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    artifact = {"llm_output": {"source_summary": {}}, "review": {"source_summary": {}}}

    render_source_summary_review(
        mock_st,
        artifact,
        key_prefix="pfx",
        source_id="src",
        artifact_path=MagicMock(),
    )

    mock_st.columns.assert_not_called()
    first_call = render_chapter.call_args_list[0]
    assert first_call.kwargs["section_key"] == "accessible_overview"
    mock_st.expander.assert_called_once_with("Other chapters", expanded=False)
    other_keys = [c.kwargs["section_key"] for c in render_chapter.call_args_list[1:]]
    assert other_keys == list(SOURCE_CHAPTER_OTHER_KEYS)
