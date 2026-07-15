"""Read-only loading and normalization for management review artifacts."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from src.ingest_queue.queue import IngestItem, list_ingest_items
from src.management_web.models import (
    DebugPayload,
    EntityCounts,
    EntityGroups,
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
from src.wiki_paths.config import WikiPaths

_SOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


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
    return "in_progress"


def build_review_queue(
    paths: WikiPaths,
    *,
    status: QueueStatusFilter = "all",
    limit: int = 50,
    offset: int = 0,
    query: str | None = None,
) -> QueueResponse:
    """Build a filtered, paginated review queue from local raw/review state.

    Args:
        paths: Resolved wiki paths.
        status: Status filter to apply to returned items.
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
    filtered = _filter_queue_items(rows, status=status, query=query)
    bounded_offset = max(offset, 0)
    bounded_limit = max(limit, 0)
    return QueueResponse(
        counts=counts,
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
        debug=DebugPayload(artifact=artifact or {}),
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
        short=_string_field(summary, "summary"),
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
    )


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


def _filter_queue_items(
    items: list[Any],
    *,
    status: QueueStatusFilter,
    query: str | None,
) -> list[Any]:
    """Apply status and text filters to queue items."""
    normalized_query = (query or "").strip().lower()
    filtered = [item for item in items if status == "all" or item.status == status]
    if not normalized_query:
        return filtered
    return [item for item in filtered if _queue_item_matches_query(item, normalized_query)]


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
    return [_normalize_entity(item, kind=kind) for item in raw_items]


def _normalize_entity(item: Any, *, kind: str) -> NormalizedEntity:
    """Normalize one entity item, preserving raw fields for debug inspection."""
    if not isinstance(item, dict):
        text = str(item).strip()
        return NormalizedEntity(
            title=text, description="", tags=[], evidence="", raw={"value": item}
        )
    title_keys = {
        "topic": ("topic_title", "title", "name"),
        "glossary": ("term", "title", "name"),
        "trend": ("trend_title", "title", "name"),
    }[kind]
    description_keys = {
        "topic": ("topic_description", "description", "summary"),
        "glossary": ("definition", "proposed_definition", "description"),
        "trend": ("trend_description", "description", "summary"),
    }[kind]
    tag_keys = {
        "topic": ("topic_tags", "tags"),
        "glossary": ("tags", "glossary_tags"),
        "trend": ("trend_tags", "tags"),
    }[kind]
    return NormalizedEntity(
        title=_first_string(item, title_keys),
        description=_first_string(item, description_keys),
        tags=_string_list_from_keys(item, tag_keys),
        evidence=_first_string(
            item, ("evidence", "source_phrase", "source_quote", "supporting_evidence")
        ),
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
    """Return unique stripped strings from the first list-valued candidate key."""
    for key in keys:
        raw = payload.get(key)
        if not isinstance(raw, list):
            continue
        return sorted({str(item).strip() for item in raw if str(item).strip()})
    return []
