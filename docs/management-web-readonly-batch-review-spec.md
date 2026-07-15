# Management Web V0 Read-Only Batch Review Technical Spec

Status: Ready for Cursor implementation
Created: 2026-07-15
Related product spec: `docs/internal-management-web-app-spec.md`

## 1. Context For Cursor

This repository builds and operates a personal LLM Wiki pipeline.

The current operator UI is a Streamlit dashboard. It works, but it is visually
heavy and cognitively tiring for high-volume article review. The long-term goal
is to replace it with a modern web management app.

The management app is private and single-user. It is not the future team-facing
wiki reader. The team-facing/public wiki surface will be designed separately.

This implementation slice must build the first read-only web review experience.
It should let the user quickly inspect many pre-analyzed Readwise articles and
see whether the extracted knowledge looks plausible.

Important product principle:

> The main review decision is article-level, but the UI must first show the
> extracted entities clearly enough that article-level approval is meaningful.

Do not force per-entity approval in this slice. Do make the extracted entities
easy to scan.

## 2. Non-Negotiable Scope

Build a local, read-only FastAPI + React/Vite application.

The slice name is:

```text
management-web-v0-readonly-batch-review
```

This slice must:

- start a FastAPI backend locally
- start a React/Vite frontend locally
- read `config/wiki_paths.toml` through the existing `WikiPaths` layer
- show a queue of available source review artifacts
- show one source in a batch-review workspace
- show article metadata, review state, source summary, tags, topics, glossary,
  and trends in a human-readable layout
- hide raw JSON by default behind a debug/details drawer
- allow moving through sources quickly
- make source text available on demand
- avoid all writes
- avoid all LLM calls
- avoid running pipeline commands such as render, lint, synthesis, or
  pre-analysis

This slice must not:

- save review decisions
- mutate `state/reviews`
- mutate `raw/readwise`
- mutate `wiki`
- call OpenAI or any other LLM provider
- add authentication yet
- add deployment packaging yet
- replace the Streamlit dashboard yet
- implement the public/team wiki reader

## 3. Recommended Location And Project Shape

Keep the first implementation in this repository.

Recommended directories:

```text
src/management_web/
  __init__.py
  api.py
  app.py
  models.py
  review_data.py

web/management/
  package.json
  vite.config.ts
  tsconfig.json
  index.html
  src/
    main.tsx
    App.tsx
    api.ts
    types.ts
    styles.css
    components/
```

Recommended Hatch scripts:

```toml
management-api = "src.management_web.app:main"
```

The frontend can be started with npm from `web/management` for now. Do not
over-engineer process management in this slice.

If the repository already has conventions for frontend packages by the time
Cursor implements this, follow those conventions instead.

## 4. Existing Code To Reuse

Use existing Python modules. Do not duplicate filesystem logic.

Required:

- `src.wiki_paths.config.load_wiki_paths`
- `src.wiki_paths.config.WikiPaths`
- `src.ingest_queue.queue.list_ingest_items`

Useful existing review facts:

- Raw Readwise exports live under `paths.raw_dir`.
- Review artifacts live under `paths.reviews_dir / <source_id> / "review.json"`.
- The path config is machine-specific and usually loaded from
  `config/wiki_paths.toml`.
- Without a path config, defaults remain repo-local for development tests.

Current local operating mode:

- knowledge store: `/Users/plischke/Desktop/Private Development/llm-wiki-data`
- private generated vault:
  `/Users/plischke/Desktop/Private Development/llm-wiki-vault-private`

Do not hard-code those absolute paths. They are here only so Cursor understands
the current architecture.

## 5. Review Artifact Shape

Review artifacts are JSON files created by the ingestion/pre-analysis pipeline.
The exact schema has evolved. Code must be tolerant of missing fields.

Common top-level fields:

```text
source
analysis_meta
llm_output
review
review_analytics
content_sha256
```

Useful fields:

- `source.title`
- `source.author`
- `source.publication`
- `source.published_date`
- `source.canonical_url`
- `source.category`
- `source.readwise_id`
- `source.raw_html`
- `source.raw_md`
- `source.content_sha256`
- `content_sha256`
- `review_analytics.review_finished_at`
- `llm_output.source_summary`
- `llm_output.topics`
- `llm_output.glossary`
- `llm_output.industry_trends`

Terminology mapping for the UI:

- `llm_output.topics` -> Topics
- `llm_output.glossary` -> Glossary
- `llm_output.industry_trends` -> Trends

Later slices will add:

- `llm_output.how_to`
- `llm_output.tools`
- `llm_output.foundation_models`
- `llm_output.implementation_studies`
- signals / interview insights if present in artifacts

This first slice should include extension points for those later categories but
does not need to render them fully.

## 6. Backend API Requirements

