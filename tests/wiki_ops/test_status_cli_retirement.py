"""CLI tests for old repo data retirement in wiki-ops-status."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from src.wiki_ops import status_cli


def test_status_cli_retirement_json_prints_only_json(tmp_path: Path, capsys) -> None:
    """Retirement JSON mode should print only machine-readable JSON."""
    repo = _init_git_repo(
        tmp_path,
        {
            "src/app.py": "ok\n",
            "wiki/page.md": "page\n",
        },
    )

    exit_code = status_cli.main(["--repo-root", str(repo), "--retirement-json"])
    captured = capsys.readouterr().out
    payload = json.loads(captured)

    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert "files" in payload
    assert "Wiki Ops Status" not in captured


def test_status_cli_retirement_plan_appends_readable_section(tmp_path: Path, capsys) -> None:
    """Retirement plan mode should append a readable section to status output."""
    repo = _init_git_repo(
        tmp_path,
        {
            "src/app.py": "ok\n",
            "wiki/page.md": "page\n",
        },
    )

    exit_code = status_cli.main(["--repo-root", str(repo), "--retirement-plan"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "Wiki Ops Status" in captured
    assert "Old Repo Data Retirement" in captured
    assert "readiness:" in captured


def test_status_cli_retirement_plan_performs_no_writes(monkeypatch, tmp_path: Path) -> None:
    """Retirement planning must not create directories during CLI execution."""
    repo = _init_git_repo(tmp_path, {"src/app.py": "ok\n"})
    mkdir_calls: list[Path] = []

    def _track_mkdir(self: Path, *args, **kwargs) -> None:
        mkdir_calls.append(self)
        raise AssertionError("unexpected mkdir")

    monkeypatch.setattr(Path, "mkdir", _track_mkdir, raising=False)
    status_cli.main(["--repo-root", str(repo), "--retirement-json"])

    assert mkdir_calls == []


def _init_git_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Initialize a Git repository with tracked files for CLI tests."""
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, env=env)
    for rel_path, content in files.items():
        target = repo / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, env=env)
    subprocess.run(
        ["git", "commit", "-m", "test"],
        cwd=repo,
        check=True,
        capture_output=True,
        env=env,
    )
    return repo
