"""CLI for listing ingest queue items."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.readwise.sync import _repo_root

from .queue import IngestItem, IngestStatus, list_ingest_items


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for ingest-queue."""
    root = _repo_root()
    parser = argparse.ArgumentParser(
        prog="ingest-queue",
        description="List raw/readwise exports vs state/reviews review status.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=root / "raw" / "readwise",
        help="Readwise export directory (default: <repo>/raw/readwise).",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=root / "state" / "reviews",
        help="Review artifacts directory (default: <repo>/state/reviews).",
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


def _item_to_dict(item: IngestItem) -> dict[str, object]:
    """Serialize one item for JSON output (repo-relative paths when possible)."""
    root = _repo_root()

    def rel(p: Path | None) -> str | None:
        if p is None:
            return None
        try:
            return p.resolve().relative_to(root).as_posix()
        except ValueError:
            return p.resolve().as_posix()

    return {
        "status": item.status,
        "basename": item.basename,
        "raw_html_path": rel(item.raw_html_path),
        "raw_md_path": rel(item.raw_md_path),
        "review_json_path": rel(item.review_json_path),
    }


def main() -> int:
    """Run ingest-queue from CLI arguments."""
    args = build_parser().parse_args()
    raw_dir = args.raw_dir.resolve()
    reviews_dir = args.reviews_dir.resolve()
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
        payload = [_item_to_dict(i) for i in items]
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
