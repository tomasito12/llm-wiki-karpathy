"""Tests for wiki-synthesis-select CLI."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_synthesis import select_cli
from tests.wiki_synthesis.review_fixture import write_finished_review, write_paths_config


def test_select_cli_json_output(tmp_path: Path, capsys) -> None:
    """Select CLI should print valid JSON with ranked entries."""
    graph_path = tmp_path / "graph.json"
    reviews_dir = tmp_path / "reviews"
    write_finished_review(reviews_dir, "a")
    write_finished_review(reviews_dir, "b")
    config_path = write_paths_config(
        tmp_path,
        graph_path=graph_path,
        cache_dir=tmp_path / "cache",
        reviews_dir=reviews_dir,
    )
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
            "--paths-config",
            str(config_path),
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
    reviews_dir = tmp_path / "reviews"
    write_finished_review(reviews_dir, "a")
    write_finished_review(reviews_dir, "b")
    config_path = write_paths_config(
        tmp_path,
        graph_path=graph_path,
        cache_dir=tmp_path / "cache",
        reviews_dir=reviews_dir,
    )
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
            "--paths-config",
            str(config_path),
            "--commands",
            "--limit",
            "1",
        ]
    )
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "hatch run wiki-synthesis-workflow --entity topic:example --yes" in captured


def test_select_cli_paths_config_overrides_graph_and_cache(tmp_path: Path, capsys) -> None:
    """Select CLI should honor external paths from --paths-config."""
    external = tmp_path / "external"
    external.mkdir()
    graph_path = external / "graph.json"
    cache_dir = external / "cache"
    reviews_dir = external / "reviews"
    cache_dir.mkdir()
    write_finished_review(reviews_dir, "a")
    write_finished_review(reviews_dir, "b")
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
    config_path = write_paths_config(
        tmp_path,
        graph_path=graph_path,
        cache_dir=cache_dir,
        reviews_dir=reviews_dir,
    )

    exit_code = select_cli.main(
        [
            "--paths-config",
            str(config_path),
            "--json",
            "--limit",
            "1",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["total_changed"] == 1


def test_select_cli_explicit_graph_path_overrides_config(tmp_path: Path, capsys) -> None:
    """An explicit --graph-path flag should override config values."""
    config_graph = tmp_path / "config-graph.json"
    cli_graph = tmp_path / "cli-graph.json"
    reviews_dir = tmp_path / "reviews"
    write_finished_review(reviews_dir, "a")
    write_finished_review(reviews_dir, "b")
    for graph_path in (config_graph, cli_graph):
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
    config_path = write_paths_config(
        tmp_path,
        graph_path=config_graph,
        cache_dir=tmp_path / "cache",
        reviews_dir=reviews_dir,
    )

    exit_code = select_cli.main(
        [
            "--paths-config",
            str(config_path),
            "--graph-path",
            str(cli_graph),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--json",
            "--limit",
            "1",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["total_changed"] == 1
