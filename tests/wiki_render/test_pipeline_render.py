"""End-to-end collection, merge, render, and export tests."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render import layout
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

    topic = next(page for page in graph.knowledge_pages if page.entity_id == "topic:local-models")
    source_page = next(file for file in rendered if file.relative_path == "sources/source-a.md")
    topic_page = next(file for file in rendered if file.relative_path == "topics/local-models.md")

    assert topic.entity_id == "topic:local-models"
    assert topic.evidence_count >= 2
    assert topic.stance_counts["supporting"] >= 1
    assert "synthesis_state: stage1-placeholder" in topic_page.text
    assert layout.wikilink("topics/edge-inference.md", "Edge Inference") in topic_page.text
    assert "## Related Topics" not in topic_page.text
    assert "derived_topics:" in source_page.text
    assert "local-models" in source_page.text
    assert payload["taxonomy_version"] == "tax123"
    exported_topic = next(
        page for page in payload["knowledge_pages"] if page["entity_id"] == "topic:local-models"
    )
    assert exported_topic["evidence_count"] == topic.evidence_count
    assert "evidence_set_hash" in exported_topic
    assert exported_topic["values"]["related_topics"] == ["edge-inference"]


def test_implementation_studies_render_as_individual_monthly_pages(tmp_path: Path) -> None:
    """Implementation studies are evidence pages, not merged knowledge pages."""
    source_id = "millions-of-calls-one-judge-01kqkyaqcyqgmyjjqs3r374v14"
    artifacts = [
        {
            "source": {
                "source_id": source_id,
                "title": "Voicebot evaluation article",
                "author": "Author",
                "publication": "Publication",
                "published_date": "2026-04-30",
                "canonical_url": "https://example.com",
                "content_sha256": "abc",
                "raw_md_rel_path": f"raw/{source_id}.md",
                "raw_html_rel_path": f"raw/{source_id}.html",
            },
            "analysis_meta": {"analysis_timestamp_utc": "2026-04-30T00:00:00+00:00"},
            "llm_output": {
                "source_summary": {
                    "summary": "A source about voicebot evaluation.",
                    "accessible_overview": "Voicebot evaluation at scale.",
                    "key_insights": ["Evaluation matters."],
                    "why_it_matters": "It affects support automation.",
                    "limitations_and_open_questions": "Single case study.",
                    "contradictions_and_skepticism": "None.",
                    "assessed_as_of": "2026-04-30",
                },
                "source_evidence_profile": {"primary_evidence_type": "case_study"},
            },
            "review": {
                "source_summary": {},
                "source_evidence_profile": {
                    "llm_item": {"primary_evidence_type": "case_study"},
                    "final_item": None,
                },
                "implementation_studies": [
                    {
                        "proposal_status": "approved",
                        "llm_item": {
                            "title": "Voicebot Evaluation at Telecom Scale",
                            "company": "Artefact and a major French telecom operator",
                            "industry": "telecom",
                            "overview": "A telecom voicebot evaluated with LLM-as-a-judge.",
                            "what_was_implemented": "An end-to-end production evaluation system.",
                            "business_objective": "Measure voicebot quality at production scale.",
                            "technical_approach": "Binary metrics evaluated by LLM judges.",
                            "deployment_context": "A conversational voicebot in production.",
                            "outcome_status": "Ongoing production use.",
                            "success_or_failure_factors": "Worked because of atomic checks.",
                            "operational_constraints": "Human review was impossible at scale.",
                            "ai_model_observations": "Transcript quality dominated errors.",
                            "implications_for_service_automation": (
                                "Shows how to run quality control."
                            ),
                            "strategic_signals": "Evaluation becomes part of the operating model.",
                            "key_lessons": ["Break vague quality into atomic binary checks."],
                            "open_questions": ["How well does this transfer to other domains?"],
                            "related_sources": ["https://example.com/article"],
                            "evidence_snippets": [
                                {
                                    "claim": "The system handled production traffic at scale.",
                                    "snippet": "millions of calls per year in production",
                                    "provenance": "stated",
                                }
                            ],
                            "assessed_as_of": "2026-04-30",
                            "proposed_tags": ["support-automation", "production-failure"],
                            "confidence": 0.95,
                            "value_level": "high",
                        },
                        "sections": {},
                        "tags": {"final_tags": ["support-automation", "production-failure"]},
                    }
                ],
            },
            "review_analytics": {"review_finished_at": "2026-04-30T00:00:00+00:00"},
        }
    ]
    wiki_dir = tmp_path / "wiki"
    collected = collect_items(artifacts, wiki_dir)
    graph = build_knowledge_graph(collected, wiki_dir=wiki_dir, taxonomy_version="tax123")
    rendered = render_graph(graph, wiki_dir=wiki_dir)
    payload = graph_export_payload(graph)

    assert not any(page.category == "impl_study" for page in graph.knowledge_pages)
    assert len(graph.implementation_studies) == 1
    study = graph.implementation_studies[0]
    assert study.path.startswith("implementation-studies/2026-04/")
    assert study.path.endswith(".md")
    assert source_id in study.path

    study_page = next(file for file in rendered if file.relative_path == study.path)
    source_page = next(file for file in rendered if file.relative_path == f"sources/{source_id}.md")
    month_index = next(
        file
        for file in rendered
        if file.relative_path == "indexes/implementation-studies-by-month.md"
    )
    tag_index = next(
        file
        for file in rendered
        if file.relative_path == "indexes/implementation-studies-by-tag.md"
    )

    assert "category: implementation-study" in study_page.text
    assert "company: Artefact and a major French telecom operator" in study_page.text
    assert "Key Lessons" in study_page.text
    assert "Evidence Snippets" in study_page.text
    assert "synthesis_state" not in study_page.text
    assert "derived_implementation_studies:" in source_page.text
    assert study.path in source_page.text
    assert "derived_pages:" in source_page.text
    assert ".md" in source_page.text
    assert layout.wikilink(study.path, study.title) in month_index.text
    assert layout.wikilink(study.path, study.title) in tag_index.text
    assert len(payload["implementation_studies"]) == 1
    assert payload["implementation_studies"][0]["path"] == study.path


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
                        "related_topics": ["edge-inference"],
                        "related_terms": ["should-not-cross-category"],
                        "proposed_tags": ["infrastructure"],
                        "confidence": 0.9,
                        "value_level": "high",
                    },
                    "sections": {},
                    "tags": {"final_tags": ["infrastructure"]},
                },
                {
                    "proposal_status": "approved",
                    "llm_item": {
                        "topic_slug": "edge-inference",
                        "topic_title": "Edge Inference",
                        "knowledge_summary": "Edge inference runs close to users.",
                        "operational_insight": "Place models near latency-sensitive work.",
                        "key_points": ["Latency constraints shape placement."],
                        "proposed_tags": ["infrastructure"],
                        "confidence": 0.8,
                        "value_level": "medium",
                    },
                    "sections": {},
                    "tags": {"final_tags": ["infrastructure"]},
                },
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
