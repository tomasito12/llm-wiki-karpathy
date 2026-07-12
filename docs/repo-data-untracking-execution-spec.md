# Technical Specification: Repo Data Untracking Execution

Last updated: 2026-07-12

This specification defines the execution step after the read-only old repo data
retirement plan.

It is intended for an implementation agent that has no prior chat context.

## Purpose

The code repository still Git-tracks historical repo-local knowledge and vault
data, even though the system now operates against external roots:

- external knowledge store:
  `/Users/plischke/Desktop/Private Development/llm-wiki-data`
- external private Obsidian vault:
  `/Users/plischke/Desktop/Private Development/llm-wiki-vault-private`

The goal of this slice is to remove old repo-local knowledge/vault data from
Git tracking without deleting the files from disk.

The execution must use `git rm --cached`, never `rm`.

## Strict Safety Boundary

This slice may:

- compute an execution plan from the existing retirement plan
- update `.gitignore`
- run `git rm --cached` for approved `untrack_later` files only
- write an audit report
- commit the resulting Git index changes only if the operator does that
  manually or explicitly asks for it

This slice must not:

- delete local files
- delete external knowledge-store files
- delete external vault files
- call an LLM
- run synthesis
- run render automatically
- push to GitHub
- modify external data
- untrack files classified as `keep_tracked`, `manual_review`,
  `keep_untracked_local_config`, `ignore_rule_needed`, or `not_managed`

## Why A Separate Command Is Acceptable

The user prefers not to add unnecessary Hatch commands. In this case a separate
execution command is justified because `wiki-ops-status` should stay read-only.

Recommended command:

```bash
hatch run wiki-retire-repo-data --dry-run
hatch run wiki-retire-repo-data --yes
```

Do not add write behavior to `wiki-ops-status`.

## Preconditions

The command must block real execution unless all required preconditions pass:

1. Retirement plan can be built.
2. `manual_review` count is zero.
3. External knowledge root is configured and exists.
4. External vault root is configured and exists.
5. Latest release verification has no `error` status.
6. Git tracked-file inventory succeeds.
7. Git working tree has no unrelated changes.
8. `.gitignore` can be updated or already contains the required patterns.
9. The candidate list is non-empty.

Warnings that may remain non-blocking:

- latest release manifest status is `warning` only because temporary artifacts
  exist
- temporary artifacts exist

The command should make those warnings visible but not block if all areas verify
as `ok`.

## Candidate Source

Use `build_retirement_plan(paths)` from `src/wiki_ops/retirement_plan.py`.

Execution candidates are exactly:

```text
file.proposed_action == "untrack_later"
```

The candidate list must be sorted by path and written to the audit report.

Never infer candidates by broad globbing directly in the execution command.
The read-only retirement plan is the single source of truth for what may be
untracked.

## Required Ignore Patterns

Ensure `.gitignore` contains these patterns before or during execution:

```gitignore
# Local path configuration
config/wiki_paths.toml

# Externalized knowledge data and generated vault content
raw/**
state/reviews/
state/synthesis/
state/wiki_render_graph.json
state/wiki_render_manifest.json
state/releases/
state/synthesis_previews/
state/synthesis_runs/
state/synthesis_backups/
state/synthesis_prompts/
state/ingest_batches/
state/ingest_manifest.json
wiki/
sources/
indexes/
```

Do not remove existing ignore rules. Only append missing rules in a clearly
named section if they are absent.

Current `.gitignore` may already include some patterns such as `raw/**`; avoid
duplicates.

## Execution Design

Add a focused module:

```text
src/wiki_ops/retire_repo_data.py
```

Suggested dataclasses:

- `RepoDataUntrackingCandidate`
- `RepoDataUntrackingPreflight`
- `RepoDataUntrackingReport`

Responsibilities:

- build the retirement plan
- validate preconditions
- collect candidates from `untrack_later`
- check `.gitignore` coverage
- support dry-run and real-run
- run `git rm --cached -- <paths>` in chunks
- write an audit report for real runs

## CLI

Add a Hatch script:

```toml
wiki-retire-repo-data = "python -m src.wiki_ops.retire_repo_data_cli"
```

CLI options:

```text
--dry-run          default behavior; print plan, no writes
--yes              required for real execution
--json             print machine-readable report
--audit-dir PATH   optional override, default state/retirement_runs
--chunk-size N     optional, default 200
```

