"""Tests for review tag slug migration."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest_review.tag_migration import (
    load_migration_map,
    migrate_review_artifact,
    migrate_reviews_root,
    migrate_slug,
    migrate_tag_list,
)


def test_migrate_slug_maps_known_old_slug() -> None:
    """Known legacy slugs map to new ontology slugs."""
    mapping = {"agentic-ai": "agent-systems"}
    assert migrate_slug("agentic-ai", mapping) == "agent-systems"
    assert migrate_slug("unknown-tag", mapping) == "unknown-tag"


def test_migrate_tag_list_remapped_and_deduped() -> None:
    """Tag lists remap, dedupe, and count remaps."""
    mapping = {"ai-evals": "ai-evaluation", "agentic-ai": "agent-systems"}
    result = migrate_tag_list(["agentic-ai", "ai-evals", "agentic-ai"], mapping)
    assert result == ["agent-systems", "ai-evaluation"]


def test_migrate_review_artifact_updates_proposed_tags(tmp_path: Path) -> None:
    """Artifact llm_item and final_tags are migrated in place."""
    artifact = {
        "source": {"source_id": "src-1"},
        "llm_output": {
            "topics": [
                {
                    "topic_title": "Test",
                    "proposed_tags": ["agentic-ai"],
                    "suggested_new_tags": [],
                }
            ]
        },
        "review": {
            "topics": [
                {
                    "llm_item": {"proposed_tags": ["agentic-ai"], "suggested_new_tags": []},
                    "tags": {"final_tags": ["ai-evals"], "approved_new_tags": []},
                }
            ]
        },
    }
    migration_map = {"topics": {"agentic-ai": "agent-systems", "ai-evals": "ai-evaluation"}}
    _, report = migrate_review_artifact(artifact, migration_map, source_id="src-1")
    assert artifact["llm_output"]["topics"][0]["proposed_tags"] == ["agent-systems"]
    assert artifact["review"]["topics"][0]["tags"]["final_tags"] == ["ai-evaluation"]
    assert report.remapped >= 2


def test_migrate_reviews_root_writes_files(tmp_path: Path) -> None:
    """migrate_reviews_root updates review.json on disk."""
    payload = {
        "source": {"source_id": "finished-a"},
        "llm_output": {"topics": [{"proposed_tags": ["llm-wiki"], "suggested_new_tags": []}]},
        "review": {
            "topics": [
                {
                    "llm_item": {"proposed_tags": ["llm-wiki"], "suggested_new_tags": []},
                    "tags": {"final_tags": [], "approved_new_tags": []},
                }
            ]
        },
        "review_analytics": {"review_finished_at": "2026-05-20T10:00:00+00:00"},
    }
    out_dir = tmp_path / "finished-a"
    out_dir.mkdir()
    (out_dir / "review.json").write_text(json.dumps(payload), encoding="utf-8")
    migration_map = load_migration_map()
    summary = migrate_reviews_root(tmp_path, migration_map, dry_run=False)
    assert summary.artifacts_processed == 1
    updated = json.loads((out_dir / "review.json").read_text(encoding="utf-8"))
    assert updated["llm_output"]["topics"][0]["proposed_tags"] == ["knowledge-systems"]


def test_load_migration_map_from_repo_config() -> None:
    """Repo config/tag_migration.yaml loads with expected sections."""
    migration_map = load_migration_map()
    assert "topics" in migration_map
    assert migration_map["topics"].get("agentic-ai") == "agent-systems"
