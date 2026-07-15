"""CLI for deterministic full-regeneration wiki rendering."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.ingest_review.review_scope import in_progress_source_ids
from src.ingest_review.schema import ARTIFACT_SCHEMA_VERSION
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError
from src.wiki_render import TOOL_VERSION
from src.wiki_render.graph_export import write_graph_export
from src.wiki_render.loader import load_review_artifacts
from src.wiki_render.report import (
    RenderRunSummary,
    format_render_summary_text,
    load_previous_render_snapshot,
)
from src.wiki_render.resolve import taxonomy_version
from src.wiki_render.scope import protected_prune_paths_for_in_progress, render_artifacts
from src.wiki_render.source_text import (
    DEFAULT_MIN_SOURCE_TEXT_AVAILABLE_RATIO,
    evaluate_source_text_coverage,
    summarize_source_text_coverage,
)
from src.wiki_render.writer import write_rendered_files

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-render argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-render",
        description="Render Obsidian markdown from reviewed ingestion artifacts.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=None,
        help="Directory containing <source_id>/review.json artifacts.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Wiki output directory.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=None,
        help="Advisory generation manifest path.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Machine-readable graph export path.",
    )
    parser.add_argument(
        "--synthesis-cache-dir",
        type=Path,
        default=None,
        help="Optional Stage 2 synthesis cache directory.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing raw Readwise Markdown exports.",
    )
    parser.add_argument(
        "--include-in-progress",
        action="store_true",
        help=(
            "Also render in-progress review artifacts for vault preview. "
            "Default scope is finished reviews only."
        ),
    )
    parser.add_argument(
        "--show-writes",
        action="store_true",
        help="List every file path that would be written or was written.",
    )
    parser.add_argument(
        "--show-prune",
        action="store_true",
        help="List every file path that would be pruned or was pruned.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and report planned writes without changing files.",
    )
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="Skip stale generated-file deletion.",
    )
    parser.add_argument(
        "--require-source-text",
        action="store_true",
        help=(
            "Fail when too few source pages include full raw text "
            f"(below {DEFAULT_MIN_SOURCE_TEXT_AVAILABLE_RATIO:.0%} coverage)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a full deterministic wiki regeneration."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    root = repo_root()
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    reviews_dir = resolve_cli_path(args.reviews_dir, configured=paths.reviews_dir)
    wiki_dir = resolve_cli_path(args.out_dir, configured=paths.wiki_dir)
    manifest_path = resolve_cli_path(args.manifest_path, configured=paths.manifest_path)
    graph_path = resolve_cli_path(args.graph_path, configured=paths.graph_path)
    synthesis_cache_dir = resolve_cli_path(
        args.synthesis_cache_dir,
        configured=paths.synthesis_dir,
    )
    raw_dir = resolve_cli_path(args.raw_dir, configured=paths.raw_dir)
    if not raw_dir.is_dir():
        LOGGER.warning(
            "raw-dir is not a directory: %s — source full text will likely be unavailable",
            raw_dir,
        )
    tax_version = taxonomy_version(root)
    include_in_progress = bool(args.include_in_progress)
    artifacts = load_review_artifacts(
        reviews_dir,
        include_in_progress=include_in_progress,
    )
    graph, rendered = render_artifacts(
        artifacts,
        wiki_dir=wiki_dir,
        raw_dir=raw_dir,
        repo_root=root,
        synthesis_cache_dir=synthesis_cache_dir,
        taxonomy_version=tax_version,
    )
    protected_paths: set[str] = set()
    excluded_in_progress = 0
    if not include_in_progress:
        excluded_in_progress = len(in_progress_source_ids(reviews_dir))
        if excluded_in_progress:
            protected_paths = protected_prune_paths_for_in_progress(
                reviews_dir=reviews_dir,
                wiki_dir=wiki_dir,
                raw_dir=raw_dir,
                repo_root=root,
                synthesis_cache_dir=synthesis_cache_dir,
                taxonomy_version=tax_version,
            )
    coverage = summarize_source_text_coverage(rendered)
    coverage_warning = evaluate_source_text_coverage(coverage)
    if coverage_warning:
        if args.require_source_text:
            LOGGER.error(coverage_warning)
            return 2
        LOGGER.warning(coverage_warning)
    write_graph_export(graph_path, graph, dry_run=args.dry_run)
    previous = load_previous_render_snapshot(manifest_path)
    report = write_rendered_files(
        wiki_dir=wiki_dir,
        files=rendered,
        manifest_path=manifest_path,
        run_metadata={
            "tool_version": TOOL_VERSION,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "taxonomy_version": tax_version,
            "render_scope": ("include_in_progress" if include_in_progress else "finished_only"),
            "excluded_in_progress_sources": excluded_in_progress,
            "source_count": len(graph.sources),
            "knowledge_page_count": len(graph.knowledge_pages),
            "signal_count": len(graph.signals),
            "interview_insight_count": len(graph.insights),
            "implementation_study_count": len(graph.implementation_studies),
            "graph_export_path": str(graph_path),
            "synthesis_cache_dir": str(synthesis_cache_dir),
        },
        dry_run=args.dry_run,
        prune=not args.no_prune,
        protected_paths=protected_paths,
    )
    LOGGER.info(
        "wiki-render complete scope=%s sources=%d pages=%d files=%d written=%d "
        "unchanged=%d pruned=%d protected=%d dry_run=%s",
        "include_in_progress" if include_in_progress else "finished_only",
        len(graph.sources),
        len(graph.knowledge_pages),
        report.planned,
        report.written,
        report.unchanged,
        report.pruned,
        report.protected_from_prune,
        args.dry_run,
    )
    if coverage.total:
        LOGGER.info(
            "source full text coverage available=%d missing=%d total=%d ratio=%.1f%%",
            coverage.available,
            coverage.missing,
            coverage.total,
            coverage.available_ratio * 100,
        )
    if report.skipped_prune and not args.no_prune:
        LOGGER.warning("Prune skipped because no previous manifest was available")
    if report.protected_from_prune:
        LOGGER.info(
            "protected %d in-progress preview file(s) from prune",
            report.protected_from_prune,
        )
    summary = RenderRunSummary(
        dry_run=args.dry_run,
        source_count=len(graph.sources),
        knowledge_page_count=len(graph.knowledge_pages),
        write_report=report,
        coverage=coverage,
        previous=previous,
        include_in_progress=include_in_progress,
        excluded_in_progress_sources=excluded_in_progress,
    )
    print(
        format_render_summary_text(
            summary,
            show_writes=args.show_writes,
            show_prune=args.show_prune,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
