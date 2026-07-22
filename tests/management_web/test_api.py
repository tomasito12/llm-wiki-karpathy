"""Tests for the management web FastAPI endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

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


def _review_node(llm_item: dict[str, Any]) -> dict[str, Any]:
    """Return a render-aligned review node for API test artifacts."""
    return {
        "proposal_status": "approved",
        "llm_item": llm_item,
        "sections": {},
        "tags": {},
    }


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
    llm_output: dict[str, Any] = {
        "source_summary": {"summary": "API summary", "key_insights": ["API insight"]},
        "topics": [{"topic_title": "API Topic", "topic_tags": ["api"]}],
        "glossary": [{"term": "API Term"}],
        "industry_trends": [{"trend_title": "API Trend"}],
    }
    artifact: dict[str, Any] = {
        "source": {"title": "API Article", "readwise_id": "rw-api"},
        "review_analytics": {"review_finished_at": review_finished_at},
        "llm_output": llm_output,
        "review": {
            "topics": [_review_node(cast(dict[str, Any], llm_output["topics"][0]))],
            "glossary": [_review_node(cast(dict[str, Any], llm_output["glossary"][0]))],
            "industry_trends": [
                _review_node(cast(dict[str, Any], llm_output["industry_trends"][0]))
            ],
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


def test_health_and_config_accept_server_like_paths(tmp_path: Path) -> None:
    """Health/config should work when create_app receives server-style WikiPaths."""
    root = tmp_path / "srv" / "llm-wiki"
    data = root / "data"
    vault = root / "vault-private"
    paths = WikiPaths(
        repo_root=tmp_path / "app",
        knowledge_root=data,
        vault_root=vault,
        raw_dir=data / "raw" / "readwise",
        reviews_dir=data / "state" / "reviews",
        synthesis_dir=data / "state" / "synthesis",
        graph_path=data / "state" / "wiki_render_graph.json",
        manifest_path=data / "state" / "wiki_render_manifest.json",
        release_dir=data / "state" / "releases",
        preview_dir=data / "tmp" / "synthesis_previews",
        run_dir=data / "tmp" / "synthesis_runs",
        backup_dir=data / "tmp" / "synthesis_backups",
        wiki_dir=vault / "wiki",
        source_pages_dir=vault / "wiki" / "sources" / "full",
        source_index_path=vault / "wiki" / "sources" / "index.md",
        indexes_dir=vault / "wiki" / "indexes",
    )
    paths.raw_dir.mkdir(parents=True)
    paths.reviews_dir.mkdir(parents=True)
    client = TestClient(create_app(paths=paths))

    health = client.get("/api/health")
    config = client.get("/api/config")

    assert health.status_code == 200
    assert health.json()["ok"] is True
    assert config.status_code == 200
    assert config.json()["paths"]["raw_dir"] == str(paths.raw_dir)
    assert config.json()["paths"]["wiki_dir"] == str(paths.wiki_dir)
    assert str(paths.knowledge_root) in config.json()["paths"]["raw_dir"]


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
    assert response.json()["source"]["entities"]["topics"][0]["hidden"] is True
    artifact = json.loads((paths.reviews_dir / "api-source" / "review.json").read_text())
    assert artifact["review"]["topics"][0]["proposal_status"] == "rejected"


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
            json={"group": "future_entities", "index": 0, "title": "Edited"},
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


def test_review_tags_endpoint_returns_registry_and_review_tags(tmp_path: Path) -> None:
    """Tag registry should merge configured tags with tags observed in review artifacts."""
    paths = _paths(tmp_path)
    config_dir = paths.repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "review_tags_topics.yaml").write_text(
        "tags:\n- registry-tag\n- shared-tag\n",
        encoding="utf-8",
    )
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    review_dir = paths.reviews_dir / "extra-source"
    review_dir.mkdir(parents=True)
    (review_dir / "review.json").write_text(
        json.dumps(
            {
                "source": {"title": "Extra"},
                "llm_output": {
                    "topics": [{"topic_title": "Extra Topic", "topic_tags": ["review-only-tag"]}]
                },
                "review": {
                    "topics": [
                        {
                            "proposal_status": "approved",
                            "llm_item": {
                                "topic_title": "Extra Topic",
                                "topic_tags": ["review-only-tag"],
                            },
                            "sections": {},
                            "tags": {},
                        }
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/tags")

    assert response.status_code == 200
    payload = response.json()
    names = [entry["name"] for entry in payload["tags"]]
    assert "registry-tag" in names
    assert "review-only-tag" in names
    assert "api" in names
    review_only = next(entry for entry in payload["tags"] if entry["name"] == "review-only-tag")
    assert review_only["source"] == "reviews"
    assert review_only["usage_count"] == 1
    registry_entry = next(entry for entry in payload["tags"] if entry["name"] == "registry-tag")
    assert registry_entry["source"] == "registry"


def test_review_tags_endpoint_filters_by_group(tmp_path: Path) -> None:
    """Tag endpoint should return the entity-group allowlist when group is set."""
    paths = _paths(tmp_path)
    config_dir = paths.repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "review_tags_trends.yaml").write_text(
        "tags:\n- support-automation\n",
        encoding="utf-8",
    )
    (config_dir / "review_tags_topics.yaml").write_text(
        "tags:\n- topic-only\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/tags", params={"group": "signals"})

    assert response.status_code == 200
    names = [entry["name"] for entry in response.json()["tags"]]
    assert names == ["support-automation"]


def test_review_types_endpoint_returns_tool_kinds(tmp_path: Path) -> None:
    """Types endpoint should return the tool types allowlist for group=tools."""
    paths = _paths(tmp_path)
    config_dir = paths.repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "review_tool_types.yaml").write_text(
        "tags:\n- app\n- terminal\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/types", params={"group": "tools"})

    assert response.status_code == 200
    names = [entry["name"] for entry in response.json()["types"]]
    assert names == ["app", "terminal"]


def test_review_types_endpoint_rejects_non_tools(tmp_path: Path) -> None:
    """Types endpoint should reject non-tool groups."""
    paths = _paths(tmp_path)
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/types", params={"group": "topics"})

    assert response.status_code == 400
    assert "tools" in response.json()["detail"]


def test_review_tags_endpoint_is_deterministic(tmp_path: Path) -> None:
    """Tag registry output should be stable across repeated reads."""
    paths = _paths(tmp_path)
    config_dir = paths.repo_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "review_tags_topics.yaml").write_text(
        "tags:\n- alpha\n- beta\n",
        encoding="utf-8",
    )
    client = TestClient(create_app(paths=paths))

    first = client.get("/api/review/tags").json()
    second = client.get("/api/review/tags").json()

    assert first == second


def test_review_tags_endpoint_does_not_mutate_raw_or_wiki_files(tmp_path: Path) -> None:
    """Reading tag registry must not write to raw or wiki files."""
    paths = _paths(tmp_path)
    _write_raw(paths, "api-source")
    _write_artifact(paths, "api-source")
    wiki_dir = paths.wiki_dir
    wiki_dir.mkdir(parents=True, exist_ok=True)
    wiki_file = wiki_dir / "note.md"
    wiki_file.write_text("unchanged", encoding="utf-8")
    raw_mtime = (paths.raw_dir / "api-source.html").stat().st_mtime_ns
    wiki_mtime = wiki_file.stat().st_mtime_ns
    client = TestClient(create_app(paths=paths))

    response = client.get("/api/review/tags")

    assert response.status_code == 200
    assert (paths.raw_dir / "api-source.html").stat().st_mtime_ns == raw_mtime
    assert wiki_file.stat().st_mtime_ns == wiki_mtime


def test_ops_status_endpoint_returns_json_without_writes(tmp_path: Path) -> None:
    """Ops status should be read-only JSON with a compact summary."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.get("/api/ops/status")

    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert "collected_at" in payload
    assert "summary" in payload
    assert isinstance(payload["status"], dict)


