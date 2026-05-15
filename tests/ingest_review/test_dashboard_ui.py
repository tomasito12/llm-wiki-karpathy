"""Tests for dashboard tag review helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.dashboard_ui import (
    build_tag_select_options,
    format_proposed_tags_caption,
)


def test_format_proposed_tags_caption_allowlist_provenance() -> None:
    """Caption marks allowlist tags vs suggested new."""
    caption = format_proposed_tags_caption(
        {"primary_tag": "rag", "secondary_tag": "", "suggested_new_tag": "novel-area"},
        {},
        ["rag", "evaluation"],
    )
    assert caption is not None
    assert "rag (allowlist)" in caption
    assert "novel-area (suggested new)" in caption


def test_format_proposed_tags_caption_prefers_reviewer_final_tags() -> None:
    """Reviewer final_* overrides LLM primary/secondary in caption."""
    caption = format_proposed_tags_caption(
        {"primary_tag": "rag", "secondary_tag": ""},
        {"final_primary_tag": "evaluation"},
        ["rag", "evaluation"],
    )
    assert caption is not None
    assert "evaluation (allowlist)" in caption
    assert "rag" not in caption


def test_format_proposed_tags_caption_empty_returns_none() -> None:
    """No tags yields None caption."""
    assert format_proposed_tags_caption({}, {}, []) is None


def test_build_tag_select_options_delegates_to_tags_module() -> None:
    """build_tag_select_options is re-exported consistently from tags module."""
    opts = build_tag_select_options(["a"], {"primary_tag": "b"})
    assert "" in opts
    assert "a" in opts
    assert "b" in opts
