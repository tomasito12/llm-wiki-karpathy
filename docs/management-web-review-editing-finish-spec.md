# Management Web Review Editing And Finish Workflow Spec

Status: Ready for Cursor implementation
Created: 2026-07-15
Related specs:

- `docs/internal-management-web-app-spec.md`
- `docs/management-web-readonly-batch-review-spec.md`
- `docs/management-web-review-decision-write-spec.md`
- `docs/management-web-decision-filter-spec.md`
- `docs/management-web-design-review-2026-07-15.md`

## 1. Goal

Make the management web app useful as the primary article review workspace.

The current app can display review artifacts, filter the work queue, and write an
article-level management decision. That is useful, but it does not yet let the
user fix the common small problems that block approval:

- wrong or noisy tags
- unclear extracted entity titles
- weak or overly technical entity descriptions
- extracted entities that should be ignored for this source
- finished articles that should leave the review queue

This slice adds focused review editing and a finish workflow.

The main product rule remains:

> The user approves the article as a whole. Entity-level editing is a support
> action, not the primary workflow.

## 2. Non-Negotiable Scope

This slice must implement:

- backend endpoints for safe, targeted review artifact edits
- frontend editing controls for currently rendered entity cards
- a finish action that marks the review artifact as finished
- backup-before-overwrite behavior for every write
- queue/source reload behavior after edits and finish
- tests for backend write safety and frontend behavior

This slice must not:

- introduce a raw JSON editor as the main UX
- allow arbitrary JSON Patch paths from the frontend
- run pre-analysis
- call OpenAI or any other LLM provider
- run wiki render
- run synthesis
- run lint
- delete files
- edit raw Readwise exports
- edit generated wiki/vault pages
- implement multi-user auth
- redesign the whole app

## 3. Product Behavior

The normal review flow should become:

1. User opens `Ready for review` + `Not reviewed`.
2. User scans Easy Read, tags, and extracted entities.
3. If everything is good enough, user clicks `Finish review`.
4. If a small issue is visible, user edits the relevant field inline.
5. User can then finish the article.
6. The article leaves the default review queue.

The UI should optimize for speed and low cognitive load.

Editing should be available, but not visually dominate the page. The default
state should still be a calm reading/review surface.

## 4. Finish Semantics

The finish action is different from the existing management decision.

Current concepts:

- `management_review.status`
  - article-level operator decision such as `approved`, `needs_attention`,
    `skipped`, or `reanalyze_requested`
- `review_analytics.review_finished_at`
  - legacy/current lifecycle marker used by queues, render scope, and wiki
    workflows to decide whether a review artifact is finished

For this slice, `Finish review` must set:

```json
{
  "review_analytics": {
    "review_finished_at": "2026-07-15T12:34:56Z"
  }
}
```

It should also set or update:

```json
{
  "management_review": {
    "status": "approved",
    "reviewed_at": "2026-07-15T12:34:56Z",
    "reviewed_by": "plischke",
    "notes": ""
  }
}
```

Rationale:

- `review_finished_at` keeps the existing pipeline semantics intact.
- `management_review.status=approved` keeps the management app's decision
  model coherent.
- One button should complete the normal successful review path.

If an artifact already has `management_review.status=needs_attention`,
`skipped`, or `reanalyze_requested`, `Finish review` should not silently
overwrite it. Return `409 Conflict` unless the request explicitly includes
`force=true`.

The first frontend implementation should not expose `force=true`. The backend
supports it only so future UX can handle edge cases deliberately.

## 5. Editable Fields

Do not build arbitrary artifact editing.

Support targeted edits for normalized entity cards currently shown in the
management app:

- topics
- glossary
- trends

Artifact group mapping:

- frontend/backend group `topics` maps to `llm_output.topics`
- frontend/backend group `glossary` maps to `llm_output.glossary`
- frontend/backend group `trends` maps to `llm_output.industry_trends`

Each editable entity may expose:

- title
- description
- tags
- hidden/rejected flag

### 5.1 Field Mapping

Review artifacts are not perfectly uniform. The backend must map normalized
frontend edits back to the existing artifact shape.

