"""Tests for ``repo_root`` resolution and repo ``.env`` loading."""

import os
from pathlib import Path

import pytest

from src.ingest_review.paths import load_repo_dotenv, repo_root


def test_repo_root_points_at_repo_layout() -> None:
    """Repository root resolves to the checkout directory."""
    root = repo_root()
    assert (root / "src").is_dir()
    assert (root / "pyproject.toml").is_file()


def test_load_repo_dotenv_reads_repo_env_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Variables from ``<repo>/.env`` are loaded into the environment."""
    key = "DOTENV_INGEST_REVIEW_TEST_VAR"
    monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env").write_text(f"{key}=from_file\n", encoding="utf-8")
    monkeypatch.setattr("src.ingest_review.paths.repo_root", lambda: tmp_path)

    returned = load_repo_dotenv()

    assert returned == tmp_path
    assert os.environ.get(key) == "from_file"
    monkeypatch.delenv(key, raising=False)
