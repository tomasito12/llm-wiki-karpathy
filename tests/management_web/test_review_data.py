"""Tests for read-only management web review data normalization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

from src.management_web.models import (
    EntityEditRequest,
    FinishReviewRequest,
    ManagementDecisionFilter,
    ManagementReviewRequest,
)
from src.management_web.review_data import (
    EntityEditConflictError,
    FinishConflictError,
    build_review_queue,
    build_review_tag_registry,
    finish_review,
    get_source_detail,
    read_raw_markdown,
    unsupported_llm_output_entity_keys,
    update_review_entity,
    validate_source_id,
    write_management_decision,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths
from src.wiki_render.resolve import proposal_is_included, reviewed_tags, scalar_value


def _paths(tmp_path: Path) -> WikiPaths:
    """Return repo-local wiki paths rooted in a temporary directory."""
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    paths.reviews_dir.mkdir(parents=True)
    return paths


def _write_raw(paths: WikiPaths, source_id: str, *, markdown: str | None = "Body") -> None:
    """Create a raw HTML export and optional Markdown sidecar."""
    (paths.raw_dir / f"{source_id}.html").write_text("<html>Article</html>", encoding="utf-8")
    if markdown is not None:
        (paths.raw_dir / f"{source_id}.md").write_text(markdown, encoding="utf-8")


def _write_artifact(
    paths: WikiPaths,
    source_id: str,
    artifact: dict[str, Any],
) -> None:
    """Write one review artifact under the configured reviews directory."""
    review_dir = paths.reviews_dir / source_id
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text(json.dumps(artifact), encoding="utf-8")


def _review_node(
    llm_item: dict[str, Any],
    *,
    status: str = "approved",
) -> dict[str, Any]:
    """Return a render-aligned review node for one llm_output item."""
    return {
        "proposal_status": status,
        "llm_item": llm_item,
        "sections": {},
        "tags": {},
    }


def _review_tree_from_llm_output(llm_output: dict[str, Any]) -> dict[str, Any]:
    """Build a paired review tree from representative llm_output entity lists."""
    review: dict[str, Any] = {}
    for artifact_key, review_key in (
        ("topics", "topics"),
        ("glossary", "glossary"),
        ("industry_trends", "industry_trends"),
        ("how_to", "how_to"),
        ("tools", "tools"),
        ("foundation_models", "foundation_models"),
        ("implementation_studies", "implementation_studies"),
        ("roundup_signals", "roundup_signals"),
        ("interview_insights", "interview_insights"),
    ):
        items = llm_output.get(artifact_key)
        if isinstance(items, list):
            review[review_key] = [
                _review_node(cast(dict[str, Any], item)) for item in items if isinstance(item, dict)
            ]
    return review


def _artifact(*, finished: bool = False) -> dict[str, Any]:
    """Return a minimal but representative review artifact."""
    review_finished_at = "2026-07-15T10:00:00Z" if finished else None
    llm_output: dict[str, Any] = {
        "source_summary": {
            "summary": "A concise summary.",
            "key_insights": ["First useful insight", "Second useful insight"],
        },
        "topics": [
            {
                "topic_title": "Agentic coding workflows",
                "topic_description": "How agents shape software work.",
                "topic_tags": ["ai-engineering", "agents"],
                "evidence": "The article discusses coding agents.",
            }
        ],
        "glossary": [
            {
                "term": "Retrieval augmented generation",
                "definition": "Grounding generation with retrieved context.",
                "tags": ["rag"],
            }
        ],
        "industry_trends": [
            {
                "trend_title": "Teams adopt AI review assistants",
                "trend_description": "Review assistants become part of delivery workflows.",
                "trend_tags": ["software-delivery"],
            }
        ],
    }
    return {
        "source": {
            "title": "Analyzed Article",
            "author": "Ada Lovelace",
            "publication": "Example Weekly",
            "published_date": "2026-07-01",
            "canonical_url": "https://example.test/article",
            "category": "article",
            "readwise_id": "rw-123",
            "raw_html": "raw/readwise/analyzed.html",
            "raw_md": "raw/readwise/analyzed.md",
            "content_sha256": "stored-hash",
        },
        "content_sha256": "stored-hash",
        "review_analytics": {"review_finished_at": review_finished_at},
        "llm_output": llm_output,
        "review": _review_tree_from_llm_output(llm_output),
    }


def _decided_artifact(status: str, *, published_date: str = "2026-07-01") -> dict[str, Any]:
    """Return an analyzed artifact with a management decision."""
    return {
        **_artifact(),
        "source": {"title": f"{status} Article", "published_date": published_date},
        "management_review": {
            "status": status,
            "reviewed_at": "2026-07-15T12:34:56Z",
            "reviewed_by": "plischke",
            "notes": "",
        },
    }


def test_build_review_queue_classifies_counts_and_items(tmp_path: Path) -> None:
    """Queue loading should classify pending, incomplete, in-progress, and finished sources."""
    paths = _paths(tmp_path)
    _write_raw(paths, "pending")
    _write_raw(paths, "incomplete", markdown=None)
    _write_raw(paths, "in-progress")
    _write_artifact(paths, "in-progress", _artifact())
    _write_raw(paths, "finished")
    _write_artifact(paths, "finished", _artifact(finished=True))

    queue = build_review_queue(paths, status="all", limit=10, offset=0, query=None)

    assert queue.counts.total == 4
    assert queue.counts.pending == 1
    assert queue.counts.incomplete == 1
    assert queue.counts.in_progress == 1
    assert queue.counts.finished == 1
    assert {item.source_id: item.status for item in queue.items} == {
        "finished": "finished",
        "in-progress": "in_progress",
        "incomplete": "incomplete",
        "pending": "pending",
    }


def test_build_review_queue_defaults_to_not_reviewed_decision_filter(tmp_path: Path) -> None:
    """Default queue loading should hide sources that already have management decisions."""
    paths = _paths(tmp_path)
    _write_raw(paths, "undecided")
    _write_artifact(paths, "undecided", _artifact())
    _write_raw(paths, "approved")
    _write_artifact(paths, "approved", _decided_artifact("approved"))

    queue = build_review_queue(paths, status="in_progress", limit=10, offset=0, query=None)

    assert [item.source_id for item in queue.items] == ["undecided"]
    assert queue.decision_counts.not_reviewed == 1
    assert queue.decision_counts.approved == 1
    assert queue.counts.in_progress == 2


def test_build_review_queue_decision_all_includes_decided_and_undecided(
    tmp_path: Path,
) -> None:
    """The all decision filter should include sources regardless of management status."""
    paths = _paths(tmp_path)
    _write_raw(paths, "undecided")
    _write_artifact(paths, "undecided", _artifact())
    _write_raw(paths, "approved")
    _write_artifact(paths, "approved", _decided_artifact("approved"))

    queue = build_review_queue(
        paths,
        status="in_progress",
        decision="all",
        limit=10,
        offset=0,
        query=None,
    )

    assert [item.source_id for item in queue.items] == ["undecided", "approved"]


@pytest.mark.parametrize(
    ("decision", "expected_source_id"),
    [
        ("approved", "approved"),
        ("needs_attention", "needs-attention"),
        ("skipped", "skipped"),
        ("reanalyze_requested", "reanalyze-requested"),
    ],
)
def test_build_review_queue_filters_by_management_decision(
    tmp_path: Path,
    decision: ManagementDecisionFilter,
    expected_source_id: str,
) -> None:
    """Decision filters should include only matching management decisions."""
    paths = _paths(tmp_path)
    for source_id, status in [
        ("approved", "approved"),
        ("needs-attention", "needs_attention"),
        ("skipped", "skipped"),
        ("reanalyze-requested", "reanalyze_requested"),
    ]:
        _write_raw(paths, source_id)
        _write_artifact(paths, source_id, _decided_artifact(status))
    _write_raw(paths, "undecided")
    _write_artifact(paths, "undecided", _artifact())

    queue = build_review_queue(
        paths,
        status="in_progress",
        decision=decision,
        limit=10,
        offset=0,
        query=None,
    )

    assert [item.source_id for item in queue.items] == [expected_source_id]


def test_build_review_queue_decision_counts_follow_source_status_filter(
    tmp_path: Path,
) -> None:
    """Decision counts should be computed after source-analysis status filtering."""
    paths = _paths(tmp_path)
    _write_raw(paths, "ready-undecided")
    _write_artifact(paths, "ready-undecided", _artifact())
    _write_raw(paths, "ready-approved")
    _write_artifact(paths, "ready-approved", _decided_artifact("approved"))
    _write_raw(paths, "finished-approved")
    _write_artifact(
        paths,
        "finished-approved",
        {
            **_decided_artifact("approved"),
            "review_analytics": {"review_finished_at": "2026-07-15T10:00:00Z"},
        },
    )

    queue = build_review_queue(
        paths,
        status="in_progress",
        decision="all",
        limit=10,
        offset=0,
        query=None,
    )

    assert queue.decision_counts.not_reviewed == 1
    assert queue.decision_counts.approved == 1
    assert queue.counts.finished == 1


def test_build_review_queue_applies_query_after_decision_filter(tmp_path: Path) -> None:
    """Query search should only search within sources matching the decision filter."""
    paths = _paths(tmp_path)
    _write_raw(paths, "undecided-api")
    _write_artifact(paths, "undecided-api", {**_artifact(), "source": {"title": "API Undecided"}})
    _write_raw(paths, "approved-api")
    _write_artifact(
        paths,
        "approved-api",
        {**_decided_artifact("approved"), "source": {"title": "API Approved"}},
    )

    queue = build_review_queue(
        paths,
        status="in_progress",
        decision="approved",
        limit=10,
        offset=0,
        query="api",
    )

    assert [item.source_id for item in queue.items] == ["approved-api"]


def test_build_review_queue_sorts_after_decision_filter(tmp_path: Path) -> None:
    """Filtered decided rows should still sort oldest published date first."""
    paths = _paths(tmp_path)
    _write_raw(paths, "newer-approved")
    _write_artifact(
        paths,
        "newer-approved",
        _decided_artifact("approved", published_date="2026-07-02"),
    )
    _write_raw(paths, "older-approved")
    _write_artifact(
        paths,
        "older-approved",
        _decided_artifact("approved", published_date="2026-06-01"),
    )

    queue = build_review_queue(
        paths,
        status="in_progress",
        decision="approved",
        limit=10,
        offset=0,
        query=None,
    )

    assert [item.source_id for item in queue.items] == ["older-approved", "newer-approved"]


def test_build_review_queue_filters_searches_and_paginates(tmp_path: Path) -> None:
    """Queue filtering should apply status, text query, limit, and offset predictably."""
    paths = _paths(tmp_path)
    _write_raw(paths, "alpha-source")
    _write_artifact(paths, "alpha-source", _artifact())
    _write_raw(paths, "beta-source")
    _write_artifact(paths, "beta-source", _artifact())
    _write_raw(paths, "gamma-source")

    queue = build_review_queue(paths, status="in_progress", limit=1, offset=1, query="source")

    assert queue.counts.in_progress == 2
    assert [item.source_id for item in queue.items] == ["beta-source"]
    assert queue.limit == 1
    assert queue.offset == 1


def test_build_review_queue_sorts_oldest_published_sources_first(tmp_path: Path) -> None:
    """Queue items should put older published sources before newer ones."""
    paths = _paths(tmp_path)
    _write_raw(paths, "newer")
    _write_artifact(
        paths,
        "newer",
        {**_artifact(), "source": {"title": "Newer", "published_date": "2026-07-02"}},
    )
    _write_raw(paths, "older")
    _write_artifact(
        paths,
        "older",
        {**_artifact(), "source": {"title": "Older", "published_date": "2026-06-01"}},
    )

    queue = build_review_queue(paths, status="all", decision="all", limit=10, offset=0, query=None)

    assert [item.source_id for item in queue.items] == ["older", "newer"]


def test_get_source_detail_normalizes_artifact_for_review_card(tmp_path: Path) -> None:
    """Source detail should expose metadata, summary, tags, and entity groups for the UI."""
    paths = _paths(tmp_path)
    _write_raw(paths, "analyzed", markdown="# Article\n\nRaw markdown body")
    _write_artifact(paths, "analyzed", _artifact())

    detail = get_source_detail(paths, "analyzed")

    assert detail.source_id == "analyzed"
    assert detail.status == "in_progress"
    assert detail.metadata.title == "Analyzed Article"
    assert detail.summary.short == "A concise summary."
    assert detail.summary.key_insights == ["First useful insight", "Second useful insight"]
    assert detail.tags == ["agents", "ai-engineering", "rag", "software-delivery"]
    assert detail.entities.topics[0].index == 0
    assert detail.entities.topics[0].title == "Agentic coding workflows"
    assert detail.entities.glossary[0].title == "Retrieval augmented generation"
    assert detail.entities.trends[0].title == "Teams adopt AI review assistants"
    assert detail.debug.artifact["content_sha256"] == "stored-hash"


def test_update_review_entity_updates_title_without_losing_unknown_fields(tmp_path: Path) -> None:
    """Entity edits should update mapped fields and preserve unknown artifact data."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(
        paths,
        "editable",
        {
            **_artifact(),
            "llm_output": {
                "topics": [
                    {
                        "topic_title": "Old title",
                        "topic_description": "Existing description.",
                        "custom_field": {"keep": True},
                    }
                ]
            },
            "review": {
                "topics": [
                    _review_node(
                        {
                            "topic_title": "Old title",
                            "topic_description": "Existing description.",
                            "custom_field": {"keep": True},
                        }
                    )
                ]
            },
        },
    )

    response = update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="topics", index=0, title="Prompt caching"),
    )

    review_path = paths.reviews_dir / "editable" / "review.json"
    artifact = json.loads(review_path.read_text(encoding="utf-8"))
    topic = artifact["llm_output"]["topics"][0]
    review_topic = artifact["review"]["topics"][0]
    assert response.source.entities.topics[0].title == "Prompt caching"
    assert response.backup_path is not None
    assert Path(response.backup_path).is_file()
    assert topic["topic_title"] == "Prompt caching"
    assert topic["custom_field"] == {"keep": True}
    assert review_topic["sections"]["topic_title"]["final_text"] == "Prompt caching"