def test_ops_operations_endpoint_returns_allowlisted_operations(tmp_path: Path) -> None:
    """Operations endpoint should expose the MVP allowlist."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.get("/api/ops/operations")

    assert response.status_code == 200
    operation_ids = {item["id"] for item in response.json()["operations"]}
    assert "wiki_lint" in operation_ids
    assert "wiki_render" in operation_ids
    assert "synthesis_batch" in operation_ids


def test_ops_start_run_rejects_unknown_operation(tmp_path: Path) -> None:
    """Unknown operation ids should return HTTP 400."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.post(
        "/api/ops/runs",
        json={"operation_id": "shell_rm_rf", "parameters": {}, "confirmed": False},
    )

    assert response.status_code == 400


def test_ops_start_run_rejects_invalid_parameter(tmp_path: Path) -> None:
    """Invalid parameters should return HTTP 400."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.post(
        "/api/ops/runs",
        json={"operation_id": "synthesis_select", "parameters": {"limit": 0}, "confirmed": False},
    )

    assert response.status_code == 400


def test_ops_start_write_operation_without_confirmation_returns_409(tmp_path: Path) -> None:
    """Write operations should require explicit confirmation."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.post(
        "/api/ops/runs",
        json={"operation_id": "wiki_render", "parameters": {}, "confirmed": False},
    )

    assert response.status_code == 409


def test_ops_start_llm_operation_without_confirmation_returns_409(tmp_path: Path) -> None:
    """LLM-capable operations should require explicit confirmation."""
    client = TestClient(create_app(paths=_paths(tmp_path)))

    response = client.post(
        "/api/ops/runs",
        json={"operation_id": "synthesis_batch", "parameters": {}, "confirmed": False},
    )

    assert response.status_code == 409


def test_ops_start_read_only_operation_does_not_require_confirmation(tmp_path: Path) -> None:
    """Read-only operations should start without confirmation."""
    from src.management_web.ops import OpsRunManager

    paths = _paths(tmp_path)
    app = create_app(paths=paths)
    app.state.ops_runs = OpsRunManager(
        paths=paths,
        command_runner=lambda _command, _cwd: (0, "lint ok", ""),
    )
    client = TestClient(app)

    response = client.post(
        "/api/ops/runs",
        json={"operation_id": "wiki_lint", "parameters": {}, "confirmed": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["operation_id"] == "wiki_lint"
    assert payload["status"] == "queued"


def test_ops_start_run_rejects_second_concurrent_operation(tmp_path: Path) -> None:
    """Only one operation may run at a time in MVP."""
    import time

    from src.management_web.ops import OpsRunManager

    paths = _paths(tmp_path)
    app = create_app(paths=paths)

    def slow_runner(_command: list[str], _cwd: Path) -> tuple[int, str, str]:
        time.sleep(0.2)
        return 0, "", ""

    app.state.ops_runs = OpsRunManager(
        paths=paths,
        command_runner=slow_runner,
    )
    client = TestClient(app)

    first = client.post(
        "/api/ops/runs",
        json={"operation_id": "wiki_lint", "parameters": {}, "confirmed": False},
    )
    assert first.status_code == 200
    second = client.post(
        "/api/ops/runs",
        json={"operation_id": "wiki_lint", "parameters": {}, "confirmed": False},
    )

    assert second.status_code == 409
