"""Tests for Brave CDP auto-launch helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.medium_to_readwise.brave_launcher import (
    brave_binary_for_app_name,
    cdp_port_from_url,
    prepare_brave_cdp_session,
    wait_for_cdp,
)


def test_cdp_port_from_url_defaults_to_9222() -> None:
    """CDP URLs without an explicit port use 9222."""
    assert cdp_port_from_url("http://127.0.0.1:9222") == 9222
    assert cdp_port_from_url("http://127.0.0.1") == 9222


def test_cdp_port_from_url_reads_custom_port() -> None:
    """Custom CDP ports are parsed from the URL."""
    assert cdp_port_from_url("http://127.0.0.1:9333") == 9333


def test_brave_binary_for_app_name_resolves_default_brave_path() -> None:
    """The default Brave app name maps to the standard macOS binary path."""
    path = brave_binary_for_app_name("Brave Browser")
    assert path.name == "Brave Browser"
    assert str(path).endswith("Brave Browser.app/Contents/MacOS/Brave Browser")


def test_prepare_brave_cdp_session_skips_when_already_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-launch is skipped when CDP already responds."""
    calls: list[str] = []
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.cdp_reachable",
        lambda *_args, **_kwargs: True,
    )

    def fake_quit(*_args: object, **_kwargs: object) -> None:
        calls.append("quit")

    monkeypatch.setattr("src.medium_to_readwise.brave_launcher.quit_brave_app", fake_quit)

    prepare_brave_cdp_session(
        "http://127.0.0.1:9222",
        launch_brave=True,
        browser_app_name="Brave Browser",
        brave_binary=Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        log=calls.append,
    )

    assert calls == ["Brave CDP already reachable at http://127.0.0.1:9222"]
    assert "quit" not in calls


def test_prepare_brave_cdp_session_relaunches_when_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unreachable CDP triggers quit, launch, and wait before continuing."""
    events: list[str] = []
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.cdp_reachable",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.quit_brave_app",
        lambda *_args, **_kwargs: events.append("quit"),
    )
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.launch_brave_with_cdp",
        lambda *_args, **_kwargs: events.append("launch"),
    )
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.wait_for_cdp",
        lambda *_args, **_kwargs: events.append("wait"),
    )

    prepare_brave_cdp_session(
        "http://127.0.0.1:9222",
        launch_brave=True,
        browser_app_name="Brave Browser",
        brave_binary=Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        log=events.append,
    )

    assert events[:3] == [
        (
            "Brave CDP not reachable at http://127.0.0.1:9222; quitting Brave Browser "
            "and relaunching with --remote-debugging-port=9222"
        ),
        "quit",
        "launch",
    ]
    assert events[-1] == "Brave CDP ready at http://127.0.0.1:9222"


def test_prepare_brave_cdp_session_raises_when_launch_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auto-launch can be disabled to preserve the manual startup workflow."""
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.cdp_reachable",
        lambda *_args, **_kwargs: False,
    )
    with pytest.raises(RuntimeError, match="Quit Brave completely"):
        prepare_brave_cdp_session(
            "http://127.0.0.1:9222",
            launch_brave=False,
            browser_app_name="Brave Browser",
            brave_binary=Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        )


def test_wait_for_cdp_raises_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Startup waits fail clearly when CDP never opens."""
    monkeypatch.setattr(
        "src.medium_to_readwise.brave_launcher.cdp_reachable",
        lambda *_args, **_kwargs: False,
    )
    with pytest.raises(RuntimeError, match="did not become reachable"):
        wait_for_cdp("http://127.0.0.1:9222", timeout_seconds=0.1)
