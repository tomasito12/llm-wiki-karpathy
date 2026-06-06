"""Tests for shared wiki contract definitions."""

from __future__ import annotations

from src.wiki_contract.categories import (
    CATEGORY_BY_FRONTMATTER,
    DERIVED_KEY_BY_GRAPH_CATEGORY,
    FRONTMATTER_CATEGORY_BY_GRAPH,
    derived_key_for_graph_category,
)
from src.wiki_contract.frontmatter import required_fields_for
from src.wiki_contract.headings import SOURCE_H2_HEADINGS, required_h2_headings_for
from src.wiki_contract.layout import MANAGED_FOLDERS, is_preserved_wiki_path


def test_managed_folders_include_generated_layout() -> None:
    """Managed folders cover all generated top-level directories."""
    assert "sources" in MANAGED_FOLDERS
    assert "indexes" in MANAGED_FOLDERS
    assert "notes" not in MANAGED_FOLDERS


def test_preserved_paths_cover_operator_areas() -> None:
    """Notes, legacy, and hub files survive reset."""
    assert is_preserved_wiki_path("AGENTS.md")
    assert is_preserved_wiki_path("notes/scratch.md")
    assert is_preserved_wiki_path("legacy/manual-ingest/README.md")
    assert not is_preserved_wiki_path("topics/foo.md")


def test_frontmatter_and_graph_categories_align() -> None:
    """Every graph category maps to a frontmatter category label."""
    assert FRONTMATTER_CATEGORY_BY_GRAPH["topic"] == "topic"
    assert FRONTMATTER_CATEGORY_BY_GRAPH["trend"] == "industry-trend"
    assert CATEGORY_BY_FRONTMATTER["implementation-study"].graph_category == "impl_study"


def test_derived_keys_exist_for_merge_and_evidence_categories() -> None:
    """Derived frontmatter keys are defined for mergeable and evidence categories."""
    assert derived_key_for_graph_category("topic") == "derived_topics"
    assert derived_key_for_graph_category("signal") == "derived_signals"
    assert "derived_implementation_studies" in DERIVED_KEY_BY_GRAPH_CATEGORY.values()


def test_required_fields_and_headings_defined_for_source() -> None:
    """Source contract fields match render/lint expectations."""
    assert "source_id" in required_fields_for("source")
    assert required_h2_headings_for("source") == SOURCE_H2_HEADINGS
