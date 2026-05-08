# LLM Wiki — Scoped Rules for `wiki_ops`

Use this file for wiki maintenance and knowledge operations only.

## Role

You are the wiki maintainer for an AI expert's personal knowledge base.
You own everything in `wiki/` and never modify `raw/`.

## Core separation

- **Process instructions** live in `wiki/AGENTS.md`, `wiki/ingest-templates.md`, `wiki/stage1-classifier.md`, and `wiki/stage2-artifact-router.md`.
- **Knowledge pages** (`wiki/sources/*.md`, `wiki/questions/*.md`, `wiki/glossary/*`, `wiki/tools/*`, `wiki/foundation-models/*`) should contain knowledge content, not prompt/process meta commentary.

## Directory structure (current)

```text
wiki/
  AGENTS.md
  ingest-templates.md
  stage1-classifier.md
  stage2-artifact-router.md
  index.md
  overview.md
  log.md
  sources/
  questions/
    question-catalog.md
    q-*.md
  glossary/
    index.md
    terms/
      *.md
  foundation-models/
    index.md
    <slug>.md
  tools/
    index.md
    <category>/
      index.md
      <tool-slug>.md
```

## Allowed content tags

Only use tags from this allowlist in page frontmatter:

- `ai-engineering`
- `tools`
- `models` (foundation-model pages only)

If a new tag is needed, add it here first.

## Allowed `type` values (frontmatter)

Use these `type` values as documented in each contract below. Do not invent new `type` strings without updating this list.

- `source`, `question`, `glossary`, `glossary-term`, `questions-catalog`, `tool`, `tools-category-index`, `tools-index`, `foundation-model`, `foundation-models-index`, `index`, `log`, `style`, and other meta types already in use under `wiki/`.

## Filename policy

- Keep filenames in stable kebab-case slugs (filesystem-safe and link-stable).
- Use human-readable language in `title` and section headings.
- Never use slug text as the only reader-facing heading when a readable phrasing is possible.

## Fixed contracts by page type

### 1) Glossary index — `wiki/glossary/index.md`

- `type: glossary`
- No `tags` in frontmatter
- No "Related pages"
- Content: plain term table (`Term | Page`), links to `glossary/terms/*`

### 2) Glossary term page — `wiki/glossary/terms/<slug>.md`

- `type: glossary-term`
- Frontmatter includes: `title`, `type`, `created`, `updated`, `tags`
- `tags` values must come from allowed tags
- No `sources` in frontmatter
- No "Related pages"
- Body headings are **fixed and mandatory** in this order:
  1. `## Definition`
  2. `## Usage Notes`
  3. `## Disagreements`
  4. `## Sources` (bullet links)

### 3) Questions catalog — `wiki/questions/question-catalog.md`

- `type: questions-catalog`
- No `tags` in frontmatter
- No "Related pages"
- Group by tag headings (for example `## ai-engineering`)
- Under each heading: bullet list of `[[q-...]]`
- A question can appear under multiple tag sections if applicable

### 4) Question page — `wiki/questions/q-<slug>.md`

- `type: question`
- Frontmatter includes: `title`, `type`, `created`, `updated`, `tags`
- No `aliases`
- No `sources` in frontmatter
- `tags` values must come from allowed tags
- No "Related pages"
- Body structure:
  1. `## Synthesized answer`
  2. optional additional explanatory subsections
  3. `## Sources` (bullet links)
- Do not use dated `Evidence — YYYY-MM-DD` sections on question pages.

### 5) Source page (non-tools overview) — `wiki/sources/<raw-basename>.md`

- `type: source`
- Frontmatter **must** include: `title`, `type`, `created`, `updated`, `tags`
- When known from the raw capture (for example Readwise `author`, outlet, or URL), also set:
  - **`author`** — string; primary byline or organization credited for the piece
  - **`publication`** — string; **venue or platform** (for example `Medium`, `Substack`, `arXiv`, `IEEE Spectrum`), not the article title or section name
