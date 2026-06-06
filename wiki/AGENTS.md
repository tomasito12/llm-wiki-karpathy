# LLM Wiki — Generated Knowledge Layer

Use this file for wiki generation, knowledge-layer structure, Obsidian conventions, and agent behavior around the **generated** vault.

This document describes the **current** architecture implemented by `wiki-render`. It is not a manual-ingest contract.

---

## Role

You maintain and operate an AI expert's Obsidian knowledge base under `wiki/`.

Your job is to:

- keep review artifacts accurate and complete
- run deterministic regeneration when reviews change
- preserve provenance, graph relationships, and evidence
- avoid treating generated markdown as the source of truth

You do **not** own `raw/` capture files except through the Readwise export workflow documented in `src/AGENTS.md`.

---

## Core principle

**Canonical source of truth:** `state/reviews/<source_id>/review.json`

Each review artifact contains human-reviewed classification output: approved entity proposals, tags, evidence fields, and source metadata. The Obsidian vault is a **generated projection** of those reviews.

```text
state/reviews/*
        ↓
  Knowledge Graph  (collect → merge → in-memory graph)
        ↓
    wiki-render    (hatch run wiki-render)
        ↓
   Obsidian Vault  (wiki/)
```

Agents must **never** treat generated pages as the primary source of truth. If vault content and a review artifact disagree, the review artifact wins. Fix the review, then regenerate.

---

## Generation command

```bash
hatch run wiki-render
```

Options:

- `--dry-run` — compute output without writing files
- `--no-prune` — skip deletion of stale generated files
- `--reviews-dir`, `--out-dir`, `--manifest-path`, `--graph-path` — override defaults

Every run performs **full regeneration**:

1. Load all `state/reviews/*/review.json` artifacts
2. Build an in-memory knowledge graph
3. Render all managed pages from scratch
4. Write advisory manifest and graph export
5. Optionally prune files that were generated previously but no longer appear in output

There are **no incremental updates** and **no dependency on previous renders**. The vault must always be reproducible from current reviews alone (plus the tag taxonomy files used for `taxonomy_version`).

---

## Folder structure

All generated top-level folders use **lowercase-hyphenated** names.

```text
wiki/
  sources/                  # one page per reviewed source (never merged)
  topics/                   # merged knowledge pages
  glossary/
  industry-trends/
  tools/
  foundation-models/
  how-to/
  implementation-studies/   # individual evidence pages (not merged)
  signals/                  # individual evidence pages (not merged)
  interview-insights/       # individual evidence pages (not merged)
  indexes/                  # generated indexes and diagnostics
```

### Path conventions

| Artifact class | Path pattern |
|----------------|--------------|
| Source | `sources/<source_id>.md` |
| Merged knowledge | `<category-folder>/<slug>.md` |
| Signal | `signals/<YYYY-MM>/<source_id>-<slug>.md` |
| Interview insight | `interview-insights/<YYYY-MM>/<source_id>-<slug>.md` |
| Implementation study | `implementation-studies/<YYYY-MM>/<source_id>-<slug>.md` |
| Index | `indexes/<name>.md` |

Monthly evidence paths use `<source_id>-<slug>` basenames. Very long names are compacted with a deterministic hash suffix (filesystem limit: 160 characters).

Tools and foundation models use **flat** folders (`tools/<slug>.md`, `foundation-models/<slug>.md`), not nested category trees.

---

## Artifact types

Three classes of generated content:

### 1. Sources (reviewed articles)

**Not merged.** One page per approved review artifact.

Sources summarize the reviewed article and link outward to everything derived from it. They accumulate tags from all derived entities on that source.

### 2. Synthesized knowledge objects (merged)

Merged across sources by stable slug and cautious title-alias grouping:

