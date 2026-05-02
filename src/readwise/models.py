"""Typed models for Reader API list responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReaderDocument:
    """Subset of Reader list document fields used by export and sync."""

    id: str
    title: str
    author: str | None
    source_url: str | None
    category: str | None
    location: str | None
    published_date: str | None
    saved_at: str | None
    updated_at: str | None
    summary: str | None
    html_content: str | None
    parent_id: str | None
    tags: dict[str, Any]

    @staticmethod
    def from_api_row(row: dict[str, Any]) -> ReaderDocument:
        """Build a document from one ``results`` entry."""
        tags = row.get("tags")
        if not isinstance(tags, dict):
            tags = {}
        return ReaderDocument(
            id=str(row["id"]),
            title=str(row.get("title") or "Untitled").strip() or "Untitled",
            author=_optional_str(row.get("author")),
            source_url=_optional_str(row.get("source_url")),
            category=_optional_str(row.get("category")),
            location=_optional_str(row.get("location")),
            published_date=_optional_str(row.get("published_date")),
            saved_at=_optional_str(row.get("saved_at")),
            updated_at=_optional_str(row.get("updated_at")),
            summary=_optional_str(row.get("summary")),
            html_content=_optional_str(row.get("html_content")),
            parent_id=_optional_str(row.get("parent_id")),
            tags=tags,
        )


def _optional_str(value: Any) -> str | None:
    """Return stripped text or ``None`` for empty API fields."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None