- Avoid duplicating `author` / `publication` inside `title` when those properties are set
- `tags` values must come from allowed tags (typically `ai-engineering`; not the tools-overview path)
- Must not include classifier/process verdict blocks in the page body
- **Required section order**:
  1. One rough summary paragraph (no heading required)
  2. `## Questions addressed by the text`
  3. For each question: readable H3 question text; include wikilink to canonical `q-*` in the subsection body
  4. `## Why it matters`
  5. `## Implications for service-call automation` (only if there are real implications)
  6. `## Context and Limitations`
  7. `## Contradictions / Unverified Claims`
  8. `## Sources` (bullet links)
- Do not create separate "Driving question(s)" and "Author's answer" sections.

### 6) Source page (tools overview) — `wiki/sources/<raw-basename>.md`

Use when Stage 1 routes to **software-tool-focused** content (see `wiki/stage1-classifier.md`): **multi-tool listicles and single-product reviews alike**. **Do not** create or update question pages for this path. After classification, use **Stage 2** (`wiki/stage2-artifact-router.md`) to decide **per product** whether updates land in `wiki/tools/` or `wiki/foundation-models/`.

- `type: source`
- Frontmatter **must** include: `title`, `type`, `created`, `updated`, `tags` (with `tags` including `tools` per below)
- When known from the raw capture, also set **`author`** and **`publication`** (same meaning as contract **5)**); avoid repeating them in `title`
- Frontmatter `tags` **must** include `tools`.
- Must not include classifier/process verdict blocks in the page body
- **Forbidden**: `## Questions addressed by the text`
- **Coverage sections (after the summary):** include **only** sections that have **one or more** bullets, and list them in **this order**:
  1. `## Apps and platforms covered` — bullets **only** `[[tools/<category>/<slug>]]` where `<category>` is **not** `mcp-servers` (apps, starters, workflow tools, etc.).
  2. `## Foundation models covered` — bullets **only** `[[foundation-models/<slug>]]`.
  3. `## MCP servers covered` — bullets **only** `[[tools/mcp-servers/<slug>]]`.
- A single-product **tools-overview** article still uses whichever of the above sections apply (often only `## Apps and platforms covered` with one bullet). **Do not** use a flat `## Tools covered` that mixes apps, MCP servers, and foundation models in one list.
- **Required section order** (full page):
  1. One rough summary paragraph (no heading required)
  2. Coverage section(s) above (non-empty only, fixed relative order)
  3. `## Why it matters`
  4. `## Implications for service-call automation` (only if there are real implications)
  5. `## Context and Limitations`
  6. `## Contradictions / Unverified Claims`
  7. `## Sources` (bullet links)

### 7) Tool page — `wiki/tools/<category>/<slug>.md`

- `type: tool`
- Frontmatter includes: `title`, `type`, `created`, `updated`, `tags`
- `tags` must include `tools`
- No `aliases`, no YAML `sources`, no "Related pages"
- Body headings are **fixed and mandatory** in this order:
  1. `## What problem does this tool solve?`
  2. `## Properties` — bullet list (e.g. free/paid, learning curve, hosting, integrations); only what the sources support
  3. `## Author assessments` — bullet list; **each bullet ends with** a wikilink to the `wiki/sources/` page it came from
  4. `## Sources` — bullet wikilinks to every source page that has touched this tool (cumulative across ingests)
- **Cross-link rule**: every tools-overview source lists each **app/platform** tool under `## Apps and platforms covered` (and MCP under `## MCP servers covered` when applicable); every matching **tool** page lists each such source under `## Sources`. **Foundation models** link from `## Foundation models covered` only; see contract **10)** for model-page `## Sources`.

### 8) Tool category index — `wiki/tools/<category>/index.md`

- `type: tools-category-index`
- No `tags` in frontmatter
- No "Related pages"
- Content: a single table `| Tool | Page |` with rows wikilinking to every `wiki/tools/<category>/<slug>.md` (excluding `index.md`)

### 9) Tools master index — `wiki/tools/index.md`

