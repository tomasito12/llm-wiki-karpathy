"""Tests for the Medium to Readwise CLI helpers."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

import pytest

from src.medium_to_readwise import cli
from src.medium_to_readwise.state import save_article_state


def test_default_reading_list_url_uses_env_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """The Reading List default can be configured through MEDIUM_READING_LIST_URL."""
    monkeypatch.setenv(
        "MEDIUM_READING_LIST_URL",
        "https://medium.com/@plischke81/list/reading-list",
    )
    assert cli.default_reading_list_url() == "https://medium.com/@plischke81/list/reading-list"


def test_build_parser_sets_expected_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """The CLI defaults target the local Brave CDP endpoint and Medium list."""
    monkeypatch.delenv("MEDIUM_READING_LIST_URL", raising=False)
    monkeypatch.delenv("READWISE_SAVE_SHORTCUT", raising=False)
    monkeypatch.delenv("READWISE_SHORTCUT_MODE", raising=False)
    monkeypatch.delenv("MEDIUM_DELAY_JITTER", raising=False)
    monkeypatch.delenv("MEDIUM_BETWEEN_ARTICLES_DELAY", raising=False)
    monkeypatch.delenv("MEDIUM_MAX_PER_HOUR", raising=False)
    monkeypatch.setattr(cli, "default_shortcut_mode", lambda: "system")
    args = cli.build_parser().parse_args([])
    assert args.cdp_url == "http://127.0.0.1:9222"
    assert args.reading_list_url == cli.FALLBACK_READING_LIST_URL
    assert args.delay == 3.0
    assert args.retry_failed is True
    assert args.readwise_shortcut == "Alt+KeyR"
    assert args.shortcut_mode == "system"
    assert args.remove_from_list is True
    assert args.readwise_confirm_timeout == 15.0
    assert args.jitter == 3.0
    assert args.between_articles == 8.0
    assert args.max_per_hour == 20


def test_limited_urls_applies_positive_limit() -> None:
    """Limit mode selects only the requested number of URLs."""
    assert cli.limited_urls(["a", "b", "c"], 2) == ["a", "b"]


def test_limited_urls_rejects_negative_limit() -> None:
    """Negative limits are treated as invalid user input."""
    with pytest.raises(ValueError, match="--limit"):
        cli.limited_urls(["a"], -1)


def test_collect_urls_if_needed_uses_cache_when_available(tmp_path: Path) -> None:
    """Cached article URLs are reused unless refresh is requested."""
    save_article_state(
        tmp_path,
        reading_list_url="https://medium.com/list/reading-list",
        urls=["https://medium.com/@a/one-abc12345"],
    )
    args = argparse.Namespace(
        state_dir=tmp_path,
        refresh_articles=False,
        dry_run=False,
        collect_only=False,
        reading_list_url="https://medium.com/list/reading-list",
        scroll_delay=0,
    )
    urls = asyncio.run(cli.collect_urls_if_needed(args, object()))
    assert urls == ["https://medium.com/@a/one-abc12345"]


def test_collect_urls_if_needed_refresh_replaces_cached_urls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Refreshing replaces the cached list instead of keeping stale navigation links."""
    save_article_state(
        tmp_path,
        reading_list_url="https://medium.com/list/reading-list",
        urls=["https://medium.com/@plischke81", "https://medium.com/@a/one-abc12345"],
    )

    async def fake_collect(*_args: Any, **_kwargs: Any) -> list[str]:
        """Return one new URL without opening a browser."""
        return ["https://medium.com/@b/two-def67890"]

    monkeypatch.setattr(cli, "collect_reading_list_urls", fake_collect)
    args = argparse.Namespace(
        state_dir=tmp_path,
        refresh_articles=True,
        dry_run=False,
        collect_only=False,
        reading_list_url="https://medium.com/list/reading-list",
        scroll_delay=0,
    )
    urls = asyncio.run(cli.collect_urls_if_needed(args, object()))
    assert urls == ["https://medium.com/@b/two-def67890"]


def test_collect_urls_if_needed_load_filters_stale_cache_without_refresh(
    tmp_path: Path,
) -> None:
    """Loading cached state strips invalid URLs even without a new harvest."""
    save_article_state(
        tmp_path,
        reading_list_url="https://medium.com/list/reading-list",
        urls=["https://medium.com/@plischke81", "https://medium.com/@a/one-abc12345"],
    )
    args = argparse.Namespace(
        state_dir=tmp_path,
        refresh_articles=False,
        dry_run=False,
        collect_only=False,
        reading_list_url="https://medium.com/list/reading-list",
        scroll_delay=0,
    )
    urls = asyncio.run(cli.collect_urls_if_needed(args, object()))
    assert urls == ["https://medium.com/@a/one-abc12345"]
