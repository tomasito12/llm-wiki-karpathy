"""Tests for the management web FastAPI endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.management_web.api import create_app
from src.management_web.models import MANAGEMENT_WEB_WRITE_CAPABILITIES
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


def _write_artifact(
    paths: WikiPaths,
    source_id: str,
    *,
    finished: bool = False,
    management_status: str | None = None,
) -> None:
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
    if management_status is not None:
        artifact["management_review"] = {
            "status": management_status,
            "reviewed_at": "2026-07-15T12:34:56Z",
            "reviewed_by": "plischke",
            "notes": "",
        }
    (review_dir / "review.json").write_text(json.dumps(artifact), encoding="utf-8")


def test_health_endpoint_reports_write_enabled_mode(tmp_path: Path) -> None:
    """Health should identify the management web service and enabled write capabilities."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "service": "management-web",
        "mode": "write_enabled",
        "capabilities": list(MANAGEMENT_WEB_WRITE_CAPABILITIES),
    }


def test_config_endpoint_returns_safe_resolved_paths(tmp_path: Path) -> None:
    """Config should expose selected resolved paths without secrets."""
    paths = _paths(tmp_path)
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "write_enabled"
    assert payload["capabilities"] == list(MANAGEMENT_WEB_WRITE_CAPABILITIES)
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
    assert payload["decision_counts"]["not_reviewed"] == 1
    assert [item["source_id"] for item in payload["items"]] == ["api-source"]
    assert payload["items"][0]["management_status"] is None


def test_review_queue_endpoint_filters_management_decisions_by_default(tmp_path: Path) -> None:
    """Queue endpoint should default to undecided work inside the selected status."""
    paths = _paths(tmp_path)
    _write_raw(paths, "undecided")
    _write_artifact(paths, "undecided")
    _write_raw(paths, "approved")
    _write_artifact(paths, "approved", management_status="approved")
    client = TestClient(create_app(paths=paths))

    default_response = client.get("/api/review/queue", params={"status": "in_progress"})
    all_response = client.get(
        "/api/review/queue",
        params={"status": "in_progress", "decision": "all"},
    )
    approved_response = client.get(
        "/api/review/queue",
        params={"status": "in_progress", "decision": "approved"},
    )

    assert default_response.status_code == 200
    assert [item["source_id"] for item in default_response.json()["items"]] == ["undecided"]
    assert all_response.status_code == 200
    assert {item["source_id"] for item in all_response.json()["items"]} == {
        "approved",
        "undecided",
    }
    assert approved_response.status_code == 200
    assert [item["source_id"] for item in approved_response.json()["items"]] == ["approved"]
    assert default_response.json()["decision_counts"]["not_reviewed"] == 1
    assert default_response.json()["decision_counts"]["approved"] == 1


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
    assert payload["management_review"] is None
    assert payload["debug"]["artifact"]["llm_output"]["source_summary"]["summary"] == "API summary"


def test_read_endpoints_return_management_decision_state(tmp_path: Path) -> None:
    """Read endpoints should expose management decision state separately from analysis status."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source", management_status="approved")
    client = TestClient(create_app(paths=paths))

    queue_response = client.get(
        "/api/review/queue",
        params={"status": "in_progress", "decision": "all"},
    )
    detail_response = client.get("/api/review/source/api-source")

    assert queue_response.status_code == 200
    assert queue_response.json()["items"][0]["management_status"] == "approved"
    assert detail_response.status_code == 200
    assert detail_response.json()["management_review"]["status"] == "approved"


def test_decision_endpoint_writes_decision_and_backup(tmp_path: Path) -> None:
    """PATCH decision should write management_review and back up existing artifacts."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch(
        "/api/review/source/api-source/decision",
        json={"status": "approved", "notes": "Looks good."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_id"] == "api-source"
    assert payload["management_review"]["status"] == "approved"
    assert payload["management_review"]["reviewed_by"] == "plischke"
    assert payload["management_review"]["notes"] == "Looks good."
    assert payload["backup_path"] is not None
    artifact = json.loads((paths.reviews_dir / "api-source" / "review.json").read_text())
    assert artifact["management_review"]["status"] == "approved"
    assert Path(payload["backup_path"]).is_file()


def test_decision_endpoint_creates_artifact_without_backup_when_missing(tmp_path: Path) -> None:
    """PATCH decision may create review.json for a raw source that has no artifact yet."""
    paths = _paths(tmp_path)
    _write_raw(paths, "pending-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch(
        "/api/review/source/pending-source/decision",
        json={"status": "skipped"},
    )

    assert response.status_code == 200
    assert response.json()["backup_path"] is None
    artifact = json.loads((paths.reviews_dir / "pending-source" / "review.json").read_text())
    assert artifact["management_review"]["status"] == "skipped"


def test_decision_endpoint_rejects_missing_raw_source(tmp_path: Path) -> None:
    """PATCH decision should 404 when the selected raw source does not exist."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.patch("/api/review/source/missing/decision", json={"status": "approved"})

    assert response.status_code == 404


def test_decision_endpoint_rejects_unsafe_source_id(tmp_path: Path) -> None:
    """PATCH decision should reject unsafe source IDs before filesystem writes."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.patch("/api/review/source/source.json/decision", json={"status": "approved"})

    assert response.status_code == 400
    assert "Invalid source_id" in response.json()["detail"]


def test_decision_endpoint_rejects_invalid_status(tmp_path: Path) -> None:
    """PATCH decision should return 400 for unsupported decision statuses."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch(
        "/api/review/source/api-source/decision",
        json={"status": "finished"},
    )

    assert response.status_code == 400
    assert "Invalid management review status" in response.json()["detail"]


def test_decision_endpoint_returns_validation_error_for_malformed_body(
    tmp_path: Path,
) -> None:
    """PATCH decision should keep malformed request bodies on FastAPI's 422 path."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch("/api/review/source/api-source/decision", json={"notes": ""})

    assert response.status_code == 422


def test_entity_endpoint_updates_entity_and_returns_refreshed_source(tmp_path: Path) -> None:
    """PATCH entity should update the artifact and return the refreshed source detail."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch(
        "/api/review/source/api-source/entity",
        json={
            "group": "topics",
            "index": 0,
            "title": "Edited topic",
            "description": "Edited description.",
            "tags": [" api ", "edited", "api"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_id"] == "api-source"
    assert payload["group"] == "topics"
    assert payload["index"] == 0
    assert Path(payload["backup_path"]).is_file()
    assert payload["source"]["entities"]["topics"][0]["title"] == "Edited topic"
    assert payload["source"]["entities"]["topics"][0]["description"] == "Edited description."
    assert payload["source"]["entities"]["topics"][0]["tags"] == ["api", "edited"]
    artifact = json.loads((paths.reviews_dir / "api-source" / "review.json").read_text())
    assert artifact["llm_output"]["topics"][0]["topic_title"] == "Edited topic"


def test_entity_endpoint_hides_entity(tmp_path: Path) -> None:
    """PATCH entity should persist hidden review_state metadata."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch(
        "/api/review/source/api-source/entity",
        json={"group": "topics", "index": 0, "hidden": True},
    )

    assert response.status_code == 200
    raw_state = response.json()["source"]["entities"]["topics"][0]["raw"]["review_state"]
    assert raw_state["hidden"] is True
    assert raw_state["hidden_by"] == "plischke"


