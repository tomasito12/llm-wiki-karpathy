# Technical Specification: Release Verification

Last updated: 2026-07-12

This specification defines the next implementation slice after:

1. central path configuration
2. artifact retention inventory
3. release manifest prototype
4. temporary artifact cleanup
5. knowledge store migration plan
6. external knowledge store operating mode

It is intended for Cursor or another implementation agent that has no prior chat
context.

## Background

The project is `llm-wiki-karpathy`, a local AI knowledge-base system.

It ingests Readwise exports, creates human-reviewed extraction artifacts, renders
a generated Obsidian wiki, and creates optional Stage 2 synthesis cache entries.

The system now supports a separated local operating mode:

```text
Code repo:
/Users/plischke/Desktop/Private Development/llm-wiki-karpathy-source-access-spec

Knowledge store:
/Users/plischke/Desktop/Private Development/llm-wiki-data

Private generated vault:
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

The active local path configuration is `config/wiki_paths.toml`. It is
machine-specific and intentionally gitignored. A committed example exists at
`config/wiki_paths.example.toml`.

The first copy-only migration has already completed. The old in-repo `state/`
and `wiki/` data was not deleted. The external knowledge store is now the
preferred source of truth for canonical knowledge data.

Release manifests already exist under:

```text
<knowledge_root>/state/releases/<release_id>.json
```

The next missing piece is a read-only verifier that can answer:

> Does the current knowledge store and generated vault still match a release
> manifest?

This is required before old repo-local data can be safely removed, before server
deployment, and before backup/rollback features become trustworthy.

## Goal

Add release verification to the existing ops surface.

The verifier should:

- load a release manifest by id or choose the latest release manifest
- recompute hashes/counts for all release manifest areas
- compare current resolved paths against manifest paths
- compare current counts/hashes against manifest counts/hashes
- report missing, changed, extra, and mismatched areas
- classify verification as `ok`, `warning`, or `error`
- provide text and JSON output
- remain read-only

Preferred command shape:

```bash
hatch run wiki-ops-status --verify-release latest
hatch run wiki-ops-status --verify-release 20260712T140520Z
hatch run wiki-ops-status --verify-release latest --verify-json
```

Do not add a new Hatch command in this slice.

## Non-Goals

Do not implement in this slice:

- rollback
- restore from release
- backup provider integration
- Git commits
- Git pushes
- deletion of old repo-local data
- copying data between stores
- writing new release manifests
- updating existing release manifests
- LLM calls
- public/team export filtering
- server deployment

This slice is read-only verification only.

## Relationship to Existing Specs

Use these documents as context:

- `docs/release-manifest-prototype-spec.md`
- `docs/external-operating-mode.md`
- `docs/knowledge-store-migration-plan-spec.md`
- `docs/data-ownership-retention-spec.md`
- `docs/temporary-artifact-cleanup-spec.md`
- `docs/path-configuration-technical-spec.md`

Use existing implementation where possible:

- `src/wiki_ops/release_manifest.py`
- `src/wiki_ops/status_cli.py`
- `src/wiki_paths/config.py`
- `src/wiki_paths/cli_helpers.py`

Do not duplicate hashing logic. Reuse `hash_path()` and release manifest area
keys from `release_manifest.py`.

## Path Configuration Requirement

The verifier must respect the central path configuration layer:

- default repo-local paths when no config exists
- `config/wiki_paths.toml` when present
- `LLM_WIKI_PATHS_CONFIG`
- `--paths-config`
- existing `wiki-ops-status` explicit path overrides

Verification must compare against the current resolved paths.

Path comparison should be strict by default:

- If manifest paths differ from current resolved paths, report a warning or
  error depending on severity.
- Do not silently verify a release against different locations without telling
  the user.

Add an explicit flag only if necessary:

```bash
--verify-allow-path-mismatch
```

If implemented, this flag should downgrade path mismatches from `error` to
`warning`. Do not hide them.

## Release Selection

Support:

```bash
--verify-release latest
--verify-release <release_id>
```

Rules:

- Release id maps to `paths.release_dir/<release_id>.json`.
- `latest` selects the lexicographically latest `*.json` file in
  `paths.release_dir`.
- If no release manifests exist, exit with code `2` and a clear error.
- If the selected file is malformed JSON, return verification status `error`.
- If schema version is unsupported, return verification status `error`.
- Do not create `paths.release_dir` in verification mode.

Release ids use UTC timestamp names such as:

```text
20260712T140520Z
```

Lexicographic sorting is valid for this format.

## Verification Model

Add a small internal module:

```text
src/wiki_ops/release_verify.py
```

Suggested dataclasses:

```python
@dataclass(frozen=True)
class ReleaseAreaVerification:
    area_key: str
    expected_path: Path | None
    current_path: Path | None
    expected_exists: bool
    current_exists: bool
    expected_file_count: int
    current_file_count: int
    expected_byte_count: int
    current_byte_count: int
    expected_sha256: str | None
    current_sha256: str | None
    status: str  # "ok" | "warning" | "error"
    messages: list[str]


