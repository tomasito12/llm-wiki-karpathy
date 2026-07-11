# Technical Specification: Wiki Synthesis Selection and Batch Automation

Last updated: 2026-07-10

This specification is intended for an implementation agent that has no prior
chat context. It describes the next controlled automation step for Stage 2 wiki
synthesis in `llm-wiki-karpathy`.

## Background Context

This repository powers a local AI knowledge-base system.

The system currently works roughly like this:

1. Articles are exported from Readwise into `raw/readwise/`.
2. LLM-assisted review artifacts are created under `state/reviews/<source_id>/review.json`.
3. `hatch run wiki-render` regenerates an Obsidian wiki under `wiki/`.
4. The render also writes `state/wiki_render_graph.json`, which is the machine-readable evidence graph.
5. Stage 2 synthesis combines multiple evidence fragments into human-readable synthesis cache entries under `state/synthesis/<category>/<slug>.json`.
6. `wiki-render` uses fresh synthesis cache entries to render nicer Obsidian wiki pages.

The user wants this system to become more automatic over time, but without
turning it into an opaque or fragile machine. The important constraints are:

- LLM calls must not explode.
- Automation must remain auditable.
- Failures must stop safely or be clearly reported.
- The system should avoid hidden side effects.
- Nightly jobs should run slowly and predictably.
- The user should be able to understand what happened the next morning.

## Current Relevant Commands

Existing commands:

```bash
hatch run wiki-ops-status
hatch run wiki-synthesis-plan --changed-only --limit 20
hatch run wiki-synthesis-workflow --entity topic:example --yes
hatch run wiki-synthesis-workflow --category topic --limit 5 --yes
hatch run wiki-synthesis-cache-lint
hatch run wiki-render --dry-run
hatch run wiki-render
```

Important current behavior:

- `wiki-synthesis-plan` is read-only.
- `wiki-synthesis-workflow --yes` makes OpenAI API calls and writes synthesis cache files.
- `wiki-synthesis-workflow` can already process more than one target with `--limit`.
- `wiki-synthesis-workflow` writes audit reports to `state/synthesis_runs/`.
- `wiki-render` never calls an LLM.
- `wiki-render --dry-run` can confirm whether the generated wiki would change.
- `wiki-ops-status` now reports high-level state and whether render/cache/artifacts look clean.

## Problem

The user currently has to manually choose and run small batches of Stage 2
synthesis candidates.

That is acceptable for testing, but not for productive long-term use.

The user would like a future nightly job that can slowly work through pending
synthesis candidates, for example with a pause of several minutes between OpenAI
calls.

However, jumping directly to a cron job is risky unless the selection and batch
execution behavior are specified first.

The main design question is:

Should the system simply process all pending synthesis candidates, or should it
first rank/recommend candidates?

Answer:

Build a small selection layer and a controlled batch layer. The selection layer
must be deterministic and read-only. The batch layer may execute the selected
work slowly, with limits and audit reports.

## Goals

Implement a controlled path from "pending synthesis candidates exist" to "a safe
batch was executed".

The intended final operator flow should be:

```bash
hatch run wiki-synthesis-select --limit 20
hatch run wiki-synthesis-batch --limit 20 --between-calls 300 --yes
hatch run wiki-synthesis-cache-lint
hatch run wiki-render --dry-run
hatch run wiki-ops-status
```

Later, the batch command can be used from cron.

## Non-Goals

Do not implement in this task:

- a cron installer
- launchd/systemd setup
- automatic Git commits
- automatic pushes
- automatic cleanup of preview/run artifacts
- automatic `wiki-render` after synthesis
- automatic website publication
- LLM-based deduplication or semantic merge decisions
- a web frontend

This task should only build the deterministic selection and controlled batch
execution layer.

## Architecture Decision

Use two layers:

1. `wiki-synthesis-select`
   - read-only
   - no LLM calls
   - no file writes
   - ranks pending synthesis candidates deterministically
   - emits text or JSON
   - can optionally print copy-paste commands

