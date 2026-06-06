"""Shared wiki folder layout and preservation rules."""

from __future__ import annotations

SOURCES = "sources"
TOPICS = "topics"
GLOSSARY = "glossary"
INDUSTRY_TRENDS = "industry-trends"
TOOLS = "tools"
FOUNDATION_MODELS = "foundation-models"
HOW_TO = "how-to"
IMPLEMENTATION_STUDIES = "implementation-studies"
SIGNALS = "signals"
INTERVIEW_INSIGHTS = "interview-insights"
INDEXES = "indexes"
NOTES = "notes"
LEGACY_MANUAL_INGEST = "legacy/manual-ingest"

MANAGED_FOLDERS: tuple[str, ...] = (
    SOURCES,
    TOPICS,
    GLOSSARY,
    INDUSTRY_TRENDS,
    TOOLS,
    FOUNDATION_MODELS,
    HOW_TO,
    IMPLEMENTATION_STUDIES,
    SIGNALS,
    INTERVIEW_INSIGHTS,
    INDEXES,
)

PRESERVED_ROOT_FILES: frozenset[str] = frozenset(
    {
        "AGENTS.md",
        "index.md",
        "log.md",
    }
)

PRESERVED_WIKI_PREFIXES: tuple[str, ...] = (
    f"{NOTES}/",
    "legacy/",
)


def is_managed_relative_path(relative_path: str) -> bool:
    """Return True when a relative path is inside a generated managed folder."""
    first = relative_path.split("/", 1)[0]
    return first in MANAGED_FOLDERS


def is_preserved_wiki_path(relative_path: str) -> bool:
    """Return True when a wiki-relative path must survive reset operations."""
    if relative_path in PRESERVED_ROOT_FILES:
        return True
    return any(relative_path.startswith(prefix) for prefix in PRESERVED_WIKI_PREFIXES)


def is_lint_skipped_path(relative_path: str) -> bool:
    """Return True when wiki-lint should skip a path outside managed folders."""
    if is_preserved_wiki_path(relative_path):
        return True
    return not is_managed_relative_path(relative_path)


def category_folder_for_graph(graph_category: str) -> str:
    """Return the managed folder name for a graph category slug."""
    from src.wiki_contract.categories import spec_for_graph

    return spec_for_graph(graph_category).folder
