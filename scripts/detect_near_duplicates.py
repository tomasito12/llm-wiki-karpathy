#!/usr/bin/env python3
"""Detect near-duplicate HTML documents in raw/readwise/ using word shingles.

Usage:
    python scripts/detect_near_duplicates.py [--threshold 0.50] [--delete]

Without --delete, prints duplicate pairs with similarity scores.
With --delete, interactively prompts which file to remove from each pair
and updates the library index to prevent re-import on next sync.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "raw" / "readwise"
INDEX_PATH = REPO_ROOT / "state" / "readwise_library.json"

SHINGLE_SIZE = 5


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


def jaccard(a: set, b: set) -> float:  # type: ignore[type-arg]
    """Jaccard similarity of two sets."""
    if not a and not b:
        return 1.0
    union = len(a | b)
    if union == 0:
        return 0.0
    return len(a & b) / union


def load_documents() -> list[tuple[str, str, set[tuple[str, ...]]]]:
    """Load all HTML files, extract text and shingles."""
    docs: list[tuple[str, str, set[tuple[str, ...]]]] = []
    for html_path in sorted(RAW_DIR.glob("*.html")):
        html = html_path.read_text(encoding="utf-8", errors="replace")
        text = extract_text(html)
        shingles = word_shingles(text)
        docs.append((html_path.stem, text, shingles))
    return docs


def find_duplicates(
    docs: list[tuple[str, str, set[tuple[str, ...]]]],
    threshold: float,
) -> list[tuple[str, str, float]]:
    """Return pairs (name_a, name_b, similarity) above threshold."""
    pairs: list[tuple[str, str, float]] = []
    n = len(docs)
    for i in range(n):
        for j in range(i + 1, n):
            sim = jaccard(docs[i][2], docs[j][2])
            if sim >= threshold:
                pairs.append((docs[i][0], docs[j][0], sim))
    pairs.sort(key=lambda x: -x[2])
    return pairs


def extract_doc_id(stem: str) -> str | None:
    """Extract the Readwise document ID (last 26-char hex segment) from a filename stem."""
    match = re.search(r"-([0-9a-z]{26})$", stem)
    return match.group(1) if match else None


def delete_with_index_update(stem: str) -> None:
    """Delete HTML+MD files and mark doc as suppressed in the library index."""
    html = RAW_DIR / f"{stem}.html"
    md = RAW_DIR / f"{stem}.md"

    for p in (html, md):
        if p.exists():
            p.unlink()
            print(f"  Deleted: {p.name}")
        else:
            print(f"  Already missing: {p.name}")

    doc_id = extract_doc_id(stem)
    if not doc_id:
        print("  Warning: could not extract doc ID from filename")
        return

    if not INDEX_PATH.exists():
        print("  Warning: library index not found — cannot mark as suppressed")
        return

    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    suppressed = idx.setdefault("suppressed_ids", [])
    if doc_id not in suppressed:
        suppressed.append(doc_id)
        suppressed.sort()
    idx["documents"].pop(doc_id, None)
    INDEX_PATH.write_text(json.dumps(idx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  Added {doc_id} to suppressed_ids in library index")


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect near-duplicate Readwise exports.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.50,
        help="Jaccard similarity threshold (default: 0.50)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Interactively delete duplicates and update library index",
    )
    args = parser.parse_args()

    print(f"Loading documents from {RAW_DIR} ...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents, computing pairwise similarity ...")

    pairs = find_duplicates(docs, args.threshold)

    if not pairs:
        print(f"\nNo near-duplicates found above threshold {args.threshold:.2f}")
        return 0

    print(f"\n{'=' * 80}")
    print(f"Found {len(pairs)} near-duplicate pair(s) (threshold >= {args.threshold:.2f}):")
    print(f"{'=' * 80}\n")

    for idx, (a, b, sim) in enumerate(pairs, 1):
        a_html = RAW_DIR / f"{a}.html"
        b_html = RAW_DIR / f"{b}.html"
        a_size = a_html.stat().st_size if a_html.exists() else 0
        b_size = b_html.stat().st_size if b_html.exists() else 0

        print(f"Pair {idx}: similarity = {sim:.2%}")
        print(f"  [1] {a}")
        print(f"      Size: {a_size:,} bytes")
        print(f"  [2] {b}")
        print(f"      Size: {b_size:,} bytes")

        if args.delete:
            while True:
                choice = input("\n  Delete [1], [2], [s]kip, or [q]uit? ").strip().lower()
                if choice == "1":
                    delete_with_index_update(a)
                    break
                elif choice == "2":
                    delete_with_index_update(b)
                    break
                elif choice == "s":
                    print("  Skipped.")
                    break
                elif choice == "q":
                    print("Quit.")
                    return 0
                else:
                    print("  Invalid choice — enter 1, 2, s, or q")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
