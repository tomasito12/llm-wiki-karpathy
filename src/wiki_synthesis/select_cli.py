"""CLI for deterministic Stage 2 synthesis candidate selection."""

from __future__ import annotations

import argparse
import json
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
from src.wiki_synthesis.planner import load_graph_export
from src.wiki_synthesis.selection import (
    DEFAULT_SELECT_LIMIT,
    format_selection_text,
    format_workflow_commands,
    select_synthesis_candidates,
)

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-select argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-select",
        description="Rank changed Stage 2 synthesis candidates without LLM calls.",
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
        "--category",
        default=None,
        help="Only select one graph category, for example topic or glossary.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Only select one entity id, for example topic:provenance-tracking.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_SELECT_LIMIT,
        help="Maximum number of ranked candidates to show.",
    )
    parser.add_argument(
        "--include-single-source",
        action="store_true",
        help="Include single-source knowledge pages in selection.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the selection result as JSON.",
    )
    parser.add_argument(
        "--commands",
        action="store_true",
        help="Print copy-pasteable wiki-synthesis-workflow commands.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Select ranked Stage 2 synthesis candidates."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    graph_path = resolve_cli_path(args.graph_path, configured=paths.graph_path)
    cache_dir = resolve_cli_path(args.cache_dir, configured=paths.synthesis_dir)
    reviews_dir = resolve_cli_path(None, configured=paths.reviews_dir)
    graph = load_graph_export(graph_path)
    result = select_synthesis_candidates(
        graph,
        cache_dir=cache_dir,
        category=args.category,
        entity=args.entity,
        include_single_source=args.include_single_source,
        limit=args.limit,
        finished_source_ids=finished_source_ids(reviews_dir),
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    elif args.commands:
        print(format_workflow_commands(result.entries))
    else:
        print(format_selection_text(result))
    LOGGER.info(
        "wiki-synthesis-select complete total=%d shown=%d",
        result.total_changed,
        result.shown,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
