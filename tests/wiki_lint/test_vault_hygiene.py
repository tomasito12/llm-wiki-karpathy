"""Tests for vault hygiene reporting."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_lint.vault_hygiene import (
    collect_vault_hygiene_status,
    load_manifest_paths,
)


def _write_manifest(manifest_path: Path, paths: list[str]) -> None:
    """Write a minimal render manifest fixture."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"files": [{"path": path, "sha256": "abc"} for path in paths]}),
        encoding="utf-8",
    )


def test_load_manifest_paths_returns_relative_paths(tmp_path: Path) -> None:
    """Manifest parsing should return wiki-relative paths."""
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["topics/example.md", "sources/source-a.md"])

    assert load_manifest_paths(manifest) == {"topics/example.md", "sources/source-a.md"}


def test_load_manifest_paths_handles_missing_file(tmp_path: Path) -> None:
    """Missing manifest files should behave like an empty manifest."""
    assert load_manifest_paths(tmp_path / "missing.json") == set()


def test_deletable_paths_from_status_skips_duplicate_keep_path() -> None:
    """Deletable paths should never include the recommended duplicate keep file."""
    from src.wiki_lint.vault_hygiene import (
        VaultDuplicateGroup,
        VaultHygieneItem,
        VaultHygieneStatus,
        deletable_paths_from_status,
    )

    status = VaultHygieneStatus(
        manifest_exists=True,
        manifest_paths=1,
        vault_markdown_files=3,
        orphan_total=2,
        safe_delete_candidates=(
            VaultHygieneItem(
                path="topics/keep.md",
                category="safe_delete_candidate",
                reason="orphan",
            ),
            VaultHygieneItem(
                path="topics/remove.md",
                category="safe_delete_candidate",
                reason="orphan",
            ),
        ),
        protected_in_progress=(),
        manual_review=(),
        manual_root_items=(),
        duplicate_groups=(
            VaultDuplicateGroup(
                sha256="abc",
                paths=("topics/keep.md", "topics/remove.md"),
                recommended_keep="topics/keep.md",
            ),
        ),
        recommended_actions=(),
    )

    assert deletable_paths_from_status(status) == ("topics/remove.md",)


def test_duplicate_removal_paths_keeps_recommended_file() -> None:
    """Duplicate removal helper should keep the recommended path only."""
    from src.wiki_lint.vault_hygiene import VaultDuplicateGroup, duplicate_removal_paths

    groups = (
        VaultDuplicateGroup(
            sha256="abc",
            paths=("topics/keep.md", "topics/remove.md"),
            recommended_keep="topics/keep.md",
        ),
    )

    assert duplicate_removal_paths(groups) == ("topics/remove.md",)


def test_collect_vault_hygiene_status_flags_stale_orphan(tmp_path: Path) -> None:
    """Managed pages outside the manifest should be safe-delete candidates."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, ["topics/current.md"])
    stale = wiki / "topics" / "stale.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("# stale\n", encoding="utf-8")
    (wiki / "topics" / "current.md").write_text("# current\n", encoding="utf-8")

    status, warnings = collect_vault_hygiene_status(
        wiki_dir=wiki,
        manifest_path=manifest,
        reviews_dir=tmp_path / "reviews",
        raw_dir=tmp_path / "raw",
        repo_root=tmp_path / "repo",
        synthesis_cache_dir=tmp_path / "synthesis",
    )

    assert status.orphan_total == 1
    assert len(status.safe_delete_candidates) == 1
    assert status.safe_delete_candidates[0].path == "topics/stale.md"
    assert warnings


def test_collect_vault_hygiene_status_does_not_mark_orphans_safe_when_render_stale(
    tmp_path: Path,
) -> None:
    """Managed orphans should not be safe-delete candidates when the render graph is stale."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    manifest = tmp_path / "manifest.json"
    graph = tmp_path / "graph.json"
    reviews = tmp_path / "reviews"
    _write_manifest(manifest, ["sources/current.md"])
    graph.write_text(
        json.dumps({"sources": [{"source_id": "current"}]}),
        encoding="utf-8",
    )
    review_dir = reviews / "new-source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-07-16T10:00:00Z"}}),
        encoding="utf-8",
    )
    stale_source = wiki / "sources" / "new-source.md"
    stale_source.parent.mkdir(parents=True)
    stale_source.write_text("# new source\n", encoding="utf-8")

    status, warnings = collect_vault_hygiene_status(
        wiki_dir=wiki,
        manifest_path=manifest,
        reviews_dir=reviews,
        raw_dir=tmp_path / "raw",
        repo_root=tmp_path / "repo",
        synthesis_cache_dir=tmp_path / "synthesis",
        graph_path=graph,
    )

    assert status.render_manifest_stale is True
    assert "1 finished source(s)" in str(status.render_manifest_stale_reason)
    assert status.orphan_total == 1
    assert not status.safe_delete_candidates
    assert len(status.manual_review) == 1
    assert "Render manifest may be stale" in status.manual_review[0].reason
    assert any("not safe to delete" in warning for warning in warnings)