2. `wiki-synthesis-batch`
   - executes selected candidates
   - requires `--yes` for real API calls
   - supports `--dry-run`
   - supports pauses between calls via `--between-calls`
   - writes normal synthesis cache entries and normal preview artifacts
   - writes one audit report
   - does not run `wiki-render`

The batch command should reuse existing synthesis workflow/executor logic rather
than duplicating the synthesis engine.

## Why Not Only `--limit 10`?

`wiki-synthesis-workflow --limit 10 --yes` already does part of the job.

But it lacks a clear automation contract:

- no explicit pause between API calls
- no named nightly/batch intent
- no deterministic relevance ranking
- no clear "this is safe for cron" status
- no batch-specific summary such as remaining candidates

The new commands should not replace the existing workflow. They should wrap or
reuse it with a clearer automation surface.

## Command 1: `wiki-synthesis-select`

### Purpose

Show which synthesis candidates should be processed next.

This is a deterministic, local, read-only selection tool.

### Proposed Hatch Script

```toml
wiki-synthesis-select = [
  "python -m src.wiki_synthesis.select_cli {args}",
]
```

### Example Usage

```bash
hatch run wiki-synthesis-select --limit 20
hatch run wiki-synthesis-select --category topic --limit 10
hatch run wiki-synthesis-select --json --limit 20
hatch run wiki-synthesis-select --commands --limit 5
```

### Inputs

- `state/wiki_render_graph.json`
- `state/synthesis/<category>/<slug>.json`
- existing planner logic from `src/wiki_synthesis.planner`

### Output

Text output should include:

- total changed candidates
- number shown
- ranking score
- entity id
- category
- source count
- evidence count
- title
- reason/notes

Example:

```text
wiki-synthesis-select total=78 shown=5
score   entity_id                                      sources evidence title
91      topic:maintenance-aware-ai-evaluation           2       15       Maintenance-Aware AI Evaluation
88      topic:organizational-ai-readiness               2       16       Organizational AI Readiness
86      topic:provenance-tracking                       2       15       Provenance Tracking
84      topic:production-debt-in-ai-systems             2       15       Production Debt in AI Systems
80      tool:operator                                   2       28       Operator
```

With `--commands`, print copy-pasteable commands:

```bash
hatch run wiki-synthesis-workflow --entity topic:maintenance-aware-ai-evaluation --yes
hatch run wiki-synthesis-workflow --entity topic:organizational-ai-readiness --yes
```

With `--json`, emit a stable object:

```json
{
  "total_changed": 78,
  "shown": 5,
  "entries": [
    {
      "rank": 1,
      "score": 91,
      "entity_id": "topic:maintenance-aware-ai-evaluation",
      "category": "topic",
      "slug": "maintenance-aware-ai-evaluation",
      "title": "Maintenance-Aware AI Evaluation",
      "source_count": 2,
      "evidence_count": 15,
      "state": "new",
      "notes": ["role_relevant", "topic"]
    }
  ]
}
```

### Candidate Eligibility

Use the same base eligibility as `wiki-synthesis-plan --changed-only`.

Default behavior:

- include only `new` and `stale`
- skip single-source pages
- skip evidence-object categories as the planner already does
- do not include `signal`, `interview insight`, or implementation-study objects if they are not synthesis targets

Options:

```text
--graph-path PATH
--cache-dir PATH
--category CATEGORY
--entity ENTITY
--limit N
--include-single-source
--json
--commands
```

### Ranking Rules

Ranking must be deterministic and explainable.

Do not use an LLM for ranking.

Suggested initial scoring:

```text
score =
  category_weight
  + source_count_weight
  + evidence_count_weight
  + role_relevance_weight
  + stale_bonus
  - model_penalty
  - possible_duplicate_penalty
```

Suggested category weights:

```text
topic:    +30
how_to:   +28
tool:     +24
glossary: +22
model:    +10
trend:    +18
other:    +0
```

Suggested source/evidence weights:

```text
source_count_weight = min(source_count, 5) * 5
evidence_count_weight = min(evidence_count, 30)
```

Suggested role relevance weight:

