# Management Web Pipeline Cockpit Spec

Date: 2026-07-16
Status: Implementation-ready draft for Cursor
Related docs:

- `docs/product-roadmap-spec.md`
- `docs/internal-management-web-app-spec.md`
- `docs/wiki-ops-status-technical-spec.md`
- `docs/wiki-synthesis-automation-technical-spec.md`
- `docs/management-web-fast-review-ux-fix-spec.md`

## 1. Purpose

The management web app currently focuses on article review. That is the right
first product surface, but the user still has to switch back to the terminal for
normal pipeline operation.

This slice adds a private operator cockpit to the management web app.

The cockpit should answer:

- What is the current system state?
- What needs attention?
- Which pipeline steps are safe to run now?
- What will a command do before it writes?
- Did the last run succeed?
- Where can I inspect logs if something failed?

The goal is not to invent new pipeline behavior. The goal is to expose existing
status and workflow commands safely through the web app.

## 2. Product Goal

Make the management app a practical daily operating surface for the local LLM
Wiki system.

The user should not need to remember which `hatch run ...` command comes next
for common maintenance work.

The cockpit should feel like a calm checklist:

1. refresh status
2. inspect recommended next actions
3. run a safe dry-run
4. run the real operation only after confirmation
5. inspect result
6. continue with the next recommended step

## 3. Current Context

The project already has these important foundations:

- `hatch run wiki-ops-status`
  - read-only
  - no LLM calls
  - JSON-capable
  - summarizes source/review/render/synthesis/vault state

- `hatch run wiki-render --dry-run`
  - read-only for the vault
  - reports planned render changes

- `hatch run wiki-render`
  - writes generated wiki output and manifest/graph state

- `hatch run wiki-lint`
  - read-only
  - checks generated wiki contract and hygiene

- `hatch run wiki-synthesis-select`
  - read-only
  - ranks changed synthesis candidates

- `hatch run wiki-synthesis-batch --dry-run`
  - read-only planning mode

- `hatch run wiki-synthesis-batch --yes`
  - may call OpenAI
  - writes synthesis cache and audit reports

- `hatch run readwise-sync`
  - writes raw Readwise exports and index state

- `hatch run ingest-preanalyze`
  - may call an LLM
  - writes review/preanalysis artifacts

The React management frontend already exists under:

```text
web/management/
```

The FastAPI backend already exists under:

```text
src/management_web/
```

The app already uses:

```text
config/wiki_paths.toml
```

Do not duplicate path logic in the frontend.

## 4. Non-Goals

Do not implement in this slice:

- cron/launchd/systemd scheduling
- server deployment
- authentication
- automatic Git commits
- automatic pushes
- automatic cleanup deletion
- semantic LLM wiki linting
- new synthesis algorithms
- new ingestion extraction prompts
- team-facing/public wiki site
- a full workflow graph engine

This slice is an operator cockpit for existing workflows.

## 5. Scope

### 5.1 MVP Scope

The MVP cockpit should include:

- status dashboard backed by `collect_ops_status`
- recommended next actions
- operation cards for common commands
- dry-run support where available
- write/LLM confirmation gates
- run history for operations launched from the web app
- log preview for the latest runs
- clear busy/running/failed/succeeded states

### 5.2 MVP Operations

Implement these first:

| Operation | Type | Writes? | LLM calls? | Confirmation |
|---|---:|---:|---:|---:|
| Refresh ops status | read | no | no | no |
| Wiki lint | read | no | no | no |
| Wiki render dry-run | read | no | no | no |
| Wiki render | write | yes | no | yes |
| Synthesis select | read | no | no | no |
| Synthesis batch dry-run | read | no | no | no |
| Synthesis batch | write | yes | yes | yes |

### 5.3 Deferred Operations

These should be designed for but do not need to ship in the first cockpit slice
unless the implementation stays small:

| Operation | Reason to defer |
|---|---|
| Readwise sync | Needs careful Readwise index/bookkeeping display |
| Ingest preanalysis | Potentially many LLM calls; needs cost controls |
| Cleanup | Destructive; already has release-manifest safety requirements |
| Vault Git commit | Requires separate private-vault Git policy UX |
| Release manifest write | Useful but secondary |

