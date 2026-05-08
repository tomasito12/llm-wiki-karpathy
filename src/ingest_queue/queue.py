"""Derive pending vs ingested Readwise exports from filesystem layout."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

IngestStatus = Literal["pending", "ingested", "incomplete"]


@dataclass(frozen=True)
class IngestItem:
    """One raw HTML export and its ingest status relative to ``wiki/sources``."""

    basename: str
    raw_html_path: Path
    raw_md_path: Path | None
    wiki_source_path: Path
    status: IngestStatus


def list_ingest_items(raw_dir: Path, wiki_sources_dir: Path) -> list[IngestItem]:
    """Pair each ``*.html`` under ``raw_dir`` with wiki ingest state.

    ``incomplete`` means the sibling ``.md`` sidecar is missing.
    """
    items: list[IngestItem] = []
    for html_path in sorted(raw_dir.glob("*.html")):
        stem = html_path.stem
        md_path = html_path.with_suffix(".md")
        wiki_path = wiki_sources_dir / f"{stem}.md"
        if not md_path.is_file():
            items.append(
                IngestItem(
                    basename=stem,
                    raw_html_path=html_path,
                    raw_md_path=None,
                    wiki_source_path=wiki_path,
                    status="incomplete",
                )
            )
            continue
        status: IngestStatus = "ingested" if wiki_path.is_file() else "pending"
        items.append(
            IngestItem(
                basename=stem,
                raw_html_path=html_path,
                raw_md_path=md_path,
                wiki_source_path=wiki_path,
                status=status,
            )
        )
    return items
