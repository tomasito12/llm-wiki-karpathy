"""Tests for wiki-synthesis-batch CLI."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_synthesis import batch_cli
from tests.wiki_synthesis.review_fixture import write_finished_review, write_paths_config


def test_batch_cli_requires_yes_for_real_run(tmp_path: Path, caplog) -> None:
    """Batch CLI should refuse real runs without --yes."""
    graph_path = _write_graph(tmp_path)

    exit_code = batch_cli.main(
        [
            "--graph-path",
            str(graph_path),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--preview-dir",
            str(tmp_path / "previews"),
            "--report-dir",
            str(tmp_path / "runs"),
            "--limit",
            "1",
        ]
    )

    assert exit_code == 2
    assert "Refusing real synthesis batch without --yes" in caplog.text


def test_batch_cli_dry_run_json_output(tmp_path: Path, capsys, monkeypatch) -> None:
    """Dry-run batch CLI should print JSON without provider calls."""
    graph_path = _write_graph(tmp_path)
    reviews_dir = tmp_path / "reviews"
    write_finished_review(reviews_dir, "source-a")
    write_finished_review(reviews_dir, "source-b")
    config_path = write_paths_config(
        tmp_path,
        graph_path=graph_path,
        cache_dir=tmp_path / "cache",
        reviews_dir=reviews_dir,
        preview_dir=tmp_path / "previews",
        run_dir=tmp_path / "runs",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    exit_code = batch_cli.main(
        [
            "--paths-config",
            str(config_path),
            "--dry-run",
            "--json",
            "--limit",
            "1",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["dry_run"] is True
    assert payload["selected"] == 1
    assert payload["called"] == 0


def test_batch_cli_rejects_limit_below_one(tmp_path: Path) -> None:
    """Batch CLI should reject invalid limits."""
    graph_path = _write_graph(tmp_path)

    exit_code = batch_cli.main(
        [
            "--graph-path",
            str(graph_path),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--preview-dir",
            str(tmp_path / "previews"),
            "--report-dir",
            str(tmp_path / "runs"),
            "--dry-run",
            "--limit",
            "0",
        ]
    )

    assert exit_code == 2


def test_batch_cli_paths_config_overrides_graph_and_cache(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Batch CLI dry-run should honor external paths from --paths-config."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    external = tmp_path / "external"
    graph_path = external / "graph.json"
    cache_dir = external / "cache"
    preview_dir = external / "previews"
    report_dir = external / "runs"
    reviews_dir = external / "reviews"
    for directory in (cache_dir, preview_dir, report_dir):
        directory.mkdir(parents=True)
    write_finished_review(reviews_dir, "source-a")
    write_finished_review(reviews_dir, "source-b")
    graph_path.write_text(
        json.dumps(
            {
                "sources": [
                    {"source_id": "source-a", "title": "Source A"},
                    {"source_id": "source-b", "title": "Source B"},
                ],
                "knowledge_pages": [
                    {
                        "entity_id": "topic:example",
                        "category": "topic",
                        "slug": "example",
                        "title": "Example",
                        "path": "topics/example.md",
                        "aliases": [],
                        "tags": ["chatbot"],
                        "types": [],
                        "source_ids": ["source-a", "source-b"],
                        "source_count": 2,
                        "evidence_count": 2,
                        "value_level": "high",
                        "confidence": 0.9,
                        "evidence": [
                            {
                                "evidence_id": "evidence-a",
                                "text": "Example evidence.",
                                "source_id": "source-a",
                                "field": "knowledge_summary",
                                "stance": "supporting",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    config_path = write_paths_config(
        tmp_path,
        graph_path=graph_path,
        cache_dir=cache_dir,
        reviews_dir=reviews_dir,
        preview_dir=preview_dir,
        run_dir=report_dir,
    )

    exit_code = batch_cli.main(
        [
            "--paths-config",
            str(config_path),
            "--dry-run",
            "--json",
            "--limit",
            "1",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["dry_run"] is True
    assert payload["selected"] == 1


def _write_graph(tmp_path: Path) -> Path:
    """Write a minimal graph export for CLI tests."""
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "sources": [
                    {"source_id": "source-a", "title": "Source A"},
                    {"source_id": "source-b", "title": "Source B"},
                ],
                "knowledge_pages": [
                    {
                        "entity_id": "topic:example",
                        "category": "topic",
                        "slug": "example",
                        "title": "Example",
                        "path": "topics/example.md",
                        "aliases": [],
                        "tags": ["chatbot"],
                        "types": [],
                        "source_ids": ["source-a", "source-b"],
                        "source_count": 2,
                        "evidence_count": 2,
                        "value_level": "high",
                        "confidence": 0.9,
                        "evidence": [
                            {
                                "evidence_id": "evidence-a",
                                "text": "Example evidence.",
                                "source_id": "source-a",
                                "field": "knowledge_summary",
                                "stance": "supporting",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return graph_path
