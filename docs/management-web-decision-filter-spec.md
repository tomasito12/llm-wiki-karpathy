# Management Web Decision Filter Spec

Status: Ready for Cursor implementation
Created: 2026-07-15
Related specs:

- `docs/management-web-readonly-batch-review-spec.md`
- `docs/management-web-review-decision-write-spec.md`
- `docs/management-web-design-review-2026-07-15.md`

## 1. Goal

Turn the management web queue into a real work queue.

The previous slice added article-level decisions:

- `approved`
- `needs_attention`
- `skipped`
- `reanalyze_requested`

However, decided articles still remain in the default `Ready for review` list.
That makes the UI less useful for actual batch work because approved/skipped
items continue to appear in the user's main queue.

This slice adds decision filtering so the default work queue shows only sources
that still need a management decision.

## 2. Product Behavior

Default behavior:

- source status filter remains `Ready for review` (`in_progress`)
- decision filter defaults to `Not reviewed`
- decided articles are hidden from the default queue

The user should be able to switch the decision filter to inspect decided
articles.

Recommended decision filter options:

```text
Not reviewed
All decisions
Approved
Needs attention
Skipped
Re-analysis requested
```

Suggested internal filter values:

```text
not_reviewed
all
approved
needs_attention
skipped
reanalyze_requested
```

The existing source-analysis status filter remains separate:

```text
All
Needs analysis
Ready for review
Finished
Incomplete
```

Do not merge source-analysis status and management decision status into one
concept.

## 3. Main UX Requirement

After the user clicks `Approve article`, `Skip`, `Needs attention`, or
`Request re-analysis`, the source should disappear from the current default
queue when the active decision filter is `Not reviewed`.

Expected behavior after a successful write:

1. decision is saved
2. queue reloads
3. current source disappears if it no longer matches the active filters
4. UI selects the next available source in the filtered queue
5. if no source remains, show an empty state

This is the key behavior that makes the app usable for batch review.

## 4. Backend API Changes

Current endpoint:

```text
GET /api/review/queue
```

Add query parameter:

```text
decision=not_reviewed|all|approved|needs_attention|skipped|reanalyze_requested
```

Default:

```text
decision=not_reviewed
```

Important compatibility note:

- If no `decision` parameter is provided, default to `not_reviewed`.
- This changes the management web default behavior intentionally.
- Existing tests may need updates.

Filtering rules:

- `not_reviewed`: include only items where `management_status is null`
- `all`: include all items regardless of management status
- `approved`: include only `management_status == "approved"`
- `needs_attention`: include only `management_status == "needs_attention"`
- `skipped`: include only `management_status == "skipped"`
- `reanalyze_requested`: include only
  `management_status == "reanalyze_requested"`

Apply filters in this order:

1. source-analysis status filter
2. decision filter
3. text query
4. date/title sorting
5. pagination

## 5. Backend Response Changes

Add decision counts to queue response.

Recommended model:

```json
{
  "decision_counts": {
    "not_reviewed": 0,
    "approved": 0,
    "needs_attention": 0,
    "skipped": 0,
    "reanalyze_requested": 0
  }
}
```

Count semantics:

- Counts should be computed after source-analysis status filtering but before
  decision filtering and pagination.
- Example: if source status is `Ready for review`, decision counts describe the
  decision breakdown within ready-for-review sources.

This lets the UI show how many ready-for-review items are still undecided.

Keep existing `counts` unchanged:

- `counts` remains source-analysis status counts across the full raw/review
  queue.
- `decision_counts` is an additional management decision summary.

## 6. Backend Implementation Notes

Likely files:

```text
src/management_web/models.py
src/management_web/review_data.py
src/management_web/api.py
tests/management_web/
```

Suggested model additions:

```python
ManagementDecisionFilter = Literal[
    "not_reviewed",
    "all",
    "approved",
    "needs_attention",
    "skipped",
    "reanalyze_requested",
]

class DecisionCounts(BaseModel):
    not_reviewed: int = 0
    approved: int = 0
    needs_attention: int = 0
    skipped: int = 0
    reanalyze_requested: int = 0
```

