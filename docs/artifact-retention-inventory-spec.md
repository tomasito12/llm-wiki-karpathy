# Technical Specification: Artifact Retention Inventory and Cleanup Preflight

Last updated: 2026-07-11

This specification is the recommended next implementation slice after:

1. central path configuration
2. full source text in generated source pages

It is intended for Cursor or another implementation agent that has no prior chat
context.

## Background

The project is `llm-wiki-karpathy`, a local AI knowledge-base system.

It ingests Readwise article exports, creates human-reviewed extraction artifacts,
renders a generated Obsidian wiki, and creates optional Stage 2 synthesis cache
entries.

The user wants the system to become maintainable as it grows from hundreds to
thousands of documents.

The current system has many folders:

- raw source exports
- review artifacts
- synthesis cache entries
- render graph and manifest
- generated wiki pages
- synthesis previews
- synthesis run reports
- synthesis backups
- prompt previews
- ingest batch logs

Some are canonical. Some are generated. Some are temporary. Right now this
classification exists mostly in docs and in scattered operational intuition.

That creates risk:

- temporary previews can look like real knowledge
- duplicate-looking folders accumulate
- Git status can become confusing
- rollback boundaries are unclear
- future cleanup could accidentally delete important data
- future migration to an external knowledge store is harder than necessary

## Goal

Add a small, read-only artifact retention inventory layer.

The layer should let the system explain:

- which important paths exist
- which paths are canonical, generated, or temporary
- which paths are safe to clean later
- which paths must never be auto-deleted
- how many files and bytes each managed artifact area contains
- whether temporary artifacts exist that could be cleaned after a release

This is a preflight slice. It must not delete files.

## Product Direction

The user explicitly does not want a growing pile of one-off Hatch commands.

Therefore:

- do not add a new Hatch command for this slice
- extend the existing `wiki-ops-status` command
- keep the implementation as reusable internal code that a future web UI can
  consume

The command may gain new flags, but no new `pyproject.toml` script should be
added.

## Non-Goals

Do not implement in this slice:

- actual deletion
- backup provider integration
- Git commits
- rollback execution
- external data migration
- server deployment
- web UI
- LLM calls
- source redaction
- public/team export filtering

This slice is only about read-only inventory and cleanup preflight information.

## Relationship to Existing Specs

Use these documents as context:

- `docs/data-ownership-retention-spec.md`
- `docs/repo-vault-split-migration-spec.md`
- `docs/path-configuration-technical-spec.md`
- `docs/wiki-ops-status-technical-spec.md`
- `docs/source-page-fulltext-implementation-spec.md`

This spec makes the retention policy executable in a small, safe way.

## Path Configuration Requirement

Use the central path configuration layer if it exists.

Expected module:

```text
src/wiki_paths/
  config.py
  cli_helpers.py
```

Expected resolved fields:

```python
paths.raw_dir
paths.reviews_dir
paths.synthesis_dir
paths.graph_path
paths.manifest_path
paths.preview_dir
paths.run_dir
paths.backup_dir
paths.wiki_dir
paths.release_dir
```

The artifact inventory must not hard-code repo-local paths when configured paths
are available.

Default behavior with no config must remain unchanged and repo-local.

## Source Page Decision

Important: the full source text implementation extends existing generated source
pages:

```text
wiki/sources/<source_id>.md
```

It does not create a separate first-slice hierarchy:

```text
sources/full/<source_id>.md
```

For retention classification, generated source pages are part of `wiki_dir`.
Do not add a durable `sources/full/` area unless a later explicit migration
changes the source-page model.

## Data Classes

The inventory should classify artifact areas into three data classes.

### Canonical

Canonical data is required to reconstruct the knowledge state.

Examples:

- `raw_dir`
- `reviews_dir`
- `synthesis_dir`
- config files used for extraction/synthesis/rendering

Rules:

- never auto-delete
- must be backed up
- may be Git-versioned selectively, but backup must not rely only on Git

### Generated

Generated data can be recreated from canonical data plus code/config.

Examples:

- `wiki_dir`
- `graph_path`
- `manifest_path`

Rules:

- safe to regenerate
- may be committed in the vault/release flow
- should be tied to a release manifest later

### Temporary

Temporary data supports human review, debugging, or operational inspection.

Examples:

- `preview_dir`
- `run_dir`
- `backup_dir`
- `state/synthesis_prompts/`
- `state/ingest_batches/`

Rules:

