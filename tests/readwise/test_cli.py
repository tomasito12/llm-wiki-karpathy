"""Tests for Readwise CLI."""

from __future__ import annotations

from pathlib import Path

from src.readwise import cli
from src.readwise.sync import ReadwiseIndexSafetyError


def test_main_missing_token_exits_nonzero(monkeypatch) -> None:
    """Without READWISE_TOKEN the CLI exits with code 1."""
    monkeypatch.delenv("READWISE_TOKEN", raising=False)
    monkeypatch.delenv("READWISE_API_TOKEN", raising=False)
    monkeypatch.setattr(cli, "load_dotenv_from_repo", lambda: None)
    assert cli.main([]) == 1


def test_main_dispatches_run_sync(monkeypatch, tmp_path: Path) -> None:
    """With token set, main runs sync and prints summary."""

    class _Result:
        examined = 2
        exported = 1
        skipped = 1
        dry_run = False
        incremental_filter_active = True
        incremental_watermark = "2024-01-01T00:00:00+00:00"

    monkeypatch.setenv("READWISE_TOKEN", "fake-token")
    monkeypatch.setattr(cli, "load_dotenv_from_repo", lambda: None)

    def _fake_run_sync(_token: str, **_kwargs: object) -> object:
        return _Result()

    monkeypatch.setattr("src.readwise.cli.run_sync", _fake_run_sync)
    assert cli.main(["--index", str(tmp_path / "i.json"), "--no-dedupe"]) == 0


def test_main_uses_configured_output_dir(monkeypatch, tmp_path: Path) -> None:
    """Readwise sync should write to configured raw_dir by default."""
    knowledge = tmp_path / "knowledge"
    raw_dir = knowledge / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
""".strip(),
        encoding="utf-8",
    )
    seen: dict[str, object] = {}

    class _Result:
        examined = 0
        exported = 0
        skipped = 0
        dry_run = True
        incremental_filter_active = False
        incremental_watermark = None

    monkeypatch.setenv("READWISE_TOKEN", "fake-token")
    monkeypatch.setattr(cli, "load_dotenv_from_repo", lambda: None)

    def _fake_run_sync(_token: str, **kwargs: object) -> object:
        seen.update(kwargs)
        return _Result()

    monkeypatch.setattr("src.readwise.cli.run_sync", _fake_run_sync)
    assert cli.main(["--paths-config", str(config_path), "--dry-run"]) == 0
    assert seen["output_dir"] == raw_dir.resolve()
    assert seen["index_path"] == (knowledge / "state" / "readwise_library.json").resolve()


def test_build_parser_dry_run_flag() -> None:
    """Dry-run flag is accepted by the parser."""
    parser = cli.build_parser()
    args = parser.parse_args(["--dry-run"])
    assert args.dry_run is True


def test_build_parser_reset_watermark_flag() -> None:
    """Reset-watermark flag is accepted by the parser."""
    parser = cli.build_parser()
    args = parser.parse_args(["--reset-watermark"])
    assert args.reset_watermark is True


def test_build_parser_allow_index_bootstrap_flag() -> None:
    """Explicit index bootstrap override is accepted by the parser."""
    parser = cli.build_parser()
    args = parser.parse_args(["--allow-index-bootstrap"])
    assert args.allow_index_bootstrap is True


def test_main_reports_index_safety_error(monkeypatch, tmp_path: Path, capsys) -> None:
    """The CLI should turn index bootstrap safety failures into exit code 2."""
    monkeypatch.setenv("READWISE_TOKEN", "fake-token")
    monkeypatch.setattr(cli, "load_dotenv_from_repo", lambda: None)

    def _fake_run_sync(_token: str, **_kwargs: object) -> object:
        raise ReadwiseIndexSafetyError("unsafe index bootstrap")

    monkeypatch.setattr("src.readwise.cli.run_sync", _fake_run_sync)

    assert cli.main(["--index", str(tmp_path / "i.json")]) == 2
    assert "unsafe index bootstrap" in capsys.readouterr().err


def test_main_prints_incremental_hint_when_zero_examined(monkeypatch, capsys) -> None:
    """Stderr notes empty API result when watermark yields zero documents."""

    class _Result:
        examined = 0
        exported = 0
        skipped = 0
        dry_run = False
        incremental_filter_active = True
        incremental_watermark = "2024-01-01T00:00:00+00:00"

    monkeypatch.setenv("READWISE_TOKEN", "fake-token")
    monkeypatch.setattr(cli, "load_dotenv_from_repo", lambda: None)
    monkeypatch.setattr("src.readwise.cli.run_sync", lambda *a, **k: _Result())
    assert cli.main(["--no-dedupe"]) == 0
    err = capsys.readouterr().err
    assert "Reader API" in err
    assert "watermark" in err


def test_load_dotenv_from_repo_passes_repo_dotenv_path(monkeypatch, tmp_path: Path) -> None:
    """``load_dotenv_from_repo`` delegates to dotenv with ``{repo}/.env``."""
    seen: dict[str, Path] = {}

    def fake_load_dotenv(path: Path) -> bool:
        seen["path"] = path
        return True

    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr("src.readwise.cli.load_dotenv", fake_load_dotenv)
    cli.load_dotenv_from_repo()
    assert seen["path"] == tmp_path / ".env"