def test_update_review_entity_updates_description_using_mapped_field(tmp_path: Path) -> None:
    """Description edits should update the first existing mapped description field."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(
        paths,
        "editable",
        {
            **_artifact(),
            "llm_output": {
                "industry_trends": [
                    {
                        "trend_title": "Old trend",
                        "operational_insight": "Old description.",
                    }
                ]
            },
            "review": {
                "industry_trends": [
                    _review_node(
                        {
                            "trend_title": "Old trend",
                            "operational_insight": "Old description.",
                        }
                    )
                ]
            },
        },
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="trends", index=0, description="Better description."),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["llm_output"]["industry_trends"][0]["trend_description"] == (
        "Better description."
    )
    assert (
        artifact["review"]["industry_trends"][0]["sections"]["trend_description"]["final_text"]
        == "Better description."
    )


def test_update_review_entity_updates_normalized_topic_description_field(tmp_path: Path) -> None:
    """Description edits should round-trip for fields already preferred by normalization."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(paths, "editable", _artifact())

    response = update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="topics", index=0, description="Round-tripped description."),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["llm_output"]["topics"][0]["knowledge_summary"] == (
        "Round-tripped description."
    )
    assert artifact["review"]["topics"][0]["sections"]["knowledge_summary"]["final_text"] == (
        "Round-tripped description."
    )
    assert response.source.entities.topics[0].description == "Round-tripped description."


