"""End-to-end collection, merge, render, and export tests."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render.collect import collect_items
from src.wiki_render.graph_export import graph_export_payload
from src.wiki_render.merge import build_knowledge_graph
from src.wiki_render.render import render_graph


def test_graph_merge_render_and_export_include_stage2_metadata(tmp_path: Path) -> None:
    """The generated graph preserves evidence and source relationships."""
    artifacts = [_artifact("source-a", "Local models", "2026-01-02")]
    collected = collect_items(artifacts, tmp_path / "wiki")
    graph = build_knowledge_graph(collected, wiki_dir=tmp_path / "wiki", taxonomy_version="tax123")
    rendered = render_graph(graph, wiki_dir=tmp_path / "wiki")
    payload = graph_export_payload(graph)

    topic = next(page for page in graph.knowledge_pages if page.category == "topic")
    source_page = next(file for file in rendered if file.relative_path == "sources/source-a.md")
    topic_page = next(file for file in rendered if file.relative_path == "topics/local-models.md")

    assert topic.entity_id == "topic:local-models"
    assert topic.evidence_count >= 2
    assert topic.stance_counts["supporting"] >= 1
    assert "synthesis_state: stage1-placeholder" in topic_page.text
    assert "derived_topics:" in source_page.text
    assert "local-models" in source_page.text
    assert payload["taxonomy_version"] == "tax123"
    exported_topic = payload["knowledge_pages"][0]
    assert exported_topic["evidence_count"] == topic.evidence_count
    assert "evidence_set_hash" in exported_topic


def _artifact(source_id: str, title: str, published_date: str) -> dict:
    """Return a minimal review artifact with topic/trend/signal content."""
    return {
        "source": {
            "source_id": source_id,
            "title": title,
            "author": "Author",
            "publication": "Publication",
            "published_date": published_date,
            "canonical_url": "https://example.com",
            "content_sha256": "abc",
            "raw_md_rel_path": f"raw/{source_id}.md",
            "raw_html_rel_path": f"raw/{source_id}.html",
        },
        "analysis_meta": {"analysis_timestamp_utc": "2026-01-03T00:00:00+00:00"},
        "llm_output": {
            "source_summary": {
                "summary": "A source about local models.",
                "accessible_overview": "Local models are becoming easier to run.",
                "key_insights": ["Consumer hardware matters."],
                "why_it_matters": "It affects deployment choices.",
                "limitations_and_open_questions": "Benchmarks are thin.",
                "contradictions_and_skepticism": "Evidence is anecdotal.",
                "assessed_as_of": published_date,
            },
            "source_evidence_profile": {"primary_evidence_type": "expert_opinion"},
        },
        "review": {
            "source_summary": {},
            "source_evidence_profile": {
                "llm_item": {"primary_evidence_type": "expert_opinion"},
                "final_item": None,
            },
            "topics": [
                {
                    "proposal_status": "approved",
                    "llm_item": {
                        "topic_slug": "local-models",
                        "topic_title": "Local Models",
                        "knowledge_summary": "Local models run near users.",
                        "operational_insight": "Treat local inference as infrastructure.",
                        "key_points": ["Hardware constraints shape reliability."],
                        "proposed_tags": ["infrastructure"],
                        "confidence": 0.9,
                        "value_level": "high",
                    },
                    "sections": {},
                    "tags": {"final_tags": ["infrastructure"]},
                }
            ],
            "industry_trends": [
                {
                    "proposal_status": "approved",
                    "llm_item": {
                        "trend_slug": "local-inference",
                        "trend_title": "Local Inference",
                        "trend_description": "Inference is moving closer to users.",
                        "evidence_from_source": "The source reports local runs.",
                        "uncertainty_note": "Single-source claim.",
                        "supporting_data_points": ["Runs on consumer GPU."],
                        "assessed_as_of": published_date,
                        "proposed_tags": ["edge-deployment"],
                    },
                    "sections": {},
                    "tags": {"final_tags": ["edge-deployment"]},
                }
            ],
            "roundup_signals": [
                {
                    "proposal_status": "approved",
                    "llm_item": {
                        "signal_title": "Local inference adoption",
                        "signal_type": "trend",
                        "summary": "More local inference experiments are appearing.",
                        "why_it_matters": "Deployment options expand.",
                        "operational_relevance": "Teams need local observability.",
                        "service_automation_relevance": "Support tools may run locally.",
                        "signal_strength": "medium",
                        "time_horizon": "medium_term",
                        "wiki_worthiness": "review_candidate",
                        "assessed_as_of": published_date,
                        "proposed_tags": ["edge-deployment"],
                        "evidence_snippets": ["Local runs are reported."],
                    },
                    "sections": {},
                    "tags": {"final_tags": ["edge-deployment"]},
                }
            ],
        },
        "review_analytics": {"review_finished_at": "2026-01-04T00:00:00+00:00"},
    }
