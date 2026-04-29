"""Authentication helpers for Medium requests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; llm-wiki-pipeline/0.1; +https://example.local)"


@dataclass(frozen=True)
class MediumAuthConfig:
    """Authentication material used for Medium HTTP requests."""

    cookie: str | None = None
    cookie_file: Path | None = None
    storage_state: Path | None = None


def build_medium_headers(auth: MediumAuthConfig | None = None) -> dict[str, str]:
    """Build Medium request headers with optional authenticated cookie."""
    headers = {"User-Agent": USER_AGENT}
    cookie = _resolve_cookie(auth)
    if cookie:
        headers["Cookie"] = cookie
    return headers


def _resolve_cookie(auth: MediumAuthConfig | None) -> str | None:
    """Resolve cookie from direct value, file, or Playwright storage state."""
    if auth is None:
        return None
    if auth.cookie:
        return auth.cookie.strip() or None
    if auth.cookie_file is not None and auth.cookie_file.exists():
        content = auth.cookie_file.read_text(encoding="utf-8").strip()
        if content:
            return content
    if auth.storage_state is not None and auth.storage_state.exists():
        return _cookie_from_storage_state(auth.storage_state)
    return None


def _cookie_from_storage_state(storage_state: Path) -> str | None:
    """Extract a Cookie header value from Playwright storage state JSON."""
    payload = json.loads(storage_state.read_text(encoding="utf-8"))
    raw_cookies = payload.get("cookies", [])
    if not isinstance(raw_cookies, list):
        return None
    pairs: list[str] = []
    for item in raw_cookies:
        if not isinstance(item, dict):
            continue
        domain = str(item.get("domain", ""))
        if "medium.com" not in domain:
            continue
        name = str(item.get("name", "")).strip()
        value = str(item.get("value", "")).strip()
        if name and value:
            pairs.append(f"{name}={value}")
    if not pairs:
        return None
    return "; ".join(pairs)
