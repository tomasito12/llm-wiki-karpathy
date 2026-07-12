"""Tests for old repo data retirement planning."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, cast

from src.wiki_ops.retirement_plan import (
    build_retirement_plan,
    classify_tracked_path,
    format_retirement_plan_text,
    list_tracked_files,
    retirement_plan_to_json,
)
from src.wiki_paths.config import default_wiki_paths


def test_classify_code_files_as_keep_tracked() -> None:
    """Normal code files should remain tracked in the code repository."""
    area, action, _reason = classify_tracked_path("src/wiki_ops/status.py")

    assert area == "src"
    assert action == "keep_tracked"


def test_classify_wiki_files_as_untrack_later() -> None:
    """Generated wiki pages should be untracked later."""
    area, action, _reason = classify_tracked_path("wiki/topics/example.md")

    assert area == "wiki"
    assert action == "untrack_later"


def test_classify_state_reviews_as_untrack_later() -> None:
    """Review artifacts should be untracked later."""
    _area, action, _reason = classify_tracked_path("state/reviews/source/review.json")

    assert action == "untrack_later"


def test_classify_state_synthesis_as_untrack_later() -> None:
    """Synthesis cache entries should be untracked later."""
    _area, action, _reason = classify_tracked_path("state/synthesis/glossary/fine-tuning.json")

    assert action == "untrack_later"


def test_classify_render_graph_and_manifest_as_untrack_later() -> None:
    """Render audit artifacts should be untracked later."""
    _area, graph_action, _reason = classify_tracked_path("state/wiki_render_graph.json")
    _area2, manifest_action, _reason2 = classify_tracked_path("state/wiki_render_manifest.json")

    assert graph_action == "untrack_later"
    assert manifest_action == "untrack_later"


def test_classify_temporary_artifacts_as_untrack_later() -> None:
    """Temporary operational artifacts should be untracked later."""
    cases = (
        "state/synthesis_previews/glossary/example.md",
        "state/synthesis_runs/20260712T120000Z.json",
        "state/synthesis_backups/glossary/example.json.bak",
        "state/synthesis_prompts/glossary-example.md",
        "state/ingest_batches/latest.log",
    )
    for path in cases:
        _area, action, _reason = classify_tracked_path(path)
        assert action == "untrack_later", path


def test_classify_legacy_raw_placeholder_as_untrack_later() -> None:
    """The historical raw placeholder should leave Git with external raw data."""
    area, action, reason = classify_tracked_path("raw/.gitkeep")

    assert area == "raw"
    assert action == "untrack_later"
    assert "externalized raw data" in reason


def test_classify_legacy_ingest_manifest_as_untrack_later() -> None:
    """The legacy ingest manifest should leave Git with external state."""
    area, action, reason = classify_tracked_path("state/ingest_manifest.json")

    assert area == "state/ingest_manifest"
    assert action == "untrack_later"
    assert "external knowledge-store state" in reason


def test_classify_tests_fixtures_as_keep_tracked() -> None:
    """Test fixtures should remain tracked in the code repository."""
    _area, action, _reason = classify_tracked_path("tests/fixtures/wiki/sample.md")

    assert action == "keep_tracked"


def test_classify_unknown_state_file_as_manual_review() -> None:
    """Unknown tracked state files should require manual review."""
    area, action, reason = classify_tracked_path("state/readwise_library.json")

    assert area == "state/readwise_library.json"
    assert action == "manual_review"
    assert "manual review" in reason.lower()


def test_format_retirement_plan_text_lists_manual_review_files(tmp_path: Path) -> None:
    """Human-readable output should name manual-review files."""
    repo = _init_git_repo(
        tmp_path,
        {
            "src/app.py": "ok\n",
            "state/readwise_library.json": "{}\n",
        },
    )
    paths = default_wiki_paths(repo)

    text = format_retirement_plan_text(build_retirement_plan(paths))

    assert "Manual review files" in text
    assert "state/readwise_library.json" in text


def test_tracked_local_config_blocks_readiness(tmp_path: Path) -> None:
    """Tracked local config files should block retirement readiness."""
    repo = _init_git_repo(
        tmp_path,
        {
            "config/wiki_paths.toml": "[paths]\n",
            "src/app.py": "print('ok')\n",
        },
    )
    paths = default_wiki_paths(repo)

    plan = build_retirement_plan(paths)

    assert plan.readiness == "blocked"
    assert any(
        item.key == "tracked_local_config" and item.status == "error" for item in plan.preconditions
    )


def test_retirement_plan_json_is_deterministic(tmp_path: Path) -> None:
    """Retirement JSON should sort files and areas deterministically."""
    repo = _init_git_repo(
        tmp_path,
        {
            "wiki/b.md": "b\n",
            "wiki/a.md": "a\n",
            "src/app.py": "ok\n",
        },
    )
    paths = default_wiki_paths(repo)

    first = cast(dict[str, Any], retirement_plan_to_json(build_retirement_plan(paths)))
    second = cast(dict[str, Any], retirement_plan_to_json(build_retirement_plan(paths)))

    assert first == second
    assert [entry["path"] for entry in first["files"]] == sorted(
        entry["path"] for entry in first["files"]
    )
    assert [area["key"] for area in first["areas"]] == sorted(
        area["key"] for area in first["areas"]
    )


def test_list_tracked_files_handles_git_failure(tmp_path: Path, monkeypatch) -> None:
    """Git inventory failures should return an error instead of raising."""

    def _fail(*args, **kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(subprocess, "run", _fail)
    paths, error = list_tracked_files(tmp_path)

    assert paths == []
    assert error == "git unavailable"


def test_build_retirement_plan_marks_git_inventory_error_as_blocked(
    tmp_path: Path, monkeypatch
) -> None:
    """Blocked readiness should follow Git inventory failures."""
    repo = _init_git_repo(tmp_path, {"src/app.py": "ok\n"})
    paths = default_wiki_paths(repo)

    def _fail(*args, **kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(subprocess, "run", _fail)
    plan = build_retirement_plan(paths)

    assert plan.readiness == "blocked"
    assert plan.git_inventory_error == "git unavailable"


def test_retirement_plan_is_read_only(monkeypatch, tmp_path: Path) -> None:
    """Retirement planning must not create directories or delete files."""
    repo = _init_git_repo(tmp_path, {"src/app.py": "ok\n"})
    paths = default_wiki_paths(repo)
    mkdir_calls: list[Path] = []

    def _track_mkdir(self: Path, *args, **kwargs) -> None:
        mkdir_calls.append(self)
        raise AssertionError("unexpected mkdir")

    monkeypatch.setattr(Path, "mkdir", _track_mkdir, raising=False)
    build_retirement_plan(paths)

    assert mkdir_calls == []


def test_external_roots_required_for_ready_state(tmp_path: Path) -> None:
    """Repo-local roots should block retirement readiness."""
    repo = _init_git_repo(
        tmp_path,
        {
            "src/app.py": "ok\n",
            "wiki/page.md": "page\n",
        },
    )
    paths = default_wiki_paths(repo)

    plan = build_retirement_plan(paths)

    assert plan.readiness == "blocked"
    assert plan.summary.untrack_later >= 1


def _init_git_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Initialize a Git repository with tracked files for retirement tests."""
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
