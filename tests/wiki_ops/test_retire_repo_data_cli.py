"""CLI tests for wiki-retire-repo-data."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from src.wiki_ops import retire_repo_data_cli
from src.wiki_ops.release_verify import ReleaseVerificationReport, VerificationStatus


def test_cli_default_is_dry_run_without_writes(tmp_path: Path, capsys, monkeypatch) -> None:
    """Default invocation should dry-run without modifying Git."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    config_path = _externalize_paths(repo)

    real_run = subprocess.run

    def _wrap(command, *args, **kwargs):
        if len(command) >= 3 and command[:3] == ["git", "rm", "--cached"]:
            raise AssertionError("unexpected git rm --cached")
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", _wrap)

    with _mock_release_verification("ok"):
        exit_code = retire_repo_data_cli.main(
            ["--repo-root", str(repo), "--paths-config", str(config_path)]
        )

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "mode: dry-run" in captured
    assert "No files were untracked." in captured


def test_cli_real_run_requires_yes(tmp_path: Path, caplog) -> None:
    """Explicit dry-run without --yes should preview without executing git rm."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    config_path = _externalize_paths(repo)

    with _mock_release_verification("ok"):
        exit_code = retire_repo_data_cli.main(
            [
                "--repo-root",
                str(repo),
                "--paths-config",
                str(config_path),
                "--dry-run",
            ]
        )

    assert exit_code == 0


def test_cli_dry_run_and_yes_exits_two(tmp_path: Path, caplog) -> None:
    """Combining --dry-run and --yes should fail."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})

    exit_code = retire_repo_data_cli.main(["--repo-root", str(repo), "--dry-run", "--yes"])

    assert exit_code == 2
    assert "Cannot combine --dry-run with --yes" in caplog.text


def test_cli_invalid_chunk_size_exits_two_in_dry_run(tmp_path: Path, caplog) -> None:
    """Invalid chunk sizes should fail cleanly before dry-run planning."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})

    exit_code = retire_repo_data_cli.main(
        ["--repo-root", str(repo), "--dry-run", "--chunk-size", "0"]
    )

    assert exit_code == 2
    assert "--chunk-size must be positive" in caplog.text


def test_cli_json_output_is_valid(tmp_path: Path, capsys) -> None:
    """JSON mode should emit a valid machine-readable report."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    config_path = _externalize_paths(repo)

    with _mock_release_verification("ok"):
        exit_code = retire_repo_data_cli.main(
            ["--repo-root", str(repo), "--paths-config", str(config_path), "--json"]
        )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert payload["mode"] == "dry_run"
    assert "candidates" in payload


def test_cli_real_run_with_yes_untracks_without_deleting_files(tmp_path: Path) -> None:
    """Real execution with --yes should untrack files but keep them on disk."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    config_path = _externalize_paths(repo)
    file_path = repo / "wiki" / "page.md"

    with _mock_release_verification("ok"):
        exit_code = retire_repo_data_cli.main(
            ["--repo-root", str(repo), "--paths-config", str(config_path), "--yes"]
        )

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert exit_code == 0
    assert file_path.is_file()
    assert "wiki/page.md" not in tracked


def _init_git_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Initialize a Git repository with tracked files."""
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


def _externalize_paths(repo: Path) -> Path:
    """Create external knowledge and vault roots for CLI path resolution."""
    knowledge = repo.parent / "knowledge"
    vault = repo.parent / "vault"
    knowledge.mkdir(exist_ok=True)
    vault.mkdir(exist_ok=True)
    config_path = repo.parent / "wiki_paths.toml"
    config_path.write_text(
        f"""
[paths]
knowledge_root = "{knowledge}"
vault_root = "{vault}"
raw_dir = "{knowledge / "raw" / "readwise"}"
reviews_dir = "{knowledge / "state" / "reviews"}"
synthesis_dir = "{knowledge / "state" / "synthesis"}"
graph_path = "{knowledge / "state" / "wiki_render_graph.json"}"
manifest_path = "{knowledge / "state" / "wiki_render_manifest.json"}"
release_dir = "{knowledge / "state" / "releases"}"
preview_dir = "{knowledge / "tmp" / "synthesis_previews"}"
run_dir = "{knowledge / "tmp" / "synthesis_runs"}"
backup_dir = "{knowledge / "tmp" / "synthesis_backups"}"
wiki_dir = "{vault / "wiki"}"
source_pages_dir = "{vault / "wiki" / "sources" / "full"}"
source_index_path = "{vault / "wiki" / "sources" / "index.md"}"
indexes_dir = "{vault / "wiki" / "indexes"}"
""".strip(),
        encoding="utf-8",
    )
    return config_path


def _mock_release_verification(status: VerificationStatus):
    """Patch release verification to return one fixed status."""

    def _verification(_paths, *, selector, allow_path_mismatch=False, checked_at=None):
        del selector, allow_path_mismatch, checked_at
        return ReleaseVerificationReport(
            schema_version=1,
            release_id="20260712T120000Z",
            manifest_path=Path("state/releases/20260712T120000Z.json"),
            checked_at=datetime(2026, 7, 12, 16, 0, tzinfo=UTC),
            status=status,
            manifest_status=status,
            path_status="ok",
            area_results=[],
            messages=[],
        )

    return patch("src.wiki_ops.retirement_plan.verify_release", side_effect=_verification)
