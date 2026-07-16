"""CLI for rendering Stage 2 operational indexes."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.ingest_review.review_scope import finished_source_ids
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError
from src.wiki_synthesis.indexes import (
    DEFAULT_TAG_HUBS,
    render_synthesis_indexes,
    write_synthesis_indexes,
)
from src.wiki_synthesis.planner import load_graph_export, plan_from_graph

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-indexes argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-indexes",
        description="Render Stage 2 operational indexes without making LLM calls.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
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


def main(argv: list[str] | None = None) -> int:
    """Render Stage 2 operational indexes."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    graph_path = resolve_cli_path(args.graph_path, configured=paths.graph_path)
    cache_dir = resolve_cli_path(args.cache_dir, configured=paths.synthesis_dir)
    wiki_dir = resolve_cli_path(args.out_dir, configured=paths.wiki_dir)
    reviews_dir = resolve_cli_path(None, configured=paths.reviews_dir)
    graph = load_graph_export(graph_path)
    plan = plan_from_graph(
        graph,
        cache_dir=cache_dir,
        include_single_source=False,
        changed_only=False,
        finished_source_ids=finished_source_ids(reviews_dir),
    )
    tags = args.tag if args.tag else list(DEFAULT_TAG_HUBS)
    files = render_synthesis_indexes(graph, plan, tags=tags)
    planned, written = write_synthesis_indexes(
        wiki_dir=wiki_dir,
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
    raise SystemExit(main(sys.argv[1:]))
