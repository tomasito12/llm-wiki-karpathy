"""Loading, normalization, and render-aligned writes for management review artifacts."""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast, get_args

from src.ingest_queue.queue import IngestItem, list_ingest_items
from src.ingest_review.dashboard_ui import (
    CHAPTER_LABELS,
    SOURCE_CHAPTER_DISPLAY_ORDER,
    effective_list_chapter_lines,
    effective_scalar_chapter_text,
)
from src.ingest_review.schema import SOURCE_SUMMARY_SCALAR_KEYS
from src.ingest_review.tags import (
    load_glossary_tags,
    load_howto_tags,
    load_impl_study_tags,
    load_model_tags,
    load_tag_list,
    load_tool_tags,
    load_tool_types,
    load_topic_tags,
    load_trend_tags,
    normalize_tag,
)
from src.management_web.entity_config import (
    ENTITY_CONFIG_BY_GROUP,
    ENTITY_CONFIGS,
    LLM_OUTPUT_NON_ENTITY_KEYS,
    SUPPORTED_ARTIFACT_KEYS,
    EditableEntityConfig,
    TagAllowlistKey,
)
from src.management_web.models import (
    DebugPayload,
    DecisionCounts,
    EditableEntityGroup,
    EntityCounts,
    EntityDetailList,
    EntityDetailScalar,
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
    NormalizedEntityGroup,
    QueueCounts,
    QueueResponse,
    QueueStatusFilter,
    RawSourceResponse,
    ReviewStatus,
    ReviewTagChoice,
    ReviewTagSource,
    ReviewTagsResponse,
    ReviewTypesResponse,
    SourceDetailResponse,
    SourceMetadata,
    SourcePaths,
    SourceSummary,
    SourceSummaryChapter,
)
from src.pipeline.atomic import atomic_write_json
from src.wiki_paths.config import WikiPaths
from src.wiki_render.resolve import (
    list_value,
    proposal_is_included,
    reviewed_tags,
    reviewed_types,
    scalar_value,
)
from src.wiki_render.resolve import (
    llm_item as review_llm_item,
)

_SOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_MANAGEMENT_REVIEW_STATUSES = set(get_args(ManagementReviewStatus))


class FinishConflictError(ValueError):
    """Raised when finishing would overwrite a conflicting management decision."""


