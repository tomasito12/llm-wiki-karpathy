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
    review_artifact_path,
    save_artifact,
    touch_review_session,
)
from src.ingest_review.extract import SourceDocument, load_readwise_pair
from src.ingest_review.schema import (
    GLOSSARY_LIST_KEYS,
    GLOSSARY_SCALAR_KEYS,
    IMPL_STUDY_LIST_KEYS,
    IMPL_STUDY_SCALAR_KEYS,
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
    assert art["artifact_schema_version"] == 3
    assert art["source"]["source_id"] == stem
    assert art["llm_output"]["roundup"]["is_roundup"] is False
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
    assert node["tags"]["approved_allowlist_tags"] == []


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
    """Calling migrate_artifact_to_v3 on a v3 artifact is a no-op."""
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
                "proposed_tags": [],
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
    assert node["tags"]["approved_allowlist_tags"] == []


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
