# Management Web Review Decision Write Spec

Status: Ready for Cursor implementation
Created: 2026-07-15
Related specs:

- `docs/internal-management-web-app-spec.md`
- `docs/management-web-readonly-batch-review-spec.md`
- `docs/management-web-design-review-2026-07-15.md`

## 1. Goal

Add the first write-capable workflow to the management web app.

The workflow is article-level review decisions:

- approve article
- mark article as needs attention
- skip article
- request re-analysis

The main review action is article-level. The user should not have to approve
every extracted entity individually when the article extraction is broadly
correct.

This slice turns the current read-only review UI into a usable operator tool,
while keeping the write surface small and auditable.

## 2. Non-Negotiable Scope

Implement article-level review decisions only.

This slice must:

- add a backend endpoint for writing one source review decision
- write only to the selected source's existing or new `review.json`
- store the decision in a clearly separated top-level block
- create a backup before overwriting an existing `review.json`
- expose the current decision in the read endpoints
- make the existing frontend article action buttons functional
- reload the source/queue state after a successful decision
- include tests for writes, backups, validation, and UI behavior

This slice must not:

- edit individual extracted entities
- edit tags
- run pre-analysis
- call OpenAI or any other LLM provider
- run wiki render
- run synthesis
- run lint
- delete files
- introduce multi-user auth
- introduce background jobs

## 3. Data Model

Store decisions in the existing review artifact under a new top-level key:

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

Allowed statuses:

```text
approved
needs_attention
skipped
reanalyze_requested
```

Field rules:

- `status`: required, one of the allowed values
- `reviewed_at`: required, UTC ISO timestamp written by backend
- `reviewed_by`: required, default `"plischke"` for now
- `notes`: optional string, default `""`

Do not overload existing `review_analytics.review_finished_at` in this slice.
That field belongs to the current Streamlit review lifecycle. This new
management UI needs its own explicit decision block first.

Future migration can later decide whether `management_review.status=approved`
should also set legacy review-finished markers. Do not do that now.

## 4. Backend API

Existing backend package:

```text
src/management_web/
```

Add a write endpoint:

```text
PATCH /api/review/source/{source_id}/decision
```

Request:

```json
{
  "status": "approved",
  "notes": ""
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
  "backup_path": "..."
}
```

For a newly created `review.json`, `backup_path` may be `null`.

HTTP behavior:

- `200`: decision written
- `400`: invalid source ID or invalid status
- `404`: source raw HTML does not exist
- `422`: malformed request body handled by FastAPI/Pydantic
- `500`: unexpected filesystem write error

## 5. Read API Changes

Extend existing models so the frontend can show current decision state.

Recommended response addition to `SourceDetailResponse`:

```json
{
  "management_review": {
    "status": "approved",
    "reviewed_at": "...",
    "reviewed_by": "plischke",
    "notes": ""
  }
}
```

When no decision exists:

```json
{
  "management_review": null
}
```

Recommended addition to queue items:

```json
{
  "management_status": "approved"
}
```

When no decision exists:

```json
{
  "management_status": null
}
```

The queue's existing source-analysis status stays unchanged:

- `pending` = needs analysis / no artifact
- `in_progress` = ready for review
- `finished` = legacy Streamlit finished
- `incomplete` = missing raw Markdown sidecar

Do not conflate this with `management_review.status`.

## 6. Filesystem Safety

Only write inside:

```text
paths.reviews_dir / <source_id> / "review.json"
```

Rules:

- validate `source_id` with existing `validate_source_id`
- require matching raw HTML to exist before writing
- never accept arbitrary file paths from the frontend
- create parent directory only for the selected source review directory
- never delete files
- never mutate raw exports or generated wiki files

## 7. Backup Rules

Before overwriting an existing `review.json`, write a timestamped backup in the
same source review directory.

Recommended pattern:

```text
review.before-management-review.<timestamp>.json
```

Example:

```text
state/reviews/<source_id>/review.before-management-review.20260715T123456Z.json
```

Rules:

- backup must be written before the new artifact is written
- backup must contain the exact previous file content
- no backup is required if no previous `review.json` exists
- use atomic write for the new `review.json` if an existing helper is available
- if backup fails, do not write the new decision

Search the repo for existing artifact save/backup helpers before implementing a
new one. The Streamlit dashboard already has related behavior.

