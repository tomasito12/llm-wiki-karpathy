"""Typed response models for the management web API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

ManagementWebMode = Literal["write_enabled"]
MANAGEMENT_WEB_MODE: ManagementWebMode = "write_enabled"
MANAGEMENT_WEB_WRITE_CAPABILITIES: tuple[str, ...] = (
    "review_decision",
    "review_entity_edit",
    "review_finish",
)

ReviewStatus = Literal["pending", "in_progress", "finished", "incomplete"]
QueueStatusFilter = Literal["all", "pending", "in_progress", "finished", "incomplete"]
ManagementReviewStatus = Literal["approved", "needs_attention", "skipped", "reanalyze_requested"]
ManagementDecisionFilter = Literal[
    "not_reviewed",
    "all",
    "approved",
    "needs_attention",
    "skipped",
    "reanalyze_requested",
]
EditableEntityGroup = Literal[
    "topics",
    "glossary",
    "trends",
    "how_to",
    "tools",
    "models",
    "implementation_studies",
    "signals",
    "interview_insights",
]
EntitySection = Literal["wiki_entities", "source_specific_insights"]
RenderMode = Literal["merged", "individual"]


class HealthResponse(BaseModel):
    """Health response for the management web backend."""

    ok: bool
    service: str
    mode: ManagementWebMode
    capabilities: list[str]


class ConfigResponse(BaseModel):
    """Safe resolved path configuration for the private management app."""

    mode: ManagementWebMode
    capabilities: list[str]
    paths: dict[str, str]


class EntityCounts(BaseModel):
    """Per-source counts of rendered entity groups."""

    topics: int = 0
    glossary: int = 0
    trends: int = 0
    how_to: int = 0
    tools: int = 0
    models: int = 0
    implementation_studies: int = 0
    signals: int = 0
    interview_insights: int = 0


class QueueCounts(BaseModel):
    """Queue counts by read-only review status."""

    total: int = 0
    pending: int = 0
    in_progress: int = 0
    finished: int = 0
    incomplete: int = 0


class DecisionCounts(BaseModel):
    """Management decision counts inside the current source-analysis filter."""

    not_reviewed: int = 0
    approved: int = 0
    needs_attention: int = 0
    skipped: int = 0
    reanalyze_requested: int = 0


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
    management_status: ManagementReviewStatus | None = None


class QueueResponse(BaseModel):
    """Paginated queue response for the review workspace."""

    counts: QueueCounts
    decision_counts: DecisionCounts
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


class EntityDetailList(BaseModel):
    """Read-only supporting list values for one entity card."""

    model_config = ConfigDict(extra="forbid")

    label: str
    items: list[str]


class NormalizedEntity(BaseModel):
    """One normalized extracted entity for compact display."""

    model_config = ConfigDict(extra="forbid")

    index: int
    title: str
    description: str
    tags: list[str]
    types: list[str] = []
    evidence: str
    hidden: bool = False
    render_category: str
    render_mode: RenderMode
    detail_lists: list[EntityDetailList] = []
    raw: dict[str, Any]


class NormalizedEntityGroup(BaseModel):
    """One configured entity group with normalized items."""

    model_config = ConfigDict(extra="forbid")

    group: EditableEntityGroup
    label: str
    section: EntitySection
    items: list[NormalizedEntity]


class EntityGroups(BaseModel):
    """Entity groups rendered in the management review workspace."""

    topics: list[NormalizedEntity]
    glossary: list[NormalizedEntity]
    trends: list[NormalizedEntity]
    groups: list[NormalizedEntityGroup]


class DebugPayload(BaseModel):
    """Debug payload hidden by default in the frontend."""

    artifact: dict[str, Any]


class ManagementReview(BaseModel):
    """Article-level decision state written by the management web UI."""

    status: ManagementReviewStatus
    reviewed_at: str
    reviewed_by: str
    notes: str = ""


class ManagementReviewRequest(BaseModel):
    """Request body for writing an article-level management decision."""

    status: str
    notes: str = ""


class ManagementDecisionResponse(BaseModel):
    """Response returned after writing a management decision."""

    source_id: str
    management_review: ManagementReview
    backup_path: str | None


class EntityEditRequest(BaseModel):
    """Request body for editing a normalized entity card."""

    group: str
    index: int
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    hidden: bool | None = None


class EntityEditResponse(BaseModel):
    """Response returned after a targeted entity edit."""

    source_id: str
    group: EditableEntityGroup
    index: int
    backup_path: str
    source: SourceDetailResponse


class FinishReviewRequest(BaseModel):
    """Request body for finishing the normal successful review workflow."""

    notes: str = ""
    force: bool = False


class FinishReviewResponse(BaseModel):
    """Response returned after finishing a review artifact."""

    source_id: str
    management_review: ManagementReview
    review_finished_at: str
    backup_path: str


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
    management_review: ManagementReview | None
    debug: DebugPayload


class RawSourceResponse(BaseModel):
    """Raw local Markdown response for on-demand source inspection."""

    source_id: str
    available: bool
    content: str
    path: str | None
