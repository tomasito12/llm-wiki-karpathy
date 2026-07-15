"""Tests for read-only management web review data normalization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.management_web.models import ManagementReviewRequest
from src.management_web.review_data import (
    build_review_queue,
    get_source_detail,
    read_raw_markdown,
    validate_source_id,
    write_management_decision,
)
from src.wiki_paths.config import WikiPaths, default_wiki_paths


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
    artifact: dict[str, object],
) -> None:
    """Write one review artifact under the configured reviews directory."""
    review_dir = paths.reviews_dir / source_id
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text(json.dumps(artifact), encoding="utf-8")


def _artifact(*, finished: bool = False) -> dict[str, object]:
    """Return a minimal but representative review artifact."""
    review_finished_at = "2026-07-15T10:00:00Z" if finished else None
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
        "llm_output": {
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

    queue = build_review_queue(paths, status="all", limit=10, offset=0, query=None)

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
    assert detail.entities.topics[0].title == "Agentic coding workflows"
    assert detail.entities.glossary[0].title == "Retrieval augmented generation"
    assert detail.entities.trends[0].title == "Teams adopt AI review assistants"
    assert detail.debug.artifact["content_sha256"] == "stored-hash"


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

    queue = build_review_queue(paths, status="all", limit=10, offset=0, query=None)

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
    queue = build_review_queue(paths, status="all", limit=10, offset=0, query=None)

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


@pytest.mark.parametrize("source_id", ["../secret", "nested/source", "source.json", ""])
def test_validate_source_id_rejects_path_traversal(source_id: str) -> None:
    """Source IDs must never be interpreted as arbitrary filesystem paths."""
    with pytest.raises(ValueError, match="Invalid source_id"):
        validate_source_id(source_id)
