# Technical Specification: Temporary Artifact Cleanup

Last updated: 2026-07-12

This specification is the recommended next implementation slice after:

1. central path configuration
2. full source text in generated source pages
3. artifact retention inventory and cleanup preflight
4. release manifest prototype

It is intended for Cursor or another implementation agent that has no prior chat
context.

## Background

The project is `llm-wiki-karpathy`, a local AI knowledge-base system.

It ingests Readwise exports, creates human-reviewed extraction artifacts, renders
a generated Obsidian wiki, and creates optional Stage 2 synthesis cache entries.

The system now distinguishes between:

- canonical data: raw exports, review artifacts, synthesis cache
- generated data: rendered wiki, render graph, render manifest, indexes
- temporary data: synthesis previews, run reports, backups, prompt previews,
  ingest batch logs

The retention inventory can explain temporary artifact areas. The release
manifest prototype can define a coherent knowledge release.

The next step is to make temporary cleanup possible without making the system
dangerous.

## Goal

Add a conservative cleanup planner and executor for temporary artifacts.

The implementation should:

- show which temporary files would be removed
- default to dry-run
- delete files only when explicitly confirmed
- require an existing release manifest before deleting anything
- delete only temporary artifact areas
- never delete canonical or generated knowledge data
- produce a machine-readable cleanup report
- keep enough audit information to understand what happened

This slice should reduce folder clutter without weakening rollback or
regeneration safety.

## Product Direction

The user does not want a growing pile of Hatch commands. However, cleanup is a
destructive lifecycle action. It should not be hidden inside the read-only
`wiki-ops-status` command.

Therefore, this slice may add one focused command:

```bash
hatch run wiki-cleanup --dry-run
hatch run wiki-cleanup --after-release 20260712T223000Z --dry-run
hatch run wiki-cleanup --after-release 20260712T223000Z --yes
```

Rationale:

- `wiki-ops-status` should remain read-only.
- Cleanup needs explicit confirmation and clearer safety boundaries.
- A dedicated command makes destructive intent visible.

Do not add additional cleanup-related Hatch commands in this slice.

## Non-Goals

Do not implement in this slice:

- cleanup of raw exports
- cleanup of review artifacts
- cleanup of synthesis cache entries
- cleanup of rendered wiki pages
- cleanup of render graph or render manifest
- rollback
- backup provider integration
- Git commits or Git cleanup
- server deployment
- LLM calls
- source redaction
- public/team export filtering

This slice only cleans temporary artifacts after a release manifest exists.

## Relationship to Existing Specs

Use these documents as context:

- `docs/data-ownership-retention-spec.md`
- `docs/artifact-retention-inventory-spec.md`
- `docs/release-manifest-prototype-spec.md`
- `docs/path-configuration-technical-spec.md`
- `docs/wiki-ops-status-technical-spec.md`

This specification implements the cleanup phase described in
`data-ownership-retention-spec.md`, but only for temporary artifacts and only
with strong safety checks.

## Path Configuration Requirement

Use the central path configuration layer.

The cleanup command must respect:

- default repo-local paths
- `--paths-config`
- `LLM_WIKI_PATHS_CONFIG`
- explicit path overrides where relevant

Expected resolved fields:

```python
paths.release_dir
paths.preview_dir
paths.run_dir
paths.backup_dir
paths.knowledge_root
```

If retention inventory defines optional temporary paths, reuse that definition
instead of duplicating path constants.

## Cleanup Scope

Cleanup is allowed only for temporary areas.

Initial cleanable areas:

| Key | Path source | Default cleanup |
|---|---|---|
| `synthesis_previews` | `paths.preview_dir` | delete all files after release |
| `synthesis_backups` | `paths.backup_dir` | delete all files after release |
| `synthesis_prompts` | `<knowledge_root>/state/synthesis_prompts` | delete all files after release |

Conservative area:

| Key | Path source | Default cleanup |
|---|---|---|
| `synthesis_runs` | `paths.run_dir` | keep by default in first slice |

Reason: run reports are audit data. They are temporary, but they may still be
useful after a release. This first cleanup slice should report them and leave
them untouched unless a later retention policy explicitly defines TTL cleanup.

Optional area:

| Key | Path source | Default cleanup |
|---|---|---|
| `ingest_batches` | `<knowledge_root>/state/ingest_batches` | keep by default in first slice |

Reason: ingest batch logs may help debug pre-analysis behavior. Report them, but
do not delete them yet.

Do not clean anything outside the allowlist.

## Release Manifest Requirement

Real cleanup requires an existing release manifest.

The command should accept:

```bash
--after-release <release_id>
```

It should resolve:

```text
paths.release_dir/<release_id>.json
```

Rules:

