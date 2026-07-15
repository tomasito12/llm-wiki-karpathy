"""Tests for wiki-lint CLI path handling."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_lint import cli


def _write_valid_wiki(wiki: Path) -> None:
    """Write a minimal valid generated wiki fixture."""
    source = wiki / "sources" / "source-a.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        """---
title: Source A
category: source
source_id: source-a
tags:
  - ai-engineering
---

# Source A

## Key insights

None.

## Derived knowledge pages

None.

## Why it matters

It matters.

## Limitations / open questions

None.

## Contradictions / unverified claims

None.

## Source metadata

None.

## Full source text

Raw body.
""",
        encoding="utf-8",
    )


def test_wiki_lint_accepts_paths_config(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """``--paths-config`` should route linting to the configured wiki_dir."""
    repo = tmp_path / "repo"
    vault = tmp_path / "vault"
    wiki = vault / "wiki"
    repo.mkdir()
    _write_valid_wiki(wiki)
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
vault_root = "{vault}"
wiki_dir = "{wiki}"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "_repo_root", lambda: repo)

    exit_code = cli.main(["--paths-config", str(config_path), "--skip-hygiene"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "contract ok" in output


def test_wiki_lint_explicit_wiki_dir_overrides_paths_config(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """Explicit ``--wiki-dir`` should win over the path config default."""
    repo = tmp_path / "repo"
    configured_vault = tmp_path / "configured-vault"
    configured_wiki = configured_vault / "wiki"
    explicit_wiki = tmp_path / "explicit-wiki"
    repo.mkdir()
    _write_valid_wiki(explicit_wiki)
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
vault_root = "{configured_vault}"
wiki_dir = "{configured_wiki}"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "_repo_root", lambda: repo)

    exit_code = cli.main(
        [
            "--paths-config",
            str(config_path),
            "--wiki-dir",
            str(explicit_wiki),
            "--skip-hygiene",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "contract ok" in output


def test_wiki_lint_skip_hygiene_only_runs_contract_checks(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """``--skip-hygiene`` should omit manifest orphan reporting."""
    repo = tmp_path / "repo"
    wiki = tmp_path / "wiki"
    repo.mkdir()
    _write_valid_wiki(wiki)
    monkeypatch.setattr(cli, "_repo_root", lambda: repo)

    exit_code = cli.main(["--wiki-dir", str(wiki), "--skip-hygiene"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "contract ok" in output
    assert "Vault Hygiene" not in output


def test_wiki_lint_hygiene_only_reports_orphans(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    """``--hygiene-only`` should report stale managed orphans."""
    repo = tmp_path / "repo"
    wiki = tmp_path / "wiki"
    repo.mkdir()
    wiki.mkdir()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"files": [{"path": "topics/current.md", "sha256": "abc"}]}),
        encoding="utf-8",
    )
    (wiki / "topics").mkdir(parents=True)
    (wiki / "topics" / "current.md").write_text("# current\n", encoding="utf-8")
    (wiki / "topics" / "stale.md").write_text("# stale\n", encoding="utf-8")
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
vault_root = "{tmp_path / "vault"}"
wiki_dir = "{wiki}"
manifest_path = "{manifest}"
reviews_dir = "{tmp_path / "reviews"}"
raw_dir = "{tmp_path / "raw"}"
synthesis_dir = "{tmp_path / "synthesis"}"
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "_repo_root", lambda: repo)

    exit_code = cli.main(["--paths-config", str(config_path), "--hygiene-only"])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "safe delete candidates: 1" in output
    assert "topics/stale.md" in output


def test_wiki_lint_missing_paths_config_returns_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Missing explicit path config files should fail with exit code 2."""
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(cli, "_repo_root", lambda: repo)

    exit_code = cli.main(["--paths-config", str(tmp_path / "missing.toml")])

    assert exit_code == 2
