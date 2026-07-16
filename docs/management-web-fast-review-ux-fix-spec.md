# Management Web Fast Review UX Fix Spec

Date: 2026-07-16
Status: Draft for implementation
Related feedback: `docs/management-web-feedback-round-2026-07-16.md`

## 1. Purpose

The management web app is now functionally capable of reviewing Readwise
articles, editing extracted entities, hiding entities, and finishing reviews.
The next step is not a new pipeline feature. The next step is to make the review
workspace easier to understand and faster to use.

This slice should reduce confusion and visual instability in the current
write-enabled review UI.

Primary user goal:

> Review many pre-analyzed articles with low cognitive load, quickly deciding
> whether the extracted knowledge is good enough, needs attention, should be
> skipped, or needs re-analysis.

## 2. Scope

This is a UX and interaction cleanup slice for the existing management web app.

In scope:

- clarify article-level actions
- stabilize the source header layout
- simplify entity card actions
- separate entity rejection/restoration from normal entity editing
- make hidden/rejected entity controls understandable
- fix sidebar label/control spacing
- prepare tag editing for a controlled tag picker
- keep the existing backend write model unless a small endpoint is needed for
  tag choices

Out of scope:

- new LLM calls
- new render semantics
- new synthesis behavior
- authentication
- deployment
- full taxonomy maintenance workflow
- large visual redesign from scratch
- changing the review artifact schema beyond existing fields

## 3. Current Problems

### 3.1 Article Actions Are Ambiguous

The current UI shows both:

- `Finish review`
- `Approve article`

The user does not understand the difference. If finishing a review also approves
the article, the UI should say so directly.

### 3.2 Header Action Layout Is Unstable

The header action buttons shift and wrap depending on title length. With long
article titles, the action area becomes cramped and some buttons become
two-line buttons.

This makes the interface feel unstable.

### 3.3 `Show hidden` Is Not Understandable

The control is visible even when no hidden entities exist. Clicking it may
produce no visible change, so it feels broken.

### 3.4 Entity Edit Buttons Are Too Verbose

Buttons such as `Edit LLM-Maintained Knowledge Bases` repeat the entity title
that is already visible.

### 3.5 `Hidden` In Edit Mode Is Confusing

The entity edit form contains a `Hidden` checkbox. The user does not know what
it means. The user also observed that `Save entity` can appear to depend on
toggling `Hidden`, because the save button is disabled unless something has
changed.

### 3.6 Tag Editing Is Too Free-Form

The current entity tag input is a comma-separated text field. That creates a
risk of typo tags and taxonomy drift.

Desired behavior:

- existing tags should be easy to select
- new tags should be possible but deliberate
- the user should see that they are creating a new tag

### 3.7 Sidebar Controls Need More Breathing Room

Labels and select/input controls in the left sidebar can feel too tight or
visually overlap.

## 4. UX Decisions

### 4.1 Article Action Model

Use one primary happy-path action:

```text
Finish as approved
```

Secondary actions:

- `Needs attention`
- `Skip`
- `Request re-analysis`

Remove the separate visible `Approve article` button unless it has a distinct
backend behavior. If the backend still uses the same status value, the frontend
should not expose two competing actions.

Behavior:

- `Finish as approved` calls the existing finish endpoint.
- `Needs attention`, `Skip`, and `Request re-analysis` call the existing
  decision endpoint.
- Existing conflict behavior remains unchanged.

### 4.2 Stable Header Layout

The header should have two stable zones:

- content zone: publication, title, byline, quiet status metadata
- action zone: navigation and review actions

Requirements:

- The action zone must not shrink based on title length.
- Buttons must keep stable heights.
- Long titles wrap within the content zone only.
- The action zone should be visually secondary except for the primary action.

Recommended layout:

- Use CSS grid:
  - left: `minmax(0, 1fr)`
  - right: fixed or bounded width, for example `260px`
- On narrow screens, stack action zone below the title.
- Use `white-space: nowrap` for short button labels where appropriate.

### 4.3 Entity Actions

Entity cards should show compact actions:

