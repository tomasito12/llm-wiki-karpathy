"""CLI for deterministic full-regeneration wiki rendering."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.ingest_review.schema import ARTIFACT_SCHEMA_VERSION
from src.wiki_render import TOOL_VERSION
from src.wiki_render.collect import collect_items
from src.wiki_render.graph_export import write_graph_export
from src.wiki_render.loader import load_review_artifacts
from src.wiki_render.merge import build_knowledge_graph
from src.wiki_render.render import render_graph
from src.wiki_render.resolve import taxonomy_version
from src.wiki_render.writer import write_rendered_files

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-render argument parser."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="wiki-render",
        description="Render Obsidian markdown from reviewed ingestion artifacts.",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=root / "state" / "reviews",
        help="Directory containing <source_id>/review.json artifacts.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "wiki",
        help="Wiki output directory.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=root / "state" / "wiki_render_manifest.json",
        help="Advisory generation manifest path.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=root / "state" / "wiki_render_graph.json",
        help="Machine-readable graph export path.",
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
    return parser


def main() -> int:
    """Run a full deterministic wiki regeneration."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    root = repo_root()
    reviews_dir = args.reviews_dir.resolve()
    wiki_dir = args.out_dir.resolve()
    tax_version = taxonomy_version(root)
    artifacts = load_review_artifacts(reviews_dir)
    collected = collect_items(artifacts, wiki_dir)
    graph = build_knowledge_graph(
        collected,
        wiki_dir=wiki_dir,
        taxonomy_version=tax_version,
    )
    rendered = render_graph(graph, wiki_dir=wiki_dir)
    write_graph_export(args.graph_path.resolve(), graph, dry_run=args.dry_run)
    report = write_rendered_files(
        wiki_dir=wiki_dir,
        files=rendered,
        manifest_path=args.manifest_path.resolve(),
        run_metadata={
            "tool_version": TOOL_VERSION,
            "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
            "taxonomy_version": tax_version,
            "source_count": len(graph.sources),
            "knowledge_page_count": len(graph.knowledge_pages),
            "signal_count": len(graph.signals),
            "interview_insight_count": len(graph.insights),
            "implementation_study_count": len(graph.implementation_studies),
            "graph_export_path": str(args.graph_path),
        },
        dry_run=args.dry_run,
        prune=not args.no_prune,
    )
    LOGGER.info(
        "wiki-render complete sources=%d pages=%d files=%d written=%d "
        "unchanged=%d pruned=%d dry_run=%s",
        len(graph.sources),
        len(graph.knowledge_pages),
        report.planned,
        report.written,
        report.unchanged,
        report.pruned,
        args.dry_run,
    )
    if report.skipped_prune and not args.no_prune:
        LOGGER.warning("Prune skipped because no previous manifest was available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
