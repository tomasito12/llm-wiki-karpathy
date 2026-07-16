# Management Web Update Wiki Workflow Spec

Date: 2026-07-16
Status: Implementation-ready draft for Cursor

Related docs:

- `docs/internal-management-web-app-spec.md`
- `docs/management-web-pipeline-cockpit-spec.md`
- `docs/management-web-pipeline-cockpit-review-2026-07-16.md`
- `docs/wiki-ops-status-technical-spec.md`
- `docs/wiki-synthesis-automation-technical-spec.md`
- `docs/product-roadmap-spec.md`

## 1. Purpose

The current Pipeline Cockpit exposes many individual operations:

- health check
- synthesis select
- synthesis batch dry-run
- synthesis batch
- render dry-run
- render write
- lint
- status refresh

This is useful for development, but it is too cognitively heavy for daily use.
The user should not have to remember or manually sequence all operations.

This slice changes the cockpit from a command panel into a guided automation
surface.

The new primary user action is:

```text
Update Wiki
```

`Update Wiki` is a backend-orchestrated workflow that runs the normal pipeline
steps in the right order, stops at risk boundaries, and shows only the decisions
that need the user's attention.

## 2. Product Goal

Reduce cognitive load.

The normal user experience should be:

1. Open the management app.
2. See whether the wiki is current or needs work.
3. Click `Update Wiki` if work is available.
4. Let the system run safe checks automatically.
5. Confirm only expensive or write-capable steps.
6. See a concise workflow result.

Manual one-off commands must remain available, but they should move into a less
prominent `Advanced manual operations` section.

## 3. Target UX

### 3.1 Primary Surface

Replace the current command-heavy Pipeline page with a calmer layout:

```text
Pipeline

[Status band]
Wiki update available
42 stale syntheses · render needs refresh · no blocking errors

Synthesis batch size: [5]
[Update Wiki]

[Workflow progress / latest workflow result]

[Advanced manual operations collapsed]
```

If no work is needed:

```text
Wiki is up to date
No render needed · synthesis cache fresh · lint clean

[Run health check]

[Advanced manual operations collapsed]
```

### 3.2 Advanced Manual Operations

The existing operation cards should not disappear. Move them into a collapsed
section:

```text
Advanced manual operations
  Health check
  Render preview
  Render write
  Candidate ranking
  Batch dry-run
  Batch execution
```

Default state: collapsed.

The user can still run single commands while debugging, but the main interface
should encourage the guided workflow.

## 4. Workflow Semantics

Implement a new backend workflow operation:

```text
update_wiki
```

This is not a shell command. It is an orchestration of existing backend
operations in Python.

The workflow must run one step at a time and write a durable run report under
the existing management run directory:

```text
{knowledge_root}/tmp/management_runs/
```

Use the existing `OpsRunManager` / operation-run style where possible, but do
not force the workflow into the old single-command abstraction if that makes
the design brittle. A workflow report may have child steps.

## 5. Workflow Steps

### Step 1: Collect Status

Run:

```python
collect_management_ops_status(paths)
```

No writes. No LLM calls. No confirmation.

Purpose:

- determine whether synthesis has changed/stale candidates
- determine whether render appears current
- determine whether cache/lint status has warnings
- determine whether uncommitted durable files exist

### Step 2: Blocker Check

If any hard blocker exists, stop before doing more work.

Hard blockers for this slice:

- status collection fails
- synthesis cache lint has errors
- source text coverage is dangerously low if this is available in status
- another operation/workflow is already running

Soft warnings should not block by default, but must be shown.

Soft warnings:

- uncommitted durable files
- changed synthesis candidates
- stale synthesis candidates
- lint warnings
- manual review items

### Step 3: Synthesis Candidate Planning

If changed/stale synthesis candidates exist, run the equivalent of:

```text
wiki-synthesis-select --limit <batch_size> --json
```

No LLM calls. No writes.

Show a readable summary:

```text
42 candidates found · 5 selected for this run
1. Context Engineering · topic · 14 sources · stale · score 140
2. Cognigy.AI · tool · 4 sources · stale · score 114
...
```

If there are no synthesis candidates, skip synthesis steps.

### Step 4: Confirm Synthesis Batch

If candidates exist, stop for inline confirmation:

```text
Run 5 synthesis updates now?
This may call the OpenAI API and will write synthesis cache files.

[Run synthesis] [Skip synthesis for now]
```

Rules:

