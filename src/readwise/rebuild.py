"""Rebuild ``readwise_library.json`` from existing ``raw/readwise`` export pairs."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from src.pipeline.source_publication import backfill_publications_in_raw_dir
from src.readwise.export import sha256_hex
from src.readwise.library_index import ExportedRecord, LibraryIndex
from src.readwise.sync import max_iso_timestamps
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPathsConfigError

_READWISE_ID_FALLBACK = re.compile(r"^[0-9a-z]{20,30}$")


def _parse_frontmatter_kv_block(md_text: str) -> dict[str, str] | None:
    """Return a flat key/value map from the first ``---`` YAML block, or ``None``."""
    lines = md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            inner = val[1:-1]
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
            val = inner
        data[key] = val
    return data


def read_readwise_fields_from_md(
    md_text: str, *, stem: str
) -> tuple[str | None, str | None, str | None]:
    """Extract ``readwise_id``, ``source_url``, ``updated_at`` from a sidecar ``.md``."""
    fm = _parse_frontmatter_kv_block(md_text)
    if fm is None:
        return None, None, None
    doc_id = fm.get("readwise_id")
    if not doc_id:
        candidate = stem.rsplit("-", maxsplit=1)[-1]
        if _READWISE_ID_FALLBACK.match(candidate):
            doc_id = candidate
    source_url = fm.get("source_url") or None
    updated_at = fm.get("updated_at") or None
    return doc_id, source_url, updated_at


@dataclass(frozen=True)
class RebuildResult:
    """Summary after scanning ``raw/readwise``."""

    scanned_html: int
    indexed: int
    skipped: list[tuple[str, str]]
    watermark: str | None


def rebuild_library_index_from_disk(
    raw_dir: Path,
    index_path: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    relative_prefix: str = "raw/readwise",
) -> RebuildResult:
    """Rebuild export index from paired ``.html`` + ``.md`` under ``raw_dir``.

    Does not call the Readwise API or modify raw files. Skips HTML without a
    sibling ``.md`` or without a resolvable ``readwise_id``.
    """
    if index_path.exists():
        existing = LibraryIndex.load(index_path)
        if existing.documents and not force:
            msg = (
                f"Refusing to overwrite non-empty index ({len(existing.documents)} documents). "
                "Pass --force to replace it."
            )
            raise ValueError(msg)

    skipped: list[tuple[str, str]] = []
    documents: dict[str, ExportedRecord] = {}
    updated_values: list[str | None] = []

    html_paths = sorted(raw_dir.glob("*.html"))
    for html_path in html_paths:
        md_path = html_path.with_suffix(".md")
        if not md_path.is_file():
            skipped.append((html_path.name, "missing_md_sidecar"))
            continue
        md_text = md_path.read_text(encoding="utf-8")
        doc_id, source_url, updated_at = read_readwise_fields_from_md(md_text, stem=html_path.stem)
        if not doc_id:
            skipped.append((html_path.name, "missing_readwise_id"))
            continue
        html_body = html_path.read_text(encoding="utf-8")
        digest = sha256_hex(html_body)
        rel_html = f"{relative_prefix}/{html_path.name}"
        rel_md = f"{relative_prefix}/{md_path.name}"
        documents[doc_id] = ExportedRecord(
            html_path=rel_html,
            md_path=rel_md,
            source_url=source_url,
            updated_at=updated_at,
            content_sha256=digest,
        )
        updated_values.append(updated_at)

    watermark = max_iso_timestamps(updated_values)
    index = LibraryIndex(documents=documents, last_updated_after=watermark)

    if not dry_run:
        index.save(index_path)

    return RebuildResult(
        scanned_html=len(html_paths),
        indexed=len(documents),
        skipped=skipped,
        watermark=watermark,
    )


def build_parser() -> argparse.ArgumentParser:
    """CLI for rebuilding the Readwise library index from disk."""
    parser = argparse.ArgumentParser(
        prog="readwise-rebuild-index",
        description="Rebuild state/readwise_library.json from raw/readwise export files.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory with paired .html and .md exports (default: configured raw_dir).",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="Library index JSON path (default: knowledge_root/state/readwise_library.json).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report only; do not write the index file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite a non-empty index (required when documents already exist).",
    )
    parser.add_argument(
        "--backfill-publication",
        action="store_true",
        help=(
            "Update each raw/readwise/*.md sidecar with a derived publication field "
            "(from site_name or source_url)."
        ),
    )
    parser.add_argument(
        "--backfill-only",
        action="store_true",
        help="With --backfill-publication, skip rebuilding readwise_library.json.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run rebuild CLI."""
    args = build_parser().parse_args(argv)
    try:
        paths = load_paths_for_cli(args)
    except WikiPathsConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    default_index = paths.knowledge_root / "state" / "readwise_library.json"
    raw_dir = resolve_cli_path(args.raw_dir, configured=paths.raw_dir).resolve()
    index_path = resolve_cli_path(args.index, configured=default_index).resolve()
    if not raw_dir.is_dir():
        print(f"raw-dir is not a directory: {raw_dir}", file=sys.stderr)
        return 1

    if args.backfill_publication:
        updated, skipped = backfill_publications_in_raw_dir(raw_dir)
        print(f"publication backfill: updated={updated} skipped={skipped}")
        if args.backfill_only:
            return 0

    try:
        result = rebuild_library_index_from_disk(
            raw_dir,
            index_path,
            dry_run=args.dry_run,
            force=args.force,
        )
    except ValueError as err:
        print(str(err), file=sys.stderr)
        return 2
    mode = "dry-run" if args.dry_run else "write"
    print(
        f"{mode}: scanned_html={result.scanned_html} indexed={result.indexed} "
        f"skipped={len(result.skipped)} watermark={result.watermark!r}"
    )
    for name, reason in result.skipped[:20]:
        print(f"  skip {name}: {reason}", file=sys.stderr)
    if len(result.skipped) > 20:
        print(f"  ... and {len(result.skipped) - 20} more skips", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
