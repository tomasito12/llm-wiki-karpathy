from __future__ import annotations

from pathlib import Path

from src.pipeline.auth import MediumAuthConfig, _cookie_from_storage_state, build_medium_headers


def test_build_medium_headers_without_auth_has_user_agent() -> None:
    headers = build_medium_headers()
    assert "User-Agent" in headers
    assert "Cookie" not in headers


def test_build_medium_headers_uses_cookie_file(tmp_path: Path) -> None:
    cookie_file = tmp_path / "medium.cookie"
    cookie_file.write_text("sid=abc123; uid=42", encoding="utf-8")
    headers = build_medium_headers(MediumAuthConfig(cookie_file=cookie_file))
    assert headers["Cookie"] == "sid=abc123; uid=42"


def test_cookie_from_storage_state_filters_non_medium_domains(tmp_path: Path) -> None:
    storage = tmp_path / "state.json"
    storage.write_text(
        (
            '{"cookies": ['
            '{"name":"sid","value":"abc","domain":".medium.com"},'
            '{"name":"foo","value":"bar","domain":".example.com"}'
            "]}"
        ),
        encoding="utf-8",
    )
    cookie = _cookie_from_storage_state(storage)
    assert cookie == "sid=abc"
