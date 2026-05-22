"""Tests for shared two-column proposal expander layout."""

from __future__ import annotations

from unittest.mock import MagicMock

from src.ingest_review.proposal_columns_ui import (
    build_proposal_expander_label,
    render_proposal_edit_column,
    render_proposal_read_column,
    strip_leading_markdown_heading,
)


def test_strip_leading_markdown_heading_removes_h2_title() -> None:
    md = "## Term\n\nBody text here."
    assert strip_leading_markdown_heading(md) == "Body text here."


def test_strip_leading_markdown_heading_noop_without_heading() -> None:
    md = "Body only."
    assert strip_leading_markdown_heading(md) == "Body only."


def test_build_proposal_expander_label_includes_badge_and_status() -> None:
    node = {"proposal_status": "pending", "llm_item": {"value_level": "high"}}
    label = build_proposal_expander_label(node, "RAG", badge="High")
    assert label == "RAG · High · Approved"


def test_render_proposal_read_column_single_node_no_expander() -> None:
    st = MagicMock()
    nodes = [{"proposal_id": "a"}]

    render_proposal_read_column(
        st,
        nodes,
        empty_text="empty",
        markdown_for_node=lambda _n: "**body**",
        label_for_node=lambda _n, _i: "x",
        use_expanders=False,
        key_prefix="pfx",
    )

    st.expander.assert_not_called()
    st.markdown.assert_called_once_with("**body**")


def test_render_proposal_read_column_multiple_uses_expanders() -> None:
    st = MagicMock()
    expander_ctx = MagicMock()
    st.expander.return_value.__enter__ = MagicMock(return_value=expander_ctx)
    st.expander.return_value.__exit__ = MagicMock(return_value=False)
    nodes = [{"proposal_id": "a"}, {"proposal_id": "b"}]

    render_proposal_read_column(
        st,
        nodes,
        empty_text="empty",
        markdown_for_node=lambda _n: "## Title\n\ncontent",
        label_for_node=lambda _n, i: f"Item {i}",
        use_expanders=True,
        key_prefix="pfx",
    )

    assert st.expander.call_count == 2
    st.expander.assert_any_call("Item 0", expanded=False, key="pfx_read_exp_0")
    st.expander.assert_any_call("Item 1", expanded=False, key="pfx_read_exp_1")
    st.markdown.assert_any_call("content")


def test_render_proposal_edit_column_single_skips_expander() -> None:
    st = MagicMock()
    rendered: list[str] = []

    render_proposal_edit_column(
        st,
        [{"proposal_id": "a"}],
        label_for_node=lambda _n, _i: "x",
        render_edit_for_node=lambda _n, _i: rendered.append("ok"),
        use_expanders=False,
        key_prefix="pfx",
    )

    st.expander.assert_not_called()
    assert rendered == ["ok"]