- `Edit`
- `Reject` for visible entities
- `Restore` for rejected entities

Do not use `Hidden` as a user-facing primary concept.

Mapping:

- rejected entity = existing hidden/rejected state in the artifact
- visible entity = not hidden/rejected

The backend may continue using the existing `hidden` field. The UI should
translate that concept into user-facing language:

- `Reject`
- `Rejected`
- `Restore`

### 4.4 Entity Edit Form

The normal edit form should only edit content fields:

- title
- description
- tags

It should not contain a `Hidden` checkbox.

Save behavior:

- `Save entity` is enabled only when title, description, or tags changed.
- This should be visually obvious. If no content changed, the disabled button
  should not look like a hidden-state problem.

Optional helper text:

```text
Change title, description, or tags to save.
```

### 4.5 Hidden/Rejected Entity Visibility

Replace `Show hidden` with a clearer control:

```text
Show rejected entities (n)
```

Behavior:

- If `n = 0`, hide this control or show it disabled in a quiet way.
- If `n > 0`, show it near the entity section controls.
- Rejected entities should display with a `Rejected` badge.
- Rejected entities should not appear by default.

### 4.6 Sidebar Controls

Improve spacing in the left sidebar:

- labels must not visually collide with input/select boxes
- vertical rhythm should be calmer
- controls should have consistent heights
- decision count text should not crowd the select

This is a CSS-only change unless markup structure prevents clean spacing.

## 5. Tag Picker Subslice

The tag picker is larger than the other UI fixes. It should still be part of
this UX cleanup effort, but implemented as a focused subslice.

### 5.1 Desired UX

Replace the comma-separated tag input with a searchable multi-select tag picker.

Requirements:

- current tags are shown as selected chips
- user can remove selected tags
- user can search existing tags
- user can add an existing tag with one click/keyboard action
- unknown input is not silently accepted as a tag
- unknown input shows an explicit create action:

```text
Create new tag: <tag>
```

### 5.2 Tag Source

Use a backend endpoint to provide available tags.

Endpoint:

```http
GET /api/review/tags
```

Response shape:

```json
{
  "tags": [
    {
      "name": "agent-systems",
      "source": "registry",
      "usage_count": 42
    }
  ]
}
```

Allowed `source` values:

- `registry`
- `reviews`
- `graph`

Initial implementation may use a merged list from:

- configured review tag registries under `config/review_tags_*.yaml`
- tags observed in review artifacts

Do not require graph availability for the first implementation. Graph tags can
be added later.

Sorting:

1. exact search match
2. prefix match
3. usage count descending
4. alphabetical

### 5.3 New Tag Creation

Creating a new tag should be possible but deliberate.

Frontend behavior:

- if search text does not match an existing tag, show:

```text
Create new tag: <search text>
```

- when selected, add it as a selected tag chip
- visually mark it as new until saved

Backend behavior:

- no separate registry write is required in this slice
- saving an entity with a new tag writes that tag into the existing review
  artifact, as today
- future taxonomy linting can later detect and normalize new tags

Validation:

- tag must be non-empty
- tag should be normalized to lowercase slug format unless existing local
  conventions say otherwise
- reject tags containing commas

## 6. Frontend Requirements

Files likely involved:

- `web/management/src/App.tsx`
- `web/management/src/styles.css`
- `web/management/src/api.ts`
- `web/management/src/types.ts`
- `web/management/src/App.test.tsx`

### 6.1 Header

Change labels:

- `Finish review` -> `Finish as approved`
- remove `Approve article` from visible secondary actions

Keep:

- previous/next navigation
- `Needs attention`
- `Skip`
- `Request re-analysis`

Layout:

- fixed/bounded action column on desktop
- no two-line action buttons at normal desktop widths
- stacked layout on narrow screens

### 6.2 Entity Cards

Change visible action labels:

- `Edit <title>` -> `Edit`
- add `Reject` for visible entities
- add `Restore` for rejected entities when rejected entities are shown

Accessibility:

- compact buttons must still have descriptive `aria-label`s

