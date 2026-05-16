"""Tests for feedback SQLite store."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.feedback_store import (
    FeedbackEvent,
    append_feedback_event,
    init_feedback_db,
    record_events_from_artifact,
)


def test_init_feedback_db_creates_file(tmp_path: Path) -> None:
    """Schema application creates the sqlite file."""
    db = tmp_path / "fb.sqlite"
    init_feedback_db(db)
    assert db.is_file()


def test_append_feedback_event_inserts_row(tmp_path: Path) -> None:
    """One event produces one retrievable row."""
    db = tmp_path / "fb.sqlite"
    rid = append_feedback_event(
        db,
        FeedbackEvent(
            source_id="s1",
            source_hash="abc",
            proposal_id="p1",
            path_in_json="tools[0]",
            decision="approved",
            llm_value_snapshot={"x": 1},
            final_value_snapshot=None,
            provider="openai",
            model="gpt-test",
            prompt_version="1",
        ),
    )
    assert rid > 0


def test_record_events_from_artifact_skips_all_pending(tmp_path: Path) -> None:
    """No rows when every review node is still pending."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "1"},
        "llm_output": {"glossary": []},
        "review": {"glossary": []},
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 0


def test_record_events_records_approved_summary_field(tmp_path: Path) -> None:
    """Approved source_summary field emits one feedback row."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "1"},
        "llm_output": {"source_summary": {"why_it_matters": "A"}},
        "review": {
            "source_summary": {
                "why_it_matters": {"status": "approved", "final_text": None, "notes": ""},
            },
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 1


def test_record_events_records_approved_key_insights_list(tmp_path: Path) -> None:
    """Approved key_insights emits feedback with list snapshots."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "2"},
        "llm_output": {"source_summary": {"key_insights": ["a", "b"]}},
        "review": {
            "source_summary": {
                "key_insights": {
                    "status": "approved",
                    "final_list": None,
                    "llm_list": ["a", "b"],
                    "notes": "",
                },
            },
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 1


def test_record_events_glossary_per_section(tmp_path: Path) -> None:
    """Non-pending glossary sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "3"},
        "llm_output": {
            "glossary": [
                {
                    "term": "RAG",
                    "proposed_definition": "Retrieval-augmented generation.",
                    "related_terms": ["embeddings"],
                },
            ],
        },
        "review": {
            "glossary": [
                {
                    "proposal_id": "g1",
                    "notes": None,
                    "llm_item": {
                        "term": "RAG",
                        "proposed_definition": "Retrieval-augmented generation.",
                        "related_terms": ["embeddings"],
                    },
                    "sections": {
                        "term": {"status": "approved", "final_text": None, "notes": None},
                        "proposed_definition": {
                            "status": "modified",
                            "final_text": "Revised def.",
                            "notes": None,
                        },
                        "extended_explanation": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "supporting_snippet": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "relevance_note": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "related_terms": {
                            "status": "approved",
                            "final_list": None,
                            "notes": None,
                            "llm_list": ["embeddings"],
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 3


def test_record_events_glossary_all_pending_emits_zero(tmp_path: Path) -> None:
    """All-pending glossary sections emit no events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "3"},
        "llm_output": {"glossary": [{"term": "RAG"}]},
        "review": {
            "glossary": [
                {
                    "proposal_id": "g1",
                    "notes": None,
                    "llm_item": {"term": "RAG"},
                    "sections": {
                        "term": {"status": "pending", "final_text": None, "notes": None},
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 0


def test_record_events_impl_study_per_section(tmp_path: Path) -> None:
    """Non-pending impl study sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "3"},
        "llm_output": {
            "implementation_studies": [
                {"title": "Pilot", "company": "Co", "overview": "Tested AI."},
            ],
        },
        "review": {
            "implementation_studies": [
                {
                    "proposal_id": "p1",
                    "notes": None,
                    "llm_item": {"title": "Pilot", "company": "Co", "overview": "Tested AI."},
                    "sections": {
                        "title": {"status": "approved", "final_text": None, "notes": None},
                        "company": {"status": "approved", "final_text": None, "notes": None},
                        "overview": {
                            "status": "modified",
                            "final_text": "Revised overview.",
                            "notes": None,
                        },
                        "key_lessons": {
                            "status": "pending",
                            "final_list": None,
                            "notes": None,
                            "llm_list": [],
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 3


def test_record_events_impl_study_all_pending_emits_zero(tmp_path: Path) -> None:
    """All-pending impl study sections emit no events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "3"},
        "llm_output": {"implementation_studies": [{"title": "T"}]},
        "review": {
            "implementation_studies": [
                {
                    "proposal_id": "p1",
                    "notes": None,
                    "llm_item": {"title": "T"},
                    "sections": {
                        "title": {"status": "pending", "final_text": None, "notes": None},
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 0


def test_record_events_topic_per_section(tmp_path: Path) -> None:
    """Non-pending topic sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "4"},
        "llm_output": {
            "topics": [
                {
                    "topic_slug": "ctx-eng",
                    "topic_title": "Context Engineering",
                    "key_points": ["p1"],
                },
            ],
        },
        "review": {
            "topics": [
                {
                    "proposal_id": "t1",
                    "notes": None,
                    "llm_item": {
                        "topic_slug": "ctx-eng",
                        "topic_title": "Context Engineering",
                        "key_points": ["p1"],
                    },
                    "sections": {
                        "topic_slug": {"status": "approved", "final_text": None, "notes": None},
                        "topic_title": {"status": "approved", "final_text": None, "notes": None},
                        "knowledge_summary": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "key_points": {
                            "status": "approved",
                            "final_list": None,
                            "notes": None,
                            "llm_list": ["p1"],
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 3


def test_record_events_howto_per_section(tmp_path: Path) -> None:
    """Non-pending how-to sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "4"},
        "llm_output": {
            "how_to": [
                {"question_title": "Q?", "answer_summary": "A."},
            ],
        },
        "review": {
            "how_to": [
                {
                    "proposal_id": "h1",
                    "notes": None,
                    "llm_item": {"question_title": "Q?", "answer_summary": "A."},
                    "sections": {
                        "question_title": {
                            "status": "approved",
                            "final_text": None,
                            "notes": None,
                        },
                        "answer_summary": {
                            "status": "modified",
                            "final_text": "Revised.",
                            "notes": None,
                        },
                        "supporting_snippet": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 2


def test_record_events_tool_per_section(tmp_path: Path) -> None:
    """Non-pending tool sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "5"},
        "llm_output": {
            "tools": [
                {
                    "name": "Cursor",
                    "short_description": "AI IDE.",
                    "core_capabilities": ["codebase indexing"],
                },
            ],
        },
        "review": {
            "tools": [
                {
                    "proposal_id": "tl1",
                    "notes": None,
                    "llm_item": {
                        "name": "Cursor",
                        "short_description": "AI IDE.",
                        "core_capabilities": ["codebase indexing"],
                    },
                    "sections": {
                        "name": {"status": "approved", "final_text": None, "notes": None},
                        "short_description": {
                            "status": "modified",
                            "final_text": "Revised.",
                            "notes": None,
                        },
                        "operational_relevance": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "core_capabilities": {
                            "status": "approved",
                            "final_list": None,
                            "notes": None,
                            "llm_list": ["codebase indexing"],
                        },
                    },
                    "types": {
                        "approved_types": ["coding-agent"],
                        "proposed_new_type": None,
                        "approved_new_type": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 3


def test_record_events_model_per_section(tmp_path: Path) -> None:
    """Non-pending foundation model sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "6"},
        "llm_output": {
            "foundation_models": [
                {
                    "model_name": "GPT-5",
                    "provider": "OpenAI",
                    "operational_summary": "Strong for coding.",
                    "core_capabilities": ["long-context"],
                },
            ],
        },
        "review": {
            "foundation_models": [
                {
                    "proposal_id": "m1",
                    "notes": None,
                    "llm_item": {
                        "model_name": "GPT-5",
                        "provider": "OpenAI",
                        "operational_summary": "Strong for coding.",
                        "core_capabilities": ["long-context"],
                    },
                    "sections": {
                        "model_name": {"status": "approved", "final_text": None, "notes": None},
                        "provider": {
                            "status": "modified",
                            "final_text": "OpenAI Inc.",
                            "notes": None,
                        },
                        "operational_summary": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "core_capabilities": {
                            "status": "approved",
                            "final_list": None,
                            "notes": None,
                            "llm_list": ["long-context"],
                        },
                    },
                    "types": {
                        "approved_types": ["frontier-model"],
                        "proposed_new_type": None,
                        "approved_new_type": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 3


def test_record_events_trend_per_section(tmp_path: Path) -> None:
    """Non-pending trend sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "4"},
        "llm_output": {
            "industry_trends": [
                {
                    "trend_slug": "cost-collapse",
                    "trend_title": "Cost Collapse",
                    "supporting_data_points": ["dp1"],
                },
            ],
        },
        "review": {
            "industry_trends": [
                {
                    "proposal_id": "tr1",
                    "notes": None,
                    "llm_item": {
                        "trend_slug": "cost-collapse",
                        "trend_title": "Cost Collapse",
                        "supporting_data_points": ["dp1"],
                    },
                    "sections": {
                        "trend_slug": {
                            "status": "approved",
                            "final_text": None,
                            "notes": None,
                        },
                        "trend_title": {
                            "status": "approved",
                            "final_text": None,
                            "notes": None,
                        },
                        "supporting_data_points": {
                            "status": "rejected",
                            "final_list": None,
                            "notes": None,
                            "llm_list": ["dp1"],
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 3


def test_record_events_source_type_detection(tmp_path: Path) -> None:
    """Approved source_type_detection emits one feedback event."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "7"},
        "llm_output": {
            "source_type_detection": {
                "detected_source_type": "ai_industry_roundup",
                "confidence": 0.9,
                "reasoning": ["Multi-item digest"],
            },
        },
        "review": {
            "source_type_detection": {
                "status": "approved",
                "notes": "Confirmed.",
                "llm_item": {
                    "detected_source_type": "ai_industry_roundup",
                    "confidence": 0.9,
                    "reasoning": ["Multi-item digest"],
                },
                "final_item": None,
            },
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 1


def test_record_events_roundup_signal_per_section(tmp_path: Path) -> None:
    """Non-pending roundup signal sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "7"},
        "llm_output": {
            "roundup_signals": [
                {
                    "signal_title": "Sig",
                    "signal_type": "trend",
                    "suggested_destinations": ["topics/"],
                },
            ],
        },
        "review": {
            "roundup_signals": [
                {
                    "proposal_id": "s1",
                    "notes": None,
                    "llm_item": {
                        "signal_title": "Sig",
                        "signal_type": "trend",
                        "suggested_destinations": ["topics/"],
                    },
                    "sections": {
                        "signal_title": {
                            "status": "approved",
                            "final_text": None,
                            "notes": None,
                        },
                        "signal_type": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "suggested_destinations": {
                            "status": "modified",
                            "final_list": ["trends/"],
                            "notes": None,
                            "llm_list": ["topics/"],
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 2


def test_record_events_interview_insight_per_section(tmp_path: Path) -> None:
    """Non-pending interview insight sections emit per-section feedback events."""
    db = tmp_path / "fb.sqlite"
    artifact = {
        "source": {"source_id": "x", "content_sha256": "h"},
        "analysis_meta": {"provider": "openai", "model": "m", "prompt_version": "7"},
        "llm_output": {
            "interview_insights": [
                {
                    "insight_title": "Insight",
                    "insight_type": "topic",
                    "contrarian_or_speculative_claims": ["claim1"],
                },
            ],
        },
        "review": {
            "interview_insights": [
                {
                    "proposal_id": "i1",
                    "notes": None,
                    "llm_item": {
                        "insight_title": "Insight",
                        "insight_type": "topic",
                        "contrarian_or_speculative_claims": ["claim1"],
                    },
                    "sections": {
                        "insight_title": {
                            "status": "approved",
                            "final_text": None,
                            "notes": None,
                        },
                        "insight_type": {
                            "status": "pending",
                            "final_text": None,
                            "notes": None,
                        },
                        "contrarian_or_speculative_claims": {
                            "status": "rejected",
                            "final_list": None,
                            "notes": None,
                            "llm_list": ["claim1"],
                        },
                    },
                    "tags": {
                        "final_primary_tag": None,
                        "final_secondary_tag": None,
                        "new_tag_approved": False,
                    },
                },
            ],
        },
    }
    n = record_events_from_artifact(db, artifact)
    assert n == 2
