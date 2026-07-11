# Technical Specification: Full Source Text in Generated Source Pages

Last updated: 2026-07-11

This specification is the recommended next implementation slice after central
path configuration.

It is intended for Cursor or another implementation agent that has no prior chat
context.

## Background

The project already generates source pages such as:

```text
wiki/sources/<source_id>.md
```

These pages currently contain:

- source metadata
- source summary
- key insights
- derived knowledge page links
- limitations/open questions
- raw markdown/html path references

They do **not** contain the full raw source text. The user must leave the wiki
page and find the raw file manually if they want to read the full article.

That is too much friction.

The user's core requirement is:

> From a generated wiki page, the user and an agent must be able to open the
> original source text directly inside the Obsidian-readable knowledge surface.

## Important Product Constraint

Avoid unnecessary duplicate structures.

Do **not** create multiple parallel source-page systems unless there is a strong
reason.

The current source pages already exist and already receive backlinks from
knowledge pages. Therefore, the first implementation should extend the existing
source pages instead of creating a second full-source folder.

## Goal

Add full raw source text to the existing generated source pages.

Target page:

```text
wiki/sources/<source_id>.md
```

New section:

```md
## Full source text

<full source markdown>
```

This should make source access work immediately:

- existing wiki links to `[[sources/<source_id>|Source Title]]` keep working
- the user can click the source link in Obsidian and scroll to the raw text
- agents can open the same source Markdown file and inspect the full source
- no new parallel `sources/full/` structure is required for the first slice

## Non-Goals

Do not implement in this slice:

- a separate public/team-safe source export
- source summarization changes
- semantic search or embeddings
- web UI
- server deployment
- cleanup tooling
- migration to a separate vault repo
- copyright/legal automation
- automatic redaction

This slice is only about adding full local source text to generated source
pages in the private/local wiki surface.

## Relationship to Existing Specs

Use these documents as context:

- `docs/path-configuration-technical-spec.md`
- `docs/private-vault-source-access-spec.md`
- `docs/data-ownership-retention-spec.md`
- `docs/repo-vault-split-migration-spec.md`

But implement only this slice.

If path configuration has already been implemented, use the new central path
module instead of introducing another path system.

If path configuration has not yet been merged, keep the implementation
compatible with current defaults and avoid hard coupling to an unfinished API.

## Current Relevant Code

Existing renderer:

```text
src/wiki_render/render/source.py
```

Current function:

```python
def render_source_page(source: SourceRecord, *, wiki_dir: Path) -> RenderedFile:
    ...
```

Current source model:

```text
src/wiki_render/models.py
```

Current `SourceRecord` includes:

```python
raw_md_rel_path: str
raw_html_rel_path: str
```

Current source page metadata already prints:

```md
- Raw markdown: `raw/readwise/<source_id>.md`
- Raw HTML: `raw/readwise/<source_id>.html`
```

Those path references are useful but insufficient because they are not direct
local reading surfaces inside the generated wiki.

## Data Source

Prefer the raw Markdown export:

```text
raw/readwise/<source_id>.md
```

Reason:

- it is already text-like
- it is easier to include in Markdown
- it avoids fragile HTML conversion

Fallback:

- if raw Markdown is missing, use a clear placeholder and keep raw HTML metadata
- do not implement HTML-to-Markdown conversion in this slice unless a stable
  existing helper already exists and is easy to reuse

Do not hand-roll an HTML parser.

## Path Resolution

The renderer must be able to find raw Markdown files.

### Preferred after Path Config

If central path configuration exists, renderer inputs should include:

```text
raw_dir
wiki_dir
```

The source full text loader should resolve:

```text
raw_dir / f"{source.source_id}.md"
```

### Compatibility Fallback

If only `raw_md_rel_path` is available, resolve it relative to the repository
root or configured knowledge root.

The implementation must not assume the current working directory is the repo
root unless existing renderer conventions already do.

## Rendering Design

Add a new renderer helper, for example:

```python
def render_source_page(
    source: SourceRecord,
    *,
    wiki_dir: Path,
    raw_dir: Path | None = None,
    include_full_text: bool = True,
) -> RenderedFile:
    ...
```

Alternative:

```python
def render_source_page(source: SourceRecord, *, context: RenderContext) -> RenderedFile:
    ...
```

Use whichever style best fits the existing code after the path-config slice.

## Frontmatter Additions

Add source text state to source page frontmatter:

```yaml
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
```

If missing:

```yaml
source_text_available: false
source_text_mode: missing
source_text_source: none
```

Do not include the full source text in frontmatter.

## Body Structure

Append the full text near the end of the existing source page, after source
metadata.

Recommended order:

