"""Read-only loading and normalization for management review artifacts."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast, get_args

from src.ingest_queue.queue import IngestItem, list_ingest_items
from src.management_web.models import (
    DebugPayload,
    DecisionCounts,
    EditableEntityGroup,
    EntityCounts,
    EntityEditRequest,
    EntityEditResponse,
    EntityGroups,
    FinishReviewRequest,
    FinishReviewResponse,
    ManagementDecisionFilter,
    ManagementDecisionResponse,
    ManagementReview,
    ManagementReviewRequest,
    ManagementReviewStatus,
    NormalizedEntity,
    QueueCounts,
    QueueResponse,
    QueueStatusFilter,
    RawSourceResponse,
    ReviewStatus,
    SourceDetailResponse,
    SourceMetadata,
    SourcePaths,
    SourceSummary,
)
from src.pipeline.atomic import atomic_write_json
from src.wiki_paths.config import WikiPaths

_SOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_MANAGEMENT_REVIEW_STATUSES = set(get_args(ManagementReviewStatus))
_ENTITY_GROUP_PATHS: dict[str, tuple[str, str]] = {
    "topics": ("llm_output", "topics"),
    "glossary": ("llm_output", "glossary"),
    "trends": ("llm_output", "industry_trends"),
}
_TITLE_KEYS = {
    "topics": ("topic", "topic_title", "title"),
    "glossary": ("term", "glossary_term", "title"),
    "trends": ("trend", "trend_title", "title"),
}
_DESCRIPTION_KEYS = {
    "topics": (
        "topic_description",
        "knowledge_summary",
        "operational_insight",
        "description",
        "summary",
    ),
    "glossary": (
        "definition",
        "proposed_definition",
        "knowledge_summary",
        "description",
        "summary",
    ),
    "trends": (
        "trend_description",
        "knowledge_summary",
        "operational_insight",
        "description",
        "summary",
    ),
}
_TAG_KEYS = {
    "topics": ("topic_tags", "proposed_tags", "primary_tag", "secondary_tag"),
    "glossary": ("tags", "glossary_tags", "proposed_tags", "primary_tag", "secondary_tag"),
    "trends": ("trend_tags", "proposed_tags", "primary_tag", "secondary_tag"),
}


class FinishConflictError(ValueError):
    """Raised when finishing would overwrite a conflicting management decision."""


def validate_source_id(source_id: str) -> str:
    """Return a safe source ID or raise when it could address arbitrary paths.

    Args:
        source_id: Raw source ID from an API route or caller.

    Returns:
        The validated source ID.

    Raises:
        ValueError: If the source ID contains path separators, extensions, or
            other characters outside the Readwise export stem convention.
    """
    if not _SOURCE_ID_PATTERN.fullmatch(source_id):
        raise ValueError(f"Invalid source_id: {source_id!r}")
    return source_id


def load_review_artifact(path: Path) -> dict[str, Any] | None:
    """Load a review artifact JSON file if present and object-shaped.

    Args:
        path: Expected path to `review.json`.

    Returns:
        The decoded artifact dict, or `None` when the file is missing or invalid.
    """
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def get_management_review(artifact: dict[str, Any] | None) -> ManagementReview | None:
    """Return normalized management review state from an artifact.

    Args:
        artifact: Loaded review artifact, when available.

    Returns:
        Management review state, or `None` when no valid block exists.
    """
    if not isinstance(artifact, dict):
        return None
    raw_review = artifact.get("management_review")
    if not isinstance(raw_review, dict):
        return None
    try:
        return ManagementReview.model_validate(raw_review)
    except ValueError:
        return None


def classify_review_status(item: IngestItem, artifact: dict[str, Any] | None) -> ReviewStatus:
    """Classify one ingest item using the management web status vocabulary.

    Args:
        item: Raw ingest queue item.
        artifact: Loaded review artifact, when available.

    Returns:
        A read-only management web review status.
    """
    if item.status == "incomplete":
        return "incomplete"
    if artifact is None:
        return "pending"
    analytics = artifact.get("review_analytics")
    if isinstance(analytics, dict) and str(analytics.get("review_finished_at") or "").strip():
        return "finished"
    if not _has_analysis_payload(artifact):
        return "pending"
    return "in_progress"


def build_review_queue(
    paths: WikiPaths,
    *,
    status: QueueStatusFilter = "all",
    decision: ManagementDecisionFilter = "not_reviewed",
    limit: int = 50,
    offset: int = 0,
    query: str | None = None,
) -> QueueResponse:
    """Build a filtered, paginated review queue from local raw/review state.

    Args:
        paths: Resolved wiki paths.
        status: Status filter to apply to returned items.
        decision: Management decision filter to apply after status filtering.
        limit: Maximum number of returned items.
        offset: Number of filtered items to skip.
        query: Optional case-insensitive search query.

    Returns:
        Queue response with counts computed before filtering and pagination.
    """
    rows = [
        _queue_item(paths, item) for item in list_ingest_items(paths.raw_dir, paths.reviews_dir)
    ]
    counts = _count_queue_items(rows)
    status_filtered = _filter_queue_items_by_status(rows, status=status)
    decision_counts = _count_decisions(status_filtered)
    filtered = _sort_queue_items(
        _filter_queue_items_by_query(
            _filter_queue_items_by_decision(status_filtered, decision=decision),
            query=query,
        )
    )
    bounded_offset = max(offset, 0)
    bounded_limit = max(limit, 0)
    return QueueResponse(
        counts=counts,
        decision_counts=decision_counts,
        items=filtered[bounded_offset : bounded_offset + bounded_limit],
        limit=bounded_limit,
        offset=bounded_offset,
    )


def get_source_detail(paths: WikiPaths, source_id: str) -> SourceDetailResponse:
    """Return normalized detail data for one source.

    Args:
        paths: Resolved wiki paths.
        source_id: Safe Readwise export stem.

    Returns:
        Normalized source detail response.

    Raises:
        ValueError: If `source_id` is unsafe.
        FileNotFoundError: If no raw HTML export exists for the source.
    """
    safe_source_id = validate_source_id(source_id)
    raw_html_path = paths.raw_dir / f"{safe_source_id}.html"
    if not raw_html_path.is_file():
        raise FileNotFoundError(f"Source not found: {safe_source_id}")
    raw_md_path = raw_html_path.with_suffix(".md")
    review_json_path = paths.reviews_dir / safe_source_id / "review.json"
    item = IngestItem(
        basename=safe_source_id,
        raw_html_path=raw_html_path,
        raw_md_path=raw_md_path if raw_md_path.is_file() else None,
        review_json_path=review_json_path,
        status="incomplete" if not raw_md_path.is_file() else "reviewed",
    )
    artifact = load_review_artifact(review_json_path)
    metadata = extract_source_metadata(safe_source_id, item, artifact)
    entities = normalize_entities(artifact)
    return SourceDetailResponse(
        source_id=safe_source_id,
        status=classify_review_status(item, artifact),
        stale=None,
        metadata=metadata,
        paths=SourcePaths(
            raw_html=str(raw_html_path),
            raw_md=str(raw_md_path) if raw_md_path.is_file() else None,
            review_json=str(review_json_path),
        ),
        summary=normalize_source_summary(artifact),
        tags=collect_tags(artifact),
        entities=entities,
        management_review=get_management_review(artifact),
        debug=DebugPayload(artifact=artifact or {}),
    )


def write_management_decision(
    paths: WikiPaths,
    source_id: str,
    decision: ManagementReviewRequest,
    *,
    reviewed_by: str = "plischke",
) -> ManagementDecisionResponse:
    """Write an article-level management review decision with backup.

    Args:
        paths: Resolved wiki paths.
        source_id: Safe Readwise export stem.
        decision: Requested article-level decision.
        reviewed_by: Operator identifier to store in the decision block.

    Returns:
        Decision response including backup path when an artifact was overwritten.

    Raises:
        ValueError: If `source_id` is unsafe.
        FileNotFoundError: If no matching raw HTML source exists.
    """
    safe_source_id = validate_source_id(source_id)
    raw_html_path = paths.raw_dir / f"{safe_source_id}.html"
    if not raw_html_path.is_file():
        raise FileNotFoundError(f"Source not found: {safe_source_id}")
    if decision.status not in _MANAGEMENT_REVIEW_STATUSES:
        raise ValueError(f"Invalid management review status: {decision.status!r}")
    review_json_path = paths.reviews_dir / safe_source_id / "review.json"
    previous_text = (
        review_json_path.read_text(encoding="utf-8") if review_json_path.is_file() else None
    )
    artifact = load_review_artifact(review_json_path) or {}
    management_review = ManagementReview(
        status=cast("ManagementReviewStatus", decision.status),
        reviewed_at=_utc_timestamp(),
        reviewed_by=reviewed_by,
        notes=decision.notes,
    )
    artifact["management_review"] = management_review.model_dump()
    backup_path: Path | None = None
    if previous_text is not None:
        backup_path = _write_review_backup(
            review_json_path, previous_text, reason="management-review"
        )
    atomic_write_json(review_json_path, artifact)
    return ManagementDecisionResponse(
        source_id=safe_source_id,
        management_review=management_review,
        backup_path=str(backup_path) if backup_path is not None else None,
    )


def update_review_entity(
    paths: WikiPaths,
    source_id: str,
    request: EntityEditRequest,
    *,
    reviewed_by: str = "plischke",
) -> EntityEditResponse:
    """Apply a targeted entity edit to an existing review artifact.

    Args:
        paths: Resolved wiki paths.
        source_id: Safe Readwise export stem.
        request: Target entity and editable fields.
        reviewed_by: Operator identifier to store in hidden state metadata.

    Returns:
        Edit response containing the refreshed source detail.

    Raises:
        ValueError: If the source ID, group, index, or field payload is invalid.
        FileNotFoundError: If raw HTML or review artifact is missing.
    """
    safe_source_id, review_json_path, artifact = _load_existing_review_artifact_for_write(
        paths, source_id
    )
    entity_group = _validate_entity_group(request.group)
    _validate_entity_edit_request(request)
    entities = _artifact_entity_list(artifact, entity_group)
    if request.index < 0 or request.index >= len(entities):
        raise ValueError(f"Entity index out of range: {request.index}")
    entity = entities[request.index]
    if not isinstance(entity, dict):
        raise ValueError(f"Entity at index {request.index} is not editable")
    _apply_entity_edit(entity, request, entity_group, reviewed_by=reviewed_by)
    backup_path = _write_review_artifact_with_backup(
        review_json_path,
        artifact,
        reason="management-edit",
    )
    return EntityEditResponse(
        source_id=safe_source_id,
        group=entity_group,
        index=request.index,
        backup_path=str(backup_path),
        source=get_source_detail(paths, safe_source_id),
    )


def finish_review(
    paths: WikiPaths,
    source_id: str,
    request: FinishReviewRequest,
    *,
    reviewed_by: str = "plischke",
) -> FinishReviewResponse:
    """Finish an analyzed review artifact and approve its management decision.

    Args:
        paths: Resolved wiki paths.
        source_id: Safe Readwise export stem.
        request: Finish request with optional notes and conflict override.
        reviewed_by: Operator identifier to store in management_review.

    Returns:
        Finish response with approval state and backup path.

    Raises:
        ValueError: If finishing is not valid for this artifact.
        FileNotFoundError: If raw HTML or review artifact is missing.
        FinishConflictError: If an existing non-approved decision blocks finish.
    """
    safe_source_id, review_json_path, artifact = _load_existing_review_artifact_for_write(
        paths, source_id
    )
    if not _has_analysis_payload(artifact):
        raise ValueError("Cannot finish review artifact with no analysis payload")
    _ensure_finish_allowed(artifact, force=request.force)
    finished_at = _utc_timestamp()
    analytics = artifact.get("review_analytics")
    if not isinstance(analytics, dict):
        analytics = {}
    analytics["review_finished_at"] = finished_at
    artifact["review_analytics"] = analytics
    management_review = ManagementReview(
        status="approved",
        reviewed_at=finished_at,
        reviewed_by=reviewed_by,
        notes=request.notes,
    )
    artifact["management_review"] = management_review.model_dump()
    backup_path = _write_review_artifact_with_backup(
        review_json_path,
        artifact,
        reason="management-edit",
    )
    return FinishReviewResponse(
        source_id=safe_source_id,
        management_review=management_review,
        review_finished_at=finished_at,
        backup_path=str(backup_path),
    )


def extract_source_metadata(
    source_id: str,
    item: IngestItem,
    artifact: dict[str, Any] | None,
) -> SourceMetadata:
    """Extract display metadata from artifact source fields with safe fallbacks.

    Args:
        source_id: Validated source ID.
        item: Raw ingest queue item.
        artifact: Loaded review artifact, when available.

    Returns:
        Source metadata response model.
    """
    source = _dict_value(artifact, "source")
    return SourceMetadata(
        title=_string_field(source, "title", fallback=source_id),
        author=_string_field(source, "author"),
        publication=_string_field(source, "publication"),
        published_date=_string_field(source, "published_date"),
        canonical_url=_string_field(source, "canonical_url"),
        category=_string_field(source, "category"),
        readwise_id=_string_field(source, "readwise_id"),
    )


def normalize_source_summary(artifact: dict[str, Any] | None) -> SourceSummary:
    """Normalize source summary fields from a review artifact.

    Args:
        artifact: Loaded review artifact, when available.

    Returns:
        Source summary response model.
    """
    llm_output = _dict_value(artifact, "llm_output")
    summary = _dict_value(llm_output, "source_summary")
    raw_insights = summary.get("key_insights") if isinstance(summary, dict) else []
    insights = (
        [str(item).strip() for item in raw_insights if str(item).strip()]
        if isinstance(raw_insights, list)
        else []
    )
    return SourceSummary(
        short=_first_string(summary, ("accessible_overview", "summary")),
        key_insights=insights,
    )


def normalize_entities(artifact: dict[str, Any] | None) -> EntityGroups:
    """Normalize the entity groups rendered in the first review slice.

    Args:
        artifact: Loaded review artifact, when available.

    Returns:
        Entity groups for topics, glossary, and trends.
    """
    llm_output = _dict_value(artifact, "llm_output")
    return EntityGroups(
        topics=_normalize_entity_list(llm_output.get("topics"), kind="topic"),
        glossary=_normalize_entity_list(llm_output.get("glossary"), kind="glossary"),
        trends=_normalize_entity_list(llm_output.get("industry_trends"), kind="trend"),
    )


def collect_tags(artifact: dict[str, Any] | None) -> list[str]:
    """Collect display tags from supported entity groups in a stable order.

    Args:
        artifact: Loaded review artifact, when available.

    Returns:
        Sorted unique tag strings.
    """
    tags: set[str] = set()
    entities = normalize_entities(artifact)
    for group in (entities.topics, entities.glossary, entities.trends):
        for entity in group:
            tags.update(entity.tags)
    return sorted(tags)


def read_raw_markdown(paths: WikiPaths, source_id: str) -> RawSourceResponse:
    """Read local raw Markdown for a source when the sidecar exists.

    Args:
        paths: Resolved wiki paths.
        source_id: Safe Readwise export stem.

    Returns:
        Raw source response; unavailable when the sidecar is missing.

    Raises:
        ValueError: If `source_id` is unsafe.
    """
    safe_source_id = validate_source_id(source_id)
    raw_md_path = paths.raw_dir / f"{safe_source_id}.md"
    if not raw_md_path.is_file():
        return RawSourceResponse(source_id=safe_source_id, available=False, content="", path=None)
    return RawSourceResponse(
        source_id=safe_source_id,
        available=True,
        content=raw_md_path.read_text(encoding="utf-8", errors="replace"),
        path=str(raw_md_path),
    )


def _queue_item(paths: WikiPaths, item: IngestItem):
    """Build one queue response item from an ingest item."""
    from src.management_web.models import QueueItem

    artifact = load_review_artifact(item.review_json_path)
    management_review = get_management_review(artifact)
    metadata = extract_source_metadata(item.basename, item, artifact)
    entities = normalize_entities(artifact)
    return QueueItem(
        source_id=item.basename,
        title=metadata.title,
        author=metadata.author,
        publication=metadata.publication,
        published_date=metadata.published_date,
        category=metadata.category,
        status=classify_review_status(item, artifact),
        stale=None,
        tags=collect_tags(artifact),
        entity_counts=EntityCounts(
            topics=len(entities.topics),
            glossary=len(entities.glossary),
            trends=len(entities.trends),
        ),
        review_json_path=str(item.review_json_path),
        raw_md_available=item.raw_md_path is not None,
        management_status=management_review.status if management_review else None,
    )


def _has_analysis_payload(artifact: dict[str, Any]) -> bool:
    """Return whether an artifact contains pre-analysis output, not only a decision."""
    llm_output = _dict_value(artifact, "llm_output")
    return any(
        key in llm_output for key in ("source_summary", "topics", "glossary", "industry_trends")
    )


def _utc_timestamp() -> str:
    """Return a UTC ISO timestamp with second precision and `Z` suffix."""
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _backup_timestamp() -> str:
    """Return a compact UTC timestamp for backup filenames."""
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def _write_review_backup(review_json_path: Path, text: str, *, reason: str) -> Path:
    """Write a non-overwriting backup for an existing review artifact."""
    timestamp = _backup_timestamp()
    for counter in range(1000):
        suffix = "" if counter == 0 else f".{counter}"
        backup_path = review_json_path.with_name(f"review.before-{reason}.{timestamp}{suffix}.json")
        try:
            with backup_path.open("x", encoding="utf-8") as backup:
                backup.write(text)
                backup.flush()
                os.fsync(backup.fileno())
            return backup_path
        except FileExistsError:
            continue
    raise OSError(f"Could not create unique review backup for {review_json_path}")


def _count_queue_items(items: Iterable[Any]) -> QueueCounts:
    """Count queue items by status."""
    counts = QueueCounts()
    for item in items:
        counts.total += 1
        if item.status == "pending":
            counts.pending += 1
        elif item.status == "in_progress":
            counts.in_progress += 1
        elif item.status == "finished":
            counts.finished += 1
        elif item.status == "incomplete":
            counts.incomplete += 1
    return counts


def _count_decisions(items: Iterable[Any]) -> DecisionCounts:
    """Count management decision states for already status-filtered items."""
    counts = DecisionCounts()
    for item in items:
        if item.management_status is None:
            counts.not_reviewed += 1
        elif item.management_status == "approved":
            counts.approved += 1
        elif item.management_status == "needs_attention":
            counts.needs_attention += 1
        elif item.management_status == "skipped":
            counts.skipped += 1
        elif item.management_status == "reanalyze_requested":
            counts.reanalyze_requested += 1
    return counts


def _filter_queue_items_by_status(
    items: list[Any],
    *,
    status: QueueStatusFilter,
) -> list[Any]:
    """Apply the source-analysis status filter to queue items."""
    return [item for item in items if status == "all" or item.status == status]


def _filter_queue_items_by_decision(
    items: list[Any],
    *,
    decision: ManagementDecisionFilter,
) -> list[Any]:
    """Apply the management decision filter to queue items."""
    if decision == "all":
        return items
    if decision == "not_reviewed":
        return [item for item in items if item.management_status is None]
    return [item for item in items if item.management_status == decision]


def _filter_queue_items_by_query(
    items: list[Any],
    *,
    query: str | None,
) -> list[Any]:
    """Apply the text query filter to queue items."""
    normalized_query = (query or "").strip().lower()
    if not normalized_query:
        return items
    return [item for item in items if _queue_item_matches_query(item, normalized_query)]


def _sort_queue_items(items: list[Any]) -> list[Any]:
    """Sort queue items by oldest publication date first with stable fallbacks."""
    return sorted(
        items,
        key=lambda item: (
            item.published_date or "9999-12-31",
            item.title.lower(),
            item.source_id,
        ),
    )


def _queue_item_matches_query(item: Any, query: str) -> bool:
    """Return whether a queue item matches a normalized search query."""
    haystack = " ".join(
        [
            item.source_id,
            item.title,
            item.author,
            item.publication,
            item.category,
            " ".join(item.tags),
        ]
    ).lower()
    return query in haystack


def _normalize_entity_list(raw_items: Any, *, kind: str) -> list[NormalizedEntity]:
    """Normalize list-like entity payloads into display cards."""
    if not isinstance(raw_items, list):
        return []
    return [_normalize_entity(item, kind=kind, index=index) for index, item in enumerate(raw_items)]


def _normalize_entity(item: Any, *, kind: str, index: int) -> NormalizedEntity:
    """Normalize one entity item, preserving raw fields for debug inspection."""
    if not isinstance(item, dict):
        text = str(item).strip()
        return NormalizedEntity(
            index=index,
            title=text,
            description="",
            tags=[],
            evidence="",
            raw={"value": item},
        )
    title_keys = {
        "topic": ("topic_title", "title", "name"),
        "glossary": ("term", "title", "name"),
        "trend": ("trend_title", "title", "name"),
    }[kind]
    description_keys = {
        "topic": (
            "topic_description",
            "knowledge_summary",
            "operational_insight",
            "description",
            "summary",
        ),
        "glossary": ("definition", "proposed_definition", "description"),
        "trend": (
            "trend_description",
            "operational_insight",
            "knowledge_summary",
            "description",
            "summary",
        ),
    }[kind]
    tag_keys = {
        "topic": ("topic_tags", "proposed_tags", "tags", "primary_tag", "secondary_tag"),
        "glossary": ("tags", "glossary_tags", "proposed_tags", "primary_tag", "secondary_tag"),
        "trend": ("trend_tags", "proposed_tags", "tags", "primary_tag", "secondary_tag"),
    }[kind]
    return NormalizedEntity(
        index=index,
        title=_first_string(item, title_keys),
        description=_first_string(item, description_keys),
        tags=_string_list_from_keys(item, tag_keys),
        evidence=_first_evidence(item),
        raw=item,
    )


def _dict_value(payload: dict[str, Any] | None, key: str) -> dict[str, Any]:
    """Return a nested dict value or an empty dict."""
    if not isinstance(payload, dict):
        return {}
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


def _string_field(payload: dict[str, Any], key: str, *, fallback: str = "") -> str:
    """Return a stripped string field from a dict payload."""
    value = payload.get(key)
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _first_string(payload: dict[str, Any], keys: tuple[str, ...]) -> str:
    """Return the first non-empty string value for candidate keys."""
    for key in keys:
        text = _string_field(payload, key)
        if text:
            return text
    return ""


def _string_list_from_keys(payload: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    """Return unique stripped strings from list or scalar candidate keys."""
    tags: set[str] = set()
    for key in keys:
        raw = payload.get(key)
        if isinstance(raw, list):
            tags.update(str(item).strip() for item in raw if str(item).strip())
        elif raw is not None:
            text = str(raw).strip()
            if text:
                tags.add(text)
    return sorted(tags)


def _first_evidence(payload: dict[str, Any]) -> str:
    """Return the first evidence-like display string from current artifact fields."""
    text = _first_string(
        payload,
        (
            "evidence",
            "supporting_snippet",
            "evidence_from_source",
            "source_phrase",
            "source_quote",
            "supporting_evidence",
        ),
    )
    if text:
        return text
    raw_points = payload.get("supporting_data_points")
    if not isinstance(raw_points, list):
        return ""
    for point in raw_points:
        if isinstance(point, dict):
            point_text = _first_string(
                point,
                ("text", "snippet", "evidence", "point", "summary", "description"),
            )
        else:
            point_text = str(point).strip()
        if point_text:
            return point_text
    return ""


def _load_existing_review_artifact_for_write(
    paths: WikiPaths,
    source_id: str,
) -> tuple[str, Path, dict[str, Any]]:
    """Load an existing artifact for a safe write operation."""
    safe_source_id = validate_source_id(source_id)
    raw_html_path = paths.raw_dir / f"{safe_source_id}.html"
    if not raw_html_path.is_file():
        raise FileNotFoundError(f"Source not found: {safe_source_id}")
    review_json_path = paths.reviews_dir / safe_source_id / "review.json"
    artifact = load_review_artifact(review_json_path)
    if artifact is None:
        raise FileNotFoundError(f"Review artifact not found: {safe_source_id}")
    return safe_source_id, review_json_path, artifact


def _validate_entity_group(group: str) -> EditableEntityGroup:
    """Return a supported editable entity group or raise."""
    if group not in _ENTITY_GROUP_PATHS:
        raise ValueError(f"Invalid entity group: {group!r}")
    return cast("EditableEntityGroup", group)


def _validate_entity_edit_request(request: EntityEditRequest) -> None:
    """Validate that at least one well-formed editable field is present."""
    has_field = any(
        value is not None
        for value in (request.title, request.description, request.tags, request.hidden)
    )
    if not has_field:
        raise ValueError("At least one editable field must be present")
    if request.title is not None and not request.title.strip():
        raise ValueError("Title cannot be empty")
    if request.description is not None and not request.description.strip():
        raise ValueError("Description cannot be empty")
    if request.tags is not None:
        _normalize_tags(request.tags)


def _artifact_entity_list(artifact: dict[str, Any], group: EditableEntityGroup) -> list[Any]:
    """Return the underlying artifact entity list for an editable group."""
    parent_key, list_key = _ENTITY_GROUP_PATHS[group]
    parent = artifact.get(parent_key)
    if not isinstance(parent, dict):
        raise ValueError(f"Artifact group parent missing: {parent_key}")
    raw_entities = parent.get(list_key)
    if not isinstance(raw_entities, list):
        raise ValueError(f"Artifact entity group missing: {group}")
    return raw_entities


def _apply_entity_edit(
    entity: dict[str, Any],
    request: EntityEditRequest,
    group: EditableEntityGroup,
    *,
    reviewed_by: str,
) -> None:
    """Apply validated entity edit fields to one artifact entity."""
    if request.title is not None:
        _set_first_mapped_string(entity, _TITLE_KEYS[group], request.title.strip())
    if request.description is not None:
        _set_first_mapped_string(entity, _DESCRIPTION_KEYS[group], request.description.strip())
    if request.tags is not None:
        _set_entity_tags(entity, _normalize_tags(request.tags), group)
    if request.hidden is not None:
        _set_entity_hidden_state(entity, request.hidden, reviewed_by=reviewed_by)


def _set_first_mapped_string(entity: dict[str, Any], keys: tuple[str, ...], value: str) -> None:
    """Set the first existing mapped string field, or the preferred field."""
    for key in keys:
        if key in entity:
            entity[key] = value
            return
    entity[keys[0]] = value


def _normalize_tags(tags: list[str]) -> list[str]:
    """Trim and deduplicate tags while preserving input order."""
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        text = str(tag).strip()
        if not text:
            raise ValueError("Tags cannot contain empty values")
        if text not in seen:
            normalized.append(text)
            seen.add(text)
    return normalized


def _set_entity_tags(
    entity: dict[str, Any],
    tags: list[str],
    group: EditableEntityGroup,
) -> None:
    """Set normalized tags using the first suitable existing tag field."""
    target_key = "proposed_tags"
    for key in _TAG_KEYS[group]:
        if isinstance(entity.get(key), list):
            target_key = key
            break
    entity[target_key] = tags
    for key in _TAG_KEYS[group]:
        if key != target_key:
            entity.pop(key, None)


def _set_entity_hidden_state(
    entity: dict[str, Any],
    hidden: bool,
    *,
    reviewed_by: str,
) -> None:
    """Set or update review hidden state without deleting the entity."""
    state = entity.get("review_state")
    if not isinstance(state, dict):
        state = {}
    state["hidden"] = hidden
    state["hidden_at"] = _utc_timestamp()
    state["hidden_by"] = reviewed_by
    entity["review_state"] = state


def _ensure_finish_allowed(artifact: dict[str, Any], *, force: bool) -> None:
    """Reject finishing when a conflicting management decision exists."""
    management_review = get_management_review(artifact)
    if management_review is None or management_review.status == "approved" or force:
        return
    raise FinishConflictError(
        f"Finish conflicts with existing management decision: {management_review.status}"
    )


def _write_review_artifact_with_backup(
    review_json_path: Path,
    artifact: dict[str, Any],
    *,
    reason: str,
) -> Path:
    """Back up and atomically overwrite an existing review artifact."""
    previous_text = review_json_path.read_text(encoding="utf-8")
    backup_path = _write_review_backup(review_json_path, previous_text, reason=reason)
    atomic_write_json(review_json_path, artifact)
    return backup_path