For `topics`:

- title fields, in priority order:
  - `topic`
  - `topic_title`
  - `title`
- description fields, in priority order:
  - `knowledge_summary`
  - `operational_insight`
  - `description`
  - `summary`
- tag fields:
  - `proposed_tags`
  - `primary_tag`
  - `secondary_tag`

For `glossary`:

- title fields:
  - `term`
  - `glossary_term`
  - `title`
- description fields:
  - `definition`
  - `knowledge_summary`
  - `description`
  - `summary`
- tag fields:
  - `proposed_tags`
  - `primary_tag`
  - `secondary_tag`

For `trends`:

- title fields:
  - `trend`
  - `trend_title`
  - `title`
- description fields:
  - `knowledge_summary`
  - `operational_insight`
  - `description`
  - `summary`
- tag fields:
  - `proposed_tags`
  - `primary_tag`
  - `secondary_tag`

Implementation rule:

- Prefer updating the first existing field from the mapping.
- If none exists, write the first preferred field for that entity group.
- Preserve all unknown fields.
- Preserve evidence/snippet/source fields unless a later spec explicitly adds
  evidence editing.

### 5.2 Hidden/Rejected Entities

The first editing slice should support hiding an entity from review/render
without deleting it.

Recommended field:

```json
{
  "review_state": {
    "hidden": true,
    "hidden_at": "2026-07-15T12:34:56Z",
    "hidden_by": "plischke"
  }
}
```

Rules:

- Do not delete the original entity object.
- Hidden entities should visually collapse or disappear from the default entity
  list.
- The UI should offer a small toggle such as `Show hidden` for the selected
  source.
- Hidden entities should remain visible in debug JSON.

Renderer behavior is not part of this slice. If the existing wiki render does
not yet ignore hidden entities, document that as a follow-up. Do not change
wiki render in this slice unless tests prove it already reads this field.

## 6. Backend API

Existing backend package:

```text
src/management_web/
```

Add these endpoints.

### 6.1 Update Entity

```text
PATCH /api/review/source/{source_id}/entity
```

Request:

```json
{
  "group": "topics",
  "index": 0,
  "title": "Prompt caching",
  "description": "Prompt caching keeps repeated prompt parts reusable so repeated calls can become cheaper and faster.",
  "tags": ["prompt-caching", "ai-engineering"],
  "hidden": false
}
```

Field rules:

- `group`: required, one of `topics`, `glossary`, `trends`
- `index`: required, zero-based index into the artifact's underlying group list
- `title`: optional string
- `description`: optional string
- `tags`: optional list of non-empty strings
- `hidden`: optional boolean

At least one editable field must be present.

Response:

```json
{
  "source_id": "...",
  "group": "topics",
  "index": 0,
  "backup_path": "...",
  "source": { "...": "refreshed SourceDetailResponse" }
}
```

Use this exact response shape. The nested `source` must be the refreshed
`SourceDetailResponse` after the edit. This keeps the frontend from needing a
second detail request after a successful entity edit.

### 6.2 Finish Review

```text
PATCH /api/review/source/{source_id}/finish
```

Request:

```json
{
  "notes": "",
  "force": false
}
```

Response:

```json
{
  "source_id": "...",
  "management_review": {
    "status": "approved",
    "reviewed_at": "2026-07-15T12:34:56Z",
    "reviewed_by": "plischke",
    "notes": ""
  },
  "review_finished_at": "2026-07-15T12:34:56Z",
  "backup_path": "..."
}
```

HTTP behavior:

- `200`: write succeeded
- `400`: unsafe source ID, unsupported group, invalid index, or invalid field
  payload
- `404`: source raw HTML or review artifact does not exist
- `409`: finish conflicts with an existing non-approved management decision
- `422`: malformed request body handled by FastAPI/Pydantic
- `500`: unexpected filesystem write error

## 7. Filesystem Safety

Only write inside:

```text
paths.reviews_dir / <source_id> / "review.json"
```

Rules:

