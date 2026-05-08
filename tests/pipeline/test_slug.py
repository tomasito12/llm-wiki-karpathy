"""Tests for filesystem slug helpers."""

from __future__ import annotations

from src.pipeline.slug import slugify


def test_slugify_empty_string_returns_document() -> None:
    assert slugify("") == "document"


def test_slugify_whitespace_only_returns_document() -> None:
    assert slugify("   \t\n  ") == "document"


def test_slugify_lowercases_and_replaces_non_alnum() -> None:
    assert slugify("My Test Title!") == "my-test-title"


def test_slugify_strips_leading_trailing_dashes() -> None:
    assert slugify("---hello---") == "hello"


def test_slugify_unicode_non_ascii_removed_or_replaced() -> None:
    assert slugify("café résumé") == "caf-r-sum"


def test_slugify_slashes_become_dashes() -> None:
    assert slugify("foo/bar/baz") == "foo-bar-baz"
