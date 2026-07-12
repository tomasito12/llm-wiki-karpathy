"""Tests for temporary artifact cleanup planning and execution."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.wiki_ops.cleanup import (
    CleanupCandidate,
    CleanupPlan,
    CleanupValidationError,
    build_cleanup_plan,
    execute_cleanup,
    validate_candidate_deletion,
    write_cleanup_report,
)
from src.wiki_ops.release_manifest import (
    SCHEMA_VERSION,
    GitMetadata,
    ReleaseAreaSummary,
    ReleaseManifest,
    ReleaseStatus,
    write_release_manifest,
)
from src.wiki_ops.retention import artifact_area_definitions
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def test_dry_run_plan_is_default_and_deletes_nothing(monkeypatch, tmp_path: Path) -> None:
    """Dry-run planning should not delete files."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    delete_calls: list[Path] = []

    def _track_unlink(self: Path, missing_ok: bool = False) -> None:
        delete_calls.append(self)
        raise AssertionError("unexpected delete")

    monkeypatch.setattr(Path, "unlink", _track_unlink, raising=False)
    plan = build_cleanup_plan(paths, dry_run=True)

    assert plan.dry_run is True
    assert plan.candidate_count >= 1
    assert delete_calls == []


def test_planning_includes_synthesis_previews_files(tmp_path: Path) -> None:
    """Planning should include synthesis preview files."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    preview = paths.preview_dir / "topic" / "example.md"
    preview.parent.mkdir(parents=True, exist_ok=True)
    preview.write_text("preview", encoding="utf-8")

    plan = build_cleanup_plan(paths)

    preview_candidates = [
        candidate for candidate in plan.candidates if candidate.area_key == "synthesis_previews"
    ]
    assert preview_candidates
    assert preview.resolve() in {candidate.path for candidate in preview_candidates}


def test_planning_includes_synthesis_backups_files(tmp_path: Path) -> None:
    """Planning should include synthesis backup files."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    backup = paths.backup_dir / "backup.json"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text("{}", encoding="utf-8")

    plan = build_cleanup_plan(paths)

    backup_candidates = [
        candidate for candidate in plan.candidates if candidate.area_key == "synthesis_backups"
    ]
    assert backup.resolve() in {candidate.path for candidate in backup_candidates}


def test_planning_reports_synthesis_runs_but_does_not_include_them(tmp_path: Path) -> None:
    """Run reports should be reported as skipped, not deleted by default."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    run_report = paths.run_dir / "run.json"
    run_report.parent.mkdir(parents=True, exist_ok=True)
    run_report.write_text("{}", encoding="utf-8")

    plan = build_cleanup_plan(paths)

    assert all(candidate.area_key != "synthesis_runs" for candidate in plan.candidates)
    skipped = next(area for area in plan.skipped_areas if area.area_key == "synthesis_runs")
    assert "audit" in skipped.reason


def test_missing_optional_temporary_directories_do_not_fail_planning(tmp_path: Path) -> None:
    """Missing optional temporary directories should not fail planning."""
    paths = default_wiki_paths(tmp_path)

    plan = build_cleanup_plan(paths)

    assert plan.candidate_count == 0
    assert plan.blocked is True


def test_symlinked_directories_are_not_traversed(tmp_path: Path) -> None:
    """Planning should not follow symlinked directories."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    (external / "hidden.md").write_text("secret", encoding="utf-8")
    preview_dir = paths.preview_dir
    preview_dir.mkdir(parents=True, exist_ok=True)
    (preview_dir / "visible.md").write_text("ok", encoding="utf-8")
    (preview_dir / "link").symlink_to(external, target_is_directory=True)

    plan = build_cleanup_plan(paths)

    assert all("hidden.md" not in str(candidate.path) for candidate in plan.candidates)
    assert any(str(candidate.path).endswith("visible.md") for candidate in plan.candidates)


def test_symlinked_files_are_not_deleted(tmp_path: Path) -> None:
    """Symlinked files should not become cleanup candidates."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    target = paths.preview_dir / "target.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("target", encoding="utf-8")
    link = paths.preview_dir / "link.md"
    link.symlink_to(target)

    plan = build_cleanup_plan(paths)

    assert link not in {candidate.path for candidate in plan.candidates}
    assert target.resolve() in {candidate.path for candidate in plan.candidates}


def test_candidates_are_sorted_deterministically(tmp_path: Path) -> None:
    """Candidates should be sorted by path for stable output."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    preview_dir = paths.preview_dir
    preview_dir.mkdir(parents=True, exist_ok=True)
    (preview_dir / "b.md").write_text("b", encoding="utf-8")
    (preview_dir / "a.md").write_text("a", encoding="utf-8")

    plan = build_cleanup_plan(paths)
    candidate_paths = [str(candidate.path) for candidate in plan.candidates]

    assert candidate_paths == sorted(candidate_paths)


