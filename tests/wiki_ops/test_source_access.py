"""Tests for private-vault source-access verification."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_ops.source_access import collect_source_access_status


def test_collect_source_access_status_reports_complete_embedded_access(
    tmp_path: Path,
) -> None:
    """Embedded text, raw Markdown, graph pages, and wikilinks should verify cleanly."""
    wiki_dir = tmp_path / "vault" / "wiki"
    source_dir = wiki_dir / "sources"
    raw_dir = tmp_path / "knowledge" / "raw" / "readwise"
    source_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)
    (source_dir / "source-a.md").write_text(
        """---
source_id: source-a
source_text_available: true
source_text_mode: full
---

# Source A

## Full source text

The complete local article body.
""",
        encoding="utf-8",
    )
    (raw_dir / "source-a.md").write_text("The canonical article body.", encoding="utf-8")
    (wiki_dir / "topics").mkdir()
    (wiki_dir / "topics" / "topic-a.md").write_text(
        "## Sources\n\n- [[sources/source-a|Source A]]\n",
        encoding="utf-8",
    )
    graph_path = tmp_path / "knowledge" / "state" / "wiki_render_graph.json"
    graph_path.parent.mkdir()
    graph_path.write_text(
        json.dumps({"sources": [{"source_id": "source-a"}]}),
        encoding="utf-8",
    )

    status, warnings = collect_source_access_status(
        wiki_dir=wiki_dir,
        raw_dir=raw_dir,
        graph_path=graph_path,
    )

    assert status.wiki_dir_exists is True
    assert status.source_pages_total == 1
    assert status.embedded_full_text == 1
    assert status.locally_linked_source_text == 0
    assert status.external_url_only == 0
    assert status.graph_sources == 1
    assert status.graph_sources_missing_pages == []
    assert status.source_links_total == 1
    assert status.broken_source_link_targets == []
    assert warnings == []


def test_collect_source_access_status_classifies_access_and_integrity_gaps(
    tmp_path: Path,
) -> None:
    """Local links, external-only pages, malformed pages, and broken links stay visible."""
    wiki_dir = tmp_path / "wiki"
    source_dir = wiki_dir / "sources"
    raw_dir = tmp_path / "raw"
    source_dir.mkdir(parents=True)
    raw_dir.mkdir()
    (source_dir / "wrong-name.md").write_text(
        """---
source_id: source-local
source_text_available: false
---

# Local source

[[../raw/readwise/source-local.md|Local raw Markdown]]
""",
        encoding="utf-8",
    )
    (raw_dir / "source-local.md").write_text("Raw body.", encoding="utf-8")
    (source_dir / "source-external.md").write_text(
        """---
source_id: source-external
source_text_available: false
canonical_url: https://example.test/article
---

# External-only source
""",
        encoding="utf-8",
    )
    (source_dir / "malformed.md").write_text("# Missing frontmatter\n", encoding="utf-8")
    (wiki_dir / "topics").mkdir()
    (wiki_dir / "topics" / "topic.md").write_text(
        "[[sources/source-missing|Missing source]]\n",
        encoding="utf-8",
    )
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "sources": [
                    {"source_id": "source-local"},
                    {"source_id": "source-external"},
                    {"source_id": "source-missing"},
                ]
            }
        ),
        encoding="utf-8",
    )

    status, warnings = collect_source_access_status(
        wiki_dir=wiki_dir,
        raw_dir=raw_dir,
        graph_path=graph_path,
    )

    assert status.source_pages_total == 3
    assert status.embedded_full_text == 0
    assert status.locally_linked_source_text == 1
    assert status.external_url_only == 1
    assert status.malformed_pages == ["sources/malformed.md"]
    assert status.source_id_mismatches == ["sources/wrong-name.md"]
    assert status.source_pages_missing_raw_markdown == ["sources/source-external.md"]
    assert status.graph_sources_missing_pages == ["source-missing"]
    assert status.broken_source_link_targets == ["sources/source-missing"]
    assert len(warnings) == 6


def test_collect_source_access_status_reports_missing_wiki_directory(
    tmp_path: Path,
) -> None:
    """A missing generated vault should return an empty report and a clear warning."""
    missing_wiki = tmp_path / "missing-wiki"

    status, warnings = collect_source_access_status(
        wiki_dir=missing_wiki,
        raw_dir=tmp_path / "raw",
        graph_path=tmp_path / "graph.json",
    )

    assert status.wiki_dir_exists is False
    assert status.source_pages_total == 0
    assert status.graph_sources is None
    assert warnings == [f"Source access cannot be verified; wiki directory missing: {missing_wiki}"]


def test_collect_source_access_status_warns_when_graph_is_unreadable(
    tmp_path: Path,
) -> None:
    """Malformed graph JSON should make graph comparison explicitly unavailable."""
    wiki_dir = tmp_path / "wiki"
    (wiki_dir / "sources").mkdir(parents=True)
    graph_path = tmp_path / "graph.json"
    graph_path.write_text("{invalid", encoding="utf-8")

    status, warnings = collect_source_access_status(
        wiki_dir=wiki_dir,
        raw_dir=tmp_path / "raw",
        graph_path=graph_path,
    )

    assert status.graph_sources is None
    assert warnings == [f"Source access graph comparison unavailable: {graph_path}"]