Add points when title, slug, tags, or evidence tags include terms relevant to the
user's work as an EnBW AI expert building service chatbots/voicebots and AI
workflows:

```text
+25 for service automation / conversational AI / contact center / voice / chatbot
+20 for agents / workflows / orchestration / evaluation / governance / auditability
+15 for knowledge management / retrieval / provenance / context / PII / privacy
+10 for AI engineering / model routing / local inference / tool use
```

The relevance term list should live in code as a small constant first. Do not
create an elaborate ontology for this feature.

Suggested stale bonus:

```text
stale: +10
new:   +0
```

Suggested model penalty:

```text
category == "model": -15
```

Reason:

Model pages can be useful, but they age faster than concepts, workflows,
governance topics, and tool/practice pages.

### Duplicate Signals

The selector should not merge or suppress candidates automatically.

It may mark possible duplicates with a note and small penalty.

Initial duplicate heuristic:

- normalize titles/slugs
- remove stopwords like `ai`, `llm`, `agentic`, `agent`, `workflow`, `workflows`
- compare token overlap
- if overlap is very high, mark `possible_duplicate`

Example:

- `llm-assisted-knowledge-compilation`
- `llm-maintained-knowledge-compilation`

These should be marked as possible duplicates, not deleted and not merged.

Keep this heuristic intentionally conservative.

## Command 2: `wiki-synthesis-batch`

### Purpose

Execute a bounded batch of synthesis calls using the same selection logic.

This is the command that can later be used from a nightly cron job.

### Proposed Hatch Script

```toml
wiki-synthesis-batch = [
  "python -m src.wiki_synthesis.batch_cli {args}",
]
```

### Example Usage

Preview:

```bash
hatch run wiki-synthesis-batch --dry-run --limit 10
```

Real run:

```bash
hatch run wiki-synthesis-batch --limit 10 --between-calls 300 --yes
```

Category-limited run:

```bash
hatch run wiki-synthesis-batch --category topic --limit 20 --between-calls 300 --yes
```

Single entity:

```bash
hatch run wiki-synthesis-batch --entity topic:provenance-tracking --yes
```

### Required Safety Behavior

Real API calls must require `--yes`.

If neither `--dry-run` nor `--yes` is passed:

- exit with status `2`
- print a clear error

If `OPENAI_API_KEY` is missing for a real run:

- exit with status `2`
- do not write files

If `--limit < 1`:

- exit with status `2`

Default limit should be conservative:

```text
--limit 5
```

Reason:

This is safer for early automation than a large default. Cron can explicitly set
a larger limit later.

### Pause Behavior

Add:

```text
--between-calls SECONDS
```

Default:

```text
0
```

Behavior:

- pause only between actual API calls
- do not pause after the last item
- do not pause in dry-run mode
- emit progress before sleeping

Example progress line:

```text
waiting topic:provenance-tracking index=3 total=10 seconds=300
```

Implementation should be testable by injecting or monkeypatching sleep. Do not
make tests actually wait.

### Selection Behavior

The batch command should use the same ranking function as
`wiki-synthesis-select`.

Default behavior:

- select top ranked changed candidates
- process up to `--limit`
- skip single-source candidates unless `--include-single-source` is passed
- honor `--category`
- honor `--entity`

If `--entity` is passed, ranking does not matter; process that entity if it is
eligible.

### Execution Behavior

The batch command should reuse existing synthesis functions.

Preferred implementation:

- create shared selection helpers in a module such as `src/wiki_synthesis/selection.py`
- `wiki-synthesis-select` uses those helpers
- `wiki-synthesis-batch` uses those helpers
- batch execution can call existing lower-level synthesis/review functions

Avoid shelling out to `hatch run wiki-synthesis-workflow` for each entity.

Reason:

Shelling out would be slower, harder to test, and less reliable for audit
metadata.

### Provider Lifecycle

For spaced calls, prefer one provider per item or ensure the provider is cleanly
closed during long pauses.

Reason:

The user specifically wants a nightly job that does not keep a long OpenAI
connection open while sleeping for several minutes.

Acceptable simple initial design:

- create an `OpenAISynthesisProvider` for one item
- call one synthesis
- close it
- render preview
- sleep
- repeat

This is more important than micro-optimizing connection reuse.

### Failure Behavior

Default:

- stop on first failed synthesis
- write an audit report containing completed items and the failure
- return non-zero exit code

Add option:

```text
--continue-on-error
```

When passed:

- record failures
- continue with remaining selected candidates
- return non-zero if any failed

This option should exist, but cron should initially not use it.

### Audit Report

The batch command must write one audit report for real runs unless disabled.

Suggested path:

```text
state/synthesis_runs/<timestamp>-batch.json
```

The report should include:

- created_at
- options
- selected entries
- completed entries
- failed entries
- skipped entries, if any
- called count
- written count
- preview count
- dry_run
- elapsed_seconds
- remaining_changed_count after the batch, if easy to compute
- model
- token usage when available

Add:

```text
--no-audit-log
```

But default should write audit logs for real runs.

### Text Output

Human-readable output should show:

```text
wiki-synthesis-batch selected=10 called=10 written=10 failed=0 dry_run=False
run written new topic:provenance-tracking ...
waiting topic:next-item index=1 total=10 seconds=300
audit_report state/synthesis_runs/20260710T220000Z-batch.json
next hatch run wiki-synthesis-cache-lint
next hatch run wiki-render --dry-run
```

Dry-run should show selected entries without API calls:

```text
wiki-synthesis-batch selected=5 called=0 written=0 failed=0 dry_run=True
planned topic:maintenance-aware-ai-evaluation score=91
planned topic:organizational-ai-readiness score=88
```

### JSON Output

Add:

```text
--json
```

Output should be stable enough for future web UI consumption.

Suggested shape:

```json
{
  "dry_run": false,
  "selected": 10,
  "called": 10,
  "written": 10,
  "failed": 0,
  "reviews": 10,
  "audit_report_path": "state/synthesis_runs/20260710T220000Z-batch.json",
  "items": [
    {
      "entity_id": "topic:provenance-tracking",
      "state": "new",
      "action": "written",
      "score": 86,
      "cache_path": "state/synthesis/topic/provenance-tracking.json",
      "preview_path": "state/synthesis_previews/topic/provenance-tracking.md"
    }
  ],
  "failures": [],
  "next_actions": [
    "hatch run wiki-synthesis-cache-lint",
    "hatch run wiki-render --dry-run"
  ]
}
```

## Suggested Module Structure

```text
src/wiki_synthesis/
  selection.py
  select_cli.py
  batch.py
  batch_cli.py
```

Tests:

```text
tests/wiki_synthesis/test_selection.py
tests/wiki_synthesis/test_select_cli.py
tests/wiki_synthesis/test_batch.py
tests/wiki_synthesis/test_batch_cli.py
```

Keep implementation small. If a separate `batch.py` becomes too much, it is
acceptable to put most logic in `batch_cli.py` initially, but selection logic
should be reusable.

## Implementation Order

### Step 1: Selection Layer

Implement:

- candidate scoring
- candidate sorting
- text output
- JSON output
- command output
- tests
- Hatch script
- `src/AGENTS.md` docs section

This step must be read-only.

### Step 2: Batch Dry-Run

Implement:

- `wiki-synthesis-batch --dry-run`
- uses selection layer
- no provider needed
- no file writes
- text and JSON output
- tests
- Hatch script
- docs

### Step 3: Batch Real Run

Implement:

- `--yes`
- OpenAI provider creation
- one item at a time
- close provider between items when sleeping
- preview rendering
- audit report
- failure handling
- tests using fake provider

### Step 4: Pause Support

Implement:

- `--between-calls`
- test with monkeypatched sleep
- ensure no sleep after last item
- ensure no sleep in dry-run

This can be done during Step 3 if simple.

## Acceptance Criteria

### Selection

Running:

```bash
hatch run wiki-synthesis-select --limit 10
```

must:

- make no LLM calls
- write no files
- show ranked changed candidates
- include score and entity id

Running:

```bash
hatch run wiki-synthesis-select --json --limit 10
```

