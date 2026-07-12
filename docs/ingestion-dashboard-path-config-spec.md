# Technical Specification: Ingestion and Dashboard Path Configuration

Last updated: 2026-07-12

This specification defines the next migration step after externalizing the
knowledge store and private vault.

It is intended for an implementation agent that has no prior chat context.

## Background

The project has been split into three operational areas:

```text
code repo:
  /Users/plischke/Desktop/Private Development/llm-wiki-karpathy-source-access-spec

external knowledge store:
  /Users/plischke/Desktop/Private Development/llm-wiki-data

external private vault:
  /Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

The code repo is Git-versioned and pushed to GitHub. The external knowledge
store and private vault are currently plain local directories, not Git repos.

The local path config is:

```text
config/wiki_paths.toml
```

It is intentionally gitignored. The committed template is:

```text
config/wiki_paths.example.toml
```

Render, synthesis, cleanup, release, and ops-status commands already use the
central path configuration. The dashboard and ingestion commands still contain
repo-local defaults in several places, for example:

```text
raw/readwise
state/reviews
wiki
```

This is now risky. If the user runs the dashboard or unattended ingestion, new
raw exports or review artifacts may be written into the code repo instead of
the external knowledge store.

## Goal

Make ingestion and dashboard workflows use the same `WikiPaths` configuration
as render/synthesis/status.

After this change, new data should land here by default:

```text
raw Readwise exports:
  /Users/plischke/Desktop/Private Development/llm-wiki-data/raw/readwise

review artifacts:
  /Users/plischke/Desktop/Private Development/llm-wiki-data/state/reviews

generated wiki context used by ingestion:
  /Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki
