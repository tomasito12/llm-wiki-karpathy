"""Tests for repo data untracking execution."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest

from src.wiki_ops.release_verify import ReleaseVerificationReport, VerificationStatus
from src.wiki_ops.retire_repo_data import (
    RepoDataUntrackingError,
    append_missing_gitignore_patterns,
    build_untracking_preflight,
    collect_untracking_candidates,
    detect_missing_gitignore_patterns,
    run_repo_data_untracking,
    untracking_report_to_json,
)
from src.wiki_ops.retirement_plan import build_retirement_plan
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def test_collect_untracking_candidates_only_includes_untrack_later(tmp_path: Path) -> None:
    """Only untrack_later files should become execution candidates."""
    repo = _init_git_repo(
        tmp_path,
        {
            "src/app.py": "ok\n",
            "wiki/page.md": "page\n",
            "state/reviews/source/review.json": "{}\n",
        },
    )
    paths = _external_wiki_paths(repo)
    plan = build_retirement_plan(paths)

    candidates = collect_untracking_candidates(plan)

    assert candidates
    assert all(candidate.path != "src/app.py" for candidate in candidates)
    assert {candidate.path for candidate in candidates} == {
        "wiki/page.md",
        "state/reviews/source/review.json",
    }


def test_manual_review_blocks_execution(tmp_path: Path) -> None:
    """Manual review files should block real execution."""
    repo = _init_git_repo(
        tmp_path,
        {
            "wiki/page.md": "page\n",
            "state/readwise_library.json": "{}\n",
        },
    )
    paths = _external_wiki_paths(repo)

    with _mock_release_verification("ok"):
        preflight = build_untracking_preflight(paths)

    assert preflight.readiness == "blocked"
    assert any("manual_review" in reason for reason in preflight.blocked_reasons)


def test_tracked_local_config_blocks_execution(tmp_path: Path) -> None:
    """Tracked local config should block execution."""
    repo = _init_git_repo(tmp_path, {"config/wiki_paths.toml": "[paths]\n", "wiki/page.md": "x\n"})
    paths = _external_wiki_paths(repo)

    with _mock_release_verification("ok"):
        preflight = build_untracking_preflight(paths)

    assert preflight.readiness == "blocked"
    assert any("Local configuration files" in reason for reason in preflight.blocked_reasons)


def test_missing_external_roots_block_execution(tmp_path: Path) -> None:
    """Repo-local roots should block execution."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    paths = default_wiki_paths(repo)

    with _mock_release_verification("ok"):
        preflight = build_untracking_preflight(paths)

    assert preflight.readiness == "blocked"
    assert any("code repository" in reason.lower() for reason in preflight.blocked_reasons)


def test_invalid_chunk_size_raises_untracking_error(tmp_path: Path) -> None:
    """Invalid chunk sizes should fail before chunk planning."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    paths = _external_wiki_paths(repo)

    with _mock_release_verification("ok"):
        with pytest.raises(RepoDataUntrackingError, match="chunk_size must be positive"):
            build_untracking_preflight(paths, chunk_size=0)


def test_detect_missing_gitignore_patterns_in_dry_run(tmp_path: Path) -> None:
    """Dry-run should detect missing required gitignore patterns."""
    repo = tmp_path / "repo"
    repo.mkdir()
    gitignore = repo / ".gitignore"
    gitignore.write_text("raw/**\n", encoding="utf-8")

    missing = detect_missing_gitignore_patterns(gitignore)

    assert "raw/**" not in missing
    assert "wiki/" in missing
    assert "state/reviews/" in missing


def test_append_missing_gitignore_patterns_in_real_run(tmp_path: Path) -> None:
    """Real execution should append only missing gitignore patterns."""
    repo = tmp_path / "repo"
    repo.mkdir()
    gitignore = repo / ".gitignore"
    gitignore.write_text("raw/**\n", encoding="utf-8")

    added = append_missing_gitignore_patterns(gitignore)
    content = gitignore.read_text(encoding="utf-8")

    assert "wiki/" in added
    assert "Externalized knowledge data and generated vault content" in content
    assert content.count("raw/**") == 1


def test_git_rm_cached_uses_list_arguments_and_chunks(tmp_path: Path, monkeypatch) -> None:
    """git rm --cached should be invoked with list arguments in chunks."""
    repo = _init_git_repo(
        tmp_path,
        {f"wiki/file-{index}.md": "x\n" for index in range(5)},
    )
    paths = _external_wiki_paths(repo)
    calls: list[list[str]] = []
    real_run = subprocess.run

    def _record_run(command, *args, **kwargs):
        if len(command) >= 3 and command[:3] == ["git", "rm", "--cached"]:
            calls.append(list(command))

            class _Result:
                returncode = 0
                stdout = ""
                stderr = ""

            return _Result()
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", _record_run)

    with _mock_release_verification("ok"):
        report = run_repo_data_untracking(paths, dry_run=False, chunk_size=2)

    assert report.files_untracked
    assert all(call[:3] == ["git", "rm", "--cached"] for call in calls)
    assert len(calls) == 3


def test_candidate_files_are_not_deleted_from_disk(tmp_path: Path, monkeypatch) -> None:
    """Untracking should remove Git index entries without deleting local files."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    file_path = repo / "wiki" / "page.md"
    paths = _external_wiki_paths(repo)

    with _mock_release_verification("ok"):
        run_repo_data_untracking(paths, dry_run=False, chunk_size=200)

    assert file_path.is_file()
    assert file_path.read_text(encoding="utf-8") == "page\n"