- validate `source_id` with the existing `validate_source_id`
- require matching raw HTML to exist
- entity editing requires an existing review artifact
- finish requires an existing review artifact
- never accept arbitrary file paths from the frontend
- never delete files
- never mutate raw exports or generated wiki files
- use `atomic_write_json`

## 8. Backup Rules

Reuse or generalize the current management review backup behavior.

Before every overwrite, write a timestamped backup in the same source review
directory.

Recommended pattern:

```text
review.before-management-edit.<timestamp>.json
```

Examples:

```text
state/reviews/<source_id>/review.before-management-edit.20260715T123456Z.json
state/reviews/<source_id>/review.before-management-edit.20260715T123456Z.1.json
```

Rules:

- backup must be written before the new artifact is written
- backup must contain the exact previous file content
- if backup fails, do not write the new artifact
- backups must not overwrite each other when multiple writes happen in the same
  second

Cursor should avoid duplicating backup logic. Prefer a small helper such as:

```python
def write_review_artifact_with_backup(
    review_json_path: Path,
    artifact: dict[str, Any],
    *,
    reason: str,
) -> Path:
    ...
```

The existing `write_management_decision()` should use the same helper after this
slice if that is a small, safe refactor. If the refactor becomes invasive, keep
the helper local to the new endpoints and note the duplication as follow-up.

## 9. Backend Implementation Notes

Likely files:

```text
src/management_web/models.py
src/management_web/review_data.py
src/management_web/api.py
tests/management_web/test_review_data.py
tests/management_web/test_api.py
```

Suggested model additions:

```python
EditableEntityGroup = Literal["topics", "glossary", "trends"]

class EntityEditRequest(BaseModel):
    group: EditableEntityGroup
    index: int
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    hidden: bool | None = None

class EntityEditResponse(BaseModel):
    source_id: str
    group: EditableEntityGroup
    index: int
    backup_path: str
    source: SourceDetailResponse

class FinishReviewRequest(BaseModel):
    notes: str = ""
    force: bool = False
```

Suggested functions:

```python
def update_review_entity(
    paths: WikiPaths,
    source_id: str,
    request: EntityEditRequest,
    *,
    reviewed_by: str = "plischke",
) -> SourceDetailResponse:
    ...

def finish_review(
    paths: WikiPaths,
    source_id: str,
    request: FinishReviewRequest,
    *,
    reviewed_by: str = "plischke",
) -> FinishReviewResponse:
    ...
```

Keep functions small:

- `_load_existing_review_artifact_for_write(...)`
- `_artifact_entity_list(artifact, group)`
- `_apply_entity_edit(entity, request, group, reviewed_by)`
- `_set_entity_tags(entity, tags)`
- `_set_entity_hidden_state(entity, hidden, reviewed_by)`
- `_ensure_finish_allowed(artifact, force)`
- `_write_review_artifact_with_backup(...)`

Every new public function must have:

- type hints
- docstring
- tests

## 10. Frontend Behavior

Likely files:

```text
web/management/src/App.tsx
web/management/src/api.ts
web/management/src/types.ts
web/management/src/App.test.tsx
web/management/src/styles.css
```

### 10.1 Entity Editing UI

Each entity card should have a small `Edit` button.

When editing:

- title becomes a text input
- description becomes a textarea
- tags become a compact comma-separated input or token-like input
- hidden/rejected is a checkbox or small action button
- actions: `Save`, `Cancel`

UX rules:

- only one entity should be in edit mode at a time
- `Cancel` restores the current server-loaded values
- `Save` disables the edit controls while the request is pending
- after successful save, reload the selected source detail
- do not reload the whole queue unless tags/status/counts shown in the queue
  might have changed; if in doubt, reload queue and source
- show a small success/error message near the edited entity

### 10.2 Hidden Entity UI

Default:

- hidden entities should not appear in the normal entity card list

Add a compact toggle:

```text
Show hidden
```

When enabled:

- hidden entities appear with muted styling
- hidden badge: `Hidden`
- user can unhide them

### 10.3 Finish Review UI

Add a primary article-level action near the existing decision buttons:

```text
Finish review
```

Behavior:

- writes `review_finished_at`
- writes/updates `management_review.status=approved`
- reloads queue with current filters
- if the finished article no longer matches the default queue, select the next
  matching article