| Review key | Folder | Graph category |
|------------|--------|----------------|
| `topics` | `topics/` | `topic` |
| `glossary` | `glossary/` | `glossary` |
| `industry_trends` | `industry-trends/` | `trend` |
| `tools` | `tools/` | `tool` |
| `foundation_models` | `foundation-models/` | `model` |
| `how_to` | `how-to/` | `how_to` |

Each merged page:

- accumulates `EvidenceItem` records from every contributing source
- tracks `first_seen`, `last_seen`, `source_count`, `source_ids`
- exposes `entity_id` as `<category>:<slug>` (for example `topic:local-models`)
- carries `synthesis_state: stage1-placeholder` in Stage 1

Only **non-rejected** proposals from `review.json` are included (`proposal_status != rejected`).

### 3. Evidence objects (not merged)

Individual observations preserved as separate pages:

| Review key | Folder | Graph category |
|------------|--------|----------------|
| `roundup_signals` | `signals/` | `signal` |
| `interview_insights` | `interview-insights/` | `insight` |
| `implementation_studies` | `implementation-studies/` | `impl_study` |

These are case studies, signals, and interview takeaways — **evidence**, not synthesized knowledge. Future cross-source synthesis may consume them via retrieval or Stage 2; Stage 1 does not merge them.

Implementation studies preserve: title, company, industry, tags, implementation fields, evidence snippets, key lessons, open questions, related sources, and structured `EvidenceItem` records.

---

## Rendering model (Stage 1)

### Merged knowledge pages

Structure:

1. `# <title>`
2. `## Current understanding` — lead prose with Stage 1 placeholder comment
3. Category-specific value sections (definition, trend statement, tool properties, etc.)
4. `## Evidence / supporting sources` — grouped `EvidenceItem` bullets with `evidence_id`, stance, field, source link
5. `## Contradictions / uncertainty` — counter and uncertainty evidence
6. `## Related pages` — related entity references when present
7. `## Sources` — backlinks to contributing source pages

Lead prose is **not** true multi-source synthesis. It is the highest-ranked single-source contribution, marked explicitly as a placeholder.

### Source pages

Structure:

1. `# <title>` — accessible overview or summary
2. `## Key insights`
3. `## Derived knowledge pages` — wikilinks to all derived pages (knowledge + evidence)
4. `## Why it matters`
5. `## Limitations / open questions`
6. `## Contradictions / unverified claims`
7. `## Source metadata` — canonical URL, raw capture paths

### Evidence pages (signals, insights, implementation studies)

Structure varies by category but always includes:

- source attribution (`source_id`, `source_title`, `source_date`, `month`)
- category-specific body fields
- `## Evidence / supporting sources` when evidence items exist
- `## Source` backlink

---

## Frontmatter conventions

Generated pages use YAML frontmatter with **`category`**, not legacy `type`.

Common fields:

| Field | Used on |
|-------|---------|
| `title`, `slug` | all pages |
| `category` | all pages (`source`, `topic`, `glossary`, `industry-trend`, `tool`, `foundation-model`, `how-to`, `implementation-study`, `signal`, `insight`, `index`, `diagnostics`) |
| `tags` | all pages (from review taxonomy) |
| `entity_id` | merged knowledge pages |
| `aliases` | merged knowledge pages |
| `first_seen`, `last_seen`, `source_count`, `source_ids` | merged knowledge pages |
| `evidence_count`, `evidence_set_hash` | pages with evidence |
| `synthesis_state` | merged knowledge pages (`stage1-placeholder`) |
| `source_id`, `source_title`, `source_date`, `month` | evidence pages |
| `company`, `industry` | implementation studies |

### Source derived metadata

Source frontmatter records what each review produced:

**Slug lists** (merged knowledge):

- `derived_topics`, `derived_glossary`, `derived_trends`, `derived_tools`, `derived_models`, `derived_how_to`

**Path lists** (evidence objects):

- `derived_signals`
- `derived_interview_insights`
- `derived_implementation_studies`

Source `tags` are the union of tags from all derived entities on that source.

---

