"""Tests for wiki operations status collection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.pipeline.atomic import atomic_write_json
from src.wiki_ops.status import (
    OpsStatusConfig,
    PipelineAlignmentStatus,
    ReviewWorkflowStatus,
    build_recommendations,
    classify_uncommitted_paths,
    collect_ops_status,
    collect_pipeline_alignment_status,
    collect_readwise_index_status,
    collect_render_status,
    collect_review_status,
    collect_review_workflow_status,
    collect_source_status,
    default_config,
    format_text_report,
    parse_git_porcelain_paths,
)
from src.wiki_synthesis.cache import cache_file_path
from src.wiki_synthesis.input_hash import synthesis_input_hash


def test_collect_source_status_counts_paired_exports(tmp_path: Path) -> None:
    """Paired html/md exports should count as complete pairs."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "one.html").write_text("<html></html>", encoding="utf-8")
    (raw_dir / "one.md").write_text("body", encoding="utf-8")
    (raw_dir / "two.html").write_text("<html></html>", encoding="utf-8")

    status = collect_source_status(raw_dir)

    assert status.raw_html == 2
    assert status.raw_markdown == 1
    assert status.paired == 1
    assert status.incomplete == 1


def test_collect_source_status_handles_missing_raw_directory(tmp_path: Path) -> None:
    """Missing raw directories should return zero counts."""
    status = collect_source_status(tmp_path / "missing")

    assert status.raw_html == 0
    assert status.raw_markdown == 0
    assert status.paired == 0
    assert status.incomplete == 0


def test_collect_readwise_index_status_reports_aligned_index(tmp_path: Path) -> None:
    """The Readwise status should report aligned raw exports and index entries."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "article-01abc.html").write_text("<html></html>", encoding="utf-8")
    (raw_dir / "article-01abc.md").write_text("body", encoding="utf-8")
    index_path = tmp_path / "state" / "readwise_library.json"
    index_path.parent.mkdir()
    index_path.write_text(
        json.dumps(
            {
                "version": 1,
                "last_updated_after": "2026-07-01T00:00:00+00:00",
                "suppressed_ids": ["01sup"],
                "documents": {
                    "01abc": {
                        "html_path": "raw/readwise/article-01abc.html",
                        "md_path": "raw/readwise/article-01abc.md",
                        "source_url": "https://example.test",
                        "updated_at": "2026-07-01T00:00:00+00:00",
                        "content_sha256": "abc",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    status, warnings = collect_readwise_index_status(raw_dir=raw_dir, index_path=index_path)

    assert status is not None
    assert status.exists is True
    assert status.documents == 1
    assert status.suppressed_ids == 1
    assert status.watermark_present is True
    assert status.raw_exports_not_in_index == 0
    assert status.index_entries_missing_raw == 0
    assert warnings == []


def test_collect_readwise_index_status_warns_when_raw_exists_without_index(
    tmp_path: Path,
) -> None:
    """Existing raw exports with a missing index should be visible in ops status."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "article-01abc.html").write_text("<html></html>", encoding="utf-8")
    (raw_dir / "article-01abc.md").write_text("body", encoding="utf-8")

    status, warnings = collect_readwise_index_status(
        raw_dir=raw_dir,
        index_path=tmp_path / "state" / "readwise_library.json",
    )

    assert status is not None
    assert status.exists is False
    assert status.documents == 0
    assert status.raw_exports_not_in_index == 1
    assert any("Readwise index missing while raw exports exist" in item for item in warnings)