def test_entity_endpoint_rejects_invalid_requests(tmp_path: Path) -> None:
    """PATCH entity should map data-layer safety failures to 400 or 404."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    assert (
        client.patch(
            "/api/review/source/source.json/entity",
            json={"group": "topics", "index": 0, "title": "Edited"},
        ).status_code
        == 400
    )
    assert (
        client.patch(
            "/api/review/source/missing/entity",
            json={"group": "topics", "index": 0, "title": "Edited"},
        ).status_code
        == 404
    )
    assert (
        client.patch(
            "/api/review/source/api-source/entity",
            json={"group": "tools", "index": 0, "title": "Edited"},
        ).status_code
        == 400
    )
    assert (
        client.patch(
            "/api/review/source/api-source/entity",
            json={"group": "topics", "index": 99, "title": "Edited"},
        ).status_code
        == 400
    )
    assert (
        client.patch(
            "/api/review/source/api-source/entity",
            json={"group": "topics", "index": 0},
        ).status_code
        == 400
    )
    assert (
        client.patch(
            "/api/review/source/api-source/entity",
            json={"group": "topics", "index": 0, "tags": ["api", " "]},
        ).status_code
        == 400
    )
    assert (
        client.patch("/api/review/source/api-source/entity", json={"group": "topics"}).status_code
        == 422
    )


def test_finish_endpoint_marks_review_finished_and_approved(tmp_path: Path) -> None:
    """PATCH finish should write lifecycle completion and approved management state."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    client = TestClient(create_app(paths=paths))

    response = client.patch("/api/review/source/api-source/finish", json={"notes": "Done"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_id"] == "api-source"
    assert payload["management_review"]["status"] == "approved"
    assert payload["management_review"]["notes"] == "Done"
    assert payload["review_finished_at"].endswith("Z")
    assert Path(payload["backup_path"]).is_file()
    artifact = json.loads((paths.reviews_dir / "api-source" / "review.json").read_text())
    assert artifact["review_analytics"]["review_finished_at"] == payload["review_finished_at"]
    assert artifact["management_review"]["status"] == "approved"


def test_finish_endpoint_returns_conflict_for_non_approved_decision(tmp_path: Path) -> None:
    """PATCH finish should return 409 when an existing non-approved decision blocks it."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source", management_status="needs_attention")
    client = TestClient(create_app(paths=paths))

    conflict_response = client.patch("/api/review/source/api-source/finish", json={})
    forced_response = client.patch(
        "/api/review/source/api-source/finish",
        json={"force": True},
    )

    assert conflict_response.status_code == 409
    assert "conflicts with existing management decision" in conflict_response.json()["detail"]
    assert forced_response.status_code == 200
    assert forced_response.json()["management_review"]["status"] == "approved"


def test_finish_endpoint_rejects_invalid_and_missing_sources(tmp_path: Path) -> None:
    """PATCH finish should map source and artifact safety failures to 400 or 404."""
    paths = _paths(tmp_path)
    _write_raw(paths, "missing-artifact")
    client = TestClient(create_app(paths=paths))

    assert client.patch("/api/review/source/source.json/finish", json={}).status_code == 400
    assert client.patch("/api/review/source/missing/finish", json={}).status_code == 404
    assert client.patch("/api/review/source/missing-artifact/finish", json={}).status_code == 404
    assert client.patch("/api/review/source/missing-artifact/finish", json=[]).status_code == 422


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
