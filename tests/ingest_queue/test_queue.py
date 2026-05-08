"""Tests for ingest queue listing."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from src.ingest_queue.cli import main
from src.ingest_queue.queue import list_ingest_items


def test_list_items_pending_when_wiki_source_missing(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    wiki_sources = tmp_path / "wiki" / "sources"
    raw.mkdir()
    wiki_sources.mkdir(parents=True)
    stem = "article-01abc"
    (raw / f"{stem}.html").write_text("<p>x</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\n---\n", encoding="utf-8")

    items = list_ingest_items(raw, wiki_sources)
    assert len(items) == 1
    assert items[0].status == "pending"
    assert items[0].raw_md_path is not None


def test_list_items_ingested_when_wiki_source_exists(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    wiki_sources = tmp_path / "wiki" / "sources"
    raw.mkdir()
    wiki_sources.mkdir(parents=True)
    stem = "article-01abc"
    (raw / f"{stem}.html").write_text("<p>x</p>", encoding="utf-8")
    (raw / f"{stem}.md").write_text("---\n---\n", encoding="utf-8")
    (wiki_sources / f"{stem}.md").write_text("---\ntype: source\n---\n", encoding="utf-8")

    items = list_ingest_items(raw, wiki_sources)
    assert items[0].status == "ingested"


def test_list_items_incomplete_without_md_sidecar(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    wiki_sources = tmp_path / "wiki" / "sources"
    raw.mkdir()
    wiki_sources.mkdir(parents=True)
    (raw / "only.html").write_text("<p>x</p>", encoding="utf-8")

    items = list_ingest_items(raw, wiki_sources)
    assert len(items) == 1
    assert items[0].status == "incomplete"
    assert items[0].raw_md_path is None


def test_list_items_empty_raw_dir(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    wiki_sources = tmp_path / "wiki" / "sources"
    raw.mkdir()
    wiki_sources.mkdir(parents=True)
    assert list_ingest_items(raw, wiki_sources) == []


def test_cli_json_filter_and_limit(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    raw = tmp_path / "raw"
    wiki_sources = tmp_path / "wiki" / "sources"
    raw.mkdir()
    wiki_sources.mkdir(parents=True)
    for i in range(3):
        stem = f"doc-{i:02d}-id{i:02d}00000000000000000001"
        (raw / f"{stem}.html").write_text("<p>a</p>", encoding="utf-8")
        (raw / f"{stem}.md").write_text("---\n---\n", encoding="utf-8")

    argv = [
        "ingest-queue",
        "--raw-dir",
        str(raw),
        "--wiki-sources-dir",
        str(wiki_sources),
        "--status",
        "all",
        "--limit",
        "2",
        "--json",
    ]
    with mock.patch("sys.argv", argv):
        assert main() == 0
    out = capsys.readouterr().out
    rows = json.loads(out)
    assert len(rows) == 2
    assert {r["status"] for r in rows} == {"pending"}