```md
# <title>

<summary/access overview>

## Key insights

...

## Derived knowledge pages

...

## Why it matters

...

## Limitations / open questions

...

## Contradictions / unverified claims

...

## Source metadata

...

## Full source text

<raw markdown body>
```

Reason:

- the reviewed summary remains at the top
- raw text is available without overwhelming the initial page view
- humans can scroll down when needed
- agents can parse the section reliably

## Raw Markdown Cleaning

The raw Markdown may contain frontmatter or Readwise metadata.

The first implementation may include it as-is if that is safest.

Preferred minimal cleanup:

- preserve article title and body
- avoid duplicating large YAML frontmatter if it is not useful
- do not remove quoted source text
- do not rewrite source prose

If cleanup is implemented, it must be conservative and tested.

Suggested helper:

```python
def load_raw_source_markdown(source: SourceRecord, *, raw_dir: Path) -> SourceText:
    ...
```

Suggested dataclass:

```python
@dataclass(frozen=True)
class SourceText:
    available: bool
    text: str
    source: str  # "raw_markdown" | "missing"
```

## Size and Performance

Including full source text will make generated wiki files larger.

This is acceptable for the private vault because direct source access is a core
requirement.

However:

- do not load raw files more than once per source
- do not scan unrelated raw files for every page
- render should remain deterministic
- avoid adding expensive transformations

If individual source pages become too large later, the future design can split
full text into `sources/full/`. Do not do that now.

## Obsidian Link Behavior

Existing links to source pages should continue to work:

```md
[[sources/<source_id>|Source Title]]
```

No large link migration should be needed in this slice.

If any source links are currently emitted without an alias, leave them unless a
small safe improvement is obvious.

## Agent Access

Agents should be able to:

1. open a generated wiki page
2. follow `[[sources/<source_id>]]`
3. read `## Full source text`

The section heading must be stable:

```md
## Full source text
```

Do not use multiple competing headings such as `Raw text`, `Original article`,
and `Full source`. One stable heading is better for retrieval.

## Privacy

This feature is for the private/local wiki surface.

Do not assume these full-text source pages are safe for team/public publishing.

Future team export must support filtering or summary-only source modes.

Add a comment or doc note if needed:

```text
Full source text is private-vault content by default.
Do not expose it in public/team exports without an explicit source_mode decision.
```

## Tests

Add or update tests in:

```text
tests/wiki_render/
```

Required tests:

1. Source page includes full source text when raw Markdown exists.
2. Source page frontmatter has `source_text_available: true`.
3. Source page frontmatter has `source_text_mode: full`.
4. Missing raw Markdown produces `source_text_available: false` and a clear body
   placeholder.
5. Existing derived-page links remain present.
6. Existing source metadata remains present.
7. `wiki-render --dry-run` can run without writing files.
8. No source page is generated outside the managed wiki source folder.

If path config has landed:

9. Renderer respects configured `raw_dir`.
10. Default repo-local raw path still works without config.

## Suggested Acceptance Tests

Create a test fixture:

```text
tmp_path/
  raw/readwise/source-a.md
  state/reviews/source-a/review.json
```

Run renderer against it and assert:

```md
## Full source text

This is the full article body.
```

Also assert the page path remains:

```text
sources/source-a.md
```

not:

```text
sources/full/source-a.md
```

for this first implementation slice.

## CLI Behavior

Do not add a new Hatch command.

`wiki-render` should generate source pages with full text by default for the
private/local wiki.

If a flag is needed for safety, prefer:

```bash
hatch run wiki-render --source-text-mode full
```

with default:

```text
full
```

But avoid adding flags unless necessary. The current product requirement is full
source access.

If path configuration exists, source text mode may later become config-driven:

```toml
[source_pages]
source_text_mode = "full"
```

Do not build multiple modes in this slice unless it stays small.

## Failure Behavior

Missing raw Markdown should not fail the entire render.

Instead:

- render the source page
- set `source_text_available: false`
- include a short placeholder:

```md
## Full source text

Full source text is not available locally. Raw metadata is listed above.
```

This keeps the wiki navigable and makes gaps visible.

## Documentation Updates

Update `wiki/AGENTS.md` source page contract:

- source pages include `## Full source text`
- full source text is generated from raw Markdown when available
- generated source pages remain managed and should not be hand-edited

Update `src/AGENTS.md` render section:

- `wiki-render` now reads raw Markdown to include full source text in generated
  source pages
- full source text is private/local by default

## Definition of Done

The implementation is complete when:

- generated `wiki/sources/<source_id>.md` pages include full raw source text
- existing source links from knowledge pages still work
- missing raw files are handled gracefully
- tests cover available and missing source text
- no new source-page duplicate hierarchy is introduced
- no new Hatch command is added
- targeted wiki-render tests pass
- lint/type checks pass

