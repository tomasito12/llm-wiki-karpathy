"""Tests for the read-only management web FastAPI endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.management_web.api import create_app
from src.wiki_paths.config import WikiPaths, default_wiki_paths


def _paths(tmp_path: Path) -> WikiPaths:
    """Return temporary wiki paths with raw and review roots created."""
    paths = default_wiki_paths(tmp_path)
    paths.raw_dir.mkdir(parents=True)
    paths.reviews_dir.mkdir(parents=True)
    return paths


def _write_raw(paths: WikiPaths, source_id: str, *, markdown: str | None = "Raw body") -> None:
    """Create a raw Readwise HTML export and optional Markdown sidecar."""
    (paths.raw_dir / f"{source_id}.html").write_text("<html>Body</html>", encoding="utf-8")
    if markdown is not None:
        (paths.raw_dir / f"{source_id}.md").write_text(markdown, encoding="utf-8")


def _write_artifact(paths: WikiPaths, source_id: str, *, finished: bool = False) -> None:
    """Write a minimal review artifact for API tests."""
    review_dir = paths.reviews_dir / source_id
    review_dir.mkdir(parents=True)
    review_finished_at = "2026-07-15T10:00:00Z" if finished else None
    artifact = {
        "source": {"title": "API Article", "readwise_id": "rw-api"},
        "review_analytics": {"review_finished_at": review_finished_at},
        "llm_output": {
            "source_summary": {"summary": "API summary", "key_insights": ["API insight"]},
            "topics": [{"topic_title": "API Topic", "topic_tags": ["api"]}],
            "glossary": [{"term": "API Term"}],
            "industry_trends": [{"trend_title": "API Trend"}],
        },
    }
    (review_dir / "review.json").write_text(json.dumps(artifact), encoding="utf-8")


def test_health_endpoint_reports_readonly_mode(tmp_path: Path) -> None:
    """Health should identify the management web service and read-only mode."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "service": "management-web", "mode": "readonly"}


def test_config_endpoint_returns_safe_resolved_paths(tmp_path: Path) -> None:
    """Config should expose selected resolved paths without secrets."""
    paths = _paths(tmp_path)
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "readonly"
    assert payload["paths"]["repo_root"] == str(paths.repo_root)
    assert payload["paths"]["raw_dir"] == str(paths.raw_dir)
    assert payload["paths"]["reviews_dir"] == str(paths.reviews_dir)
    assert "OPENAI_API_KEY" not in json.dumps(payload)


def test_review_queue_endpoint_returns_counts_and_items(tmp_path: Path) -> None:
    """Queue endpoint should return filtered review items and status counts."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    _write_raw(paths, "finished-source")
    _write_artifact(paths, "finished-source", finished=True)
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/queue", params={"status": "in_progress"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["counts"]["in_progress"] == 1
    assert payload["counts"]["finished"] == 1
    assert [item["source_id"] for item in payload["items"]] == ["api-source"]


def test_source_detail_endpoint_returns_normalized_artifact(tmp_path: Path) -> None:
    """Source detail endpoint should return human-readable review card data."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source", markdown="Raw article text")
    _write_artifact(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/source/api-source")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_id"] == "api-source"
    assert payload["metadata"]["title"] == "API Article"
    assert payload["summary"]["short"] == "API summary"
    assert payload["entities"]["topics"][0]["title"] == "API Topic"
    assert payload["debug"]["artifact"]["llm_output"]["source_summary"]["summary"] == "API summary"


def test_raw_source_endpoint_returns_available_markdown(tmp_path: Path) -> None:
    """Raw endpoint should return local Markdown content on demand."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source", markdown="Raw article text")
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/source/api-source/raw")

    assert response.status_code == 200
    assert response.json()["available"] is True
    assert response.json()["content"] == "Raw article text"


def test_raw_source_endpoint_returns_unavailable_for_missing_markdown(tmp_path: Path) -> None:
    """Raw endpoint should not fail when a Markdown sidecar is missing."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source", markdown=None)
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/source/api-source/raw")

    assert response.status_code == 200
    assert response.json() == {
        "source_id": "api-source",
        "available": False,
        "content": "",
        "path": None,
    }


def test_invalid_source_id_returns_bad_request(tmp_path: Path) -> None:
    """Invalid source IDs should be rejected before filesystem resolution."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.get("/api/review/source/source.json")

    assert response.status_code == 400
    assert "Invalid source_id" in response.json()["detail"]