must print valid JSON to stdout.

Running:

```bash
hatch run wiki-synthesis-select --commands --limit 5
```

must print copy-pasteable `wiki-synthesis-workflow --entity ... --yes` commands.

### Batch Dry-Run

Running:

```bash
hatch run wiki-synthesis-batch --dry-run --limit 5
```

must:

- make no LLM calls
- write no files
- show which entries would be processed

### Batch Real Run

Running without `--yes` and without `--dry-run`:

```bash
hatch run wiki-synthesis-batch --limit 5
```

must fail safely with exit code `2`.

Running with `--yes`:

```bash
hatch run wiki-synthesis-batch --limit 2 --yes
```

must:

- call the provider for up to 2 selected entries
- write synthesis cache entries
- write review previews
- write one audit report
- print next recommended commands

Running with spacing:

```bash
hatch run wiki-synthesis-batch --limit 3 --between-calls 300 --yes
```

must:

- sleep between calls only
- not sleep after the final call
- close provider sessions appropriately

## Test Requirements

Run at minimum:

```bash
hatch run test:run tests/wiki_synthesis tests/test_hatch_scripts.py
hatch run lint:check
```

If code changes are broad, also run:

```bash
hatch run test:run
hatch run test:cov
```

Required unit tests:

- selection ranks role-relevant topics above lower-value models
- selection is deterministic for equal scores
- selection respects category filter
- selection respects entity filter
- selection marks possible duplicates without excluding them
- select CLI prints valid JSON
- select CLI prints command mode
- batch dry-run does not call provider
- batch real run requires `--yes`
- batch real run writes cache and preview with fake provider
- batch writes one audit report
- batch stops on first error by default
- batch can continue on error with `--continue-on-error`
- batch sleeps between calls but not after the last call
- Hatch scripts include the new commands

## Documentation Updates

Update `src/AGENTS.md` with a short section:

```markdown
## Wiki synthesis selection and batch automation

- Run `hatch run wiki-synthesis-select --limit 20` to inspect ranked changed synthesis candidates.
- This command is read-only and makes no LLM calls.
- Run `hatch run wiki-synthesis-batch --dry-run --limit 10` before real automation.
- Real batch execution requires `--yes`.
- Use `--between-calls 300` for slow nightly-style runs.
- The batch command writes synthesis cache files, previews, and an audit report, but does not run `wiki-render`.
- After a real batch, run `hatch run wiki-synthesis-cache-lint` and `hatch run wiki-render --dry-run`.
```

Optionally update `docs/current-system-status.md` only if it describes current
operations commands.

## Recommended Cron Shape Later

Do not implement this now, but design the batch command so this later command
sequence is possible:

```bash
cd /path/to/llm-wiki-karpathy
hatch run wiki-ops-status
hatch run wiki-synthesis-batch --limit 20 --between-calls 300 --yes
hatch run wiki-synthesis-cache-lint
hatch run wiki-render --dry-run
hatch run wiki-ops-status
```

At first, do not run real `wiki-render` automatically from cron.

Once trust is high, a later job may add:

```bash
hatch run wiki-render
```

Automatic commits are a separate future feature and must not be part of this
implementation.

## Open Design Choices

Use these defaults unless the user explicitly decides otherwise:

- Default batch limit: `5`
- Default select limit: `20`
- Default pause: `0` seconds
- Nightly suggested pause: `300` seconds
- Stop on first error by default
- Do not render automatically
- Do not commit automatically
- Do not run LLM-based duplicate merging
- Prefer topics/how-tos/tools/glossary over models

## Definition of Done

The feature is done when:

1. `wiki-synthesis-select` is implemented and tested.
2. `wiki-synthesis-batch --dry-run` is implemented and tested.
3. `wiki-synthesis-batch --yes` is implemented with fake-provider tests.
4. `--between-calls` is implemented and testable without real waiting.
5. Both commands are wired into Hatch.
6. `src/AGENTS.md` documents the new workflow.
7. Lint and targeted tests pass.
8. No real OpenAI call is made by tests.
9. No automatic render or commit is performed by the batch command.

