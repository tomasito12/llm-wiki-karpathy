"""CLI entry point for Readwise Reader → ``raw/`` sync."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.readwise.sync import _repo_root, run_sync


def load_dotenv_from_repo() -> None:
    """Load ``.env`` from the repository root if the file exists.

    Does not override variables already set in the process environment.
    """
    env_file = _repo_root() / ".env"
    load_dotenv(env_file)


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for readwise sync."""
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="readwise-sync",
        description="Export Readwise Reader archive documents tagged 'processed' to raw/readwise/",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=root / "state" / "readwise_library.json",
        help="Path to read/write export index JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "raw" / "readwise",
        help="Directory for paired .html and .md exports.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=root,
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
    return parser


def main() -> int:
    """Run sync from CLI arguments and environment."""
    load_dotenv_from_repo()
    parser = build_parser()
    args = parser.parse_args()
    token = os.environ.get("READWISE_TOKEN") or os.environ.get("READWISE_API_TOKEN")
    if not token or not token.strip():
        print(
            "Missing READWISE_TOKEN (or READWISE_API_TOKEN). "
            "Set it to your token from https://readwise.io/access_token",
            file=sys.stderr,
        )
        return 1
    result = run_sync(
        token.strip(),
        index_path=args.index,
        output_dir=args.output_dir,
        repo_root=args.repo_root,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
