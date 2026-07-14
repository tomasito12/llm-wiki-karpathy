"""Tests for vault Git strategy CLI integration."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops import status_cli


def test_status_cli_vault_git_json_output_is_valid_json(tmp_path: Path, capsys) -> None:
    """The CLI should print valid vault Git strategy JSON with --vault-git-json."""
    vault_root, wiki_dir, config_path, repo_root = _bootstrap_vault_fixture(tmp_path)

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--vault-git-json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert payload["recommendations"]["use_plain_git"] is True
    assert payload["recommendations"]["ready_for_git_init"] is True


def test_status_cli_vault_git_strategy_appends_readable_section(tmp_path: Path, capsys) -> None:
    """The CLI should append a vault Git strategy section when requested."""
    vault_root, wiki_dir, config_path, repo_root = _bootstrap_vault_fixture(tmp_path)

    exit_code = status_cli.main(
        [
            "--repo-root",
            str(repo_root),
            "--paths-config",
            str(config_path),
            "--vault-git-strategy",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured
    assert "Private Vault Git Strategy" in captured
    assert "ready for git init: yes" in captured


def _bootstrap_vault_fixture(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path]:
    """Create a minimal external vault fixture with aligned source access."""
    repo_root = tmp_path / "repo"
    knowledge_root = tmp_path / "knowledge"
    vault_root = tmp_path / "vault"
    wiki_dir = vault_root / "wiki"
    raw_dir = knowledge_root / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source-a.md").write_text("raw body", encoding="utf-8")
    (wiki_dir / "sources").mkdir(parents=True)
    (wiki_dir / "sources" / "source-a.md").write_text(
        """---
source_id: source-a
source_text_available: true
---

# Source A

## Full source text

raw body
""",
        encoding="utf-8",
    )
    graph_path = knowledge_root / "state" / "wiki_render_graph.json"
    graph_path.parent.mkdir(parents=True)
    graph_path.write_text(
        json.dumps({"sources": [{"source_id": "source-a"}]}),
        encoding="utf-8",
    )
    config_path = tmp_path / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge_root}"
vault_root = "{vault_root}"
raw_dir = "{raw_dir}"
reviews_dir = "{knowledge_root}/state/reviews"
graph_path = "{graph_path}"
manifest_path = "{knowledge_root}/state/wiki_render_manifest.json"
wiki_dir = "{wiki_dir}"
""".strip(),
        encoding="utf-8",
    )
    (knowledge_root / "state" / "reviews").mkdir(parents=True)
    (repo_root / "wiki").mkdir(parents=True)
    return vault_root, wiki_dir, config_path, repo_root
