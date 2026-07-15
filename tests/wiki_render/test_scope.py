"""Tests for wiki-render scope and artifact loading."""

from __future__ import annotations

import json
from pathlib import Path

from src.wiki_render.loader import load_review_artifacts
from src.wiki_render.models import RenderedFile
from src.wiki_render.scope import protected_prune_paths_for_in_progress
from src.wiki_render.writer import write_rendered_files


def _write_review(
    reviews_dir: Path,
    source_id: str,
    *,
    finished: bool,
    title: str,
) -> None:
    """Write a minimal review artifact for scope tests."""
    review_dir = reviews_dir / source_id
    review_dir.mkdir(parents=True)
    finished_at = "2026-05-01T00:00:00+00:00" if finished else None
    (review_dir / "review.json").write_text(
        json.dumps(
            {
                "source": {
                    "source_id": source_id,
                    "title": title,
                    "author": "",
                    "publication": "",
                    "canonical_url": "",
                    "published_date": "2026-01-01",
                    "content_sha256": "abc",
                    "raw_md_rel_path": f"raw/readwise/{source_id}.md",
                    "raw_html_rel_path": f"raw/readwise/{source_id}.html",
                },
                "analysis_meta": {"analysis_timestamp_utc": "2026-05-01T00:00:00+00:00"},
                "llm_output": {
                    "source_summary": {
                        "summary": "Summary",
                        "accessible_overview": "Overview",
                        "key_insights": [],
                        "why_it_matters": "Matters",
                        "limitations_and_open_questions": "Limits",
                        "contradictions_and_skepticism": "None",
                        "assessed_as_of": "2026-05-01",
                    }
                },
                "review": {"source_summary": {}, "topics": []},
                "review_analytics": {"review_finished_at": finished_at},
            }
        ),
        encoding="utf-8",
    )


def test_load_review_artifacts_defaults_to_finished_only(tmp_path: Path) -> None:
    """Default render scope should exclude in-progress review artifacts."""
    reviews_dir = tmp_path / "reviews"
    _write_review(reviews_dir, "finished-a", finished=True, title="Finished")
    _write_review(reviews_dir, "pending-b", finished=False, title="Pending")

    artifacts = load_review_artifacts(reviews_dir)

    assert len(artifacts) == 1
    assert artifacts[0]["source"]["source_id"] == "finished-a"


def test_load_review_artifacts_can_include_in_progress(tmp_path: Path) -> None:
    """Preview scope should include both finished and in-progress artifacts."""
    reviews_dir = tmp_path / "reviews"
    _write_review(reviews_dir, "finished-a", finished=True, title="Finished")
    _write_review(reviews_dir, "pending-b", finished=False, title="Pending")

    artifacts = load_review_artifacts(reviews_dir, include_in_progress=True)

    assert {item["source"]["source_id"] for item in artifacts} == {"finished-a", "pending-b"}


def test_writer_protects_in_progress_paths_from_prune(tmp_path: Path) -> None:
    """Finished-only renders must not delete in-progress preview files."""
    wiki_dir = tmp_path / "wiki"
    manifest = tmp_path / "manifest.json"
    in_progress_page = wiki_dir / "sources" / "pending-b.md"
    in_progress_page.parent.mkdir(parents=True)
    in_progress_page.write_text("# pending\n", encoding="utf-8")
    write_rendered_files(
        wiki_dir=wiki_dir,
        files=[
            RenderedFile(relative_path="sources/finished-a.md", text="# finished\n"),
            RenderedFile(relative_path="sources/pending-b.md", text="# pending\n"),
        ],
        manifest_path=manifest,
        run_metadata={},
        prune=True,
    )

    report = write_rendered_files(
        wiki_dir=wiki_dir,
        files=[RenderedFile(relative_path="sources/finished-a.md", text="# finished\n")],
        manifest_path=manifest,
        run_metadata={},
        prune=True,
        protected_paths={"sources/pending-b.md"},
    )

    assert in_progress_page.exists()
    assert report.protected_from_prune == 1
    assert report.pruned == 0


def test_protected_prune_paths_for_in_progress_returns_source_page_paths(
    tmp_path: Path,
) -> None:
    """Protected prune paths should include rendered files for in-progress reviews."""
    repo = tmp_path / "repo"
    reviews_dir = repo / "state" / "reviews"
    raw_dir = repo / "raw" / "readwise"
    wiki_dir = repo / "wiki"
    raw_dir.mkdir(parents=True)
    wiki_dir.mkdir()
    _write_review(reviews_dir, "pending-b", finished=False, title="Pending")
    (raw_dir / "pending-b.md").write_text("Body\n", encoding="utf-8")

    protected = protected_prune_paths_for_in_progress(
        reviews_dir=reviews_dir,
        wiki_dir=wiki_dir,
        raw_dir=raw_dir,
        repo_root=repo,
        synthesis_cache_dir=repo / "state" / "synthesis",
        taxonomy_version="tax-test",
    )

    assert "sources/pending-b.md" in protected
