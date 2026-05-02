import sys
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from pathlib import Path

from src.pipeline import cli
from src.pipeline.models import DiscoveredItem
from src.pipeline.state_store import SourceStateStore


def test_discover_new_items_applies_limit_after_seen_filter(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "sources_config.json"
    config_path.write_text(
        '{"sources":[{"name":"demo","kind":"medium","url":"https://medium.com/tag/chatbots"}]}',
        encoding="utf-8",
    )
    state_path = tmp_path / "sources_seen.json"
    store = SourceStateStore(state_path)
    store.upsert_item(
        source_name="demo",
        item_id="seen",
        title="Seen title",
        canonical_url="https://medium.com/a",
        published_at=None,
        local_path=None,
        status="parsed",
    )

    in_range_pubdate = format_datetime(datetime.now(tz=UTC) - timedelta(days=3))
    too_new_pubdate = format_datetime(datetime.now(tz=UTC) - timedelta(days=1))

    discovered = [
        DiscoveredItem(
            item_id="seen",
            source_name="demo",
            source_url="https://medium.com/tag/chatbots",
            url="https://medium.com/a",
            title="Seen title",
            published_at=in_range_pubdate,
        ),
        DiscoveredItem(
            item_id="new-1",
            source_name="demo",
            source_url="https://medium.com/tag/chatbots",
            url="https://medium.com/b",
            title="New title",
            published_at=in_range_pubdate,
        ),
        DiscoveredItem(
            item_id="new-too-fresh",
            source_name="demo",
            source_url="https://medium.com/tag/chatbots",
            url="https://medium.com/c",
            title="Too fresh",
            published_at=too_new_pubdate,
        ),
    ]

    monkeypatch.setattr(cli, "DEFAULT_CONFIG", config_path)
    monkeypatch.setattr(cli, "DEFAULT_STATE", state_path)

    def fake_discover_with_options(
        source,
        limit=None,
        use_browser=False,
        max_scrolls=150,
        auth=None,
        archive_window_start_days=None,
        archive_window_end_days=None,
    ):
        return discovered

    monkeypatch.setattr(cli, "discover_medium_items_with_options", fake_discover_with_options)

    result = cli.discover_new_items(
        source_name="demo",
        limit=1,
        window_start_days=5,
        window_end_days=2,
    )
    assert len(result) == 1
    assert result[0].item_id == "new-1"


def test_discover_new_items_forwards_browser_flags(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "sources_config.json"
    config_path.write_text(
        '{"sources":[{"name":"demo","kind":"medium","url":"https://medium.com/tag/chatbots"}]}',
        encoding="utf-8",
    )
    state_path = tmp_path / "sources_seen.json"
    in_range_pubdate = format_datetime(datetime.now(tz=UTC) - timedelta(days=3))
    captured: dict[str, object] = {}

    def fake_discover(
        source,
        limit=None,
        use_browser=False,
        max_scrolls=150,
        auth=None,
        archive_window_start_days=None,
        archive_window_end_days=None,
    ):
        captured["use_browser"] = use_browser
        captured["max_scrolls"] = max_scrolls
        return [
            DiscoveredItem(
                item_id="new-1",
                source_name="demo",
                source_url="https://medium.com/tag/chatbots",
                url="https://medium.com/b",
                title="New title",
                published_at=in_range_pubdate,
            )
        ]

    monkeypatch.setattr(cli, "DEFAULT_CONFIG", config_path)
    monkeypatch.setattr(cli, "DEFAULT_STATE", state_path)
    monkeypatch.setattr(cli, "discover_medium_items_with_options", fake_discover)

    result = cli.discover_new_items(
        source_name="demo",
        limit=1,
        window_start_days=5,
        window_end_days=2,
        use_browser=True,
        max_scrolls=12,
    )
    assert len(result) == 1
    assert captured["use_browser"] is True
    assert captured["max_scrolls"] == 12


def test_is_in_target_window_inclusive_bounds() -> None:
    today = datetime.now(tz=UTC)
    at_start = format_datetime(today - timedelta(days=5))
    at_end = format_datetime(today - timedelta(days=2))
    outside = format_datetime(today - timedelta(days=1))

    assert cli._is_in_target_window(at_start, window_start_days=5, window_end_days=2)
    assert cli._is_in_target_window(at_end, window_start_days=5, window_end_days=2)
    assert not cli._is_in_target_window(outside, window_start_days=5, window_end_days=2)


def test_is_in_target_window_rejects_invalid_window() -> None:
    sample = format_datetime(datetime.now(tz=UTC) - timedelta(days=3))
    try:
        cli._is_in_target_window(sample, window_start_days=1, window_end_days=2)
    except ValueError as exc:
        assert "window_start_days" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid window bounds")


def test_discover_new_items_rejects_non_medium_source(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "sources_config.json"
    config_path.write_text(
        '{"sources":[{"name":"demo","kind":"substack","url":"https://example.com"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "DEFAULT_CONFIG", config_path)
    try:
        cli.discover_new_items(source_name="demo", limit=1)
    except ValueError as exc:
        assert "Unsupported source kind" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-medium source")


def test_build_parser_auth_login_defaults() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["auth-login"])
    assert args.command == "auth-login"
    assert str(args.output).endswith("state/medium.storage_state.json")
    assert args.timeout_seconds == 300


def test_main_dispatches_auth_login(monkeypatch, tmp_path: Path) -> None:
    called: dict[str, object] = {}

    def fake_run_auth_login(output: Path, timeout_seconds: int) -> int:
        called["output"] = output
        called["timeout_seconds"] = timeout_seconds
        return 0

    monkeypatch.setattr(cli, "run_auth_login", fake_run_auth_login)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pipeline",
            "auth-login",
            "--output",
            str(tmp_path / "state.json"),
            "--timeout-seconds",
            "42",
        ],
    )
    assert cli.main() == 0
    assert called["timeout_seconds"] == 42
