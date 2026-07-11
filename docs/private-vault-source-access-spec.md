# Technical Specification: Private Vault Source Access

Last updated: 2026-07-11

This specification defines how the user and local agents should access full
source texts from the Obsidian wiki.

It is intended for an implementation agent that has no prior chat context.

## Problem

The generated wiki currently links to original source URLs and source metadata,
but the user wants direct access to the full source text from inside Obsidian.

The current experience is too indirect:

- open wiki page
- see source reference
- copy or follow an external URL
- search for raw text elsewhere

That breaks the main use case.

The generated wiki must let the user and an agent jump from a synthesis or topic
page to the full local source text in one click.

## User Priority

The primary user is the user themself, not the team.

Team access is a later feature and may use a filtered export. The private vault
can contain full source text if that is what makes the system useful.

## Goal

Create a private Obsidian-compatible source access layer.

Every generated wiki page that references sources should link to local full
source pages.

Example:

```md
## Sources

- [[sources/full/2026-07-article-id|Article Title]]
```

The linked source page should contain enough full text for human reading and
agent retrieval.

## Non-Goals

Do not implement in this task:

- public/team source publication rules
- copyright/legal automation
- web UI
- semantic search
- embedding index
- server deployment
- automatic source cleanup

This task is only about local/private source access.

## Target Structure

Preferred vault structure:

```text
vault/
  wiki/
    topics/
    glossary/
    how_to/
    tools/
    models/
    trends/
    indexes/
  sources/
    full/
      <source_id>.md
    index.md
  indexes/
```

If the current repo still uses `wiki/` as the output root, source pages can
temporarily live under:

```text
wiki/sources/full/<source_id>.md
wiki/sources/index.md
```

The final split can move them to `vault/sources/full/`.

## Source Page Content

Each source page should be Markdown and Obsidian-readable.

Recommended structure:

```md
---
category: source
source_id: <source_id>
title: <title>
url: <original_url>
author: <author>
published_date: <date>
ingested_at: <timestamp>
generated: true
source_text_available: true
---

# <Title>

Original URL: <url>

## Local Source Text

<full markdown body>
```

If the raw Markdown body is available, prefer it over HTML conversion.

If only HTML is available, convert to clean Markdown using an existing parser or
the current extraction pipeline. Do not hand-roll fragile HTML string parsing if
a project helper already exists.

## Source Page Slugs

Use stable source ids as filenames:

```text
sources/full/<source_id>.md
```

Do not use mutable article titles as filenames.

Reason:

- titles can change
- slugs may collide
- existing review artifacts already use source ids

## Links From Wiki Pages

Generated wiki pages should include source links that resolve inside Obsidian.

Preferred link:

```md
[[sources/full/<source_id>|<Source Title>]]
```

If source pages live under `wiki/sources/full` temporarily, links should match
the actual Obsidian-relative location.

The renderer should not emit broken links.

## Agent Access

Agent tools should be able to resolve source links without Obsidian.

Every source link should be derivable:

```text
source_id -> sources/full/<source_id>.md
```

Do not require the agent to parse an external URL first.

## Relationship to Raw Data

Raw files remain canonical originals:

```text
raw/readwise/<source_id>.html
raw/readwise/<source_id>.md
```

Generated source pages are readable access copies:

```text
sources/full/<source_id>.md
```

The source page can be regenerated from raw data. It is not the original.

However, source pages are important because they are the bridge between the
wiki, Obsidian, and agent retrieval.

## Privacy and Team Access

The private vault may contain full source text.

Do not assume the same content can be exposed to teammates or a public website.

Future team export should support modes:

```text
source_mode = "none"       # no source pages
source_mode = "summary"    # metadata + summary + URL
source_mode = "excerpt"    # limited excerpts
source_mode = "full"       # full text, explicit opt-in only
```

Default for private vault:

```text
source_mode = "full"
```

Default for future team/public export:

```text
source_mode = "summary"
```

## Renderer Requirements

The wiki renderer should eventually:

1. Read source metadata from review artifacts or graph exports.
2. Generate source pages for all referenced sources.
3. Render links from wiki pages to source pages.
4. Render a source index.
5. Keep source pages in a managed folder.
6. Prune deleted/obsolete managed source pages safely.

Do not hand-edit generated source pages.

## Source Index

Generate:

```text
sources/index.md
```

It should include:

- source title
- source id
- publication date when available
- ingested date when available
- original URL
- linked wiki topics/entities when available

Example:

```md
# Sources

| Source | Date | Used By |
|---|---:|---|
| [[sources/full/example-id|Example Article]] | 2026-07-11 | [[wiki/topics/local-pii-redaction]] |
```

## Cleanup and Pruning

Source pages are generated, but they should not be casually deleted.

Safe pruning rule:

- only prune pages inside the managed source folder
- only prune when the source id is no longer present in raw data or approved
  review artifacts
- dry-run first

## Implementation Order

### Step 1: Decide Output Paths

Add path configuration for:

- raw input directory
- source page output directory
- wiki output directory

Do not hardcode final paths into renderer logic.

### Step 2: Generate Source Pages

Implement source page generation from existing raw Markdown.

If raw Markdown is missing, fall back to cleaned HTML if existing helpers can do
it safely.

### Step 3: Link Wiki Pages to Source Pages

Update rendered wiki pages so source references use Obsidian wikilinks to local
source pages.

### Step 4: Source Index

Generate `sources/index.md`.

### Step 5: Tests

Add tests for:

- source page path stability
- source page frontmatter
- full text inclusion
- wiki page source links
- source index links
- no broken source links for graph sources

## Acceptance Criteria

The feature is done when:

- a user can open a generated wiki page in Obsidian and click to the full local
  source text
- an agent can map `source_id` to a local source Markdown file
- source pages are generated, not manually edited
- original raw files remain preserved separately
- team/public exposure is not accidentally enabled

