# Management Web Full Entity Coverage Spec

Status: Ready for Cursor implementation
Created: 2026-07-15
Related specs:

- `docs/internal-management-web-app-spec.md`
- `docs/management-web-readonly-batch-review-spec.md`
- `docs/management-web-review-decision-write-spec.md`
- `docs/management-web-decision-filter-spec.md`
- `docs/management-web-review-editing-finish-spec.md`

## 1. Goal

Make the management web review workspace complete enough that the user can
review a source before treating it as finished for render.

The current management web app started with:

- topics
- glossary
- trends

That is not enough. Many review artifacts also contain:

- how-tos
- tools
- foundation models
- implementation studies
- roundup signals
- interview insights

Before the user relies on `Finish review` as "ready for wiki render", the app
must show and support review actions for all entity groups that can be extracted
from a source.

This slice extends entity coverage and fixes a source-of-truth issue: edits must
be reflected in the `review` tree used by wiki render, not only in
`llm_output`.

## 2. Why This Matters

The system has two related artifact areas:

- `llm_output`
  - raw structured output from the extraction pipeline
  - useful for display fallbacks and debugging
- `review`
  - human-reviewable proposal tree
  - used by `wiki_render.collect` through helpers such as `scalar_value`,
    `list_value`, `reviewed_tags`, and `proposal_is_included`

If the management web app edits only `llm_output`, the UI may appear correct,
but `wiki-render` can still render the old unedited values from `review`.

Therefore, this slice must make management edits render-aligned:

- update the relevant `review.<group>[index]` node as the primary write target
- keep the matching `llm_output.<group>[index]` item in sync when it exists
- preserve unknown fields in both locations
- continue returning normalized display data from the refreshed artifact

This applies to existing groups and new groups.

## 3. Non-Negotiable Scope

This slice must implement:

- display coverage for all supported entity groups
- edit/hide/unhide coverage for all supported entity groups
- render-aligned writes into the `review` tree
- compatibility with existing direct `llm_output` display data
- entity counts in queue rows for all supported groups
- tests proving edited values are visible to wiki-render-style accessors
- tests proving hidden/rejected entities do not count as normal approved review
  items where applicable

This slice must not:

- run OpenAI or any other LLM provider
- run wiki render automatically
- run synthesis
- change synthesis prompts
- introduce a raw JSON editor as the main UX
- add arbitrary JSON Patch support
- delete source or review files
- edit raw Readwise exports
- edit generated wiki/vault pages
- implement deployment or authentication
- redesign the whole review app

## 4. Entity Groups

Use these frontend/backend group names.

| Group | Artifact list | Render category | Render behavior |
| --- | --- | --- | --- |
| `topics` | `topics` | `topic` | merged knowledge page |
| `glossary` | `glossary` | `glossary` | merged knowledge page |
| `trends` | `industry_trends` | `trend` | merged knowledge page |
| `how_to` | `how_to` | `how_to` | merged knowledge page |
| `tools` | `tools` | `tool` | merged knowledge page |
| `models` | `foundation_models` | `model` | merged knowledge page |
| `implementation_studies` | `implementation_studies` | `impl_study` | individual source page |
| `signals` | `roundup_signals` | `signal` | individual source page |
| `interview_insights` | `interview_insights` | `insight` | individual source page |

Notes:

- `tools`, `models`, and `how_to` are normal synthesis candidates later.
- `implementation_studies`, `signals`, and `interview_insights` are
  source-near individual pages. They should not be forced into the same synthesis
  mental model.
- The UI may group these into two sections:
  - `Wiki entities`: topics, glossary, trends, how-to, tools, models
  - `Source-specific insights`: implementation studies, signals, interview
    insights

## 5. Source Of Truth For Writes

For every editable entity group, write to the `review` tree first.

Expected review list location:

```text
review.<artifact_list>[index]
```

Each review node typically has:

```json
{
  "proposal_id": "...",
  "proposal_status": "approved",
  "llm_item": { "...": "raw proposed item" },
  "sections": {
    "field_name": {
      "status": "pending",
      "final_text": null,
      "final_list": null,
      "llm_list": []
    }
  },
  "tags": {
    "final_tags": [],
    "approved_new_tags": []
  }
}
```

Implementation rules:

- Scalar edits should write `sections.<field>.final_text`.
- List edits should write `sections.<field>.final_list`.
- Tag edits should write `tags.final_tags`.
- Hidden/rejected state should write `proposal_status="rejected"` for render
  exclusion and also keep the UI-friendly `review_state.hidden=true` metadata.