- If `--yes` is passed without `--after-release`, exit with code `2`.
- If the release manifest file does not exist, exit with code `2`.
- If the release manifest has `status = "blocked"`, exit with code `2`.
- If the release manifest schema version is unsupported, exit with code `2`.
- If the release manifest paths are incompatible with the current resolved
  paths, exit with code `2` unless an explicit `--allow-path-mismatch` flag is
  passed.

Dry-run may run without `--after-release`, but it must report that real cleanup
is blocked until a release id is provided.

## Path Safety Rules

This is the most important part of the implementation.

Before deleting any file, validate:

- the file is under a known temporary area
- the temporary area is one of the allowed cleanup areas
- the file is not a symlink
- the resolved file path is still inside the resolved temporary area
- the file is not under `raw_dir`
- the file is not under `reviews_dir`
- the file is not under `synthesis_dir`
- the file is not under `wiki_dir`
- the file is not `graph_path`
- the file is not `manifest_path`
- the file is not inside `release_dir`

If any planned deletion fails safety validation, abort the entire real cleanup
with exit code `2`.

Do not follow symlinked directories. Do not delete symlinks in this first slice.

## Cleanup Plan Model

Add a small internal module:

```text
src/wiki_ops/cleanup.py
```

Suggested dataclasses:

```python
@dataclass(frozen=True)
class CleanupCandidate:
    area_key: str
    path: Path
    byte_count: int
    reason: str


@dataclass(frozen=True)
class CleanupSkippedArea:
    area_key: str
    path: Path
    reason: str


@dataclass(frozen=True)
class CleanupPlan:
    dry_run: bool
    after_release: str | None
    release_manifest_path: Path | None
    candidates: list[CleanupCandidate]
    skipped_areas: list[CleanupSkippedArea]
    candidate_count: int
    candidate_bytes: int
    blocked: bool
    blocked_reasons: list[str]
```

Suggested executor result:

```python
@dataclass(frozen=True)
class CleanupResult:
    dry_run: bool
    deleted_count: int
    deleted_bytes: int
    deleted_paths: list[Path]
    report_path: Path | None
```

## Planning Rules

Planning must be read-only.

Planning should:

- inspect retention inventory
- collect files from allowed cleanup areas
- ignore missing temporary areas
- ignore directories themselves in the candidate list
- ignore symlinks
- sort candidates by path for deterministic output
- compute total candidate count and bytes
- include skipped areas with reasons

Suggested reasons:

- `clean after release`
- `kept for audit in first cleanup slice`
- `missing optional temporary area`
- `not in cleanup allowlist`

## Execution Rules

Real execution happens only when:

```bash
--yes
```

is passed and a valid:

```bash
--after-release <release_id>
```

is provided.

Execution should:

1. Build the cleanup plan.
2. Validate the release manifest.
3. Validate every candidate path again immediately before deletion.
4. Delete files only, not directories, in the first slice.
5. Leave empty directories in place.
6. Write a cleanup report after successful execution.

If any deletion fails, stop and return non-zero. The cleanup report should note
partial deletion if practical.

## Cleanup Report

After real cleanup, write an audit report under:

```text
paths.knowledge_root/state/cleanup_runs/<timestamp>.json
```

If `knowledge_root` is not available, use:

```text
paths.release_dir/../cleanup_runs/<timestamp>.json
```

Suggested report fields:

```json
{
  "schema_version": 1,
  "created_at": "2026-07-12T23:00:00Z",
  "after_release": "20260712T223000Z",
  "release_manifest_path": "/abs/path/state/releases/20260712T223000Z.json",
  "dry_run": false,
  "deleted_count": 25,
  "deleted_bytes": 123456,
  "deleted_paths": [
    "/abs/path/state/synthesis_previews/topic/example.md"
  ],
  "skipped_areas": [
    {
      "area_key": "synthesis_runs",
      "reason": "kept for audit in first cleanup slice"
    }
  ]
}
```

Dry-run should not write a cleanup report by default.

Optional flag:

```bash
--write-dry-run-report
```

may write a dry-run report, but this is not required.

## CLI Behavior

Add one Hatch script:

```toml
wiki-cleanup = "src.wiki_ops.cleanup_cli:main"
```

CLI options:

```text
--dry-run
--yes
--after-release <release_id>
--paths-config <path>
--json
--area <area_key>        # optional, repeatable; only allowed temporary areas
--allow-path-mismatch   # advanced escape hatch, should be rarely used
```

Default behavior:

```bash
hatch run wiki-cleanup
```

should behave like:

```bash
hatch run wiki-cleanup --dry-run
```

Real cleanup:

```bash
hatch run wiki-cleanup --after-release 20260712T223000Z --yes
```

The command should refuse ambiguous combinations:

- `--yes` without `--after-release`: exit `2`
- `--dry-run --yes`: exit `2`
- unknown `--area`: exit `2`
- area outside cleanup allowlist: exit `2`