- `type: tools-index`
- No `tags` in frontmatter
- No "Related pages"
- Content: a single table `| Category | Page |` with rows wikilinking to every `wiki/tools/<category>/index.md`
- **Scope:** lists **tool categories only**. **Not** used for foundation-model families—those live under `wiki/foundation-models/`.

### 10) Foundation model page — `wiki/foundation-models/<slug>.md`

- `type: foundation-model`
- Frontmatter includes: `title`, `type`, `created`, `updated`, `tags` (**must** include `models`); optional `vendor`, `homepage`, `open_weights` (`yes` | `no` | `partial` | `unknown`) when sourced.
- No `aliases`, no YAML `sources`, no "Related pages"
- Body headings are **fixed and mandatory** in this order:
  1. `## Summary` — short neutral overview; mark uncertainty when sources are thin.
  2. `## Technical snapshot` — bullets grounded in sources (architecture, modalities, context length, tool calling); note when `## Timeline` supersedes a field.
  3. `## Access and licensing` — API, weights, self-host, pricing **as stated**; `unknown` allowed.
  4. `## Evaluation claims` — benchmark or headline numbers with **provenance labels**: `Vendor-claimed`, `Third-party`, or `Anecdotal`.
  5. `## Limitations and risks` — only if sourced; otherwise one line: “Not covered in current sources.”
  6. `## Timeline` — **append-only**, newest first. Each dated block: `### YYYY-MM-DD`, 1–3 bullets, then a **Source:** line with `[[sources/<basename>]]`.
  7. `## Commentary` — optional opinion bullets; **each bullet ends with** a `[[sources/...]]` wikilink. Omit if the ingest only adds factual timeline material.
  8. `## Sources` — cumulative bullet wikilinks to every `wiki/sources/` page that cited this model.
- **Cross-link rule**: every tools-overview source that mentions the model lists it under `## Foundation models covered`; every foundation-model page lists that source under `## Sources`.

### 11) Foundation models index — `wiki/foundation-models/index.md`

- `type: foundation-models-index`
- No `tags` in frontmatter
- No "Related pages"
- Content: a single table `| Model | Page |` with rows wikilinking to every `wiki/foundation-models/<slug>.md` (excluding `index.md`)

## Stage 1 classifier rules

Use `wiki/stage1-classifier.md` to classify:

- **Industry radar digest** vs **non-radar**, then **named software tool(s) as primary subject** (tools-overview: **one or many** products) vs **thesis-first non-radar** (questions + source + glossary).
- Stage 1 answers **archetype only**. Per-item routing (**foundation model** vs **app** vs **MCP**) is **Stage 2** — see `wiki/stage2-artifact-router.md`.
- Classifier output belongs in working notes / logs, not in final source page content.

## Question abstraction rule (generic-first)

When creating or selecting questions, every rule below applies to **both** the filename slug (`q-<slug>.md`) **and** the frontmatter `title`. A question must remain reusable across future sources that ask the same thing.

### Q1 — Source-agnostic wording

Question titles and slugs must be phrased so any future source asking the same thing can attach evidence to the same page. Do not embed source-specific identifiers, brand names, author framing, or article-specific phrasing.

- Good: `q-which-elements-underpin-production-ai-systems` / "Which elements underpin production AI systems?"
- Bad: `q-yadavs-six-pillars-of-production-ai` / "Yadav's six pillars of production AI"

### Q2 — No quantifier lock-in

Titles and slugs must not embed numeric counts that come from one source (`six`, `five`, `10`, `three pillars`, `four layers`, etc.). The count belongs to the source's framing, not to the underlying question. Use the unquantified concept noun.

- Good: `q-which-elements-underpin-production-ai-systems` / "Which elements underpin production AI systems?"
- Bad: `q-what-six-concepts-underpin-production-ai-systems` / "What six concepts underpin production AI systems?"

### Q3 — No answer leakage

Question wording must not presuppose, name, or hint at the answer. Prefer neutral interrogatives (`what determines`, `which factors`, `how is X designed`) over leading constructions (`why is X mostly Y`, `why X is the main cause of Y`). The synthesized answer must be free to evolve as new evidence arrives without renaming the question page.

