"""Heuristic gate for implementation-study proposals (post-LLM, pre-artifact)."""

from __future__ import annotations

import re

from src.ingest_review.schema import EvidenceSnippet, ImplementationStudyProposal

_IMPL_EVIDENCE_KEYWORDS = re.compile(
    r"\b("
    r"production|pilot|rolled\s+out|deployed|deployment|scaled|scale|"
    r"metric|metrics|%|latency|cost|tickets|users|customers|"
    r"failed|failure|incident|outage|rollout|adoption|"
    r"contact\s+center|call\s+center|hospital|enterprise"
    r")\b",
    re.IGNORECASE,
)

_FILLER_OUTCOME = frozenset(
    {
        "",
        "unknown",
        "tbd",
        "n/a",
        "not stated",
        "unclear",
        "not specified",
    }
)


def _field_text(proposal: ImplementationStudyProposal, *keys: str) -> str:
    parts: list[str] = []
    for key in keys:
        val = getattr(proposal, key, "")
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    return " ".join(parts)


def _has_operational_keyword_signal(proposal: ImplementationStudyProposal) -> bool:
    blob = _field_text(
        proposal,
        "deployment_context",
        "outcome_status",
        "operational_constraints",
        "success_or_failure_factors",
    )
    return bool(_IMPL_EVIDENCE_KEYWORDS.search(blob))


def _stated_snippet_count(snippets: list[EvidenceSnippet]) -> int:
    return sum(1 for s in snippets if s.provenance == "stated" and (s.snippet or s.claim))


def _specific_nonempty(text: str) -> bool:
    norm = text.strip().lower()
    return bool(norm) and norm not in _FILLER_OUTCOME and len(norm) >= 12


def impl_study_meets_evidence_threshold(proposal: ImplementationStudyProposal) -> bool:
    """Return True when proposal has minimum operational deployment evidence."""
    snippets = proposal.evidence_snippets
    stated_count = _stated_snippet_count(snippets)
    if len(snippets) < 2 or stated_count < 1:
        return False
    if not _specific_nonempty(proposal.deployment_context):
        return False
    if not _specific_nonempty(proposal.outcome_status):
        return False
    if not (proposal.company or "").strip():
        return False
    return _has_operational_keyword_signal(proposal)


def demote_weak_impl_study(proposal: ImplementationStudyProposal) -> ImplementationStudyProposal:
    """Demote proposals that fail the evidence threshold (reviewer-visible, default reject)."""
    return proposal.model_copy(
        update={
            "suggested_action": "ignore",
            "value_level": "low",
            "confidence": min(float(proposal.confidence), 0.25),
        }
    )


def filter_impl_study_proposals(
    proposals: list[ImplementationStudyProposal],
) -> list[ImplementationStudyProposal]:
    """Apply evidence gate; demote weak proposals instead of dropping them."""
    return [
        p if impl_study_meets_evidence_threshold(p) else demote_weak_impl_study(p)
        for p in proposals
    ]


def format_impl_study_evidence_caption(llm_item: dict[str, object]) -> str:
    """Compact evidence summary for dashboard cards."""
    from src.ingest_review.schema import ImplementationStudyProposal

    proposal = ImplementationStudyProposal.model_validate(llm_item)
    snippets = proposal.evidence_snippets
    stated = _stated_snippet_count(snippets)
    deploy = "yes" if _specific_nonempty(proposal.deployment_context) else "no"
    outcomes = "yes" if _specific_nonempty(proposal.outcome_status) else "no"
    keywords = "yes" if _has_operational_keyword_signal(proposal) else "no"
    gate = "pass" if impl_study_meets_evidence_threshold(proposal) else "weak"
    return (
        f"Evidence gate: {gate} · Deployment: {deploy} · Outcomes: {outcomes} · "
        f"Ops signals: {keywords} · Stated snippets: {stated}/{len(snippets)}"
    )


def impl_study_likely_misclassified(llm_item: dict[str, object]) -> bool:
    """True when the proposal lacks stated deployment evidence (reviewer hint)."""
    from src.ingest_review.schema import ImplementationStudyProposal

    proposal = ImplementationStudyProposal.model_validate(llm_item)
    if impl_study_meets_evidence_threshold(proposal):
        return False
    snippets = proposal.evidence_snippets
    if not snippets:
        return True
    return _stated_snippet_count(snippets) == 0