## 6. UX Design

Add a new cockpit view to the management web app.

Do not remove the review workspace. The app should support at least two main
views:

- `Review`
- `Pipeline`

Simple navigation is enough for this slice.

### 6.1 Pipeline View Layout

Recommended layout:

```text
Top app bar
  Review | Pipeline

Pipeline page
  Status summary band
  Recommended next actions
  Operation cards
  Recent runs
  Log/details drawer
```

### 6.2 Status Summary Band

Show compact facts from ops status:

- raw export pairs
- review workflow counts
- render status
- synthesis fresh/stale counts
- changed synthesis candidates
- vault lint/hygiene warning count if available

Use calm labels.

Example:

```text
Pipeline Status
506 sources · 292 reviewed · render current · 42 stale syntheses
```

### 6.3 Recommended Next Actions

Show the `recommendations` from `wiki-ops-status` prominently.

Requirements:

- Each recommendation should be readable as a checklist item.
- If a matching operation exists, show a small action button next to it.
- If no direct operation exists, show it as guidance only.

Example:

```text
1. Refresh stale synthesis entries before final render. [Open synthesis batch]
2. Review uncommitted docs and code files before continuing.
3. Optional: synthesize the next small batch from wiki-synthesis-plan. [Dry-run batch]
```

### 6.4 Operation Cards

Each operation card should show:

- operation name
- what it reads
- what it writes, if anything
- whether it can call an LLM
- default parameters
- primary safe action
- destructive/write action only when explicitly confirmed

Example card:

```text
Wiki Render
Updates generated Obsidian wiki pages from finished reviews.

Safe check: Dry-run
Writes: wiki output, graph, manifest

[Dry-run] [Run render...]
```

### 6.5 Confirmation UX

Any operation that writes files or can call an LLM must require confirmation.

Confirmation modal should show:

- operation name
- command-equivalent summary
- writes expected
- LLM possible yes/no
- key parameters
- checkbox or explicit confirmation button

Do not rely only on button color for safety.

### 6.6 Run State UX

When an operation runs:

- show `queued`, `running`, `succeeded`, `failed`, or `cancelled`
- show start time
- show elapsed time
- show exit code when complete
- show stdout/stderr tail
- show full audit path if a report file exists

The UI does not need to stream logs in real time in the first implementation.
Polling every few seconds is enough.

### 6.7 Parameters

For MVP, expose only a small set of parameters.

Synthesis batch:

- `limit`
- `between_calls`
- `continue_on_error`
- real run requires confirmation

Recommended defaults:

- dry-run limit: `10`
- real batch limit: `5`
- between calls: `300` seconds
- continue on error: `false`

Wiki render:

- dry-run
- real run
- optional `require_source_text` checkbox, default `true` for real run if
  existing CLI supports it

Synthesis select:

- limit, default `20`

Wiki lint:

- no advanced parameters in MVP

## 7. Backend Architecture

Add a small operations layer under:

```text
src/management_web/
  ops.py
```

or:

```text
src/wiki_ops/web_runner.py
```

Recommendation:

- keep web-specific API models in `src/management_web/models.py`
- keep operation execution logic in `src/management_web/ops.py`
- reuse existing pipeline modules where straightforward
- for CLI-shaped operations, prefer invoking Python modules with
  `sys.executable -m ...` rather than shelling out through `hatch`

Do not run arbitrary commands from frontend input.

Use a hardcoded operation registry.

## 8. Backend API

### 8.1 Get Ops Status

```http
GET /api/ops/status
```

Behavior:

- read-only
- no LLM calls
- no writes
- returns current ops status using existing status collector

Response:

```json
{
  "status": { "...": "same shape as wiki-ops-status --json" },
  "collected_at": "2026-07-16T10:00:00Z"
}
```

### 8.2 List Operations

```http
GET /api/ops/operations
```

Response:

```json
{
  "operations": [
    {
      "id": "wiki_render_dry_run",
      "label": "Wiki render dry-run",
      "description": "Preview generated wiki changes.",
      "writes": false,
      "llm_calls": false,
      "requires_confirmation": false,
      "parameters": []
    }
  ]
}
```