- Unhide should restore `proposal_status="approved"` unless a future status
  model says otherwise.
- Also update the corresponding `llm_output.<artifact_list>[index]` item when it
  exists, so the debug/display fallback remains coherent.
- If the `review` node is missing but `llm_output` exists, return `409 Conflict`
  with a clear message. Do not silently create a partial review tree in this
  slice.

Rationale:

- `wiki_render.collect` already uses the `review` tree.
- Existing Streamlit review state also lives under `review`.
- Keeping both trees in sync avoids UI/render drift.

## 6. Normalized Display Model

Replace the narrow `EntityGroups` shape with a generic group model while keeping
frontend ergonomics simple.

Recommended backend response shape:

```json
{
  "entities": {
    "groups": [
      {
        "group": "topics",
        "label": "Topics",
        "section": "wiki_entities",
        "items": [
          {
            "index": 0,
            "title": "...",
            "description": "...",
            "tags": ["..."],
            "types": ["..."],
            "evidence": "...",
            "hidden": false,
            "render_category": "topic",
            "render_mode": "merged",
            "raw": {}
          }
        ]
      }
    ]
  }
}
```

Compatibility rule:

- Keep `entities.topics`, `entities.glossary`, and `entities.trends` only if
  existing tests or frontend code still need them during this slice.
- Add the generic `entities.groups` shape in the same response.
- New frontend rendering must iterate over `entities.groups`; do not add more
  hard-coded `<EntityGroup>` blocks.

Each item should expose:

- `index`
- `title`
- `description`
- `tags`
- `types` for tools/models where applicable
- `evidence`
- `hidden`
- `render_category`
- `render_mode`: `merged` or `individual`
- `raw`

## 7. Field Mapping

Use the schema keys already defined in `src/ingest_review/schema.py` and the
render config in `src/wiki_render/collect.py`.

### 7.1 Title Fields

| Group | Title field |
| --- | --- |
| `topics` | `topic_title` |
| `glossary` | `term` |
| `trends` | `trend_title` |
| `how_to` | `question_title` |
| `tools` | `name` |
| `models` | `model_name` |
| `implementation_studies` | `title` |
| `signals` | `signal_title` |
| `interview_insights` | `insight_title` |

Fallbacks are allowed for older artifacts, but writes should use the canonical
field above.

### 7.2 Description Fields

Use one primary description field per group for the compact card:

| Group | Primary description field |
| --- | --- |
| `topics` | `knowledge_summary` |
| `glossary` | `proposed_definition` |
| `trends` | `trend_description` |
| `how_to` | `answer_summary` |
| `tools` | `short_description` |
| `models` | `operational_profile` |
| `implementation_studies` | `overview` |
| `signals` | `summary` |
| `interview_insights` | `summary` |

The UI does not need to expose every scalar field in this slice. It should show
the most important compact field first and keep deeper review fields as future
work.

### 7.3 List Fields For Detail Display

For readability, display important list fields as bullets when present:

| Group | List fields |
| --- | --- |
| `topics` | `key_points` |
| `how_to` | `implementation_steps`, `prerequisites` |
| `tools` | `core_capabilities`, `integration_ecosystem` |
| `models` | `core_capabilities`, `benchmark_observations`, `comparative_observations` |
| `implementation_studies` | `key_lessons`, `open_questions` |
| `signals` | `suggested_destinations`, `mentioned_entities`, `evidence_snippets` |
| `interview_insights` | `suggested_destinations`, `mentioned_entities`, `evidence_snippets` |

List editing is not part of this slice. Display these lists read-only as
supporting detail. A later slice can add a newline-per-item list editor.

### 7.4 Tags And Types

Tag fields:

- `proposed_tags`
- `primary_tag`
- `secondary_tag`
- `suggested_new_tags`
- `suggested_new_tag`

For edits:

- write reviewed tags into `review.<group>[index].tags.final_tags`
- normalize by trimming whitespace and removing duplicates while preserving
  order
- also update `llm_output.<group>[index].proposed_tags` as a display fallback
- remove stale scalar `primary_tag` / `secondary_tag` only from `llm_output`
  when writing a final tag list

Types:

- tools and models have `proposed_types` and `proposed_new_type`
- reviewed types should use the existing `types` review node when present:
  - `types.approved_types`
  - `types.reviewer_types_added`

Type editing is not part of this slice. Displaying types is required.

## 8. Hidden / Rejected Behavior

