# Technical Specification: Old Repo Data Retirement

Last updated: 2026-07-12

This specification defines the next migration step after introducing external
path configuration, release manifests, release verification, and temporary
artifact cleanup.

It is intended for an implementation agent that has no prior chat context.

## Background

The project is moving from a single mixed repository toward a cleaner operating
model:

- the code repository contains Python code, tests, documentation, command-line
  wiring, and configuration templates
- the external knowledge store contains raw sources, review artifacts,
  synthesis cache files, render graph/manifest files, release manifests, and
  temporary operational artifacts
- the external private Obsidian vault contains generated wiki pages and full
  source pages

The current local operating paths are expected to look like this:

```text
code repo:
  /Users/plischke/Desktop/Private Development/llm-wiki-karpathy

external knowledge store:
  /Users/plischke/Desktop/Private Development/llm-wiki-data

external private vault:
  /Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

The code repository should eventually stop versioning long-lived knowledge data
such as generated wiki pages, review artifacts, synthesis cache files, and
render artifacts. Those files belong to the external knowledge store or vault.

However, this must be done carefully. The old repo-local data should not be
deleted in this step. The first implementation slice is a read-only retirement
plan that shows exactly what is still tracked in Git, why it should stay or
move out of Git, and what later action would be safe.

## User Goals

The user wants:

- a maintainable product-like structure
- clear ownership of every data directory
- no duplicated permanent data structures
- no accidental loss of raw sources, reviews, synthesis cache files, or wiki
  pages
- reliable rollback and verification before any destructive cleanup
- fewer confusing uncommitted generated files in the code repository
- direct Obsidian and agent access to full source texts through the external
  private vault

## Non-Goals

This implementation slice must not:

- delete local files
- delete external knowledge-store or vault files
- call an LLM
- run synthesis
- run render automatically
- create a GitHub repository
- push to GitHub
- change the backup provider
- move private notes or meeting notes
- implement server deployment

This slice should be read-only, except for code/tests/docs changes that
implement the inventory feature itself.

## Existing System Capabilities

Assume the repository already has or is expected to have these capabilities:

- configurable paths through `config/wiki_paths.toml`
- a gitignored local path config and a committed example config
- `wiki-ops-status` for overall state reporting
- retention inventory for canonical/generated/temporary data
- release manifest creation
- release verification through `wiki-ops-status --verify-release latest`
- temporary artifact cleanup guarded by a release manifest
- migration-plan reporting for external knowledge/vault roots

If some of these are not present in the local branch, implement this slice so it
integrates with the closest existing modules rather than inventing a parallel
system.

## Required Preconditions Before Any Later Untracking

The retirement plan should report these preconditions. It should not execute
them automatically.

Before any future `git rm --cached` action is allowed, the operator should have
run:

```bash
hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root
hatch run wiki-ops-status --verify-release latest
hatch run wiki-render --dry-run --require-source-text
hatch run wiki-synthesis-cache-lint
hatch run wiki-lint
git status --short
```

Expected readiness:

- external knowledge root is configured and exists
- external vault root is configured and exists
- latest release manifest verifies successfully
- render dry-run reports no required writes
- source-text coverage is acceptable
- synthesis cache has no errors
- wiki lint is clean
- code repo has no unrelated dirty changes

The user has also created a one-time iCloud migration safety backup. Do not
hard-code this path in production logic, but it is useful context for operators:

```text
~/Library/Mobile Documents/com~apple~CloudDocs/LLM Wiki Backups/20260712T145527Z-migration-backup
```

## Data Ownership Rules

The retirement plan must classify tracked files into explicit ownership
classes.

### Keep Tracked In Code Repo

These files should remain Git-tracked in the code repository:

```text
src/**
tests/**
docs/**
config/*.example.toml
pyproject.toml
README.md
AGENTS.md
.gitignore
```

Also keep intentionally small test fixtures under:

```text
tests/fixtures/**
```

### Local Config, Never Tracked

These files may exist locally but should not be tracked:

```text
config/wiki_paths.toml
.env
.env.*
```

### External Knowledge Store, Not Code Repo

These repo-local paths are historical knowledge data. If they are tracked in the
code repository, the retirement plan should mark them as `untrack_later`, not
delete:

```text
raw/readwise/**
state/reviews/**
state/synthesis/**
state/wiki_render_graph.json
state/wiki_render_manifest.json
state/releases/**
```

### External Private Vault, Not Code Repo

These repo-local generated vault paths should also be marked as `untrack_later`
if tracked:

```text
wiki/**
sources/**
indexes/**
```

Depending on the current project layout, source pages may still live under
`wiki/sources/**` instead of top-level `sources/**`. The implementation should
classify both patterns correctly.

### Temporary Artifacts

These repo-local temporary artifacts should not be tracked. If tracked, mark
them as `untrack_later`; if untracked, they are candidates for normal temporary
cleanup policy, not this retirement slice.

```text
state/synthesis_previews/**
state/synthesis_runs/**
state/synthesis_backups/**
state/synthesis_prompts/**
state/ingest_batches/**
```

Important: `state/synthesis_runs/**` contains audit reports. Do not delete
them in this slice. The retirement plan may recommend moving long-term audit
reports to the external knowledge store, but it must not remove them.

### Manual Review

Unknown files under these areas should be classified as `manual_review`:

```text
state/**
raw/**
wiki/**
sources/**
indexes/**
```

The implementation should explain why a file is unknown instead of silently
assigning it to a broad cleanup bucket.

## Implementation Slice

Implement a read-only "old repo data retirement" inventory.

Preferred integration:

```bash
hatch run wiki-ops-status --retirement-plan
hatch run wiki-ops-status --retirement-json
```

Do not add a new Hatch command unless the existing `wiki-ops-status` CLI is
structurally unable to host the feature.

### Module

Add a focused module, for example:

```text
src/wiki_ops/retirement_plan.py
```

Responsibilities:

- call Git to list currently tracked files in the code repository
- classify tracked files according to the ownership rules above
- count files and bytes by ownership class and proposed action
- detect risky or ambiguous files that need manual review
- report precondition status using existing ops-status/migration/release
  helpers where available
- produce stable text and JSON output
- perform no writes
- create no directories
- delete nothing

### Git Tracking Source

Use Git as the source of truth for "what is still versioned in the code repo":

```bash
git ls-files -z
```

Implementation requirements:

- handle paths with spaces safely
- treat Git output as repository-relative paths
- do not use shell string parsing where Python subprocess list arguments are
  sufficient
- gracefully report an error/warning if Git is unavailable
- do not scan external knowledge/vault roots for tracked files because they are
  outside the code repository

### Proposed Actions

Every tracked file should receive one of these proposed actions:

- `keep_tracked`
- `keep_untracked_local_config`
- `untrack_later`
- `manual_review`
- `ignore_rule_needed`
- `not_managed`

Use these meanings:

- `keep_tracked`: belongs in the code repo
- `keep_untracked_local_config`: should exist locally but must not be tracked
- `untrack_later`: belongs to external data/vault ownership and should later be
  removed from Git tracking with `git rm --cached`
- `manual_review`: cannot be safely classified
- `ignore_rule_needed`: pattern should be covered by `.gitignore`
- `not_managed`: outside this migration scope

The first implementation should not run `git rm --cached`. It should only
produce the list of files that a later, explicitly approved execution step
would untrack.

### Text Output

`hatch run wiki-ops-status --retirement-plan` should append a concise section:

```text
Old Repo Data Retirement
- tracked files inspected: 1234
- keep tracked: 210
- untrack later: 980
- manual review: 4
- readiness: warning

Largest untrack-later areas
- wiki: 614 files, 12.4 MB
- state/reviews: 360 files, 8.2 MB
- state/synthesis: 124 files, 1.1 MB

Preconditions
- external knowledge root: ok
- external vault root: ok
- latest release verification: ok
- render dry-run: not checked by this command
- git working tree: clean

Recommended next actions
1. Review manual_review files.
2. Confirm latest release verification before untracking.
3. In a later approved step, run git rm --cached only for untrack_later files.
```

Keep the language plain and operator-friendly.

### JSON Output

`hatch run wiki-ops-status --retirement-json` should output a machine-readable
object and no human status report.

Suggested shape:

```json
{
  "schema_version": 1,
  "code_root": "/absolute/path/to/repo",
  "readiness": "warning",
  "summary": {
    "tracked_files": 1234,
    "keep_tracked": 210,
    "untrack_later": 980,
    "manual_review": 4,
    "total_bytes": 123456789
  },
  "preconditions": [
    {
      "key": "external_knowledge_root",
      "status": "ok",
      "message": "External knowledge root is configured."
    }
  ],
  "areas": [
    {
      "key": "wiki",
      "proposed_action": "untrack_later",
      "file_count": 614,
      "byte_count": 12400000
    }
  ],
  "files": [
    {
      "path": "wiki/topics/example.md",
      "area": "wiki",
      "proposed_action": "untrack_later",
      "byte_count": 1234,
      "reason": "Generated wiki page belongs to external private vault."
    }
  ]
}
```

The JSON should be deterministic:

- sort files by path
- sort areas by key
- avoid timestamps unless there is a strong reason

## Readiness Rules

The retirement plan should expose a readiness state:

- `ready`: all required preconditions known, no manual-review files, working
  tree clean, external roots configured
- `warning`: safe to inspect but not ready for execution, for example latest
  release verification has warning status or manual-review files exist
- `blocked`: executing future untracking would be unsafe

Block when:

- path configuration still points all primary areas to the code repo
- external knowledge root is required but missing
- external vault root is required but missing
- Git tracked-file inventory cannot be read
- latest release verification reports errors, if verification data is available
- local config file is tracked

Warn when:

- no latest release manifest exists
- latest release verification is warning but not error
- temporary artifacts exist and are not yet cleaned
- manual-review files exist
- Git working tree is dirty

## Future Execution Phase

This spec does not implement execution, but the read-only report should prepare
for a later explicit execution spec.

The later execution phase should:

- require explicit user approval
- require a clean Git working tree
- require successful release verification
- run `git rm --cached` only
- never run `rm`
- never delete external files
- write an audit report before and after untracking
- update `.gitignore` in the same commit as the untracking
- keep the old files on disk until the user confirms a separate local cleanup

Example future command shape, not part of this slice:

```bash
hatch run wiki-ops-status --retirement-plan
# later, after review and explicit approval:
hatch run wiki-retire-repo-data --plan latest --yes
```

Avoid implementing this execution command now unless the user explicitly asks
for it.

## .gitignore Recommendations

The retirement plan may report suggested ignore patterns, but it should not
blindly rewrite `.gitignore`.

Likely future ignore patterns:

```gitignore
# Local path configuration
config/wiki_paths.toml

# Externalized knowledge data and generated vault content
raw/readwise/
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
wiki/
sources/
indexes/
```

Do not ignore:

```text
src/**
tests/**
docs/**
config/*.example.toml
```

If tests require fixture data that resembles wiki/state paths, place it under
`tests/fixtures/**`.

## Testing Requirements

Add tests for:

- classifying normal code files as `keep_tracked`
- classifying `wiki/**` as `untrack_later`
- classifying `state/reviews/**` as `untrack_later`
- classifying `state/synthesis/**` as `untrack_later`
- classifying render graph/manifest as `untrack_later`
- classifying temporary artifacts as `untrack_later`
- preserving `tests/fixtures/**` as `keep_tracked`
- flagging unknown `state/**` files as `manual_review`
- detecting tracked `config/wiki_paths.toml` as blocked
- producing deterministic JSON
- handling Git inventory failure gracefully
- ensuring `--retirement-plan` performs no writes
- ensuring `--retirement-json` prints only JSON

If the project uses snapshot-style CLI tests, include representative text output
but avoid brittle byte counts unless using a controlled temp repo.

## Validation Commands

Run at minimum:

```bash
hatch run lint
hatch run typecheck
hatch run test
hatch run wiki-ops-status --retirement-plan
hatch run wiki-ops-status --retirement-json
```

If the project uses different Hatch script names for tests/type checks, use the
existing project conventions.

## Definition of Done

This slice is complete when:

- `wiki-ops-status --retirement-plan` exists and is read-only
- `wiki-ops-status --retirement-json` exists and is read-only
- tracked repo-local knowledge/vault files are clearly classified
- the report explains what should stay tracked and what should be untracked
  later
- the report flags ambiguous files instead of guessing
- no local files are deleted
- no files are untracked from Git by this slice
- no LLM calls are made
- tests cover classification, JSON output, and safety behavior
- documentation explains that actual untracking is a separate approved step

## Operator Guidance After Implementation

After this feature lands, the user should run:

```bash
hatch run wiki-ops-status --retirement-plan
hatch run wiki-ops-status --retirement-json
```

Then review:

- whether all `untrack_later` files are expected historical repo-local
  knowledge/vault data
- whether any `manual_review` files need a new rule
- whether `.gitignore` recommendations are complete
- whether latest release verification still passes

Only after that review should a separate implementation step be planned for
`git rm --cached` and `.gitignore` updates.
