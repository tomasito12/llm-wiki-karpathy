"""Tests for release manifest building and hashing."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.wiki_ops.release_manifest import (
    GitMetadata,
    build_release_manifest,
    collect_git_metadata,
    evaluate_release_status,
    hash_path,
    write_release_manifest,
)
from src.wiki_ops.retention import collect_retention_inventory
from src.wiki_paths.config import default_wiki_paths


def test_hash_path_for_file_returns_stable_sha256(tmp_path: Path) -> None:
    """Hashing a single file should return stable metadata."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")

    first = hash_path(file_path)
    second = hash_path(file_path)

    assert first.kind == "file"
    assert first.file_count == 1
    assert first.byte_count == 5
    assert first.sha256 == second.sha256
    assert first.sha256 is not None


def test_directory_hash_is_deterministic_regardless_of_creation_order(tmp_path: Path) -> None:
    """Directory hashes should not depend on file creation order."""
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / "b.txt").write_text("bb", encoding="utf-8")
    (directory / "a.txt").write_text("aa", encoding="utf-8")

    first = hash_path(directory)

    other = tmp_path / "other"
    other.mkdir()
    (other / "a.txt").write_text("aa", encoding="utf-8")
    (other / "b.txt").write_text("bb", encoding="utf-8")
    second = hash_path(other)

    assert first.file_count == 2
    assert first.sha256 == second.sha256


def test_directory_hash_ignores_symlinked_directories(tmp_path: Path) -> None:
    """Directory hashing should not follow symlinked directories."""
    directory = tmp_path / "raw"
    external = tmp_path / "external"
    external.mkdir()
    (external / "hidden.txt").write_text("secret", encoding="utf-8")
    directory.mkdir()
    (directory / "visible.txt").write_text("ok", encoding="utf-8")
    (directory / "link").symlink_to(external, target_is_directory=True)

    result = hash_path(directory)

    assert result.file_count == 1
    assert result.byte_count == 2


def test_missing_path_is_represented_as_missing(tmp_path: Path) -> None:
    """Missing paths should not raise and should report kind missing."""
    result = hash_path(tmp_path / "missing")

    assert result.exists is False
    assert result.kind == "missing"
    assert result.sha256 is None


def test_manifest_includes_required_schema_fields(tmp_path: Path) -> None:
    """Release manifests should include the required top-level schema fields."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(
        paths,
        release_id="20260712T223000Z",
        created_at=datetime(2026, 7, 12, 22, 30, tzinfo=UTC),
    )
    payload = manifest.to_dict()

    assert payload["schema_version"] == 1
    assert payload["release_id"] == "20260712T223000Z"
    assert payload["created_at"] == "2026-07-12T22:30:00Z"
    assert payload["status"] in {"ready", "warning", "blocked"}
    assert isinstance(payload["status_reasons"], list)
    assert "git_commit" in payload["code"]
    assert "git_dirty" in payload["code"]
    assert "areas" in payload
    assert "retention" in payload


def test_manifest_includes_resolved_paths(tmp_path: Path) -> None:
    """Manifest paths should reflect resolved wiki path configuration."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(paths, release_id="20260712T223000Z")

    assert manifest.paths["raw_dir"] == str(paths.raw_dir)
    assert manifest.paths["wiki_dir"] == str(paths.wiki_dir)
    assert manifest.paths["release_dir"] == str(paths.release_dir)


def test_manifest_counts_reviews_use_review_artifacts_not_directory_files(
    tmp_path: Path,
) -> None:
    """counts.reviews should count review artifacts, not every file under reviews/."""
    paths = _bootstrap_release_repo(tmp_path)
    review_dir = paths.reviews_dir / "source"
    (review_dir / "notes.txt").write_text("extra file", encoding="utf-8")
    review_dir_two = paths.reviews_dir / "source-two"
    review_dir_two.mkdir()
    (review_dir_two / "review.json").write_text("{}", encoding="utf-8")

    manifest = build_release_manifest(paths, release_id="20260712T223000Z")

    assert manifest.areas["reviews"].file_count == 3
    assert manifest.counts["reviews"] == 2


def test_manifest_counts_reviews_use_ops_status_when_provided(tmp_path: Path) -> None:
    """counts.reviews should prefer ops_status review artifact counts when available."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    paths = _bootstrap_release_repo(tmp_path)
    ops_status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(artifacts=42, finished=40, in_progress=2, malformed=0),
        render=RenderStatus(False, False, False, None, None),
        synthesis=SynthesisStatus(
            cache_entries=0,
            fresh=None,
            stale=None,
            errors=None,
            missing=None,
            plan=SynthesisPlanStatus(None, None, None, None, None),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
    )

    manifest = build_release_manifest(
        paths,
        release_id="20260712T223000Z",
        ops_status=ops_status,
    )

    assert manifest.counts["reviews"] == 42


def test_manifest_includes_canonical_and_generated_area_hashes(tmp_path: Path) -> None:
    """Canonical and generated areas should include deterministic hashes."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(paths, release_id="20260712T223000Z")

    for key in ("raw_readwise", "reviews", "render_graph", "wiki"):
        area = manifest.areas[key]
        assert area.exists is True
        assert area.file_count >= 1
        assert area.sha256 is not None
    synthesis_cache = manifest.areas["synthesis_cache"]
    assert synthesis_cache.exists is True
    assert synthesis_cache.sha256 is not None