def test_missing_release_manifest_blocks_real_cleanup(tmp_path: Path) -> None:
    """Missing release manifests should block real cleanup."""
    paths = _bootstrap_cleanup_repo(tmp_path)

    plan = build_cleanup_plan(
        paths,
        dry_run=False,
        after_release="20260712T223000Z",
    )

    assert plan.blocked is True
    assert any("Release manifest not found" in reason for reason in plan.blocked_reasons)


def test_blocked_release_manifest_blocks_real_cleanup(tmp_path: Path) -> None:
    """Blocked release manifests should block real cleanup."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    manifest_path = _write_release_manifest(
        paths,
        release_id="20260712T223000Z",
        status="blocked",
    )

    plan = build_cleanup_plan(
        paths,
        dry_run=False,
        after_release="20260712T223000Z",
    )

    assert plan.blocked is True
    assert plan.release_manifest_path == manifest_path
    assert any("blocked" in reason.lower() for reason in plan.blocked_reasons)


def test_path_mismatch_blocks_real_cleanup(tmp_path: Path) -> None:
    """Path mismatches between manifest and current config should block cleanup."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    _write_release_manifest(paths, release_id="20260712T223000Z", status="warning")
    moved_wiki = tmp_path / "moved-wiki"
    moved_wiki.mkdir()
    paths = replace(paths, wiki_dir=moved_wiki)

    plan = build_cleanup_plan(
        paths,
        dry_run=False,
        after_release="20260712T223000Z",
    )

    assert plan.blocked is True
    assert any("paths do not match" in reason for reason in plan.blocked_reasons)


def test_execute_cleanup_validates_all_candidates_before_deleting_any(
    tmp_path: Path,
) -> None:
    """Safety validation failures should abort before any file is deleted."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    first = paths.preview_dir / "first.md"
    second = paths.preview_dir / "second.md"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")
    _write_release_manifest(paths, release_id="20260712T223000Z", status="warning")
    plan = CleanupPlan(
        dry_run=False,
        after_release="20260712T223000Z",
        release_manifest_path=paths.release_dir / "20260712T223000Z.json",
        candidates=[
            CleanupCandidate(
                area_key="synthesis_previews",
                path=first.resolve(),
                byte_count=5,
                reason="clean after release",
            ),
            CleanupCandidate(
                area_key="synthesis_previews",
                path=paths.wiki_dir / "page.md",
                byte_count=4,
                reason="clean after release",
            ),
            CleanupCandidate(
                area_key="synthesis_previews",
                path=second.resolve(),
                byte_count=6,
                reason="clean after release",
            ),
        ],
        skipped_areas=[],
        candidate_count=3,
        candidate_bytes=15,
        blocked=False,
        blocked_reasons=[],
    )

    with pytest.raises(CleanupValidationError):
        execute_cleanup(
            plan,
            paths,
            created_at=datetime(2026, 7, 12, 23, 0, tzinfo=UTC),
        )

    assert first.exists() is True
    assert second.exists() is True
    assert not (paths.knowledge_root / "state" / "cleanup_runs").exists()


def test_real_cleanup_deletes_only_allowed_temporary_files(tmp_path: Path) -> None:
    """Real cleanup should delete only allowlisted temporary files."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    preview = paths.preview_dir / "topic" / "example.md"
    preview.parent.mkdir(parents=True, exist_ok=True)
    preview.write_text("preview", encoding="utf-8")
    run_report = paths.run_dir / "run.json"
    run_report.parent.mkdir(parents=True, exist_ok=True)
    run_report.write_text("{}", encoding="utf-8")
    _write_release_manifest(paths, release_id="20260712T223000Z", status="warning")

    plan = build_cleanup_plan(
        paths,
        dry_run=False,
        after_release="20260712T223000Z",
    )
    result = execute_cleanup(
        plan,
        paths,
        created_at=datetime(2026, 7, 12, 23, 0, tzinfo=UTC),
    )

    assert preview.exists() is False
    assert run_report.exists() is True
    assert result.deleted_count == plan.candidate_count
    assert result.report_path is not None


def test_real_cleanup_never_deletes_protected_files(tmp_path: Path) -> None:
    """Protected canonical and generated files must never be deleted."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    _write_release_manifest(paths, release_id="20260712T223000Z", status="warning")
    protected_files = [
        paths.raw_dir / "source.md",
        paths.reviews_dir / "source" / "review.json",
        paths.synthesis_dir / "topic" / "entry.json",
        paths.wiki_dir / "page.md",
        paths.graph_path,
        paths.manifest_path,
    ]
    for file_path in protected_files:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("protected", encoding="utf-8")
    release_manifest = paths.release_dir / "20260712T223000Z.json"

    plan = build_cleanup_plan(
        paths,
        dry_run=False,
        after_release="20260712T223000Z",
    )
    execute_cleanup(
        plan,
        paths,
        created_at=datetime(2026, 7, 12, 23, 0, tzinfo=UTC),
    )

    for file_path in protected_files:
        assert file_path.exists() is True
    assert release_manifest.exists() is True


def test_validate_candidate_deletion_rejects_protected_paths(tmp_path: Path) -> None:
    """Safety validation should reject protected paths even if they appear as candidates."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    area_roots = {
        definition.key: definition.path
        for definition in artifact_area_definitions(paths)
        if definition.data_class == "temporary"
    }
    wiki_file = paths.wiki_dir / "page.md"
    wiki_file.parent.mkdir(parents=True, exist_ok=True)
    wiki_file.write_text("wiki", encoding="utf-8")
    candidate = CleanupCandidate(
        area_key="synthesis_previews",
        path=wiki_file.resolve(),
        byte_count=4,
        reason="clean after release",
    )

    error = validate_candidate_deletion(candidate, area_roots=area_roots, paths=paths)

    assert error is not None