- if none remains, show the existing empty state

The existing `Approve article` button may remain for now, but the UI should make
`Finish review` the normal happy-path action. If both buttons are visually
present, avoid making the choice confusing:

- `Finish review` = complete review lifecycle
- `Approve article` = decision only, does not finish lifecycle

If this feels too confusing in implementation, hide `Approve article` behind a
secondary overflow/action area and keep `Finish review` as the visible primary
action.

## 11. Validation Rules

Backend validation:

- reject empty title if `title` is provided
- reject empty description if `description` is provided
- normalize tags by trimming whitespace
- reject empty tags after trimming
- de-duplicate tags while preserving order
- reject entity indexes outside the current group list
- reject updates where no editable field is present
- reject `Finish review` when artifact has no analysis payload

Frontend validation:

- disable `Save` when all edited fields are unchanged
- show clear inline error for empty title or empty tags
- do not try to enforce full taxonomy correctness in this slice

Taxonomy linting and tag recommendation remain future work.

## 12. Interaction With Existing Pipeline

This slice writes the same review artifacts that the existing pipeline already
uses.

Important expected effects:

- `review_analytics.review_finished_at` changes source status to `finished`
- finished sources leave the default `Ready for review` queue
- future `wiki-render` should consume the edited artifact fields naturally if it
  already reads those fields
- hidden entities may require a later render update if render currently ignores
  `review_state.hidden`

Do not run render automatically from the management web app in this slice.

## 13. Testing Requirements

Backend tests:

- entity edit updates title without losing unknown fields
- entity edit updates description using the correct mapped field
- entity edit updates tags and normalizes whitespace/duplicates
- entity hide writes `review_state.hidden=true`
- entity unhide writes `review_state.hidden=false` or removes the hidden state
  consistently
- entity edit rejects invalid source ID
- entity edit rejects missing raw HTML
- entity edit rejects missing review artifact
- entity edit rejects invalid group
- entity edit rejects out-of-range index
- entity edit backs up previous artifact before overwrite
- finish writes `review_finished_at`
- finish writes `management_review.status=approved`
- finish rejects conflict with `needs_attention`, `skipped`, or
  `reanalyze_requested`
- finish with `force=true` can override such a conflict
- finish rejects missing review artifact
- finish backs up previous artifact before overwrite
- writes do not mutate raw or wiki files

Frontend tests:

- clicking `Edit` opens editable fields for one entity
- `Cancel` exits edit mode without API call
- `Save` calls the entity endpoint with group/index/fields
- successful save refreshes source display
- failed save shows an inline error
- hiding an entity removes it from the default entity list
- `Show hidden` reveals hidden entities
- `Finish review` calls the finish endpoint
- successful finish reloads queue and selects next matching source
- successful finish shows empty state when no source remains
- finish conflict shows an error and keeps the current source visible

Quality gates:

```bash
hatch run pytest tests/management_web -q
hatch run lint:check
cd web/management && npm run test -- --run
cd web/management && npm run build
cd web/management && npm run lint
```

If there are existing broader project test commands in the current branch,
running them is welcome but not required for this slice unless touched files
make it necessary.

## 14. Definition Of Done

The slice is complete when:

- the user can edit visible entity title/description/tags
- the user can hide and unhide visible entities
- the user can finish a review from the management web app
- finished reviews leave the default work queue
- all writes are backed up and atomic
- backend and frontend tests cover the main happy paths and safety failures
- no LLM calls are introduced
- no generated wiki pages are written
- no raw source files are mutated
- the implementation works with `config/wiki_paths.toml`

## 15. Follow-Ups Not In This Slice

Do not implement these now:

- support editing how-tos, tools, models, signals, and interview insights
- taxonomy recommendation or tag linting
- keyboard shortcuts for batch editing
- render support for hidden entities if not already present
- automatic `wiki-render` after finish
- operation log UI
- auth/deployment hardening
- polished toast notification system
- multi-user reviewer identity

These are important, but the current slice should stay focused on replacing the
core Streamlit review workflow.