@dataclass(frozen=True)
class ReleaseVerificationReport:
    schema_version: int
    release_id: str
    manifest_path: Path
    checked_at: datetime
    status: str  # "ok" | "warning" | "error"
    manifest_status: str | None
    path_status: str
    area_results: list[ReleaseAreaVerification]
    messages: list[str]
```

Suggested public functions:

```python
def select_release_manifest_path(paths: WikiPaths, selector: str) -> Path:
    ...


def verify_release(
    paths: WikiPaths,
    *,
    selector: str,
    allow_path_mismatch: bool = False,
    checked_at: datetime | None = None,
) -> ReleaseVerificationReport:
    ...


def release_verification_to_json(report: ReleaseVerificationReport) -> dict[str, object]:
    ...


def format_release_verification_text(report: ReleaseVerificationReport) -> str:
    ...
```

All public functions must have type hints and docstrings.

## Areas to Verify

Verify the areas already recorded by the release manifest:

- `raw_readwise`
- `reviews`
- `synthesis_cache`
- `render_graph`
- `render_manifest`
- `wiki`

Use the manifest's `areas` object as the expected data.

Use the current resolved paths for current data:

| Manifest area | Current path |
|---|---|
| `raw_readwise` | `paths.raw_dir` |
| `reviews` | `paths.reviews_dir` |
| `synthesis_cache` | `paths.synthesis_dir` |
| `render_graph` | `paths.graph_path` |
| `render_manifest` | `paths.manifest_path` |
| `wiki` | `paths.wiki_dir` |

If the manifest contains unknown areas, preserve them in JSON as warnings but do
not fail the entire verification unless required areas are missing.

If a required area is missing from the manifest, verification status is `error`.

## Comparison Rules

For each area compare:

- existence
- file count
- byte count
- sha256
- path

### Area `ok`

Area status is `ok` when:

- current path exists status matches expected
- file count matches
- byte count matches
- sha256 matches
- path matches or path mismatch was allowed and no content changed

### Area `warning`

Area status is `warning` when:

- path differs but `--verify-allow-path-mismatch` was passed
- manifest contains an unknown extra area
- manifest status was `warning`, but content still matches

### Area `error`

Area status is `error` when:

- current path is missing while manifest expected it to exist
- file count differs
- byte count differs
- sha256 differs
- path differs and path mismatch is not allowed
- required manifest area is missing
- current path hash cannot be computed

Use `error` rather than `warning` for content mismatch. This verifier is meant
to catch corruption or accidental edits.

## Overall Status

Overall status:

- `error` if any area is `error`, manifest cannot be loaded, schema is
  unsupported, or no release manifest can be selected.
- `warning` if no errors but any area/report warning exists.
- `ok` only when all required areas match and there are no report warnings.

Manifest status handling:

- If manifest status is `blocked`, overall status should be `warning` when
  content matches. The verifier is answering whether the manifest matches disk,
  not whether it was a perfect release.
- If manifest status is `warning`, overall status should be `warning` even when
  content matches.
- If manifest status is `ready` and content matches, overall status can be
  `ok`.

## CLI Integration

Extend:

```text
src/wiki_ops/status_cli.py
```

Add flags:

```bash
--verify-release <release_id|latest>
--verify-json
--verify-allow-path-mismatch
```

Behavior:

- `--verify-release` appends a readable verification section to the normal
  `wiki-ops-status` output.
- `--verify-release ... --verify-json` prints only verification JSON and exits.
- Verification mode is read-only.
- It must not write release manifests.
- It must not create missing directories.
- It must not run `wiki-render`.
- It must not call an LLM.

Exit codes:

- `0` for `ok` or `warning`
- `2` for `error`

Rationale:

- Warning means "human attention may be useful, but verification completed."
- Error means "release does not match disk or could not be verified."

## Text Output

Example:

```text
Release Verification
- release: 20260712T140520Z
- manifest: /Users/plischke/Desktop/Private Development/llm-wiki-data/state/releases/20260712T140520Z.json
- status: warning
- manifest status: warning