def test_update_review_entity_normalizes_tags(tmp_path: Path) -> None:
    """Tag edits should trim whitespace and deduplicate while preserving order."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(paths, "editable", _artifact())

    response = update_review_entity(
        paths,
        "editable",
        EntityEditRequest(
            group="topics",
            index=0,
            tags=[" ai-engineering ", "prompt-caching", "ai-engineering"],
        ),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["llm_output"]["topics"][0]["proposed_tags"] == [
        "ai-engineering",
        "prompt-caching",
    ]
    assert artifact["review"]["topics"][0]["tags"]["final_tags"] == [
        "ai-engineering",
        "prompt-caching",
    ]
    assert response.source.entities.topics[0].tags == ["ai-engineering", "prompt-caching"]


def test_update_review_entity_replaces_scalar_tag_fields(tmp_path: Path) -> None:
    """Tag edits should not leave stale primary/secondary tag fields visible."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(
        paths,
        "editable",
        {
            **_artifact(),
            "llm_output": {
                "topics": [
                    {
                        "topic_title": "Scalar tags",
                        "topic_description": "Description.",
                        "primary_tag": "old-primary",
                        "secondary_tag": "old-secondary",
                    }
                ]
            },
            "review": {
                "topics": [
                    _review_node(
                        {
                            "topic_title": "Scalar tags",
                            "topic_description": "Description.",
                            "primary_tag": "old-primary",
                            "secondary_tag": "old-secondary",
                        }
                    )
                ]
            },
        },
    )

    response = update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="topics", index=0, tags=["new-tag"]),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    topic = artifact["llm_output"]["topics"][0]
    assert topic["proposed_tags"] == ["new-tag"]
    assert "primary_tag" not in topic
    assert "secondary_tag" not in topic
    assert response.source.entities.topics[0].tags == ["new-tag"]