def test_missing_on_disk_candidate_can_still_be_untracked(tmp_path: Path) -> None:
    """Missing worktree files that remain tracked should still be untracked."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    (repo / "wiki" / "page.md").unlink()
    paths = _external_wiki_paths(repo)
    clean_git = patch(
        "src.wiki_ops.retirement_plan.collect_git_metadata",
        return_value=_clean_git_metadata(repo),
    )

    with _mock_release_verification("ok"), clean_git:
        report = run_repo_data_untracking(paths, dry_run=False, chunk_size=200)

    assert report.files_untracked == ["wiki/page.md"]
    tracked, _error = _git_ls_files(repo)
    assert "wiki/page.md" not in tracked


def test_dry_run_performs_no_writes(tmp_path: Path, monkeypatch) -> None:
    """Dry-run must not modify gitignore or run git rm --cached."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    paths = _external_wiki_paths(repo)

    real_run = subprocess.run

    def _wrap(command, *args, **kwargs):
        if len(command) >= 3 and command[:3] == ["git", "rm", "--cached"]:
            raise AssertionError("unexpected git rm --cached")
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", _wrap)

    with _mock_release_verification("ok"):
        report = run_repo_data_untracking(paths, dry_run=True)

    assert report.mode == "dry_run"
    assert report.files_untracked == []
    assert report.gitignore_updated is False


def test_untracking_json_is_valid_and_deterministic(tmp_path: Path) -> None:
    """JSON output should be deterministic for identical inputs."""
    repo = _init_git_repo(tmp_path, {"wiki/a.md": "a\n", "wiki/b.md": "b\n"})
    paths = _external_wiki_paths(repo)

    with _mock_release_verification("ok"):
        first = cast(
            dict[str, Any],
            untracking_report_to_json(run_repo_data_untracking(paths, dry_run=True)),
        )
        second = cast(
            dict[str, Any],
            untracking_report_to_json(run_repo_data_untracking(paths, dry_run=True)),
        )

    assert first == second
    assert [candidate["path"] for candidate in first["candidates"]] == sorted(
        candidate["path"] for candidate in first["candidates"]
    )


def test_real_run_writes_audit_report(tmp_path: Path) -> None:
    """Real runs should write one audit report under the audit directory."""
    repo = _init_git_repo(tmp_path, {"wiki/page.md": "page\n"})
    paths = _external_wiki_paths(repo)
    audit_dir = repo / "state" / "retirement_runs"

    with _mock_release_verification("ok"):
        report = run_repo_data_untracking(
            paths,
            dry_run=False,
            audit_dir=audit_dir,
            when=_fixed_moment(),
        )

    assert report.audit_report_path is not None
    assert report.audit_report_path.parent == audit_dir
    assert report.audit_report_path.exists()


def _init_git_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Initialize a Git repository with tracked files."""
    repo = tmp_path / "repo"
    repo.mkdir()
    env = _git_env()
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


def _external_wiki_paths(repo: Path) -> WikiPaths:
    """Return wiki paths with external knowledge and vault roots."""
    knowledge = repo.parent / "knowledge"
    vault = repo.parent / "vault"
    knowledge.mkdir(exist_ok=True)
    vault.mkdir(exist_ok=True)
    return WikiPaths(
        repo_root=repo,
        knowledge_root=knowledge,
        vault_root=vault,
        raw_dir=knowledge / "raw" / "readwise",
        reviews_dir=knowledge / "state" / "reviews",
        synthesis_dir=knowledge / "state" / "synthesis",
        graph_path=knowledge / "state" / "wiki_render_graph.json",
        manifest_path=knowledge / "state" / "wiki_render_manifest.json",
        release_dir=knowledge / "state" / "releases",
        preview_dir=knowledge / "tmp" / "synthesis_previews",
        run_dir=knowledge / "tmp" / "synthesis_runs",
        backup_dir=knowledge / "tmp" / "synthesis_backups",
        wiki_dir=vault / "wiki",
        source_pages_dir=vault / "wiki" / "sources" / "full",
        source_index_path=vault / "wiki" / "sources" / "index.md",
        indexes_dir=vault / "wiki" / "indexes",
    )


def _git_env() -> dict[str, str]:
    """Return Git author env for test repositories."""
    return {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }


def _git_ls_files(repo: Path) -> tuple[list[str], str | None]:
    """Return tracked files for one repository."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return [], result.stderr.decode("utf-8", errors="replace")
    return [item for item in result.stdout.decode("utf-8").split("\0") if item], None


def _mock_release_verification(status: VerificationStatus):
    """Patch release verification to return one fixed status."""

    def _verification(_paths, *, selector, allow_path_mismatch=False, checked_at=None):
        del selector, allow_path_mismatch, checked_at
        return ReleaseVerificationReport(
            schema_version=1,
            release_id="20260712T120000Z",
            manifest_path=Path("state/releases/20260712T120000Z.json"),
            checked_at=_fixed_moment(),
            status=status,
            manifest_status=status,
            path_status="ok",
            area_results=[],
            messages=[],
        )

    return patch("src.wiki_ops.retirement_plan.verify_release", side_effect=_verification)


def _clean_git_metadata(repo: Path):
    from src.wiki_ops.release_manifest import GitMetadata

    return GitMetadata(
        repo_root=repo.resolve(),
        git_commit="abc123",
        git_dirty=False,
    )


def _fixed_moment():
    from datetime import UTC, datetime

    return datetime(2026, 7, 12, 16, 0, tzinfo=UTC)
