"""Filesystem operations for wiki baseline reset."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from src.pipeline.atomic import atomic_write_text
from src.pipeline.ingest_manifest import IngestManifest
from src.readwise.library_index import LibraryIndex
from src.readwise.sync import _repo_root

CONFIRMATION_PHRASE = "RESET-WIKI"

_WIKI_INSTRUCTION_RELPATHS: frozenset[str] = frozenset(
    {
        "AGENTS.md",
        "stage1-classifier.md",
        "ingest-templates.md",
        "stage2-artifact-router.md",
    }
)


def wiki_instruction_relpaths() -> frozenset[str]:
    """Return POSIX relpaths under ``wiki/`` preserved on reset."""
    return _WIKI_INSTRUCTION_RELPATHS


def is_instruction_wiki_file(relative_posix: str) -> bool:
    """Return True if this relative path is a preserved instruction file."""
    return relative_posix in _WIKI_INSTRUCTION_RELPATHS


def readwise_library_document_count(index_path: Path) -> int:
    """Return how many documents are recorded in the Readwise export index."""
    if not index_path.exists():
        return 0
    return len(LibraryIndex.load(index_path).documents)


def clear_readwise_export_index(index_path: Path) -> None:
    """Write an empty library index (clears exported-doc list and watermark)."""
    LibraryIndex.empty().save(index_path)


def clear_ingest_manifest(manifest_path: Path) -> None:
    """Write an empty ingest manifest file."""
    IngestManifest.empty().save(manifest_path)


def delete_non_instruction_wiki_files(wiki_root: Path) -> list[str]:
    """Delete all files under ``wiki_root`` except instruction files.

    Returns sorted POSIX paths relative to ``wiki_root``.
    """
    deleted: list[str] = []
    for path in sorted((p for p in wiki_root.rglob("*") if p.is_file()), reverse=True):
        rel = path.relative_to(wiki_root).as_posix()
        if is_instruction_wiki_file(rel):
            continue
        path.unlink()
        deleted.append(rel)
    return sorted(deleted)


def prune_empty_directories(wiki_root: Path) -> None:
    """Remove empty directories under ``wiki_root`` (deepest first)."""
    dirs = [p for p in wiki_root.rglob("*") if p.is_dir()]
    for path in sorted(dirs, key=lambda p: len(p.parts), reverse=True):
        if path.resolve() == wiki_root.resolve():
            continue
        try:
            path.rmdir()
        except OSError:
            pass


def write_wiki_shell_files(
    wiki_root: Path,
    *,
    today_iso: str,
    state_results: dict[str, bool],
) -> None:
    """Write minimal hub pages after reset."""
    wiki_root.mkdir(parents=True, exist_ok=True)
    (wiki_root / "sources").mkdir(parents=True, exist_ok=True)
    (wiki_root / "questions").mkdir(parents=True, exist_ok=True)
    (wiki_root / "glossary" / "terms").mkdir(parents=True, exist_ok=True)

    atomic_write_text(
        wiki_root / "index.md",
        "\n".join(
            [
                "---",
                "title: Wiki index",
                "type: index",
                f"created: {today_iso}",
                f"updated: {today_iso}",
                "---",
                "",
                "- [[glossary/index]]",
                "- [[questions/question-catalog]]",
                "",
            ]
        ),
    )
    state_summary = ", ".join(
        f"{name} {'cleared' if cleared else 'preserved'}"
        for name, cleared in sorted(state_results.items())
    )
    atomic_write_text(
        wiki_root / "log.md",
        "\n".join(
            [
                "---",
                "title: Wiki log",
                "type: log",
                f"created: {today_iso}",
                f"updated: {today_iso}",
                "---",
                "",
                f"- {today_iso}: Reset wiki knowledge baseline. Instruction files retained; "
                f"wiki content cleared. State: {state_summary}.",
                "",
            ]
        ),
    )
    atomic_write_text(
        wiki_root / "questions" / "question-catalog.md",
        "\n".join(
            [
                "---",
                "title: Questions catalog",
                "type: questions-catalog",
                f"created: {today_iso}",
                f"updated: {today_iso}",
                "---",
                "",
                "## ai-engineering",
                "",
            ]
        ),
    )
    atomic_write_text(
        wiki_root / "glossary" / "index.md",
        "\n".join(
            [
                "---",
                "title: Glossary",
                "type: glossary",
                f"created: {today_iso}",
                f"updated: {today_iso}",
                "---",
                "",
                "| Term | Page |",
                "|------|------|",
                "",
            ]
        ),
    )


def run_wiki_reset(
    wiki_root: Path,
    index_path: Path,
    *,
    clear_readwise_index: bool = False,
    manifest_path: Path | None = None,
    clear_manifest: bool = True,
) -> tuple[list[str], dict[str, bool]]:
    """Run full reset. Raises ``FileNotFoundError`` if ``wiki_root`` is missing."""
    if not wiki_root.is_dir():
        msg = f"Wiki root is not a directory: {wiki_root}"
        raise FileNotFoundError(msg)

    deleted = delete_non_instruction_wiki_files(wiki_root)
    prune_empty_directories(wiki_root)

    today_iso = date.today().isoformat()
    state_results = {
        "readwise_library": clear_readwise_index,
        "ingest_manifest": clear_manifest,
    }
    write_wiki_shell_files(
        wiki_root,
        today_iso=today_iso,
        state_results=state_results,
    )

    if clear_readwise_index:
        clear_readwise_export_index(index_path)
    if clear_manifest:
        clear_ingest_manifest(manifest_path or default_ingest_manifest_path())
    return deleted, state_results


def default_wiki_root() -> Path:
    """Default ``wiki/`` directory under repo root."""
    return _repo_root() / "wiki"


def default_readwise_index_path() -> Path:
    """Default ``state/readwise_library.json`` path."""
    return _repo_root() / "state" / "readwise_library.json"


def default_ingest_manifest_path() -> Path:
    """Default ``state/ingest_manifest.json`` path."""
    return _repo_root() / "state" / "ingest_manifest.json"