def test_update_review_entity_hides_and_unhides_without_deleting_entity(tmp_path: Path) -> None:
    """Hidden edits should write review_state and keep the original entity object."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(paths, "editable", _artifact())

    hidden_response = update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="topics", index=0, hidden=True),
    )
    unhidden_response = update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="topics", index=0, hidden=False),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    topic = artifact["llm_output"]["topics"][0]
    review_topic = artifact["review"]["topics"][0]
    assert (
        hidden_response.source.debug.artifact["review"]["topics"][0]["proposal_status"]
        == "rejected"
    )
    assert topic["review_state"]["hidden"] is False
    assert review_topic["proposal_status"] == "approved"
    assert topic["topic_title"] == "Agentic coding workflows"
    assert unhidden_response.source.entities.topics[0].hidden is False


def test_update_review_entity_rejects_invalid_inputs(tmp_path: Path) -> None:
    """Entity edits should reject unsafe paths, missing artifacts, invalid groups, and indexes."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(paths, "editable", _artifact())
    _write_raw(paths, "missing-artifact")

    with pytest.raises(ValueError, match="Invalid source_id"):
        update_review_entity(
            paths,
            "../secret",
            EntityEditRequest(group="topics", index=0, title="Safe title"),
        )
    with pytest.raises(FileNotFoundError, match="Review artifact not found"):
        update_review_entity(
            paths,
            "missing-artifact",
            EntityEditRequest(group="topics", index=0, title="Safe title"),
        )
    with pytest.raises(ValueError, match="Invalid entity group"):
        update_review_entity(
            paths,
            "editable",
            EntityEditRequest(group="future_entities", index=0, title="Safe title"),
        )
    with pytest.raises(ValueError, match="Entity index out of range"):
        update_review_entity(
            paths,
            "editable",
            EntityEditRequest(group="topics", index=99, title="Safe title"),
        )
    with pytest.raises(ValueError, match="At least one editable field"):
        update_review_entity(paths, "editable", EntityEditRequest(group="topics", index=0))
    with pytest.raises(ValueError, match="Title cannot be empty"):
        update_review_entity(
            paths,
            "editable",
            EntityEditRequest(group="topics", index=0, title=" "),
        )
    with pytest.raises(ValueError, match="Tags cannot contain empty values"):
        update_review_entity(
            paths,
            "editable",
            EntityEditRequest(group="topics", index=0, tags=["valid", " "]),
        )


def test_update_review_entity_rejects_missing_raw_source(tmp_path: Path) -> None:
    """Entity edits should require the matching raw HTML source."""
    paths = _paths(tmp_path)
    _write_artifact(paths, "orphan", _artifact())

    with pytest.raises(FileNotFoundError, match="Source not found"):
        update_review_entity(
            paths,
            "orphan",
            EntityEditRequest(group="topics", index=0, title="Safe title"),
        )


def test_update_review_entity_does_not_mutate_raw_or_wiki_files(tmp_path: Path) -> None:
    """Entity edits should only modify the selected review artifact."""
    paths = _paths(tmp_path)
    paths.wiki_dir.mkdir(parents=True)
    wiki_page = paths.wiki_dir / "page.md"
    wiki_page.write_text("wiki", encoding="utf-8")
    _write_raw(paths, "editable", markdown="Original markdown")
    _write_artifact(paths, "editable", _artifact())
    raw_html = paths.raw_dir / "editable.html"
    raw_md = paths.raw_dir / "editable.md"
    raw_html_text = raw_html.read_text(encoding="utf-8")
    raw_md_text = raw_md.read_text(encoding="utf-8")

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="topics", index=0, title="Updated title"),
    )

    assert raw_html.read_text(encoding="utf-8") == raw_html_text
    assert raw_md.read_text(encoding="utf-8") == raw_md_text
    assert wiki_page.read_text(encoding="utf-8") == "wiki"


def test_finish_review_writes_finished_timestamp_and_approved_decision(tmp_path: Path) -> None:
    """Finishing should mark lifecycle completion and approve the management review."""
    paths = _paths(tmp_path)
    _write_raw(paths, "ready")
    _write_artifact(paths, "ready", _artifact())

    response = finish_review(paths, "ready", FinishReviewRequest(notes="Looks good."))

    artifact = json.loads((paths.reviews_dir / "ready" / "review.json").read_text())
    assert response.source_id == "ready"
    assert response.management_review.status == "approved"
    assert response.management_review.reviewed_by == "plischke"
    assert response.management_review.notes == "Looks good."
    assert response.review_finished_at.endswith("Z")
    assert Path(response.backup_path).is_file()
    assert artifact["review_analytics"]["review_finished_at"] == response.review_finished_at
    assert artifact["management_review"]["status"] == "approved"
    assert (
        build_review_queue(
            paths,
            status="finished",
            decision="approved",
            limit=10,
            offset=0,
            query=None,
        )
        .items[0]
        .source_id
        == "ready"
    )


@pytest.mark.parametrize("status", ["needs_attention", "skipped", "reanalyze_requested"])
def test_finish_review_rejects_conflicting_management_decision(
    tmp_path: Path,
    status: str,
) -> None:
    """Finishing should not silently overwrite non-approved management decisions."""
    paths = _paths(tmp_path)
    _write_raw(paths, "ready")
    _write_artifact(paths, "ready", _decided_artifact(status))

    with pytest.raises(ValueError, match="conflicts with existing management decision"):
        finish_review(paths, "ready", FinishReviewRequest())


def test_finish_review_force_overrides_conflicting_management_decision(tmp_path: Path) -> None:
    """A forced finish should deliberately convert conflicting decisions to approved."""
    paths = _paths(tmp_path)
    _write_raw(paths, "ready")
    _write_artifact(paths, "ready", _decided_artifact("needs_attention"))

    response = finish_review(paths, "ready", FinishReviewRequest(force=True))

    assert response.management_review.status == "approved"
    artifact = json.loads((paths.reviews_dir / "ready" / "review.json").read_text())
    assert artifact["management_review"]["status"] == "approved"