## 8. Backend Implementation Notes

Suggested new or updated functions in `src/management_web/review_data.py`:

```python
def get_management_review(artifact: dict[str, Any] | None) -> ManagementReview | None:
    """Return normalized management review state from an artifact."""

def write_management_decision(
    paths: WikiPaths,
    source_id: str,
    decision: ManagementReviewRequest,
    *,
    reviewed_by: str = "plischke",
) -> ManagementDecisionResponse:
    """Write an article-level management review decision with backup."""
```

All functions must have:

- type hints
- docstrings
- tests

Use Pydantic models in `src/management_web/models.py` for request/response
schemas.

Timestamp format:

- UTC
- second precision is enough
- suffix with `Z`

## 9. Frontend Behavior

Replace the current placeholder behavior for article actions.

Buttons:

- Approve article
- Needs attention
- Skip
- Request re-analysis

UI behavior:

- Buttons are enabled when a source is selected.
- Clicking a button writes the corresponding decision.
- Show a small confirmation/success state after writing.
- Show current decision state near the article header.
- Disable buttons while the request is pending.
- On success, reload source detail and queue data.
- On error, show a visible error message.

Suggested mapping:

```text
Approve article      -> approved
Needs attention      -> needs_attention
Skip                 -> skipped
Request re-analysis  -> reanalyze_requested
```

Notes:

- Do not add a notes field in the first implementation unless it is very cheap.
- If notes are added, keep them optional and simple.
- Do not prompt with a modal unless the implementation already has a modal
  pattern. A direct click is acceptable for this slice because backups exist and
  the action can be overwritten by a later decision.

Visual behavior:

- Current decision should be visible but not visually loud.
- `approved` can be positive/green but subtle.
- `needs_attention` and `reanalyze_requested` can be amber.
- `skipped` can be gray.

## 10. Interaction With Existing Status Filters

Do not change the current source-analysis status filters in this slice.

The default queue should remain `Ready for review` (`in_progress`).

Optional if cheap:

- show management decision as a small badge in queue rows

Do not add new queue filters for management decision yet unless it is trivial.

## 11. Tests

Backend tests are required.

Minimum backend tests:

- valid decision writes `management_review`
- existing `review.json` is backed up before overwrite
- missing artifact creates a new `review.json` with `management_review`
- invalid status returns validation error
- unsafe `source_id` is rejected
- missing raw source returns 404
- read source detail returns existing `management_review`
- queue item includes `management_status`
- write does not mutate raw files or wiki files

Frontend tests are required.

Minimum frontend tests:

- current decision state renders when present
- clicking Approve article calls the decision endpoint
- buttons are disabled while request is pending
- source/queue reload after success
- error response is displayed

No tests may require:

- OpenAI API key
- network access outside local test process
- real user data

## 12. Quality Checks

Run:

```bash
hatch run lint:check
hatch run pytest tests/management_web -q
cd web/management
npm run test -- --run
npm run build
npm run lint
```

If frontend package files change, ensure lockfile updates are intentional.

## 13. Manual Smoke Test

1. Start backend:

   ```bash
   hatch run management-api --paths-config config/wiki_paths.toml
   ```

2. Start frontend:

   ```bash
   hatch run management-ui
   ```

3. Select a Ready for review article.
4. Click `Approve article`.
5. Confirm decision badge appears.
6. Confirm page reloads without losing the selected article.
7. Inspect the relevant `review.json`.
8. Confirm `management_review.status` is `approved`.
9. Confirm a backup file exists if a `review.json` already existed.
10. Click `Needs attention`.
11. Confirm the decision updates and another backup is written.

## 14. Definition Of Done

The slice is complete when:

- article-level decision endpoint exists
- endpoint validates source ID and status
- endpoint writes only to the selected review artifact
- backups are created before overwrites
- source detail exposes current management decision
- queue exposes management decision state
- frontend buttons write decisions
- frontend shows current decision
- tests cover backend and frontend behavior
- no LLM calls are introduced
- no render/synthesis/lint operation is triggered

## 15. Explicit Non-Goals

Do not implement:

- per-entity approve/reject
- tag editing
- source re-analysis execution
- notes workflow beyond optional simple notes
- keyboard shortcuts
- management decision filters
- authentication
- deployment
- background job tracking
