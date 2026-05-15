"""Tests for review artifact assembly."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest_review.artifact import (
    aggregate_impl_study_section_status,
    aggregate_review_status,
    build_new_artifact,
    default_analysis_meta,
    default_review_for_llm_output,
    migrate_artifact_to_v2,
    migrate_artifact_to_v3,
    migrate_artifact_to_v4,
    migrate_artifact_to_v5,
    migrate_artifact_to_v6,
    migrate_artifact_to_v7,
    migrate_artifact_to_v8,
    migrate_artifact_to_v9,
    review_artifact_path,
    save_artifact,
    touch_review_session,
)
from src.ingest_review.extract import SourceDocument, load_readwise_pair
from src.ingest_review.schema import (
    GLOSSARY_LIST_KEYS,
    GLOSSARY_SCALAR_KEYS,
    HOWTO_LIST_KEYS,
    HOWTO_SCALAR_KEYS,
    IMPL_STUDY_LIST_KEYS,
    IMPL_STUDY_SCALAR_KEYS,
    INSIGHT_LIST_KEYS,
    INSIGHT_SCALAR_KEYS,
    MODEL_LIST_KEYS,
    MODEL_SCALAR_KEYS,
    SIGNAL_LIST_KEYS,
    SIGNAL_SCALAR_KEYS,
    TOOL_LIST_KEYS,
    TOOL_SCALAR_KEYS,
    TOPIC_LIST_KEYS,
    TOPIC_SCALAR_KEYS,
    TREND_LIST_KEYS,
    TREND_SCALAR_KEYS,
    LlmClassificationOutput,
)


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
    assert rev["source_summary"]["accessible_overview"]["status"] == "pending"
    assert rev["source_summary"]["why_it_matters"]["status"] == "pending"
    assert rev["source_summary"]["key_insights"]["llm_list"] == []
    assert rev["source_type_detection"]["status"] == "pending"
    assert rev["roundup_signals"] == []
    assert rev["interview_insights"] == []


def test_migrate_v1_artifact_maps_legacy_source_summary_fields() -> None:
    """v1 context_limitations / contradictions / string insights map to v2 keys."""
    art: dict[str, Any] = {
        "artifact_schema_version": 1,
        "llm_output": {
            "source_summary": {
                "why_it_matters": "w",
                "key_insights": "- one\n- two",
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
    assert art["artifact_schema_version"] == 9
    assert art["source"]["source_id"] == stem
    assert art["llm_output"]["source_type_detection"]["detected_source_type"] == "unknown"
    assert "implementation_studies" in art["review"]
    assert "enterprise_studies" not in art["review"]


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


def test_default_review_builds_impl_study_per_section_nodes() -> None:
    """Implementation studies get per-section review nodes (not flat status)."""
    llm: dict[str, Any] = {
        "implementation_studies": [
            {
                "title": "AI pilot",
                "company": "Acme",
                "overview": "Tested AI.",
                "key_lessons": ["lesson1"],
                "open_questions": ["q1"],
                "related_sources": ["url1"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    impl = rev["implementation_studies"]
    assert len(impl) == 1
    node = impl[0]
    assert "proposal_id" in node
    assert "sections" in node
    assert "tags" in node
    sections = node["sections"]
    for sk in IMPL_STUDY_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
        assert sections[sk]["final_text"] is None
    for lk in IMPL_STUDY_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert sections[lk]["final_list"] is None
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["key_lessons"]["llm_list"] == ["lesson1"]
    assert node["tags"]["final_primary_tag"] is None
    assert node["tags"]["new_tag_approved"] is False


def test_migrate_v2_to_v3_renames_enterprise_studies() -> None:
    """migrate_artifact_to_v3 renames enterprise_studies to implementation_studies."""
    art: dict[str, Any] = {
        "artifact_schema_version": 2,
        "llm_output": {
            "source_summary": {},
            "enterprise_studies": [
                {"company_name": "Corp", "confidence": 0.5},
            ],
        },
        "review": {
            "source_summary": {},
            "enterprise_studies": [
                {"proposal_id": "abc", "status": "pending", "llm_item": {}, "final_item": None},
            ],
        },
    }
    migrate_artifact_to_v3(art)
    assert art["artifact_schema_version"] == 3
    assert "implementation_studies" in art["llm_output"]
    assert "enterprise_studies" not in art["llm_output"]
    assert "implementation_studies" in art["review"]
    assert "enterprise_studies" not in art["review"]
    impl = art["review"]["implementation_studies"]
    assert len(impl) == 1
    assert "sections" in impl[0]


def test_migrate_v3_is_noop_on_v3() -> None:
    """Calling migrate_artifact_to_v3 on a v3+ artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 3,
        "llm_output": {"implementation_studies": []},
        "review": {"implementation_studies": []},
    }
    migrate_artifact_to_v3(art)
    assert art["artifact_schema_version"] == 3