- Good: `q-what-determines-rag-effectiveness` / "What determines RAG effectiveness?"
- Bad: `q-why-is-rag-effectiveness-mostly-a-retrieval-problem` / "Why is RAG effectiveness mostly a retrieval problem?"

### Dedupe directive

If a new source adds aspects to an existing question, extend the existing `q-*.md` (or add an alias-style heading inside the body if needed) instead of creating a near-duplicate page. Run the `A0` dedupe gate against `wiki/questions/question-catalog.md` before creating any new `q-*` file.

## Glossary parity rule

`wiki/glossary/index.md` and `wiki/glossary/terms/` must stay in two-way parity. Adding a term to the index is only complete once its page exists, and vice versa.

- Every row in `wiki/glossary/index.md` must point to an existing `wiki/glossary/terms/<slug>.md`.
- Every page under `wiki/glossary/terms/` (excluding hidden/system files) must appear as a row in `wiki/glossary/index.md`.
- During an ingest, create the term page in the same step as the index row update. Never leave dangling links between ingests.

## Tools index parity rule

`wiki/tools/index.md`, each `wiki/tools/<category>/index.md`, and all `wiki/tools/<category>/<tool-slug>.md` pages must stay in two-way parity. Adding a tool is only complete once its category index row exists and the master index lists the category if new.

- Every row in `wiki/tools/<category>/index.md` must point to an existing `wiki/tools/<category>/<slug>.md`.
- Every tool page under `wiki/tools/<category>/` (excluding `index.md`) must appear as a row in that category's `index.md`.
- Every category folder under `wiki/tools/` (excluding the root `index.md`) must appear as a row in `wiki/tools/index.md`, and every such row must resolve to an existing `wiki/tools/<category>/index.md`.
- During a tools-overview ingest, create or update the tool page, category `index.md`, and master `wiki/tools/index.md` in the same step. Never leave dangling links between ingests.

**T0 (tools dedupe):** Before creating a new tool page, read `wiki/tools/index.md` (when present) and the relevant `wiki/tools/<category>/index.md`. If the tool already has a page, extend it; otherwise create a new `<slug>.md` and add index rows.

**T0b (new tool category gate — `wiki/tools` only):** Before creating a **new** `wiki/tools/<category>/` folder, read `wiki/tools/index.md` and reuse the closest existing category row when the product fits an established bucket. If you must add a category, add the folder, category `index.md`, master index row, and append a one-line note to `wiki/log.md`. **Foundation model families never use this gate** — use `wiki/foundation-models/index.md` for dedupe.

## Foundation models index parity rule

`wiki/foundation-models/index.md` and `wiki/foundation-models/*.md` (excluding `index.md`) must stay in **two-way parity** (same spirit as glossary parity).

- Every row in `wiki/foundation-models/index.md` must point to an existing `wiki/foundation-models/<slug>.md`.
- Every foundation-model page must appear as a row in `wiki/foundation-models/index.md`.
- During an ingest, update the model page, index row, and `## Sources` in the same step.

## Readwise raw hygiene (mandatory)

For each `raw/readwise/<basename>.md`:

- Read `.md` frontmatter only for metadata.
- Read paired `.html` in full for actual content extraction.
- If paired `.html` is missing, stop and request re-export.
- A completed ingest creates exactly one `wiki/sources/<basename>.md` with the **same basename** as the raw pair. **That file’s presence is the source of truth for “already ingested”** (see `hatch run ingest-queue`). The ingest manifest is audit-only and must never be used to skip dedupe.

## Ingest manifest contract (audit log)

After **every** completed ingest (success or structured failure), upsert **exactly one** manifest record keyed by `source_id` = the raw basename (stem shared by `.html` / `.md` / `wiki/sources/<basename>.md`).

Required fields on the record:

