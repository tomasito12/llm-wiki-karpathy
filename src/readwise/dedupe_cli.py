"""CLI for near-duplicate cleanup of Readwise exports."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable
from pathlib import Path

from src.readwise.near_duplicates import (
    DEFAULT_THRESHOLD,
    find_duplicate_pairs,
    load_documents,
    run_dedupe,
)
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for readwise dedupe."""
    parser = argparse.ArgumentParser(
        prog="readwise-dedupe",
        description=(
            "Detect near-duplicate Readwise exports in raw/readwise/ and remove "
            "the shorter copy by default."
        ),
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Readwise export directory (default: configured raw_dir).",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Export index JSON path (default: knowledge_root/state/readwise_library.json).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Jaccard similarity threshold (default: {DEFAULT_THRESHOLD:.2f}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report deletions without writing files or updating the index.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for each duplicate pair instead of deleting the shorter copy.",
    )
    return parser


def format_dedupe_summary(result: object) -> str:
    """Return a one-line summary for sync or CLI output."""
    from src.readwise.near_duplicates import DedupeResult

    if not isinstance(result, DedupeResult):
        return ""
    mode = "dry-run" if result.dry_run else "dedupe"
    return (
        f"{mode}: scanned={result.documents_scanned} pairs={result.pairs_found} "
        f"deleted={len(result.deleted)}"
    )


def print_dedupe_details(
    *,
    raw_dir: Path,
    threshold: float,
    result: object,
) -> None:
    """Print duplicate pairs and deletion actions."""
    from src.readwise.near_duplicates import DedupeResult

    if not isinstance(result, DedupeResult):
        return
    if result.pairs_found == 0:
        print(f"No near-duplicates found above threshold {threshold:.2f}")
        return

    docs = load_documents(raw_dir)
    pairs = find_duplicate_pairs(docs, threshold)
    deleted = set(result.deleted)
    print(f"Found {result.pairs_found} near-duplicate pair(s) (threshold >= {threshold:.2f}):")
    for idx, pair in enumerate(pairs, 1):
        print(f"Pair {idx}: similarity = {pair.similarity:.2%}")
        print(f"  [1] {pair.stem_a} ({pair.text_len_a:,} chars)")
        print(f"  [2] {pair.stem_b} ({pair.text_len_b:,} chars)")
        if pair.stem_a in deleted:
            print("  -> would delete [1]" if result.dry_run else "  -> deleted [1]")
        elif pair.stem_b in deleted:
            print("  -> would delete [2]" if result.dry_run else "  -> deleted [2]")
        else:
            print("  -> kept both")
        print()


def run_readwise_dedupe(
    *,
    raw_dir: Path,
    index_path: Path,
    threshold: float = DEFAULT_THRESHOLD,
    dry_run: bool = False,
    interactive: bool = False,
    input_fn: Callable[[str], str] = input,
    verbose: bool = True,
) -> int:
    """Run near-duplicate cleanup and optionally print a summary."""
    raw_dir = raw_dir.resolve()
    index_path = index_path.resolve()
    if not raw_dir.is_dir():
        print(f"raw-dir is not a directory: {raw_dir}", file=sys.stderr)
        return 1

    if verbose:
        print(f"Scanning {raw_dir} for near-duplicates ...")
    result = run_dedupe(
        raw_dir=raw_dir,
        index_path=index_path,
        threshold=threshold,
        dry_run=dry_run,
        interactive=interactive,
        input_fn=input_fn,
    )
    if verbose:
        print(format_dedupe_summary(result))
        if result.deleted:
            action = "Would delete" if result.dry_run else "Deleted"
            for stem in result.deleted:
                print(f"  {action}: {stem}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run dedupe from CLI arguments."""
    args = build_parser().parse_args(argv)
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    default_index = paths.knowledge_root / "state" / "readwise_library.json"
    return run_readwise_dedupe(
        raw_dir=resolve_cli_path(args.raw_dir, configured=paths.raw_dir),
        index_path=resolve_cli_path(args.index, configured=default_index),
        threshold=args.threshold,
        dry_run=args.dry_run,
        interactive=args.interactive,
    )


if __name__ == "__main__":
    raise SystemExit(main())
