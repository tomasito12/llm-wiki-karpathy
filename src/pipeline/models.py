"""Shared data models for the source parsing pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceConfig:
    """Defines a configured upstream content source."""

    name: str
    kind: str
    url: str


@dataclass(frozen=True)
class DiscoveredItem:
    """Represents a discovered candidate article before parsing."""

    item_id: str
    source_name: str
    source_url: str
    url: str
    title: str
    published_at: str | None


@dataclass(frozen=True)
class ParsedDocument:
    """Represents parsed markdown output ready for staging."""

    item: DiscoveredItem
    markdown: str
    author: str | None
    canonical_url: str
    claps: int | None
    author_followers: int | None
    responses: list[str]