Create a FastAPI app. It must be read-only.

### 6.1 Configuration

The backend must load paths with:

```python
load_wiki_paths(config_path=optional_path)
```

Supported configuration options:

- CLI flag `--paths-config`
- environment variable `LLM_WIKI_PATHS_CONFIG`
- default discovery of `config/wiki_paths.toml`

The backend should expose the resolved paths in a safe status endpoint. It may
show paths because this is a private local management app. Do not expose API
keys or environment secrets.

### 6.2 Endpoints

Use a simple `/api` prefix.

Required endpoints:

```text
GET /api/health
GET /api/config
GET /api/review/queue
GET /api/review/source/{source_id}
GET /api/review/source/{source_id}/raw
```

#### `GET /api/health`

Returns:

```json
{
  "ok": true,
  "service": "management-web",
  "mode": "readonly"
}
```

#### `GET /api/config`

Returns selected resolved paths and mode:

```json
{
  "mode": "readonly",
  "paths": {
    "repo_root": "...",
    "knowledge_root": "...",
    "vault_root": "...",
    "raw_dir": "...",
    "reviews_dir": "...",
    "wiki_dir": "..."
  }
}
```

#### `GET /api/review/queue`

Query parameters:

```text
status=all|pending|in_progress|finished|incomplete
limit=number
offset=number
q=string
```

Default:

```text
status=all
limit=50
offset=0
```

Return shape:

```json
{
  "counts": {
    "total": 0,
    "pending": 0,
    "in_progress": 0,
    "finished": 0,
    "incomplete": 0
  },
  "items": [
    {
      "source_id": "...",
      "title": "...",
      "author": "...",
      "publication": "...",
      "published_date": "...",
      "category": "...",
      "status": "in_progress",
      "stale": false,
      "tags": ["..."],
      "entity_counts": {
        "topics": 0,
        "glossary": 0,
        "trends": 0
      },
      "review_json_path": "...",
      "raw_md_available": true
    }
  ],
  "limit": 50,
  "offset": 0
}
```

Status rules:

- `pending`: raw export exists but no `review.json`
- `incomplete`: raw HTML exists but matching raw Markdown sidecar is missing
- `in_progress`: `review.json` exists and no
  `review_analytics.review_finished_at`
- `finished`: `review.json` exists and
  `review_analytics.review_finished_at` is present

The existing `list_ingest_items()` only knows `pending`, `reviewed`, and
`incomplete`. Build the finer status classification in `src/management_web`
without changing `list_ingest_items()` unless there is a clear reason.

Stale rules:

- If both current raw Markdown hash and stored artifact hash can be determined,
  mark `stale=true` when they differ.
- If this is hard to implement safely in the first slice, return `stale=null`
  and document it. Do not guess.

#### `GET /api/review/source/{source_id}`

Returns a normalized source detail object:

```json
{
  "source_id": "...",
  "status": "in_progress",
  "stale": false,
  "metadata": {
    "title": "...",
    "author": "...",
    "publication": "...",
    "published_date": "...",
    "canonical_url": "...",
    "category": "...",
    "readwise_id": "..."
  },
  "paths": {
    "raw_html": "...",
    "raw_md": "...",
    "review_json": "..."
  },
  "summary": {
    "short": "...",
    "key_insights": ["..."]
  },
  "tags": ["..."],
  "entities": {
    "topics": [],
    "glossary": [],
    "trends": []
  },
  "debug": {
    "artifact": {}
  }
}
```

The `debug.artifact` field may contain the raw artifact, but the frontend must
hide it by default.

Entity normalization should be tolerant:

- include title/name fields when present
- include tags when present
- include short descriptions/evidence snippets when present
- include enough raw fields for the frontend to display something useful
- never fail the whole endpoint because one entity item has an unexpected shape

#### `GET /api/review/source/{source_id}/raw`

Returns raw Markdown content if available:

```json
{
  "source_id": "...",
  "available": true,
  "content": "...",
  "path": "..."
}
```

If unavailable:

```json
{
  "source_id": "...",
  "available": false,
  "content": "",
  "path": null
}
```

This endpoint is read-only. Do not fetch the internet. Only read local raw
Markdown.

## 7. Backend Implementation Notes

Create typed response models with Pydantic or dataclasses.

Every Python function must have:

- type hints
- a docstring
- tests

Recommended helper functions:

- `load_review_artifact(path: Path) -> dict[str, Any] | None`
- `classify_review_status(raw_item, artifact) -> ReviewStatus`
- `extract_source_metadata(source_id, raw_item, artifact) -> SourceMetadata`
- `normalize_source_summary(artifact) -> SourceSummary`
- `normalize_entities(artifact) -> EntityGroups`
- `collect_tags(artifact) -> list[str]`
- `read_raw_markdown(source_id, paths) -> RawSourceResponse`

