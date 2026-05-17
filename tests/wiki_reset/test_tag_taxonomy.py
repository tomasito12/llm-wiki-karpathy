"""Tests for review tag taxonomy baseline reset."""

from __future__ import annotations

from pathlib import Path

import yaml

from src.ingest_review.tags import default_topic_tags_path, load_tag_list
from src.wiki_reset.reset import run_wiki_reset
from src.wiki_reset.tag_taxonomy import (
    baseline_tag_taxonomy,
    reset_tag_taxonomy,
    tag_taxonomy_differs_from_baseline,
    write_tag_taxonomy_file,
)


def test_reset_tag_taxonomy_writes_baseline_seeds(tmp_path: Path) -> None:
    """Reset overwrites allowlists with minimal starter tags."""
    path = default_topic_tags_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_tag_taxonomy_file(path, ["custom-tag", "another-tag"], comment="old")

    written = reset_tag_taxonomy(tmp_path)
    assert "config/review_tags_topics.yaml" in written

    loaded = load_tag_list(path)
    assert loaded == baseline_tag_taxonomy(tmp_path)[path]


def test_tag_taxonomy_differs_from_baseline_detects_drift(tmp_path: Path) -> None:
    reset_tag_taxonomy(tmp_path)
    assert tag_taxonomy_differs_from_baseline(tmp_path) is False

    path = default_topic_tags_path(tmp_path)
    write_tag_taxonomy_file(path, ["extra-tag"], comment="x")
    assert tag_taxonomy_differs_from_baseline(tmp_path) is True


def test_run_wiki_reset_resets_tag_taxonomy_by_default(tmp_path: Path) -> None:
    """Full wiki reset resets config allowlists when config_root is set."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    topic_path = default_topic_tags_path(tmp_path)
    topic_path.parent.mkdir(parents=True, exist_ok=True)
    topic_path.write_text(
        yaml.dump({"tags": ["drift-a", "drift-b"]}, default_flow_style=False),
        encoding="utf-8",
    )

    _deleted, state_results = run_wiki_reset(
        wiki,
        tmp_path / "lib.json",
        manifest_path=tmp_path / "manifest.json",
        reviews_root=tmp_path / "reviews",
        feedback_db_path=tmp_path / "fb.sqlite",
        config_root=tmp_path,
    )
    assert state_results["tag_taxonomy"] is True
    assert load_tag_list(topic_path) == baseline_tag_taxonomy(tmp_path)[topic_path]


def test_run_wiki_reset_keep_tag_taxonomy_skips_config(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    topic_path = default_topic_tags_path(tmp_path)
    topic_path.parent.mkdir(parents=True, exist_ok=True)
    topic_path.write_text(
        yaml.dump({"tags": ["only-custom"]}, default_flow_style=False),
        encoding="utf-8",
    )

    _deleted, state_results = run_wiki_reset(
        wiki,
        tmp_path / "lib.json",
        manifest_path=tmp_path / "manifest.json",
        reviews_root=tmp_path / "reviews",
        feedback_db_path=tmp_path / "fb.sqlite",
        reset_tag_taxonomy_config=False,
        config_root=tmp_path,
    )
    assert state_results["tag_taxonomy"] is False
    assert load_tag_list(topic_path) == ["only-custom"]