The previous slice introduced `review_state.hidden`.

For render correctness, this slice must connect hidden state to render inclusion.

Rules:

- Hide entity:
  - set `review.<group>[index].proposal_status = "rejected"`
  - set `review.<group>[index].review_state.hidden = true`
  - set `review.<group>[index].review_state.hidden_at`
  - set `review.<group>[index].review_state.hidden_by`
  - mirror `review_state.hidden = true` into `llm_output.<group>[index]` if it
    exists
- Unhide entity:
  - set `review.<group>[index].proposal_status = "approved"`
  - set or mirror `review_state.hidden = false`

This is important because `wiki_render.resolve.proposal_is_included()` already
excludes `proposal_status="rejected"`.

If existing hidden entities only have `llm_output.review_state.hidden`, the
normalizer should display them as hidden, but the first edit/save should also
repair the corresponding `review` node.

## 9. Backend API Changes

Keep the existing endpoint:

```text
PATCH /api/review/source/{source_id}/entity
```

Extend accepted `group` values:

```text
topics
glossary
trends
how_to
tools
models
implementation_studies
signals
interview_insights
```

Request shape remains:

```json
{
  "group": "how_to",
  "index": 0,
  "title": "How to use prompt caching",
  "description": "Prompt caching helps when repeated prompt prefixes make requests expensive.",
  "tags": ["prompt-caching", "ai-engineering"],
  "hidden": false
}
```

Do not add separate endpoints per entity group.

Response shape remains:

```json
{
  "source_id": "...",
  "group": "how_to",
  "index": 0,
  "backup_path": "...",
  "source": { "...": "refreshed SourceDetailResponse" }
}
```

HTTP behavior:

- `200`: edit succeeded
- `400`: unsafe source ID, unsupported group, invalid index, or invalid field
  payload
- `404`: source raw HTML or review artifact does not exist
- `409`: review node and llm output cannot be safely aligned
- `422`: malformed request body
- `500`: unexpected filesystem write error

## 10. Queue Counts

Queue rows currently expose counts for only three groups.

Expand entity counts so the user can see whether a source contains more than
topics/glossary/trends.

Recommended shape:

```json
{
  "entity_counts": {
    "topics": 2,
    "glossary": 1,
    "trends": 0,
    "how_to": 1,
    "tools": 2,
    "models": 1,
    "implementation_studies": 0,
    "signals": 3,
    "interview_insights": 0
  }
}
```

Add these fields to the existing `entity_counts` object. Preserve existing field
names for backward compatibility, but do not leave the new groups out.

Counts should count non-hidden/non-rejected entities by default. The source
detail response can separately expose hidden entities when `Show hidden` is on.

## 11. Frontend Behavior

The frontend should stop hard-coding three entity sections.

Use a group configuration such as:

```ts
const ENTITY_GROUPS = [
  { group: "topics", label: "Topics", section: "Wiki entities" },
  { group: "glossary", label: "Glossary", section: "Wiki entities" },
  { group: "trends", label: "Trends", section: "Wiki entities" },
  { group: "how_to", label: "How-tos", section: "Wiki entities" },
  { group: "tools", label: "Tools", section: "Wiki entities" },
  { group: "models", label: "Models", section: "Wiki entities" },
  { group: "implementation_studies", label: "Implementation studies", section: "Source-specific insights" },
  { group: "signals", label: "Signals", section: "Source-specific insights" },
  { group: "interview_insights", label: "Interview insights", section: "Source-specific insights" }
]
```

UX rules:

- Keep the default review surface compact.
- Show all groups that have at least one visible item.
- Hide empty groups behind a compact "empty groups" line or do not render them.
- Keep `Show hidden` global for the selected source.
- Hidden/rejected items should be muted and visible only when `Show hidden` is
  enabled.
- Only one entity can be edited at a time.
- Entity edit controls should remain the same: title, description, tags,
  hidden, Save, Cancel.
- Source-specific insights should be visually distinct enough that the user
  understands they are not merged synthesis pages.

No major design pass is required in this slice. Keep styling consistent with the
current management web UI.

## 12. Finish Review Guard

Do not allow `Finish review` when the selected source has unsupported or
unreviewable entity groups that are not displayed by the management web app.

After this slice, the known supported groups are the full list in section 4.

Backend finish guard:

- inspect `llm_output`
- if it contains a non-empty known entity list that has no corresponding
  supported management-web group, reject finish with `409`
- if it contains unknown keys that are not entity lists, ignore them

