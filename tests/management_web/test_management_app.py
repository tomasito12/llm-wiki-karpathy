"""Tests for the management API CLI entry point."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.management_web import app as management_app


def test_main_loads_repo_dotenv_before_starting_server(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Startup loads ``.env`` so in-process ops see OPENAI_API_KEY."""
    load_calls: list[bool] = []

    def _fake_load_repo_dotenv(*, override: bool = False) -> Path:
        del override
        load_calls.append(True)
        return tmp_path

    monkeypatch.setattr(management_app, "load_repo_dotenv", _fake_load_repo_dotenv)
    monkeypatch.setattr(management_app, "create_app", lambda **_kwargs: object())
    monkeypatch.setattr(management_app.uvicorn, "run", lambda *_args, **_kwargs: None)

    exit_code = management_app.main([])

    assert exit_code == 0
    assert load_calls == [True]
