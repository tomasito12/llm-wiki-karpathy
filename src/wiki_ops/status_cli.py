"""CLI for read-only wiki operations status."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_ops.status import (
    OpsStatusConfig,
    collect_ops_status,
    format_text_report,
)
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-ops-status argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-ops-status",
        description="Summarize wiki source, review, render, synthesis, and artifact state.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: detected repo root).",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing Readwise raw exports.",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=None,
        help="Directory containing review artifacts.",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=None,
        help="Generated Obsidian wiki directory.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=None,
        help="Path to the wiki-render manifest.",
    )
    parser.add_argument(
        "--synthesis-cache-dir",
        type=Path,
        default=None,
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis preview markdown files.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis run audit reports.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis backup artifacts.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the status report as JSON.",
    )
    parser.add_argument(
        "--paths-json",
        action="store_true",
        help="Print resolved wiki path configuration as JSON and exit.",
    )
    return parser


def config_from_args(args: argparse.Namespace) -> OpsStatusConfig:
    """Build status config from parsed CLI arguments."""
    repo = (args.repo_root or repo_root()).resolve()
    paths = load_paths_for_cli(args, repo_root_override=repo)
    return OpsStatusConfig(
        repo_root=repo,
        raw_dir=resolve_cli_path(args.raw_dir, configured=paths.raw_dir),
        reviews_dir=resolve_cli_path(args.reviews_dir, configured=paths.reviews_dir),
        wiki_dir=resolve_cli_path(args.wiki_dir, configured=paths.wiki_dir),
        graph_path=resolve_cli_path(args.graph_path, configured=paths.graph_path),
        manifest_path=resolve_cli_path(args.manifest_path, configured=paths.manifest_path),
        synthesis_cache_dir=resolve_cli_path(
            args.synthesis_cache_dir,
            configured=paths.synthesis_dir,
        ),
        preview_dir=resolve_cli_path(args.preview_dir, configured=paths.preview_dir),
        run_dir=resolve_cli_path(args.run_dir, configured=paths.run_dir),
        backup_dir=resolve_cli_path(args.backup_dir, configured=paths.backup_dir),
    )


def main(argv: list[str] | None = None) -> int:
    """Collect and print wiki operations status."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    repo = (args.repo_root or repo_root()).resolve()
    try:
        paths = load_paths_for_cli(args, repo_root_override=repo)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    if args.paths_json:
        print(json.dumps(paths.to_dict(), indent=2, sort_keys=True))
        return 0
    config = config_from_args(args)
    status = collect_ops_status(config)
    if args.json:
        print(json.dumps(status.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_text_report(status))
    LOGGER.info("wiki-ops-status complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