## Provenance

### EvidenceItems

The graph layer materializes atomic **`EvidenceItem`** records from review fields and snippets. Each item carries:

- `evidence_id` — stable short hash from source, entity slug, field, and text
- `text` — the claim or snippet
- `source_id`, `source_title`, `source_date`, `published_date`, `assessed_as_of`, `ingested_at`
- `category`, `entity_slug`, `field`
- `stance` — `supporting`, `counter`, `uncertainty`, or `neutral` (inferred from field name)
- `provenance`, `evidence_type`, `confidence`, `value_level`

Evidence items are rendered on page bodies and exported in `state/wiki_render_graph.json`.

### Graph relationships

- **Source → derived pages:** slug/path lists in source frontmatter; wikilinks in `## Derived knowledge pages`
- **Knowledge page → sources:** `source_ids` in frontmatter; `## Sources` section
- **Evidence page → source:** `source_id` in frontmatter; `## Source` section
- **Tag propagation:** entity tags roll up to source tags and appear in tag indexes

Agents must **preserve provenance**. Do not remove source references, evidence sections, or derived metadata from generated pages. Do not rewrite lead prose to imply multi-source synthesis in Stage 1.

---

## Stage 1 vs Stage 2

| | Stage 1 (current) | Stage 2 (future) |
|---|-------------------|------------------|
| Lead prose | Single-source placeholder | True multi-source synthesis from accumulated evidence |
| `synthesis_state` | `stage1-placeholder` | TBD (for example `synthesized`) |
| Merge | Structural merge + evidence accumulation | May add narrative synthesis, contradiction resolution |
| Input | `state/reviews/*` | Likely `state/wiki_render_graph.json` + reviews |

Stage 2 is **not implemented**. Agents must not pretend Stage 1 pages contain synthesized multi-source narrative.

---

## Tags and taxonomy

Tags come from human-reviewed proposals in `review.json`, validated against allowlists in:

- `config/review_tags_topics.yaml` (topics and how-tos)
- `config/review_tags_trends.yaml`
- `config/review_tags_glossary.yaml`
- `config/review_tags_tools.yaml`
- `config/review_tags_models.yaml`
- `config/review_tags_impl_study.yaml`

Product **types** (separate from retrieval tags): `config/review_tool_types.yaml`, `config/review_model_types.yaml`.

The renderer computes `taxonomy_version` as a hash of these files. It is recorded in the manifest and graph export.

---

## Managed vs editable content

### Generated — do not hand-edit

These paths are owned by `wiki-render`. Manual edits will be **overwritten** on the next run and may be **pruned** if they no longer appear in output:

```text
wiki/sources/
wiki/topics/
wiki/glossary/
wiki/industry-trends/
wiki/tools/
wiki/foundation-models/
wiki/how-to/
wiki/implementation-studies/
wiki/signals/
wiki/interview-insights/
wiki/indexes/
```

To change generated content, update the underlying `state/reviews/<source_id>/review.json` (via the ingest review dashboard) and rerun `hatch run wiki-render`.

### Safe for manual content

Paths **outside** the managed folders above are not regenerated or pruned. Use these for operator-owned notes:

- `wiki/AGENTS.md` (this file)
- `wiki/notes/` or other top-level folders **not** listed in managed folders — personal annotations, scratchpads, workflow notes
- Legacy instruction files preserved by `wiki-reset` (see below) — historical reference only

Do **not** store manual notes inside managed folders unless you accept that the next render will delete or overwrite them.

### Legacy files (historical, not generation contracts)

These files may exist under `wiki/` but are **not** produced by `wiki-render`:

- `wiki/legacy/manual-ingest/stage1-classifier.md`
- `wiki/legacy/manual-ingest/stage2-artifact-router.md`
- `wiki/legacy/manual-ingest/ingest-templates.md`
- `wiki/index.md`, `wiki/log.md` (legacy hub/log shells from `wiki-reset`)

