"""Tests for glossary related_terms canonical alignment."""

from __future__ import annotations

from src.ingest_review.glossary_related_terms_align import (
    align_glossary_proposals_related_terms,
    align_glossary_related_terms,
    build_related_term_resolution_maps,
    related_term_matches_known_label,
    resolve_related_term_to_canonical,
)
from src.ingest_review.schema import GlossaryProposal, LlmClassificationOutput, SourceTypeDetection
from src.ingest_review.wiki_snapshot import WikiSnapshot


def test_align_expands_acronym_to_batch_full_term() -> None:
    """RLHF in related_terms becomes the sibling term's canonical spelling."""
    props = [
        GlossaryProposal(term="Constitutional AI", related_terms=["RLHF"]),
        GlossaryProposal(term="Reinforcement Learning from Human Feedback", related_terms=[]),
    ]
    out = align_glossary_proposals_related_terms(props, [])
    assert out[0].related_terms == ["Reinforcement Learning from Human Feedback"]


def test_align_no_op_when_acronym_ambiguous() -> None:
    """Two batch terms yielding the same acronym key: do not rewrite raw related token."""
    props = [
        GlossaryProposal(term="Big Red Cat", related_terms=["brc"]),
        GlossaryProposal(term="Blue River Cave", related_terms=[]),
    ]
    out = align_glossary_proposals_related_terms(props, [])
    assert out[0].related_terms == ["brc"]


def test_align_wiki_only_normalized_match() -> None:
    """Related string matches EXISTING_GLOSSARY_TERMS after normalization."""
    props = [
        GlossaryProposal(term="Zebra", related_terms=["  neural network  "]),
    ]
    out = align_glossary_proposals_related_terms(props, ["Neural Network"])
    assert out[0].related_terms == ["Neural Network"]


def test_align_dedupes_after_rewrite() -> None:
    """Multiple raw strings collapsing to one canonical appear once."""
    props = [
        GlossaryProposal(
            term="A",
            related_terms=["RLHF", "Reinforcement Learning from Human Feedback"],
        ),
        GlossaryProposal(term="Reinforcement Learning from Human Feedback"),
    ]
    out = align_glossary_proposals_related_terms(props, [])
    assert out[0].related_terms == ["Reinforcement Learning from Human Feedback"]


def test_align_lmm_classification_output_wrapper() -> None:
    """align_glossary_related_terms updates parsed.glossary."""
    parsed = LlmClassificationOutput(
        source_type_detection=SourceTypeDetection(detected_source_type="standard_article"),
        glossary=[
            GlossaryProposal(term="X", related_terms=["y"]),
            GlossaryProposal(term="Y"),
        ],
    )
    wiki = WikiSnapshot(
        glossary_terms=[],
        tool_names=[],
        foundation_model_names=[],
        implementation_study_titles=[],
        topic_titles=[],
        howto_titles=[],
        trend_titles=[],
    )
    out = align_glossary_related_terms(parsed, wiki)
    assert out.glossary[0].related_terms == ["Y"]


def test_related_term_matches_known_acronym() -> None:
    norm_to, acr_to = build_related_term_resolution_maps(
        ["Reinforcement Learning from Human Feedback"],
        [],
    )
    assert related_term_matches_known_label("RLHF", norm_to, acr_to) is True


def test_resolve_unmatched_returns_raw() -> None:
    norm_to, acr_to = build_related_term_resolution_maps(["Alpha"], [])
    assert resolve_related_term_to_canonical("No such thing", norm_to, acr_to) == "No such thing"
