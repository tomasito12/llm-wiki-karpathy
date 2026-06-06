"""Derive pending vs reviewed Readwise exports from filesystem layout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

IngestStatus = Literal["pending", "reviewed", "incomplete"]


@dataclass(frozen=True)
class IngestItem:
    """One raw HTML export and its review status."""

    basename: str
    raw_html_path: Path
    raw_md_path: Path | None
    review_json_path: Path
    status: IngestStatus


def list_ingest_items(raw_dir: Path, reviews_dir: Path) -> list[IngestItem]:
    """Pair each ``*.html`` under ``raw_dir`` with review artifact state.

    ``incomplete`` means the sibling ``.md`` sidecar is missing.
    ``reviewed`` means ``state/reviews/<basename>/review.json`` exists.
    """
    items: list[IngestItem] = []
    for html_path in sorted(raw_dir.glob("*.html")):
        stem = html_path.stem
        md_path = html_path.with_suffix(".md")
        review_json_path = reviews_dir / stem / "review.json"
        if not md_path.is_file():
            items.append(
                IngestItem(
                    basename=stem,
                    raw_html_path=html_path,
                    raw_md_path=None,
                    review_json_path=review_json_path,
                    status="incomplete",
                )
            )
            continue
        status: IngestStatus = "reviewed" if review_json_path.is_file() else "pending"
        items.append(
            IngestItem(
                basename=stem,
                raw_html_path=html_path,
                raw_md_path=md_path,
                review_json_path=review_json_path,
                status=status,
            )
        )
    return items
