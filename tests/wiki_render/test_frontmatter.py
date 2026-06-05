"""Tests for markdown frontmatter rendering."""

from __future__ import annotations

from src.wiki_render.frontmatter import markdown_document


def test_frontmatter_omits_empty_values_and_keeps_order() -> None:
    """Frontmatter is deterministic and excludes empty values."""
    text = markdown_document(
        {
            "title": "Example",
            "empty": "",
            "tags": ["b", "a"],
            "none": None,
        },
        "# Example",
    )

    assert text.startswith("---\ntitle: Example\ntags:")
    assert "empty:" not in text
    assert text.endswith("# Example\n")