- not canonical knowledge
- should not be committed by default
- may be cleaned later, but not in this slice
- cleanup must always be dry-run-first in a later slice

## Proposed Internal Module

Add a small module:

```text
src/wiki_ops/retention.py
```

Suggested dataclasses:

```python
@dataclass(frozen=True)
class ArtifactAreaDefinition:
    key: str
    path: Path
    data_class: str  # "canonical" | "generated" | "temporary"
    purpose: str
    cleanup_policy: str
    must_backup: bool
    git_policy: str


@dataclass(frozen=True)
class ArtifactAreaStatus:
    key: str
    path: Path
    data_class: str
    purpose: str
    cleanup_policy: str
    must_backup: bool
    git_policy: str
    exists: bool
    file_count: int
    byte_count: int
    newest_mtime: float | None
    oldest_mtime: float | None
    warnings: list[str]


@dataclass(frozen=True)
class RetentionInventory:
    areas: list[ArtifactAreaStatus]
    totals_by_class: dict[str, dict[str, int]]
    cleanup_preflight: CleanupPreflight
    warnings: list[str]
```

Suggested cleanup preflight:

```python
@dataclass(frozen=True)
class CleanupPreflight:
    temporary_file_count: int
    temporary_byte_count: int
    cleanup_candidate_count: int
    cleanup_candidate_bytes: int
    cleanup_blocked_reason: str | None
```

This is only a report. It must not delete anything.

## Area Definitions

Create definitions from resolved `WikiPaths`.

Minimum areas:

| Key | Path | Class | Cleanup |
|---|---|---|---|
| `raw_readwise` | `paths.raw_dir` | canonical | never |
| `reviews` | `paths.reviews_dir` | canonical | never |
| `synthesis_cache` | `paths.synthesis_dir` | canonical | never |
| `render_graph` | `paths.graph_path` | generated | replaced by render |
| `render_manifest` | `paths.manifest_path` | generated | replaced by render |
| `wiki` | `paths.wiki_dir` | generated | regenerated by render |
| `synthesis_previews` | `paths.preview_dir` | temporary | clean after release |
| `synthesis_runs` | `paths.run_dir` | temporary | keep latest / TTL later |
| `synthesis_backups` | `paths.backup_dir` | temporary | clean after release |

Optional repo-local legacy temporary areas if they exist:

| Key | Path | Class | Cleanup |
|---|---|---|---|
| `synthesis_prompts` | `<knowledge_root>/state/synthesis_prompts` | temporary | manual / TTL later |
| `ingest_batches` | `<knowledge_root>/state/ingest_batches` | temporary | TTL later |

If `knowledge_root` is available in `WikiPaths`, derive optional legacy paths
from it. If not, derive them from repo root.

## Counting Rules

For directories:

- recursively count regular files
- sum file sizes in bytes
- record newest and oldest modification times
- ignore broken symlinks
- do not follow symlinked directories by default

For files:

- `file_count` is `1` if the file exists
- `byte_count` is the file size
- mtime fields are the file mtime

If a path is missing:

- `exists = false`
- counts are zero
- do not treat missing optional temporary paths as errors

## Safety Rules

This implementation must be read-only.

Do not call:

- `unlink`
- `rmdir`
- `rm`
- `shutil.rmtree`
- write operations

The tests should make it clear that the implementation only reads filesystem
metadata.

## CLI Integration

Extend the existing command:

```bash
hatch run wiki-ops-status
```

Do not add a new Hatch script.

Add one or both of these flags:

```text
--retention
--retention-json
```

Recommended behavior:

```bash
hatch run wiki-ops-status --retention
```

prints a readable retention section after the existing status report.

```bash
hatch run wiki-ops-status --retention-json
```

prints only the retention inventory JSON and exits.

Existing behavior must remain unchanged:

```bash
hatch run wiki-ops-status
hatch run wiki-ops-status --json
hatch run wiki-ops-status --paths-json
```

`--json` may include a compact `retention` object only if that does not bloat
the existing output too much. Prefer keeping detailed inventory behind
`--retention-json`.

## Text Output

Recommended concise text section:

```text
Retention Inventory
- canonical: 3 areas, 724 files, 142.3 MB
- generated: 3 areas, 1266 files, 38.1 MB
- temporary: 5 areas, 91 files, 7.4 MB
- cleanup preflight: temporary artifacts present; cleanup requires a release manifest
```

Then optionally list areas:

```text
Areas
- raw_readwise: canonical, present, 724 files, never auto-delete
- synthesis_previews: temporary, present, 25 files, clean after release
```

