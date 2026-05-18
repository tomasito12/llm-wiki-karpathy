"""Tests for inferring missing foundation model names after classification."""

from __future__ import annotations

from src.ingest_review.foundation_model_name_backfill import (
    backfill_foundation_model_names,
    infer_foundation_model_name,
)
from src.ingest_review.schema import (
    FoundationModelProposal,
    LlmClassificationOutput,
    SourceSummaryBlock,
)


def _mercury_proposal() -> FoundationModelProposal:
    return FoundationModelProposal(
        model_name="",
        supporting_snippet=(
            '"Most AI models generate text token by token. Mercury 2 uses a diffusion '
            'architecture, starting with a rough full output and refining it in parallel."'
        ),
        maturity_signals="Launched on February 24, 2026.",
        value_level="high",
        confidence=0.79,
    )


def _kimi_proposal() -> FoundationModelProposal:
    return FoundationModelProposal(
        model_name="",
        supporting_snippet=(
            '"One trillion total parameters, but only thirty-two billion activate per query '
            'thanks to a mixture-of-experts architecture. Coordinates up to 100 AI sub-agents."'
        ),
        maturity_signals="Released on January 27, 2026 with open access.",
        value_level="high",
        confidence=0.91,
    )


def _deepseek_proposal() -> FoundationModelProposal:
    return FoundationModelProposal(
        model_name="DeepSeek V4",
        supporting_snippet='"DeepSeek V4 dropped in early March 2026."',
        provider="DeepSeek",
        value_level="high",
        confidence=0.95,
    )


def test_infer_foundation_model_name_from_uses_pattern() -> None:
    name = infer_foundation_model_name(_mercury_proposal(), wiki_names=[])
    assert name == "Mercury 2"


def test_infer_foundation_model_name_preserves_existing() -> None:
    proposal = _deepseek_proposal()
    assert infer_foundation_model_name(proposal, wiki_names=[]) == "DeepSeek V4"


def test_backfill_assigns_roundup_names_by_elimination() -> None:
    summary = SourceSummaryBlock(
        why_it_matters=(
            "Mercury 2, Kimi K2.5, and DeepSeek V4 are included because the article "
            "emphasizes speed and multimodality."
        ),
    )
    parsed = LlmClassificationOutput(
        source_summary=summary,
        foundation_models=[_mercury_proposal(), _kimi_proposal(), _deepseek_proposal()],
    )
    wiki_names = ["Mercury 2", "Kimi K2.5", "DeepSeek V4", "GPT-5"]

    out = backfill_foundation_model_names(parsed, wiki_names)
    names = [m.model_name for m in out.foundation_models]

    assert names[0] == "Mercury 2"
    assert names[1] == "Kimi K2.5"
    assert names[2] == "DeepSeek V4"


def test_backfill_noop_when_all_named() -> None:
    parsed = LlmClassificationOutput(foundation_models=[_deepseek_proposal()])
    out = backfill_foundation_model_names(parsed, ["DeepSeek V4"])
    assert out.foundation_models[0].model_name == "DeepSeek V4"
