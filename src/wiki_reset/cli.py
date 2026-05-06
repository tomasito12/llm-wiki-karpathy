"""Entry point for ``wiki-reset``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.wiki_reset.reset import (
    CONFIRMATION_PHRASE,
    default_readwise_index_path,
    default_wiki_root,
    run_wiki_reset,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-reset CLI."""
    parser = argparse.ArgumentParser(
        prog="wiki-reset",
        description=(
            "Delete all wiki content except instruction markdown, recreate empty hub shells, "
            "and clear Readwise export index (ingested article tracking)."
        ),
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=default_wiki_root(),
        help="Wiki root directory (default: <repo>/wiki).",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=default_readwise_index_path(),
        help="Readwise library JSON path (default: <repo>/state/readwise_library.json).",
    )
    parser.add_argument(
        "--keep-readwise-index",
        action="store_true",
        help="Do not clear the Readwise export index; only reset wiki files.",
    )
    parser.add_argument(
        "--confirm",
        default=None,
        metavar="PHRASE",
        help=f"Non-interactive confirmation; must be exactly {CONFIRMATION_PHRASE!r}.",
    )
    return parser


def main() -> int:
    """Run CLI; return process exit code."""
    args = build_parser().parse_args()
    phrase = CONFIRMATION_PHRASE

    if args.confirm is not None:
        if args.confirm != phrase:
            print(
                f"Confirmation mismatch: expected {phrase!r}, got {args.confirm!r}.",
                file=sys.stderr,
            )
            return 1
    else:
        print(
            "This will DELETE all wiki pages except the four instruction files, "
            "recreate empty wiki shells, and "
            + (
                "CLEAR the Readwise export index (document list + watermark)."
                if not args.keep_readwise_index
                else "leave the Readwise index unchanged."
            )
        )
        print(f"Type {phrase!r} to confirm, or anything else to abort.")
        if input().strip() != phrase:
            print("Aborted.", file=sys.stderr)
            return 1

    try:
        deleted, index_cleared = run_wiki_reset(
            args.wiki_dir.resolve(),
            args.index.resolve(),
            clear_readwise_index=not args.keep_readwise_index,
        )
    except FileNotFoundError as err:
        print(str(err), file=sys.stderr)
        return 1

    print(f"Removed {len(deleted)} wiki file(s). Readwise index cleared: {index_cleared}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
