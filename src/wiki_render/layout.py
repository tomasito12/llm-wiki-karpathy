"""Canonical generated wiki layout."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.pipeline.slug import slugify
from src.wiki_contract.categories import CATEGORY_BY_GRAPH
from src.wiki_contract.layout import (
    FOUNDATION_MODELS,
    GLOSSARY,
    HOW_TO,
    IMPLEMENTATION_STUDIES,
    INDEXES,
    INDUSTRY_TRENDS,
    INTERVIEW_INSIGHTS,
    MANAGED_FOLDERS,
    NOTES,
    SIGNALS,
    SOURCES,
    TOOLS,
    TOPICS,
    is_managed_relative_path,
)

MAX_MONTHLY_BASENAME_LENGTH = 160

CATEGORY_FOLDERS: dict[str, str] = {
    graph_category: spec.folder for graph_category, spec in CATEGORY_BY_GRAPH.items()
}


@dataclass(frozen=True)
class PagePath:
    """A rendered page path with both absolute and repo-relative forms."""

    absolute: Path
    relative: str


def safe_slug(value: str) -> str:
    """Return a filesystem-safe slug for generated page names."""
    return slugify(value)


def month_bucket(date_text: str) -> str:
    """Return ``YYYY-MM`` from a date string, or ``unknown`` when unavailable."""
    text = str(date_text or "").strip()
    if len(text) >= 7 and text[4] == "-":
        return text[:7]
    return "unknown"


def managed_folder_paths(wiki_dir: Path) -> list[Path]:
    """Return absolute paths for all generated top-level folders."""
    return [wiki_dir / folder for folder in MANAGED_FOLDERS]


def page_path(wiki_dir: Path, category: str, slug: str) -> PagePath:
    """Return the generated path for a merged knowledge or source page."""
    folder = CATEGORY_FOLDERS[category]
    file_name = f"{safe_slug(slug)}.md"
    absolute = wiki_dir / folder / file_name
    return PagePath(absolute=absolute, relative=f"{folder}/{file_name}")


def monthly_item_path(
    wiki_dir: Path,
    category: str,
    *,
    source_id: str,
    slug: str,
    date_text: str,
) -> PagePath:
    """Return the generated path for a signal or interview insight page."""
    folder = CATEGORY_FOLDERS[category]
    month = month_bucket(date_text)
    base_name = _compact_monthly_basename(safe_slug(source_id), safe_slug(slug))
    file_name = f"{base_name}.md"
    absolute = wiki_dir / folder / month / file_name
    return PagePath(absolute=absolute, relative=f"{folder}/{month}/{file_name}")


def index_path(wiki_dir: Path, name: str) -> PagePath:
    """Return the generated path for an index page."""
    file_name = f"{safe_slug(name)}.md"
    absolute = wiki_dir / INDEXES / file_name
    return PagePath(absolute=absolute, relative=f"{INDEXES}/{file_name}")


def wikilink(relative_path: str, label: str | None = None) -> str:
    """Return an Obsidian wikilink for a generated relative markdown path."""
    target = relative_path.removesuffix(".md")
    if label:
        return f"[[{target}|{label}]]"
    return f"[[{target}]]"


def _compact_monthly_basename(source_slug: str, item_slug: str) -> str:
    """Return a collision-resistant basename that respects filesystem limits."""
    full = f"{source_slug}-{item_slug}"
    if len(full) <= MAX_MONTHLY_BASENAME_LENGTH:
        return full
    digest = hashlib.sha256(full.encode("utf-8")).hexdigest()[:10]
    source_part = source_slug[:80].rstrip("-")
    remaining = MAX_MONTHLY_BASENAME_LENGTH - len(source_part) - len(digest) - 2
    item_part = item_slug[: max(24, remaining)].rstrip("-")
    compact = f"{source_part}-{item_part}-{digest}"
    return compact[:MAX_MONTHLY_BASENAME_LENGTH].strip("-")


__all__ = [
    "FOUNDATION_MODELS",
    "GLOSSARY",
    "HOW_TO",
    "IMPLEMENTATION_STUDIES",
    "INDEXES",
    "INDUSTRY_TRENDS",
    "INTERVIEW_INSIGHTS",
    "MANAGED_FOLDERS",
    "NOTES",
    "PagePath",
    "SIGNALS",
    "SOURCES",
    "TOOLS",
    "TOPICS",
    "index_path",
    "is_managed_relative_path",
    "managed_folder_paths",
    "month_bucket",
    "monthly_item_path",
    "page_path",
    "safe_slug",
    "wikilink",
]
