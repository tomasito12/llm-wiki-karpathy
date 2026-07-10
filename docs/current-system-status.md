# Current System Status

Last reviewed: 2026-07-10

This document is a short orientation map for future sessions. It explains what is stable, what is partially built, and what should be handled next before adding more features.

## Executive Summary

The foundation is usable and internally consistent enough to continue. The wiki can be regenerated deterministically from reviewed source artifacts, Stage 2 synthesis caches can be planned and rendered, and the current Obsidian output passes the wiki-specific checks.

The previous test-runner blocker has been fixed. Hatch now uses Python 3.12 for project environments, Pytest no longer crashes on `readline`, and the full test suite plus coverage run successfully.

## Current Architecture

The current pipeline has these layers:

1. `raw/readwise/`
   Local source exports. These are not committed to Git.

2. `state/reviews/<source_id>/review.json`
   Human-reviewed extraction artifacts. These are the canonical source of truth for generated wiki content.

3. `hatch run wiki-render`
   Deterministically builds the generated Obsidian vault under `wiki/` and writes:
   - `state/wiki_render_manifest.json`
   - `state/wiki_render_graph.json`

4. `state/wiki_render_graph.json`
   Machine-readable graph export. This is the input for Stage 2 synthesis planning and execution.

5. `state/synthesis/<category>/<slug>.json`
   Stage 2 synthesis cache entries. These are generated only by the synthesis workflow and are keyed by the current evidence hash.

6. `wiki/`
   Generated Obsidian projection. Managed wiki pages should not be hand-edited because `wiki-render` can overwrite them.

## What Is Stable

- `wiki-render` is idempotent on the current checked-in state.
- `wiki-lint` passes.
- `wiki-synthesis-cache-lint` passes for all existing synthesis cache entries.
- `lint:check` passes (`ruff` and `ty`).
- `test:run` and `test:cov` pass on Python 3.12.
- Existing Stage 2 synthesis cache entries are fresh against the current graph.
- Stage 2 input hashes now normalize tiny float representation differences, so render-only confidence formatting changes do not force unnecessary LLM resynthesis.
- `wiki-reset` tests no longer delete the real `state/wiki_render_manifest.json` when using temporary test paths.
- Related-page links are now generated from Stage 1 graph relationships instead of being empty placeholders.
- The README has been realigned with the current Readwise -> review -> render -> synthesis workflow and no longer describes the old manual ingest/page taxonomy as the active path.
- The long-term second-brain vision is documented in `docs/second-brain-vision.md`.
- The user's EnBW AI expert role and service-automation relevance profile are documented in the README, second-brain vision, ingestion philosophy, and code-agent command reference.

## Standard Operating Flow

Use this flow when new Readwise sources have been reviewed or when Stage 2
synthesis batches were created.

1. Sync or add sources.
   - `hatch run readwise-sync`
   - Do not edit files under `raw/` by hand.

2. Review/classify sources.
   - Use the dashboard or pre-analysis workflow.
   - The durable review artifacts live under `state/reviews/<source_id>/review.json`.

3. Render Stage 1 and graph data.
   - `hatch run wiki-render`
   - This updates the generated Obsidian vault and `state/wiki_render_graph.json`.

4. Plan synthesis work.
   - `hatch run wiki-synthesis-plan --changed-only --limit 20`
   - Prefer small batches and high-value entities first.

5. Run targeted Stage 2 synthesis.
   - `hatch run wiki-synthesis-workflow --entity topic:example --yes`
   - This writes final cache files under `state/synthesis/<category>/<slug>.json`.
   - It also writes preview and audit artifacts under `state/synthesis_previews/`
     and `state/synthesis_runs/`.

6. Review previews.
   - Inspect `state/synthesis_previews/<category>/<slug>.md`.
   - If the page is poor, refresh only that entity instead of rerunning the whole batch.

7. Validate and render final wiki output.
   - `hatch run wiki-synthesis-cache-lint`
   - `hatch run wiki-render --dry-run`
   - If the dry-run would write files and the previews look good, run `hatch run wiki-render`.

