"""CLI for listing ingest queue items."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from src.readwise.sync import _repo_root
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError

from .queue import IngestItem, IngestStatus, list_ingest_items

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for ingest-queue."""
    parser = argparse.ArgumentParser(
        prog="ingest-queue",
        description="List raw/readwise exports vs state/reviews review status.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Readwise export directory (default: configured raw_dir).",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=None,
        help="Review artifacts directory (default: configured reviews_dir).",
    )
    parser.add_argument(
        "--status",
        choices=["pending", "reviewed", "incomplete", "all"],
        default="pending",
        help="Filter by review status (default: pending).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Max rows to print after filtering.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of a text table.",
    )
    return parser


def _item_to_dict(item: IngestItem, *, repo_root: Path) -> dict[str, object]:
    """Serialize one item for JSON output (repo-relative paths when possible)."""

    def rel(p: Path | None) -> str | None:
        if p is None:
            return None
        try:
            return p.resolve().relative_to(repo_root).as_posix()
        except ValueError:
            return p.resolve().as_posix()

    return {
        "status": item.status,
        "basename": item.basename,
        "raw_html_path": rel(item.raw_html_path),
        "raw_md_path": rel(item.raw_md_path),
        "review_json_path": rel(item.review_json_path),
    }


def main(argv: list[str] | None = None) -> int:
    """Run ingest-queue from CLI arguments."""
    args = build_parser().parse_args(argv)
    repo = _repo_root().resolve()
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    raw_dir = resolve_cli_path(args.raw_dir, configured=paths.raw_dir).resolve()
    reviews_dir = resolve_cli_path(args.reviews_dir, configured=paths.reviews_dir).resolve()
    if not raw_dir.is_dir():
        print(f"raw-dir is not a directory: {raw_dir}", file=sys.stderr)
        return 1
    reviews_dir.mkdir(parents=True, exist_ok=True)

    items = list_ingest_items(raw_dir, reviews_dir)
    filter_status: IngestStatus | None = None if args.status == "all" else args.status
    if filter_status is not None:
        items = [i for i in items if i.status == filter_status]

    if args.limit is not None:
        items = items[: max(args.limit, 0)]

    if args.json:
        payload = [_item_to_dict(i, repo_root=repo) for i in items]
        print(json.dumps(payload, indent=2))
        return 0

    print(f"{'status':<12} {'basename':<40} review_json")
    for item in items:
        review_display = (
            str(item.review_json_path)
            if item.review_json_path.is_file()
            else "(missing review.json)"
        )
        basename = item.basename
        if len(basename) > 40:
            basename = basename[:37] + "..."
        print(f"{item.status:<12} {basename:<40} {review_display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
