"""Tests for dashboard tag review helpers (no Streamlit runtime)."""

from __future__ import annotations

from unittest.mock import MagicMock

from src.ingest_review.artifact import ensure_sources_review_auto_approved
from src.ingest_review.dashboard_ui import (
    apply_chapter_edit,
    build_readonly_chapters_markdown,
    build_tag_select_options,
    chapter_edit_textarea_value,
    effective_list_chapter_lines,
    effective_scalar_chapter_text,
    format_proposed_tags_caption,
    format_source_link_markdown,
    google_search_markdown,
    normalize_sources_list,
    render_skip_extraction_screen,
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


def test_normalize_sources_list_filters_empty_and_non_list() -> None:
    """Non-list input yields empty; blanks are dropped."""
    assert normalize_sources_list(None) == []
    assert normalize_sources_list([" https://a.com ", "", "ref"]) == [
        "https://a.com",
        "ref",
    ]


def test_format_source_link_markdown_http_is_clickable() -> None:
    """HTTP(S) URLs render as markdown links."""
    md = format_source_link_markdown("https://example.com/path")
    assert md == "- [https://example.com/path](https://example.com/path)"


def test_format_source_link_markdown_plain_reference_is_bullet() -> None:
    """Non-URL references stay plain bullets."""
    assert format_source_link_markdown("Smith et al., 2024") == "- Smith et al., 2024"


def test_ensure_sources_review_auto_approved_sets_status() -> None:
    """Pending sources review node becomes approved on load."""
    artifact = {
        "review": {
            "source_summary": {
                "sources": {"status": "pending", "final_list": ["x"], "llm_list": []},
            }
        }
    }
    ensure_sources_review_auto_approved(artifact)
    node = artifact["review"]["source_summary"]["sources"]
    assert node["status"] == "approved"
    assert node["final_list"] is None


def _sample_artifact() -> dict:
    return {
        "llm_output": {
            "source_summary": {
                "summary": "LLM summary",
                "key_insights": ["a", "b"],
                "sources": ["https://example.com"],
            }
        },
        "review": {"source_summary": {}},
    }


def test_effective_scalar_chapter_text_prefers_final_text() -> None:
    """final_text overrides LLM draft when set."""
    llm_ss = {"summary": "LLM summary"}
    node = {"final_text": "Edited"}
    assert effective_scalar_chapter_text(llm_ss, node, "summary") == "Edited"


def test_effective_list_chapter_lines_prefers_final_list() -> None:
    """final_list overrides llm_list when set."""
    llm_ss = {"key_insights": ["a"]}
    node = {"final_list": ["x", "y"], "llm_list": ["a"]}
    assert effective_list_chapter_lines(llm_ss, node, "key_insights") == ["x", "y"]


def test_apply_chapter_edit_modified_when_text_differs() -> None:
    """Edited scalar sets status modified and stores final_text."""
    artifact = _sample_artifact()
    apply_chapter_edit(artifact, "summary", "Reviewer version")
    node = artifact["review"]["source_summary"]["summary"]
    assert node["status"] == "modified"
    assert node["final_text"] == "Reviewer version"


def test_apply_chapter_edit_approved_when_unchanged() -> None:
    """Unchanged scalar clears final_text and sets approved."""
    artifact = _sample_artifact()
    apply_chapter_edit(artifact, "summary", "LLM summary")
    node = artifact["review"]["source_summary"]["summary"]
    assert node["status"] == "approved"
    assert node["final_text"] is None


def test_apply_chapter_edit_key_insights_caps_at_five() -> None:
    """key_insights edits are capped at five lines."""
    artifact = _sample_artifact()
    raw = "\n".join(f"line{i}" for i in range(7))
    apply_chapter_edit(artifact, "key_insights", raw)
    node = artifact["review"]["source_summary"]["key_insights"]
    assert node["status"] == "modified"
    assert node["final_list"] == [f"line{i}" for i in range(5)]


def test_build_readonly_chapters_markdown_includes_headings() -> None:
    """Read-only markdown includes chapter headings and body."""
    md = build_readonly_chapters_markdown(_sample_artifact())
    assert "## Summary" in md
    assert "LLM summary" in md
    assert "## Key insights" in md
    assert "- a" in md
    assert "## Sources" in md
    assert "https://example.com" in md


def test_chapter_edit_textarea_value_reflects_effective_text() -> None:
    """Edit box default uses effective chapter content."""
    artifact = _sample_artifact()
    apply_chapter_edit(artifact, "summary", "Edited summary")
    assert chapter_edit_textarea_value(artifact, "summary") == "Edited summary"


def test_google_search_markdown_builds_encoded_url() -> None:
    md = google_search_markdown("RAG patterns")
    assert '[Google: "RAG patterns"]' in md
    assert "google.com/search" in md
    assert "q=RAG+patterns" in md or "q=RAG%20patterns" in md


def test_google_search_markdown_empty_query() -> None:
    assert google_search_markdown("") == ""
    assert google_search_markdown("   ") == ""


def test_render_skip_extraction_screen_never_gates_tools_roundup() -> None:
    """List tool roundups bypass the skip gate even when skip_recommended is true."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    artifact = {
        "llm_output": {
            "source_type_detection": {"detected_source_type": "ai_tools_roundup"},
            "extraction_meta": {"skip_recommended": True, "skip_reason": "test"},
        }
    }
    assert render_skip_extraction_screen(mock_st, artifact, key_prefix="pfx") is False
    mock_st.warning.assert_not_called()
    mock_st.info.assert_called_once()


def test_render_skip_extraction_screen_never_gates_how_to_roundup() -> None:
    """List how-to roundups bypass the skip gate."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    artifact = {
        "llm_output": {
            "source_type_detection": {"detected_source_type": "how_to_roundup"},
            "extraction_meta": {"skip_recommended": True},
        }
    }
    assert render_skip_extraction_screen(mock_st, artifact, key_prefix="pfx") is False
    mock_st.info.assert_called_once()


def test_render_skip_extraction_screen_shows_warning_when_skip_and_not_roundup() -> None:
    """Standard articles with skip_recommended still show the warning."""
    col1, col2 = MagicMock(), MagicMock()
    col1.button.return_value = False
    col2.button.return_value = False
    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.columns.return_value = (col1, col2)
    artifact = {
        "llm_output": {
            "source_type_detection": {"detected_source_type": "standard_article"},
            "extraction_meta": {
                "skip_recommended": True,
                "skip_reason": "No durable knowledge",
                "review_burden_estimate": "low",
                "total_candidates_considered": 3,
            },
        }
    }
    assert render_skip_extraction_screen(mock_st, artifact, key_prefix="pfx") is False
    mock_st.warning.assert_called_once()
