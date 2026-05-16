"""Align glossary ``related_terms`` strings to canonical ``term`` labels (batch + wiki)."""

from __future__ import annotations

import re
from collections.abc import Sequence

from src.ingest_review.schema import GlossaryProposal, LlmClassificationOutput
from src.ingest_review.wiki_snapshot import WikiSnapshot

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "and",
        "or",
        "to",
        "from",
        "in",
        "on",
        "for",
        "with",
        "by",
        "as",
        "at",
    }
)


def normalize_glossary_label(s: str) -> str:
    """Lowercase and collapse internal whitespace for comparison."""
    return " ".join(str(s).strip().lower().split())


def _letter_acronym_key(term: str) -> str:
    """First-letter acronym (significant words only), lowercase, or \"\" if unusable."""
    words = re.findall(r"[A-Za-z]+", term)
    letters: list[str] = []
    for w in words:
        if w.lower() in _STOPWORDS:
            continue
        letters.append(w[0].lower())
    if len(letters) < 2:
        return ""
    return "".join(letters)


def _compact_alnum_lower(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def build_related_term_resolution_maps(
    batch_terms: Sequence[str],
    wiki_terms: Sequence[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Return (normalized_label_to_canonical, acronym_key_to_canonical).

    Batch ``term`` strings take precedence over wiki for the same normalized key.
    Acronym keys are only registered when exactly one canonical phrase produces that key
    (across batch then wiki, deduped by first occurrence).
    """
    batch = [str(t).strip() for t in batch_terms if str(t).strip()]
    wiki = [str(t).strip() for t in wiki_terms if str(t).strip()]
    norm_to: dict[str, str] = {}
    for c in batch:
        n = normalize_glossary_label(c)
        if n not in norm_to:
            norm_to[n] = c
    for c in wiki:
        n = normalize_glossary_label(c)
        if n not in norm_to:
            norm_to[n] = c

    ordered = list(dict.fromkeys(batch + wiki))
    acr_groups: dict[str, list[str]] = {}
    for c in ordered:
        a = _letter_acronym_key(c)
        if not a:
            continue
        acr_groups.setdefault(a, []).append(c)
    acr_to = {a: cs[0] for a, cs in acr_groups.items() if len(cs) == 1}
    return norm_to, acr_to


def resolve_related_term_to_canonical(
    raw: str,
    norm_to: dict[str, str],
    acr_to: dict[str, str],
) -> str:
    """Map one related-term string to its canonical label, or return *raw* unchanged."""
    r = str(raw).strip()
    if not r:
        return r
    n = normalize_glossary_label(r)
    if n in norm_to:
        return norm_to[n]
    compact = _compact_alnum_lower(r)
    if len(compact) >= 2 and compact in acr_to:
        return acr_to[compact]
    return r


def related_term_matches_known_label(
    raw: str,
    norm_to: dict[str, str],
    acr_to: dict[str, str],
) -> bool:
    """True if *raw* is empty or matches a batch/wiki label via normalization or unique acronym."""
    r = str(raw).strip()
    if not r:
        return True
    if normalize_glossary_label(r) in norm_to:
        return True
    compact = _compact_alnum_lower(r)
    return len(compact) >= 2 and compact in acr_to


def align_glossary_proposals_related_terms(
    proposals: Sequence[GlossaryProposal],
    wiki_glossary_terms: Sequence[str],
) -> list[GlossaryProposal]:
    """Rewrite related_terms on each proposal to canonical spellings; dedupe by norm key."""
    batch = [p.term for p in proposals]
    norm_to, acr_to = build_related_term_resolution_maps(batch, wiki_glossary_terms)
    out: list[GlossaryProposal] = []
    for p in proposals:
        rel = [str(x) for x in p.related_terms if str(x).strip()]
        new_rel: list[str] = []
        seen: set[str] = set()
        for r in rel:
            canon = resolve_related_term_to_canonical(r, norm_to, acr_to)
            kn = normalize_glossary_label(canon)
            if kn in seen:
                continue
            seen.add(kn)
            new_rel.append(canon)
        out.append(p.model_copy(update={"related_terms": new_rel}))
    return out


def align_glossary_related_terms(
    parsed: LlmClassificationOutput,
    wiki: WikiSnapshot,
) -> LlmClassificationOutput:
    """Apply :func:`align_glossary_proposals_related_terms` to ``parsed.glossary``."""
    if not parsed.glossary:
        return parsed
    new_g = align_glossary_proposals_related_terms(parsed.glossary, wiki.glossary_terms)
    return parsed.model_copy(update={"glossary": new_g})
