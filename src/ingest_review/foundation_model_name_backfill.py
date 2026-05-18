"""Infer missing ``model_name`` on foundation-model proposals after classification."""

from __future__ import annotations

import re
from collections.abc import Sequence

from src.ingest_review.schema import (
    FoundationModelProposal,
    LlmClassificationOutput,
    SourceSummaryBlock,
)

_MODEL_NAME_TOKEN = r"[A-Z][A-Za-z0-9]+(?:\s+(?:V?\d+(?:\.\d+)?|[A-Z0-9][A-Za-z0-9.-]+)){0,2}"
_USES_NAME_RE = re.compile(rf"\b({_MODEL_NAME_TOKEN})\s+uses\b")
_DROPPED_NAME_RE = re.compile(rf"\b({_MODEL_NAME_TOKEN})\s+dropped\b")
_DESCRIBES_AS_RE = re.compile(
    rf"(?:describes|presents)\s+({_MODEL_NAME_TOKEN})\s+as\b",
    re.IGNORECASE,
)
_ROUNDUP_TRIPLE_RE = re.compile(
    r"([A-Z][A-Za-z0-9][A-Za-z0-9 .-]*?),\s+"
    r"([A-Z][A-Za-z0-9][A-Za-z0-9 .-]*?),\s+and\s+"
    r"([A-Z][A-Za-z0-9][A-Za-z0-9 .-]*?)\s+are\s+included",
    re.IGNORECASE,
)


def _text_blobs(proposal: FoundationModelProposal) -> list[str]:
    """Collect searchable text from one proposal."""
    return [
        proposal.supporting_snippet,
        proposal.maturity_signals,
        proposal.operational_profile,
        proposal.deployment_implications,
        proposal.weaknesses_limitations,
        " ".join(proposal.core_capabilities),
        " ".join(proposal.comparative_observations),
    ]


def _longest_wiki_name_in_text(text: str, wiki_names: Sequence[str]) -> str | None:
    """Return the longest wiki model name that appears as a substring in *text*."""
    if not text.strip():
        return None
    lower = text.lower()
    best: str | None = None
    best_len = 0
    for raw in wiki_names:
        name = raw.strip()
        if len(name) < 3:
            continue
        if name.lower() in lower and len(name) > best_len:
            best = name
            best_len = len(name)
    return best


def _regex_name_from_text(text: str) -> str | None:
    """Extract a model name from common article phrasing."""
    if not text.strip():
        return None
    for pattern in (_USES_NAME_RE, _DROPPED_NAME_RE, _DESCRIBES_AS_RE):
        match = pattern.search(text)
        if match:
            candidate = match.group(1).strip(" \"'.,;")
            if len(candidate) >= 3:
                return candidate
    return None


def _roundup_triple_names(source_summary_text: str) -> list[str]:
    """Parse lists like ``Mercury 2, Kimi K2.5, and DeepSeek V4 are included``."""
    match = _ROUNDUP_TRIPLE_RE.search(source_summary_text)
    if not match:
        return []
    return [g.strip() for g in match.groups() if g.strip()]


def infer_foundation_model_name(
    proposal: FoundationModelProposal,
    *,
    wiki_names: Sequence[str],
    source_summary_text: str = "",
) -> str:
    """Best-effort model title when the LLM left ``model_name`` empty."""
    if proposal.model_name.strip():
        return proposal.model_name.strip()

    for blob in _text_blobs(proposal):
        from_regex = _regex_name_from_text(blob)
        if from_regex:
            return from_regex
        from_wiki = _longest_wiki_name_in_text(blob, wiki_names)
        if from_wiki:
            return from_wiki

    combined = " ".join(_text_blobs(proposal))
    from_wiki = _longest_wiki_name_in_text(combined, wiki_names)
    if from_wiki:
        return from_wiki

    for name in _roundup_triple_names(source_summary_text):
        if name.lower() in combined.lower():
            return name

    return ""


def _source_summary_text(summary: SourceSummaryBlock | None) -> str:
    if summary is None:
        return ""
    parts = [
        summary.summary,
        summary.why_it_matters,
        summary.accessible_overview,
        " ".join(summary.key_insights),
    ]
    return " ".join(p for p in parts if p)


def backfill_foundation_model_names(
    parsed: LlmClassificationOutput,
    wiki_names: Sequence[str],
) -> LlmClassificationOutput:
    """Fill empty ``model_name`` fields using snippets, wiki names, and source summary."""
    if not parsed.foundation_models:
        return parsed

    summary_text = _source_summary_text(parsed.source_summary)
    roundup_names = _roundup_triple_names(summary_text)
    assigned: set[str] = set()

    new_models: list[FoundationModelProposal] = []
    for proposal in parsed.foundation_models:
        if proposal.model_name.strip():
            new_models.append(proposal)
            assigned.add(proposal.model_name.strip().lower())
            continue

        name = infer_foundation_model_name(
            proposal,
            wiki_names=wiki_names,
            source_summary_text=summary_text,
        )
        if name:
            assigned.add(name.lower())
            new_models.append(proposal.model_copy(update={"model_name": name}))
            continue
        new_models.append(proposal)

    still_empty = [m for m in new_models if not m.model_name.strip()]
    if still_empty and roundup_names:
        remaining = [n for n in roundup_names if n.lower() not in assigned]
        for proposal, fallback in zip(still_empty, remaining, strict=False):
            idx = new_models.index(proposal)
            new_models[idx] = proposal.model_copy(update={"model_name": fallback})
            assigned.add(fallback.lower())

    return parsed.model_copy(update={"foundation_models": new_models})
