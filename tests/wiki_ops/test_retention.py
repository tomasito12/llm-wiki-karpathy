"""Tests for artifact retention inventory."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops.retention import (
    CLEANUP_BLOCKED_REASON,
    artifact_area_definitions,
    collect_retention_inventory,
    inventory_area,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def test_builds_area_definitions_from_wiki_paths(tmp_path: Path) -> None:
    """Area definitions should be derived from resolved WikiPaths."""
    paths = default_wiki_paths(tmp_path)
    definitions = artifact_area_definitions(paths)
    keys = {definition.key for definition in definitions}

    assert "raw_readwise" in keys
    assert "wiki" in keys
    assert "synthesis_prompts" in keys
    assert definitions[0].path == paths.raw_dir


def test_classifies_core_paths_by_data_class(tmp_path: Path) -> None:
    """Canonical, generated, and temporary areas should be classified correctly."""
    paths = default_wiki_paths(tmp_path)
    by_key = {item.key: item for item in artifact_area_definitions(paths)}

    assert by_key["raw_readwise"].data_class == "canonical"
    assert by_key["reviews"].data_class == "canonical"
    assert by_key["synthesis_cache"].data_class == "canonical"
    assert by_key["wiki"].data_class == "generated"
    assert by_key["render_graph"].data_class == "generated"
    assert by_key["render_manifest"].data_class == "generated"
    assert by_key["synthesis_previews"].data_class == "temporary"
    assert by_key["synthesis_runs"].data_class == "temporary"
    assert by_key["synthesis_backups"].data_class == "temporary"
    assert by_key["synthesis_prompts"].data_class == "temporary"
    assert by_key["ingest_batches"].data_class == "temporary"


def test_counts_files_and_bytes_for_directories(tmp_path: Path) -> None:
    """Directory inventory should count nested regular files and bytes."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "a.md").write_text("aaa", encoding="utf-8")
    nested = raw_dir / "nested"
    nested.mkdir()
    (nested / "b.md").write_text("bb", encoding="utf-8")
    paths = default_wiki_paths(tmp_path)
    definition = next(
        item for item in artifact_area_definitions(paths) if item.key == "raw_readwise"
    )

    status = inventory_area(definition)

    assert status.exists is True
    assert status.file_count == 2
    assert status.byte_count == 5
    assert status.newest_mtime is not None
    assert status.oldest_mtime is not None


def test_counts_single_file_area_such_as_render_graph(tmp_path: Path) -> None:
    """Single-file areas such as graph or manifest should report one file."""
    graph_path = tmp_path / "state" / "wiki_render_graph.json"
    graph_path.parent.mkdir(parents=True)
    graph_path.write_text("{}", encoding="utf-8")
    paths = default_wiki_paths(tmp_path)
    definition = next(
        item for item in artifact_area_definitions(paths) if item.key == "render_graph"
    )

    status = inventory_area(definition)

    assert status.file_count == 1
    assert status.byte_count == graph_path.stat().st_size


def test_missing_optional_temporary_directories_do_not_error(tmp_path: Path) -> None:
    """Missing optional temporary paths should not produce top-level warnings."""
    paths = default_wiki_paths(tmp_path)
    inventory = collect_retention_inventory(paths)
    prompts = next(area for area in inventory.areas if area.key == "synthesis_prompts")

    assert prompts.exists is False
    assert prompts.file_count == 0
    assert "synthesis_prompts" not in " ".join(inventory.warnings)


def test_missing_canonical_directories_produce_warnings(tmp_path: Path) -> None:
    """Missing required canonical paths should produce warnings."""
    paths = default_wiki_paths(tmp_path)
    inventory = collect_retention_inventory(paths)

    assert any("Canonical path missing: raw_readwise" in warning for warning in inventory.warnings)
    assert any("Canonical path missing: reviews" in warning for warning in inventory.warnings)


