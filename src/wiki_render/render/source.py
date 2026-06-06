"""Render source pages."""

from __future__ import annotations

from pathlib import Path

from src.wiki_contract.frontmatter import DERIVED_FRONTMATTER_KEYS
from src.wiki_contract.headings import SOURCE_H2_HEADINGS
from src.wiki_render import layout
from src.wiki_render.frontmatter import markdown_document
from src.wiki_render.models import RenderedFile, SourceRecord
from src.wiki_render.render.common import bullet_list, heading, paragraph


def render_source_page(source: SourceRecord, *, wiki_dir: Path) -> RenderedFile:
    """Render one source page."""
    path = layout.page_path(wiki_dir, "source", source.source_id).relative
    derived_pages = sorted(
        {page_path for paths in source.derived_paths.values() for page_path in paths}
    )
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
        **{
            key: sorted(values)
            for key, values in sorted(source.derived_paths.items())
            if key in DERIVED_FRONTMATTER_KEYS and key != "derived_pages"
        },
    }
    if derived_pages:
        frontmatter["derived_pages"] = derived_pages
    body = heading(1, source.title)
    body += paragraph(source.accessible_overview or source.summary)
    body += heading(2, SOURCE_H2_HEADINGS[0])
    body += bullet_list(source.key_insights)
    body += _derived_section(source)
    body += heading(2, SOURCE_H2_HEADINGS[2])
    body += paragraph(source.why_it_matters or "Not covered in current review.")
    body += heading(2, SOURCE_H2_HEADINGS[3])
    body += paragraph(source.limitations_and_open_questions or "Not covered in current review.")
    body += heading(2, SOURCE_H2_HEADINGS[4])
    body += paragraph(source.contradictions_and_skepticism or "No contradictions captured.")
    body += heading(2, SOURCE_H2_HEADINGS[5])
    metadata = [
        f"Canonical URL: {source.canonical_url}" if source.canonical_url else "",
        f"Raw markdown: `{source.raw_md_rel_path}`" if source.raw_md_rel_path else "",
        f"Raw HTML: `{source.raw_html_rel_path}`" if source.raw_html_rel_path else "",
    ]
    body += bullet_list(metadata)
    return RenderedFile(relative_path=path, text=markdown_document(frontmatter, body))


def _derived_section(source: SourceRecord) -> str:
    """Render derived generated-page backlinks."""
    body = heading(2, SOURCE_H2_HEADINGS[1])
    links = sorted(
        {layout.wikilink(path) for paths in source.derived_paths.values() for path in paths}
    )
    if links:
        body += bullet_list(links)
    else:
        body += "No derived knowledge pages captured.\n\n"
    return body