This is a safety rail against future extraction changes silently bypassing the
review UI.

## 13. Implementation Notes

Likely files:

```text
src/management_web/models.py
src/management_web/review_data.py
src/management_web/api.py
tests/management_web/test_review_data.py
tests/management_web/test_api.py
web/management/src/types.ts
web/management/src/api.ts
web/management/src/App.tsx
web/management/src/App.test.tsx
web/management/src/styles.css
```

Suggested backend config:

```python
@dataclass(frozen=True)
class EditableEntityConfig:
    group: str
    artifact_key: str
    review_key: str
    render_category: str
    render_mode: Literal["merged", "individual"]
    title_key: str
    description_key: str
    tag_keys: tuple[str, ...]
    type_keys: tuple[str, ...] = ()
    evidence_keys: tuple[str, ...] = ()
```

The existing `_ENTITY_GROUP_PATHS`, `_TITLE_KEYS`, `_DESCRIPTION_KEYS`, and
`_TAG_KEYS` can be replaced by one config map.

Suggested normalization flow:

1. Load artifact.
2. For each supported group:
   - read review nodes from `review.<review_key>`
   - read fallback items from `llm_output.<artifact_key>`
   - pair items by index for this slice
   - compute title/description/tags from review final fields first, then
     `llm_item`, then `llm_output`
   - compute hidden from `proposal_status=="rejected"` or `review_state.hidden`
3. Return groups in stable configured order.

Pairing by index is acceptable in this slice because existing review generation
creates review nodes in the same order as `llm_output`. Do not introduce a
complex proposal-ID matching migration unless tests prove it is necessary.

## 14. Tests

Backend tests:

- normalizes all nine supported groups from representative artifacts
- queue counts include all nine groups
- edit `how_to` title writes `review.how_to[0].sections.question_title.final_text`
  and mirrors `llm_output.how_to[0].question_title`
- edit `tools` description writes `review.tools[0].sections.short_description.final_text`
- edit `models` tags writes `review.foundation_models[0].tags.final_tags`
- edit `implementation_studies` title writes the review section and mirrors
  `llm_output.implementation_studies`
- edit `signals` description writes `review.roundup_signals[0].sections.summary.final_text`
- edit `interview_insights` description writes
  `review.interview_insights[0].sections.summary.final_text`
- hiding a `how_to` sets `proposal_status="rejected"` and hides it from normal
  detail output
- unhiding restores `proposal_status="approved"`
- hidden/rejected entities are excluded from queue counts
- edit returns `409` when an `llm_output` entity exists but the matching review
  node is missing
- finish returns `409` if a future non-empty supported-looking entity list is
  not covered by the management web group config
- existing topic/glossary/trend editing still works and now writes the review
  tree as well as `llm_output`

Frontend tests:

- renders how-tos/tools/models when present
- renders implementation studies/signals/interview insights in a separate
  source-specific section
- editing a how-to calls the existing entity endpoint with `group="how_to"`
- editing a tool or model preserves existing edit UX
- hidden source-specific insight disappears by default and appears with
  `Show hidden`
- queue row displays expanded entity counts without becoming visually noisy
- Finish review remains disabled or returns a clear error if backend reports
  unsupported unreviewed entity coverage

Quality gates:

```bash
hatch run pytest tests/management_web -q
hatch run lint:check
hatch run test:run
cd web/management && npm run test -- --run
cd web/management && npm run build
cd web/management && npm run lint
```

## 15. Definition Of Done

The slice is complete when:

- all known extracted entity groups are visible in the management web source
  detail
- all known groups can be hidden/unhidden
- the important title/description/tag fields can be edited for all known groups
- edits are written to the render-used `review` tree
- edits are mirrored to `llm_output` for display/debug coherence
- queue counts make non-topic entities visible at a glance
- `Finish review` is no longer premature because hidden entity groups cannot
  bypass the UI silently
- tests prove wiki-render-style accessors see edited values
- no LLM calls, render calls, synthesis calls, raw mutations, or wiki mutations
  are introduced

## 16. Follow-Ups Not In This Slice

Do not implement these now:

- full editing for every scalar/list field of every entity type
- type editing for tools and models
- taxonomy recommendation or tag linting
- proposal-ID based repair/migration of old artifacts
- automatic render after finish
- render-specific UI preview
- synthesis changes
- public/team wiki publication
- deployment/auth changes

These are valuable later, but the current goal is to make review coverage
complete and render-aligned.