def test_finish_review_rejects_missing_or_unanalyzed_artifacts(tmp_path: Path) -> None:
    """Finishing should require an existing artifact with analysis payload."""
    paths = _paths(tmp_path)
    _write_raw(paths, "missing-artifact")
    _write_raw(paths, "management-only")
    _write_artifact(
        paths,
        "management-only",
        {
            "management_review": {
                "status": "approved",
                "reviewed_at": "2026-07-15T12:34:56Z",
                "reviewed_by": "plischke",
                "notes": "",
            }
        },
    )

    with pytest.raises(FileNotFoundError, match="Review artifact not found"):
        finish_review(paths, "missing-artifact", FinishReviewRequest())
    with pytest.raises(ValueError, match="no analysis payload"):
        finish_review(paths, "management-only", FinishReviewRequest())


def test_finish_review_does_not_mutate_raw_or_wiki_files(tmp_path: Path) -> None:
    """Finishing should only modify the selected review artifact and its backup."""
    paths = _paths(tmp_path)
    paths.wiki_dir.mkdir(parents=True)
    wiki_page = paths.wiki_dir / "page.md"
    wiki_page.write_text("wiki", encoding="utf-8")
    _write_raw(paths, "ready", markdown="Original markdown")
    _write_artifact(paths, "ready", _artifact())
    raw_html = paths.raw_dir / "ready.html"
    raw_md = paths.raw_dir / "ready.md"
    raw_html_text = raw_html.read_text(encoding="utf-8")
    raw_md_text = raw_md.read_text(encoding="utf-8")

    finish_review(paths, "ready", FinishReviewRequest())

    assert raw_html.read_text(encoding="utf-8") == raw_html_text
    assert raw_md.read_text(encoding="utf-8") == raw_md_text
    assert wiki_page.read_text(encoding="utf-8") == "wiki"


def test_get_source_detail_returns_existing_management_review(tmp_path: Path) -> None:
    """Source detail should expose existing management review decisions."""
    paths = _paths(tmp_path)
    _write_raw(paths, "decided")
    _write_artifact(
        paths,
        "decided",
        {
            **_artifact(),
            "management_review": {
                "status": "approved",
                "reviewed_at": "2026-07-15T12:34:56Z",
                "reviewed_by": "plischke",
                "notes": "Looks good.",
            },
        },
    )

    detail = get_source_detail(paths, "decided")

    assert detail.management_review is not None
    assert detail.management_review.status == "approved"
    assert detail.management_review.reviewed_by == "plischke"
    assert detail.management_review.notes == "Looks good."


def test_build_review_queue_includes_management_status(tmp_path: Path) -> None:
    """Queue rows should expose management decision status separately from analysis status."""
    paths = _paths(tmp_path)
    _write_raw(paths, "decided")
    _write_artifact(
        paths,
        "decided",
        {
            **_artifact(),
            "management_review": {
                "status": "needs_attention",
                "reviewed_at": "2026-07-15T12:34:56Z",
                "reviewed_by": "plischke",
                "notes": "",
            },
        },
    )

    queue = build_review_queue(paths, status="all", decision="all", limit=10, offset=0, query=None)

    assert queue.items[0].status == "in_progress"
    assert queue.items[0].management_status == "needs_attention"


def test_get_source_detail_prefers_accessible_overview_for_easy_read(tmp_path: Path) -> None:
    """Easy Read should prefer the shorter accessible overview over the summary."""
    paths = _paths(tmp_path)
    _write_raw(paths, "easy-read")
    _write_artifact(
        paths,
        "easy-read",
        {
            "source": {"title": "Easy Read"},
            "llm_output": {
                "source_summary": {
                    "accessible_overview": "Easy read overview.",
                    "summary": "Longer technical summary.",
                    "key_insights": [],
                }
            },
        },
    )

    detail = get_source_detail(paths, "easy-read")

    assert detail.summary.short == "Easy read overview."


def test_get_source_detail_tolerates_missing_optional_fields(tmp_path: Path) -> None:
    """Missing optional artifact fields should not prevent source detail rendering."""
    paths = _paths(tmp_path)
    _write_raw(paths, "minimal")
    _write_artifact(paths, "minimal", {"llm_output": {"topics": ["unexpected scalar"]}})

    detail = get_source_detail(paths, "minimal")

    assert detail.metadata.title == "minimal"
    assert detail.summary.short == ""
    assert detail.tags == []
    assert detail.entities.topics[0].title == "unexpected scalar"
    assert detail.entities.glossary == []
    assert detail.entities.trends == []


def test_get_source_detail_normalizes_current_review_artifact_fields(tmp_path: Path) -> None:
    """Current artifact fields should keep tags, descriptions, and evidence visible."""
    paths = _paths(tmp_path)
    _write_raw(paths, "current")
    _write_artifact(
        paths,
        "current",
        {
            "source": {"title": "Current Artifact"},
            "llm_output": {
                "topics": [
                    {
                        "topic_title": "Contact center evaluation",
                        "knowledge_summary": "Evaluation criteria for contact-center AI.",
                        "operational_insight": "Track containment and handoff quality together.",
                        "proposed_tags": ["contact-center-automation"],
                        "primary_tag": "evaluation",
                        "secondary_tag": "governance",
                        "supporting_snippet": "Teams compare quality and containment together.",
                        "supporting_data_points": ["A fallback data point."],
                    }
                ],
                "glossary": [
                    {
                        "term": "Containment rate",
                        "proposed_definition": "Share of conversations resolved without handoff.",
                        "proposed_tags": ["metrics", "automation"],
                    }
                ],
                "industry_trends": [
                    {
                        "trend_title": "Voicebot reviews move toward operational evidence",
                        "operational_insight": "Operational QA becomes part of rollout decisions.",
                        "proposed_tags": ["voicebots"],
                        "evidence_from_source": "The source describes evidence-based QA.",
                    }
                ],
            },
        },
    )

    detail = get_source_detail(paths, "current")

    assert detail.tags == [
        "automation",
        "contact-center-automation",
        "evaluation",
        "governance",
        "metrics",
        "voicebots",
    ]
    assert detail.entities.topics[0].description == "Evaluation criteria for contact-center AI."
    assert detail.entities.topics[0].evidence == "Teams compare quality and containment together."
    assert detail.entities.topics[0].tags == [
        "contact-center-automation",
        "evaluation",
        "governance",
    ]
    assert detail.entities.glossary[0].tags == ["automation", "metrics"]
    assert detail.entities.trends[0].description == (
        "Operational QA becomes part of rollout decisions."
    )
    assert detail.entities.trends[0].evidence == "The source describes evidence-based QA."
    assert detail.entities.trends[0].tags == ["voicebots"]