def test_aggregate_impl_study_section_status_all_pending() -> None:
    """All-pending sections report 'pending'."""
    sections = {
        "overview": {"status": "pending"},
        "title": {"status": "pending"},
    }
    assert aggregate_impl_study_section_status(sections) == "pending"


def test_aggregate_impl_study_section_status_mixed() -> None:
    """Mix of approved + pending reports 'mixed'."""
    sections = {
        "overview": {"status": "approved"},
        "title": {"status": "pending"},
    }
    assert aggregate_impl_study_section_status(sections) == "mixed"


def test_aggregate_impl_study_section_status_all_approved() -> None:
    """All approved reports 'approved'."""
    sections = {
        "overview": {"status": "approved"},
        "title": {"status": "approved"},
    }
    assert aggregate_impl_study_section_status(sections) == "approved"


def test_default_review_builds_glossary_per_section_nodes() -> None:
    """Glossary proposals get per-section review nodes (not flat status)."""
    llm: dict[str, Any] = {
        "glossary": [
            {
                "term": "RAG",
                "proposed_definition": "Retrieval-augmented generation.",
                "extended_explanation": "Long explanation.",
                "supporting_snippet": "...",
                "relevance_note": "Core pattern.",
                "related_terms": ["vector search", "embeddings"],
                "primary_tag": "",
                "confidence": 0.85,
                "suggested_action": "create",
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    glossary = rev["glossary"]
    assert len(glossary) == 1
    node = glossary[0]
    assert "proposal_id" in node
    assert "sections" in node
    assert "tags" in node
    sections = node["sections"]
    for sk in GLOSSARY_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
        assert sections[sk]["final_text"] is None
    for lk in GLOSSARY_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert sections[lk]["final_list"] is None
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["related_terms"]["llm_list"] == ["vector search", "embeddings"]
    assert node["tags"]["final_primary_tag"] is None
    assert node["tags"]["new_tag_approved"] is False


def test_migrate_v3_upgrades_old_glossary_flat_nodes() -> None:
    """migrate_artifact_to_v3 rebuilds flat glossary nodes into per-section format."""
    art: dict[str, Any] = {
        "artifact_schema_version": 2,
        "llm_output": {
            "source_summary": {},
            "glossary": [
                {
                    "term": "MoE",
                    "proposed_definition": "Mixture of Experts.",
                    "supporting_snippet": "...",
                    "confidence": 0.7,
                    "suggested_action": "create",
                },
            ],
        },
        "review": {
            "source_summary": {},
            "glossary": [
                {
                    "proposal_id": "old-id",
                    "status": "pending",
                    "notes": None,
                    "llm_item": {"term": "MoE"},
                    "final_item": None,
                    "reviewer_tags_added": [],
                },
            ],
        },
    }
    migrate_artifact_to_v3(art)
    glossary = art["review"]["glossary"]
    assert len(glossary) == 1
    node = glossary[0]
    assert isinstance(node, dict)
    assert "sections" in node
    sections = node["sections"]
    assert isinstance(sections, dict)
    assert "term" in sections
    term_sec = sections["term"]
    assert isinstance(term_sec, dict)
    assert term_sec["status"] == "pending"


def test_aggregate_review_status_includes_glossary_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts glossary per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import GlossaryProposal

    parsed = LlmClassificationOutput(
        glossary=[GlossaryProposal(term="RAG", proposed_definition="def")]
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    g_sections = art["review"]["glossary"][0]["sections"]
    g_sections["term"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_aggregate_review_status_includes_impl_study_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts impl study per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import ImplementationStudyProposal

    parsed = LlmClassificationOutput(
        implementation_studies=[ImplementationStudyProposal(title="T", company="C")]
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    impl_sections = art["review"]["implementation_studies"][0]["sections"]
    impl_sections["title"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_default_review_builds_topic_per_section_nodes() -> None:
    """Topic contributions get per-section review nodes."""
    llm: dict[str, Any] = {
        "topics": [
            {
                "topic_slug": "context-engineering",
                "topic_title": "Context Engineering",
                "knowledge_summary": "Summary.",
                "key_points": ["point1"],
                "related_topics": ["prompt-engineering"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    topics = rev["topics"]
    assert len(topics) == 1
    node = topics[0]
    assert "proposal_id" in node
    assert "sections" in node
    assert "tags" in node
    sections = node["sections"]
    for sk in TOPIC_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in TOPIC_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["key_points"]["llm_list"] == ["point1"]
    assert sections["related_topics"]["llm_list"] == ["prompt-engineering"]


def test_default_review_builds_howto_per_section_nodes() -> None:
    """How-to proposals get per-section review nodes."""
    llm: dict[str, Any] = {
        "how_to": [
            {
                "question_title": "How to build evals?",
                "answer_summary": "Answer.",
                "implementation_steps": ["step1"],
                "prerequisites": ["req1"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    howtos = rev["how_to"]
    assert len(howtos) == 1
    node = howtos[0]
    assert "proposal_id" in node
    assert "sections" in node
    sections = node["sections"]
    for sk in HOWTO_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in HOWTO_LIST_KEYS:
        assert lk in sections
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["implementation_steps"]["llm_list"] == ["step1"]


def test_default_review_builds_trend_per_section_nodes() -> None:
    """Industry trend proposals get per-section review nodes."""
    llm: dict[str, Any] = {
        "industry_trends": [
            {
                "trend_name": "inference-cost-collapse",
                "trend_description": "Costs falling.",
                "supporting_data_points": ["dp1"],
                "related_trends": ["model-commoditization"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    trends = rev["industry_trends"]
    assert len(trends) == 1
    node = trends[0]
    assert "proposal_id" in node
    assert "sections" in node
    sections = node["sections"]
    for sk in TREND_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in TREND_LIST_KEYS:
        assert lk in sections
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["supporting_data_points"]["llm_list"] == ["dp1"]


def test_migrate_v3_to_v4_converts_flat_howto() -> None:
    """migrate_artifact_to_v4 rebuilds flat how_to nodes to per-section."""
    art: dict[str, Any] = {
        "artifact_schema_version": 3,
        "llm_output": {
            "source_summary": {},
            "how_to": [
                {"question_title": "Q?", "answer_summary": "A."},
            ],
            "industry_trends": [],
        },
        "review": {
            "source_summary": {},
            "how_to": [
                {
                    "proposal_id": "old-id",
                    "status": "pending",
                    "notes": None,
                    "llm_item": {"question_title": "Q?"},
                    "final_item": None,
                    "reviewer_tags_added": [],
                },
            ],
            "industry_trends": [],
        },
    }
    migrate_artifact_to_v4(art)
    assert art["artifact_schema_version"] == 4
    howtos = art["review"]["how_to"]
    assert len(howtos) == 1
    assert "sections" in howtos[0]
    assert "topics" in art["review"]


def test_migrate_v4_adds_empty_topics() -> None:
    """migrate_artifact_to_v4 adds topics review if missing."""
    art: dict[str, Any] = {
        "artifact_schema_version": 3,
        "llm_output": {"source_summary": {}, "how_to": [], "industry_trends": []},
        "review": {"source_summary": {}, "how_to": [], "industry_trends": []},
    }
    migrate_artifact_to_v4(art)
    assert art["artifact_schema_version"] == 4
    assert "topics" in art["review"]
    assert art["review"]["topics"] == []


def test_migrate_v4_is_noop_on_v4() -> None:
    """Calling migrate_artifact_to_v4 on a v4 artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 4,
        "llm_output": {},
        "review": {"topics": [], "how_to": [], "industry_trends": []},
    }
    migrate_artifact_to_v4(art)
    assert art["artifact_schema_version"] == 4


def test_aggregate_review_status_includes_topic_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts topic per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import TopicContribution

    parsed = LlmClassificationOutput(
        topics=[TopicContribution(topic_slug="ctx-eng", topic_title="Context Engineering")]
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    t_sections = art["review"]["topics"][0]["sections"]
    t_sections["topic_slug"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_default_review_builds_tool_per_section_nodes() -> None:
    """Tool proposals get per-section review nodes."""
    llm: dict[str, Any] = {
        "tools": [
            {
                "name": "Cursor",
                "short_description": "AI coding assistant.",
                "operational_relevance": "Improves coding.",
                "core_capabilities": ["codebase indexing"],
                "integration_ecosystem": ["MCP"],
                "related_tools": ["Claude Code"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    tools = rev["tools"]
    assert len(tools) == 1
    node = tools[0]
    assert "proposal_id" in node
    assert "sections" in node
    assert "tags" in node
    sections = node["sections"]
    for sk in TOOL_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in TOOL_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["core_capabilities"]["llm_list"] == ["codebase indexing"]
    assert sections["related_tools"]["llm_list"] == ["Claude Code"]


def test_migrate_v4_to_v5_converts_flat_tools() -> None:
    """migrate_artifact_to_v5 rebuilds flat tools nodes to per-section."""
    art: dict[str, Any] = {
        "artifact_schema_version": 4,
        "llm_output": {
            "source_summary": {},
            "tools": [
                {"name": "Cursor", "short_description": "IDE.", "proposed_tags": ["coding-agent"]},
            ],
        },
        "review": {
            "source_summary": {},
            "tools": [
                {
                    "proposal_id": "old-id",
                    "status": "pending",
                    "notes": None,
                    "llm_item": {"name": "Cursor", "proposed_tags": ["coding-agent"]},
                    "final_item": None,
                    "reviewer_tags_added": [],
                },
            ],
        },
    }
    migrate_artifact_to_v5(art)
    assert art["artifact_schema_version"] == 5
    tools = art["review"]["tools"]
    assert len(tools) == 1
    assert "sections" in tools[0]
    llm_tool = art["llm_output"]["tools"][0]
    assert "proposed_types" in llm_tool
    assert llm_tool["proposed_types"] == ["coding-agent"]
    assert "proposed_tags" not in llm_tool


def test_migrate_v5_is_noop_on_v5() -> None:
    """Calling migrate_artifact_to_v5 on a v5 artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 5,
        "llm_output": {"tools": []},
        "review": {"tools": []},
    }
    migrate_artifact_to_v5(art)
    assert art["artifact_schema_version"] == 5


def test_migrate_v5_handles_tool_type_to_proposed_types() -> None:
    """migrate_artifact_to_v5 converts legacy tool_type string to proposed_types list."""
    art: dict[str, Any] = {
        "artifact_schema_version": 4,
        "llm_output": {
            "source_summary": {},
            "tools": [
                {"name": "Ollama", "tool_type": "local-llm-tooling"},
            ],
        },
        "review": {
            "source_summary": {},
            "tools": [
                {
                    "proposal_id": "old",
                    "status": "pending",
                    "notes": None,
                    "llm_item": {"name": "Ollama", "tool_type": "local-llm-tooling"},
                    "final_item": None,
                    "reviewer_tags_added": [],
                },
            ],
        },
    }
    migrate_artifact_to_v5(art)
    llm_tool = art["llm_output"]["tools"][0]
    assert llm_tool.get("proposed_types") == ["local-llm-tooling"]


def test_aggregate_review_status_includes_tool_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts tool per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import ToolProposal

    parsed = LlmClassificationOutput(tools=[ToolProposal(name="Cursor", short_description="IDE.")])
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    t_sections = art["review"]["tools"][0]["sections"]
    t_sections["name"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_default_review_builds_model_per_section_nodes() -> None:
    """Foundation model proposals get per-section review nodes."""
    llm: dict[str, Any] = {
        "foundation_models": [
            {
                "model_name": "GPT-5",
                "provider": "OpenAI",
                "operational_summary": "Strong for coding.",
                "core_capabilities": ["long-context", "tool calling"],
                "benchmark_observations": ["SWE-Bench leader"],
                "comparative_observations": ["outperforms Claude"],
                "related_models": ["GPT-4o"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    models = rev["foundation_models"]
    assert len(models) == 1
    node = models[0]
    assert "proposal_id" in node
    assert "sections" in node
    assert "tags" in node
    sections = node["sections"]
    for sk in MODEL_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in MODEL_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["core_capabilities"]["llm_list"] == ["long-context", "tool calling"]
    assert sections["related_models"]["llm_list"] == ["GPT-4o"]


def test_migrate_v5_to_v6_converts_flat_models() -> None:
    """migrate_artifact_to_v6 rebuilds flat foundation_models nodes to per-section."""
    art: dict[str, Any] = {
        "artifact_schema_version": 5,
        "llm_output": {
            "source_summary": {},
            "foundation_models": [
                {"model_name": "GPT-5", "provider": "OpenAI", "article_summary": "Old summary."},
            ],
        },
        "review": {
            "source_summary": {},
            "foundation_models": [
                {
                    "proposal_id": "old-id",
                    "status": "pending",
                    "notes": None,
                    "llm_item": {"model_name": "GPT-5", "article_summary": "Old summary."},
                    "final_item": None,
                    "reviewer_tags_added": [],
                },
            ],
        },
    }
    migrate_artifact_to_v6(art)
    assert art["artifact_schema_version"] == 6
    models = art["review"]["foundation_models"]
    assert len(models) == 1
    assert "sections" in models[0]


def test_migrate_v6_is_noop_on_v6() -> None:
    """Calling migrate_artifact_to_v6 on a v6 artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 6,
        "llm_output": {"foundation_models": []},
        "review": {"foundation_models": []},
    }
    migrate_artifact_to_v6(art)
    assert art["artifact_schema_version"] == 6


def test_aggregate_review_status_includes_model_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts foundation model per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import FoundationModelProposal

    parsed = LlmClassificationOutput(
        foundation_models=[FoundationModelProposal(model_name="GPT-5", provider="OpenAI")]
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    m_sections = art["review"]["foundation_models"][0]["sections"]
    m_sections["model_name"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_assessed_as_of_field_exists_on_temporal_models() -> None:
    """assessed_as_of field exists with empty default on all temporal models."""
    from src.ingest_review.schema import (
        IndustryTrendProposal,
        InterviewInsight,
        RoundupSignal,
        SourceSummaryBlock,
    )

    for cls in (SourceSummaryBlock, IndustryTrendProposal, RoundupSignal, InterviewInsight):
        instance = cls()
        assert hasattr(instance, "assessed_as_of"), f"{cls.__name__} missing assessed_as_of"
        assert instance.assessed_as_of == "", f"{cls.__name__} assessed_as_of default not empty"


def test_migrate_v6_to_v7_converts_roundup_to_source_type() -> None:
    """migrate_artifact_to_v7 converts roundup to source_type_detection."""
    art: dict[str, Any] = {
        "artifact_schema_version": 6,
        "llm_output": {
            "source_summary": {},
            "roundup": {"is_roundup": True, "reasoning": "Multi-item digest.", "confidence": 0.9},
        },
        "review": {
            "source_summary": {},
            "roundup": {
                "status": "approved",
                "notes": "Confirmed roundup.",
                "llm_item": {"is_roundup": True, "reasoning": "digest", "confidence": 0.9},
                "final_item": None,
            },
        },
    }
    migrate_artifact_to_v7(art)
    assert art["artifact_schema_version"] == 7
    assert "roundup" not in art["llm_output"]
    assert "roundup" not in art["review"]
    std = art["llm_output"]["source_type_detection"]
    assert std["detected_source_type"] == "ai_industry_roundup"
    assert std["confidence"] == 0.9
    assert std["reasoning"] == ["Multi-item digest."]
    rev_std = art["review"]["source_type_detection"]
    assert rev_std["status"] == "approved"
    assert rev_std["notes"] == "Confirmed roundup."
    assert art["llm_output"]["roundup_signals"] == []
    assert art["llm_output"]["interview_insights"] == []
    assert art["review"]["roundup_signals"] == []
    assert art["review"]["interview_insights"] == []


def test_migrate_v7_non_roundup_maps_to_unknown() -> None:
    """migrate_artifact_to_v7 with is_roundup=False maps to unknown."""
    art: dict[str, Any] = {
        "artifact_schema_version": 6,
        "llm_output": {
            "source_summary": {},
            "roundup": {"is_roundup": False, "reasoning": "", "confidence": 0.0},
        },
        "review": {
            "source_summary": {},
            "roundup": {"status": "pending", "notes": None, "llm_item": {}, "final_item": None},
        },
    }
    migrate_artifact_to_v7(art)
    assert art["llm_output"]["source_type_detection"]["detected_source_type"] == "unknown"


def test_migrate_v7_is_noop_on_v7() -> None:
    """Calling migrate_artifact_to_v7 on a v7 artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 7,
        "llm_output": {"source_type_detection": {"detected_source_type": "unknown"}},
        "review": {"source_type_detection": {}},
    }
    migrate_artifact_to_v7(art)
    assert art["artifact_schema_version"] == 7


def test_default_review_builds_signal_per_section_nodes() -> None:
    """Roundup signal proposals get per-section review nodes."""
    llm: dict[str, Any] = {
        "roundup_signals": [
            {
                "signal_title": "Context pipelines becoming product boundary",
                "signal_type": "trend",
                "summary": "Pattern observed.",
                "suggested_destinations": ["topics/"],
                "mentioned_entities": ["OpenAI"],
                "evidence_snippets": ["quote1"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    signals = rev["roundup_signals"]
    assert len(signals) == 1
    node = signals[0]
    assert "proposal_id" in node
    assert "sections" in node
    sections = node["sections"]
    for sk in SIGNAL_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in SIGNAL_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["suggested_destinations"]["llm_list"] == ["topics/"]
    assert sections["mentioned_entities"]["llm_list"] == ["OpenAI"]


def test_default_review_builds_insight_per_section_nodes() -> None:
    """Interview insight proposals get per-section review nodes."""
    llm: dict[str, Any] = {
        "interview_insights": [
            {
                "insight_title": "Harness quality > model quality",
                "insight_type": "topic",
                "summary": "Key argument.",
                "suggested_destinations": ["topics/"],
                "mentioned_entities": ["Anthropic"],
                "contrarian_or_speculative_claims": ["claim1"],
                "evidence_snippets": ["quote1"],
            },
        ],
        "source_summary": {},
    }
    rev = default_review_for_llm_output(llm)
    insights = rev["interview_insights"]
    assert len(insights) == 1
    node = insights[0]
    assert "proposal_id" in node
    assert "sections" in node
    sections = node["sections"]
    for sk in INSIGHT_SCALAR_KEYS:
        assert sk in sections
        assert sections[sk]["status"] == "pending"
    for lk in INSIGHT_LIST_KEYS:
        assert lk in sections
        assert sections[lk]["status"] == "pending"
        assert isinstance(sections[lk]["llm_list"], list)
    assert sections["contrarian_or_speculative_claims"]["llm_list"] == ["claim1"]


def test_aggregate_review_status_includes_signal_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts roundup signal per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import RoundupSignal

    parsed = LlmClassificationOutput(
        roundup_signals=[RoundupSignal(signal_title="sig", signal_type="trend")]
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    s_sections = art["review"]["roundup_signals"][0]["sections"]
    s_sections["signal_title"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_aggregate_review_status_includes_insight_sections(tmp_path: Path) -> None:
    """aggregate_review_status counts interview insight per-section statuses."""
    doc = _minimal_doc(tmp_path)
    from src.ingest_review.schema import InterviewInsight

    parsed = LlmClassificationOutput(
        interview_insights=[InterviewInsight(insight_title="ins", insight_type="topic")]
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert aggregate_review_status(art) == "all_pending"
    i_sections = art["review"]["interview_insights"][0]["sections"]
    i_sections["insight_title"]["status"] = "approved"
    assert aggregate_review_status(art) == "mixed"


def test_simplified_tag_fields_exist_on_all_tag_models() -> None:
    """All proposal models have primary_tag, secondary_tag, suggested_new_tag."""
    from src.ingest_review.schema import (
        GlossaryProposal,
        HowToProposal,
        ImplementationStudyProposal,
        IndustryTrendProposal,
        InterviewInsight,
        RoundupSignal,
        TopicContribution,
    )

    for cls in (
        GlossaryProposal,
        TopicContribution,
        HowToProposal,
        IndustryTrendProposal,
        RoundupSignal,
        InterviewInsight,
        ImplementationStudyProposal,
    ):
        instance = cls()
        assert hasattr(instance, "primary_tag"), f"{cls.__name__} missing primary_tag"
        assert hasattr(instance, "suggested_new_tag"), f"{cls.__name__} missing suggested_new_tag"
        assert instance.primary_tag == ""
        assert instance.suggested_new_tag == ""


def test_roundup_signal_has_simplified_tags() -> None:
    """RoundupSignal has simplified tag fields."""
    from src.ingest_review.schema import RoundupSignal

    sig = RoundupSignal(signal_title="test")
    assert sig.primary_tag == ""
    assert sig.secondary_tag == ""
    assert sig.suggested_new_tag == ""
    assert sig.value_level == "medium"


def test_interview_insight_has_simplified_tags() -> None:
    """InterviewInsight has simplified tag fields."""
    from src.ingest_review.schema import InterviewInsight

    ins = InterviewInsight(insight_title="test")
    assert ins.primary_tag == ""
    assert ins.secondary_tag == ""
    assert ins.suggested_new_tag == ""
    assert ins.value_level == "medium"


def test_build_per_section_tag_node_has_new_structure(tmp_path: Path) -> None:
    """Per-section review nodes use simplified tag structure."""
    from src.ingest_review.schema import GlossaryProposal, TopicContribution

    doc = _minimal_doc(tmp_path)
    parsed = LlmClassificationOutput(
        glossary=[GlossaryProposal(term="X")],
        topics=[TopicContribution(topic_slug="y")],
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    gl_tags = art["review"]["glossary"][0]["tags"]
    assert "final_primary_tag" in gl_tags
    assert "new_tag_approved" in gl_tags
    assert gl_tags["new_tag_approved"] is False

    tp_tags = art["review"]["topics"][0]["tags"]
    assert "final_primary_tag" in tp_tags
    assert tp_tags["new_tag_approved"] is False


def test_proposal_status_on_new_review_nodes(tmp_path: Path) -> None:
    """New review nodes have proposal_status='pending'."""
    from src.ingest_review.schema import GlossaryProposal

    doc = _minimal_doc(tmp_path)
    parsed = LlmClassificationOutput(
        glossary=[GlossaryProposal(term="X")],
    )
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert art["review"]["glossary"][0]["proposal_status"] == "pending"


def test_review_analytics_on_new_artifact(tmp_path: Path) -> None:
    """New artifacts have review_analytics with expected keys."""
    doc = _minimal_doc(tmp_path)
    parsed = LlmClassificationOutput()
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    analytics = art["review_analytics"]
    assert analytics["review_started_at"] is None
    assert analytics["proposals_total"] == 0
    assert analytics["batch_actions_used"] == []


def test_migrate_artifact_to_v8_adds_proposal_status() -> None:
    """migrate_artifact_to_v8 adds proposal_status and converts tag structure."""
    art: dict[str, Any] = {
        "artifact_schema_version": 7,
        "llm_output": {"source_summary": {}},
        "review": {
            "source_summary": {},
            "glossary": [
                {
                    "proposal_id": "test-id",
                    "notes": None,
                    "llm_item": {"term": "RAG"},
                    "sections": {},
                    "tags": {
                        "approved_allowlist_tags": [],
                        "reviewer_tags_added": [],
                        "approved_new_tags": [],
                    },
                },
            ],
        },
    }
    migrate_artifact_to_v8(art)
    assert art["artifact_schema_version"] == 8
    node = art["review"]["glossary"][0]
    assert node["proposal_status"] == "pending"
    assert node["tags"]["final_primary_tag"] is None
    assert node["tags"]["new_tag_approved"] is False
    assert "review_analytics" in art
    assert "extraction_meta" in art["llm_output"]


def test_migrate_v8_is_noop_on_v8() -> None:
    """Calling migrate_artifact_to_v8 on a v8 artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 8,
        "llm_output": {"extraction_meta": {}},
        "review": {},
        "review_analytics": {},
    }
    migrate_artifact_to_v8(art)
    assert art["artifact_schema_version"] == 8


def test_migrate_artifact_to_v9_adds_evidence_type() -> None:
    """migrate_artifact_to_v9 sets evidence_type=unknown on proposals missing the field."""
    art: dict[str, Any] = {
        "artifact_schema_version": 8,
        "llm_output": {
            "extraction_meta": {},
            "topics": [{"topic_slug": "x", "confidence": 0.5}],
        },
        "review": {
            "topics": [
                {
                    "proposal_id": "p1",
                    "proposal_status": "pending",
                    "llm_item": {"topic_slug": "x"},
                    "sections": {},
                    "tags": {},
                },
            ],
        },
        "review_analytics": {},
    }
    migrate_artifact_to_v9(art)
    assert art["artifact_schema_version"] == 9
    assert art["llm_output"]["topics"][0]["evidence_type"] == "unknown"
    assert art["review"]["topics"][0]["llm_item"]["evidence_type"] == "unknown"
    assert art["review_analytics"]["evidence_type_counts"] == {}


def test_migrate_v9_preserves_valid_evidence_type() -> None:
    """migrate_artifact_to_v9 keeps valid evidence_type values."""
    art: dict[str, Any] = {
        "artifact_schema_version": 8,
        "llm_output": {"glossary": [{"term": "RAG", "evidence_type": "vendor_claim"}]},
        "review": {},
        "review_analytics": {},
    }
    migrate_artifact_to_v9(art)
    assert art["llm_output"]["glossary"][0]["evidence_type"] == "vendor_claim"


def test_migrate_v9_coerces_invalid_evidence_type() -> None:
    """Invalid evidence_type values become unknown."""
    art: dict[str, Any] = {
        "artifact_schema_version": 8,
        "llm_output": {"tools": [{"name": "X", "evidence_type": "not-a-real-type"}]},
        "review": {},
        "review_analytics": {},
    }
    migrate_artifact_to_v9(art)
    assert art["llm_output"]["tools"][0]["evidence_type"] == "unknown"


def test_migrate_v9_is_noop_on_v9() -> None:
    """Calling migrate_artifact_to_v9 on a v9 artifact is a no-op."""
    art: dict[str, Any] = {
        "artifact_schema_version": 9,
        "llm_output": {"glossary": [{"term": "X", "evidence_type": "benchmark"}]},
        "review": {},
        "review_analytics": {"evidence_type_counts": {}},
    }
    migrate_artifact_to_v9(art)
    assert art["artifact_schema_version"] == 9
    assert art["llm_output"]["glossary"][0]["evidence_type"] == "benchmark"


def test_new_artifact_review_analytics_has_evidence_type_counts(tmp_path: Path) -> None:
    """New artifacts initialize evidence_type_counts in review_analytics."""
    doc = _minimal_doc(tmp_path)
    parsed = LlmClassificationOutput()
    art = build_new_artifact(
        doc,
        parsed,
        analysis_meta=default_analysis_meta(provider="x", model="y", prompt_version="z"),
        root=tmp_path,
    )
    assert art["review_analytics"]["evidence_type_counts"] == {}
