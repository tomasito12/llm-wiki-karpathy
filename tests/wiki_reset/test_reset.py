"""Tests for wiki baseline reset."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from src.pipeline.ingest_manifest import IngestManifest
from src.readwise.library_index import ExportedRecord, LibraryIndex
from src.wiki_reset.reset import (
    CONFIRMATION_PHRASE,
    clear_ingest_manifest,
    clear_readwise_export_index,
    default_readwise_index_path,
    delete_non_instruction_wiki_files,
    is_instruction_wiki_file,
    readwise_library_document_count,
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


def test_clear_ingest_manifest_writes_empty(tmp_path: Path) -> None:
    """Ingest manifest is cleared to an empty records map."""
    path = tmp_path / "ingest_manifest.json"
    path.write_text('{"records": {"x": {}}}', encoding="utf-8")
    clear_ingest_manifest(path)
    text = path.read_text(encoding="utf-8")
    assert '"records": {}' in text


def test_readwise_library_document_count_missing_file(tmp_path: Path) -> None:
    """Missing index path yields zero documents."""
    assert readwise_library_document_count(tmp_path / "nope.json") == 0


def test_readwise_library_document_count_counts_entries(tmp_path: Path) -> None:
    """Document count matches JSON contents."""
    path = tmp_path / "lib.json"
    LibraryIndex(
        documents={
            "a": ExportedRecord(
                html_path="h",
                md_path="m",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            )
        },
        last_updated_after=None,
    ).save(path)
    assert readwise_library_document_count(path) == 1


def test_run_wiki_reset_default_preserves_readwise_index(tmp_path: Path) -> None:
    """Default reset clears wiki and manifest but not Readwise export index."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("instr", encoding="utf-8")
    (wiki / "tools").mkdir()
    (wiki / "tools" / "x.md").write_text("bye", encoding="utf-8")
    idx = tmp_path / "state" / "lib.json"
    idx.parent.mkdir()
    LibraryIndex(
        documents={
            "keep": ExportedRecord(
                html_path="raw/readwise/x.html",
                md_path="raw/readwise/x.md",
                source_url=None,
                updated_at="2024-01-01T00:00:00+00:00",
                content_sha256="abc",
            )
        },
        last_updated_after="2024-01-01T00:00:00+00:00",
    ).save(idx)
    before = idx.read_text(encoding="utf-8")
    manifest = tmp_path / "state" / "ingest_manifest.json"
    manifest.write_text('{"version": 1, "records": {"x": {}}}', encoding="utf-8")

    reviews = tmp_path / "state" / "reviews"
    reviews.mkdir(parents=True)
    (reviews / "some-source").mkdir()
    (reviews / "some-source" / "review.json").write_text("{}", encoding="utf-8")
    feedback_db = tmp_path / "state" / "review_feedback.sqlite"
    feedback_db.write_text("fake", encoding="utf-8")

    deleted, state_results = run_wiki_reset(
        wiki,
        idx,
        manifest_path=manifest,
        reviews_root=reviews,
        feedback_db_path=feedback_db,
    )
    assert "tools/x.md" in deleted
    assert state_results == {
        "readwise_library": False,
        "ingest_manifest": True,
        "review_state": True,
    }
    assert idx.read_text(encoding="utf-8") == before
    assert '"records": {}' in manifest.read_text(encoding="utf-8")
    assert not (reviews / "some-source").exists()
    assert not feedback_db.exists()
    log_text = (wiki / "log.md").read_text(encoding="utf-8")
    assert "readwise_library preserved" in log_text
    assert "ingest_manifest cleared" in log_text
    assert "review_state cleared" in log_text


