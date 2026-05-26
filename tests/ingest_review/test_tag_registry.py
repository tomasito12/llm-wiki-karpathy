"""Tests for tag taxonomy registry metadata."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.tag_registry import (
    TAG_TAXONOMIES,
    taxonomy_by_id,
    taxonomy_path,
)
from src.ingest_review.tags import default_topic_tags_path


def test_tag_taxonomies_has_nine_entries() -> None:
    assert len(TAG_TAXONOMIES) == 9
    ids = {spec.id for spec in TAG_TAXONOMIES}
    assert ids == {
        "topics",
        "glossary",
        "howto",
        "trends",
        "impl_study",
        "tool_tags",
        "model_tags",
        "tool_types",
        "model_types",
    }


def test_taxonomy_by_id_resolves_topics() -> None:
    spec = taxonomy_by_id("topics")
    assert spec is not None
    assert spec.label == "Topics & insights"


def test_taxonomy_path_under_config(tmp_path: Path) -> None:
    spec = taxonomy_by_id("topics")
    assert spec is not None
    path = taxonomy_path(spec, tmp_path)
    assert path == default_topic_tags_path(tmp_path)
    assert path.name == "review_tags_topics.yaml"
    assert path.parent.name == "config"