def test_collect_vault_hygiene_status_classifies_manual_legacy_paths(tmp_path: Path) -> None:
    """Preserved manual folders should require review instead of auto-delete."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, [])
    legacy = wiki / "legacy" / "manual-ingest" / "README.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("# legacy\n", encoding="utf-8")
    (wiki / "log.md").write_text("# log\n", encoding="utf-8")

    status, _warnings = collect_vault_hygiene_status(
        wiki_dir=wiki,
        manifest_path=manifest,
        reviews_dir=tmp_path / "reviews",
        raw_dir=tmp_path / "raw",
        repo_root=tmp_path / "repo",
        synthesis_cache_dir=tmp_path / "synthesis",
    )

    assert status.orphan_total == 2
    assert not status.safe_delete_candidates
    assert len(status.manual_review) == 2
    assert len(status.manual_root_items) == 2


def test_collect_vault_hygiene_status_detects_exact_duplicates(tmp_path: Path) -> None:
    """Exact duplicate managed pages should be grouped with a keep recommendation."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    manifest = tmp_path / "manifest.json"
    _write_manifest(
        manifest,
        ["interview-insights/2026-04/example-short.md"],
    )
    body = "# duplicate body\n"
    short = wiki / "interview-insights" / "2026-04" / "example-short.md"
    long = wiki / "interview-insights" / "2026-04" / "example-with-very-long-title.md"
    short.parent.mkdir(parents=True)
    short.write_text(body, encoding="utf-8")
    long.write_text(body, encoding="utf-8")

    status, _warnings = collect_vault_hygiene_status(
        wiki_dir=wiki,
        manifest_path=manifest,
        reviews_dir=tmp_path / "reviews",
        raw_dir=tmp_path / "raw",
        repo_root=tmp_path / "repo",
        synthesis_cache_dir=tmp_path / "synthesis",
    )

    assert len(status.duplicate_groups) == 1
    group = status.duplicate_groups[0]
    assert group.recommended_keep == "interview-insights/2026-04/example-short.md"
    assert len(group.paths) == 2


def test_collect_vault_hygiene_status_warns_when_manifest_missing(tmp_path: Path) -> None:
    """Missing manifest should produce guidance without crashing."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()

    status, warnings = collect_vault_hygiene_status(
        wiki_dir=wiki,
        manifest_path=tmp_path / "missing.json",
        reviews_dir=tmp_path / "reviews",
        raw_dir=tmp_path / "raw",
        repo_root=tmp_path / "repo",
        synthesis_cache_dir=tmp_path / "synthesis",
    )

    assert not status.manifest_exists
    assert warnings
    assert "Render manifest is missing" in warnings[0]


def test_collect_vault_hygiene_status_handles_missing_wiki_dir(tmp_path: Path) -> None:
    """Missing wiki directories should return an empty hygiene snapshot."""
    status, warnings = collect_vault_hygiene_status(
        wiki_dir=tmp_path / "missing-wiki",
        manifest_path=tmp_path / "manifest.json",
        reviews_dir=tmp_path / "reviews",
        raw_dir=tmp_path / "raw",
        repo_root=tmp_path / "repo",
        synthesis_cache_dir=tmp_path / "synthesis",
    )

    assert status.vault_markdown_files == 0
    assert warnings
    assert "wiki directory missing" in warnings[0].lower()