Safety:

- Reject path traversal in `source_id`.
- Resolve source IDs only through queue/index lookup or strict filename-safe
  validation.
- Never accept arbitrary filesystem paths from the frontend.
- Never write files.
- Never create directories.

## 8. Frontend Requirements

Build a calm, dense, work-focused UI. This is an internal operator tool, not a
landing page.

Recommended stack:

- React
- Vite
- TypeScript
- plain CSS or a small component library if already introduced by Cursor

Do not spend this slice on visual spectacle. The goal is a usable review
surface.

### 8.1 Layout

Recommended page layout:

```text
Top bar:
  Management Web · Read-only · Path/config indicator

Left column:
  Queue filters
  Counts
  Source list

Main column:
  Source metadata
  Status/stale indicators
  Source summary
  Tags
  Entity groups
  Raw source drawer
  Debug JSON drawer

Right column or compact side panel:
  Current source position
  Entity counts
  Placeholder review actions disabled/read-only
```

The UI should make it easy to answer:

- What is this article?
- Is the analysis stale?
- What tags did the system assign?
- What concepts/topics/trends did it extract?
- Does this look plausible enough to approve later?
- Where can I inspect details if something looks wrong?

### 8.2 Queue UX

The queue should support:

- status filter
- text search
- selecting a source
- next/previous source buttons
- counts by status

Keyboard shortcuts are not required in this slice, but the component structure
should make them easy to add later.

### 8.3 Review Card UX

Show extraction groups in compact, scannable sections.

Minimum sections:

- Summary
- Tags
- Topics
- Glossary
- Trends

Each entity card should prefer:

- title/name
- tags/chips
- one short description
- evidence/source phrase if available

Avoid showing giant JSON blocks or huge raw text inline.

### 8.4 Read-Only Action Placeholders

Show disabled or clearly read-only placeholders for the later article-level
decisions:

- Approve article
- Needs attention
- Skip
- Request re-analysis

They must not perform writes in this slice.

Visible copy should make read-only mode obvious.

## 9. Testing Requirements

Backend tests are required.

Minimum tests:

- loading queue from temporary raw/reviews directories
- classifying pending/in_progress/finished/incomplete
- source detail endpoint with a minimal artifact
- source detail endpoint with missing optional fields
- raw source endpoint available
- raw source endpoint unavailable
- source ID traversal is rejected
- health/config endpoints work

Frontend tests are strongly preferred if the project setup makes them
reasonable. If not, document manual smoke steps.

Do not require a real OpenAI key. Do not make network calls.

## 10. Quality Checks

Run at least:

```bash
hatch run lint:check
hatch run lint:format
hatch run pytest tests/management_web
```

If frontend tooling is added, also run the relevant frontend checks, for
example:

```bash
cd web/management
npm install
npm run build
npm run lint
```

If `npm install` is needed, note it clearly in the implementation summary.

## 11. Manual Smoke Test

After implementation:

1. Start the backend.
2. Start the frontend.
3. Open the app locally.
4. Confirm the app displays the configured external knowledge/vault paths.
5. Confirm queue counts roughly match the current dashboard/ops status.
6. Select an in-progress source.
7. Confirm summary, tags, topics, glossary, and trends render as readable UI.
8. Confirm raw source can be opened on demand.
9. Confirm JSON is hidden by default.
10. Confirm no write files are modified after browsing the app.

## 12. Definition Of Done

The slice is done when:

- FastAPI backend starts locally.
- React/Vite frontend starts locally.
- The app reads the central path config.
- Queue counts render.
- A source can be selected.
- The review workspace shows article metadata, status, summary, tags, topics,
  glossary, and trends.
- Raw source text is available on demand.
- Debug JSON is hidden by default.
- There are no writes, no LLM calls, and no pipeline command execution.
- Backend tests cover the read-only data layer and endpoints.
- Existing Streamlit dashboard behavior is not changed.
- Documentation explains how to run the new local app.

## 13. Explicit Non-Goals

Do not implement these in this slice:

- saving review decisions
- editing tags
- disabling entities
- re-analyzing articles
- running pre-analysis
- running render/lint/synthesis
- authentication
- deployment to Hetzner
- public/team wiki reader
- agent API
- cron/background jobs
- full support for every entity type

## 14. Follow-Up Slices

Recommended next slices after user review:

1. Add how-tos, tools, models, signals, and interview insights to the entity
   overview.
2. Add keyboard navigation.
3. Add article-level write decisions: `approved`, `needs_attention`, `skipped`,
   `reanalyze_requested`.
4. Add simple tag corrections and entity disable actions.
5. Add safe re-analysis controls.
6. Add authentication and deployment packaging.
