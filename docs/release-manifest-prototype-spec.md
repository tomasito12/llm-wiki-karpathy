# Technical Specification: Release Manifest Prototype

Last updated: 2026-07-12

This specification is the recommended next implementation slice after:

1. central path configuration
2. full source text in generated source pages
3. artifact retention inventory and cleanup preflight

It is intended for Cursor or another implementation agent that has no prior chat
context.

## Background

The project is `llm-wiki-karpathy`, a local AI knowledge-base system.

It ingests Readwise exports, creates human-reviewed extraction artifacts, renders
a generated Obsidian wiki, and creates optional Stage 2 synthesis cache entries.

The user wants the system to become maintainable as it grows from hundreds to
thousands of documents. Recent architecture work separates data into three
classes:

- canonical data: raw exports, review artifacts, synthesis cache, configuration
- generated data: rendered wiki, render graph, render manifest, indexes
- temporary data: previews, run reports, backups, prompt previews, ingest logs

The artifact retention inventory can now explain these areas, but cleanup is
still blocked because the system has no release boundary.

That release boundary is the next missing piece.

## Goal

Add a first, conservative release manifest prototype.

The release manifest should describe one coherent knowledge release:

- which canonical and generated paths were present
- how many files were included in each area
- deterministic hashes for important areas
- the current code commit when available
- the resolved path configuration
- the current artifact retention summary
- whether temporary artifacts exist
- whether the release is complete enough to be a future cleanup/rollback anchor

This slice must be safe:

- no cleanup
- no rollback
- no Git commits
- no LLM calls
- no backup provider integration
- no server deployment

The manifest is metadata. It does not copy or archive data.

## Product Direction

The user does not want a growing pile of one-off Hatch commands.

Prefer extending the existing operational surface:

- add release-manifest support to `wiki-ops-status` where practical
- add at most one focused command only if writing a manifest would make
  `wiki-ops-status` confusing

Recommended command shape:

```bash
hatch run wiki-ops-status --release-dry-run
hatch run wiki-ops-status --release-json
hatch run wiki-ops-status --write-release-manifest --yes
```

Alternative acceptable shape:

```bash
hatch run wiki-release --dry-run
hatch run wiki-release --json
hatch run wiki-release --write --yes
```

If a new command is added, document why it is justified. The preferred reason is
that writing a release manifest is a distinct lifecycle action, while
`wiki-ops-status` remains read-only by default.

## Non-Goals

Do not implement in this slice:

- deleting temporary files
- cleaning previews, runs, or backups
- rollback execution
- restoring old releases
- copying raw data into release folders
- creating backup snapshots
- pushing to Git
- committing generated files
- changing the Obsidian vault layout
- public or team export filtering
- LLM-based quality review

This slice creates or previews a manifest only.

## Relationship to Existing Specs

Use these documents as context:

- `docs/data-ownership-retention-spec.md`
- `docs/artifact-retention-inventory-spec.md`
- `docs/repo-vault-split-migration-spec.md`
- `docs/path-configuration-technical-spec.md`
- `docs/wiki-ops-status-technical-spec.md`
- `docs/source-page-fulltext-implementation-spec.md`

This specification turns the release-manifest concept from
`data-ownership-retention-spec.md` into a small first implementation.

## Path Configuration Requirement

Use the central path configuration layer.

Expected resolved fields:

```python
paths.raw_dir
paths.reviews_dir
paths.synthesis_dir
paths.graph_path
paths.manifest_path
paths.release_dir
paths.preview_dir
paths.run_dir
paths.backup_dir
paths.wiki_dir
paths.indexes_dir
```

The implementation must respect:

- default repo-local paths
- `--paths-config`
- `LLM_WIKI_PATHS_CONFIG`
- explicit CLI overrides that already exist on `wiki-ops-status`

If the artifact retention slice introduced helper functions for applying
`wiki-ops-status` path overrides, reuse them.

## Output Path

Release manifests should be written under:

```text
paths.release_dir/<release_id>.json
```

Default repo-local path:

```text
state/releases/<release_id>.json
```

Suggested release id format:

```text
YYYYMMDDTHHMMSSZ
```

Example:

```text
20260712T223000Z
```

Use UTC for release ids and timestamps.

The implementation should create `paths.release_dir` only when explicitly
writing a manifest. Dry-run and JSON preview must not create directories.

## Release Completeness Model

The release prototype should classify readiness conservatively.

Suggested states:

```text
ready
warning
blocked
```

`ready` means:

- raw source directory exists and contains files
- review directory exists and contains review artifacts
- synthesis cache directory exists, even if it contains zero files
- wiki directory exists and contains generated pages
- render graph exists
- render manifest exists
- no retention warning for missing canonical paths

`warning` means:

- temporary artifacts are present
- synthesis cache has warnings but no errors
- there are uncommitted files
- source full-text coverage is incomplete but above the configured guard
- render output appears present but may not be freshly verified

