"""Tests for wiki baseline reset."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from src.readwise.library_index import LibraryIndex
from src.wiki_reset.reset import (
    CONFIRMATION_PHRASE,
    clear_ingest_manifest,
    clear_readwise_export_index,
    clear_sources_seen_state,
    default_readwise_index_path,
    delete_non_instruction_wiki_files,
    is_instruction_wiki_file,
    run_wiki_reset,
    wiki_instruction_relpaths,
    write_wiki_shell_files,
)


def test_is_instruction_wiki_file_matches_allowlist() -> None:
    """Known instruction paths are recognized."""
    assert is_instruction_wiki_file("AGENTS.md") is True
    assert is_instruction_wiki_file("sources/foo.md") is False


def test_wiki_instruction_relpaths_is_non_empty() -> None:
    """Instruction set is non-empty and stable."""
    paths = wiki_instruction_relpaths()
    assert len(paths) == 4
    assert "ingest-templates.md" in paths


def test_delete_non_instruction_wiki_files_keeps_instructions(tmp_path: Path) -> None:
    """Only non-instruction files are removed."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("keep", encoding="utf-8")
    (wiki / "sources").mkdir()
    (wiki / "sources" / "x.md").write_text("gone", encoding="utf-8")

    deleted = delete_non_instruction_wiki_files(wiki)
    assert deleted == ["sources/x.md"]
    assert (wiki / "AGENTS.md").read_text(encoding="utf-8") == "keep"
    assert not (wiki / "sources" / "x.md").exists()


def test_clear_readwise_export_index_writes_empty(tmp_path: Path) -> None:
    """Index file is replaced with an empty library index."""
    path = tmp_path / "readwise_library.json"
    path.write_text(
        '{"version": 1, "last_updated_after": "2020-01-01T00:00:00+00:00", '
        '"documents": {"a": {"html_path": "x", "md_path": "y", '
        '"source_url": null, "updated_at": null, "content_sha256": null}}}',
        encoding="utf-8",
    )
    clear_readwise_export_index(path)
    loaded = LibraryIndex.load(path)
    assert loaded.documents == {}
    assert loaded.last_updated_after is None


def test_clear_sources_seen_state_writes_empty(tmp_path: Path) -> None:
    """Sources-seen state is cleared to an empty sources map."""
    path = tmp_path / "sources_seen.json"
    path.write_text('{"sources": {"rss": {"x": {}}}}', encoding="utf-8")
    clear_sources_seen_state(path)
    assert path.read_text(encoding="utf-8").strip() == '{\n  "sources": {}\n}'


def test_clear_ingest_manifest_writes_empty(tmp_path: Path) -> None:
    """Ingest manifest is cleared to an empty records map."""
    path = tmp_path / "ingest_manifest.json"
    path.write_text('{"records": {"x": {}}}', encoding="utf-8")
    clear_ingest_manifest(path)
    text = path.read_text(encoding="utf-8")
    assert '"records": {}' in text