def test_symlinked_directories_are_not_traversed(tmp_path: Path) -> None:
    """Inventory should not follow symlinked directories when counting files."""
    raw_dir = tmp_path / "raw" / "readwise"
    external = tmp_path / "external"
    external.mkdir()
    (external / "hidden.md").write_text("secret", encoding="utf-8")
    raw_dir.mkdir(parents=True)
    (raw_dir / "visible.md").write_text("ok", encoding="utf-8")
    (raw_dir / "link").symlink_to(external, target_is_directory=True)
    paths = default_wiki_paths(tmp_path)
    definition = next(
        item for item in artifact_area_definitions(paths) if item.key == "raw_readwise"
    )

    status = inventory_area(definition)

    assert status.file_count == 1


def test_inventory_is_read_only(monkeypatch, tmp_path: Path) -> None:
    """Retention inventory must not delete or write files."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    sample = raw_dir / "sample.md"
    sample.write_text("keep me", encoding="utf-8")

    def _forbidden(*args, **kwargs):
        raise AssertionError("retention inventory attempted a write/delete operation")

    monkeypatch.setattr(Path, "unlink", _forbidden)
    monkeypatch.setattr(Path, "write_text", _forbidden)
    collect_retention_inventory(default_wiki_paths(tmp_path))

    assert sample.read_text(encoding="utf-8") == "keep me"


def test_cleanup_preflight_is_read_only_blocked(tmp_path: Path) -> None:
    """Cleanup preflight should report blocked cleanup with zero candidates."""
    preview_dir = tmp_path / "state" / "synthesis_previews"
    preview_dir.mkdir(parents=True)
    (preview_dir / "preview.md").write_text("preview", encoding="utf-8")
    inventory = collect_retention_inventory(default_wiki_paths(tmp_path))

    assert inventory.cleanup_preflight.temporary_file_count == 1
    assert inventory.cleanup_preflight.cleanup_candidate_count == 0
    assert inventory.cleanup_preflight.cleanup_blocked_reason == CLEANUP_BLOCKED_REASON


def test_retention_json_shape_is_stable(tmp_path: Path) -> None:
    """Retention inventory JSON should include expected top-level keys."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "source.md").write_text("body", encoding="utf-8")
    payload = collect_retention_inventory(default_wiki_paths(tmp_path)).to_dict()

    assert "areas" in payload
    assert "totals_by_class" in payload
    assert "cleanup_preflight" in payload
    assert payload["totals_by_class"]["canonical"]["files"] >= 1
    json.dumps(payload)


def test_path_config_overrides_are_reflected_in_definitions(tmp_path: Path) -> None:
    """External knowledge paths from WikiPaths should appear in area definitions."""
    knowledge_root = tmp_path / "knowledge"
    paths = WikiPaths(
        repo_root=tmp_path / "repo",
        knowledge_root=knowledge_root,
        vault_root=tmp_path / "vault",
        raw_dir=knowledge_root / "raw" / "readwise",
        reviews_dir=knowledge_root / "state" / "reviews",
        synthesis_dir=knowledge_root / "state" / "synthesis",
        graph_path=knowledge_root / "state" / "wiki_render_graph.json",
        manifest_path=knowledge_root / "state" / "wiki_render_manifest.json",
        release_dir=knowledge_root / "state" / "releases",
        preview_dir=knowledge_root / "tmp" / "synthesis_previews",
        run_dir=knowledge_root / "tmp" / "synthesis_runs",
        backup_dir=knowledge_root / "tmp" / "synthesis_backups",
        wiki_dir=tmp_path / "vault" / "wiki",
        source_pages_dir=tmp_path / "vault" / "sources" / "full",
        source_index_path=tmp_path / "vault" / "sources" / "index.md",
        indexes_dir=tmp_path / "vault" / "indexes",
    )
    by_key = {item.key: item for item in artifact_area_definitions(paths)}

    assert by_key["raw_readwise"].path == knowledge_root / "raw" / "readwise"
    assert by_key["wiki"].path == tmp_path / "vault" / "wiki"