### 8.3 Start Operation

```http
POST /api/ops/runs
```

Request:

```json
{
  "operation_id": "wiki_render_dry_run",
  "parameters": {
    "require_source_text": true
  },
  "confirmed": false
}
```

Rules:

- unknown operation id -> `400`
- invalid parameter -> `400`
- write operation without `confirmed: true` -> `409`
- LLM-capable operation without `confirmed: true` -> `409`
- if another operation is already running -> `409` in MVP

Response:

```json
{
  "run_id": "20260716T100000Z-wiki-render-dry-run",
  "operation_id": "wiki_render_dry_run",
  "status": "queued"
}
```

### 8.4 Get Run

```http
GET /api/ops/runs/{run_id}
```

Response:

```json
{
  "run_id": "20260716T100000Z-wiki-render-dry-run",
  "operation_id": "wiki_render_dry_run",
  "status": "succeeded",
  "started_at": "2026-07-16T10:00:00Z",
  "finished_at": "2026-07-16T10:00:03Z",
  "exit_code": 0,
  "stdout_tail": "...",
  "stderr_tail": "",
  "report_path": "/path/to/report.json"
}
```

### 8.5 List Runs

```http
GET /api/ops/runs?limit=20
```

Returns recent management-launched runs.

## 9. Operation Registry

Use explicit operation definitions.

Example conceptual shape:

```python
OperationDefinition(
    id="wiki_render_dry_run",
    label="Wiki render dry-run",
    module="src.wiki_render",
    args=["--paths-config", "{paths_config}", "--dry-run"],
    writes=False,
    llm_calls=False,
    parameters=[...],
)
```

Operation definitions must not be constructed from arbitrary frontend command
strings.

### 9.1 MVP Operation Commands

Use the configured `wiki_paths.toml`.

Suggested module invocations:

```bash
python -m src.wiki_ops.status_cli --paths-config config/wiki_paths.toml --json
python -m src.wiki_lint --paths-config config/wiki_paths.toml
python -m src.wiki_render --paths-config config/wiki_paths.toml --dry-run
python -m src.wiki_render --paths-config config/wiki_paths.toml --require-source-text
python -m src.wiki_synthesis.select_cli --paths-config config/wiki_paths.toml --limit 20 --json
python -m src.wiki_synthesis.batch_cli --paths-config config/wiki_paths.toml --dry-run --limit 10
python -m src.wiki_synthesis.batch_cli --paths-config config/wiki_paths.toml --limit 5 --between-calls 300 --yes
```

If a module has a direct callable API that is cleaner than subprocess execution,
it may be used. But subprocess execution is acceptable for the cockpit MVP
because it preserves existing CLI behavior and audit output.

## 10. Run Storage

Store management-launched run reports under the knowledge store:

```text
{knowledge_root}/tmp/management_runs/
```

Each run should write one JSON report:

```text
{knowledge_root}/tmp/management_runs/<run_id>.json
```

Report fields:

- run_id
- operation_id
- label
- status
- parameters
- command/module args
- cwd
- started_at
- finished_at
- duration_seconds
- exit_code
- stdout_tail
- stderr_tail
- full stdout/stderr path if stored separately
- report_path if the underlying operation produced one

Do not commit these reports by default. They are operational audit artifacts.

## 11. Concurrency

MVP rule:

- only one operation can run at a time

If an operation is running:

- `POST /api/ops/runs` for another operation returns `409`
- frontend shows the current running operation

Reason:

- avoids simultaneous render/synthesis/status races
- avoids unexpected API cost overlap
- keeps local filesystem writes simpler

Future versions can support a queue if needed.

## 12. Cancellation

Cancellation is optional for MVP.

If implemented:

```http
POST /api/ops/runs/{run_id}/cancel
```

Only cancel the process launched by the management app.

If not implemented, the UI should say:

```text
Running. Close terminal/server to interrupt if necessary.
```

## 13. Safety Rules

Hard requirements:

- frontend cannot submit arbitrary shell commands
- operation ids must be allowlisted
- parameters must be validated server-side
- write/LLM operations require confirmation
- no OpenAI key value is ever sent to frontend
- raw source text must not appear in operation logs unless an existing command
  prints it; avoid adding such printing