- The workflow should pause in a `waiting_for_confirmation` state.
- It must be resumable by calling a confirmation endpoint.
- It must not call OpenAI before confirmation.
- If the user chooses `Skip synthesis for now`, continue to render dry-run with
  existing cache state.

### Step 5: Run Synthesis Batch

If confirmed, run the equivalent of:

```text
wiki-synthesis-batch --limit <batch_size> --yes --json
```

Use the configured batch size.

No automatic `--continue-on-error` for this slice unless the existing UI already
has a clear parameter. Default: stop on first error.

Show a readable summary:

```text
Synthesis batch completed
5 selected · 5 attempted · 5 written · 0 failed
```

If the batch fails:

- stop workflow
- show failed step
- show readable error
- keep technical logs expandable
- do not proceed to render

### Step 6: Render Dry-Run

Run automatically:

```text
wiki-render --dry-run
```

No writes.

Show a readable summary from stdout/stderr:

```text
Render preview completed
1070 output files · 0 would write · 0 would prune
295/295 source pages include raw text
```

If render dry-run fails, stop workflow.

### Step 7: Confirm Render Write

If render dry-run reports no files to write and no prune, the workflow may skip
render write and continue to lint.

If render dry-run reports changes, stop for inline confirmation:

```text
Write generated wiki files?
23 files will be updated · 0 stale files pruned

[Write render] [Stop here]
```

Rules:

- Do not write the vault before confirmation.
- Always include `--require-source-text` for real render writes.
- If the user chooses `Stop here`, workflow ends with status `waiting/stopped`
  and clear next step.

### Step 8: Render Write

If confirmed, run:

```text
wiki-render --require-source-text
```

Show concise output:

```text
Render written
23 files written · 1047 unchanged · 0 pruned
```

If render write fails, stop workflow and do not run lint.

### Step 9: Wiki Lint

Run automatically after render write, or after render dry-run if no write was
needed:

```text
wiki-lint
```

No writes.

Show concise output:

```text
Wiki health check completed
0 safe delete candidates · 0 duplicate groups · 0 blocking warnings
```

If lint fails:

- workflow status is `warning` or `failed` depending on exit code
- show readable warning list
- keep technical logs expandable

### Step 10: Final Status Refresh

Run status collection again.

Show final result:

```text
Wiki updated successfully
Synthesis fresh · render current · lint clean
```

or:

```text
Wiki update stopped
Synthesis succeeded, render write still needs approval
```

## 6. Batch Size

The workflow must expose a configurable synthesis batch size.

Default:

```text
5
```

Allowed:

```text
1..100
```

UI:

```text
Synthesis batch size [5]
```

Rules:

- The value is chosen before starting `Update Wiki`.
- The workflow report records the selected value.
- The confirmation step must say how many candidates will be processed:

```text
5 of 42 synthesis candidates will be processed.
```

## 7. Backend API Design

Add workflow endpoints under the existing management API.

Suggested endpoints:

```text
GET  /api/ops/workflows/update-wiki/status
POST /api/ops/workflows/update-wiki/start
POST /api/ops/workflows/update-wiki/{run_id}/confirm
POST /api/ops/workflows/update-wiki/{run_id}/skip
GET  /api/ops/workflows/update-wiki/{run_id}
GET  /api/ops/workflows/update-wiki/runs
```

Exact route names may change if they fit existing API style better, but the
semantics must remain.

### 7.1 Start Request

```json
{
  "synthesis_batch_size": 5
}
```

Validation:

- integer
- min 1
- max 100

### 7.2 Workflow Run Model

A workflow run should include:

```json
{
  "run_id": "20260716T170000Z-update-wiki",
  "workflow_id": "update_wiki",
  "status": "running | waiting_for_confirmation | succeeded | failed | stopped",
  "current_step": "synthesis_confirm",
  "started_at": "...",
  "finished_at": null,
  "parameters": {
    "synthesis_batch_size": 5
  },
  "steps": [
    {
      "id": "status",
      "label": "Status check",
      "status": "succeeded",
      "writes": false,
      "llm_calls": false,
      "summary_lines": ["42 synthesis candidates found"],
      "technical_stdout": "",
      "technical_stderr": ""
    }
  ],
  "pending_confirmation": {
    "id": "synthesis_batch",
    "title": "Run 5 synthesis updates now?",
    "description": "This may call the OpenAI API and will write synthesis cache files.",
    "confirm_label": "Run synthesis",
    "skip_label": "Skip synthesis for now"
  }
}
```