def test_run_wiki_reset_reset_readwise_clears_index(tmp_path: Path) -> None:
    """Opt-in flag clears Readwise export index."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("x", encoding="utf-8")
    idx = tmp_path / "lib.json"
    LibraryIndex(
        documents={
            "a": ExportedRecord(
                html_path="h",
                md_path="m",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            )
        },
        last_updated_after=None,
    ).save(idx)
    manifest = tmp_path / "manifest.json"

    _deleted, state_results = run_wiki_reset(
        wiki,
        idx,
        clear_readwise_index=True,
        manifest_path=manifest,
        reviews_root=tmp_path / "no-reviews",
        feedback_db_path=tmp_path / "no.db",
    )
    assert state_results["readwise_library"] is True
    loaded = LibraryIndex.load(idx)
    assert loaded.documents == {}
    assert IngestManifest.load(manifest).records == {}


def test_run_wiki_reset_manifest_no_tmp_artifacts(tmp_path: Path) -> None:
    """Manifest clear uses atomic write (no stray .tmp files)."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    idx = tmp_path / "lib.json"
    LibraryIndex.empty().save(idx)
    manifest = tmp_path / "manifest.json"
    run_wiki_reset(
        wiki,
        idx,
        manifest_path=manifest,
        reviews_root=tmp_path / "no-reviews",
        feedback_db_path=tmp_path / "no.db",
    )
    assert list(manifest.parent.rglob("*.tmp")) == []


