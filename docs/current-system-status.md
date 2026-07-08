# Current System Status

Last reviewed: 2026-07-08

This document is a short orientation map for future sessions. It explains what is stable, what is partially built, and what should be handled next before adding more features.

## Executive Summary

The foundation is usable and internally consistent enough to continue. The wiki can be regenerated deterministically from reviewed source artifacts, Stage 2 synthesis caches can be planned and rendered, and the current Obsidian output passes the wiki-specific checks.

The main instability is not the wiki pipeline itself. The Python test runner currently crashes before test collection because the Hatch environment uses Python 3.11.4 even though the project declares Python `>=3.12,<3.13`, and importing `readline` exits with code `245`. This should be treated as an environment/tooling issue and fixed before relying on the full test suite again.

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
- Existing Stage 2 synthesis cache entries are fresh against the current graph.
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
=> exits 245 before useful output
```

Targeted Pytest runs with `python -X faulthandler -m pytest` also crash before test collection. The stack trace points into Pytest startup/capture and importing `readline`. A direct `hatch run python -c "import readline"` also exits with code `245`.

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

### 1. Test Environment Is Not Trustworthy

The project declares Python `>=3.12,<3.13`, but Hatch currently uses Python 3.11.4. This likely explains the Pytest/readline crash.

Recommended next step:

1. Install or expose Python 3.12 locally.
2. Recreate Hatch environments.
3. Rerun `hatch run test:run` and `hatch run test:cov`.

Do not interpret the current Pytest crash as a product regression until the Python environment is corrected.

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

1. Fix Python/Hatch test environment.
2. Rerun full checks:
   - `hatch run lint:check`
   - `hatch run test:run`
   - `hatch run wiki-render --dry-run`
   - `hatch run wiki-lint`
   - `hatch run wiki-synthesis-cache-lint --json`
3. Clean up README drift so future sessions do not follow the old manual workflow.
4. Continue Stage 2 synthesis in small reviewed batches.
5. Only after Stage 2 is boring and repeatable, consider retrieval/API/team access features.

## Current Judgment

Continue the project, but keep the next phase conservative. The system is not collapsing under its own weight, but it needs boring maintenance now: test environment repair, documentation alignment, and small synthesis batches. Avoid new architectural features until those are done.