Areas
- raw_readwise: ok, 724 files, 11.1 MB
- reviews: ok, 378 files, 18.9 MB
- synthesis_cache: ok, 124 files, 697.7 KB
- render_graph: ok, 1 files, 13.8 MB
- render_manifest: ok, 1 files, 244.8 KB
- wiki: ok, 1294 files, 9.5 MB

Messages
- Manifest status is warning: Temporary artifacts were present when it was created.
```

If content mismatch exists:

```text
Release Verification
- release: 20260712T140520Z
- status: error

Areas
- wiki: error, sha256 differs
```

Keep the text concise. Detailed hashes can live in JSON.

## JSON Output

Example shape:

```json
{
  "schema_version": 1,
  "release_id": "20260712T140520Z",
  "manifest_path": ".../state/releases/20260712T140520Z.json",
  "checked_at": "2026-07-12T14:30:00Z",
  "status": "warning",
  "manifest_status": "warning",
  "messages": [
    "Manifest status is warning."
  ],
  "areas": [
    {
      "area_key": "raw_readwise",
      "expected_path": ".../raw/readwise",
      "current_path": ".../raw/readwise",
      "expected_file_count": 724,
      "current_file_count": 724,
      "expected_byte_count": 11588524,
      "current_byte_count": 11588524,
      "expected_sha256": "...",
      "current_sha256": "...",
      "status": "ok",
      "messages": []
    }
  ]
}
```

Paths should serialize as strings.

Do not include full file lists in this slice.

## Tests

Add tests for:

- selecting `latest` from multiple release manifests
- selecting an explicit release id
- missing release directory returns error
- malformed manifest returns error
- unsupported schema returns error
- all areas match returns `ok` when manifest status is `ready`
- all areas match returns `warning` when manifest status is `warning`
- file count mismatch returns `error`
- byte count mismatch returns `error`
- sha mismatch returns `error`
- missing required manifest area returns `error`
- path mismatch returns `error` by default
- path mismatch returns `warning` with `--verify-allow-path-mismatch`
- `--verify-json` emits valid JSON only
- normal `--verify-release latest` appends readable text to normal status
- verification does not create missing directories

Recommended files:

```text
tests/wiki_ops/test_release_verify.py
tests/wiki_ops/test_status_cli_release_verify.py
```

Run at least:

```bash
hatch run lint:check
hatch run test:run tests/wiki_ops/test_release_verify.py tests/wiki_ops/test_status_cli_release_verify.py tests/wiki_ops/test_release_manifest.py tests/wiki_ops/test_status_cli_release.py
```

If shared status CLI code changes significantly, also run:

```bash
hatch run test:run tests/wiki_ops/test_status_cli.py tests/wiki_ops/test_migration_plan.py tests/wiki_ops/test_status_cli_migration.py
```

## Live Smoke Tests

After implementation, run against the current external operating mode:

```bash
hatch run wiki-ops-status --verify-release latest
hatch run wiki-ops-status --verify-release latest --verify-json
hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root
```

Expected current behavior:

- selected latest release is in `<knowledge_root>/state/releases/`
- required areas verify by count/hash
- status may be `warning` because latest manifest status is currently `warning`
  due to retained temporary audit artifacts
- no cache warnings
- no render needed

## Acceptance Criteria

This slice is done when:

- `hatch run wiki-ops-status --verify-release latest` works
- `hatch run wiki-ops-status --verify-release <release_id>` works
- `--verify-json` returns machine-readable JSON only
- content drift produces `error`
- path mismatch is visible
- the command is read-only
- no new Hatch command is added
- tests cover success, warning, and error cases
- lint and type checks pass

## Future Slices

After release verification is implemented and trusted, later slices can define:

1. backup verification for `llm-wiki-data`
2. old repo-local data retirement
3. rollback planning
4. private vault Git strategy
5. server deployment path config

Do not implement those in this slice.
