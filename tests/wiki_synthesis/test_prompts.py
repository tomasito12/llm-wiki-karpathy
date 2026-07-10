"""Tests for Stage 2 synthesis prompt construction."""

from __future__ import annotations

from typing import Any

import pytest

from src.wiki_synthesis.input_hash import synthesis_input_hash
from src.wiki_synthesis.prompts import build_prompt_bundle, find_knowledge_page


def test_build_prompt_bundle_contains_grounding_context() -> None:
    """Prompt bundles should include metadata, sources, evidence, and schema."""
    graph = _graph()
    page = graph["knowledge_pages"][0]
    current_hash = synthesis_input_hash(page)

    bundle = build_prompt_bundle(graph, entity_id="topic:local-models")

    assert bundle.prompt_version == 1
    assert bundle.synthesis_input_hash == current_hash
    assert "Category-specific rule:" in bundle.system_prompt
    assert "For topic pages" in bundle.system_prompt
    assert "mixed AI/product/operations team" in bundle.system_prompt
    assert "explain them briefly in context" in bundle.system_prompt
    assert "ENTITY" in bundle.user_prompt
    assert "- entity_id: topic:local-models" in bundle.user_prompt
    assert "SOURCES" in bundle.user_prompt
    assert "source-a: Source A" in bundle.user_prompt
    assert "EVIDENCE" in bundle.user_prompt
    assert "[evidence-a]" in bundle.user_prompt
    assert "Local models run near users." in bundle.user_prompt
    assert '"synthesis_input_hash":' in bundle.user_prompt
    assert '"synthesis_prompt_version": 1' in bundle.user_prompt
    assert '"practical_example":' in bundle.user_prompt
    assert '"workflow_variants":' in bundle.user_prompt
    assert "service automation, chatbot, voicebot" in bundle.user_prompt
    assert "start with the practical function" in bundle.user_prompt
    assert "then name the technical concept or architecture" in bundle.user_prompt
    assert "Do not write in childish" in bundle.user_prompt
    assert current_hash in bundle.user_prompt


def test_build_prompt_bundle_includes_previous_synthesis_as_continuity_only() -> None:
    """Previous cache content should be included but framed as non-authoritative."""
    bundle = build_prompt_bundle(
        _graph(),
        entity_id="topic:local-models",
        previous_cache={
            "synthesis_input_hash": "oldhash",
            "executive_synthesis": "Old synthesis text.",
            "what_to_remember": ["Old point."],
        },
    )

    assert bundle.cached_input_hash == "oldhash"
    assert "PREVIOUS SYNTHESIS" in bundle.user_prompt
    assert "Use this only as continuity context" in bundle.user_prompt
    assert "Old synthesis text." in bundle.user_prompt


def test_build_prompt_bundle_warns_for_single_source_pages() -> None:
    """Single-source prompts should not ask the model to imply consensus."""
    graph = _graph(source_count=1)

    bundle = build_prompt_bundle(graph, entity_id="topic:local-models")

    assert "SINGLE-SOURCE MODE" in bundle.user_prompt
    assert "Do not imply consensus across sources." in bundle.user_prompt
    assert "source-grounded readable summary" in bundle.user_prompt


def test_build_prompt_bundle_uses_relevance_guidance_for_models() -> None:
    """Model prompts should ask for practical relevance instead of forced examples."""
    bundle = build_prompt_bundle(_graph(category="model"), entity_id="model:local-models")

    assert "For foundation model pages" in bundle.system_prompt
    assert "Do not force a workflow example" in bundle.system_prompt
    assert 'Treat practical_example as "Practical relevance"' in bundle.user_prompt
    assert "not as a hypothetical workflow" in bundle.user_prompt
    assert "Use an empty list unless the evidence explicitly describes distinct workflows" in (
        bundle.user_prompt
    )


def test_build_prompt_bundle_requires_workflow_variants_for_how_tos() -> None:
    """How-to prompts should preserve materially different workflows as variants."""
    bundle = build_prompt_bundle(_graph(category="how_to"), entity_id="how_to:local-models")

    assert "For how-to pages" in bundle.system_prompt
    assert "Always include at least one workflow variant for how-to pages." in bundle.user_prompt
    assert "Do not merge incompatible workflows" in bundle.user_prompt


def test_prompt_bundle_messages_are_chat_ready() -> None:
    """Prompt bundles should expose system/user chat messages."""
    messages = build_prompt_bundle(_graph(), entity_id="topic:local-models").messages()

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "expert knowledge synthesizer" in messages[0]["content"]


def test_find_knowledge_page_raises_for_missing_entity() -> None:
    """Missing entities should fail before an LLM call is attempted."""
    with pytest.raises(ValueError, match="Knowledge entity not found"):
        find_knowledge_page(_graph(), entity_id="topic:missing")


def _graph(*, source_count: int = 2, category: str = "topic") -> dict[str, Any]:
    """Return a minimal graph export with one knowledge page."""
    source_ids = ["source-a", "source-b"][:source_count]
    entity_id = f"{category}:local-models"
    path_prefix = "models" if category == "model" else f"{category}s"
    return {
        "sources": [
            {
                "source_id": "source-a",
                "title": "Source A",
                "published_date": "2026-01-01",
                "assessed_as_of": "2026-06-16",
                "tags": ["ai-engineering"],
            },
            {
                "source_id": "source-b",
                "title": "Source B",
                "published_date": "2026-02-01",
                "assessed_as_of": "2026-06-16",
                "tags": ["inference-systems"],
            },
        ],
        "knowledge_pages": [
            {
                "entity_id": entity_id,
                "category": category,
                "slug": "local-models",
                "title": "Local Models",
                "path": f"{path_prefix}/local-models.md",
                "aliases": [],
                "tags": ["ai-engineering"],
                "types": [],
                "source_ids": source_ids,
                "source_count": source_count,
                "evidence_count": 1,
                "value_level": "high",
                "confidence": 0.9,
                "supporting_count": 1,
                "counter_count": 0,
                "uncertainty_count": 0,
                "neutral_count": 0,
                "evidence": [
                    {
                        "evidence_id": "evidence-a",
                        "text": "Local models run near users.",
                        "source_id": "source-a",
                        "source_title": "Source A",
                        "source_date": "2026-01-01",
                        "published_date": "2026-01-01",
                        "assessed_as_of": "2026-06-16",
                        "category": category,
                        "entity_slug": "local-models",
                        "confidence": 0.9,
                        "value_level": "high",
                        "provenance": "summary",
                        "stance": "supporting",
                        "evidence_type": "claim",
                        "field": "knowledge_summary",
                    }
                ],
            }
        ],
    }
