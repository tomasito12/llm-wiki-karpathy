"""Tests for per-section regeneration merge helpers."""

from __future__ import annotations

from typing import Any

from src.ingest_review.schema import LlmClassificationOutput
from src.ingest_review.source_regen import apply_regenerated_source_section


def test_apply_regenerated_source_section_updates_llm_and_review() -> None:
    """Regeneration merge writes LLM text and resets review to pending."""
    llm = LlmClassificationOutput().model_dump(mode="json")
    llm["source_summary"]["summary"] = "old"
    rev = {
        "source_summary": {
            "summary": {
                "status": "approved",
                "final_text": None,
                "notes": None,
                "section_regeneration_meta": None,
            },
        },
    }
    art: dict[str, Any] = {"artifact_schema_version": 2, "llm_output": llm, "review": rev}
    apply_regenerated_source_section(
        art,
        "summary",
        "new summary text",
        model="gpt-test",
        prompt_version="2",
    )
    assert art["llm_output"]["source_summary"]["summary"] == "new summary text"
    assert art["review"]["source_summary"]["summary"]["status"] == "pending"
    meta = art["review"]["source_summary"]["summary"]["section_regeneration_meta"]
    assert isinstance(meta, dict)
    assert meta["regen_count"] == 1
    assert meta["model"] == "gpt-test"