### 6.3 Entity Editing

Remove hidden checkbox from edit form.

Edit fields:

- title
- description
- tags via tag picker

Save is enabled only when one of those fields changed.

### 6.4 Rejected Entity Toggle

Compute rejected count from normalized entities.

Display:

- no control when rejected count is zero, or disabled quiet control
- active control when rejected count is greater than zero

### 6.5 Sidebar

CSS polish:

- increase label-control gap
- add margin between decision count text and controls
- ensure select/input content does not overlap labels
- keep count cards, but spacing should feel calmer

## 7. Backend Requirements

Files likely involved:

- `src/management_web/api.py`
- `src/management_web/models.py`
- `src/management_web/review_data.py`
- `tests/management_web/test_api.py`
- `tests/management_web/test_review_data.py`

### 7.1 Tag Registry Endpoint

Add:

```http
GET /api/review/tags
```

Return available tag choices.

Minimum implementation:

- collect tags from config review tag registries
- collect tags from existing review artifacts
- include usage counts where cheap
- return deterministic sorted output

No writes.

### 7.2 Existing Entity Update Endpoint

Keep using:

```http
PATCH /api/review/source/{source_id}/entity
```

No endpoint change required for reject/restore if it can continue using:

```json
{ "group": "...", "index": 0, "hidden": true }
```

The frontend should wrap this with user-facing labels `Reject` and `Restore`.

## 8. Data And Persistence

No new durable state type is required.

Existing writes remain:

- entity edits update the review artifact
- reject/restore updates the existing hidden/rejected state
- finish writes review completion and management approval
- secondary decisions write management review state

Backups before writes remain required.

## 9. Testing Requirements

### Backend Tests

Add or update tests for:

- tag registry endpoint returns tags from config/reviews
- tag registry output is deterministic
- tag registry does not require graph
- existing entity update still supports hidden true/false
- no raw/wiki files are mutated by tag registry reads

### Frontend Tests

Add or update tests for:

- primary action label is `Finish as approved`
- no visible `Approve article` button in the default header
- entity edit button text is compact `Edit`
- edit button has descriptive accessible label
- edit form does not show `Hidden`
- visible entity shows `Reject`
- rejected entity shows `Rejected` and `Restore`
- rejected entity toggle is hidden or disabled when count is zero
- tag picker shows existing tags
- tag picker supports explicit create-new-tag flow
- save stays disabled when no content field changed
- save becomes enabled when title/description/tags changed

### Visual/Manual Checks

Manual browser checks:

- 1280px desktop width
- large monitor width
- narrow laptop width

Check:

- header buttons do not wrap unexpectedly
- long titles do not compress action buttons
- sidebar labels do not overlap controls
- default review flow is understandable without reading docs

## 10. Definition Of Done

The slice is complete when:

- the user can explain the article-level actions without ambiguity
- the header layout is stable with long and short titles
- entity actions are compact and understandable
- entity rejection/restoration is separate from editing
- hidden/rejected entity controls are only visible when meaningful
- tag editing no longer depends on raw comma-separated free text
- sidebar controls have clean spacing
- existing backend write semantics remain intact
- all management web backend tests pass
- all management frontend tests pass
- `hatch run lint:check` passes
- `hatch run test:run` passes
- `npm run test -- --run` passes in `web/management`
- `npm run build` passes in `web/management`
- `npm run lint` passes in `web/management`

## 11. Suggested Implementation Order

1. Backend tag registry endpoint
2. Frontend action label cleanup
3. Header layout stabilization
4. Entity action label cleanup
5. Reject/restore action separation
6. Rejected entity toggle/count behavior
7. Tag picker
8. Sidebar spacing polish
9. Browser review and final tests

## 12. Notes For Cursor

Do not broaden this slice into a full redesign.

Do not introduce a component library unless absolutely necessary. A small local
tag picker component is sufficient.

Do not change render behavior.

Do not introduce LLM calls.

Keep the implementation boring and reviewable.

Prefer small components extracted from `App.tsx` only when they reduce local
complexity for this slice.