def test_write_management_decision_creates_new_artifact_when_missing(tmp_path: Path) -> None:
    """A pending raw source should get a new review.json with only management_review."""
    paths = _paths(tmp_path)
    _write_raw(paths, "pending")

    response = write_management_decision(
        paths,
        "pending",
        ManagementReviewRequest(status="approved", notes=""),
    )

    review_path = paths.reviews_dir / "pending" / "review.json"
    artifact = json.loads(review_path.read_text(encoding="utf-8"))
    assert response.source_id == "pending"
    assert response.backup_path is None
    assert artifact["management_review"]["status"] == "approved"
    assert artifact["management_review"]["reviewed_by"] == "plischke"
    assert artifact["management_review"]["notes"] == ""
    assert artifact["management_review"]["reviewed_at"].endswith("Z")


def test_write_management_decision_backs_up_existing_artifact(tmp_path: Path) -> None:
    """Existing review.json content should be backed up before overwriting."""
    paths = _paths(tmp_path)
    _write_raw(paths, "existing")
    original_artifact = _artifact()
    _write_artifact(paths, "existing", original_artifact)
    review_path = paths.reviews_dir / "existing" / "review.json"
    original_text = review_path.read_text(encoding="utf-8")

    response = write_management_decision(
        paths,
        "existing",
        ManagementReviewRequest(status="needs_attention", notes="Review taxonomy."),
    )

    assert response.backup_path is not None
    backup_path = Path(response.backup_path)
    assert backup_path.name.startswith("review.before-management-review.")
    assert backup_path.read_text(encoding="utf-8") == original_text
    updated_artifact = json.loads(review_path.read_text(encoding="utf-8"))
    assert updated_artifact["source"]["title"] == "Analyzed Article"
    assert updated_artifact["management_review"]["status"] == "needs_attention"
    assert updated_artifact["management_review"]["notes"] == "Review taxonomy."


def test_write_management_decision_keeps_multiple_backups_in_same_second(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repeated decisions in one second should not overwrite earlier backups."""
    paths = _paths(tmp_path)
    _write_raw(paths, "existing")
    _write_artifact(paths, "existing", _artifact())
    monkeypatch.setattr(
        "src.management_web.review_data._backup_timestamp",
        lambda: "20260715T123456Z",
    )

    write_management_decision(
        paths,
        "existing",
        ManagementReviewRequest(status="approved", notes=""),
    )
    before_second_write = (paths.reviews_dir / "existing" / "review.json").read_text(
        encoding="utf-8"
    )
    write_management_decision(
        paths,
        "existing",
        ManagementReviewRequest(status="needs_attention", notes=""),
    )

    backups = sorted(
        (paths.reviews_dir / "existing").glob("review.before-management-review.*.json")
    )
    assert len(backups) == 2
    assert any(json.loads(path.read_text(encoding="utf-8"))["source"] for path in backups)
    assert any(path.read_text(encoding="utf-8") == before_second_write for path in backups)


def test_management_only_decision_artifact_keeps_queue_status_pending(tmp_path: Path) -> None:
    """Decision-only artifacts should not be mistaken for completed pre-analysis."""
    paths = _paths(tmp_path)
    _write_raw(paths, "pending")

    write_management_decision(
        paths,
        "pending",
        ManagementReviewRequest(status="skipped", notes=""),
    )
    queue = build_review_queue(paths, status="all", decision="all", limit=10, offset=0, query=None)

    assert queue.items[0].status == "pending"
    assert queue.items[0].management_status == "skipped"


def test_write_management_decision_rejects_missing_raw_source(tmp_path: Path) -> None:
    """Decision writes should require a matching raw HTML source."""
    paths = _paths(tmp_path)

    with pytest.raises(FileNotFoundError, match="Source not found"):
        write_management_decision(
            paths,
            "missing",
            ManagementReviewRequest(status="approved", notes=""),
        )


def test_write_management_decision_rejects_unsafe_source_id(tmp_path: Path) -> None:
    """Decision writes should use the same source ID safety gate as reads."""
    paths = _paths(tmp_path)

    with pytest.raises(ValueError, match="Invalid source_id"):
        write_management_decision(
            paths,
            "../secret",
            ManagementReviewRequest(status="approved", notes=""),
        )


def test_write_management_decision_does_not_mutate_raw_or_wiki_files(tmp_path: Path) -> None:
    """Decision writes should be scoped to the selected review artifact."""
    paths = _paths(tmp_path)
    paths.wiki_dir.mkdir(parents=True)
    wiki_page = paths.wiki_dir / "page.md"
    wiki_page.write_text("wiki", encoding="utf-8")
    _write_raw(paths, "source", markdown="Original markdown")
    raw_html = paths.raw_dir / "source.html"
    raw_md = paths.raw_dir / "source.md"
    raw_html_text = raw_html.read_text(encoding="utf-8")
    raw_md_text = raw_md.read_text(encoding="utf-8")

    write_management_decision(
        paths,
        "source",
        ManagementReviewRequest(status="skipped", notes=""),
    )

    assert raw_html.read_text(encoding="utf-8") == raw_html_text
    assert raw_md.read_text(encoding="utf-8") == raw_md_text
    assert wiki_page.read_text(encoding="utf-8") == "wiki"


def test_read_raw_markdown_returns_available_content(tmp_path: Path) -> None:
    """Raw source reading should return local Markdown without writing files."""
    paths = _paths(tmp_path)
    _write_raw(paths, "source", markdown="Local source text")

    raw = read_raw_markdown(paths, "source")

    assert raw.available is True
    assert raw.content == "Local source text"
    assert raw.path == str(paths.raw_dir / "source.md")


def test_read_raw_markdown_returns_unavailable_when_sidecar_missing(tmp_path: Path) -> None:
    """Missing Markdown sidecars should produce an unavailable read-only response."""
    paths = _paths(tmp_path)
    _write_raw(paths, "source", markdown=None)

    raw = read_raw_markdown(paths, "source")

    assert raw.available is False
    assert raw.content == ""
    assert raw.path is None


def _full_coverage_artifact() -> dict[str, Any]:
    """Return an artifact containing all supported entity groups."""
    llm_output: dict[str, Any] = {
        "source_summary": {"summary": "Full coverage summary."},
        "topics": [{"topic_title": "Topic A", "topic_tags": ["topic-a"]}],
        "glossary": [{"term": "Term A", "tags": ["glossary-a"]}],
        "industry_trends": [{"trend_title": "Trend A", "trend_tags": ["trend-a"]}],
        "how_to": [{"question_title": "How to cache prompts", "answer_summary": "Cache prefixes."}],
        "tools": [
            {"name": "Tool A", "short_description": "Tool summary.", "proposed_tags": ["tool-a"]}
        ],
        "foundation_models": [
            {
                "model_name": "Model A",
                "operational_profile": "Model profile.",
                "proposed_tags": ["model-a"],
            }
        ],
        "implementation_studies": [{"title": "Study A", "overview": "Study overview."}],
        "roundup_signals": [{"signal_title": "Signal A", "summary": "Signal summary."}],
        "interview_insights": [{"insight_title": "Insight A", "summary": "Insight summary."}],
    }
    return {
        "source": {"title": "Full Coverage Article"},
        "llm_output": llm_output,
        "review": _review_tree_from_llm_output(llm_output),
    }


def test_normalize_all_supported_entity_groups(tmp_path: Path) -> None:
    """Source detail should normalize all nine supported entity groups."""
    paths = _paths(tmp_path)
    _write_raw(paths, "full")
    _write_artifact(paths, "full", _full_coverage_artifact())

    detail = get_source_detail(paths, "full")

    assert [group.group for group in detail.entities.groups] == [
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
    assert detail.entities.groups[3].items[0].title == "How to cache prompts"
    assert detail.entities.groups[6].section == "source_specific_insights"


def test_queue_counts_include_all_supported_entity_groups(tmp_path: Path) -> None:
    """Queue rows should expose counts for every supported entity group."""
    paths = _paths(tmp_path)
    _write_raw(paths, "full")
    _write_artifact(paths, "full", _full_coverage_artifact())

    queue = build_review_queue(paths, status="in_progress", limit=10, offset=0, query=None)

    counts = queue.items[0].entity_counts
    assert counts.topics == 1
    assert counts.how_to == 1
    assert counts.tools == 1
    assert counts.models == 1
    assert counts.implementation_studies == 1
    assert counts.signals == 1
    assert counts.interview_insights == 1


def test_update_review_entity_writes_how_to_title_to_review_tree(tmp_path: Path) -> None:
    """How-to title edits should write review sections and mirror llm_output."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    llm_output: dict[str, Any] = {
        "how_to": [{"question_title": "Old how-to", "answer_summary": "Old answer."}]
    }
    _write_artifact(
        paths,
        "editable",
        {"llm_output": llm_output, "review": _review_tree_from_llm_output(llm_output)},
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="how_to", index=0, title="How to use prompt caching"),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["review"]["how_to"][0]["sections"]["question_title"]["final_text"] == (
        "How to use prompt caching"
    )
    assert artifact["llm_output"]["how_to"][0]["question_title"] == "How to use prompt caching"
    assert scalar_value(artifact["review"]["how_to"][0], "question_title") == (
        "How to use prompt caching"
    )


