"""Tests for how-to two-column helpers (no Streamlit runtime)."""

from __future__ import annotations

from src.ingest_review.howtos_ui import (
    apply_howto_proposal_edits,
    apply_howto_scalar_edit,
    build_readonly_howtos_markdown,
    effective_howto_scalar,
    format_howto_proposal_readonly_markdown,
)


def _sample_node() -> dict:
    return {
        "proposal_id": "abc",
        "proposal_status": "approved",
        "llm_item": {
            "question_title": "How to chunk?",
            "answer_summary": "Use overlapping windows.",
            "value_level": "high",
            "confidence": 0.9,
            "evidence_type": "independent_analysis",
        },
        "sections": {},
        "tags": {},
    }


def test_effective_howto_scalar_prefers_final_text() -> None:
    llm = {"question_title": "Draft"}
    sections = {"question_title": {"final_text": "Final title", "status": "modified"}}
    assert effective_howto_scalar(llm, sections, "question_title") == "Final title"


def test_apply_howto_scalar_edit_modified_when_differs() -> None:
    sections: dict = {}
    llm = {"answer_summary": "Original"}
    apply_howto_scalar_edit(sections, llm, "answer_summary", "Edited")
    assert sections["answer_summary"]["status"] == "modified"
    assert sections["answer_summary"]["final_text"] == "Edited"


def test_format_howto_readonly_includes_title() -> None:
    md = format_howto_proposal_readonly_markdown(_sample_node(), [])
    assert "How to chunk?" in md
    assert "Approved" in md


def test_format_howto_readonly_shows_what_and_problem_before_summary() -> None:
    node = _sample_node()
    node["llm_item"]["what_and_problem"] = "Chunking helps models read long documents."
    md = format_howto_proposal_readonly_markdown(node, [])
    assert "**What is it and what problem does it solve?**" in md
    assert "Chunking helps models read long documents." in md
    assert md.index("What is it") < md.index("Answer summary")
    assert "Relevance" not in md


def test_build_readonly_howtos_markdown_empty() -> None:
    assert "No how-to" in build_readonly_howtos_markdown([], [])


def test_apply_howto_proposal_edits_all_reviewable_fields() -> None:
    node = _sample_node()
    apply_howto_proposal_edits(
        node,
        {
            "question_title": "How to chunk?",
            "what_and_problem": "Chunking splits long text into pieces.",
            "answer_summary": "New summary",
            "caveats": "",
            "implementation_steps": "step one",
            "prerequisites": "",
        },
    )
    assert node["sections"]["answer_summary"]["status"] == "modified"
