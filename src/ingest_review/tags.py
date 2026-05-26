"""Load review-layer tag allowlists from YAML config."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.ingest_review.paths import repo_root

_TAG_SLUG_RE = re.compile(r"[^a-z0-9]+")

MAX_PROPOSED_TAGS = 5


def normalize_tag(raw: str) -> str:
    """Normalize a tag slug: lowercase kebab-case, stripped."""
    s = raw.strip().lower().replace("_", "-")
    s = _TAG_SLUG_RE.sub("-", s)
    return s.strip("-")


def normalize_tag_list(
    raw: list[str] | None,
    *,
    cap: int = MAX_PROPOSED_TAGS,
) -> list[str]:
    """Dedupe normalized tags; preserve order; apply *cap* when positive."""
    if not raw:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        nt = normalize_tag(str(item))
        if not nt or nt in seen:
            continue
        seen.add(nt)
        out.append(nt)
        if cap > 0 and len(out) >= cap:
            break
    return out


def _tag_tokens(tag: str) -> set[str]:
    """Split a normalized tag into hyphen tokens."""
    return {t for t in tag.split("-") if t}


def _similarity_score(candidate: str, existing: str) -> float:
    """Heuristic similarity in [0, 1] for warning-only near-duplicate detection."""
    if not candidate or not existing:
        return 0.0
    if candidate == existing:
        return 0.0
    if candidate in existing or existing in candidate:
        return 0.92
    ct = _tag_tokens(candidate)
    et = _tag_tokens(existing)
    if not ct or not et:
        return 0.0
    overlap = len(ct & et) / max(len(ct), len(et))
    if overlap >= 0.5:
        return 0.75 + 0.2 * overlap
    # prefix family (e.g. agent-* )
    parts_c = candidate.split("-")
    parts_e = existing.split("-")
    if len(parts_c) >= 2 and len(parts_e) >= 2 and parts_c[0] == parts_e[0]:
        if parts_c[0] in ("agent", "workflow", "model", "tool", "ai"):
            return 0.7
    # light Levenshtein ratio for typos / minor rewording
    if len(candidate) > 3 and len(existing) > 3:
        dist = _levenshtein(candidate, existing)
        mx = max(len(candidate), len(existing))
        ratio = 1.0 - dist / mx
        if ratio >= 0.82:
            return ratio
    return 0.0


def _levenshtein(a: str, b: str) -> int:
    """Classic Levenshtein distance (small strings only)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def find_similar_tags(
    candidate: str,
    allowlist: list[str],
    *,
    max_results: int = 5,
    min_score: float = 0.65,
) -> list[str]:
    """Return allowlist tags that may be near-duplicates of *candidate* (warning only)."""
    norm = normalize_tag(candidate)
    if not norm:
        return []
    allow_set = {normalize_tag(t) for t in allowlist if t}
    if norm in allow_set:
        return []
    scored: list[tuple[float, str]] = []
    for tag in allow_set:
        if not tag or tag == norm:
            continue
        score = _similarity_score(norm, tag)
        if score >= min_score:
            scored.append((score, tag))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [t for _, t in scored[:max_results]]


def build_tag_select_options(allowlist: list[str], llm_item: dict[str, object]) -> list[str]:
    """Options for primary/secondary selectboxes: empty, allowlist, orphan LLM values."""
    options: list[str] = [""]
    seen: set[str] = set()
    for t in allowlist:
        nt = normalize_tag(str(t))
        if nt and nt not in seen:
            seen.add(nt)
            options.append(nt)
    for key in ("primary_tag", "secondary_tag"):
        raw = normalize_tag(str(llm_item.get(key) or ""))
        if raw and raw not in seen:
            seen.add(raw)
            options.append(raw)
    return options


def load_tag_list(path: Path) -> list[str]:
    """Load a YAML file that is either a bare list or ``{ tags: [...] }``."""
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [normalize_tag(str(x)) for x in raw if str(x).strip()]
    if isinstance(raw, dict) and "tags" in raw:
        inner = raw["tags"]
        if isinstance(inner, list):
            return [normalize_tag(str(x)) for x in inner if str(x).strip()]
    return []


