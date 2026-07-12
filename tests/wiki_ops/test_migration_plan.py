"""Tests for knowledge store migration planning."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from src.wiki_ops.migration_plan import (
    build_migration_plan,
    classify_current_location,
    detect_path_overlaps,
    migration_plan_to_json,
)
from src.wiki_ops.status import (
    ArtifactStatus,
    OpsStatus,
    RenderStatus,
    ReviewStatus,
    SourceStatus,
    SynthesisPlanStatus,
    SynthesisStatus,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def test_default_repo_local_layout_returns_warning_not_crash(tmp_path: Path) -> None:
    """Default repo-local layout should produce a warning readiness status."""
    paths = _bootstrap_repo_local_layout(tmp_path)

    plan = build_migration_plan(paths)

    assert plan.readiness.status == "warning"
    assert any(
        "No external knowledge_root is configured yet." in warning
        for warning in plan.readiness.warnings
    )


def test_require_external_knowledge_root_blocks_when_equal_to_repo(tmp_path: Path) -> None:
    """Requiring external knowledge root should block repo-local configuration."""
    paths = _bootstrap_repo_local_layout(tmp_path)

    plan = build_migration_plan(paths, require_external_knowledge_root=True)

    assert plan.readiness.status == "blocked"
    assert any(
        "knowledge_root equals repo_root" in reason for reason in plan.readiness.blocked_reasons
    )


def test_require_external_vault_root_blocks_when_equal_to_repo(tmp_path: Path) -> None:
    """Requiring external vault root should block repo-local configuration."""
    paths = _bootstrap_repo_local_layout(tmp_path)

    plan = build_migration_plan(paths, require_external_vault_root=True)

    assert plan.readiness.status == "blocked"
    assert any("vault_root equals repo_root" in reason for reason in plan.readiness.blocked_reasons)


def test_external_paths_are_classified_as_knowledge_store_and_vault(tmp_path: Path) -> None:
    """External configured roots should classify paths outside the code repo."""
    repo = tmp_path / "repo"
    knowledge = tmp_path / "knowledge"
    vault = tmp_path / "vault"
    _bootstrap_repo_local_layout(repo)
    paths = WikiPaths(
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
    paths.raw_dir.mkdir(parents=True)
    (paths.raw_dir / "source.md").write_text("body", encoding="utf-8")
    paths.wiki_dir.mkdir(parents=True)
    (paths.wiki_dir / "page.md").write_text("page", encoding="utf-8")

    plan = build_migration_plan(paths)
    raw_area = next(area for area in plan.areas if area.area_key == "raw_readwise")
    wiki_area = next(area for area in plan.areas if area.area_key == "wiki")

    assert raw_area.current_location == "knowledge_store"
    assert raw_area.migration_action == "already_external"
    assert wiki_area.current_location == "vault"
    assert wiki_area.migration_action == "already_external"


def test_missing_optional_temporary_paths_are_not_blockers(tmp_path: Path) -> None:
    """Missing optional temporary paths should not block migration planning."""
    paths = _bootstrap_repo_local_layout(tmp_path)

    plan = build_migration_plan(paths)
    prompts = next(area for area in plan.areas if area.area_key == "synthesis_prompts")

    assert prompts.exists is False
    assert plan.readiness.status != "blocked" or all(
        "synthesis_prompts" not in reason for reason in plan.readiness.blocked_reasons
    )


def test_missing_required_canonical_paths_block(tmp_path: Path) -> None:
    """Missing required canonical paths should block readiness."""
    paths = default_wiki_paths(tmp_path)

    plan = build_migration_plan(paths)

    assert plan.readiness.status == "blocked"
    assert any("raw_readwise" in reason for reason in plan.readiness.blocked_reasons)


def test_path_overlap_detection_blocks_unsafe_layouts(tmp_path: Path) -> None:
    """Unsafe nested path layouts should be detected."""
    paths = default_wiki_paths(tmp_path)
    paths = replace(paths, wiki_dir=paths.raw_dir / "wiki")

    overlaps = detect_path_overlaps(paths)

    assert any("wiki_dir is inside raw_dir" in item for item in overlaps)


def test_file_counting_ignores_symlink_directories(tmp_path: Path) -> None:
    """Migration planning should ignore symlinked directories when counting files."""
    paths = _bootstrap_repo_local_layout(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    (external / "hidden.md").write_text("secret", encoding="utf-8")
    for existing in paths.preview_dir.glob("*"):
        if existing.is_file():
            existing.unlink()
    (paths.preview_dir / "visible.md").write_text("ok", encoding="utf-8")
    (paths.preview_dir / "link").symlink_to(external, target_is_directory=True)

    plan = build_migration_plan(paths)
    previews = next(area for area in plan.areas if area.area_key == "synthesis_previews")

    assert previews.file_count == 1


def test_migration_plan_json_contains_required_fields(tmp_path: Path) -> None:
    """Migration JSON should include schema, roots, readiness, and areas."""
    paths = _bootstrap_repo_local_layout(tmp_path)

    payload = migration_plan_to_json(build_migration_plan(paths))

    assert payload["schema_version"] == 1
    assert "roots" in payload
    assert "readiness" in payload
    assert isinstance(payload["areas"], list)
    assert json.dumps(payload)


def test_migration_plan_is_read_only(monkeypatch, tmp_path: Path) -> None:
    """Migration planning must not create directories or delete files."""
    paths = _bootstrap_repo_local_layout(tmp_path)
    mkdir_calls: list[Path] = []

    def _track_mkdir(self: Path, *args, **kwargs) -> None:
        mkdir_calls.append(self)
        raise AssertionError("unexpected mkdir")

    monkeypatch.setattr(Path, "mkdir", _track_mkdir, raising=False)

    build_migration_plan(paths)

    assert mkdir_calls == []


def test_missing_releases_directory_does_not_block_readiness(tmp_path: Path) -> None:
    """Missing releases directory should warn, not block migration readiness."""
    paths = _bootstrap_repo_local_layout(tmp_path, create_release_dir=False)

    plan = build_migration_plan(paths)

    assert plan.readiness.status == "warning"
    assert not any("releases" in reason for reason in plan.readiness.blocked_reasons)
    assert any("No release manifest exists." in warning for warning in plan.readiness.warnings)
    releases = next(area for area in plan.areas if area.area_key == "releases")
    assert releases.exists is False
    assert releases.status == "ok"


def test_empty_raw_directory_blocks_when_review_artifacts_exist(tmp_path: Path) -> None:
    """Empty raw exports should block when review artifacts already exist."""
    paths = _bootstrap_repo_local_layout(tmp_path)
    for file_path in paths.raw_dir.glob("*"):
        file_path.unlink()
    ops_status = _sample_ops_status(review_artifacts=5, graph_sources=10)

    plan = build_migration_plan(paths, ops_status=ops_status)
    raw_area = next(area for area in plan.areas if area.area_key == "raw_readwise")

    assert raw_area.file_count == 0
    assert raw_area.status == "blocked"
    assert any("contains no files" in warning for warning in raw_area.warnings)


def test_empty_raw_directory_warns_without_downstream_data(tmp_path: Path) -> None:
    """Empty raw exports should warn even when no review or graph data exists yet."""
    paths = _bootstrap_repo_local_layout(tmp_path)
    for file_path in paths.raw_dir.glob("*"):
        file_path.unlink()
    ops_status = _sample_ops_status(review_artifacts=0, graph_sources=0)

    plan = build_migration_plan(paths, ops_status=ops_status)
    raw_area = next(area for area in plan.areas if area.area_key == "raw_readwise")

    assert raw_area.status == "warning"


def test_latest_release_manifest_only_evaluates_newest(tmp_path: Path) -> None:
    """Only the newest release manifest should drive readiness warnings."""
    paths = _bootstrap_repo_local_layout(tmp_path)
    release_dir = paths.release_dir
    (release_dir / "20260101T000000Z.json").write_text(
        json.dumps({"status": "warning"}),
        encoding="utf-8",
    )
    (release_dir / "20260712T120000Z.json").write_text(
        json.dumps({"status": "ready"}),
        encoding="utf-8",
    )

    plan = build_migration_plan(paths)

    assert plan.readiness.status == "warning"
    assert not any(
        "Latest release manifest readiness is warning." in warning
        for warning in plan.readiness.warnings
    )


def test_classify_current_location_external(tmp_path: Path) -> None:
    """Paths outside known roots should classify as external."""
    repo = tmp_path / "repo"
    repo.mkdir()
    paths = default_wiki_paths(repo)
    external = tmp_path / "external-data"
    external.mkdir()
    (external / "file.txt").write_text("x", encoding="utf-8")

    location = classify_current_location(external, paths)

    assert location == "external"


def _bootstrap_repo_local_layout(
    tmp_path: Path,
    *,
    create_release_dir: bool = True,
) -> WikiPaths:
    """Create a minimal repo-local layout for migration planning tests."""
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
    (paths.preview_dir / "preview.md").write_text("preview", encoding="utf-8")
    if create_release_dir:
        paths.release_dir.mkdir(parents=True, exist_ok=True)
    return paths


def _sample_ops_status(*, review_artifacts: int, graph_sources: int) -> OpsStatus:
    """Build a minimal ops status snapshot for migration tests."""
    empty_plan = SynthesisPlanStatus(
        new=None,
        stale=None,
        unchanged=None,
        skipped_single_source=None,
        skipped_evidence_object=None,
    )
    return OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(
            artifacts=review_artifacts,
            finished=review_artifacts,
            in_progress=0,
            malformed=0,
        ),
        render=RenderStatus(
            wiki_dir_exists=True,
            graph_exists=True,
            manifest_exists=True,
            graph_sources=graph_sources,
            graph_knowledge_pages=graph_sources,
        ),
        synthesis=SynthesisStatus(
            cache_entries=0,
            fresh=0,
            stale=0,
            errors=0,
            missing=0,
            plan=empty_plan,
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
    )
