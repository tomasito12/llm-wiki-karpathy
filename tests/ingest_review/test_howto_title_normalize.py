"""Tests for how-to page title normalization."""

from __future__ import annotations

from src.ingest_review.howto_title_normalize import (
    howto_title_needs_normalization,
    normalize_howto_proposal,
    normalize_howto_question_title,
)
from src.ingest_review.schema import HowToProposal


def test_voicebot_interrogative_title_normalizes() -> None:
    """User-reported pattern: interrogative + qualifier → noun phrase + qualifier split."""
    raw = "How do you evaluate a production voicebot at scale without reviewing every call?"
    page, qual = normalize_howto_question_title(raw)
    assert page == "Evaluation of a Production Voicebot"
    assert "without" in qual.lower() or "scale" in qual.lower()


def test_howto_title_needs_normalization_detects_question_mark() -> None:
    assert howto_title_needs_normalization("Evaluation of X?")
    assert not howto_title_needs_normalization("Evaluation of a Production Voicebot")


def test_already_good_title_unchanged() -> None:
    good = "Evaluation of a Production Voicebot"
    page, qual = normalize_howto_question_title(good)
    assert page == good
    assert qual == ""


def test_normalize_howto_proposal_merges_qualifier_into_what_and_problem() -> None:
    hp = HowToProposal(
        question_title=(
            "How do you evaluate a production voicebot when you cannot review every call?"
        ),
        what_and_problem="",
    )
    out = normalize_howto_proposal(hp)
    assert out.question_title == "Evaluation of a Production Voicebot"
    assert "cannot review" in out.what_and_problem.lower() or "when" in out.what_and_problem.lower()


def test_how_to_prefix_stripped() -> None:
    page, _ = normalize_howto_question_title("How to build an eval pipeline for RAG")
    assert page.lower().startswith("building") or page.lower().startswith("build")
    assert "?" not in page
    assert not page.lower().startswith("how")
