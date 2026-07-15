"""Tests for generated-file writer."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render.models import RenderedFile
from src.wiki_render.writer import write_rendered_files


def test_writer_skips_unchanged_files_and_records_manifest(tmp_path: Path) -> None:
    """Re-running with identical content does not rewrite files."""
    wiki_dir = tmp_path / "wiki"
    manifest = tmp_path / "state" / "wiki_render_manifest.json"
    files = [RenderedFile(relative_path="topics/example.md", text="hello\n")]

    first = write_rendered_files(
        wiki_dir=wiki_dir,
        files=files,
        manifest_path=manifest,
        run_metadata={"tool_version": "1"},
        prune=True,
    )
    second = write_rendered_files(
        wiki_dir=wiki_dir,
        files=files,
        manifest_path=manifest,
        run_metadata={"tool_version": "1"},
        prune=True,
    )

    assert first.written == 1
    assert first.write_paths == ("topics/example.md",)
    assert second.unchanged == 1
    assert manifest.is_file()


def test_writer_prunes_only_manifest_tracked_files(tmp_path: Path) -> None:
    """Prune deletes stale generated files but not untracked neighbors."""
    wiki_dir = tmp_path / "wiki"
    manifest = tmp_path / "state" / "wiki_render_manifest.json"
    write_rendered_files(
        wiki_dir=wiki_dir,
        files=[RenderedFile(relative_path="topics/old.md", text="old\n")],
        manifest_path=manifest,
        run_metadata={},
        prune=True,
    )
    untracked = wiki_dir / "topics" / "manual.md"
    untracked.write_text("manual\n", encoding="utf-8")

    report = write_rendered_files(
        wiki_dir=wiki_dir,
        files=[RenderedFile(relative_path="topics/new.md", text="new\n")],
        manifest_path=manifest,
        run_metadata={},
        prune=True,
    )

    assert report.pruned == 1
    assert report.prune_paths == ("topics/old.md",)
    assert not (wiki_dir / "topics" / "old.md").exists()
    assert untracked.exists()


def test_writer_does_not_prune_notes_folder(tmp_path: Path) -> None:
    """Files under wiki/notes/ are outside managed folders and never pruned."""
    wiki_dir = tmp_path / "wiki"
    manifest = tmp_path / "state" / "wiki_render_manifest.json"
    notes_file = wiki_dir / "notes" / "scratch.md"
    notes_file.parent.mkdir(parents=True)
    notes_file.write_text("# scratch\n", encoding="utf-8")

    write_rendered_files(
        wiki_dir=wiki_dir,
        files=[RenderedFile(relative_path="topics/only.md", text="only\n")],
        manifest_path=manifest,
        run_metadata={},
        prune=True,
    )

    assert notes_file.exists()
