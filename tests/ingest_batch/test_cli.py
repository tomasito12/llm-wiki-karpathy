"""Tests for the ingest pre-analysis CLI."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from src.ingest_batch import cli
from src.ingest_batch.preanalyze import PreanalyzeResult


def test_build_parser_accepts_limit_and_dirs(tmp_path: Path) -> None:
    """CLI parser accepts the key pre-analysis options."""
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "--limit",
            "12",
            "--no-skip-existing",
            "--raw-dir",
            str(tmp_path / "raw"),
            "--reviews-dir",
            str(tmp_path / "reviews"),
            "--wiki-root",
            str(tmp_path / "wiki"),
        ]
    )
    assert args.limit == 12
    assert args.skip_existing is False
    assert args.raw_dir == tmp_path / "raw"


def test_main_returns_error_when_api_key_missing(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """The CLI fails fast before doing work when OPENAI_API_KEY is absent."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: tmp_path)

    code = cli.main(["--raw-dir", str(raw_dir), "--reviews-dir", str(tmp_path / "reviews")])

    assert code == 2


def test_main_runs_preanalysis_with_cli_options(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """The CLI passes parsed options into the pre-analysis runner."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    calls: list[dict[str, object]] = []
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: tmp_path)

    def fake_run(**kwargs: object) -> PreanalyzeResult:
        calls.append(kwargs)
        return PreanalyzeResult(selected=1, processed=["a"])

    monkeypatch.setattr(cli, "preanalyze_pending_with_repo_defaults", fake_run)

    code = cli.main(
        [
            "--limit",
            "3",
            "--raw-dir",
            str(raw_dir),
            "--reviews-dir",
            str(tmp_path / "reviews"),
            "--wiki-root",
            str(tmp_path / "wiki"),
            "--model",
            "test-model",
        ]
    )

    assert code == 0
    assert calls[0]["limit"] == 3
    assert calls[0]["model"] == "test-model"
