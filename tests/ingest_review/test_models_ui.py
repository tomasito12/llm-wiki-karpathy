"""Tests for model two-column helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.models_ui import (
    apply_model_scalar_edit,
    build_readonly_models_markdown,
    effective_model_scalar,
    format_model_readonly_markdown,
)


def _sample_node() -> dict:
    return {
        "proposal_status": "approved",
        "llm_item": {
            "model_name": "GPT-5",
            "provider": "OpenAI",
            "operational_summary": "Strong reasoning.",
            "value_level": "high",
            "confidence": 0.95,
            "evidence_type": "benchmark",
        },
        "sections": {},
    }


def test_effective_model_scalar_prefers_final_text() -> None:
    llm = {"model_name": "Draft"}
    sections = {"model_name": {"final_text": "Final", "status": "modified"}}
    assert effective_model_scalar(llm, sections, "model_name") == "Final"


def test_apply_model_scalar_edit_modified_when_differs() -> None:
    sections: dict = {}
    llm = {"provider": "OpenAI"}
    apply_model_scalar_edit(sections, llm, "provider", "Other")
    assert sections["provider"]["status"] == "modified"


def test_format_model_readonly_includes_name() -> None:
    md = format_model_readonly_markdown(_sample_node())
    assert "GPT-5" in md


def test_build_readonly_models_markdown_empty() -> None:
    assert "No model" in build_readonly_models_markdown([])