8. Commit only durable artifacts.
   - Commit final synthesis caches in `state/synthesis/`.
   - Commit generated wiki pages and `state/wiki_render_manifest.json` when they changed.
   - Do not commit `state/synthesis_previews/`, `state/synthesis_runs/`, or
     `state/synthesis_backups/` unless there is a deliberate review/audit reason.

## Current Check Results

Run on 2026-07-10:

```text
hatch run wiki-render --dry-run
=> sources=360 pages=614 files=1264 written=0 unchanged=1264 pruned=0

hatch run wiki-synthesis-cache-lint
=> checked=89 ok=89 warnings=0 errors=0

hatch run wiki-synthesis-plan --changed-only --limit 20 --json
=> new=83 stale=0 unchanged=84 skipped_single_source=447 skipped_evidence_object=275

hatch run lint:check
=> ruff ok, ty ok

hatch run test:run
=> 901 passed

hatch run test:cov
=> 901 passed, total coverage 75%
```

The earlier failure mode was fixed in this pass:

- Hatch previously selected Anaconda Python 3.11.4.
- The project now pins Hatch environments to Python 3.12.
- `hatch run python -c "import readline"` succeeds.
- Pytest starts normally and completes.

## Stage 2 Status

Stage 2 is partially implemented and usable in controlled batches.

Available commands:

- `hatch run wiki-synthesis-plan`
- `hatch run wiki-synthesis-doctor`
- `hatch run wiki-synthesis-prompt`
- `hatch run wiki-synthesis-run`
- `hatch run wiki-synthesis-review`
- `hatch run wiki-synthesis-cache-lint`
- `hatch run wiki-synthesis-indexes`
- `hatch run wiki-synthesis-workflow`

Current behavior:

- Multi-source knowledge pages are synthesis candidates.
- Single-source pages are skipped by default.
- Signals, interview insights, and implementation studies are treated as evidence objects, not synthesis targets.
- Existing synthesis cache entries render into the managed wiki during `wiki-render`.
- Missing synthesis cache entries fall back to Stage 1 pages.
- Stale synthesis cache entries are detected by evidence hash.

Current cache count:

- 13 glossary synthesis pages
- 8 how-to synthesis pages
- 11 model synthesis pages
- 16 tool synthesis pages
- 41 topic synthesis pages

## Main Risks

### 1. Keep the Test Environment Pinned

The project now explicitly pins Hatch environments to Python 3.12. Keep that pin unless the project Python requirement changes.

Maintenance rule:

- If tests crash before collection, first check `hatch run python --version`.
- Do not silently fall back to Anaconda Python 3.11.
- Recreate Hatch environments after changing Python constraints.

### 2. Documentation Drift

The largest README drift has been cleaned up. Remaining documentation risk is normal maintenance drift between README, `src/AGENTS.md`, `wiki/AGENTS.md`, and implementation details.

Maintenance rule:

- Keep root README as a high-level orientation.
- Treat `src/AGENTS.md` as the command reference.
- Treat `wiki/AGENTS.md` as the generated vault contract.
- When behavior changes, update the scoped instruction file first, then the README if the change affects normal operation.

### 3. Stage 2 Batch Size and Cost

There are currently 157 new multi-source synthesis candidates. Running them all at once would create unnecessary API cost and review burden.

Recommended next step:

- Continue with small batches by category.
- Prefer high-value categories first: glossary, topics, how-to.
- Use `wiki-synthesis-plan --changed-only` before every batch.
- Review previews before rendering into `wiki/`.

## Recommended Next Work Sequence

1. Continue Stage 2 synthesis in small reviewed batches.
2. Before each batch, rerun:
   - `hatch run lint:check`
   - `hatch run test:run`
   - `hatch run wiki-render --dry-run`
   - `hatch run wiki-lint`
   - `hatch run wiki-synthesis-cache-lint --json`
3. Only after Stage 2 is boring and repeatable, consider retrieval/API/team access features.

## Current Judgment

Continue the project, but keep the next phase conservative. The system is not collapsing under its own weight. The test environment is repaired and the top-level README now matches the current workflow. The next useful work is small Stage 2 synthesis batches. Avoid new architectural features until Stage 2 is boring and repeatable.
