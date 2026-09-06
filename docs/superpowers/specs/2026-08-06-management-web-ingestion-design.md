# Management Web Ingestion Design

## Goal

Add Readwise source synchronization and bounded ingest pre-analysis to the
management dashboard without adding controls to the Review Workspace or making
the Pipeline Cockpit visually dense.

## Information architecture

The global navigation remains `Review | Pipeline`. Pipeline receives three
focused internal stages:

1. `Intake & Analysis`
2. `Build Wiki`
3. `Advanced`

`Intake & Analysis` is the default stage. The existing status summary remains
visible across Pipeline. `Build Wiki` contains the guided Update Wiki workflow.
The existing low-level operation cards and run details remain under `Advanced`.

## Intake operations

### Sync Readwise

Expose the existing `src.readwise` CLI through the allowlisted management
operation runner. It performs the normal incremental sync, writes new paired
HTML/Markdown exports and index state, and keeps the CLI's default automatic
near-duplicate cleanup. The UI uses one `Sync new documents…` action followed
by an explicit confirmation explaining that files and index state are written
and shorter near-duplicates may be removed.

The first slice does not add a separate dry-run step, interactive duplicate
selection, watermark reset, index bootstrap, or custom similarity threshold.

### Pre-analyze documents

Expose `src.ingest_batch.cli` through the same operation runner. Parameters:

- `limit`: integer from 1 through 100, default 10
- `between_articles`: seconds from 0 through 3600, default 300

The operation keeps the CLI's default `skip-existing` behavior. It writes
review artifacts, may issue OpenAI calls, and therefore requires explicit
confirmation. The confirmation displays the selected maximum document count
and pause.

## Runtime and safety

Both actions reuse `OpsRunManager` and `ManagementRunCoordinator`. Only one
management operation or guided workflow can run at a time. Existing polling,
run reports, stdout/stderr capture, and recent-run history remain canonical.

Operation commands must use the existing path-config propagation. Tokens remain
server-side and are never returned to the frontend. Missing tokens and CLI
safety failures appear as failed run output.

## Result presentation

The Intake stage shows two restrained cards and the latest result for each.
Readwise output summarizes examined, exported, skipped, and dedupe actions.
Pre-analysis output shows progress plus selected, processed, skipped, failed,
and elapsed results. Full stdout/stderr remains behind technical details.

The Review Workspace is not changed. Newly produced review artifacts appear
through its normal queue refresh/loading behavior.

## Testing

Backend tests cover operation metadata, parameter validation, exact command
construction, confirmation, and shared concurrency. Frontend tests cover stage
navigation, defaults, confirmation content, API payloads, busy state, and result
rendering. Existing Python and frontend suites must remain green.
