# Current System Status

Last reviewed: 2026-07-12

This document is a short orientation map for future sessions. It explains what is stable, what is partially built, and what should be handled next before adding more features.

## Executive Summary

The foundation is usable and internally consistent enough to continue. The wiki
can be regenerated deterministically from reviewed source artifacts, Stage 2
synthesis caches can be planned and rendered, and the current Obsidian output
passes the wiki-specific checks.

The project now has an external local operating mode:

- code repo: `llm-wiki-karpathy-source-access-spec`
- knowledge store: `llm-wiki-data`
- private generated vault: `llm-wiki-vault-private`

The copy-only migration has completed and the external paths are controlled by
local `config/wiki_paths.toml`. See
[`docs/external-operating-mode.md`](external-operating-mode.md).

## Current Architecture

The current pipeline has these layers in the external operating mode:

1. `<knowledge_root>/raw/readwise/`
   Local source exports. These are not committed to Git.

2. `<knowledge_root>/state/reviews/<source_id>/review.json`
   Human-reviewed extraction artifacts. These are the canonical source of truth for generated wiki content.

3. `hatch run wiki-render`
   Deterministically builds the generated Obsidian vault under `<vault_root>/wiki/` and writes:
   - `<knowledge_root>/state/wiki_render_manifest.json`
   - `<knowledge_root>/state/wiki_render_graph.json`

4. `<knowledge_root>/state/wiki_render_graph.json`
   Machine-readable graph export. This is the input for Stage 2 synthesis planning and execution.

5. `<knowledge_root>/state/synthesis/<category>/<slug>.json`
   Stage 2 synthesis cache entries. These are generated only by the synthesis workflow and are keyed by the current evidence hash.

6. `<vault_root>/wiki/`
   Generated Obsidian projection. Managed wiki pages should not be hand-edited because `wiki-render` can overwrite them.

## What Is Stable

- `wiki-render` is idempotent against the external knowledge store and private vault.
- `wiki-lint` passes.
- `wiki-synthesis-cache-lint` passes for all existing synthesis cache entries.
- `lint:check` passes (`ruff` and `ty`).
- `test:run` and `test:cov` pass on Python 3.12.
- Existing Stage 2 synthesis cache entries are fresh against the current graph.
- External `knowledge_root` and `vault_root` are configured locally through
  `config/wiki_paths.toml`.
- The first copy-only migration has been completed and verified.
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
   - The durable review artifacts live under
     `<knowledge_root>/state/reviews/<source_id>/review.json`.

3. Render Stage 1 and graph data.
   - `hatch run wiki-render`
   - This updates the generated Obsidian vault and `state/wiki_render_graph.json`.

4. Plan synthesis work.
   - `hatch run wiki-synthesis-plan --changed-only --limit 20`
   - Prefer small batches and high-value entities first.

5. Run targeted Stage 2 synthesis.
   - `hatch run wiki-synthesis-workflow --entity topic:example --yes`
   - This writes final cache files under
     `<knowledge_root>/state/synthesis/<category>/<slug>.json`.
   - It also writes preview and audit artifacts under configured temporary paths
     such as `<knowledge_root>/tmp/synthesis_previews/` and
     `<knowledge_root>/tmp/synthesis_runs/`.

6. Review previews.
   - Inspect `<knowledge_root>/tmp/synthesis_previews/<category>/<slug>.md`
     when previews are enabled.
   - If the page is poor, refresh only that entity instead of rerunning the whole batch.

7. Validate and render final wiki output.
   - `hatch run wiki-synthesis-cache-lint`
   - `hatch run wiki-render --dry-run`
   - If the dry-run would write files and the previews look good, run `hatch run wiki-render`.

8. Commit only durable artifacts.
   - In external operating mode, do not assume generated knowledge data belongs
     in the code repo.
   - Commit code, tests, docs, and config examples.
   - Commit local release artifacts only when there is a deliberate
     development/release reason.
   - Do not commit `config/wiki_paths.toml`; it is machine-specific.

## Current Check Results

Run on 2026-07-12 after copy-only migration:

```text
hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root
=> external roots active; raw/reviews/synthesis/graph/manifest/releases/wiki already external

hatch run wiki-render --dry-run --require-source-text
=> sources=360 pages=614 files=1264 written=0 unchanged=1264 pruned=0
=> source full text coverage available=358 missing=2 total=360 ratio=99.4%

hatch run wiki-synthesis-cache-lint
=> checked=124 ok=124 warnings=0 errors=0

hatch run wiki-synthesis-plan --changed-only --limit 20 --json
=> changed candidates=43, stale=0

hatch run lint:check
=> ruff ok, ty ok

hatch run wiki-lint
=> ok
```

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

- 124 synthesis cache entries total
- 124 fresh
- 0 stale
- 0 errors

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

### 3. External Store Backup

The external knowledge store is now the important data location. It is not yet
backed by a formal backup policy in this repo.

Maintenance rule:

- Do not delete old repo-local data until `llm-wiki-data` has a real backup.
- Prefer a later explicit backup slice over ad hoc manual copying.

### 4. Stage 2 Batch Size and Cost

There are still changed synthesis candidates. Running them all at once would create unnecessary API cost and review burden.

Recommended next step:

- Continue with small batches by category.
- Prefer high-value categories first: glossary, topics, how-to.
- Use `wiki-synthesis-plan --changed-only` before every batch.
- Review previews before rendering into `wiki/`.

## Recommended Next Work Sequence

1. Keep the external operating mode stable.
2. Add a copy-verification command that compares source and external stores by
   count and hash.
3. Decide and document backup strategy for `llm-wiki-data`.
4. Continue Stage 2 synthesis in small reviewed batches.
5. Before each batch, rerun:
   - `hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root`
   - `hatch run lint:check`
   - `hatch run test:run`
   - `hatch run wiki-render --dry-run --require-source-text`
   - `hatch run wiki-lint`
   - `hatch run wiki-synthesis-cache-lint --json`

## Current Judgment

Continue the project, but keep the next phase conservative. The external
knowledge store split is now real enough to operate, but not yet backed up or
fully automated. The next useful work is stabilization around verification,
backup, and small Stage 2 synthesis batches. Avoid deleting old in-repo data
until rollback and backup are boring.