```

The code repo must not silently receive new ingestion data.

## Non-Goals

Do not implement:

- a new web UI framework
- a redesigned dashboard
- automatic Git versioning for the external knowledge store
- automatic backups
- server deployment
- cron jobs
- LLM prompt changes
- source/vault cleanup
- deletion of repo-local ignored files

This slice is only about path correctness for ingestion and dashboard workflows.

## Scope

Update at least these areas:

```text
src/dashboard/app.py
src/dashboard/preanalyze_ui.py
src/dashboard/readwise_sync_ui.py
src/ingest_batch/cli.py
src/ingest_queue/cli.py
src/readwise/cli.py
src/readwise/dedupe_cli.py
src/readwise/rebuild.py
```

Also inspect these modules for path assumptions and update only if needed:

```text
src/wiki_reset/cli.py
src/wiki_reset/reset.py
src/ingest_review/feedback_store.py
src/pipeline/ingest_manifest.py
```

Do not broaden the change into unrelated refactoring.

## Existing Path API

Use the existing path configuration APIs:

```python
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    resolve_cli_path,
)
from src.wiki_paths.config import WikiPaths, load_wiki_paths
```

Current behavior:

- `config/wiki_paths.toml` is loaded automatically when present.
- `LLM_WIKI_PATHS_CONFIG` can override the config path.
- CLI commands can support `--paths-config`.
- If no config exists, defaults remain repo-local for backward compatibility.

Keep this fallback behavior. Do not make path config mandatory globally.

## Dashboard Requirements

The Streamlit dashboard entry point is:

```text
src/dashboard/app.py
```

Current problem:

```python
raw_dir = root / "raw" / "readwise"
wiki_root = root / "wiki"
reviews_root = root / "state" / "reviews"
```

Required behavior:

1. Load `WikiPaths` at dashboard startup.
2. Use configured defaults in sidebar fields:

   ```text
   raw_dir      -> paths.raw_dir
   wiki_root    -> paths.wiki_dir
   reviews_root -> paths.reviews_dir
   ```

3. Show a clear sidebar caption with:

   ```text
   Code repo: <repo_root>
   Knowledge root: <knowledge_root>
   Vault root: <vault_root>
   Path config: <loaded config path or "repo-local defaults">
   ```

4. Preserve manual text input overrides for now, because they are useful for
   emergency debugging.
5. Add a small warning if any selected ingestion path points inside the code
   repo while an external `knowledge_root` or `vault_root` is configured.

Suggested warning:

```text
Warning: selected ingestion paths point inside the code repo. This may recreate
repo-local data that has been externalized.
```

Do not use custom CSS for this slice. Follow existing Streamlit style.

## Dashboard Pre-Analyze Sidebar

`render_preanalyze_sidebar()` already receives:

```python
raw_dir
reviews_root
wiki_root
```

Keep that shape. The caller should pass configured paths from `WikiPaths`.

Ensure the background command receives explicit paths so it cannot fall back to
repo-local defaults.

If it shells out to `hatch run ingest-preanalyze`, include:

```bash
--raw-dir <paths.raw_dir>
--reviews-dir <paths.reviews_dir>
--wiki-root <paths.wiki_dir>
```

Also pass `--paths-config` if the new CLI supports it.

## Readwise Sync Sidebar

`render_readwise_sync_sidebar()` receives:

```python
output_dir
```

Ensure the dashboard passes:

```python
paths.raw_dir
```

The Readwise sync command itself should also support configured defaults.

## `ingest-preanalyze` CLI Requirements

File:

```text
src/ingest_batch/cli.py
```

Add:

```text
--paths-config
```

Use `load_paths_for_cli(args)` to set defaults:

```text
--raw-dir     default: paths.raw_dir
--reviews-dir default: paths.reviews_dir
--wiki-root   default: paths.wiki_dir
```

Keep explicit CLI path flags as overrides.

Update help text from repo-local defaults to configured defaults, for example:

```text
Readwise export directory (default: configured raw_dir)
```

The command should still work without `config/wiki_paths.toml`.

## Ingest Queue CLI Requirements

File:

```text
src/ingest_queue/cli.py
```

Add:

```text
--paths-config
```

Use configured defaults:

```text
raw_dir     -> paths.raw_dir
reviews_dir -> paths.reviews_dir
```

Explicit `--raw-dir` and `--reviews-dir` should continue to override config.

## Readwise Sync CLI Requirements

File:

```text
src/readwise/cli.py
```

Add:

```text
--paths-config
```

Use configured default:

```text
--output-dir -> paths.raw_dir
```

Preserve existing explicit `--output-dir` behavior.

The command should continue to load `.env` from the code repo for
`READWISE_TOKEN` / `READWISE_API_TOKEN`.

## Readwise Dedupe CLI Requirements

File:

```text
src/readwise/dedupe_cli.py
```

Add:

```text
--paths-config
```

Use configured default:

```text
--raw-dir -> paths.raw_dir
```

This matters because dedupe can delete duplicate raw exports. It must operate
on the external raw store by default, not stale repo-local data.

## Readwise Rebuild CLI Requirements

File:

```text
src/readwise/rebuild.py
```

Add:

```text
--paths-config
```

Use configured defaults:

```text
--raw-dir -> paths.raw_dir
--index   -> paths.knowledge_root / "state" / "readwise_library.json"
```

If a dedicated readwise library path is later added to `WikiPaths`, use it.
For this slice, deriving it from `knowledge_root` is acceptable.

## Wiki Reset Caution

`wiki-reset` can clear review artifacts and wiki output. It still has repo-local
defaults in some places.

For this slice, either:

1. update `wiki-reset` to use `WikiPaths`, or
2. explicitly leave it unchanged but add a warning in this spec's follow-up
   notes and tests proving ingestion/dashboard paths are fixed.

Preferred: update `wiki-reset` only if it is small and low risk. Do not let it
expand the slice too much.

## Feedback Store and Legacy Ingest Manifest

These remain special:

```text
state/review_feedback.sqlite
state/ingest_manifest.json
```

Current architecture decision:

- `review_feedback.sqlite` is local operational feedback and should eventually
  move to the external knowledge store or be explicitly documented as local.
- `ingest_manifest.json` is legacy/optional and not active in the current
  review -> render workflow.

Do not redesign these in this slice unless required by tests.

If touched, prefer:

```text
review_feedback.sqlite -> paths.knowledge_root / "state" / "review_feedback.sqlite"
ingest_manifest.json   -> paths.knowledge_root / "state" / "ingest_manifest.json"
```

## Status Visibility

After implementation, the dashboard should make it obvious where data will be
written.

Minimum acceptable visibility:

- sidebar shows code repo, knowledge root, vault root
- raw/reviews/wiki path inputs default to configured external paths
- warning if selected paths point into the code repo

Do not redesign the dashboard UI in this slice.

## Tests

Add or update tests for:

### Path Loading

- dashboard helper loads `WikiPaths` from `config/wiki_paths.toml`
- fallback still works without config
- env var `LLM_WIKI_PATHS_CONFIG` is respected if existing tests cover this
  elsewhere, do not duplicate deeply

### CLI Defaults

For each updated CLI:

- no explicit path flags + config file -> uses configured external paths
- explicit path flags override configured paths
- no config file -> keeps repo-local defaults
- invalid explicit `--paths-config` exits 2 or raises existing
  `WikiPathsConfigError` handling path

### Safety

- dashboard default `raw_dir` is `paths.raw_dir`, not `repo/raw/readwise`
- dashboard default `reviews_root` is `paths.reviews_dir`, not
  `repo/state/reviews`
- dashboard default `wiki_root` is `paths.wiki_dir`, not `repo/wiki`
- background preanalysis command includes explicit raw/reviews/wiki paths
- Readwise sync sidebar receives configured raw path

### Regression

- existing render/synthesis/status tests remain green
- existing dashboard behavior still loads tag taxonomies from the code repo
  `config/` directory

## Validation Commands

Run:

```bash
hatch run lint:check
hatch run lint:format --check
hatch run test:run
hatch run wiki-ops-status
hatch run ingest-preanalyze --limit 1 --skip-existing --paths-config config/wiki_paths.toml
hatch run ingest-queue --paths-config config/wiki_paths.toml
hatch run readwise-dedupe --dry-run --paths-config config/wiki_paths.toml
```

If a command would call an external API, use its dry-run mode or only validate
argument parsing.

If Ruff cannot write its cache in this worktree, use:

```bash
RUFF_CACHE_DIR=/tmp/llm-wiki-ruff-cache hatch run lint:check
RUFF_CACHE_DIR=/tmp/llm-wiki-ruff-cache hatch run lint:format --check
```

## Definition of Done

This slice is complete when:

- dashboard defaults point to configured external paths
- `ingest-preanalyze` uses configured external paths by default
- ingest queue uses configured external paths by default
- Readwise sync writes to configured external raw dir by default
- Readwise dedupe scans/deletes only in configured raw dir by default
- Readwise rebuild reads/writes configured external locations by default
- explicit CLI path overrides still work
- no command silently recreates repo-local `raw/readwise`, `state/reviews`, or
  `wiki` when `config/wiki_paths.toml` exists
- tests cover the new path behavior
- no LLM calls are required for validation

## Operator Check After Merge

After implementation and commit, run:

```bash
hatch run wiki-ops-status
hatch run wiki-render --dry-run --require-source-text
hatch run ingest-queue
```

Then open the dashboard:

```bash
hatch run dashboard
```

Confirm in the sidebar:

```text
Raw readwise dir:
  /Users/plischke/Desktop/Private Development/llm-wiki-data/raw/readwise

Reviews state dir:
  /Users/plischke/Desktop/Private Development/llm-wiki-data/state/reviews

Wiki root:
  /Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki
```

Do not run real Readwise sync or real LLM preanalysis unless the user explicitly
approves the API/network call.

## Follow-Up After This Slice

Once ingestion/dashboard paths are fixed, the next architecture decision is the
backup/versioning model for:

```text
/Users/plischke/Desktop/Private Development/llm-wiki-data
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

Open questions for that later step:

- Should the knowledge store become its own private Git repo?
- Should the private vault become its own private Git repo?
- Should large raw exports be backed up by filesystem snapshots instead of Git?
- Should successful ingestion/synthesis/render runs create release manifests
  automatically?
- Should the server pull code only, or code plus data snapshots?
