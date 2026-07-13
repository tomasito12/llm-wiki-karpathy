"""CLI entry point for Readwise Reader → ``raw/`` sync."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.readwise.dedupe_cli import run_readwise_dedupe
from src.readwise.near_duplicates import DEFAULT_THRESHOLD
from src.readwise.sync import _repo_root, run_sync
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def load_dotenv_from_repo() -> None:
    """Load ``.env`` from the repository root if the file exists.

    Does not override variables already set in the process environment.
    """
    env_file = _repo_root() / ".env"
    load_dotenv(env_file)


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for readwise sync."""
    parser = argparse.ArgumentParser(
        prog="readwise-sync",
        description="Export Readwise Reader archive documents tagged 'processed' to raw/readwise/",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Export index JSON path (default: knowledge_root/state/readwise_library.json).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for paired .html and .md exports (default: configured raw_dir).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (used to resolve index paths on disk).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print counts only; do not write files or update the index.",
    )
    parser.add_argument(
        "--prune-missing",
        action="store_true",
        help="Re-export when indexed files are missing from disk.",
    )
    parser.add_argument(
        "--reset-watermark",
        action="store_true",
        help=(
            "Clear last_updated_after in the index before syncing so this run uses the "
            "default ~100-day lookback (document entries are kept)."
        ),
    )
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Skip near-duplicate cleanup after sync (default: remove shorter copies).",
    )
    parser.add_argument(
        "--dedupe-threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Similarity threshold for post-sync dedupe (default: {DEFAULT_THRESHOLD:.2f}).",
    )
    parser.add_argument(
        "--dedupe-interactive",
        action="store_true",
        help="Prompt for each duplicate pair during post-sync dedupe.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run sync from CLI arguments and environment."""
    load_dotenv_from_repo()
    args = build_parser().parse_args(argv)
    repo = (args.repo_root or _repo_root()).resolve()
    try:
        paths = load_paths_for_cli(args, repo_root_override=repo)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    token = os.environ.get("READWISE_TOKEN") or os.environ.get("READWISE_API_TOKEN")
    if not token or not token.strip():
        print(
            "Missing READWISE_TOKEN (or READWISE_API_TOKEN). "
            "Set it to your token from https://readwise.io/access_token",
            file=sys.stderr,
        )
        return 1
    default_index = paths.knowledge_root / "state" / "readwise_library.json"
    index_path = resolve_cli_path(args.index, configured=default_index)
    output_dir = resolve_cli_path(args.output_dir, configured=paths.raw_dir)
    result = run_sync(
        token.strip(),
        index_path=index_path,
        output_dir=output_dir,
        repo_root=repo,
        dry_run=args.dry_run,
        prune_missing=args.prune_missing,
        reset_watermark=args.reset_watermark,
    )
    mode = "dry-run" if result.dry_run else "sync"
    print(f"{mode}: examined={result.examined} exported={result.exported} skipped={result.skipped}")
    if result.examined == 0 and result.incremental_filter_active:
        wm = result.incremental_watermark or "(unknown)"
        print(
            "Note: The Reader API returned no documents for archive + tag 'processed' "
            "with updates after this run's watermark (updatedAfter).\n"
            "Confirm items are archived and tagged in Reader. To ignore the saved "
            "watermark and use the ~100-day default window instead, run again with "
            "--reset-watermark (or set last_updated_after to null in the index JSON).",
            file=sys.stderr,
        )
        print(f"(watermark used: {wm})", file=sys.stderr)

    if not args.no_dedupe and not result.dry_run:
        dedupe_code = run_readwise_dedupe(
            raw_dir=output_dir,
            index_path=index_path,
            threshold=args.dedupe_threshold,
            dry_run=False,
            interactive=args.dedupe_interactive,
            verbose=True,
        )
        if dedupe_code != 0:
            return dedupe_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
