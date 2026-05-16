"""Build compact title lists from the wiki for LLM dedupe prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path


def _read_text(path: Path) -> str:
    """Return file text or empty string if missing."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _strip_wikilink(inner: str) -> str:
    """Normalize ``[[path|alias]]`` or ``[[path]]`` to path."""
    inner = inner.strip()
    if "|" in inner:
        return inner.split("|", 1)[0].strip()
    return inner


def parse_glossary_terms(glossary_index: Path, *, cap: int = 200) -> list[str]:
    """Parse first column (term names) from ``wiki/glossary/index.md`` table."""
    text = _read_text(glossary_index)
    terms: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or line.startswith("| Term"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) >= 1 and "[[" not in parts[0]:
            term = parts[0]
            if term and term != "Term":
                terms.append(term)
        elif len(parts) >= 1:
            m = re.search(r"\[\[([^\]]+)\]\]", parts[0])
            if m:
                link = _strip_wikilink(m.group(1))
                slug = Path(link).stem.replace("-", " ")
                terms.append(slug)
    return terms[:cap]


def parse_topic_titles(index_path: Path, *, cap: int = 200) -> list[str]:
    """Parse topic titles from ``wiki/topics/index.md`` table rows."""
    text = _read_text(index_path)
    titles: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Topic" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        if "[[" in cell:
            m = re.search(r"\[\[topics/([^]|]+)\]\]", cell)
            if m:
                slug = Path(m.group(1)).stem
                titles.append(slug.replace("-", " "))
        elif cell and cell != "Topic":
            titles.append(cell)
    return titles[:cap]


def parse_topic_slugs(index_path: Path, *, cap: int = 200) -> list[str]:
    """Parse kebab-case topic slugs from ``wiki/topics/index.md`` (for cross-link validation)."""
    from src.ingest_review.tags import normalize_tag

    text = _read_text(index_path)
    slugs: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Topic" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        slug = ""
        if "[[" in cell:
            m = re.search(r"\[\[topics/([^]|]+)\]\]", cell)
            if m:
                slug = normalize_tag(Path(m.group(1)).stem)
        elif cell and cell != "Topic":
            slug = normalize_tag(cell)
        if slug and slug not in seen:
            seen.add(slug)
            slugs.append(slug)
    return slugs[:cap]


def parse_howto_titles(index_path: Path, *, cap: int = 200) -> list[str]:
    """Parse how-to titles from ``wiki/howtos/index.md`` table rows."""
    text = _read_text(index_path)
    titles: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "How" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        if "[[" in cell:
            m = re.search(r"\[\[howtos/([^]|]+)\]\]", cell)
            if m:
                slug = Path(m.group(1)).stem
                titles.append(slug.replace("-", " "))
        elif cell and cell != "How-to":
            titles.append(cell)
    return titles[:cap]


def parse_trend_titles(index_path: Path, *, cap: int = 200) -> list[str]:
    """Parse trend titles from ``wiki/trends/index.md`` table rows."""
    text = _read_text(index_path)
    titles: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Trend" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        if "[[" in cell:
            m = re.search(r"\[\[trends/([^]|]+)\]\]", cell)
            if m:
                slug = Path(m.group(1)).stem
                titles.append(slug.replace("-", " "))
        elif cell and cell != "Trend":
            titles.append(cell)
    return titles[:cap]


def parse_trend_slugs(index_path: Path, *, cap: int = 200) -> list[str]:
    """Parse kebab-case trend slugs from ``wiki/trends/index.md`` (for cross-link validation)."""
    from src.ingest_review.tags import normalize_tag

    text = _read_text(index_path)
    slugs: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Trend" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        slug = ""
        if "[[" in cell:
            m = re.search(r"\[\[trends/([^]|]+)\]\]", cell)
            if m:
                slug = normalize_tag(Path(m.group(1)).stem)
        elif cell and cell != "Trend":
            slug = normalize_tag(cell)
        if slug and slug not in seen:
            seen.add(slug)
            slugs.append(slug)
    return slugs[:cap]


def parse_tools_index(tools_index: Path, wiki_tools: Path, *, cap: int = 400) -> list[str]:
    """Collect tool names from master tools index and category index tables."""
    names: list[str] = []
    master = _read_text(tools_index)
    for line in master.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Category" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) >= 1:
            m = re.search(r"\[\[tools/([^]|]+)\]\]", parts[0])
            if m:
                rel = m.group(1).strip()
                if rel.endswith("/index"):
                    category_dir = rel[: -len("/index")]
                    cat_index = wiki_tools / category_dir / "index.md"
                    names.extend(_parse_tool_category_table(cat_index, wiki_tools))
    dedup: list[str] = []
    seen: set[str] = set()
    for n in names:
        if n not in seen:
            seen.add(n)
            dedup.append(n)
    return dedup[:cap]


def _parse_tool_category_table(category_index: Path, wiki_tools: Path) -> list[str]:
    """Parse ``| Tool | Page |`` rows in a category index."""
    text = _read_text(category_index)
    found: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Tool" in line[:20]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        if "[[" in cell:
            m = re.search(r"\[\[tools/([^]|]+)\]\]", cell)
            if m:
                slug = Path(m.group(1)).stem
                if slug != "index":
                    found.append(slug.replace("-", " "))
        elif cell and cell != "Tool":
            found.append(cell)
    return found


def parse_foundation_model_names(index_path: Path, *, cap: int = 150) -> list[str]:
    """Parse model names from ``wiki/foundation-models/index.md``."""
    text = _read_text(index_path)
    names: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Model" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        if "[[" in cell:
            m = re.search(r"\[\[foundation-models/([^]|]+)\]\]", cell)
            if m:
                slug = Path(m.group(1)).stem
                names.append(slug.replace("-", " "))
        elif cell and cell != "Model":
            names.append(cell)
    return names[:cap]


def parse_implementation_study_titles(index_path: Path, *, cap: int = 200) -> list[str]:
    """Parse implementation-study titles from ``wiki/implementations/index.md``."""
    text = _read_text(index_path)
    titles: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|--") or "Title" in line[:15]:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if not parts:
            continue
        cell = parts[0]
        if "[[" in cell:
            m = re.search(r"\[\[implementations/([^]|]+)\]\]", cell)
            if m:
                slug = Path(m.group(1)).stem
                titles.append(slug.replace("-", " "))
        elif cell and cell != "Title":
            titles.append(cell)
    return titles[:cap]


@dataclass(frozen=True)
class WikiSnapshot:
    """Capped lists for injection into analysis prompts."""

    glossary_terms: list[str]
    tool_names: list[str]
    foundation_model_names: list[str]
    implementation_study_titles: list[str] = dataclass_field(default_factory=list)
    topic_titles: list[str] = dataclass_field(default_factory=list)
    topic_slugs: list[str] = dataclass_field(default_factory=list)
    howto_titles: list[str] = dataclass_field(default_factory=list)
    trend_titles: list[str] = dataclass_field(default_factory=list)
    trend_slugs: list[str] = dataclass_field(default_factory=list)


def build_wiki_snapshot(wiki_root: Path, *, cap_per_list: int = 200) -> WikiSnapshot:
    """Scan wiki paths under ``wiki_root`` and return snapshot lists."""
    glossary_index = wiki_root / "glossary" / "index.md"
    tools_index = wiki_root / "tools" / "index.md"
    wiki_tools = wiki_root / "tools"
    fm_index = wiki_root / "foundation-models" / "index.md"
    impl_index = wiki_root / "implementations" / "index.md"
    topics_index = wiki_root / "topics" / "index.md"
    howtos_index = wiki_root / "howtos" / "index.md"
    trends_index = wiki_root / "trends" / "index.md"
    return WikiSnapshot(
        glossary_terms=parse_glossary_terms(glossary_index, cap=cap_per_list),
        tool_names=parse_tools_index(tools_index, wiki_tools, cap=cap_per_list * 2),
        foundation_model_names=parse_foundation_model_names(fm_index, cap=cap_per_list),
        implementation_study_titles=parse_implementation_study_titles(impl_index, cap=cap_per_list),
        topic_titles=parse_topic_titles(topics_index, cap=cap_per_list),
        topic_slugs=parse_topic_slugs(topics_index, cap=cap_per_list),
        howto_titles=parse_howto_titles(howtos_index, cap=cap_per_list),
        trend_titles=parse_trend_titles(trends_index, cap=cap_per_list),
        trend_slugs=parse_trend_slugs(trends_index, cap=cap_per_list),
    )