class EntityEditConflictError(ValueError):
    """Raised when an entity edit cannot align review and llm_output nodes."""


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
    config = ENTITY_CONFIG_BY_GROUP[entity_group]
    review_nodes = _review_entity_list(artifact, config)
    llm_items = _llm_entity_list(artifact, config)
    if request.index < 0 or request.index >= max(len(review_nodes), len(llm_items)):
        raise ValueError(f"Entity index out of range: {request.index}")
    llm_has_item = request.index < len(llm_items) and isinstance(llm_items[request.index], dict)
    review_has_node = request.index < len(review_nodes) and isinstance(
        review_nodes[request.index], dict
    )
    if llm_has_item and not review_has_node:
        raise EntityEditConflictError(
            f"Review node missing for {entity_group} index {request.index}"
        )
    if not review_has_node:
        raise ValueError(f"Entity index out of range: {request.index}")
    review_node = review_nodes[request.index]
    llm_entity = llm_items[request.index] if llm_has_item else None
    _apply_entity_edit(
        review_node,
        llm_entity,
        request,
        config,
        reviewed_by=reviewed_by,
    )
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
    _ensure_finish_entity_coverage(artifact)
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
        Source summary response model including full on-demand chapters.
    """
    llm_output = _dict_value(artifact, "llm_output")
    summary = _dict_value(llm_output, "source_summary")
    review_summary = _dict_value(_dict_value(artifact, "review"), "source_summary")
    raw_insights = summary.get("key_insights") if isinstance(summary, dict) else []
    insights = (
        [str(item).strip() for item in raw_insights if str(item).strip()]
        if isinstance(raw_insights, list)
        else []
    )
    chapters = _source_summary_chapters(summary, review_summary)
    return SourceSummary(
        short=_first_string(summary, ("accessible_overview", "summary")),
        key_insights=insights,
        chapters=chapters,
    )


def _source_summary_chapters(
    llm_summary: dict[str, Any],
    review_summary: dict[str, Any],
) -> list[SourceSummaryChapter]:
    """Build Streamlit-aligned source summary chapters for on-demand inspection."""
    chapters: list[SourceSummaryChapter] = []
    for section_key in SOURCE_CHAPTER_DISPLAY_ORDER:
        label = CHAPTER_LABELS.get(section_key, section_key.replace("_", " ").title())
        node = review_summary.get(section_key)
        review_node = node if isinstance(node, dict) else {}
        if section_key == "sources":
            items = effective_list_chapter_lines(llm_summary, review_node, "sources")
            chapters.append(
                SourceSummaryChapter(
                    key=section_key,
                    label=label,
                    body="\n".join(items),
                    items=items,
                )
            )
            continue
        if section_key == "key_insights":
            items = effective_list_chapter_lines(llm_summary, review_node, section_key)
            chapters.append(
                SourceSummaryChapter(
                    key=section_key,
                    label=label,
                    body="\n".join(items),
                    items=items,
                )
            )
            continue
        if section_key in SOURCE_SUMMARY_SCALAR_KEYS:
            body = effective_scalar_chapter_text(llm_summary, review_node, section_key)
            chapters.append(
                SourceSummaryChapter(
                    key=section_key,
                    label=label,
                    body=body,
                    items=[],
                )
            )
    return chapters


def collect_tags(artifact: dict[str, Any] | None) -> list[str]:
    """Collect display tags from supported entity groups in a stable order.

    Rejected/hidden entities do not contribute tags. This matches wiki-render
    collection, which only unions tags from included proposals.

    Args:
        artifact: Loaded review artifact, when available.

    Returns:
        Sorted unique tag strings.
    """
    tags: set[str] = set()
    entities = normalize_entities(artifact)
    for group in entities.groups:
        for entity in group.items:
            if entity.hidden:
                continue
            tags.update(entity.tags)
    return sorted(tags)


def build_review_tag_registry(
    paths: WikiPaths,
    *,
    group: str | None = None,
) -> ReviewTagsResponse:
    """Return tag choices from config registries and review artifacts.

    When ``group`` is set, return only the Streamlit-aligned allowlist for that
    entity group (plus observed usage counts for those tags).

    Args:
        paths: Resolved wiki paths.
        group: Optional editable entity group slug.

    Returns:
        Deterministically sorted tag choices with usage counts.

    Raises:
        ValueError: If ``group`` is unknown.
    """
    usage_counts = _collect_tag_usage_from_artifacts(paths.reviews_dir)
    if group is None:
        registry_tags = _load_registry_tags(paths.repo_root)
    else:
        registry_tags = _load_group_allowlist_tags(paths.repo_root, group)
    choices: list[ReviewTagChoice] = []
    for name in sorted(registry_tags | (set(usage_counts) if group is None else set())):
        if group is not None and name not in registry_tags:
            continue
        source: ReviewTagSource = "registry" if name in registry_tags else "reviews"
        choices.append(
            ReviewTagChoice(
                name=name,
                source=source,
                usage_count=usage_counts.get(name, 0),
            )
        )
    choices.sort(key=lambda choice: (-choice.usage_count, choice.name))
    return ReviewTagsResponse(tags=choices)


def build_review_type_registry(
    paths: WikiPaths,
    *,
    group: str,
) -> ReviewTypesResponse:
    """Return tool-kind choices from the tool types allowlist and review usage.

    Args:
        paths: Resolved wiki paths.
        group: Editable entity group slug; only ``tools`` is supported.

    Returns:
        Deterministically sorted type choices with usage counts.

    Raises:
        ValueError: If ``group`` is not ``tools``.
    """
    if group != "tools":
        msg = f"Type editing is only supported for tools, not {group!r}"
        raise ValueError(msg)
    registry_types = {normalize_tag(name) for name in load_tool_types(paths.repo_root)}
    registry_types.discard("")
    usage_counts = _collect_type_usage_from_artifacts(paths.reviews_dir, group="tools")
    choices: list[ReviewTagChoice] = []
    for name in sorted(registry_types):
        choices.append(
            ReviewTagChoice(
                name=name,
                source="registry",
                usage_count=usage_counts.get(name, 0),
            )
        )
    choices.sort(key=lambda choice: (-choice.usage_count, choice.name))
    return ReviewTypesResponse(types=choices)


def _load_group_allowlist_tags(repo_root: Path, group: str) -> set[str]:
    """Load the Streamlit-aligned tag allowlist for one entity group."""
    config = ENTITY_CONFIG_BY_GROUP.get(group)
    if config is None:
        msg = f"Unknown entity group: {group}"
        raise ValueError(msg)
    allowlist_key = config.tag_allowlist
    if allowlist_key is None:
        return set()
    return set(_load_allowlist_tags(repo_root, allowlist_key))


def _load_allowlist_tags(repo_root: Path, allowlist_key: TagAllowlistKey) -> list[str]:
    """Load one configured tag allowlist."""
    loaders: dict[TagAllowlistKey, Any] = {
        "topic": load_topic_tags,
        "glossary": load_glossary_tags,
        "trend": load_trend_tags,
        "howto": load_howto_tags,
        "tool": load_tool_tags,
        "model": load_model_tags,
        "impl_study": load_impl_study_tags,
    }
    return list(loaders[allowlist_key](repo_root))


def normalize_entities(artifact: dict[str, Any] | None) -> EntityGroups:
    """Normalize all supported entity groups for the management review workspace.

    Args:
        artifact: Loaded review artifact, when available.

    Returns:
        Entity groups including legacy topic/glossary/trend fields and generic groups.
    """
    groups = [_normalize_entity_group(artifact, config) for config in ENTITY_CONFIGS]
    by_group = {group.group: group for group in groups}
    return EntityGroups(
        topics=by_group["topics"].items,
        glossary=by_group["glossary"].items,
        trends=by_group["trends"].items,
        groups=groups,
    )


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
        entity_counts=_entity_counts(entities),
        review_json_path=str(item.review_json_path),
        raw_md_available=item.raw_md_path is not None,
        management_status=management_review.status if management_review else None,
    )


def _has_analysis_payload(artifact: dict[str, Any]) -> bool:
    """Return whether an artifact contains pre-analysis output, not only a decision."""
    llm_output = _dict_value(artifact, "llm_output")
    if isinstance(llm_output.get("source_summary"), dict):
        return True
    return bool(_llm_output_entity_list_keys(llm_output))


def _llm_output_entity_list_keys(llm_output: dict[str, Any]) -> list[str]:
    """Return non-empty entity-like list keys present under ``llm_output``."""
    keys: list[str] = []
    for key, value in llm_output.items():
        if key in LLM_OUTPUT_NON_ENTITY_KEYS:
            continue
        if not isinstance(value, list) or not value:
            continue
        if not all(isinstance(item, dict) for item in value):
            continue
        keys.append(key)
    return keys


def unsupported_llm_output_entity_keys(llm_output: dict[str, Any]) -> list[str]:
    """Return unsupported entity list keys that would bypass management-web coverage."""
    return [
        key
        for key in _llm_output_entity_list_keys(llm_output)
        if key not in SUPPORTED_ARTIFACT_KEYS
    ]


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


def _normalize_entity_group(
    artifact: dict[str, Any] | None,
    config: EditableEntityConfig,
) -> NormalizedEntityGroup:
    """Normalize one configured entity group from review and llm_output data."""
    review_nodes = _review_entity_list(artifact or {}, config)
    llm_items = _llm_entity_list(artifact or {}, config)
    item_count = max(len(review_nodes), len(llm_items))
    items = [
        _normalize_entity_item(
            config,
            review_nodes[index] if index < len(review_nodes) else None,
            llm_items[index] if index < len(llm_items) else None,
            index=index,
        )
        for index in range(item_count)
        if _entity_item_exists(
            review_nodes[index] if index < len(review_nodes) else None,
            llm_items[index] if index < len(llm_items) else None,
        )
    ]
    return NormalizedEntityGroup(
        group=cast("EditableEntityGroup", config.group),
        label=config.label,
        section=config.section,
        items=items,
    )


def _entity_item_exists(review_node: Any, llm_item: Any) -> bool:
    """Return whether an entity pair has renderable content at an index."""
    if isinstance(review_node, dict) or isinstance(llm_item, dict):
        return True
    return llm_item is not None and str(llm_item).strip() != ""


def _normalize_entity_item(
    config: EditableEntityConfig,
    review_node: dict[str, Any] | None,
    llm_item: Any,
    *,
    index: int,
) -> NormalizedEntity:
    """Normalize one entity item using review-first render accessors."""
    if isinstance(llm_item, dict):
        llm_dict = llm_item
    elif llm_item is not None and not isinstance(review_node, dict):
        text = str(llm_item).strip()
        return NormalizedEntity(
            index=index,
            title=text,
            description="",
            tags=[],
            types=[],
            evidence="",
            hidden=False,
            render_category=config.render_category,
            render_mode=config.render_mode,
            detail_scalars=[],
            detail_lists=[],
            raw={"value": llm_item},
        )
    else:
        llm_dict = {}
    review_dict = review_node if isinstance(review_node, dict) else {}
    title = _entity_title(config, review_dict, llm_dict)
    description = _entity_description(config, review_dict, llm_dict)
    tags = _entity_tags(config, review_dict, llm_dict)
    types = _entity_types(review_dict, llm_dict)
    hidden = _entity_is_hidden(review_dict, llm_dict)
    evidence = _entity_evidence(review_dict, llm_dict)
    return NormalizedEntity(
        index=index,
        title=title,
        description=description,
        tags=tags,
        types=types,
        evidence=evidence,
        hidden=hidden,
        render_category=config.render_category,
        render_mode=config.render_mode,
        detail_scalars=_entity_detail_scalars(
            config,
            review_dict,
            llm_dict,
            description=description,
            evidence=evidence,
        ),
        detail_lists=_entity_detail_lists(config, review_dict, llm_dict),
        raw=llm_dict or review_dict,
    )


def _entity_title(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
) -> str:
    """Return the display title for one entity."""
    if review_node:
        title = scalar_value(review_node, config.title_key)
        if title:
            return title
        embedded = review_llm_item(review_node)
        if embedded:
            title = _first_string(embedded, (config.title_key, *config.title_fallback_keys))
            if title:
                return title
    return _first_string(llm_item, (config.title_key, *config.title_fallback_keys))


def _entity_description(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
) -> str:
    """Return the compact description for one entity."""
    if review_node:
        description = scalar_value(review_node, config.description_key)
        if description:
            return description
        embedded = review_llm_item(review_node)
        if embedded:
            description = _first_string(
                embedded,
                (config.description_key, *config.description_fallback_keys),
            )
            if description:
                return description
    return _first_string(
        llm_item,
        (config.description_key, *config.description_fallback_keys),
    )


def _entity_detail_lists(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
) -> list[EntityDetailList]:
    """Return read-only supporting list fields for one entity card."""
    detail_lists: list[EntityDetailList] = []
    seen_labels: set[str] = set()
    for field_key, label in config.detail_list_fields:
        if review_node:
            items = list_value(review_node, field_key)
        else:
            items = _list_from_llm_item(llm_item, field_key)
        if items:
            detail_lists.append(EntityDetailList(label=label, items=items))
            seen_labels.add(label)
    for field_key, items in _leftover_list_fields(config, review_node, llm_item):
        label = _humanize_field_label(field_key)
        if not items or label in seen_labels:
            continue
        detail_lists.append(EntityDetailList(label=label, items=items))
        seen_labels.add(label)
    return detail_lists


def _entity_detail_scalars(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
    *,
    description: str,
    evidence: str,
) -> list[EntityDetailScalar]:
    """Return the full scalar extraction payload for on-demand inspection.

    Includes the primary description and evidence so Full extraction is
    self-contained (Streamlit-aligned), not only the secondary fields.
    """
    detail_scalars: list[EntityDetailScalar] = []
    description_normalized = description.strip()
    seen_bodies: set[str] = set()
    seen_labels: set[str] = set()
    if description_normalized:
        detail_scalars.append(
            EntityDetailScalar(label=config.description_label, body=description_normalized)
        )
        seen_bodies.add(description_normalized)
        seen_labels.add(config.description_label)
    for field_key, label in config.detail_scalar_fields:
        if field_key == config.description_key:
            continue
        body = _entity_scalar_field(review_node, llm_item, field_key)
        if not body or body in seen_bodies or label in seen_labels:
            continue
        detail_scalars.append(EntityDetailScalar(label=label, body=body))
        seen_bodies.add(body)
        seen_labels.add(label)
    evidence_normalized = evidence.strip()
    if (
        evidence_normalized
        and evidence_normalized not in seen_bodies
        and config.evidence_label not in seen_labels
    ):
        detail_scalars.append(
            EntityDetailScalar(label=config.evidence_label, body=evidence_normalized)
        )
        seen_bodies.add(evidence_normalized)
        seen_labels.add(config.evidence_label)
    for field_key, body in _leftover_scalar_fields(config, review_node, llm_item):
        label = _humanize_field_label(field_key)
        if not body or body in seen_bodies or label in seen_labels:
            continue
        detail_scalars.append(EntityDetailScalar(label=label, body=body))
        seen_bodies.add(body)
        seen_labels.add(label)
    return detail_scalars


_FULL_EXTRACTION_SKIP_KEYS: frozenset[str] = frozenset(
    {
        "proposed_tags",
        "suggested_new_tags",
        "primary_tag",
        "secondary_tag",
        "suggested_new_tag",
        "topic_tags",
        "glossary_tags",
        "trend_tags",
        "tags",
        "proposed_types",
        "proposed_new_type",
        "match_candidates",
        "confidence",
        "suggested_action",
        "value_level",
        "evidence_type",
        "review_state",
        "assessed_as_of",
        "suggested_destinations",
        "mentioned_entities",
    }
)


def _configured_extraction_keys(config: EditableEntityConfig) -> set[str]:
    """Return field keys already covered by the compact card or configured details."""
    keys = {
        config.title_key,
        config.description_key,
        *config.title_fallback_keys,
        *config.evidence_keys,
        *config.tag_keys,
        *config.type_keys,
    }
    keys.update(field_key for field_key, _label in config.detail_scalar_fields)
    keys.update(field_key for field_key, _label in config.detail_list_fields)
    keys.update(_FULL_EXTRACTION_SKIP_KEYS)
    return keys


def _leftover_scalar_fields(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
) -> list[tuple[str, str]]:
    """Return nonempty scalar leftovers not covered by configured extraction fields."""
    known = _configured_extraction_keys(config)
    leftovers: list[tuple[str, str]] = []
    source = review_llm_item(review_node) if review_node else {}
    if not source:
        source = llm_item
    for field_key, raw in source.items():
        if field_key in known or not isinstance(raw, str):
            continue
        body = raw.strip()
        if body:
            leftovers.append((field_key, body))
    return leftovers


def _leftover_list_fields(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
) -> list[tuple[str, list[str]]]:
    """Return nonempty list leftovers not covered by configured extraction fields."""
    known = _configured_extraction_keys(config)
    leftovers: list[tuple[str, list[str]]] = []
    candidate_keys: list[str] = []
    if review_node:
        candidate_keys.extend(review_llm_item(review_node))
    candidate_keys.extend(llm_item)
    seen_keys: set[str] = set()
    for field_key in candidate_keys:
        if field_key in known or field_key in seen_keys:
            continue
        seen_keys.add(field_key)
        if review_node:
            items = list_value(review_node, field_key)
            if not items:
                items = _list_from_llm_item(llm_item, field_key)
        else:
            items = _list_from_llm_item(llm_item, field_key)
        if items:
            leftovers.append((field_key, items))
    return leftovers


def _humanize_field_label(field_key: str) -> str:
    """Convert a snake_case extraction key into a short display label."""
    return field_key.replace("_", " ").strip().capitalize()


def _entity_scalar_field(
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
    field_key: str,
) -> str:
    """Return one review-first scalar field for full extraction."""
    if review_node:
        text = scalar_value(review_node, field_key)
        if text:
            return text
        embedded = review_llm_item(review_node)
        if embedded:
            text = _first_string(embedded, (field_key,))
            if text:
                return text
    return _first_string(llm_item, (field_key,))


def _entity_evidence(review_node: dict[str, Any], llm_item: dict[str, Any]) -> str:
    """Return the first evidence-like string from review or llm data."""
    if review_node:
        for key in (
            "evidence",
            "supporting_snippet",
            "evidence_from_source",
            "source_phrase",
            "source_quote",
            "supporting_evidence",
        ):
            text = scalar_value(review_node, key)
            if text:
                return text
    return _first_evidence(llm_item)


def _entity_is_hidden(review_node: dict[str, Any], llm_item: dict[str, Any]) -> bool:
    """Return whether an entity is hidden or rejected from normal display."""
    if review_node and not proposal_is_included(review_node):
        return True
    for payload in (review_node, llm_item):
        state = payload.get("review_state") if isinstance(payload, dict) else None
        if isinstance(state, dict) and state.get("hidden") is True:
            return True
    return False


def _entity_tags(
    config: EditableEntityConfig,
    review_node: dict[str, Any],
    llm_item: dict[str, Any],
) -> list[str]:
    """Return display tags from review accessors with llm_output fallbacks."""
    if review_node:
        tags = reviewed_tags(review_node)
        if tags:
            return tags
        embedded = review_llm_item(review_node)
        if embedded:
            return _tags_from_llm_item(embedded, config)
    return _tags_from_llm_item(llm_item, config)


def _entity_types(review_node: dict[str, Any], llm_item: dict[str, Any]) -> list[str]:
    """Return display types from review accessors with llm_output fallbacks."""
    if review_node:
        types = reviewed_types(review_node)
        if types:
            return types
        embedded = review_llm_item(review_node)
        if embedded:
            return _types_from_llm_item(embedded)
    return _types_from_llm_item(llm_item)


def _tags_from_llm_item(llm_item: dict[str, Any], config: EditableEntityConfig) -> list[str]:
    """Return display tags from an llm_output item."""
    return _string_list_from_keys(llm_item, config.tag_keys)


def _types_from_llm_item(llm_item: dict[str, Any]) -> list[str]:
    """Return display types from an llm_output item."""
    types: set[str] = set()
    proposed = llm_item.get("proposed_types")
    if isinstance(proposed, list):
        types.update(str(item).strip() for item in proposed if str(item).strip())
    proposed_new = llm_item.get("proposed_new_type")
    if isinstance(proposed_new, str) and proposed_new.strip():
        types.add(proposed_new.strip())
    return sorted(types)


def _list_from_llm_item(llm_item: dict[str, Any], key: str) -> list[str]:
    """Return a stripped string list from one llm_output field."""
    raw = llm_item.get(key)
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _entity_counts(entities: EntityGroups) -> EntityCounts:
    """Count visible entities per group for queue rows."""
    counts = EntityCounts()
    for group in entities.groups:
        visible = sum(1 for item in group.items if not item.hidden)
        setattr(counts, group.group, visible)
    return counts


def _review_entity_list(artifact: dict[str, Any], config: EditableEntityConfig) -> list[Any]:
    """Return the review-tree entity list for one configured group."""
    review = _dict_value(artifact, "review")
    raw_entities = review.get(config.review_key)
    return raw_entities if isinstance(raw_entities, list) else []


def _llm_entity_list(artifact: dict[str, Any], config: EditableEntityConfig) -> list[Any]:
    """Return the llm_output entity list for one configured group."""
    llm_output = _dict_value(artifact, "llm_output")
    raw_entities = llm_output.get(config.artifact_key)
    return raw_entities if isinstance(raw_entities, list) else []


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
    if group not in ENTITY_CONFIG_BY_GROUP:
        raise ValueError(f"Invalid entity group: {group!r}")
    return cast("EditableEntityGroup", group)


def _validate_entity_edit_request(request: EntityEditRequest) -> None:
    """Validate that at least one well-formed editable field is present."""
    has_field = any(
        value is not None
        for value in (
            request.title,
            request.description,
            request.tags,
            request.types,
            request.hidden,
        )
    )
    if not has_field:
        raise ValueError("At least one editable field must be present")
    if request.title is not None and not request.title.strip():
        raise ValueError("Title cannot be empty")
    if request.description is not None and not request.description.strip():
        raise ValueError("Description cannot be empty")
    if request.tags is not None:
        _normalize_tags(request.tags)
    if request.types is not None:
        if request.group != "tools":
            raise ValueError("Type editing is only supported for tools")
        _normalize_tags(request.types)


def _apply_entity_edit(
    review_node: dict[str, Any],
    llm_entity: dict[str, Any] | None,
    request: EntityEditRequest,
    config: EditableEntityConfig,
    *,
    reviewed_by: str,
) -> None:
    """Apply validated entity edit fields to review and mirrored llm_output nodes."""
    if request.title is not None:
        _set_review_scalar(review_node, config.title_key, request.title.strip())
        if llm_entity is not None:
            llm_entity[config.title_key] = request.title.strip()
    if request.description is not None:
        _set_review_scalar(review_node, config.description_key, request.description.strip())
        if llm_entity is not None:
            llm_entity[config.description_key] = request.description.strip()
    if request.tags is not None:
        tags = _normalize_tags(request.tags)
        _set_review_tags(review_node, tags)
        if llm_entity is not None:
            _set_llm_tags(llm_entity, tags, config)
    if request.types is not None:
        types = _normalize_tags(request.types)
        _set_review_types(review_node, types)
        if llm_entity is not None:
            _set_llm_types(llm_entity, types, config)
    if request.hidden is not None:
        _set_review_hidden_state(review_node, request.hidden, reviewed_by=reviewed_by)
        if llm_entity is not None:
            _set_llm_hidden_state(llm_entity, request.hidden, reviewed_by=reviewed_by)


def _set_review_scalar(review_node: dict[str, Any], key: str, value: str) -> None:
    """Write a reviewed scalar field into the review tree."""
    section = _ensure_review_section(review_node, key)
    section["final_text"] = value


def _ensure_review_section(review_node: dict[str, Any], key: str) -> dict[str, Any]:
    """Return or create a review section for one scalar/list field."""
    sections = review_node.get("sections")
    if not isinstance(sections, dict):
        sections = {}
        review_node["sections"] = sections
    section = sections.get(key)
    if not isinstance(section, dict):
        section = {}
        sections[key] = section
    section["status"] = "modified"
    return section


def _set_review_tags(review_node: dict[str, Any], tags: list[str]) -> None:
    """Write reviewed tags into the review tree."""
    tag_node = review_node.get("tags")
    if not isinstance(tag_node, dict):
        tag_node = {}
        review_node["tags"] = tag_node
    tag_node["final_tags"] = tags


def _set_llm_tags(
    llm_entity: dict[str, Any],
    tags: list[str],
    config: EditableEntityConfig,
) -> None:
    """Mirror reviewed tags into llm_output for display coherence."""
    llm_entity["proposed_tags"] = tags
    for key in config.tag_keys:
        if key != "proposed_tags":
            llm_entity.pop(key, None)


def _set_review_types(review_node: dict[str, Any], types: list[str]) -> None:
    """Write reviewed tool kinds into the review tree."""
    type_node = review_node.get("types")
    if not isinstance(type_node, dict):
        type_node = {}
        review_node["types"] = type_node
    type_node["approved_types"] = types
    type_node["reviewer_types_added"] = []
    type_node["approved_new_types"] = []


def _set_llm_types(
    llm_entity: dict[str, Any],
    types: list[str],
    config: EditableEntityConfig,
) -> None:
    """Mirror reviewed tool kinds into llm_output for display coherence."""
    llm_entity["proposed_types"] = types
    for key in config.type_keys:
        if key != "proposed_types":
            llm_entity.pop(key, None)


def _set_review_hidden_state(
    review_node: dict[str, Any],
    hidden: bool,
    *,
    reviewed_by: str,
) -> None:
    """Set render-aligned hidden state on a review node."""
    review_node["proposal_status"] = "rejected" if hidden else "approved"
    state = review_node.get("review_state")
    if not isinstance(state, dict):
        state = {}
    state["hidden"] = hidden
    state["hidden_at"] = _utc_timestamp()
    state["hidden_by"] = reviewed_by
    review_node["review_state"] = state


def _set_llm_hidden_state(
    llm_entity: dict[str, Any],
    hidden: bool,
    *,
    reviewed_by: str,
) -> None:
    """Mirror hidden metadata into llm_output for display coherence."""
    state = llm_entity.get("review_state")
    if not isinstance(state, dict):
        state = {}
    state["hidden"] = hidden
    state["hidden_at"] = _utc_timestamp()
    state["hidden_by"] = reviewed_by
    llm_entity["review_state"] = state


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


def _load_registry_tags(repo_root: Path) -> set[str]:
    """Load normalized tags from configured review tag registries."""
    config_dir = repo_root / "config"
    tags: set[str] = set()
    if not config_dir.is_dir():
        return tags
    for path in sorted(config_dir.glob("review_tags_*.yaml")):
        for tag in load_tag_list(path):
            if tag:
                tags.add(tag)
    return tags


def _collect_tag_usage_from_artifacts(reviews_dir: Path) -> Counter[str]:
    """Count tag usage across normalized entities in review artifacts."""
    counts: Counter[str] = Counter()
    if not reviews_dir.is_dir():
        return counts
    for review_json in sorted(reviews_dir.glob("*/review.json")):
        artifact = load_review_artifact(review_json)
        if artifact is None:
            continue
        entities = normalize_entities(artifact)
        for group in entities.groups:
            for entity in group.items:
                if entity.hidden:
                    continue
                for tag in entity.tags:
                    normalized = normalize_tag(tag)
                    if normalized:
                        counts[normalized] += 1
    return counts


def _collect_type_usage_from_artifacts(
    reviews_dir: Path,
    *,
    group: str,
) -> Counter[str]:
    """Count type/kind usage for one entity group across review artifacts."""
    counts: Counter[str] = Counter()
    if not reviews_dir.is_dir():
        return counts
    for review_json in sorted(reviews_dir.glob("*/review.json")):
        artifact = load_review_artifact(review_json)
        if artifact is None:
            continue
        entities = normalize_entities(artifact)
        for entity_group in entities.groups:
            if entity_group.group != group:
                continue
            for entity in entity_group.items:
                if entity.hidden:
                    continue
                for type_name in entity.types:
                    normalized = normalize_tag(type_name)
                    if normalized:
                        counts[normalized] += 1
    return counts


def _ensure_finish_allowed(artifact: dict[str, Any], *, force: bool) -> None:
    """Reject finishing when a conflicting management decision exists."""
    management_review = get_management_review(artifact)
    if management_review is None or management_review.status == "approved" or force:
        return
    raise FinishConflictError(
        f"Finish conflicts with existing management decision: {management_review.status}"
    )


def _ensure_finish_entity_coverage(artifact: dict[str, Any]) -> None:
    """Reject finishing when llm_output contains unsupported entity groups."""
    llm_output = _dict_value(artifact, "llm_output")
    unsupported = unsupported_llm_output_entity_keys(llm_output)
    if unsupported:
        blocked = unsupported[0]
        raise FinishConflictError(
            f"Finish blocked by unsupported entity group in artifact: {blocked}"
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
