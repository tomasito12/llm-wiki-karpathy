"""Tests for Readwise shortcut helpers."""

from __future__ import annotations

import pytest

from src.medium_to_readwise.shortcut import (
    build_applescript_shortcut,
    default_shortcut_mode,
    parse_readwise_shortcut,
    playwright_shortcut_expression,
    trigger_system_shortcut,
)


def test_parse_readwise_shortcut_accepts_option_r_alias() -> None:
    """Option+R and Alt+KeyR parse to the same macOS shortcut."""
    assert parse_readwise_shortcut("Option+R") == parse_readwise_shortcut("Alt+KeyR")


def test_playwright_shortcut_expression_maps_alt_to_option_modifier() -> None:
    """Playwright uses Alt for the macOS Option modifier."""
    assert playwright_shortcut_expression("Alt+KeyR") == "Alt+KeyR"


def test_build_applescript_shortcut_activates_brave_and_sends_option_r() -> None:
    """System shortcut delivery uses AppleScript against the Brave app."""
    script = build_applescript_shortcut("Option+R")
    assert 'tell application "Brave Browser" to activate' in script
    assert 'keystroke "r" using {option down}' in script


def test_trigger_system_shortcut_runs_osascript(monkeypatch: pytest.MonkeyPatch) -> None:
    """System shortcut mode shells out to osascript."""
    calls: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> None:
        calls.append(command)
        assert check is True

    monkeypatch.setattr("src.medium_to_readwise.shortcut.subprocess.run", fake_run)
    trigger_system_shortcut("Alt+KeyR")
    assert calls[0][0] == "osascript"
    assert "option down" in calls[0][2]


def test_default_shortcut_mode_is_system_on_macos(monkeypatch: pytest.MonkeyPatch) -> None:
    """macOS defaults to real system keystrokes for extension shortcuts."""
    monkeypatch.setattr("src.medium_to_readwise.shortcut.platform.system", lambda: "Darwin")
    assert default_shortcut_mode() == "system"