def test_update_review_entity_writes_tools_description_to_review_tree(tmp_path: Path) -> None:
    """Tool description edits should write the mapped review section."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    llm_output: dict[str, Any] = {
        "tools": [{"name": "Tool A", "short_description": "Old description."}]
    }
    _write_artifact(
        paths,
        "editable",
        {"llm_output": llm_output, "review": _review_tree_from_llm_output(llm_output)},
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="tools", index=0, description="Better tool description."),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["review"]["tools"][0]["sections"]["short_description"]["final_text"] == (
        "Better tool description."
    )


def test_update_review_entity_writes_model_tags_to_review_tree(tmp_path: Path) -> None:
    """Model tag edits should write review.tags.final_tags."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    llm_output: dict[str, Any] = {
        "foundation_models": [
            {"model_name": "Model A", "operational_profile": "Profile.", "proposed_tags": ["old"]}
        ]
    }
    _write_artifact(
        paths,
        "editable",
        {"llm_output": llm_output, "review": _review_tree_from_llm_output(llm_output)},
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="models", index=0, tags=["frontier-model", "local-model"]),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["review"]["foundation_models"][0]["tags"]["final_tags"] == [
        "frontier-model",
        "local-model",
    ]
    assert reviewed_tags(artifact["review"]["foundation_models"][0]) == [
        "frontier-model",
        "local-model",
    ]


def test_update_review_entity_writes_signal_and_insight_descriptions(tmp_path: Path) -> None:
    """Source-specific insight descriptions should write review summary sections."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    llm_output: dict[str, Any] = {
        "roundup_signals": [{"signal_title": "Signal A", "summary": "Old signal summary."}],
        "interview_insights": [{"insight_title": "Insight A", "summary": "Old insight summary."}],
    }
    _write_artifact(
        paths,
        "editable",
        {"llm_output": llm_output, "review": _review_tree_from_llm_output(llm_output)},
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="signals", index=0, description="Updated signal summary."),
    )
    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(
            group="interview_insights",
            index=0,
            description="Updated insight summary.",
        ),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["review"]["roundup_signals"][0]["sections"]["summary"]["final_text"] == (
        "Updated signal summary."
    )
    assert artifact["review"]["interview_insights"][0]["sections"]["summary"]["final_text"] == (
        "Updated insight summary."
    )


def test_update_review_entity_writes_implementation_study_title_to_review_tree(
    tmp_path: Path,
) -> None:
    """Implementation study title edits should write review sections and mirror llm_output."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    llm_output: dict[str, Any] = {
        "implementation_studies": [{"title": "Old study", "overview": "Old overview."}]
    }
    _write_artifact(
        paths,
        "editable",
        {"llm_output": llm_output, "review": _review_tree_from_llm_output(llm_output)},
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="implementation_studies", index=0, title="Updated study"),
    )

    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["review"]["implementation_studies"][0]["sections"]["title"]["final_text"] == (
        "Updated study"
    )
    assert artifact["llm_output"]["implementation_studies"][0]["title"] == "Updated study"