def test_area_filter_limits_candidates(tmp_path: Path) -> None:
    """Area filters should limit cleanup candidates to one allowlisted area."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    preview = paths.preview_dir / "preview.md"
    preview.parent.mkdir(parents=True, exist_ok=True)
    preview.write_text("preview", encoding="utf-8")
    backup = paths.backup_dir / "backup.json"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text("{}", encoding="utf-8")

    plan = build_cleanup_plan(
        paths,
        selected_areas=frozenset({"synthesis_previews"}),
    )

    assert {candidate.area_key for candidate in plan.candidates} <= {"synthesis_previews"}


def test_write_cleanup_report_creates_one_json_file(tmp_path: Path) -> None:
    """Real cleanup should write one cleanup report JSON file."""
    paths = _bootstrap_cleanup_repo(tmp_path)
    report_path = write_cleanup_report(
        paths,
        after_release="20260712T223000Z",
        release_manifest_path=paths.release_dir / "20260712T223000Z.json",
        dry_run=False,
        deleted_paths=[paths.preview_dir / "preview.md"],
        deleted_bytes=7,
        skipped_areas=[],
        created_at=datetime(2026, 7, 12, 23, 0, tzinfo=UTC),
    )

    assert report_path.exists()
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["after_release"] == "20260712T223000Z"


def _bootstrap_cleanup_repo(tmp_path: Path):
    """Create a minimal repo with temporary artifacts and a valid release manifest."""
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    (paths.raw_dir / "source.md").write_text("body", encoding="utf-8")
    review_dir = paths.reviews_dir / "source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text("{}", encoding="utf-8")
    paths.synthesis_dir.mkdir(parents=True)
    paths.wiki_dir.mkdir(parents=True)
    (paths.wiki_dir / "page.md").write_text("page", encoding="utf-8")
    paths.graph_path.parent.mkdir(parents=True, exist_ok=True)
    paths.graph_path.write_text("{}", encoding="utf-8")
    paths.manifest_path.write_text("{}", encoding="utf-8")
    paths.preview_dir.mkdir(parents=True, exist_ok=True)
    (paths.preview_dir / "seed.md").write_text("seed", encoding="utf-8")
    return paths


def _write_release_manifest(
    paths: WikiPaths,
    *,
    release_id: str,
    status: ReleaseStatus,
) -> Path:
    """Write a minimal valid release manifest for cleanup tests."""
    manifest = ReleaseManifest(
        schema_version=SCHEMA_VERSION,
        release_id=release_id,
        created_at="2026-07-12T22:30:00Z",
        status=status,
        status_reasons=[],
        code=GitMetadata(repo_root=paths.repo_root, git_commit="abc", git_dirty=False),
        paths={
            "raw_dir": str(paths.raw_dir),
            "reviews_dir": str(paths.reviews_dir),
            "synthesis_dir": str(paths.synthesis_dir),
            "wiki_dir": str(paths.wiki_dir),
            "graph_path": str(paths.graph_path),
            "manifest_path": str(paths.manifest_path),
            "release_dir": str(paths.release_dir),
        },
        areas={
            "raw_readwise": ReleaseAreaSummary("canonical", True, 1, 1, "hash"),
            "reviews": ReleaseAreaSummary("canonical", True, 1, 1, "hash"),
            "synthesis_cache": ReleaseAreaSummary("canonical", True, 0, 0, "hash"),
            "render_graph": ReleaseAreaSummary("generated", True, 1, 1, "hash"),
            "render_manifest": ReleaseAreaSummary("generated", True, 1, 1, "hash"),
            "wiki": ReleaseAreaSummary("generated", True, 1, 1, "hash"),
        },
        counts={"raw_files": 1, "reviews": 1, "synthesis_entries": 0, "wiki_files": 1},
        retention={
            "temporary_file_count": 1,
            "temporary_byte_count": 1,
            "cleanup_candidate_count": 0,
            "cleanup_blocked_reason": "test",
        },
        warnings=[],
        output_path=paths.release_dir / f"{release_id}.json",
    )
    return write_release_manifest(manifest)