### 7.3 Confirmation Request

```json
{
  "confirmation_id": "synthesis_batch"
}
```

The backend must reject confirmation if the workflow is not waiting for that
exact confirmation.

## 8. Backend Safety Rules

- Only one operation or workflow may run at a time.
- `Update Wiki` must not bypass existing confirmation requirements for LLM
  calls or writes.
- If the browser disconnects, the workflow should continue until the next
  confirmation or terminal state.
- The workflow report must be written atomically.
- Technical stdout/stderr should be retained, but the UI should default to
  readable summaries.
- Do not introduce automatic Git commits in this slice.
- Do not introduce cron/background scheduled runs in this slice.
- Do not delete files in this slice.

## 9. Frontend UX Requirements

### 9.1 New Primary Cockpit

The Pipeline tab should prioritize:

1. status
2. `Update Wiki`
3. workflow progress/result
4. problems requiring attention
5. collapsed advanced manual operations

Recommended next actions should no longer be a prominent action list. If kept,
they should become passive hints:

```text
Hints
- 42 stale syntheses are ready for the next update.
- Durable files are uncommitted.
```

No large buttons in the hint list.

### 9.2 Workflow Progress UI

Show steps as a simple vertical timeline:

```text
✓ Status check
✓ Candidate planning
⏸ Run synthesis? [Run synthesis] [Skip]
○ Render preview
○ Render write
○ Health check
```

Each step should show:

- status icon/text
- one-line summary
- expandable technical details

### 9.3 Manual Operations UI

Move existing operation cards into:

```text
Advanced manual operations
```

Default: collapsed.

This section is for debugging and exceptional manual control.

## 10. Result Parsing

Do not show raw JSON as the primary output.

Add frontend or backend helpers to turn known command outputs into summary
lines.

Required parsers for this slice:

- `wiki-synthesis-select --json`
  - supports real keys: `entries`, `shown`, `total_changed`
  - show top 5 entries by rank
  - show title/entity/category/source count/state/score if present

- `wiki-synthesis-batch --json`
  - show selected/planned/attempted/called/written/failed/dry_run if present

- `wiki-render --dry-run`
  - parse key lines from the human stdout summary
  - include would write / unchanged / would prune / source full text coverage

- `wiki-render`
  - parse written/unchanged/pruned/source text coverage from stdout/stderr

- `wiki-lint`
  - parse warnings, safe delete candidates, duplicate groups, manual review
    items if present

Technical logs remain available under an expandable control.

## 11. Testing Requirements

### Backend Tests

Add tests for:

- start validates synthesis batch size
- workflow starts with status check
- workflow pauses before synthesis batch when candidates exist
- confirmation with wrong id is rejected
- skipping synthesis continues to render dry-run
- render write pauses before writing when dry-run has changes
- lint runs after render write
- failure stops later steps
- workflow report is written atomically
- only one workflow/operation may run at a time

### Frontend Tests

Add tests for:

- primary `Update Wiki` button exists
- batch size defaults to 5
- invalid batch size is not allowed
- recommended next actions are not shown as prominent command buttons
- workflow timeline renders step states
- pending synthesis confirmation renders inline
- pending render confirmation renders inline
- advanced manual operations are collapsed by default
- technical details expand locally within a step

### Existing Tests

Update existing Pipeline Cockpit tests that assume all operations are always
prominent.

## 12. Definition Of Done

This slice is complete when:

- The Pipeline page has one primary `Update Wiki` action.
- The synthesis batch size defaults to 5 and can be changed from 1 to 100.
- Safe read-only checks run automatically inside the workflow.
- LLM/write steps pause for explicit inline confirmation.
- Workflow progress is shown as a readable step timeline.
- Existing manual operations are still available but collapsed under advanced
  controls.
- Raw stdout/stderr/JSON is never the default primary output.
- Tests cover backend orchestration and frontend workflow UX.
- `npm run lint`, `npm run test -- --run`, `npm run build`,
  `hatch run lint:check`, and `hatch run test:run` pass.

## 13. Non-Goals

Do not implement in this slice:

- cron jobs
- fully unattended autopilot
- automatic Git commits
- automatic pushes
- cleanup/deletion
- public/team wiki publishing
- authentication changes
- deployment changes
- new synthesis prompt changes

This slice is the bridge from manual cockpit to guided automation.