def default_tool_types_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tool_types.yaml``."""
    return (root or repo_root()) / "config" / "review_tool_types.yaml"


def default_howto_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_howto.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_howto.yaml"


def load_tool_types(root: Path | None = None) -> list[str]:
    """Return approved tool type registry."""
    return load_tag_list(default_tool_types_path(root))


def load_howto_tags(root: Path | None = None) -> list[str]:
    """Return how-to proposal tag allowlist (same vocabulary as topics)."""
    return load_topic_tags(root)


def default_tool_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_tools.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_tools.yaml"


def load_tool_tags(root: Path | None = None) -> list[str]:
    """Return tool retrieval-tag allowlist (distinct from product types)."""
    return load_tag_list(default_tool_tags_path(root))


def default_model_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_models.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_models.yaml"


def load_model_tags(root: Path | None = None) -> list[str]:
    """Return foundation-model retrieval-tag allowlist (distinct from model types)."""
    return load_tag_list(default_model_tags_path(root))


def default_glossary_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_glossary.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_glossary.yaml"


def load_glossary_tags(root: Path | None = None) -> list[str]:
    """Return glossary tag allowlist."""
    return load_tag_list(default_glossary_tags_path(root))


def default_topic_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_topics.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_topics.yaml"


def load_topic_tags(root: Path | None = None) -> list[str]:
    """Return topic tag allowlist."""
    return load_tag_list(default_topic_tags_path(root))


def default_trend_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_trends.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_trends.yaml"


def load_trend_tags(root: Path | None = None) -> list[str]:
    """Return trend tag allowlist."""
    return load_tag_list(default_trend_tags_path(root))


def default_model_types_path(root: Path | None = None) -> Path:
    """Path to ``config/review_model_types.yaml``."""
    return (root or repo_root()) / "config" / "review_model_types.yaml"


def load_model_types(root: Path | None = None) -> list[str]:
    """Return approved model type registry."""
    return load_tag_list(default_model_types_path(root))


def default_impl_study_tags_path(root: Path | None = None) -> Path:
    """Path to ``config/review_tags_impl_study.yaml``."""
    return (root or repo_root()) / "config" / "review_tags_impl_study.yaml"


def load_impl_study_tags(root: Path | None = None) -> list[str]:
    """Return implementation-study tag allowlist."""
    return load_tag_list(default_impl_study_tags_path(root))


def default_extraction_budgets_path(root: Path | None = None) -> Path:
    """Path to ``config/extraction_budgets.yaml``."""
    return (root or repo_root()) / "config" / "extraction_budgets.yaml"


def load_extraction_budgets(root: Path | None = None) -> dict[str, int]:
    """Return ``{entity_key: max_proposals}`` from the budgets config."""
    path = default_extraction_budgets_path(root)
    if not path.is_file():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    budgets_section = raw.get("extraction_budgets")
    if not isinstance(budgets_section, dict):
        return {}
    result: dict[str, int] = {}
    for key, val in budgets_section.items():
        if isinstance(val, dict) and "max" in val:
            result[str(key)] = int(val["max"])
        elif isinstance(val, int):
            result[str(key)] = val
    return result


def save_tag_list(path: Path, tags: list[str], *, comment: str | None = None) -> None:
    """Replace the full allowlist with a normalized, sorted, deduped tag list."""
    from src.pipeline.atomic import atomic_write_text

    normalized = sorted({normalize_tag(t) for t in tags if normalize_tag(t)})
    lines: list[str] = []
    if comment:
        lines.append(f"# {comment}")
    body = yaml.dump({"tags": normalized}, default_flow_style=False, sort_keys=False)
    lines.append(body.rstrip())
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, "\n".join(lines))


def add_tags_to_list(path: Path, new_tags: list[str]) -> list[str]:
    """Append normalized tags not already on the allowlist. Returns slugs added."""
    existing = load_tag_list(path)
    existing_set = set(existing)
    to_add: list[str] = []
    for raw in new_tags:
        nt = normalize_tag(str(raw))
        if nt and nt not in existing_set and nt not in to_add:
            to_add.append(nt)
            existing_set.add(nt)
    if not to_add:
        return []
    save_tag_list(path, existing + to_add)
    return to_add


def remove_tags_from_list(path: Path, tags_to_remove: list[str]) -> list[str]:
    """Remove tags from the allowlist. Returns slugs that were removed."""
    remove_set = {normalize_tag(str(t)) for t in tags_to_remove if normalize_tag(str(t))}
    if not remove_set:
        return []
    current = load_tag_list(path)
    removed = [t for t in current if t in remove_set]
    if not removed:
        return []
    remaining = [t for t in current if t not in remove_set]
    save_tag_list(path, remaining)
    return removed


def rename_tag_in_list(path: Path, old_slug: str, new_slug: str) -> None:
    """Rename one allowlist entry (YAML only; does not migrate review artifacts)."""
    old = normalize_tag(old_slug)
    new = normalize_tag(new_slug)
    if not old:
        raise ValueError("old slug is empty")
    if not new:
        raise ValueError("new slug is empty")
    if old == new:
        return
    current = load_tag_list(path)
    if old not in current:
        raise ValueError(f"tag not in allowlist: {old}")
    if new in current:
        raise ValueError(f"tag already exists: {new}")
    updated = [new if t == old else t for t in current]
    save_tag_list(path, updated)


def append_tags_to_yaml(path: Path, new_tags: list[str]) -> None:
    """Append new tags to a YAML allowlist file, deduplicating."""
    add_tags_to_list(path, new_tags)


def parse_comma_separated_tags(raw: str) -> list[str]:
    """Split comma-separated user input into normalized tag slugs."""
    return normalize_tag_list(
        [x.strip() for x in raw.split(",") if x.strip()],
        cap=0,
    )
