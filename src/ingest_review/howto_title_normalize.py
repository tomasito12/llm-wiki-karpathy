"""Normalize LLM how-to question_title values into broad wiki page titles."""

from __future__ import annotations

import re

from src.ingest_review.schema import HowToProposal

# Interrogative openers the model often copies from sources.
_INTERROGATIVE_PREFIX_RE = re.compile(
    r"^(?:"
    r"how to\s+"
    r"|how do you\s+"
    r"|how do we\s+"
    r"|how should you\s+"
    r"|how should we\s+"
    r"|how can you\s+"
    r"|how can we\s+"
    r"|how would you\s+"
    r"|what is the best way to\s+"
    r"|what's the best way to\s+"
    r"|when should you\s+"
    r"|when should we\s+"
    r")",
    re.IGNORECASE,
)

# Trailing situational clauses → what_and_problem, not title.
_QUALIFIER_TAIL_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"\s+without\s+.+$", re.IGNORECASE),
    re.compile(r"\s+when\s+.+$", re.IGNORECASE),
    re.compile(r"\s+if\s+.+$", re.IGNORECASE),
    re.compile(r"\s+for teams that\s+.+$", re.IGNORECASE),
    re.compile(r"\s+at scale\s+.+$", re.IGNORECASE),
    re.compile(r"\s+at scale\s*$", re.IGNORECASE),
)

# Leading verb → noun-phrase page title stem.
_VERB_TO_NOUN: dict[str, str] = {
    "evaluate": "evaluation of",
    "evaluating": "evaluation of",
    "choose": "choosing",
    "choosing": "choosing",
    "select": "selecting",
    "selecting": "selecting",
    "pick": "choosing",
    "build": "building",
    "building": "building",
    "create": "creating",
    "creating": "creating",
    "design": "design of",
    "designing": "design of",
    "implement": "implementation of",
    "implementing": "implementation of",
    "deploy": "deployment of",
    "deploying": "deployment of",
    "measure": "measurement of",
    "measuring": "measurement of",
    "monitor": "monitoring",
    "monitoring": "monitoring",
    "test": "testing",
    "testing": "testing",
    "debug": "debugging",
    "debugging": "debugging",
    "compare": "comparing",
    "comparing": "comparing",
    "integrate": "integration of",
    "integrating": "integration of",
    "optimize": "optimization of",
    "optimizing": "optimization of",
    "improve": "improving",
    "improving": "improving",
    "configure": "configuration of",
    "configuring": "configuration of",
    "set up": "setup of",
    "setup": "setup of",
    "run": "running",
    "running": "running",
    "train": "training",
    "training": "training",
    "fine-tune": "fine-tuning",
    "fine tune": "fine-tuning",
}

_SMALL_WORDS = frozenset({"a", "an", "the", "of", "for", "in", "on", "to", "and", "or", "with"})


def howto_title_needs_normalization(title: str) -> bool:
    """Return True if *title* looks like an interrogative or over-qualified question."""
    t = title.strip()
    if not t:
        return False
    if t.endswith("?"):
        return True
    if _INTERROGATIVE_PREFIX_RE.match(t):
        return True
    lower = t.lower()
    return any(
        needle in lower
        for needle in (
            " without ",
            " when ",
            " if ",
            " how do you ",
            " how to ",
            " how should ",
        )
    )


def _strip_qualifier_tail(core: str) -> tuple[str, str]:
    """Split trailing constraint clause from the procedural core phrase."""
    qualifiers: list[str] = []
    text = core.strip()
    changed = True
    while changed and text:
        changed = False
        for pat in _QUALIFIER_TAIL_RES:
            m = pat.search(text)
            if m:
                qualifiers.insert(0, m.group(0).strip())
                text = text[: m.start()].strip()
                changed = True
                break
    qual = "; ".join(q for q in qualifiers if q)
    return text, qual


def _title_case_phrase(phrase: str) -> str:
    """Title-case a short noun phrase; keep small words lower except at start."""
    words = phrase.split()
    if not words:
        return ""
    out: list[str] = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i > 0 and lw in _SMALL_WORDS:
            out.append(lw)
        elif w.isupper() and len(w) > 1:
            out.append(w)
        else:
            out.append(lw.capitalize())
    return " ".join(out)


def _core_to_page_title(core: str) -> str:
    """Turn a verb-led procedural phrase into a noun-phrase page title."""
    text = core.strip().rstrip("?").strip()
    if not text:
        return ""

    lower = text.lower()
    for verb, noun in sorted(_VERB_TO_NOUN.items(), key=lambda x: -len(x[0])):
        if lower == verb:
            return _title_case_phrase(noun)
        if lower.startswith(verb + " "):
            rest = text[len(verb) :].strip()
            return _title_case_phrase(f"{noun} {rest}")

    return _title_case_phrase(text)


def normalize_howto_question_title(title: str) -> tuple[str, str]:
    """Return ``(page_title, qualifier_text)`` for a raw LLM question_title.

      If *title* already looks like a page title, returns it unchanged with an
    empty qualifier.
    """
    raw = title.strip()
    if not raw:
        return "", ""

    if not howto_title_needs_normalization(raw):
        return raw, ""

    text = raw.rstrip("?").strip()
    text = _INTERROGATIVE_PREFIX_RE.sub("", text).strip()
    core, qual = _strip_qualifier_tail(text)
    page = _core_to_page_title(core)
    if not page:
        return raw, qual
    return page, qual


def _merge_qualifier_into_what_and_problem(what_and_problem: str, qualifier: str) -> str:
    """Prepend extracted qualifier context when not already present."""
    qual = qualifier.strip().rstrip(".")
    if not qual:
        return what_and_problem.strip()
    existing = what_and_problem.strip()
    qual_lower = qual.lower()
    if existing and qual_lower in existing.lower():
        return existing
    prefix = f"This how-to addresses constraints including: {qual}."
    if not existing:
        return prefix
    return f"{prefix} {existing}"


def normalize_howto_proposal(proposal: HowToProposal) -> HowToProposal:
    """Normalize one how-to proposal title; fold qualifiers into what_and_problem."""
    page_title, qual = normalize_howto_question_title(proposal.question_title)
    if page_title == proposal.question_title.strip() and not qual:
        return proposal
    return proposal.model_copy(
        update={
            "question_title": page_title,
            "what_and_problem": _merge_qualifier_into_what_and_problem(
                proposal.what_and_problem, qual
            ),
        }
    )


def normalize_howto_titles_in_output(
    how_to: list[HowToProposal],
) -> list[HowToProposal]:
    """Normalize all how-to question_title fields in a classification pass."""
    return [normalize_howto_proposal(hp) for hp in how_to]
