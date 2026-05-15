"""Tests for unified why_it_matters source chapter migration."""

from __future__ import annotations

from src.ingest_review.artifact import (
    migrate_llm_source_summary_dict,
    migrate_review_source_summary_unified_why,
)
from src.ingest_review.providers.openai_provider import (
    SOURCE_CHAPTERS_RUBRIC,
    _section_regen_rubric,
)
from src.ingest_review.schema import SOURCE_SUMMARY_SCALAR_KEYS, SourceSummaryBlock


def test_source_summary_scalar_keys_excludes_legacy_automation_fields() -> None:
    """Merged schema has no separate implications_automation or practical_relevance keys."""
    assert "why_it_matters" in SOURCE_SUMMARY_SCALAR_KEYS
    assert "implications_automation" not in SOURCE_SUMMARY_SCALAR_KEYS
    assert "practical_relevance" not in SOURCE_SUMMARY_SCALAR_KEYS


def test_migrate_merges_legacy_three_fields_into_why_it_matters() -> None:
    """Legacy LLM dict concatenates three fields into why_it_matters."""
    raw = {
        "why_it_matters": "Part A.",
        "implications_automation": "Part B.",
        "practical_relevance": "Part C.",
    }
    out = migrate_llm_source_summary_dict(raw)
    assert "implications_automation" not in out
    assert "practical_relevance" not in out
    assert "Part A." in out["why_it_matters"]
    assert "Part B." in out["why_it_matters"]
    assert "Part C." in out["why_it_matters"]


def test_migrate_review_merges_legacy_review_nodes() -> None:
    """Legacy review nodes merge into why_it_matters and drop obsolete keys."""
    artifact = {
        "llm_output": {
            "source_summary": {
                "why_it_matters": "L1",
                "implications_automation": "L2",
                "practical_relevance": "L3",
            }
        },
        "review": {
            "source_summary": {
                "why_it_matters": {"status": "pending", "final_text": None, "notes": None},
                "implications_automation": {
                    "status": "approved",
                    "final_text": None,
                    "notes": None,
                },
                "practical_relevance": {"status": "pending", "final_text": None, "notes": None},
            }
        },
    }
    migrate_review_source_summary_unified_why(artifact)
    rev = artifact["review"]["source_summary"]
    assert "implications_automation" not in rev
    assert "practical_relevance" not in rev
    why_node = rev["why_it_matters"]
    assert why_node.get("status") == "modified"


def test_source_summary_block_no_legacy_fields() -> None:
    """SourceSummaryBlock only exposes unified why_it_matters."""
    block = SourceSummaryBlock(why_it_matters="unified")
    assert block.why_it_matters == "unified"
    assert not hasattr(block, "implications_automation") or "implications_automation" not in (
        SourceSummaryBlock.model_fields
    )


def test_source_chapters_rubric_single_why_it_matters() -> None:
    """Rubric defines one why_it_matters block, not separate automation sections."""
    assert "**why_it_matters**" in SOURCE_CHAPTERS_RUBRIC
    assert "**implications_automation**" not in SOURCE_CHAPTERS_RUBRIC
    assert "**practical_relevance**" not in SOURCE_CHAPTERS_RUBRIC


def test_rubric_discourages_forced_service_automation() -> None:
    """Unified rubric warns against generic service-automation paragraphs."""
    lower = SOURCE_CHAPTERS_RUBRIC.lower()
    assert "service automation" in lower
    assert "do not" in lower or "only when" in lower


def test_section_regen_rubric_no_orphan_keys() -> None:
    """Section regen map has why_it_matters only, not removed keys."""
    assert _section_regen_rubric("why_it_matters")
    assert _section_regen_rubric("implications_automation") == ""
    assert _section_regen_rubric("practical_relevance") == ""
