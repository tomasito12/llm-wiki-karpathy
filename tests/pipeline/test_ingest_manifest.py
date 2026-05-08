"""Tests for ingest manifest persistence."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

from src.pipeline.ingest_manifest import (
    IngestManifest,
    IngestManifestRecord,
    IngestManifestStore,
    Stage2RouteRecord,
    default_manifest_path,
)


def test_manifest_load_missing_returns_empty(tmp_path: Path) -> None:
    """Missing manifest behaves like an empty manifest."""
    manifest = IngestManifest.load(tmp_path / "missing.json")
    assert manifest.records == {}


def test_manifest_roundtrip_preserves_routes_and_artifacts(tmp_path: Path) -> None:
    """Saved manifest reloads routes, artifacts, and status."""
    path = tmp_path / "manifest.json"
    record = IngestManifestRecord(
        source_id="source-1",
        raw_md_path="raw/readwise/source.md",
        raw_html_path="raw/readwise/source.html",
        canonical_url="https://example.com/source",
        title="Source",
        stage1_route="tools-overview",
        stage2_routes=[
            Stage2RouteRecord(
                name="Tool",
                route="tool",
                target_path="wiki/tools/example/tool.md",
            )
        ],
        wiki_artifacts=["wiki/sources/source.md"],
        status="rendered",
    )
    manifest = IngestManifest(records={"source-1": record})
    manifest.save(path)

    loaded = IngestManifest.load(path)
    assert loaded.records["source-1"].status == "rendered"
    assert loaded.records["source-1"].stage2_routes[0].route == "tool"
    assert loaded.records["source-1"].wiki_artifacts == ["wiki/sources/source.md"]


def test_manifest_store_updates_status_and_errors(tmp_path: Path) -> None:
    """Store can upsert records and append validation errors."""
    store = IngestManifestStore(tmp_path / "manifest.json")
    record = IngestManifestRecord(
        source_id="source-1",
        raw_md_path="raw/readwise/source.md",
        raw_html_path="raw/readwise/source.html",
        canonical_url=None,
        title="Source",
    )
    store.upsert_record(record)
    updated = store.update_status("source-1", "failed", error="broken link")
    assert updated.status == "failed"
    assert updated.errors == ["broken link"]


def test_default_manifest_path_is_under_state() -> None:
    """Default manifest path points to state/ingest_manifest.json."""
    path = default_manifest_path()
    assert path.parent.name == "state"
    assert path.name == "ingest_manifest.json"


def test_manifest_store_upsert_no_tmp_files(tmp_path: Path) -> None:
    """Saving via the store leaves no ``*.tmp`` files next to the manifest."""
    path = tmp_path / "manifest.json"
    store = IngestManifestStore(path)
    record = IngestManifestRecord(
        source_id="source-1",
        raw_md_path="raw/readwise/source.md",
        raw_html_path="raw/readwise/source.html",
        canonical_url="https://example.com/p",
        title="Source",
        author="A",
        publication="Pub",
        published_date="2024-01-01",
        content_sha256="deadbeef",
        stage1_route="tools-overview",
        stage2_routes=[Stage2RouteRecord(name="X", route="tool", target_path="wiki/tools/c/x.md")],
        wiki_artifacts=["wiki/sources/source.md"],
        status="rendered",
    )
    store.upsert_record(record)
    assert list(tmp_path.rglob("*.tmp")) == []


def test_manifest_store_second_upsert_keeps_created_at(tmp_path: Path) -> None:
    """Re-upserting the same ``source_id`` preserves ``created_at``."""
    path = tmp_path / "manifest.json"
    store = IngestManifestStore(path)
    first = IngestManifestRecord(
        source_id="s1",
        raw_md_path="raw/readwise/a.md",
        raw_html_path="raw/readwise/a.html",
        canonical_url=None,
        title="T",
        created_at="2019-06-01T00:00:00+00:00",
        updated_at="2019-06-01T00:00:00+00:00",
    )
    with mock.patch(
        "src.pipeline.ingest_manifest.utc_now_iso",
        side_effect=["2020-01-01T00:00:00+00:00", "2021-01-01T00:00:00+00:00"],
    ):
        store.upsert_record(first)
        second = IngestManifestRecord(
            source_id="s1",
            raw_md_path="raw/readwise/a.md",
            raw_html_path="raw/readwise/a.html",
            canonical_url="https://ex.test",
            title="T2",
            status="rendered",
            created_at="ignored",
            updated_at="ignored",
        )
        store.upsert_record(second)
    loaded = IngestManifest.load(path).records["s1"]
    assert loaded.created_at == "2019-06-01T00:00:00+00:00"
    assert loaded.title == "T2"
    assert loaded.updated_at == "2021-01-01T00:00:00+00:00"


def test_update_status_failed_appends_error(tmp_path: Path) -> None:
    """``update_status`` sets status and appends error text."""
    path = tmp_path / "manifest.json"
    store = IngestManifestStore(path)
    store.upsert_record(
        IngestManifestRecord(
            source_id="s1",
            raw_md_path="m.md",
            raw_html_path="h.html",
            canonical_url=None,
            title="T",
        )
    )
    updated = store.update_status("s1", "failed", error="lint failed")
    assert updated.status == "failed"
    assert updated.errors == ["lint failed"]


def test_ingest_manifest_cli_prints_count(tmp_path: Path) -> None:
    """CLI reports record count for a manifest file."""
    from src.pipeline import ingest_manifest

    path = tmp_path / "manifest.json"
    IngestManifest.empty().save(path)
    with mock.patch("sys.argv", ["ingest-manifest", "--path", str(path)]):
        assert ingest_manifest.main() == 0