Invalid combinations:

- `--dry-run --yes` should exit 2
- real execution without `--yes` should exit 2

Default invocation should be dry-run:

```bash
hatch run wiki-retire-repo-data
```

## Git Execution

For real execution:

1. Rebuild the retirement plan.
2. Validate preconditions.
3. Update `.gitignore` with missing required patterns.
4. Run `git rm --cached -- <candidate paths>` in chunks.
5. Write an audit report to:

```text
state/retirement_runs/<timestamp>.json
```

The audit report path is intentionally repo-local operational state for this
transition. It may later move to the external knowledge store.

Use subprocess list arguments, not shell strings:

```python
subprocess.run(["git", "rm", "--cached", "--", *chunk], ...)
```

Do not pass paths through a shell.

## Handling Missing Files

If a tracked candidate file no longer exists in the worktree but is still
tracked by Git, `git rm --cached` should still be able to remove it from the
index.

The execution should not require candidate files to exist on disk. It should
only require that they are still tracked by Git.

## Handling Large Candidate Lists

There may be around 2,000 candidates. Chunk `git rm --cached` calls to avoid
command-line length issues.

Default chunk size: 200.

## Output

Dry-run text output should look like:

```text
Repo Data Untracking
- mode: dry-run
- candidates: 1990
- gitignore additions: 7
- readiness: ready

Largest areas
- state/reviews: 378 files, 18.9 MB
- wiki: 1294 files, 9.5 MB

No files were untracked.
```

Real-run text output should look like:

```text
Repo Data Untracking
- mode: real
- candidates: 1990
- git rm --cached chunks: 10
- gitignore updated: yes
- audit report: state/retirement_runs/20260712T160000Z.json

Files were removed from Git tracking only. Local files were not deleted.
```

## JSON Report

The JSON report should include:

```json
{
  "schema_version": 1,
  "mode": "dry_run",
  "readiness": "ready",
  "candidate_count": 1990,
  "gitignore_additions": [],
  "chunks_planned": 10,
  "chunks_executed": 0,
  "files_untracked": [],
  "local_files_deleted": 0,
  "external_files_touched": 0,
  "preconditions": [],
  "candidates": []
}
```

For real runs, include all untracked file paths.

## Tests

Add tests for:

- dry-run is default and performs no writes
- real-run requires `--yes`
- `--dry-run --yes` exits 2
- only `untrack_later` files become candidates
- `manual_review` blocks execution
- tracked local config blocks execution
- missing external roots block execution
- `.gitignore` missing patterns are detected in dry-run
- `.gitignore` missing patterns are appended in real-run
- `git rm --cached` is called with list arguments and chunks
- candidate files are not deleted from disk
- candidate files that are missing on disk can still be untracked
- JSON output is valid and deterministic

Use temporary Git repositories in tests. Do not run against the developer's real
repository in unit tests.

## Validation Commands

Run:

```bash
hatch run lint:check
hatch run lint:format --check
hatch run test:run tests/wiki_ops/test_retirement_plan.py tests/wiki_ops/test_status_cli_retirement.py
hatch run test:run tests/wiki_ops/test_retire_repo_data.py tests/wiki_ops/test_retire_repo_data_cli.py
hatch run wiki-retire-repo-data --dry-run
```

If Ruff cache cannot be written in the worktree, run with:

```bash
RUFF_CACHE_DIR=/tmp/llm-wiki-ruff-cache hatch run lint:check
RUFF_CACHE_DIR=/tmp/llm-wiki-ruff-cache hatch run lint:format --check
```

## Definition of Done

This slice is complete when:

- `wiki-retire-repo-data` exists
- default mode is dry-run
- real mode requires `--yes`
- execution uses the retirement plan as candidate source
- no local files are deleted
- no external files are touched
- `.gitignore` receives only missing required rules
- a real run writes an audit report
- tests cover safety and candidate selection
- dry-run output clearly says no files were untracked

## Operator Flow After Implementation

Recommended flow:

```bash
hatch run wiki-ops-status --retirement-plan
hatch run wiki-retire-repo-data --dry-run
hatch run wiki-retire-repo-data --yes
git status --short
hatch run wiki-ops-status --retirement-plan
hatch run wiki-render --dry-run --require-source-text
hatch run wiki-synthesis-cache-lint
```

After reviewing the Git diff, commit the `.gitignore` update and Git index
removals together.