They describe the **previous** manual-ingest workflow. Do not use them as contracts for generated pages. Prefer this file and `src/AGENTS.md` for current tooling.

The legacy **`wiki/questions/`** tree is **not part** of the generated architecture. Question-style knowledge is represented as `how-to/` pages and `topics/` in the new model.

---

## Diagnostics and maintenance

| Path | Role |
|------|------|
| `state/wiki_render_manifest.json` | Advisory record of last render: file paths, content hashes, counts, `taxonomy_version`. Used for write-if-unchanged and safe prune. **Not** used for incremental merge. |
| `state/wiki_render_graph.json` | Machine-readable full graph: sources, knowledge pages, signals, interview insights, implementation studies, evidence payloads, alias map. Stage 2 input. |
| `wiki/indexes/knowledge-graph.md` | Human-readable diagnostics: page counts, duplicate candidates, thinly-supported pages, tag frequency, contradiction highlights |
| `wiki/indexes/aliases.md` | Canonical entity aliases for ontology maintenance |
| `wiki/indexes/index.md` | Landing page linking to all generated indexes |

Generated indexes include:

- `*-by-tag.md` for sources, topics, trends, tools, models, glossary, how-to, implementation studies
- `signals-by-month.md`, `interview-insights-by-month.md`, `implementation-studies-by-month.md`

Use diagnostics pages and graph export when debugging merge behavior, duplicate candidates, or missing backlinks.

---

## Obsidian conventions

- **Wikilinks:** `[[relative/path/to/page|Label]]` — paths omit the `.md` extension
- **Embeds:** not used by the generator
- **Callouts / plugins:** generated indexes are plugin-free markdown
- **Filenames:** kebab-case slugs; human-readable `title` in frontmatter and headings
- **Links:** generator emits wikilinks for all cross-references between sources, knowledge pages, and evidence pages

---

## Agent guidance

### Do

- Treat `state/reviews/*` as source of truth
- Run `hatch run wiki-render` after review changes
- Preserve provenance, evidence sections, and source backlinks
- Use graph export and diagnostics indexes to investigate structure
- Fix data upstream in review artifacts, not by patching generated markdown
- Read `src/AGENTS.md` for ingest dashboard, Readwise sync, and code-side workflows

### Do not

- Hand-edit managed generated pages expecting changes to persist
- Remove or flatten source attribution
- Rewrite Stage 1 lead prose as if it were multi-source synthesis
- Force generated pages back into legacy contracts (`type: question`, nested `tools/<category>/`, `glossary/terms/`, manual index parity tables, etc.)
- Use `wiki/legacy/manual-ingest/` docs as render contracts
- Treat `wiki/index.md` or `wiki/log.md` as generated output

### Session checklist (`wiki_ops`)

1. Read this file.
2. Confirm which review artifacts changed (`state/reviews/`).
3. Run `hatch run wiki-render` (or `--dry-run` first for large changes).
4. Spot-check `wiki/indexes/knowledge-graph.md` and affected source pages for backlinks.
5. Commit review artifacts and regenerated vault together when appropriate.

---

## End-to-end workflow (current)

```text
raw/readwise/*          Readwise export (paired .html + .md)
        ↓
ingest review dashboard  hatch run dashboard — classify + human approve
        ↓
state/reviews/*         review.json per source
        ↓
wiki-render             hatch run wiki-render — full vault regeneration
        ↓
wiki/                   Obsidian vault (generated projection)
```

The ingest review dashboard **does not** write wiki pages directly. Wiki generation is a separate deterministic step.

---

## Related documentation

| Document | Scope |
|----------|-------|
| `src/AGENTS.md` | Python tooling, dashboard, Readwise, tests, `wiki-reset` |
| `docs/tagging-ontology.md` | Tag allowlists and taxonomy migration |
| Root `AGENTS.md` | Intent routing between `wiki_ops` and `code_ops` |