def test_run_wiki_reset_keep_reviews_preserves_artifacts(tmp_path: Path) -> None:
    """clear_reviews=False preserves review artifacts and feedback database."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    idx = tmp_path / "lib.json"
    LibraryIndex.empty().save(idx)
    manifest = tmp_path / "manifest.json"
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "src-id").mkdir()
    (reviews / "src-id" / "review.json").write_text("{}", encoding="utf-8")
    feedback_db = tmp_path / "fb.sqlite"
    feedback_db.write_text("db", encoding="utf-8")

    _deleted, state_results = run_wiki_reset(
        wiki,
        idx,
        manifest_path=manifest,
        clear_reviews=False,
        reviews_root=reviews,
        feedback_db_path=feedback_db,
    )
    assert state_results["review_state"] is False
    assert (reviews / "src-id" / "review.json").exists()
    assert feedback_db.exists()
    log_text = (wiki / "log.md").read_text(encoding="utf-8")
    assert "review_state preserved" in log_text


def test_clear_review_artifacts_empty_dir(tmp_path: Path) -> None:
    """Clearing a reviews dir with no subdirs returns 0."""
    from src.wiki_reset.reset import clear_review_artifacts

    reviews = tmp_path / "reviews"
    reviews.mkdir()
    assert clear_review_artifacts(reviews) == 0


def test_clear_review_artifacts_missing_dir(tmp_path: Path) -> None:
    """Clearing a missing reviews dir returns 0."""
    from src.wiki_reset.reset import clear_review_artifacts

    assert clear_review_artifacts(tmp_path / "nope") == 0


def test_clear_review_artifacts_removes_subdirs(tmp_path: Path) -> None:
    """All source subdirectories are removed."""
    from src.wiki_reset.reset import clear_review_artifacts

    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "a").mkdir()
    (reviews / "a" / "review.json").write_text("{}", encoding="utf-8")
    (reviews / "b").mkdir()
    (reviews / "b" / "review.json").write_text("{}", encoding="utf-8")

    removed = clear_review_artifacts(reviews)
    assert removed == 2
    assert reviews.is_dir()
    assert list(reviews.iterdir()) == []


def test_clear_feedback_db_removes_file(tmp_path: Path) -> None:
    """Feedback DB file is deleted when present."""
    from src.wiki_reset.reset import clear_feedback_db

    db = tmp_path / "fb.sqlite"
    db.write_text("x", encoding="utf-8")
    assert clear_feedback_db(db) is True
    assert not db.exists()


def test_clear_feedback_db_missing_is_noop(tmp_path: Path) -> None:
    """Missing feedback DB returns False."""
    from src.wiki_reset.reset import clear_feedback_db

    assert clear_feedback_db(tmp_path / "nope.sqlite") is False


def test_default_readwise_index_path_is_under_state() -> None:
    """Default index path points at state/readwise_library.json."""
    p = default_readwise_index_path()
    assert p.name == "readwise_library.json"
    assert p.parent.name == "state"


def test_default_reviews_root_is_under_state() -> None:
    """Default reviews root points at state/reviews."""
    from src.wiki_reset.reset import default_reviews_root

    p = default_reviews_root()
    assert p.name == "reviews"
    assert p.parent.name == "state"


def test_default_feedback_db_path_is_under_state() -> None:
    """Default feedback DB path points at state/review_feedback.sqlite."""
    from src.wiki_reset.reset import default_feedback_db_path as reset_fb_path

    p = reset_fb_path()
    assert p.name == "review_feedback.sqlite"
    assert p.parent.name == "state"


def test_write_wiki_shell_files_writes_expected_frontmatter(tmp_path: Path) -> None:
    """Shell writer produces expected frontmatter types."""
    wiki = tmp_path / "w"
    write_wiki_shell_files(
        wiki,
        today_iso="2099-01-01",
        state_results={
            "readwise_library": False,
            "ingest_manifest": True,
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
    LibraryIndex.empty().save(idx)
    manifest = tmp_path / "manifest.json"
    IngestManifest.empty().save(manifest)

    argv = [
        "wiki-reset",
        "--wiki-dir",
        str(wiki),
        "--index",
        str(idx),
        "--manifest",
        str(manifest),
        "--confirm",
        CONFIRMATION_PHRASE,
    ]
    with (
        mock.patch.object(cli.sys, "argv", argv),
        mock.patch.object(cli, "default_reviews_root", return_value=tmp_path / "no-reviews"),
        mock.patch.object(cli, "default_feedback_db_path", return_value=tmp_path / "no.db"),
    ):
        assert cli.main() == 0
    assert (wiki / "index.md").exists()
    assert LibraryIndex.load(idx).documents == {}
    assert IngestManifest.load(manifest).records == {}


def test_main_keep_reviews_flag(tmp_path: Path) -> None:
    """CLI --keep-reviews preserves review state."""
    from src.wiki_reset import cli

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    idx = tmp_path / "idx.json"
    LibraryIndex.empty().save(idx)
    manifest = tmp_path / "manifest.json"
    IngestManifest.empty().save(manifest)

    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "src-x").mkdir()
    (reviews / "src-x" / "review.json").write_text("{}", encoding="utf-8")
    feedback = tmp_path / "fb.sqlite"
    feedback.write_text("db", encoding="utf-8")

    argv = [
        "wiki-reset",
        "--wiki-dir",
        str(wiki),
        "--index",
        str(idx),
        "--manifest",
        str(manifest),
        "--keep-reviews",
        "--confirm",
        CONFIRMATION_PHRASE,
    ]
    with (
        mock.patch.object(cli.sys, "argv", argv),
        mock.patch.object(cli, "default_reviews_root", return_value=reviews),
        mock.patch.object(cli, "default_feedback_db_path", return_value=feedback),
    ):
        assert cli.main() == 0
    assert (reviews / "src-x" / "review.json").exists()
    assert feedback.exists()


def test_main_reset_readwise_index_flag(tmp_path: Path) -> None:
    """CLI --reset-readwise-index clears export index."""
    from src.wiki_reset import cli

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "AGENTS.md").write_text("k", encoding="utf-8")
    idx = tmp_path / "idx.json"
    LibraryIndex(
        documents={
            "z": ExportedRecord(
                html_path="h",
                md_path="m",
                source_url=None,
                updated_at=None,
                content_sha256=None,
            )
        },
        last_updated_after=None,
    ).save(idx)
    manifest = tmp_path / "manifest.json"

    argv = [
        "wiki-reset",
        "--wiki-dir",
        str(wiki),
        "--index",
        str(idx),
        "--manifest",
        str(manifest),
        "--reset-readwise-index",
        "--confirm",
        CONFIRMATION_PHRASE,
    ]
    with (
        mock.patch.object(cli.sys, "argv", argv),
        mock.patch.object(cli, "default_reviews_root", return_value=tmp_path / "no-reviews"),
        mock.patch.object(cli, "default_feedback_db_path", return_value=tmp_path / "no.db"),
    ):
        assert cli.main() == 0
    assert LibraryIndex.load(idx).documents == {}