def test_run_wiki_reset_creates_shells(tmp_path: Path) -> None:
    """Reset removes content and writes hub files."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("instr", encoding="utf-8")
    (wiki / "tools").mkdir()
    (wiki / "tools" / "x.md").write_text("bye", encoding="utf-8")
    idx = tmp_path / "state" / "lib.json"
    sources_seen = tmp_path / "state" / "sources_seen.json"
    manifest = tmp_path / "state" / "ingest_manifest.json"

    deleted, state_results = run_wiki_reset(
        wiki,
        idx,
        clear_readwise_index=True,
        sources_seen_path=sources_seen,
        manifest_path=manifest,
    )
    assert "tools/x.md" in deleted
    assert state_results == {
        "readwise_library": True,
        "sources_seen": True,
        "ingest_manifest": True,
    }
    assert (wiki / "index.md").exists()
    assert (wiki / "glossary" / "index.md").exists()
    assert (wiki / "questions" / "question-catalog.md").exists()
    assert not (wiki / "tools").exists()
    log_text = (wiki / "log.md").read_text(encoding="utf-8")
    assert "ingest_manifest cleared" in log_text
    assert "readwise_library cleared" in log_text
    assert "sources_seen cleared" in log_text
    assert '"documents": {}' in idx.read_text(encoding="utf-8")
    assert '"sources": {}' in sources_seen.read_text(encoding="utf-8")
    assert '"records": {}' in manifest.read_text(encoding="utf-8")


def test_run_wiki_reset_keep_readwise_logs_unchanged(tmp_path: Path) -> None:
    """When skipping index clear, log states Readwise was left unchanged."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("x", encoding="utf-8")
    idx = tmp_path / "lib.json"
    idx.write_text('{"version": 1}', encoding="utf-8")
    sources_seen = tmp_path / "sources_seen.json"
    sources_seen.write_text('{"sources": {"rss": {}}}', encoding="utf-8")
    manifest = tmp_path / "ingest_manifest.json"
    manifest.write_text('{"records": {"x": {}}}', encoding="utf-8")

    _deleted, state_results = run_wiki_reset(
        wiki,
        idx,
        clear_readwise_index=False,
        sources_seen_path=sources_seen,
        manifest_path=manifest,
        clear_source_state=False,
        clear_manifest=False,
    )
    assert state_results == {
        "readwise_library": False,
        "sources_seen": False,
        "ingest_manifest": False,
    }
    log_text = (wiki / "log.md").read_text(encoding="utf-8")
    assert "readwise_library preserved" in log_text
    assert "sources_seen preserved" in log_text
    assert "ingest_manifest preserved" in log_text
    assert idx.read_text(encoding="utf-8") == '{"version": 1}'
    assert sources_seen.read_text(encoding="utf-8") == '{"sources": {"rss": {}}}'
    assert manifest.read_text(encoding="utf-8") == '{"records": {"x": {}}}'


def test_default_readwise_index_path_is_under_state() -> None:
    """Default index path points at state/readwise_library.json."""
    p = default_readwise_index_path()
    assert p.name == "readwise_library.json"
    assert p.parent.name == "state"


def test_write_wiki_shell_files_writes_expected_frontmatter(tmp_path: Path) -> None:
    """Shell writer produces expected frontmatter types."""
    wiki = tmp_path / "w"
    write_wiki_shell_files(
        wiki,
        today_iso="2099-01-01",
        state_results={
            "readwise_library": False,
            "sources_seen": False,
            "ingest_manifest": False,
        },
    )
    text = (wiki / "index.md").read_text(encoding="utf-8")
    assert "type: index" in text
    assert "[[glossary/index]]" in text


def test_run_wiki_reset_missing_wiki_dir_raises(tmp_path: Path) -> None:
    """FileNotFoundError when wiki root is not a directory."""
    missing = tmp_path / "nope"
    with pytest.raises(FileNotFoundError, match="not a directory"):
        run_wiki_reset(missing, tmp_path / "i.json")


def test_main_wrong_confirm_exits_one() -> None:
    """CLI rejects wrong non-interactive confirmation phrase."""
    from src.wiki_reset import cli

    with mock.patch.object(cli.sys, "argv", ["wiki-reset", "--confirm", "nope"]):
        assert cli.main() == 1


def test_main_confirm_ok_runs_reset(tmp_path: Path) -> None:
    """CLI accepts matching --confirm and runs reset."""
    from src.wiki_reset import cli

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    idx = tmp_path / "idx.json"
    sources_seen = tmp_path / "sources_seen.json"
    manifest = tmp_path / "manifest.json"

    argv = [
        "wiki-reset",
        "--wiki-dir",
        str(wiki),
        "--index",
        str(idx),
        "--sources-seen",
        str(sources_seen),
        "--manifest",
        str(manifest),
        "--confirm",
        CONFIRMATION_PHRASE,
    ]
    with mock.patch.object(cli.sys, "argv", argv):
        assert cli.main() == 0
    assert (wiki / "index.md").exists()
    loaded = LibraryIndex.load(idx)
    assert loaded.documents == {}
    assert sources_seen.exists()
    assert manifest.exists()