- real synthesis batch must show `LLM calls possible`
- real render must show `writes vault/wiki output`
- cleanup/destructive operations are not in MVP

## 14. Frontend Requirements

Files likely involved:

```text
web/management/src/App.tsx
web/management/src/api.ts
web/management/src/types.ts
web/management/src/styles.css
web/management/src/App.test.tsx
```

If `App.tsx` becomes too large, extract small components:

```text
web/management/src/PipelineCockpit.tsx
web/management/src/ReviewWorkspace.tsx
```

Do not do a broad frontend architecture rewrite.

### 14.1 Navigation

Add simple navigation:

- `Review`
- `Pipeline`

Default view can remain `Review`.

### 14.2 Pipeline Page

Show:

- status summary
- recommendations
- operation cards
- recent runs
- selected run details

### 14.3 Refresh Behavior

The page should load status on entry.

Add a `Refresh status` button.

When an operation completes, refresh status automatically.

### 14.4 Polling

When a run is queued or running:

- poll `GET /api/ops/runs/{run_id}` every 2-5 seconds
- stop polling when terminal state is reached

Terminal states:

- `succeeded`
- `failed`
- `cancelled`

### 14.5 Confirmation Modal

Use a simple modal or inline confirmation panel.

Must show:

- operation label
- writes yes/no
- LLM calls yes/no
- parameters
- confirm button
- cancel button

## 15. Backend Tests

Add tests under:

```text
tests/management_web/
```

Test:

- `GET /api/ops/status` returns JSON without writes
- `GET /api/ops/operations` returns allowlisted operations
- starting read-only operation does not require confirmation
- starting write operation without confirmation returns `409`
- starting LLM operation without confirmation returns `409`
- invalid operation id returns `400`
- invalid parameter returns `400`
- only one operation can run at a time
- run report is written for completed runs
- failed operation records non-zero exit code and stderr tail

Use test doubles for operation execution where possible. Do not make real LLM
calls in tests.

## 16. Frontend Tests

Add/update tests for:

- Pipeline navigation appears
- Pipeline page loads status summary
- recommendations render
- operation cards render safety metadata
- read-only operation can be started without confirmation
- write/LLM operation opens confirmation
- running state is shown
- successful run refreshes status
- failed run shows error/log tail

## 17. Manual Verification

Manual local checks:

1. Start backend:

```bash
hatch run management-api --paths-config config/wiki_paths.toml
```

2. Start frontend:

```bash
hatch run management-ui -- --host 127.0.0.1 --port 5173
```

3. Open:

```text
http://127.0.0.1:5173/
```

4. Verify:

- Review page still works.
- Pipeline page loads.
- Status summary matches `hatch run wiki-ops-status`.
- Wiki lint operation completes.
- Wiki render dry-run completes.
- Real render requires confirmation.
- Synthesis batch real run requires confirmation and exposes LLM warning.

Do not run a real synthesis batch during manual verification unless the user
explicitly approves OpenAI API calls.

## 18. Definition Of Done

The slice is done when:

- pipeline page exists in the management app
- ops status is visible without terminal use
- recommendations are visible
- safe read-only operations can be launched from UI
- write/LLM operations are gated by confirmation
- recent run history is visible
- run logs/errors are inspectable
- no arbitrary command execution is possible
- review workspace still works
- backend tests pass
- frontend tests pass
- `hatch run lint:check` passes
- `hatch run test:run` passes
- `npm run test -- --run` passes in `web/management`
- `npm run build` passes in `web/management`
- `npm run lint` passes in `web/management`

## 19. Notes For Cursor

Keep this implementation conservative.

This is not a general automation framework. It is a small allowlisted cockpit
for the existing LLM Wiki pipeline.

Prefer:

- explicit operation ids
- explicit parameters
- explicit safety metadata
- boring JSON reports
- simple polling

Avoid:

- arbitrary shell command endpoints
- hidden background automation
- cron
- auto-commit
- destructive cleanup
- LLM calls in tests
- large frontend redesign beyond what the cockpit needs
