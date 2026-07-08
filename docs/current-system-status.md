# Current System Status

Last reviewed: 2026-07-08

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
- The long-term second-brain vision is documented in `docs/second-brain-vision.md`.

## Current Check Results

Run on 2026-07-08:

```text
hatch run wiki-render --dry-run
=> sources=360 pages=614 files=1264 written=0 unchanged=1264 pruned=0

hatch run wiki-lint
=> ok

hatch run wiki-synthesis-cache-lint --json
=> checked=10 ok=10 warnings=0 errors=0

hatch run wiki-synthesis-plan --changed-only --limit 20 --json
=> new=157 stale=0 unchanged=10 skipped_single_source=447 skipped_evidence_object=275

hatch run lint:check
=> ruff ok, ty ok

hatch run test:run
=> 892 passed before the final hash regression test was added

hatch run test:cov
=> 893 passed, total coverage 75%
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

- 7 glossary synthesis pages
- 3 topic synthesis pages

## Main Risks

### 1. Keep the Test Environment Pinned

The project now explicitly pins Hatch environments to Python 3.12. Keep that pin unless the project Python requirement changes.

Maintenance rule:

- If tests crash before collection, first check `hatch run python --version`.
- Do not silently fall back to Anaconda Python 3.11.
- Recreate Hatch environments after changing Python constraints.

### 2. Documentation Drift

Some top-level README sections still describe the older manual ingest workflow. The scoped `src/AGENTS.md` and `wiki/AGENTS.md` files are closer to the real current system, but `wiki/AGENTS.md` also needed Stage 2 wording updates.

Recommended next step:

- Keep root README as a high-level orientation.
- Treat `src/AGENTS.md` as the command reference.
- Treat `wiki/AGENTS.md` as the generated vault contract.
- Gradually remove or clearly label old manual-ingest README sections.

### 3. Stage 2 Batch Size and Cost

There are currently 157 new multi-source synthesis candidates. Running them all at once would create unnecessary API cost and review burden.

Recommended next step:

- Continue with small batches by category.
- Prefer high-value categories first: glossary, topics, how-to.
- Use `wiki-synthesis-plan --changed-only` before every batch.
- Review previews before rendering into `wiki/`.

## Recommended Next Work Sequence

1. Clean up README drift so future sessions do not follow the old manual workflow.
2. Continue Stage 2 synthesis in small reviewed batches.
3. Before each batch, rerun:
   - `hatch run lint:check`
   - `hatch run test:run`
   - `hatch run wiki-render --dry-run`
   - `hatch run wiki-lint`
   - `hatch run wiki-synthesis-cache-lint --json`
4. Only after Stage 2 is boring and repeatable, consider retrieval/API/team access features.

## Current Judgment

Continue the project, but keep the next phase conservative. The system is not collapsing under its own weight. The test environment is now repaired, and the next useful work is documentation alignment plus small synthesis batches. Avoid new architectural features until Stage 2 is boring and repeatable.
