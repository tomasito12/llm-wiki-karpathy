"""Readwise save shortcut helpers for Playwright and macOS system input."""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass

DEFAULT_READWISE_SHORTCUT = "Alt+KeyR"
DEFAULT_BROWSER_APP_NAME = "Brave Browser"


@dataclass(frozen=True)
class ParsedShortcut:
    """Normalized shortcut modifiers and key."""

    modifiers: tuple[str, ...]
    key: str


def default_shortcut_mode() -> str:
    """Return the default shortcut delivery mode for the current platform."""
    return "system" if platform.system() == "Darwin" else "playwright"


def parse_readwise_shortcut(shortcut: str) -> ParsedShortcut:
    """Parse a shortcut such as ``Alt+KeyR`` or ``Option+R``."""
    tokens = [token.strip() for token in shortcut.replace("-", "+").split("+") if token.strip()]
    if not tokens:
        raise ValueError("Shortcut must include at least one key")

    modifiers: list[str] = []
    key: str | None = None
    for token in tokens:
        normalized = token.lower()
        if normalized in {"alt", "option", "opt"}:
            modifiers.append("alt")
        elif normalized in {"meta", "cmd", "command"}:
            modifiers.append("meta")
        elif normalized in {"ctrl", "control"}:
            modifiers.append("control")
        elif normalized in {"shift"}:
            modifiers.append("shift")
        elif normalized.startswith("key") and len(normalized) > 3:
            key = normalized[3:]
        else:
            key = normalized

    if key is None:
        raise ValueError(f"Shortcut is missing a key: {shortcut}")
    return ParsedShortcut(modifiers=tuple(modifiers), key=key)


def playwright_shortcut_expression(shortcut: str) -> str:
    """Return the Playwright ``keyboard.press`` expression for ``shortcut``."""
    parsed = parse_readwise_shortcut(shortcut)
    if not parsed.modifiers:
        return parsed.key
    modifier_expr = "+".join(
        "Alt" if modifier == "alt" else modifier.capitalize() for modifier in parsed.modifiers
    )
    key_expr = parsed.key if parsed.key.startswith("Key") else f"Key{parsed.key.upper()}"
    return f"{modifier_expr}+{key_expr}"


def applescript_modifier_clause(modifiers: tuple[str, ...]) -> str:
    """Return an AppleScript modifier clause for ``modifiers``."""
    mapping = {
        "alt": "option down",
        "meta": "command down",
        "control": "control down",
        "shift": "shift down",
    }
    clause = ", ".join(mapping[modifier] for modifier in modifiers)
    return f" using {{{clause}}}" if clause else ""


def build_applescript_shortcut(
    shortcut: str,
    *,
    browser_app_name: str = DEFAULT_BROWSER_APP_NAME,
) -> str:
    """Build AppleScript that activates Brave and sends the configured shortcut."""
    parsed = parse_readwise_shortcut(shortcut)
    modifier_clause = applescript_modifier_clause(parsed.modifiers)
    return (
        f'tell application "{browser_app_name}" to activate\n'
        "delay 0.3\n"
        'tell application "System Events"\n'
        f'  keystroke "{parsed.key}"{modifier_clause}\n'
        "end tell"
    )


def trigger_system_shortcut(
    shortcut: str,
    *,
    browser_app_name: str = DEFAULT_BROWSER_APP_NAME,
) -> None:
    """Send a real macOS keystroke to the browser so extension shortcuts fire."""
    script = build_applescript_shortcut(shortcut, browser_app_name=browser_app_name)
    subprocess.run(  # noqa: S603
        ["osascript", "-e", script],
        check=True,
    )
