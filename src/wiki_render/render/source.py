"""Render source pages."""

from __future__ import annotations

from pathlib import Path

from src.wiki_render import layout
from src.wiki_render.frontmatter import markdown_document
from src.wiki_render.models import RenderedFile, SourceRecord
from src.wiki_render.render.common import bullet_list, heading, paragraph


def render_source_page(source: SourceRecord, *, wiki_dir: Path) -> RenderedFile:
    """Render one source page."""
    path = layout.page_path(wiki_dir, "source", source.source_id).relative
    frontmatter = {
        "title": source.title,
        "slug": source.source_id,
        "category": "source",
        "tags": sorted(source.source_tags),
        "source_id": source.source_id,
        "author": source.author,
        "publication": source.publication,
        "published_date": source.published_date,
        "assessed_as_of": source.assessed_as_of,
        "ingested_at": source.ingested_at,
        "canonical_url": source.canonical_url,
        "content_sha256": source.content_sha256,
        **{key: sorted(values) for key, values in sorted(source.derived.items())},
        **{
            key: sorted(values)
            for key, values in sorted(source.derived_paths.items())
            if key in {"derived_signals", "derived_interview_insights"}
        },
    }
    body = heading(1, source.title)
    body += paragraph(source.accessible_overview or source.summary)
    body += heading(2, "Key insights")
    body += bullet_list(source.key_insights)
    body += _derived_section(source)
    body += heading(2, "Why it matters")
    body += paragraph(source.why_it_matters or "Not covered in current review.")
    body += heading(2, "Limitations / open questions")
    body += paragraph(source.limitations_and_open_questions or "Not covered in current review.")
    body += heading(2, "Contradictions / unverified claims")
    body += paragraph(source.contradictions_and_skepticism or "No contradictions captured.")
    body += heading(2, "Source metadata")
    metadata = [
        f"Canonical URL: {source.canonical_url}" if source.canonical_url else "",
        f"Raw markdown: `{source.raw_md_rel_path}`" if source.raw_md_rel_path else "",
        f"Raw HTML: `{source.raw_html_rel_path}`" if source.raw_html_rel_path else "",
    ]
    body += bullet_list(metadata)
    return RenderedFile(relative_path=path, text=markdown_document(frontmatter, body))


def _derived_section(source: SourceRecord) -> str:
    """Render derived generated-page backlinks."""
    body = heading(2, "Derived knowledge pages")
    links: list[str] = []
    for values in source.derived_paths.values():
        links.extend(layout.wikilink(path) for path in sorted(values))
    if links:
        body += bullet_list(sorted(links))
    else:
        body += "No derived knowledge pages captured.\n\n"
    return body