Keep this human-readable and calm. The status command should help the user feel
oriented, not overwhelmed.

## JSON Output

`--retention-json` should produce a stable object:

```json
{
  "areas": [
    {
      "key": "raw_readwise",
      "path": "/abs/path/raw/readwise",
      "data_class": "canonical",
      "purpose": "Original Readwise markdown/html exports",
      "cleanup_policy": "never",
      "must_backup": true,
      "git_policy": "do not commit by default",
      "exists": true,
      "file_count": 724,
      "byte_count": 149221376,
      "newest_mtime": 1783791000.0,
      "oldest_mtime": 1781200000.0,
      "warnings": []
    }
  ],
  "totals_by_class": {
    "canonical": {"areas": 3, "files": 1084, "bytes": 180000000},
    "generated": {"areas": 3, "files": 1266, "bytes": 41000000},
    "temporary": {"areas": 5, "files": 91, "bytes": 7400000}
  },
  "cleanup_preflight": {
    "temporary_file_count": 91,
    "temporary_byte_count": 7400000,
    "cleanup_candidate_count": 0,
    "cleanup_candidate_bytes": 0,
    "cleanup_blocked_reason": "cleanup is not implemented in this read-only slice"
  },
  "warnings": []
}
```

## Recommendations Integration

`wiki-ops-status` already prints recommendations.

Extend recommendations conservatively:

- if temporary artifacts exist:
  - `Temporary artifacts are present; keep them for now or clean them after a release manifest exists.`
- if canonical paths are missing:
  - `Canonical path missing: <key>. Verify path configuration before continuing.`
- if generated paths are missing but canonical inputs exist:
  - existing render recommendations are enough; avoid duplicate noise

Do not recommend deletion yet.

## Release Manifest Dependency

Cleanup should be blocked until a release manifest exists.

This slice does not implement release manifests.

The cleanup preflight should therefore report:

```text
cleanup_blocked_reason = "cleanup is not implemented in this read-only slice"
```

or:

```text
cleanup_blocked_reason = "no release manifest support yet"
```

Do not fake release readiness.

## Tests

Add tests under:

```text
tests/wiki_ops/test_retention.py
tests/wiki_ops/test_status_cli.py
```

Required tests:

1. Builds area definitions from `WikiPaths`.
2. Classifies raw, reviews, and synthesis as canonical.
3. Classifies wiki, graph, and manifest as generated.
4. Classifies previews, runs, backups, prompts, and ingest batches as temporary.
5. Counts files and bytes for directories.
6. Counts a single file area such as graph or manifest.
7. Missing optional temporary directories do not produce errors.
8. Missing canonical directories produce warnings.
9. Symlinked directories are not traversed.
10. `wiki-ops-status --retention-json` prints valid JSON.
11. `wiki-ops-status --retention` includes a readable retention section.
12. Existing `wiki-ops-status`, `--json`, and `--paths-json` still work.
13. Path config overrides are respected.
14. No files are deleted or written.

If practical, add a test that monkeypatches deletion-like functions or uses a
read-only fixture to prove the code is metadata-only.

## Suggested Implementation Steps

1. Add `src/wiki_ops/retention.py`.
2. Add dataclasses and pure functions for area definitions and filesystem
   inventory.
3. Add `format_retention_text()`.
4. Wire `wiki-ops-status --retention` and `--retention-json`.
5. Add recommendations for temporary artifacts and missing canonical paths.
6. Add tests.
7. Run targeted tests and lint.

## Commands to Run

```bash
hatch run test:run tests/wiki_ops/test_retention.py tests/wiki_ops/test_status_cli.py
hatch run test:run tests/wiki_paths tests/wiki_ops/test_status.py tests/wiki_synthesis/test_select_cli.py tests/wiki_synthesis/test_batch_cli.py
hatch run lint:check
hatch run wiki-ops-status --retention
hatch run wiki-ops-status --retention-json
```

Do not run destructive cleanup commands because none should exist in this slice.

## Definition of Done

The implementation is complete when:

- the system has a reusable artifact retention inventory module
- the inventory uses central path configuration
- no new Hatch command is added
- `wiki-ops-status --retention` works
- `wiki-ops-status --retention-json` works
- canonical/generated/temporary areas are classified clearly
- file counts and byte counts are reported
- missing canonical paths produce warnings
- temporary artifacts are reported but not deleted
- tests cover path config, classification, missing paths, and JSON output
- lint/type checks pass

