"""Tests for wiki-synthesis-select CLI."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_synthesis import select_cli


def test_select_cli_json_output(tmp_path: Path, capsys) -> None:
    """Select CLI should print valid JSON with ranked entries."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "knowledge_pages": [
                    {
                        "entity_id": "topic:example",
                        "category": "topic",
                        "slug": "example",
                        "title": "Example",
                        "path": "topics/example.md",
                        "source_ids": ["a", "b"],
                        "source_count": 2,
                        "evidence_count": 2,
                        "tags": ["chatbot"],
                        "evidence": [
                            {
                                "evidence_id": "ev-1",
                                "text": "Evidence",
                                "source_id": "a",
                                "field": "knowledge_summary",
                                "stance": "supporting",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = select_cli.main(
        [
            "--graph-path",
            str(graph_path),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--json",
            "--limit",
            "5",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["total_changed"] == 1
    assert payload["entries"][0]["entity_id"] == "topic:example"


def test_select_cli_commands_output(tmp_path: Path, capsys) -> None:
    """Select CLI command mode should print workflow invocations."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "knowledge_pages": [
                    {
                        "entity_id": "topic:example",
                        "category": "topic",
                        "slug": "example",
                        "title": "Example",
                        "path": "topics/example.md",
                        "source_ids": ["a", "b"],
                        "source_count": 2,
                        "evidence_count": 2,
                        "tags": [],
                        "evidence": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = select_cli.main(
        [
            "--graph-path",
            str(graph_path),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--commands",
            "--limit",
            "1",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "hatch run wiki-synthesis-workflow --entity topic:example --yes" in captured
