"""Tests for Readwise dedupe CLI path configuration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from src.readwise import dedupe_cli


def test_dedupe_cli_uses_configured_raw_dir(tmp_path: Path) -> None:
    """Dedupe should scan the configured external raw directory by default."""
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

    with patch.object(dedupe_cli, "run_readwise_dedupe", return_value=0) as mock_run:
        code = dedupe_cli.main(["--paths-config", str(config_path), "--dry-run"])

    assert code == 0
    assert mock_run.call_args.kwargs["raw_dir"] == raw_dir.resolve()


def test_dedupe_cli_explicit_raw_dir_overrides_config(tmp_path: Path) -> None:
    """Explicit --raw-dir should override configured defaults."""
    knowledge = tmp_path / "knowledge"
    override_raw = tmp_path / "override-raw"
    override_raw.mkdir()
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
""".strip(),
        encoding="utf-8",
    )

    with patch.object(dedupe_cli, "run_readwise_dedupe", return_value=0) as mock_run:
        code = dedupe_cli.main(
            [
                "--paths-config",
                str(config_path),
                "--raw-dir",
                str(override_raw),
                "--dry-run",
            ]
        )

    assert code == 0
    assert mock_run.call_args.kwargs["raw_dir"] == override_raw.resolve()


def test_dedupe_cli_missing_paths_config_exits_two(tmp_path: Path) -> None:
    """Invalid --paths-config should exit with code 2."""
    code = dedupe_cli.main(["--paths-config", str(tmp_path / "missing.toml"), "--dry-run"])
    assert code == 2
