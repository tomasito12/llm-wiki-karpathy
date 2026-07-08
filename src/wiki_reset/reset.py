"""Filesystem operations for wiki baseline reset."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from src.pipeline.atomic import atomic_write_text
from src.pipeline.ingest_manifest import IngestManifest
from src.readwise.library_index import LibraryIndex
from src.readwise.sync import _repo_root
from src.wiki_contract.layout import MANAGED_FOLDERS, NOTES, is_preserved_wiki_path
from src.wiki_reset.tag_taxonomy import reset_tag_taxonomy

CONFIRMATION_PHRASE = "RESET-WIKI"


def wiki_instruction_relpaths() -> frozenset[str]:
    """Return POSIX relpaths under ``wiki/`` preserved on reset (legacy alias)."""
    from src.wiki_contract.layout import PRESERVED_ROOT_FILES

    return PRESERVED_ROOT_FILES


def is_instruction_wiki_file(relative_posix: str) -> bool:
    """Return True if this relative path must survive reset."""
    return is_preserved_wiki_path(relative_posix)


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


def remove_wiki_render_manifest(manifest_path: Path) -> None:
    """Remove the wiki render advisory manifest if present."""
    if manifest_path.is_file():
        manifest_path.unlink()


def delete_non_instruction_wiki_files(wiki_root: Path) -> list[str]:
    """Delete generated wiki files while preserving operator-owned paths.

    Returns sorted POSIX paths relative to ``wiki_root``.
    """
    deleted: list[str] = []
    for path in sorted((p for p in wiki_root.rglob("*") if p.is_file()), reverse=True):
        rel = path.relative_to(wiki_root).as_posix()
        if is_preserved_wiki_path(rel):
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
    """Write minimal wiki-render-era shells after reset."""
    wiki_root.mkdir(parents=True, exist_ok=True)
    for folder in MANAGED_FOLDERS:
        (wiki_root / folder).mkdir(parents=True, exist_ok=True)
    notes_dir = wiki_root / NOTES
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_readme = notes_dir / "README.md"
    if not notes_readme.is_file():
        atomic_write_text(
            notes_readme,
            "\n".join(
                [
                    "---",
                    "title: Manual Notes",
                    "category: notes",
                    "---",
                    "",
                    "Operator-owned notes live here. Content in `wiki/notes/` survives "
                    "`wiki-render` and `wiki-reset`.",
                    "",
                ]
            ),
        )

    index_path = wiki_root / "index.md"
    if not index_path.is_file():
        atomic_write_text(
            index_path,
            "\n".join(
                [
                    "---",
                    "title: Wiki Hub",
                    "category: hub",
                    f"updated: {today_iso}",
                    "---",
                    "",
                    "- [[indexes/index|Generated indexes]]",
                    "- [[indexes/system-status|System status]]",
                    "- [[indexes/knowledge-graph|Knowledge graph diagnostics]]",
                    f"- [[{NOTES}/README|Manual notes]]",
                    "",
                ]
            ),
        )

    log_path = wiki_root / "log.md"
    state_summary = ", ".join(
        f"{name} {'cleared' if cleared else 'preserved'}"
        for name, cleared in sorted(state_results.items())
    )
    log_entry = (
        f"- {today_iso}: Reset wiki knowledge baseline. Preserved paths retained; "
        f"generated content cleared. State: {state_summary}. "
        "Run `hatch run wiki-render` when review artifacts are available."
    )
    if log_path.is_file():
        existing = log_path.read_text(encoding="utf-8")
        atomic_write_text(log_path, existing.rstrip() + "\n" + log_entry + "\n")
    else:
        atomic_write_text(
            log_path,
            "\n".join(
                [
                    "---",
                    "title: Wiki log",
                    "category: log",
                    f"updated: {today_iso}",
                    "---",
                    "",
                    log_entry,
                    "",
                ]
            ),
        )


def clear_review_artifacts(reviews_root: Path) -> int:
    """Delete all review artifact directories. Returns count of removed dirs."""
    if not reviews_root.is_dir():
        return 0
    removed = 0
    for child in sorted(reviews_root.iterdir()):
        if child.is_dir():
            shutil.rmtree(child)
            removed += 1
    return removed


def clear_feedback_db(db_path: Path) -> bool:
    """Delete the feedback SQLite database if it exists. Returns True if removed."""
    if db_path.is_file():
        db_path.unlink()
        return True
    return False


def default_reviews_root() -> Path:
    """Default ``state/reviews/`` directory under repo root."""
    return _repo_root() / "state" / "reviews"


def default_feedback_db_path() -> Path:
    """Default ``state/review_feedback.sqlite`` path."""
    return _repo_root() / "state" / "review_feedback.sqlite"


def default_wiki_render_manifest_path() -> Path:
    """Default ``state/wiki_render_manifest.json`` path."""
    return _repo_root() / "state" / "wiki_render_manifest.json"


def run_wiki_reset(
    wiki_root: Path,
    index_path: Path,
    *,
    clear_readwise_index: bool = False,
    manifest_path: Path | None = None,
    clear_manifest: bool = True,
    clear_wiki_render_manifest: bool = True,
    wiki_render_manifest_path: Path | None = None,
    clear_reviews: bool = True,
    reset_tag_taxonomy_config: bool = True,
    config_root: Path | None = None,
    reviews_root: Path | None = None,
    feedback_db_path: Path | None = None,
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
        "wiki_render_manifest": clear_wiki_render_manifest,
        "review_state": clear_reviews,
        "tag_taxonomy": reset_tag_taxonomy_config,
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
    if clear_wiki_render_manifest:
        remove_wiki_render_manifest(
            wiki_render_manifest_path
            or _wiki_render_manifest_path_for(manifest_path)
            or default_wiki_render_manifest_path()
        )
    if clear_reviews:
        clear_review_artifacts(reviews_root or default_reviews_root())
        clear_feedback_db(feedback_db_path or default_feedback_db_path())
    if reset_tag_taxonomy_config:
        reset_tag_taxonomy(config_root or _repo_root())
    return deleted, state_results


def default_wiki_root() -> Path:
    """Default ``wiki/`` directory under repo root."""
    return _repo_root() / "wiki"


def _wiki_render_manifest_path_for(manifest_path: Path | None) -> Path | None:
    """Return a sibling wiki-render manifest for custom state paths."""
    if manifest_path is None:
        return None
    return manifest_path.parent / "wiki_render_manifest.json"


def default_readwise_index_path() -> Path:
    """Default ``state/readwise_library.json`` path."""
    return _repo_root() / "state" / "readwise_library.json"


def default_ingest_manifest_path() -> Path:
    """Default ``state/ingest_manifest.json`` path."""
    return _repo_root() / "state" / "ingest_manifest.json"
