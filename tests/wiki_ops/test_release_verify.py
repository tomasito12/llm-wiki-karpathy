"""Tests for release manifest verification."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.wiki_ops.release_manifest import build_release_manifest
from src.wiki_ops.release_verify import (
    ReleaseSelectionError,
    select_release_manifest_path,
    verify_release,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def test_select_release_manifest_path_latest_chooses_lexicographic_latest(tmp_path: Path) -> None:
    """Latest selector should choose the lexicographically greatest manifest."""
    paths = _bootstrap_release_repo(tmp_path)
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    (release_dir / "20260101T000000Z.json").write_text("{}", encoding="utf-8")
    (release_dir / "20260712T120000Z.json").write_text("{}", encoding="utf-8")

    selected = select_release_manifest_path(paths, "latest")

    assert selected.name == "20260712T120000Z.json"


def test_select_release_manifest_path_explicit_id(tmp_path: Path) -> None:
    """Explicit release ids should map to one manifest file."""
    paths = _bootstrap_release_repo(tmp_path)
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    manifest = release_dir / "20260712T140520Z.json"
    manifest.write_text("{}", encoding="utf-8")

    selected = select_release_manifest_path(paths, "20260712T140520Z")

    assert selected == manifest


def test_select_release_manifest_path_missing_directory_raises(tmp_path: Path) -> None:
    """Missing release directories should raise a selection error."""
    paths = _bootstrap_release_repo(tmp_path)

    with pytest.raises(ReleaseSelectionError, match="No release manifests found"):
        select_release_manifest_path(paths, "latest")


def test_verify_release_malformed_manifest_returns_error(tmp_path: Path) -> None:
    """Malformed manifest JSON should produce an error report."""
    paths = _bootstrap_release_repo(tmp_path)
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    manifest = release_dir / "20260712T140520Z.json"
    manifest.write_text("{not-json", encoding="utf-8")

    report = verify_release(
        paths,
        selector="20260712T140520Z",
        checked_at=datetime(2026, 7, 12, 14, 30, tzinfo=UTC),
    )

    assert report.status == "error"
    assert any("malformed" in message.lower() for message in report.messages)


def test_verify_release_unsupported_schema_returns_error(tmp_path: Path) -> None:
    """Unsupported schema versions should produce an error report."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", schema_version=99)

    report = verify_release(paths, selector="20260712T140520Z")

    assert report.status == "error"
    assert any("Unsupported release manifest schema" in message for message in report.messages)


def test_verify_release_all_areas_match_ready_manifest_returns_ok(tmp_path: Path) -> None:
    """Matching content with a ready manifest should verify as ok."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", status="ready")

    report = verify_release(paths, selector="20260712T140520Z")

    assert report.status == "ok"
    assert all(area.status == "ok" for area in report.area_results)


def test_verify_release_all_areas_match_warning_manifest_returns_warning(tmp_path: Path) -> None:
    """Matching content with a warning manifest should verify as warning."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(
        paths,
        release_id="20260712T140520Z",
        status="warning",
        status_reasons=["Temporary artifacts were present when it was created."],
    )

    report = verify_release(paths, selector="20260712T140520Z")

    assert report.status == "warning"
    assert report.manifest_status == "warning"
    assert any("Manifest status is warning." in message for message in report.messages)


def test_verify_release_file_count_mismatch_returns_error(tmp_path: Path) -> None:
    """File count drift should produce an area error."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", status="ready")
    (paths.raw_dir / "extra.md").write_text("more", encoding="utf-8")

    report = verify_release(paths, selector="20260712T140520Z")
    raw_area = _area(report, "raw_readwise")

    assert report.status == "error"
    assert raw_area.status == "error"
    assert any("File count differs." in message for message in raw_area.messages)


def test_verify_release_byte_count_mismatch_returns_error(tmp_path: Path) -> None:
    """Byte count drift should produce an area error."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", status="ready")
    source_md = paths.raw_dir / "source.md"
    source_md.write_text(source_md.read_text(encoding="utf-8") + "changed", encoding="utf-8")

    report = verify_release(paths, selector="20260712T140520Z")
    raw_area = _area(report, "raw_readwise")

    assert report.status == "error"
    assert raw_area.status == "error"
    assert any(
        message in {"Byte count differs.", "sha256 differs."} for message in raw_area.messages
    )


