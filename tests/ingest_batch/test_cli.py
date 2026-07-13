"""Tests for the ingest pre-analysis CLI."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from src.ingest_batch import cli
from src.ingest_batch.preanalyze import PreanalyzeResult
from src.wiki_paths.config import default_wiki_paths


def _write_paths_config(
    tmp_path: Path,
    *,
    repo_root: Path,
    knowledge_root: Path,
) -> Path:
    """Write a minimal external knowledge config file."""
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge_root}"
""".strip(),
        encoding="utf-8",
    )
    (repo_root / "config").mkdir(parents=True, exist_ok=True)
    return config_path


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
    assert args.between_articles == 0.0


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
    assert calls[0]["between_articles_seconds"] == 0.0


def test_main_passes_between_articles_delay(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """The CLI forwards between-article pacing to the pre-analysis runner."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    calls: list[dict[str, object]] = []
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: tmp_path)

    def fake_run(**kwargs: object) -> PreanalyzeResult:
        calls.append(kwargs)
        return PreanalyzeResult(selected=0)

    monkeypatch.setattr(cli, "preanalyze_pending_with_repo_defaults", fake_run)

    code = cli.main(
        [
            "--raw-dir",
            str(raw_dir),
            "--reviews-dir",
            str(tmp_path / "reviews"),
            "--between-articles",
            "600",
        ]
    )

    assert code == 0
    assert calls[0]["between_articles_seconds"] == 600.0


def test_main_uses_configured_paths_without_explicit_flags(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """Without explicit path flags the CLI should use configured external paths."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    raw_dir = knowledge / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    repo.mkdir()
    config_path = _write_paths_config(tmp_path, repo_root=repo, knowledge_root=knowledge)
    calls: list[dict[str, object]] = []
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: repo)

    def fake_run(**kwargs: object) -> PreanalyzeResult:
        calls.append(kwargs)
        return PreanalyzeResult(selected=0)

    monkeypatch.setattr(cli, "preanalyze_pending_with_repo_defaults", fake_run)

    code = cli.main(["--paths-config", str(config_path)])

    assert code == 0
    assert calls[0]["raw_dir"] == raw_dir.resolve()
    assert calls[0]["reviews_root"] == (knowledge / "state" / "reviews").resolve()


def test_main_explicit_path_overrides_paths_config(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """Explicit CLI path flags should override configured defaults."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    override_raw = tmp_path / "override-raw"
    override_raw.mkdir()
    repo.mkdir()
    knowledge.mkdir()
    config_path = _write_paths_config(tmp_path, repo_root=repo, knowledge_root=knowledge)
    calls: list[dict[str, object]] = []
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: repo)

    def fake_run(**kwargs: object) -> PreanalyzeResult:
        calls.append(kwargs)
        return PreanalyzeResult(selected=0)

    monkeypatch.setattr(cli, "preanalyze_pending_with_repo_defaults", fake_run)

    code = cli.main(
        [
            "--paths-config",
            str(config_path),
            "--raw-dir",
            str(override_raw),
        ]
    )

    assert code == 0
    assert calls[0]["raw_dir"] == override_raw.resolve()


def test_main_without_config_keeps_repo_local_defaults(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """Without a config file the CLI should keep repo-local defaults."""
    repo = tmp_path / "repo"
    raw_dir = repo / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    calls: list[dict[str, object]] = []
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: repo)
    monkeypatch.setattr(cli, "load_paths_for_cli", lambda _args: default_wiki_paths(repo))

    def fake_run(**kwargs: object) -> PreanalyzeResult:
        calls.append(kwargs)
        return PreanalyzeResult(selected=0)

    monkeypatch.setattr(cli, "preanalyze_pending_with_repo_defaults", fake_run)

    code = cli.main([])

    defaults = default_wiki_paths(repo)
    assert code == 0
    assert calls[0]["raw_dir"] == defaults.raw_dir.resolve()
    assert calls[0]["reviews_root"] == defaults.reviews_dir.resolve()


def test_main_missing_paths_config_exits_two(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """An invalid --paths-config path should exit with code 2."""
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(cli, "load_repo_dotenv", lambda: repo)

    code = cli.main(["--paths-config", str(tmp_path / "missing.toml")])

    assert code == 2
