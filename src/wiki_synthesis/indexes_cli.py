"""CLI for rendering Stage 2 operational indexes."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_synthesis.indexes import (
    DEFAULT_TAG_HUBS,
    render_synthesis_indexes,
    write_synthesis_indexes,
)
from src.wiki_synthesis.planner import load_graph_export, plan_from_graph

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-indexes argument parser."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-indexes",
        description="Render Stage 2 operational indexes without making LLM calls.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=root / "state" / "wiki_render_graph.json",
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=root / "state" / "synthesis",
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "wiki",
        help="Wiki output directory.",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=None,
        help="Render a specific tag hub. May be passed multiple times.",
    )
    parser.add_argument(
        "--all-default-tags",
        action="store_true",
        help="Render the default high-value tag hubs. This is the default when --tag is absent.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute output without writing files.",
    )
    return parser


def main() -> int:
    """Render Stage 2 operational indexes."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    graph = load_graph_export(args.graph_path.resolve())
    plan = plan_from_graph(
        graph,
        cache_dir=args.cache_dir.resolve(),
        include_single_source=False,
        changed_only=False,
    )
    tags = args.tag if args.tag else list(DEFAULT_TAG_HUBS)
    files = render_synthesis_indexes(graph, plan, tags=tags)
    planned, written = write_synthesis_indexes(
        wiki_dir=args.out_dir.resolve(),
        files=files,
        dry_run=args.dry_run,
    )
    LOGGER.info(
        "wiki-synthesis-indexes complete files=%d written=%d dry_run=%s",
        planned,
        written,
        args.dry_run,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
