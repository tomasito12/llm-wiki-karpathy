"""Tests for wiki-vault-cleanup CLI."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import vault_cleanup_cli


def test_vault_cleanup_cli_yes_without_after_release_fails(
    tmp_path: Path,
    monkeypatch,
    caplog,
) -> None:
    """Real cleanup without a release id should fail closed."""
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(vault_cleanup_cli, "repo_root", lambda: repo)

    exit_code = vault_cleanup_cli.main(["--yes"])

    assert exit_code == 2
    assert "after-release" in caplog.text.lower()


def test_vault_cleanup_cli_dry_run_prints_candidates(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """Default dry-run should print vault cleanup candidates."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    vault = tmp_path / "vault"
    wiki = vault / "wiki"
    repo.mkdir()
    wiki.mkdir(parents=True)
    manifest = knowledge / "state" / "wiki_render_manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"files": []}), encoding="utf-8")
    stale = wiki / "topics" / "stale.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("# stale\n", encoding="utf-8")
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
vault_root = "{vault}"
wiki_dir = "{wiki}"
manifest_path = "{manifest}"
reviews_dir = "{knowledge / 'state' / 'reviews'}"
raw_dir = "{knowledge / 'raw' / 'readwise'}"
synthesis_dir = "{knowledge / 'state' / 'synthesis'}"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(vault_cleanup_cli, "repo_root", lambda: repo)

    exit_code = vault_cleanup_cli.main(["--paths-config", str(config_path), "--dry-run"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "topics/stale.md" in output
    assert "Vault Cleanup Dry Run" in output
