"""Write Reader documents as paired HTML + Markdown files."""

from __future__ import annotations

import hashlib
import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from src.pipeline.atomic import atomic_write_text
from src.pipeline.slug import slugify
from src.readwise.library_index import ExportedRecord
from src.readwise.models import ReaderDocument

EXCERPT_MAX_CHARS = 4000


class _TextCollector(HTMLParser):
    """Collect visible text from HTML for excerpt generation."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data)

    def text(self) -> str:
        """Return normalized plaintext."""
        raw = " ".join(self._chunks)
        raw = html.unescape(raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw


def plaintext_excerpt_from_html(html_fragment: str, *, max_chars: int = EXCERPT_MAX_CHARS) -> str:
    """Strip tags and return a bounded plaintext excerpt."""
    collector = _TextCollector()
    try:
        collector.feed(html_fragment)
        collector.close()
    except Exception:
        return ""
    text = collector.text()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def _yaml_escape(value: str) -> str:
    """Double-quote YAML string with escapes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def json_list_yaml(items: list[str]) -> str:
    """Format string list as inline YAML flow sequence."""
    inner = ", ".join(_yaml_escape(item) for item in items)
    return f"[{inner}]"


def build_markdown_sidecar(doc: ReaderDocument, *, excerpt: str) -> str:
    """Build markdown file: YAML frontmatter + body (summary or excerpt)."""
    tag_keys = sorted(doc.tags.keys()) if doc.tags else []
    lines = [
        "---",
        f"readwise_id: {_yaml_escape(doc.id)}",
        f"title: {_yaml_escape(doc.title)}",
    ]
    if doc.author:
        lines.append(f"author: {_yaml_escape(doc.author)}")
    if doc.source_url:
        lines.append(f"source_url: {_yaml_escape(doc.source_url)}")
    if doc.category:
        lines.append(f"category: {_yaml_escape(doc.category)}")
    if doc.location:
        lines.append(f"location: {_yaml_escape(doc.location)}")
    if doc.published_date:
        lines.append(f"published_date: {_yaml_escape(doc.published_date)}")
    if doc.saved_at:
        lines.append(f"saved_at: {_yaml_escape(doc.saved_at)}")
    if doc.updated_at:
        lines.append(f"updated_at: {_yaml_escape(doc.updated_at)}")
    if tag_keys:
        lines.append(f"tags: {json_list_yaml(tag_keys)}")
    lines.extend(["---", ""])
    body = (doc.summary or "").strip() or excerpt
    lines.append(body)
    if not body.endswith("\n"):
        lines.append("")
    return "\n".join(lines)


@dataclass(frozen=True)
class ExportPaths:
    """Resolved paths for one export pair."""

    html_path: Path
    md_path: Path
    stem: str


def export_paths_for(doc: ReaderDocument, output_dir: Path) -> ExportPaths:
    """Compute sibling ``.html`` / ``.md`` paths under ``output_dir``."""
    base = f"{slugify(doc.title)}-{doc.id}"
    return ExportPaths(
        html_path=output_dir / f"{base}.html",
        md_path=output_dir / f"{base}.md",
        stem=base,
    )


def sha256_hex(text: str) -> str:
    """Return hex digest of UTF-8 bytes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_document_export(
    doc: ReaderDocument,
    output_dir: Path,
    *,
    relative_prefix: str = "raw/readwise",
) -> tuple[ExportedRecord, str, str]:
    """Write HTML and MD files; return record and relative paths for the index.

    ``relative_prefix`` is how paths are stored in the index (repo-relative).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = export_paths_for(doc, output_dir)

    html_body = doc.html_content
    if html_body:
        atomic_write_text(paths.html_path, html_body)
        digest = sha256_hex(html_body)
    else:
        stub = f"<!-- readwise export: no html_content for id={doc.id} title={doc.title!r} -->\n"
        atomic_write_text(paths.html_path, stub)
        digest = sha256_hex(stub)

    excerpt = plaintext_excerpt_from_html(html_body or "")
    md_text = build_markdown_sidecar(doc, excerpt=excerpt)
    atomic_write_text(paths.md_path, md_text)

    rel_html = f"{relative_prefix}/{paths.html_path.name}"
    rel_md = f"{relative_prefix}/{paths.md_path.name}"
    record = ExportedRecord(
        html_path=rel_html,
        md_path=rel_md,
        source_url=doc.source_url,
        updated_at=doc.updated_at,
        content_sha256=digest,
    )
    return record, rel_html, rel_md