- `source_id`, `raw_md_path`, `raw_html_path`, `canonical_url` (from raw metadata when known), `title`, optional `author`, `publication`, `published_date`
- `content_sha256` — hash of the paired `.html` body (same concept as `state/readwise_library.json`)
- `stage1_route` — one of `radar`, `tools-overview`, `questions`, `unknown`
- `stage2_routes` — list of `{name, route, target_path?, notes?}` per Stage 2 decisions
- `wiki_artifacts` — every wiki path created or materially updated in this ingest (source page, tools, models, questions, glossary, indices, `wiki/log.md` if touched)
- `status` — `rendered` on success; `failed` with `errors` populated when the ingest aborts; `needs_review` when human follow-up is required

**Never** use the manifest to decide whether to ingest — use `hatch run ingest-queue` / wiki file presence instead.

## QA checklist (run after every ingest)

1. Source page matches required section order exactly (standard source vs tools-overview source, per contract).
2. No process/prompt text leaked into source/question/glossary content pages.
3. Question headings are readable natural language, not slug-only text.
4. Question page has no `aliases`, no YAML `sources`, and includes `## Sources` bullets.
5. Glossary term pages use exact 4 fixed headings in order.
6. Glossary index and question catalog contain no "Related pages" section.
7. Frontmatter tags use only allowed tags.
8. No unintended `wiki/<tag>/` hub folder/page created.
9. Question titles and slugs contain no source-specific quantifiers (no `six`, `ten`, `three pillars`, numerals tied to one source) — see Q2.
10. Question titles use neutral framing and do not presuppose or hint at the answer (no `why X is mostly Y` patterns) — see Q3.
11. Every term row in `wiki/glossary/index.md` resolves to an existing `wiki/glossary/terms/<slug>.md`.
12. Every page under `wiki/glossary/terms/` is listed as a row in `wiki/glossary/index.md`.
13. Tools-overview source pages have tag `tools`, contain no `## Questions addressed by the text`, use split coverage headings (contract **6)**), and do not mix `[[foundation-models/...]]` links into `## Apps and platforms covered` or vice versa.
14. Tool pages (`type: tool`) use exactly the 4 fixed headings in order (`What problem…`, `Properties`, `Author assessments`, `Sources`).
15. Each tool page is listed in its category `wiki/tools/<category>/index.md`, and vice versa (tools index parity).
16. Each category `index.md` is listed in `wiki/tools/index.md`, and vice versa (tools index parity).
17. Each `[[tools/...]]` wikilink under `## Apps and platforms covered` or `## MCP servers covered` resolves to an existing `wiki/tools/<category>/<slug>.md`.
18. Each `[[foundation-models/...]]` wikilink under `## Foundation models covered` resolves to an existing `wiki/foundation-models/<slug>.md`.
19. Foundation-model pages (`type: foundation-model`) use the 8 fixed headings in order (contract **10)**), include tag `models`, and use dated `## Timeline` blocks with explicit `Source:` lines.
20. `wiki/foundation-models/index.md` is in two-way parity with all non-index model pages.
21. Ingest manifest: one upsert for this `source_id` with `stage1_route`, `stage2_routes`, `wiki_artifacts`, and `status` consistent with the ingest outcome (see **Ingest manifest contract**).

## Session start checklist (`wiki_ops`)

1. Read this file.
2. Read `wiki/stage1-classifier.md` and `wiki/stage2-artifact-router.md` (Stage 2 before assigning artifacts on a tools-overview ingest).
3. Read `wiki/index.md` and latest `wiki/log.md` entries.
4. Read `wiki/questions/question-catalog.md`.
5. Read `wiki/glossary/index.md`.
6. Read `wiki/tools/index.md` when present (before any tools-overview ingest, tool dedupe, or **T0b** category decisions).
7. Read `wiki/foundation-models/index.md` when ingesting named **models** or model-news listicles.
8. During a tools-overview ingest, read the relevant `wiki/tools/<category>/index.md` before creating a new tool page (T0 dedupe gate).

## Notes

- Keep content concise, concrete, and source-grounded.
- Keep page titles readable and consistent with file purpose.