`blocked` means:

- a canonical path is missing
- render graph or manifest is missing
- wiki directory is missing or empty
- retention inventory reports missing required canonical data
- release manifest output path already exists and overwrite was not explicitly
  requested

The first implementation may use a simpler readiness check, but it must not mark
a release as `ready` when required canonical data is missing.

## Hashing Rules

Compute deterministic hashes for important files and directories.

Recommended function:

```python
hash_path(path: Path) -> PathHash
```

Suggested dataclass:

```python
@dataclass(frozen=True)
class PathHash:
    path: Path
    exists: bool
    kind: str  # "file" | "directory" | "missing" | "other"
    file_count: int
    byte_count: int
    sha256: str | None
```

For files:

- hash the file bytes with SHA-256
- `file_count = 1`
- `byte_count = file size`

For directories:

- recursively walk regular files
- do not follow symlinked directories
- ignore symlinked files
- sort relative paths lexicographically
- hash both relative path and file bytes
- include separators so path boundaries are unambiguous

Suggested directory hashing stream:

```text
<relative_posix_path>\0<sha256(file_bytes)>\0<size>\n
```

Then SHA-256 the full stream.

This avoids loading every file into one giant string.

## Manifest Schema

Suggested top-level JSON:

```json
{
  "schema_version": 1,
  "release_id": "20260712T223000Z",
  "created_at": "2026-07-12T22:30:00Z",
  "status": "warning",
  "status_reasons": [
    "Temporary artifacts are present."
  ],
  "code": {
    "repo_root": "/abs/path/llm-wiki-karpathy",
    "git_commit": "abc123",
    "git_dirty": true
  },
  "paths": {
    "raw_dir": "/abs/path/raw/readwise",
    "reviews_dir": "/abs/path/state/reviews",
    "synthesis_dir": "/abs/path/state/synthesis",
    "wiki_dir": "/abs/path/wiki",
    "graph_path": "/abs/path/state/wiki_render_graph.json",
    "manifest_path": "/abs/path/state/wiki_render_manifest.json",
    "release_dir": "/abs/path/state/releases"
  },
  "areas": {
    "raw_readwise": {
      "data_class": "canonical",
      "exists": true,
      "file_count": 724,
      "byte_count": 11588524,
      "sha256": "..."
    },
    "reviews": {
      "data_class": "canonical",
      "exists": true,
      "file_count": 360,
      "byte_count": 19827979,
      "sha256": "..."
    },
    "synthesis_cache": {
      "data_class": "canonical",
      "exists": true,
      "file_count": 124,
      "byte_count": 713800,
      "sha256": "..."
    },
    "render_graph": {
      "data_class": "generated",
      "exists": true,
      "file_count": 1,
      "byte_count": 14456459,
      "sha256": "..."
    },
    "render_manifest": {
      "data_class": "generated",
      "exists": true,
      "file_count": 1,
      "byte_count": 250665,
      "sha256": "..."
    },
    "wiki": {
      "data_class": "generated",
      "exists": true,
      "file_count": 1294,
      "byte_count": 10007582,
      "sha256": "..."
    }
  },
  "counts": {
    "raw_files": 724,
    "reviews": 360,
    "synthesis_entries": 124,
    "wiki_files": 1294
  },
  "retention": {
    "temporary_file_count": 189,
    "temporary_byte_count": 1226494,
    "cleanup_candidate_count": 0,
    "cleanup_blocked_reason": "cleanup is not implemented in this read-only slice"
  },
  "warnings": []
}
```

The exact schema may be smaller, but it must include:

- `schema_version`
- `release_id`
- `created_at`
- `status`
- `status_reasons`
- `code.git_commit`
- `code.git_dirty`
- resolved paths
- area hashes and counts
- temporary artifact summary

## Git Metadata

Collect Git metadata read-only.

Recommended:

```bash
git rev-parse HEAD
git status --porcelain
```

If Git is unavailable, do not fail the release preview. Report:

```json
{
  "git_commit": null,
  "git_dirty": null,
  "git_error": "..."
}
```

If the worktree is dirty, the manifest may still be previewed and written, but
status should be at least `warning`.

Do not run `git add`, `git commit`, `git reset`, `git clean`, or `git push`.

## CLI Behavior

### Dry-run / Preview

Preview mode must not write files.

Recommended:

```bash
hatch run wiki-ops-status --release-dry-run
```

Print a concise section:

```text
Release Manifest Preview
- release id: 20260712T223000Z
- status: warning
- canonical: 3 areas, 1226 files, 30.6 MB
- generated: 3 areas, 1296 files, 23.6 MB
- temporary artifacts: 189 files
- output path: state/releases/20260712T223000Z.json
```

### JSON Preview

Recommended:

```bash
hatch run wiki-ops-status --release-json
```

Print the full manifest JSON without writing it.

### Write

Writing must be explicit:

