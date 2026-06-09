"""Tests for local Medium to Readwise progress state."""

from __future__ import annotations

from pathlib import Path

from src.medium_to_readwise.state import (
    append_run_log,
    completed_url_keys,
    default_state_dir,
    ensure_state_dir,
    failed_url_keys,
    load_article_state,
    load_json_object,
    load_processed_state,
    merge_article_urls,
    pending_urls,
    processed_entries,
    save_article_state,
    save_processed_entries,
    screenshot_path,
    upsert_processed_entry,
    utc_now_iso,
)


def test_utc_now_iso_returns_zulu_timestamp() -> None:
    """UTC timestamps use the expected compact ISO suffix."""
    assert utc_now_iso().endswith("Z")


def test_default_state_dir_points_to_medium_state() -> None:
    """The default progress directory is under local repository state."""
    assert default_state_dir().as_posix().endswith("state/medium_to_readwise")


def test_ensure_state_dir_creates_screenshots_directory(tmp_path: Path) -> None:
    """State initialization creates the screenshot subdirectory."""
    ensure_state_dir(tmp_path)
    assert (tmp_path / "screenshots").is_dir()


def test_load_json_object_returns_default_when_missing(tmp_path: Path) -> None:
    """Missing JSON files use the supplied default object."""
    assert load_json_object(tmp_path / "missing.json", default={"x": 1}) == {"x": 1}


def test_article_state_roundtrip_merges_and_saves_urls(tmp_path: Path) -> None:
    """Discovered article URLs round-trip through articles.json."""
    urls = merge_article_urls(
        ["https://medium.com/@a/one-abc12345"],
        [
            "https://medium.com/@a/one-abc12345?utm_source=x",
            "https://medium.com/@b/two-def67890",
        ],
    )
    save_article_state(tmp_path, reading_list_url="https://medium.com/list/reading-list", urls=urls)
    state = load_article_state(tmp_path)
    assert state["urls"] == [
        "https://medium.com/@a/one-abc12345",
        "https://medium.com/@b/two-def67890",
    ]


def test_save_article_state_filters_invalid_cached_urls(tmp_path: Path) -> None:
    """Persisted article state never stores profiles or navigation links."""
    save_article_state(
        tmp_path,
        reading_list_url="https://medium.com/@plischke81/list/reading-list",
        urls=[
            "https://medium.com/@plischke81",
            "https://medium.com/@youandyourband/gatori-fishing-in-america-c63152d79ba1",
        ],
    )
    assert load_article_state(tmp_path)["urls"] == [
        "https://medium.com/@youandyourband/gatori-fishing-in-america-c63152d79ba1"
    ]


def test_processed_state_roundtrip_returns_entries(tmp_path: Path) -> None:
    """Processed article entries round-trip through processed.json."""
    entries = [{"url": "https://medium.com/@a/one", "status": "ok"}]
    save_processed_entries(tmp_path, entries)
    assert load_processed_state(tmp_path) == {"entries": entries}
    assert processed_entries(tmp_path) == entries


def test_append_run_log_writes_timestamped_line(tmp_path: Path) -> None:
    """Run logging appends a line with the supplied message."""
    append_run_log(tmp_path, "processed https://medium.com/@a/one")
    assert "processed https://medium.com/@a/one" in (tmp_path / "run.log").read_text()


def test_completed_and_failed_url_keys_track_statuses() -> None:
    """Resume helpers separate successful and failed article states."""
    entries = [
        {"canonical_url": "https://medium.com/@a/one?utm_source=x", "status": "ok"},
        {"canonical_url": "https://medium.com/@b/two", "status": "failed"},
    ]
    assert completed_url_keys(entries) == {"https://medium.com/@a/one"}
    assert failed_url_keys(entries) == {"https://medium.com/@b/two"}


def test_pending_urls_skip_completed_and_optionally_failed() -> None:
    """Pending URL filtering supports resume and failed retry behavior."""
    urls = [
        "https://medium.com/@a/one-abc12345",
        "https://medium.com/@b/two-def67890",
        "https://medium.com/@c/three-fedcba98",
    ]
    entries = [
        {"canonical_url": "https://medium.com/@a/one-abc12345", "status": "ok"},
        {"canonical_url": "https://medium.com/@b/two-def67890", "status": "failed"},
    ]
    assert pending_urls(urls, entries) == [
        "https://medium.com/@b/two-def67890",
        "https://medium.com/@c/three-fedcba98",
    ]
    assert pending_urls(urls, entries, retry_failed=False) == [
        "https://medium.com/@c/three-fedcba98"
    ]


def test_upsert_processed_entry_replaces_existing_url() -> None:
    """The latest entry replaces older state for the same canonical URL."""
    entries = [{"canonical_url": "https://medium.com/@a/one", "status": "failed"}]
    updated = upsert_processed_entry(
        entries,
        {"canonical_url": "https://medium.com/@a/one?utm_source=x", "status": "ok"},
    )
    assert updated == [{"canonical_url": "https://medium.com/@a/one?utm_source=x", "status": "ok"}]


def test_screenshot_path_is_filesystem_safe(tmp_path: Path) -> None:
    """Failure screenshot paths are deterministic and safe for local files."""
    path = screenshot_path(tmp_path, url="https://medium.com/@a/one?utm_source=x", timestamp="now")
    assert path == tmp_path / "screenshots" / "medium-com-a-one-now.png"
