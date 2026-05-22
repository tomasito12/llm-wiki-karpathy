"""Shared two-column read/edit layout for multi-proposal entity sections."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.ingest_review.proposal_decision_ui import proposal_status_label

MarkdownForNode = Callable[[dict[str, Any]], str]
LabelForNode = Callable[[dict[str, Any], int], str]
RenderEditForNode = Callable[[dict[str, Any], int], None]


def build_proposal_expander_label(
    node: dict[str, Any],
    title: str,
    *,
    badge: str | None = None,
) -> str:
    """Build a consistent expander title: title, optional value badge, proposal status."""
    parts: list[str] = [title.strip() or "Untitled"]
    if badge:
        parts.append(badge)
    parts.append(proposal_status_label(node))
    return " · ".join(parts)


def strip_leading_markdown_heading(markdown: str, *, level: int = 2) -> str:
    """Remove the first ATX heading of *level* (expander label replaces the title)."""
    prefix = "#" * level + " "
    lines = markdown.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith(prefix):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


def _readonly_body(markdown: str, *, in_expander: bool) -> str:
    if in_expander:
        return strip_leading_markdown_heading(markdown)
    return markdown


def render_proposal_read_column(
    st: Any,
    nodes: list[dict[str, Any]],
    *,
    empty_text: str,
    markdown_for_node: MarkdownForNode,
    label_for_node: LabelForNode,
    use_expanders: bool,
    key_prefix: str,
) -> None:
    """Render the read-only column for one or more proposals."""
    if not nodes:
        st.markdown(empty_text)
        return
    if not use_expanders:
        st.markdown(markdown_for_node(nodes[0]))
        return
    for index, node in enumerate(nodes):
        label = label_for_node(node, index)
        with st.expander(
            label,
            expanded=False,
            key=f"{key_prefix}_read_exp_{index}",
        ):
            body = _readonly_body(markdown_for_node(node), in_expander=True)
            st.markdown(body)


def render_proposal_edit_column(
    st: Any,
    nodes: list[dict[str, Any]],
    *,
    label_for_node: LabelForNode,
    render_edit_for_node: RenderEditForNode,
    use_expanders: bool,
    key_prefix: str,
) -> None:
    """Render the edit column for one or more proposals."""
    if not nodes:
        return
    if not use_expanders:
        render_edit_for_node(nodes[0], 0)
        return
    for index, node in enumerate(nodes):
        label = label_for_node(node, index)
        with st.expander(
            label,
            expanded=False,
            key=f"{key_prefix}_edit_exp_{index}",
        ):
            render_edit_for_node(node, index)


def render_two_column_proposal_review(
    st: Any,
    nodes: list[dict[str, Any]],
    *,
    key_prefix: str,
    empty_readonly_text: str,
    label_for_node: LabelForNode,
    readonly_markdown_for_node: MarkdownForNode,
    render_edit_for_node: RenderEditForNode,
) -> None:
    """Read-only catalog (left) and edit panels (right); expanders when len(nodes) > 1."""
    use_expanders = len(nodes) > 1
    read_col, edit_col = st.columns(2)
    with read_col:
        render_proposal_read_column(
            st,
            nodes,
            empty_text=empty_readonly_text,
            markdown_for_node=readonly_markdown_for_node,
            label_for_node=label_for_node,
            use_expanders=use_expanders,
            key_prefix=key_prefix,
        )
    with edit_col:
        render_proposal_edit_column(
            st,
            nodes,
            label_for_node=label_for_node,
            render_edit_for_node=render_edit_for_node,
            use_expanders=use_expanders,
            key_prefix=key_prefix,
        )