def test_temporary_artifacts_produce_warning_status(tmp_path: Path) -> None:
    """Temporary artifacts should downgrade release readiness to warning."""
    paths = _bootstrap_release_repo(tmp_path)
    preview_dir = paths.preview_dir
    preview_dir.mkdir(parents=True, exist_ok=True)
    (preview_dir / "preview.md").write_text("preview", encoding="utf-8")
    inventory = collect_retention_inventory(paths)

    status, reasons, _warnings = evaluate_release_status(
        inventory=inventory,
        area_hashes={key: hash_path(area.path) for key, area in _area_map(inventory).items()},
        git=GitMetadata(repo_root=paths.repo_root, git_commit="abc", git_dirty=False),
        ops_status=None,
        source_text_warning=None,
    )

    assert status == "warning"
    assert any("Temporary artifacts are present." in reason for reason in reasons)


def test_missing_canonical_paths_produce_blocked_status(tmp_path: Path) -> None:
    """Missing canonical data should block release readiness."""
    paths = default_wiki_paths(tmp_path)
    inventory = collect_retention_inventory(paths)

    status, reasons, _warnings = evaluate_release_status(
        inventory=inventory,
        area_hashes={key: hash_path(area.path) for key, area in _area_map(inventory).items()},
        git=GitMetadata(repo_root=paths.repo_root, git_commit=None, git_dirty=None),
        ops_status=None,
        source_text_warning=None,
    )

    assert status == "blocked"
    assert any("Canonical path missing" in reason for reason in reasons)


def test_dirty_git_metadata_produces_warning_status(tmp_path: Path) -> None:
    """Dirty Git metadata should produce warning status when available."""
    paths = _bootstrap_release_repo(tmp_path)
    inventory = collect_retention_inventory(paths)
    git = GitMetadata(repo_root=paths.repo_root, git_commit="abc123", git_dirty=True)

    status, reasons, _warnings = evaluate_release_status(
        inventory=inventory,
        area_hashes={key: hash_path(area.path) for key, area in _area_map(inventory).items()},
        git=git,
        ops_status=None,
        source_text_warning=None,
    )

    assert status == "warning"
    assert any("uncommitted changes" in reason.lower() for reason in reasons)


def test_collect_git_metadata_gracefully_handles_missing_git(tmp_path: Path) -> None:
    """Git metadata collection should not fail when Git is unavailable."""
    metadata = collect_git_metadata(tmp_path)

    assert metadata.git_commit is None or isinstance(metadata.git_commit, str)
    assert metadata.git_dirty is None or isinstance(metadata.git_dirty, bool)


def test_write_release_manifest_creates_one_json_file(tmp_path: Path) -> None:
    """Writing a manifest should create exactly one JSON file."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(paths, release_id="20260712T223000Z")

    output_path = write_release_manifest(manifest)

    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["release_id"] == "20260712T223000Z"
    assert list(paths.release_dir.glob("*.json")) == [output_path]


def test_write_release_manifest_refuses_overwrite_by_default(tmp_path: Path) -> None:
    """Existing manifest files should not be overwritten unless requested."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(paths, release_id="20260712T223000Z")
    write_release_manifest(manifest)

    with pytest.raises(FileExistsError):
        write_release_manifest(manifest, overwrite=False)


def test_release_manifest_is_read_only_except_for_explicit_write(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Preview/build paths must not delete files."""
    paths = _bootstrap_release_repo(tmp_path)
    delete_calls: list[Path] = []

    def _track_unlink(self: Path, missing_ok: bool = False) -> None:
        delete_calls.append(self)
        raise AssertionError("unexpected delete")

    monkeypatch.setattr(Path, "unlink", _track_unlink, raising=False)

    build_release_manifest(paths, release_id="20260712T223000Z")

    assert delete_calls == []


def _bootstrap_release_repo(tmp_path: Path):
    """Create a minimal repo layout that satisfies release readiness checks."""
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    (paths.raw_dir / "source.html").write_text("<html></html>", encoding="utf-8")
    (paths.raw_dir / "source.md").write_text("body", encoding="utf-8")
    review_dir = paths.reviews_dir / "source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text("{}", encoding="utf-8")
    paths.synthesis_dir.mkdir(parents=True)
    paths.graph_path.parent.mkdir(parents=True, exist_ok=True)
    paths.graph_path.write_text('{"sources": []}', encoding="utf-8")
    paths.manifest_path.write_text("{}", encoding="utf-8")
    wiki_source = paths.wiki_dir / "sources"
    wiki_source.mkdir(parents=True)
    (wiki_source / "source.md").write_text(
        "---\nsource_text_available: true\n---\nbody\n",
        encoding="utf-8",
    )
    return paths


def _area_map(inventory):
    """Return inventory areas keyed by area name."""
    return {area.key: area for area in inventory.areas}