def test_hiding_how_to_rejects_from_normal_detail_output(tmp_path: Path) -> None:
    """Hidden how-tos should disappear from default detail output and queue counts."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    llm_output: dict[str, Any] = {
        "how_to": [{"question_title": "Hide me", "answer_summary": "Answer."}]
    }
    _write_artifact(
        paths,
        "editable",
        {"llm_output": llm_output, "review": _review_tree_from_llm_output(llm_output)},
    )

    update_review_entity(
        paths,
        "editable",
        EntityEditRequest(group="how_to", index=0, hidden=True),
    )

    detail = get_source_detail(paths, "editable")
    queue = build_review_queue(paths, status="in_progress", limit=10, offset=0, query=None)
    how_to_group = next(group for group in detail.entities.groups if group.group == "how_to")
    assert how_to_group.items[0].hidden is True
    assert queue.items[0].entity_counts.how_to == 0
    artifact = json.loads((paths.reviews_dir / "editable" / "review.json").read_text())
    assert artifact["review"]["how_to"][0]["proposal_status"] == "rejected"
    assert proposal_is_included(artifact["review"]["how_to"][0]) is False


def test_update_review_entity_returns_conflict_when_review_node_missing(tmp_path: Path) -> None:
    """Entity edits should reject llm_output-only entities without a review node."""
    paths = _paths(tmp_path)
    _write_raw(paths, "editable")
    _write_artifact(
        paths,
        "editable",
        {"llm_output": {"how_to": [{"question_title": "Orphan how-to"}]}, "review": {}},
    )

    with pytest.raises(EntityEditConflictError, match="Review node missing"):
        update_review_entity(
            paths,
            "editable",
            EntityEditRequest(group="how_to", index=0, title="Edited"),
        )


def test_finish_review_rejects_unsupported_entity_coverage(tmp_path: Path) -> None:
    """Finish should reject artifacts with future entity lists not covered by the UI."""
    paths = _paths(tmp_path)
    _write_raw(paths, "ready")
    artifact = _artifact()
    llm_output = cast(dict[str, Any], artifact["llm_output"])
    llm_output["future_entities"] = [{"title": "Future entity"}]
    _write_artifact(paths, "ready", artifact)

    with pytest.raises(FinishConflictError, match="unsupported entity group"):
        finish_review(paths, "ready", FinishReviewRequest())


def test_unsupported_llm_output_entity_keys_detects_unknown_entity_lists() -> None:
    """Unsupported entity detection should scan all llm_output entity lists."""
    llm_output: dict[str, Any] = {
        "source_summary": {"summary": "Summary only."},
        "topics": [{"topic_title": "Known topic"}],
        "future_entities": [{"title": "Future entity"}],
        "notes": ["not", "entity", "lists"],
    }

    assert unsupported_llm_output_entity_keys(llm_output) == ["future_entities"]


@pytest.mark.parametrize("source_id", ["../secret", "nested/source", "source.json", ""])
def test_validate_source_id_rejects_path_traversal(source_id: str) -> None:
    """Source IDs must never be interpreted as arbitrary filesystem paths."""
    with pytest.raises(ValueError, match="Invalid source_id"):
        validate_source_id(source_id)


def test_build_review_tag_registry_merges_config_and_review_tags(tmp_path: Path) -> None:
    """Tag registry should include configured tags and tags observed in review artifacts."""
    paths = _paths(tmp_path)
    config_dir = paths.repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "review_tags_topics.yaml").write_text("tags:\n- registry-tag\n", encoding="utf-8")
    _write_artifact(
        paths,
        "tagged",
        {
            "source": {"title": "Tagged"},
            "llm_output": {
                "topics": [{"topic_title": "Topic", "topic_tags": ["review-tag"]}],
            },
            "review": {
                "topics": [
                    _review_node({"topic_title": "Topic", "topic_tags": ["review-tag"]}),
                ],
            },
        },
    )

    response = build_review_tag_registry(paths)

    names = [entry.name for entry in response.tags]
    assert "registry-tag" in names
    assert "review-tag" in names
    review_tag = next(entry for entry in response.tags if entry.name == "review-tag")
    assert review_tag.source == "reviews"
    assert review_tag.usage_count == 1


def test_build_review_tag_registry_sorts_by_usage_then_name(tmp_path: Path) -> None:
    """Tag registry should sort by usage count descending, then alphabetically."""
    paths = _paths(tmp_path)
    config_dir = paths.repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "review_tags_topics.yaml").write_text(
        "tags:\n- alpha\n- beta\n- gamma\n",
        encoding="utf-8",
    )
    _write_artifact(
        paths,
        "one",
        {
            "source": {"title": "One"},
            "llm_output": {"topics": [{"topic_title": "T1", "topic_tags": ["beta", "gamma"]}]},
            "review": {
                "topics": [
                    _review_node({"topic_title": "T1", "topic_tags": ["beta", "gamma"]}),
                ],
            },
        },
    )
    _write_artifact(
        paths,
        "two",
        {
            "source": {"title": "Two"},
            "llm_output": {"topics": [{"topic_title": "T2", "topic_tags": ["gamma"]}]},
            "review": {"topics": [_review_node({"topic_title": "T2", "topic_tags": ["gamma"]})]},
        },
    )

    response = build_review_tag_registry(paths)

    assert [entry.name for entry in response.tags] == ["gamma", "beta", "alpha"]
