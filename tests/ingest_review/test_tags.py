"""Tests for tag YAML loaders."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.tags import load_tag_list


def test_load_tag_list_accepts_bare_list(tmp_path: Path) -> None:
    """YAML list at root is loaded as strings."""
    p = tmp_path / "t.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")
    assert load_tag_list(p) == ["a", "b"]


def test_load_tag_list_accepts_tags_key(tmp_path: Path) -> None:
    """YAML object with ``tags`` key is supported."""
    p = tmp_path / "t.yaml"
    p.write_text("tags: [x, y]\n", encoding="utf-8")
    assert load_tag_list(p) == ["x", "y"]


def test_load_tag_list_missing_returns_empty(tmp_path: Path) -> None:
    """Missing file yields empty list."""
    assert load_tag_list(tmp_path / "nope.yaml") == []
