"""Typed response models for the read-only management web API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

ReviewStatus = Literal["pending", "in_progress", "finished", "incomplete"]
QueueStatusFilter = Literal["all", "pending", "in_progress", "finished", "incomplete"]


class HealthResponse(BaseModel):
    """Health response for the management web backend."""

    ok: bool
    service: str
    mode: Literal["readonly"]


class ConfigResponse(BaseModel):
    """Safe resolved path configuration for the private management app."""

    mode: Literal["readonly"]
    paths: dict[str, str]


class EntityCounts(BaseModel):
    """Per-source counts of rendered entity groups."""

    topics: int = 0
    glossary: int = 0
    trends: int = 0


class QueueCounts(BaseModel):
    """Queue counts by read-only review status."""

    total: int = 0
    pending: int = 0
    in_progress: int = 0
    finished: int = 0
    incomplete: int = 0


class QueueItem(BaseModel):
    """One source row in the batch review queue."""

    source_id: str
    title: str
    author: str
    publication: str
    published_date: str
    category: str
    status: ReviewStatus
    stale: bool | None
    tags: list[str]
    entity_counts: EntityCounts
    review_json_path: str
    raw_md_available: bool


class QueueResponse(BaseModel):
    """Paginated queue response for the review workspace."""

    counts: QueueCounts
    items: list[QueueItem]
    limit: int
    offset: int


class SourceMetadata(BaseModel):
    """Display metadata for one Readwise source."""

    title: str
    author: str
    publication: str
    published_date: str
    canonical_url: str
    category: str
    readwise_id: str


class SourcePaths(BaseModel):
    """Resolved local paths associated with one source."""

    raw_html: str
    raw_md: str | None
    review_json: str


class SourceSummary(BaseModel):
    """Human-readable source summary for the review card."""

    short: str
    key_insights: list[str]


class NormalizedEntity(BaseModel):
    """One normalized extracted entity for compact display."""

    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    tags: list[str]
    evidence: str
    raw: dict[str, Any]


class EntityGroups(BaseModel):
    """Entity groups rendered by the first read-only review slice."""

    topics: list[NormalizedEntity]
    glossary: list[NormalizedEntity]
    trends: list[NormalizedEntity]


class DebugPayload(BaseModel):
    """Debug payload hidden by default in the frontend."""

    artifact: dict[str, Any]


class SourceDetailResponse(BaseModel):
    """Normalized detail object for one review source."""

    source_id: str
    status: ReviewStatus
    stale: bool | None
    metadata: SourceMetadata
    paths: SourcePaths
    summary: SourceSummary
    tags: list[str]
    entities: EntityGroups
    debug: DebugPayload


class RawSourceResponse(BaseModel):
    """Raw local Markdown response for on-demand source inspection."""

    source_id: str
    available: bool
    content: str
    path: str | None