def test_collect_readwise_index_status_warns_about_two_way_mismatch(
    tmp_path: Path,
) -> None:
    """Raw-only and index-only entries should both be reported."""
    raw_dir = tmp_path / "raw" / "readwise"
    raw_dir.mkdir(parents=True)
    (raw_dir / "raw-only-01raw.html").write_text("<html></html>", encoding="utf-8")
    (raw_dir / "raw-only-01raw.md").write_text("body", encoding="utf-8")
    index_path = tmp_path / "state" / "readwise_library.json"
    index_path.parent.mkdir()
    index_path.write_text(
        json.dumps(
            {
                "version": 1,
                "last_updated_after": "2026-07-01T00:00:00+00:00",
                "documents": {
                    "01missing": {
                        "html_path": "raw/readwise/missing-01missing.html",
                        "md_path": "raw/readwise/missing-01missing.md",
                        "source_url": None,
                        "updated_at": None,
                        "content_sha256": None,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    status, warnings = collect_readwise_index_status(raw_dir=raw_dir, index_path=index_path)

    assert status is not None
    assert status.raw_exports_not_in_index == 1
    assert status.index_entries_missing_raw == 1
    assert any("raw export pairs are not in the index" in item for item in warnings)
    assert any("index entries are missing raw files" in item for item in warnings)


def test_collect_review_status_counts_finished_and_in_progress(tmp_path: Path) -> None:
    """Review artifacts should split finished and in-progress counts."""
    reviews_dir = tmp_path / "reviews"
    finished_dir = reviews_dir / "finished-source"
    in_progress_dir = reviews_dir / "pending-source"
    finished_dir.mkdir(parents=True)
    in_progress_dir.mkdir(parents=True)
    (finished_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-05-01T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    (in_progress_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": None}}),
        encoding="utf-8",
    )

    status = collect_review_status(reviews_dir)

    assert status.artifacts == 2
    assert status.finished == 1
    assert status.in_progress == 1
    assert status.malformed == 0


def test_collect_review_status_counts_malformed_json(tmp_path: Path) -> None:
    """Malformed review JSON should increment the malformed counter."""
    reviews_dir = tmp_path / "reviews"
    broken_dir = reviews_dir / "broken"
    broken_dir.mkdir(parents=True)
    (broken_dir / "review.json").write_text("{not-json", encoding="utf-8")

    status = collect_review_status(reviews_dir)

    assert status.artifacts == 1
    assert status.malformed == 1
    assert status.finished == 0
    assert status.in_progress == 0


def test_collect_render_status_reads_graph_counts(tmp_path: Path) -> None:
    """Render status should expose graph source and knowledge-page counts."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps({"sources": [{"source_id": "a"}], "knowledge_pages": [{}, {}]}),
        encoding="utf-8",
    )

    status = collect_render_status(
        wiki_dir=tmp_path / "wiki",
        graph_path=graph_path,
        manifest_path=tmp_path / "manifest.json",
    )

    assert status.graph_exists is True
    assert status.manifest_exists is False
    assert status.wiki_dir_exists is False
    assert status.graph_sources == 1
    assert status.graph_knowledge_pages == 2


def test_collect_render_status_handles_missing_graph(tmp_path: Path) -> None:
    """Missing graph files should report null graph counts."""
    status = collect_render_status(
        wiki_dir=tmp_path / "wiki",
        graph_path=tmp_path / "missing-graph.json",
        manifest_path=tmp_path / "missing-manifest.json",
    )

    assert status.graph_exists is False
    assert status.graph_sources is None
    assert status.graph_knowledge_pages is None


def test_classify_uncommitted_paths_groups_artifact_classes(tmp_path: Path) -> None:
    """Git paths should classify durable, preview, run, backup, and other artifacts."""
    repo_root = tmp_path
    paths = [
        "state/synthesis/topic/example.json",
        "state/synthesis_previews/topic/example.md",
        "state/synthesis_runs/20260710T120000Z.json",
        "state/synthesis_backups/refresh/topic/example.json",
        "docs/spec.md",
        "wiki/topics/example.md",
    ]

    counts = classify_uncommitted_paths(repo_root, paths)

    assert counts["durable"] == 2
    assert counts["synthesis_cache"] == 1
    assert counts["render_outputs"] == 1
    assert counts["previews"] == 1
    assert counts["runs"] == 1
    assert counts["backups"] == 1
    assert counts["other"] == 1


def test_classify_uncommitted_paths_handles_untracked_directories(tmp_path: Path) -> None:
    """Untracked directory porcelain paths should classify after path normalization."""
    (tmp_path / "state" / "synthesis_backups").mkdir(parents=True)
    (tmp_path / "state" / "synthesis_previews" / "model").mkdir(parents=True)
    (tmp_path / "state" / "synthesis_runs").mkdir(parents=True)
    paths = [
        "state/synthesis_backups/",
        "state/synthesis_previews/model/",
        "state/synthesis_runs/",
    ]

    counts = classify_uncommitted_paths(tmp_path, paths)

    assert counts["backups"] == 1
    assert counts["previews"] == 1
    assert counts["runs"] == 1
    assert counts["other"] == 0


def test_parse_git_porcelain_paths_handles_renames() -> None:
    """Porcelain rename lines should use the destination path."""
    lines = ["R  old/path.md -> new/path.md", "?? state/synthesis/topic/new.json"]

    paths = parse_git_porcelain_paths(lines)

    assert paths == ["new/path.md", "state/synthesis/topic/new.json"]


def test_collect_ops_status_includes_recommendations_and_json_keys(tmp_path: Path) -> None:
    """Full status collection should include recommendations and stable JSON keys."""
    config = _minimal_config(tmp_path)
    config.raw_dir.mkdir(parents=True)
    config.reviews_dir.mkdir(parents=True)
    config.wiki_dir.mkdir()
    config.synthesis_cache_dir.mkdir(parents=True)
    (config.raw_dir / "source.html").write_text("<html></html>", encoding="utf-8")
    (config.raw_dir / "source.md").write_text("body", encoding="utf-8")
    review_dir = config.reviews_dir / "source"
    review_dir.mkdir()
    (review_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-05-01T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    graph = {
        "sources": [{"source_id": "source"}],
        "knowledge_pages": [
            {
                "entity_id": "topic:example",
                "category": "topic",
                "slug": "example",
                "title": "Example",
                "path": "topics/example.md",
                "aliases": [],
                "tags": ["ai-engineering"],
                "types": [],
                "source_ids": ["source-a", "source-b"],
                "source_count": 2,
                "evidence_count": 1,
                "value_level": "high",
                "confidence": 0.9,
                "evidence": [
                    {
                        "evidence_id": "evidence-a",
                        "text": "Example evidence.",
                        "source_id": "source-a",
                        "field": "knowledge_summary",
                        "stance": "supporting",
                    }
                ],
            }
        ],
    }
    config.graph_path.write_text(json.dumps(graph), encoding="utf-8")
    config.manifest_path.write_text("{}", encoding="utf-8")
    page = graph["knowledge_pages"][0]
    atomic_write_json(
        cache_file_path(config.synthesis_cache_dir, category="topic", slug="example"),
        _cache_entry(page, synthesis_input_hash(page)),
    )
    porcelain = ["?? state/synthesis_previews/topic/example.md"]

    status = collect_ops_status(config, porcelain_lines=porcelain)
    payload = status.to_dict()

    assert "sources" in payload
    assert "readwise_index" in payload
    assert "source_access" in payload
    assert "reviews" in payload
    assert "render" in payload
    assert "synthesis" in payload
    assert "artifacts" in payload
    assert "pipeline" in payload
    assert "vault_hygiene" in payload
    assert status.vault_hygiene is not None
    assert "recommendations" in payload
    assert status.recommendations
    assert status.artifacts.uncommitted_previews == 1


def test_collect_review_workflow_status_counts_all_buckets(tmp_path: Path) -> None:
    """Workflow counts should include not started and skipped raw export pairs."""
    raw_dir = tmp_path / "raw"
    reviews_dir = tmp_path / "reviews"
    raw_dir.mkdir()
    reviews_dir.mkdir()
    for stem in ("finished", "pending", "new", "skipped"):
        (raw_dir / f"{stem}.html").write_text("<html></html>", encoding="utf-8")
        (raw_dir / f"{stem}.md").write_text("body", encoding="utf-8")
    finished_dir = reviews_dir / "finished"
    pending_dir = reviews_dir / "pending"
    finished_dir.mkdir()
    pending_dir.mkdir()
    (finished_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": "2026-05-01T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    (pending_dir / "review.json").write_text(
        json.dumps({"review_analytics": {"review_finished_at": None}}),
        encoding="utf-8",
    )
    (reviews_dir / "skipped_sources.json").write_text(
        json.dumps({"sources": {"skipped": {"skipped_at": "2026-05-01T00:00:00+00:00"}}}),
        encoding="utf-8",
    )

    status = collect_review_workflow_status(raw_dir=raw_dir, reviews_dir=reviews_dir)

    assert status.raw_total == 4
    assert status.finished == 1
    assert status.in_progress == 1
    assert status.not_started == 1
    assert status.skipped == 1


def test_collect_pipeline_alignment_status_flags_reviews_not_in_graph(
    tmp_path: Path,
) -> None:
    """Pipeline alignment should explain when review artifacts outpace the render snapshot."""
    raw_dir = tmp_path / "raw"
    reviews_dir = tmp_path / "reviews"
    graph_path = tmp_path / "graph.json"
    raw_dir.mkdir()
    reviews_dir.mkdir()
    for stem in ("in-graph", "missing-from-graph"):
        (raw_dir / f"{stem}.html").write_text("<html></html>", encoding="utf-8")
        (raw_dir / f"{stem}.md").write_text("body", encoding="utf-8")
        review_dir = reviews_dir / stem
        review_dir.mkdir()
        finished_at = "2026-05-01T00:00:00+00:00" if stem == "in-graph" else None
        (review_dir / "review.json").write_text(
            json.dumps({"review_analytics": {"review_finished_at": finished_at}}),
            encoding="utf-8",
        )
    graph_path.write_text(
        json.dumps({"sources": [{"source_id": "in-graph"}]}),
        encoding="utf-8",
    )

    pipeline, warnings = collect_pipeline_alignment_status(
        raw_dir=raw_dir,
        reviews_dir=reviews_dir,
        graph_path=graph_path,
        source_pages=1,
    )

    assert pipeline.review_artifacts == 2
    assert pipeline.graph_sources == 1
    assert pipeline.reviews_not_in_graph == 0
    assert pipeline.finished_not_in_graph == 0
    assert pipeline.in_progress_excluded_from_render == 1
    assert pipeline.in_progress_in_graph == 0
    assert pipeline.render_stale is False


def test_build_recommendations_suggest_render_when_reviews_not_in_graph() -> None:
    """Stale render snapshots should recommend a render dry-run with the gap count."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(2, 1, 1, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            0,
            0,
            0,
            0,
            0,
            SynthesisPlanStatus(0, 0, 0, 0, 0),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
        pipeline=PipelineAlignmentStatus(
            raw_export_pairs=2,
            workflow=ReviewWorkflowStatus(2, 0, 1, 1, 0),
            review_artifacts=2,
            graph_sources=1,
            source_pages=1,
            reviews_not_in_graph=1,
            finished_not_in_graph=1,
            in_progress_in_graph=0,
            graph_sources_without_review=0,
            in_progress_excluded_from_render=0,
            source_pages_vs_graph_delta=0,
            render_stale=True,
            render_stale_reason="1 finished source(s) are not in the last render snapshot.",
        ),
    )

    recommendations = build_recommendations(status)

    assert (
        recommendations[0] == "Run wiki-render --dry-run: 1 finished source(s) are not in the "
        "last render snapshot yet."
    )


def test_format_text_report_includes_pipeline_alignment_section() -> None:
    """The text report should explain how raw, review, and render buckets relate."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(4, 4, 4, 0),
        reviews=ReviewStatus(2, 1, 1, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            0,
            None,
            None,
            None,
            None,
            SynthesisPlanStatus(None, None, None, None, None),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
        pipeline=PipelineAlignmentStatus(
            raw_export_pairs=4,
            workflow=ReviewWorkflowStatus(4, 1, 1, 1, 1),
            review_artifacts=2,
            graph_sources=1,
            source_pages=1,
            reviews_not_in_graph=0,
            finished_not_in_graph=0,
            in_progress_in_graph=0,
            graph_sources_without_review=0,
            in_progress_excluded_from_render=1,
            source_pages_vs_graph_delta=0,
            render_stale=False,
            render_stale_reason=None,
        ),
    )

    report = format_text_report(status)

    assert "How to read this report" in report
    assert "Pipeline alignment" in report
    assert "1 finished, 1 in progress, 1 not started, 1 skipped (of 4 total)" in report
    assert "- in-progress sources excluded from finished-only render: 1" in report
    assert "see Pipeline alignment for not started/skipped." in report


def test_build_recommendations_suggest_render_when_graph_missing() -> None:
    """Missing graph state should recommend running wiki-render."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(False, False, False, None, None),
        synthesis=SynthesisStatus(
            0,
            None,
            None,
            None,
            None,
            SynthesisPlanStatus(None, None, None, None, None),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
    )

    recommendations = build_recommendations(status)

    assert recommendations[0] == "Run hatch run wiki-render to create graph state."


def test_build_recommendations_suggest_render_dry_run_after_cache_changes() -> None:
    """Unrendered synthesis cache changes should recommend a render dry-run."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            1,
            1,
            0,
            0,
            0,
            SynthesisPlanStatus(0, 0, 1, 0, 0),
        ),
        artifacts=ArtifactStatus(1, 1, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
    )

    recommendations = build_recommendations(status)

    assert (
        recommendations[0] == "Run hatch run wiki-render --dry-run after synthesis cache changes."
    )
    assert "Render snapshot matches current review artifacts" not in recommendations


def test_build_recommendations_allows_no_render_after_render_outputs_changed() -> None:
    """Cache changes with render output changes should not repeat the dry-run hint."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            1,
            1,
            0,
            0,
            0,
            SynthesisPlanStatus(0, 0, 1, 0, 0),
        ),
        artifacts=ArtifactStatus(2, 1, 1, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
    )

    recommendations = build_recommendations(status)

    assert (
        recommendations[0]
        == "Render snapshot matches current review artifacts; no full render required."
    )


def test_build_recommendations_warn_about_uncommitted_other() -> None:
    """Uncommitted docs/code should produce an explicit recommendation."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            0,
            0,
            0,
            0,
            0,
            SynthesisPlanStatus(0, 0, 0, 0, 0),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 3),
        recommendations=[],
        warnings=[],
    )

    recommendations = build_recommendations(status)

    assert "Review uncommitted docs and code files before continuing." in recommendations


def test_build_recommendations_skip_temporary_message_when_other_uncommitted() -> None:
    """Temporary-only guidance should not appear when docs/code are also uncommitted."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            0,
            0,
            0,
            0,
            0,
            SynthesisPlanStatus(0, 0, 0, 0, 0),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 2, 0, 0, False, 1),
        recommendations=[],
        warnings=[],
    )

    recommendations = build_recommendations(status)

    assert not any(
        "preview/run/backup artifacts can remain local" in item for item in recommendations
    )
    assert "Review uncommitted docs and code files before continuing." in recommendations


def test_format_text_report_shows_other_and_backup_counts() -> None:
    """The text report should expose other and backup uncommitted counts."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(False, False, False, None, None),
        synthesis=SynthesisStatus(
            0,
            None,
            None,
            None,
            None,
            SynthesisPlanStatus(None, None, None, None, None),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 1, 2, 3, True, 7),
        recommendations=[],
        warnings=[],
    )

    report = format_text_report(status)

    assert "- uncommitted backup files: 3" in report
    assert "- uncommitted other files: 7" in report


def test_format_text_report_shows_vault_hygiene_section() -> None:
    """The text report should expose vault hygiene counts."""
    from src.wiki_lint.vault_hygiene import VaultHygieneStatus
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(0, 0, 0, 0),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(True, True, True, 1, 1),
        synthesis=SynthesisStatus(
            0,
            None,
            None,
            None,
            None,
            SynthesisPlanStatus(None, None, None, None, None),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
        vault_hygiene=VaultHygieneStatus(
            manifest_exists=True,
            manifest_paths=10,
            vault_markdown_files=12,
            orphan_total=2,
            safe_delete_candidates=(),
            protected_in_progress=(),
            manual_review=(),
            manual_root_items=(),
            duplicate_groups=(),
            recommended_actions=("No vault hygiene action required.",),
        ),
    )

    report = format_text_report(status)

    assert "Vault Hygiene" in report
    assert "- orphan generated pages: 2" in report


def test_format_text_report_shows_readwise_index_section() -> None:
    """The text report should expose Readwise index health."""
    from src.wiki_ops.status import (
        ArtifactStatus,
        OpsStatus,
        ReadwiseIndexStatus,
        RenderStatus,
        ReviewStatus,
        SourceStatus,
        SynthesisPlanStatus,
        SynthesisStatus,
    )

    status = OpsStatus(
        sources=SourceStatus(1, 1, 1, 0),
        readwise_index=ReadwiseIndexStatus(
            path="/tmp/readwise_library.json",
            exists=True,
            documents=1,
            suppressed_ids=2,
            watermark_present=True,
            raw_exports_not_in_index=0,
            index_entries_missing_raw=0,
            malformed=False,
        ),
        reviews=ReviewStatus(0, 0, 0, 0),
        render=RenderStatus(False, False, False, None, None),
        synthesis=SynthesisStatus(
            0,
            None,
            None,
            None,
            None,
            SynthesisPlanStatus(None, None, None, None, None),
        ),
        artifacts=ArtifactStatus(0, 0, 0, 0, 0, 0, False, 0),
        recommendations=[],
        warnings=[],
    )

    report = format_text_report(status)

    assert "Readwise Index" in report
    assert "- documents: 1" in report
    assert "- suppressed ids: 2" in report


def _cache_entry(page: dict[str, Any], input_hash: str) -> dict[str, Any]:
    """Return a complete minimal cache entry for status tests."""
    return {
        "entity_id": page["entity_id"],
        "category": page["category"],
        "slug": page["slug"],
        "title": page["title"],
        "synthesis_input_hash": input_hash,
        "executive_synthesis": "Example synthesis.",
        "what_to_remember": ["Remember this."],
        "consensus": ["Shared claim."],
        "tensions": ["Open tension."],
        "evidence_quality": ["Two supporting sources."],
        "practical_takeaway": "Apply carefully.",
    }


def _minimal_config(tmp_path: Path) -> OpsStatusConfig:
    """Return a minimal ops status config rooted in a temp directory."""
    config = default_config(tmp_path)
    return OpsStatusConfig(
        repo_root=config.repo_root,
        raw_dir=tmp_path / "raw" / "readwise",
        reviews_dir=tmp_path / "state" / "reviews",
        wiki_dir=tmp_path / "wiki",
        graph_path=tmp_path / "state" / "wiki_render_graph.json",
        manifest_path=tmp_path / "state" / "wiki_render_manifest.json",
        synthesis_cache_dir=tmp_path / "state" / "synthesis",
        preview_dir=tmp_path / "state" / "synthesis_previews",
        run_dir=tmp_path / "state" / "synthesis_runs",
        backup_dir=tmp_path / "state" / "synthesis_backups",
    )