## Text Output

Dry-run text should be calm and explicit:

```text
Wiki Cleanup Dry Run
- after release: not provided
- cleanup status: blocked for real execution
- candidates: 25 files, 1.2 MB
- real cleanup requires --after-release <release_id> --yes

Areas
- synthesis_previews: 20 files, clean after release
- synthesis_backups: 5 files, clean after release
- synthesis_runs: skipped, kept for audit in first cleanup slice
```

Real execution text:

```text
Wiki Cleanup Complete
- after release: 20260712T223000Z
- deleted: 25 files, 1.2 MB
- report: state/cleanup_runs/20260712T230000Z.json
```

Do not print hundreds of paths in normal text mode. Use `--json` for full
details.

## JSON Output

`--json` should emit either the cleanup plan or execution result.

Dry-run JSON should include all candidate paths.

Real cleanup JSON should include deleted paths and report path.

Use stable keys and sorted candidate paths.

## Integration With `wiki-ops-status`

Do not make `wiki-ops-status` delete anything.

Optionally extend `wiki-ops-status --retention` to mention:

```text
Run `hatch run wiki-cleanup --dry-run` to inspect temporary cleanup candidates.
```

This is optional. Avoid making status output noisy.

## Tests

Add tests under:

```text
tests/wiki_ops/test_cleanup.py
tests/wiki_ops/test_cleanup_cli.py
```

Required tests:

1. Dry-run is the default.
2. Dry-run writes no files and deletes nothing.
3. Planning includes `synthesis_previews` files.
4. Planning includes `synthesis_backups` files.
5. Planning reports but does not include `synthesis_runs` by default.
6. Missing optional temporary directories do not fail planning.
7. Symlinked directories are not traversed.
8. Symlinked files are not deleted.
9. Candidates are sorted deterministically.
10. `--yes` without `--after-release` exits `2`.
11. `--dry-run --yes` exits `2`.
12. Missing release manifest exits `2` for real cleanup.
13. Blocked release manifest exits `2` for real cleanup.
14. Path mismatch between manifest and current config exits `2`.
15. Real cleanup with valid release manifest deletes only allowed temporary files.
16. Real cleanup never deletes raw, reviews, synthesis cache, wiki, graph,
    manifest, or release files.
17. Real cleanup writes one cleanup report.
18. `--json` emits valid JSON.
19. `--area synthesis_previews` limits candidates to that area.
20. Unknown or non-allowed area exits `2`.

If practical, monkeypatch `Path.unlink` in dry-run tests to prove no deletion is
attempted.

## Suggested Implementation Steps

1. Add `src/wiki_ops/cleanup.py`.
2. Add cleanup dataclasses and JSON serialization helpers.
3. Reuse retention inventory to discover temporary areas.
4. Implement release manifest loading and validation.
5. Implement cleanup planning.
6. Implement path safety validation.
7. Implement cleanup execution.
8. Add `src/wiki_ops/cleanup_cli.py`.
9. Add one Hatch script: `wiki-cleanup`.
10. Add tests.
11. Run targeted tests and lint.

## Commands to Run

At minimum:

```bash
hatch run test:run tests/wiki_ops/test_cleanup.py tests/wiki_ops/test_cleanup_cli.py
hatch run lint:check
hatch run wiki-cleanup --dry-run
hatch run wiki-cleanup --dry-run --json
```

Manual safety smoke test:

```bash
hatch run wiki-cleanup --yes
# must fail with exit code 2 because --after-release is missing
```

If a test release manifest exists:

```bash
hatch run wiki-cleanup --after-release <release_id> --dry-run
```

Do not run real cleanup against the user's actual repository during
implementation review unless the user explicitly approves it.

## Definition of Done

This slice is done when:

- cleanup planning works in dry-run mode
- dry-run is the default
- real cleanup requires `--after-release` and `--yes`
- only allowed temporary areas can be deleted
- canonical and generated data are protected by path safety checks
- cleanup reports are written after real cleanup
- release manifests are required for real cleanup
- existing status, retention, and release manifest commands still work
- tests and lint pass

## Cursor Handoff Prompt

Use this prompt when handing the implementation to Cursor:

```text
Please implement the next slice from:

docs/temporary-artifact-cleanup-spec.md

Important:
- This is the first destructive capability in the project, so keep it extremely
  conservative.
- Default mode must be dry-run.
- Real cleanup must require `--after-release <release_id>` and `--yes`.
- Delete only allowlisted temporary files from retention inventory.
- Never delete raw exports, reviews, synthesis cache, rendered wiki, graph,
  manifest, release manifests, or symlinks.
- Use central path configuration and release manifests.
- Add focused tests for path safety and CLI refusal cases.
- Do not run real cleanup against the user's actual repo unless explicitly
  approved.
```

