"""Tests for review artifact assembly."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest_review.artifact import (
    aggregate_review_status,
    build_new_artifact,
    default_analysis_meta,
    default_review_for_llm_output,
    migrate_artifact_to_v2,
    review_artifact_path,
    save_artifact,
    touch_review_session,
)
from src.ingest_review.extract import SourceDocument, load_readwise_pair
from src.ingest_review.schema import LlmClassificationOutput


def _minimal_doc(tmp_path: Path) -> SourceDocument:
    """Build a tiny SourceDocument in a temp raw dir."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "s-01id"
    html = raw / f"{stem}.html"
    md = raw / f"{stem}.md"
    html.write_text("<p>hi</p>", encoding="utf-8")
    md.write_text("---\ntitle: Hi\n---\n", encoding="utf-8")
    return load_readwise_pair(html)


def test_default_review_all_pending() -> None:
    """Fresh review overlay marks every node pending."""
    llm = LlmClassificationOutput().model_dump(mode="json")
    rev = default_review_for_llm_output(llm)
    assert rev["source_summary"]["summary"]["status"] == "pending"
    assert rev["source_summary"]["why_it_matters"]["status"] == "pending"
    assert rev["source_summary"]["key_insights"]["llm_list"] == []
    assert rev["roundup"]["status"] == "pending"


def test_migrate_v1_artifact_maps_legacy_source_summary_fields() -> None:
    """v1 context_limitations / contradictions / string insights map to v2 keys."""
    art: dict[str, Any] = {
        "artifact_schema_version": 1,
        "llm_output": {
            "source_summary": {
                "why_it_matters": "w",
                "key_insights": "- one\n- two",
                "implications_automation": "i",
                "context_limitations": "legacy lim",
                "contradictions": "legacy c",
                "sources": ["https://x"],
            },
            "glossary": [],
            "tools": [],
            "foundation_models": [],
            "how_to": [],
            "enterprise_studies": [],
            "industry_trends": [],
            "roundup": {"is_roundup": False, "reasoning": "", "confidence": 0.0},
        },
        "review": {"source_summary": {}},
    }
    migrate_artifact_to_v2(art)
    assert art["artifact_schema_version"] == 2
    ss = art["llm_output"]["source_summary"]
    assert ss["limitations_and_open_questions"] == "legacy lim"
    assert ss["contradictions_and_skepticism"] == "legacy c"
    assert ss["key_insights"] == ["one", "two"]
    assert ss["summary"] == ""


def test_artifact_reexports_apply_regenerated_source_section() -> None:
    """Dashboard imports merge helper from artifact; ensure re-export is wired."""
    import src.ingest_review.artifact as artifact_mod

    assert hasattr(artifact_mod, "apply_regenerated_source_section")
    assert callable(artifact_mod.apply_regenerated_source_section)


def test_build_new_artifact_has_expected_keys(tmp_path: Path) -> None:
    """Artifact bundles source metadata and llm_output."""
    raw = tmp_path / "raw"
    raw.mkdir()
    stem = "s-01id"
    (raw / f"{stem}.html").write_text("<p>hi</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\ntitle: Hi\n---\n", encoding="utf-8")
    doc = load_readwise_pair(raw / f"{stem}.html")
    parsed = LlmClassificationOutput()
    meta = default_analysis_meta(provider="openai", model="gpt-test", prompt_version="1")
    art = build_new_artifact(doc, parsed, analysis_meta=meta, root=tmp_path)
    assert art["artifact_schema_version"] == 2
    assert art["source"]["source_id"] == stem
    assert art["llm_output"]["roundup"]["is_roundup"] is False


def test_aggregate_review_status_all_pending(tmp_path: Path) -> None:
    """Default artifact review is all pending."""
    doc = _minimal_doc(tmp_path)
    art = build_new_artifact(
        doc,
        LlmClassificationOutput(),
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"


def test_save_artifact_roundtrip(tmp_path: Path) -> None:
    """save_artifact writes JSON loadable by json module."""
    import json

    doc = _minimal_doc(tmp_path)
    art = build_new_artifact(
        doc,
        LlmClassificationOutput(),
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    path = review_artifact_path(doc.source_id, state_reviews=tmp_path / "state" / "reviews")
    touch_review_session(art)
    save_artifact(path, art)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["source"]["source_id"] == doc.source_id