```bash
hatch run wiki-ops-status --write-release-manifest --yes
```

Rules:

- require `--yes`
- create `paths.release_dir` if needed
- write exactly one JSON file
- fail if the target file already exists unless an explicit `--overwrite` flag
  is provided
- print the written path
- do not clean anything

If the implementation uses a dedicated command instead, preserve the same safety
rules.

## Integration With Artifact Retention

The release manifest should reuse the retention inventory where possible.

Do not duplicate data class definitions. Reuse:

- artifact area definitions
- filesystem counting rules
- temporary artifact totals
- retention warnings

The release manifest may add deterministic hashes on top of retention status.

Future cleanup will use release manifests as a safety condition, but cleanup is
not implemented here.

## Text Output Requirements

Keep text output concise and readable.

Do not print every file path in text mode.

Text mode should show:

- release id
- status
- output path
- canonical/generated/temporary summary
- blocking reasons
- warnings

Detailed hashes belong in JSON, not normal text output.

## JSON Stability

The manifest JSON is intended for future automation.

Use stable keys.

Avoid including:

- machine-specific temporary fields unless clearly named
- nondeterministic ordering
- verbose per-file lists

Sort area keys and path hashes where practical.

## Safety Rules

This slice may only write when explicitly asked to write a release manifest.

It must not:

- delete files
- modify canonical data
- modify generated wiki files
- modify synthesis cache files
- modify temporary artifacts
- call OpenAI or any LLM provider
- run `wiki-render`
- run synthesis commands
- run cleanup commands

Dry-run and JSON preview must be strictly read-only.

## Tests

Add tests under a focused test module, for example:

```text
tests/wiki_ops/test_release_manifest.py
tests/wiki_ops/test_status_cli_release.py
```

Required tests:

1. Hashing a single file returns stable SHA-256, file count, and byte count.
2. Hashing a directory is deterministic regardless of file creation order.
3. Directory hashing ignores symlinked directories.
4. Missing paths are represented as missing, not as errors.
5. Manifest includes required top-level schema fields.
6. Manifest includes resolved path configuration.
7. Manifest includes canonical and generated area hashes.
8. Temporary artifacts produce warning or warning status.
9. Missing canonical paths produce blocked status.
10. Dirty Git metadata produces warning status when Git metadata is available.
11. JSON preview writes no files.
12. Writing without `--yes` fails with exit code `2`.
13. Writing with `--yes` creates exactly one manifest file.
14. Existing manifest path is not overwritten by default.
15. Existing `wiki-ops-status`, `--json`, `--paths-json`, `--retention`, and
    `--retention-json` behavior remains unchanged.
16. Explicit path overrides and `--paths-config` are respected.

If practical, add a read-only test that monkeypatches deletion functions to
prove no cleanup is attempted.

## Suggested Implementation Steps

1. Add a small internal module, for example:

   ```text
   src/wiki_ops/release_manifest.py
   ```

2. Implement dataclasses:

   - `PathHash`
   - `ReleaseManifest`
   - optional `ReleaseStatus`

3. Implement deterministic file and directory hashing.
4. Reuse retention inventory to identify areas and temporary artifact counts.
5. Add Git metadata collection with graceful fallback.
6. Add manifest builder function:

   ```python
   build_release_manifest(paths: WikiPaths, release_id: str | None = None) -> ReleaseManifest
   ```

7. Add text formatting and JSON serialization.
8. Wire CLI preview and write behavior.
9. Add tests.
10. Run targeted tests and lint.

## Commands to Run

At minimum:

```bash
hatch run test:run tests/wiki_ops/test_release_manifest.py tests/wiki_ops/test_status_cli.py
hatch run lint:check
hatch run wiki-ops-status --release-json
hatch run wiki-ops-status --release-dry-run
```

If the implementation adds a dedicated release command, run that command's
dry-run and JSON modes instead.

## Definition of Done

This slice is done when:

- a release manifest can be previewed as JSON without writing files
- a release manifest can be written only with explicit confirmation
- the manifest contains stable hashes and counts for canonical and generated
  areas
- temporary artifacts are reported but not cleaned
- missing canonical data blocks readiness
- dirty Git state is visible
- existing status and retention commands still work
- tests and lint pass

## Cursor Handoff Prompt

Use this prompt when handing the implementation to Cursor:

```text
Please implement the next slice from:

docs/release-manifest-prototype-spec.md

Important:
- Keep this conservative and safe.
- Do not implement cleanup, rollback, Git commits, backup snapshots, or LLM calls.
- Reuse the central path configuration and artifact retention inventory.
- The release manifest must provide deterministic hashes and counts for
  canonical/generated areas.
- Preview modes must be read-only.
- Writing a manifest must require explicit confirmation (`--yes`) and must not
  overwrite existing manifests by default.
- Existing `wiki-ops-status` behavior must remain unchanged unless a release
  flag is passed.
- Add focused tests and run lint.
```