Suggested function changes:

```python
def build_review_queue(
    paths: WikiPaths,
    *,
    status: QueueStatusFilter = "all",
    decision: ManagementDecisionFilter = "not_reviewed",
    limit: int = 50,
    offset: int = 0,
    query: str | None = None,
) -> QueueResponse:
    ...
```

Keep functions small:

- `_count_decisions(items)`
- `_filter_decision_items(items, decision=...)`

Every new function must have:

- type hints
- docstring
- tests

## 7. Frontend Behavior

Likely files:

```text
web/management/src/App.tsx
web/management/src/api.ts
web/management/src/types.ts
web/management/src/App.test.tsx
```

Add decision filter UI near the existing source status filter.

Suggested label:

```text
Decision
```

Options:

```text
Not reviewed
All decisions
Approved
Needs attention
Skipped
Re-analysis requested
```

Default:

```text
Not reviewed
```

Queue request should include both filters:

```text
/api/review/queue?status=in_progress&decision=not_reviewed&limit=250
```

After writing a decision:

- reload queue with the active status and decision filters
- if selected source is still present, keep it selected
- otherwise select the first item in the new queue
- if queue is empty, clear selected source and show empty state

Do not show a misleading success state attached to an old source that has just
left the queue.

Suggested UX:

- show a small transient success message at the top of the review panel or
  queue panel
- if source leaves the queue, show the next source immediately

## 8. Counts UI

Keep source-analysis counts visible but compact.

Add decision counts in a compact way.

Minimum acceptable UI:

- show `Not reviewed` decision count somewhere near the decision filter
- show selected decision filter count if available

Preferred UI if simple:

```text
Decision
[Not reviewed v]
180 not reviewed · 12 approved · 3 needs attention
```

Avoid making the counts visually heavy. This is supporting information, not the
main review content.

## 9. Tests

Backend tests required:

- default queue excludes items with `management_review`
- `decision=all` includes decided and undecided items
- `decision=approved` includes only approved items
- `decision=needs_attention` includes only needs-attention items
- `decision=skipped` includes only skipped items
- `decision=reanalyze_requested` includes only re-analysis-requested items
- decision counts are computed after source status filter
- source-analysis counts remain unchanged
- query search still works with decision filter
- sorting remains oldest first after filtering

Frontend tests required:

- default queue request includes `decision=not_reviewed`
- decision filter can switch to `All decisions`
- decided queue badges still render when visible
- after approving an item under `Not reviewed`, UI selects the next source
- after approving the last visible item, selected source clears and empty state
  renders
- write errors still display
- refresh errors still display separately from write errors

No tests may require:

- OpenAI API key
- real user data
- external network access

## 10. Quality Checks

Run:

```bash
hatch run lint:check
hatch run pytest tests/management_web -q
cd web/management
npm run test -- --run
npm run build
npm run lint
```

## 11. Manual Smoke Test

1. Start backend:

   ```bash
   hatch run management-api --paths-config config/wiki_paths.toml
   ```

2. Start frontend:

   ```bash
   hatch run management-ui
   ```

3. Confirm default filters:

   ```text
   Status: Ready for review
   Decision: Not reviewed
   ```

4. Select first source.
5. Click `Approve article`.
6. Confirm source disappears from the current queue.
7. Confirm next source is selected.
8. Switch decision filter to `Approved`.
9. Confirm approved source appears with an approved badge.
10. Switch back to `Not reviewed`.
11. Confirm approved source is hidden again.

## 12. Definition Of Done

The slice is complete when:

- backend accepts `decision` queue filter
- default decision filter is `not_reviewed`
- queue response includes `decision_counts`
- frontend exposes decision filter
- default UI hides decided articles
- successful decision writes advance to the next undecided source
- decided articles can still be inspected via filter
- backend and frontend tests cover the behavior
- no new LLM calls or pipeline operations are introduced

## 13. Explicit Non-Goals

Do not implement:

- notes editing
- per-entity decisions
- tag editing
- re-analysis execution
- keyboard shortcuts
- authentication
- deployment
- background jobs
