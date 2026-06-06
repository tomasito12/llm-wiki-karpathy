"""Detect and remove near-duplicate Readwise HTML exports in ``raw/readwise/``."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from src.readwise.library_index import LibraryIndex

SHINGLE_SIZE = 5
DEFAULT_THRESHOLD = 0.50


class _TextExtractor(HTMLParser):
    """Strip HTML tags and collect text."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def extract_text(html: str) -> str:
    """Return normalized plain text from HTML."""
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.get_text()
    return re.sub(r"\s+", " ", text).strip().lower()


def word_shingles(text: str, k: int = SHINGLE_SIZE) -> set[tuple[str, ...]]:
    """Return set of word k-grams."""
    words = text.split()
    if len(words) < k:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + k]) for i in range(len(words) - k + 1)}


def jaccard(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    """Jaccard similarity of two sets."""
    if not a and not b:
        return 1.0
    union = len(a | b)
    if union == 0:
        return 0.0
    return len(a & b) / union


@dataclass(frozen=True)
class RawDocument:
    """One loaded HTML export with extracted text and shingles."""

    stem: str
    text: str
    shingles: set[tuple[str, ...]]


@dataclass(frozen=True)
class DuplicatePair:
    """Two near-duplicate exports and their similarity score."""

    stem_a: str
    stem_b: str
    similarity: float
    text_len_a: int
    text_len_b: int


@dataclass(frozen=True)
class DedupeResult:
    """Summary after scanning ``raw/readwise`` for near-duplicates."""

    documents_scanned: int
    pairs_found: int
    deleted: tuple[str, ...]
    dry_run: bool
    interactive: bool


def load_documents(raw_dir: Path) -> list[RawDocument]:
    """Load all HTML files under *raw_dir*, extracting text and shingles."""
    docs: list[RawDocument] = []
    for html_path in sorted(raw_dir.glob("*.html")):
        html = html_path.read_text(encoding="utf-8", errors="replace")
        text = extract_text(html)
        docs.append(
            RawDocument(
                stem=html_path.stem,
                text=text,
                shingles=word_shingles(text),
            )
        )
    return docs


def find_duplicate_pairs(
    docs: list[RawDocument],
    threshold: float,
) -> list[DuplicatePair]:
    """Return pairs above *threshold*, sorted by descending similarity."""
    by_stem = {doc.stem: doc for doc in docs}
    stems = [doc.stem for doc in docs]
    pairs: list[DuplicatePair] = []
    for i, stem_a in enumerate(stems):
        doc_a = by_stem[stem_a]
        for stem_b in stems[i + 1 :]:
            doc_b = by_stem[stem_b]
            sim = jaccard(doc_a.shingles, doc_b.shingles)
            if sim >= threshold:
                pairs.append(
                    DuplicatePair(
                        stem_a=stem_a,
                        stem_b=stem_b,
                        similarity=sim,
                        text_len_a=len(doc_a.text),
                        text_len_b=len(doc_b.text),
                    )
                )
    pairs.sort(key=lambda pair: -pair.similarity)
    return pairs


def extract_doc_id(stem: str) -> str | None:
    """Extract the Readwise document ID from a filename stem."""
    match = re.search(r"-([0-9a-z]{26})$", stem)
    return match.group(1) if match else None


def choose_shorter_stem(
    pair: DuplicatePair,
    *,
    raw_dir: Path,
) -> str:
    """Return the stem to delete — the export with less plain text."""
    if pair.text_len_a < pair.text_len_b:
        return pair.stem_a
    if pair.text_len_b < pair.text_len_a:
        return pair.stem_b
    a_html = raw_dir / f"{pair.stem_a}.html"
    b_html = raw_dir / f"{pair.stem_b}.html"
    a_size = a_html.stat().st_size if a_html.is_file() else 0
    b_size = b_html.stat().st_size if b_html.is_file() else 0
    if a_size != b_size:
        return pair.stem_a if a_size < b_size else pair.stem_b
    return min(pair.stem_a, pair.stem_b)


def delete_export(
    stem: str,
    *,
    raw_dir: Path,
    index: LibraryIndex,
) -> None:
    """Delete HTML+MD files for *stem* and suppress the doc in *index*."""
    for suffix in (".html", ".md"):
        path = raw_dir / f"{stem}{suffix}"
        if path.is_file():
            path.unlink()

    doc_id = extract_doc_id(stem)
    if doc_id is None:
        return
    index.documents.pop(doc_id, None)
    if doc_id not in index.suppressed_ids:
        index.suppressed_ids.append(doc_id)


def run_dedupe(
    *,
    raw_dir: Path,
    index_path: Path,
    threshold: float = DEFAULT_THRESHOLD,
    dry_run: bool = False,
    interactive: bool = False,
    input_fn: Callable[[str], str] = input,
) -> DedupeResult:
    """Scan *raw_dir* for near-duplicates and optionally remove shorter exports."""
    docs = load_documents(raw_dir)
    pairs = find_duplicate_pairs(docs, threshold)
    if not pairs:
        return DedupeResult(
            documents_scanned=len(docs),
            pairs_found=0,
            deleted=(),
            dry_run=dry_run,
            interactive=interactive,
        )

    index = LibraryIndex.load(index_path)
    deleted: list[str] = []
    removed: set[str] = set()

    for pair in pairs:
        if pair.stem_a in removed or pair.stem_b in removed:
            continue
        if interactive:
            choice = _prompt_pair_action(pair, raw_dir=raw_dir, input_fn=input_fn)
            if choice == "quit":
                break
            if choice == "skip":
                continue
            stem_to_delete = choice
        else:
            stem_to_delete = choose_shorter_stem(pair, raw_dir=raw_dir)

        if dry_run:
            deleted.append(stem_to_delete)
            removed.add(stem_to_delete)
            continue

        delete_export(stem_to_delete, raw_dir=raw_dir, index=index)
        deleted.append(stem_to_delete)
        removed.add(stem_to_delete)

    if not dry_run and deleted:
        index.save(index_path)

    return DedupeResult(
        documents_scanned=len(docs),
        pairs_found=len(pairs),
        deleted=tuple(deleted),
        dry_run=dry_run,
        interactive=interactive,
    )


def _prompt_pair_action(
    pair: DuplicatePair,
    *,
    raw_dir: Path,
    input_fn: Callable[[str], str],
) -> str:
    """Prompt the operator to delete one side of *pair*, skip, or quit."""
    a_html = raw_dir / f"{pair.stem_a}.html"
    b_html = raw_dir / f"{pair.stem_b}.html"
    a_size = a_html.stat().st_size if a_html.is_file() else 0
    b_size = b_html.stat().st_size if b_html.is_file() else 0
    print(f"Pair: similarity = {pair.similarity:.2%}")
    print(f"  [1] {pair.stem_a} ({pair.text_len_a:,} chars, {a_size:,} bytes)")
    print(f"  [2] {pair.stem_b} ({pair.text_len_b:,} chars, {b_size:,} bytes)")
    while True:
        choice = input_fn("  Delete [1], [2], [s]kip, or [q]uit? ").strip().lower()
        if choice == "1":
            return pair.stem_a
        if choice == "2":
            return pair.stem_b
        if choice == "s":
            return "skip"
        if choice == "q":
            return "quit"
        print("  Invalid choice — enter 1, 2, s, or q")
