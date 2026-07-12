"""CLI for repo-local knowledge and vault data untracking execution."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.wiki_ops.retire_repo_data import (
    DEFAULT_AUDIT_DIR,
    DEFAULT_CHUNK_SIZE,
    RepoDataUntrackingError,
    format_untracking_report_text,
    run_repo_data_untracking,
    untracking_report_to_json,
)
from src.wiki_ops.status import OpsStatusConfig, collect_ops_status
from src.wiki_paths.cli_helpers import add_paths_config_argument, load_paths_for_cli
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-retire-repo-data argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-retire-repo-data",
        description="Plan or execute Git untracking for old repo-local knowledge data.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: detected repo root).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview untracking candidates without modifying Git or .gitignore.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Execute real untracking after validating retirement preconditions.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the untracking report as JSON.",
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=None,
        help=f"Audit report directory override (default: {DEFAULT_AUDIT_DIR}).",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Number of paths per git rm --cached chunk.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Plan or execute repo data untracking."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    if args.yes and args.dry_run:
        LOGGER.error("Cannot combine --dry-run with --yes")
        return 2
    if args.chunk_size <= 0:
        LOGGER.error("--chunk-size must be positive")
        return 2
    if not args.yes and not args.dry_run:
        args.dry_run = True

    repo = (args.repo_root or repo_root()).resolve()
    try:
        paths = load_paths_for_cli(args, repo_root_override=repo)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2

    config = OpsStatusConfig(
        repo_root=repo,
        raw_dir=paths.raw_dir,
        reviews_dir=paths.reviews_dir,
        wiki_dir=paths.wiki_dir,
        graph_path=paths.graph_path,
        manifest_path=paths.manifest_path,
        synthesis_cache_dir=paths.synthesis_dir,
        preview_dir=paths.preview_dir,
        run_dir=paths.run_dir,
        backup_dir=paths.backup_dir,
    )
    ops_status = collect_ops_status(config)
    dry_run = not args.yes

    try:
        report = run_repo_data_untracking(
            paths,
            dry_run=dry_run,
            chunk_size=args.chunk_size,
            audit_dir=args.audit_dir,
            ops_status=ops_status,
        )
    except RepoDataUntrackingError as exc:
        LOGGER.error("%s", exc)
        return 2

    if args.json:
        print(json.dumps(untracking_report_to_json(report), indent=2, sort_keys=True))
    else:
        print(format_untracking_report_text(report))

    if report.readiness == "blocked":
        for reason in report.blocked_reasons:
            LOGGER.error("%s", reason)
        if not dry_run:
            return 2

    LOGGER.info("wiki-retire-repo-data complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
