"""Tests for Streamlit-free review value resolution."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render.resolve import (
    list_value,
    proposal_is_included,
    reviewed_tags,
    scalar_value,
    taxonomy_version,
)


def test_scalar_and_list_values_prefer_final_review_edits() -> None:
    """Final review values override the LLM proposal."""
    node = {
        "proposal_status": "approved",
        "llm_item": {"title": "LLM title", "items": ["llm"]},
        "sections": {
            "title": {"final_text": "Final title"},
            "items": {"final_list": ["final"]},
        },
    }

    assert scalar_value(node, "title") == "Final title"
    assert list_value(node, "items") == ["final"]


def test_rejected_proposals_are_excluded_and_tags_are_normalized() -> None:
    """Proposal inclusion and tags follow review metadata."""
    node = {
        "proposal_status": "rejected",
        "llm_item": {"proposed_tags": ["Agent Systems"]},
        "tags": {"final_tags": ["Context_Engineering"], "approved_new_tags": ["Agent Systems"]},
    }

    assert not proposal_is_included(node)
    assert reviewed_tags(node) == ["context-engineering", "agent-systems"]


def test_taxonomy_version_changes_when_taxonomy_files_change(tmp_path: Path) -> None:
    """Taxonomy hashes identify the active tag/type config set."""
    config = tmp_path / "config"
    config.mkdir()
    path = config / "review_tags_topics.yaml"
    path.write_text("tags:\n- ai-engineering\n", encoding="utf-8")

    first = taxonomy_version(tmp_path)
    path.write_text("tags:\n- ai-engineering\n- agent-systems\n", encoding="utf-8")
    second = taxonomy_version(tmp_path)

    assert first != second