def test_verify_release_sha_mismatch_returns_error(tmp_path: Path) -> None:
    """Hash drift should produce an area error."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", status="ready")
    (paths.wiki_dir / "sources" / "source.md").write_text(
        "---\nsource_text_available: true\n---\nchanged\n",
        encoding="utf-8",
    )

    report = verify_release(paths, selector="20260712T140520Z")
    wiki_area = _area(report, "wiki")

    assert report.status == "error"
    assert wiki_area.status == "error"
    assert any("sha256 differs." in message for message in wiki_area.messages)


def test_verify_release_missing_required_manifest_area_returns_error(tmp_path: Path) -> None:
    """Missing required manifest areas should produce an error."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(paths, release_id="20260712T140520Z")
    payload = manifest.to_dict()
    del payload["areas"]["wiki"]
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    (release_dir / "20260712T140520Z.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    report = verify_release(paths, selector="20260712T140520Z")
    wiki_area = _area(report, "wiki")

    assert report.status == "error"
    assert wiki_area.status == "error"
    assert any("Required manifest area is missing." in message for message in wiki_area.messages)


def test_verify_release_missing_required_path_returns_error(tmp_path: Path) -> None:
    """Missing required manifest paths should produce an area error."""
    paths = _bootstrap_release_repo(tmp_path)
    manifest = build_release_manifest(paths, release_id="20260712T140520Z")
    payload = manifest.to_dict()
    del payload["paths"]["wiki_dir"]
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    (release_dir / "20260712T140520Z.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    report = verify_release(paths, selector="20260712T140520Z")
    wiki_area = _area(report, "wiki")

    assert report.status == "error"
    assert report.path_status == "error"
    assert wiki_area.status == "error"
    assert any("Required manifest path is missing." in message for message in wiki_area.messages)


def test_verify_release_path_mismatch_returns_error_by_default(tmp_path: Path) -> None:
    """Path drift should error when mismatches are not allowed."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", status="ready")
    moved_paths = _replace_paths(paths, raw_dir=tmp_path / "moved" / "raw")
    moved_paths.raw_dir.mkdir(parents=True)
    for file_path in paths.raw_dir.glob("*"):
        (moved_paths.raw_dir / file_path.name).write_text(
            file_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    report = verify_release(moved_paths, selector="20260712T140520Z")
    raw_area = _area(report, "raw_readwise")

    assert report.status == "error"
    assert report.path_status == "error"
    assert raw_area.status == "error"
    assert any("Path differs from manifest." in message for message in raw_area.messages)


def test_verify_release_path_mismatch_allowed_returns_warning(tmp_path: Path) -> None:
    """Allowed path drift should warn when content still matches."""
    paths = _bootstrap_release_repo(tmp_path)
    _write_manifest(paths, release_id="20260712T140520Z", status="ready")
    moved_paths = _replace_paths(paths, raw_dir=tmp_path / "moved" / "raw")
    moved_paths.raw_dir.mkdir(parents=True)
    for file_path in paths.raw_dir.glob("*"):
        (moved_paths.raw_dir / file_path.name).write_text(
            file_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    report = verify_release(
        moved_paths,
        selector="20260712T140520Z",
        allow_path_mismatch=True,
    )
    raw_area = _area(report, "raw_readwise")

    assert report.status == "warning"
    assert report.path_status == "warning"
    assert raw_area.status == "warning"
    assert any("Path differs from manifest." in message for message in raw_area.messages)


def test_verify_release_does_not_create_missing_directories(tmp_path: Path, monkeypatch) -> None:
    """Verification must remain read-only and not create release directories."""
    paths = _bootstrap_release_repo(tmp_path)
    mkdir_calls: list[Path] = []

    def _track_mkdir(self: Path, *args, **kwargs) -> None:
        mkdir_calls.append(self)
        raise AssertionError("unexpected mkdir")

    monkeypatch.setattr(Path, "mkdir", _track_mkdir, raising=False)

    with pytest.raises(ReleaseSelectionError):
        verify_release(paths, selector="latest")

    assert mkdir_calls == []


def _write_manifest(
    paths: WikiPaths,
    *,
    release_id: str,
    status: str = "ready",
    status_reasons: list[str] | None = None,
    schema_version: int = 1,
) -> Path:
    """Write one release manifest that matches the current repo layout."""
    manifest = build_release_manifest(paths, release_id=release_id)
    payload = manifest.to_dict()
    payload["schema_version"] = schema_version
    payload["status"] = status
    if status_reasons is not None:
        payload["status_reasons"] = status_reasons
    release_dir = paths.release_dir
    release_dir.mkdir(parents=True)
    output_path = release_dir / f"{release_id}.json"
    output_path.write_text(json.dumps(payload), encoding="utf-8")
    return output_path


def _area(report, area_key: str):
    """Return one area verification result by key."""
    return next(area for area in report.area_results if area.area_key == area_key)


def _replace_paths(paths: WikiPaths, **overrides: Path) -> WikiPaths:
    """Return a copy of wiki paths with selected fields replaced."""
    return WikiPaths(
        repo_root=paths.repo_root,
        knowledge_root=paths.knowledge_root,
        vault_root=paths.vault_root,
        raw_dir=overrides.get("raw_dir", paths.raw_dir),
        reviews_dir=overrides.get("reviews_dir", paths.reviews_dir),
        synthesis_dir=overrides.get("synthesis_dir", paths.synthesis_dir),
        graph_path=overrides.get("graph_path", paths.graph_path),
        manifest_path=overrides.get("manifest_path", paths.manifest_path),
        release_dir=overrides.get("release_dir", paths.release_dir),
        preview_dir=overrides.get("preview_dir", paths.preview_dir),
        run_dir=overrides.get("run_dir", paths.run_dir),
        backup_dir=overrides.get("backup_dir", paths.backup_dir),
        wiki_dir=overrides.get("wiki_dir", paths.wiki_dir),
        source_pages_dir=overrides.get("source_pages_dir", paths.source_pages_dir),
        source_index_path=overrides.get("source_index_path", paths.source_index_path),
        indexes_dir=overrides.get("indexes_dir", paths.indexes_dir),
    )


def _bootstrap_release_repo(tmp_path: Path) -> WikiPaths:
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
