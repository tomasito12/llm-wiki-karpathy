# Technical Specification: Knowledge Store Migration Plan

Last updated: 2026-07-12

This specification defines the next implementation slice after:

1. central path configuration
2. source pages with full source text
3. artifact retention inventory
4. release manifest prototype
5. temporary artifact cleanup

It is intended for Cursor or another implementation agent that has no prior chat
context.

## Background

The project is `llm-wiki-karpathy`, a local AI knowledge-base system.

It currently ingests Readwise exports, stores human review artifacts, creates
Stage 2 synthesis cache entries, renders an Obsidian wiki, and keeps temporary
operational artifacts such as previews, run reports, backups, and prompt
previews.

The long-term architecture should separate:

- code and tests
- canonical knowledge data
- generated Obsidian vault output
- temporary operational artifacts
- private personal notes

The user wants this separation because the current all-in-one repository makes
normal operation feel noisy and risky. Knowledge operations create Git changes
while code development is happening. Raw data is not yet backed up in a clean
place. Temporary folders can look like durable state. Rollback boundaries are
not obvious enough.

The project already has a central path configuration layer. This means commands
can now resolve `knowledge_root`, `vault_root`, `raw_dir`, `reviews_dir`,
`synthesis_dir`, `wiki_dir`, `release_dir`, and temporary artifact directories.

The next step is not to move files yet.

The next step is to create a read-only migration planning layer that explains
what would move, what would stay, what is missing, and whether the current
system is ready for a future copy-based migration.

## Goal

Add a read-only knowledge-store migration plan.

The implementation should answer:

- Which current paths are still inside the code repository?
- Which paths are already external through path configuration?
- Which folders are canonical, generated, or temporary?
- Which data would be copied into a future knowledge store?
- Which data would be rendered into a future vault?
- Which data should stay in the code repo?
- Which paths are missing, empty, or suspicious?
- Are current release, cleanup, and render artifacts consistent enough to start
  a future copy migration?

This slice must make the future split understandable before any file movement
happens.

## Product Direction

The user does not want a growing pile of Hatch commands.

Therefore, this slice should not add a new Hatch script.

Extend the existing read-only ops command:

```bash
hatch run wiki-ops-status --migration-plan
hatch run wiki-ops-status --migration-json
```

Rationale:

- `wiki-ops-status` is already the operational overview command.
- The migration plan is read-only status information.
- A future real copy/migration command can be added later if needed, but only
  after the plan is useful and trusted.

## Non-Goals

Do not implement in this slice:

- copying files
- moving files
- deleting old in-repo data
- editing `.gitignore`
- creating a new repository
- creating a backup
- creating a release manifest
- running `wiki-render`
- running synthesis
- committing files
- server deployment
- public/team export filtering
- private notes migration
- Obsidian vault publishing

This slice is only a read-only migration planner.

## Relationship to Existing Specs

Use these documents as context:

- `docs/repo-vault-split-migration-spec.md`
- `docs/data-ownership-retention-spec.md`
- `docs/path-configuration-technical-spec.md`
- `docs/artifact-retention-inventory-spec.md`
- `docs/release-manifest-prototype-spec.md`
- `docs/temporary-artifact-cleanup-spec.md`
- `docs/source-page-fulltext-implementation-spec.md`

This specification implements the planning part of Phase 2 from
`repo-vault-split-migration-spec.md`.

It must reuse the path configuration and retention inventory rather than
duplicating folder classification logic.

## Target Architecture Reminder

The intended future layout is:

```text
code repo
knowledge store
private vault
private notes vault
```

### Code Repo

Contains:

- `src/`
- `tests/`
- `docs/`
- `config/`
- `pyproject.toml`
- code-facing README and agent instructions

Should not own long-term generated knowledge data.

### Knowledge Store

Contains canonical and operational knowledge data:

- `raw/readwise/`
- `state/reviews/`
- `state/synthesis/`
- `state/wiki_render_graph.json`
- `state/wiki_render_manifest.json`
- `state/releases/`
- `tmp/synthesis_previews/`
- `tmp/synthesis_runs/`
- `tmp/synthesis_backups/`
- `tmp/synthesis_prompts/`
- `tmp/ingest_batches/`

The knowledge store may initially be a normal local/server directory with
backups, not necessarily a Git repository.

### Private Vault

Contains generated Obsidian-readable output:

- generated wiki pages
- generated source pages with full source text
- generated indexes
- attachments if needed later

The generated wiki should not be hand-edited.

### Private Notes Vault

Contains personal daily notes, meeting transcripts, project notes, and
confidential work material.

It is intentionally out of scope for this migration planner. It should have a
separate privacy and backup policy later.

## Migration Classification

The migration plan should classify each managed path with these fields:

```text
area_key
current_path
target_path
current_location
target_location
data_class
migration_action
exists
file_count
byte_count
status
warnings
```

### current_location

Allowed values:

- `code_repo`
- `knowledge_store`
- `vault`
- `external`
- `missing`

Use resolved absolute paths.

`code_repo` means the path is under `paths.repo_root`.

`knowledge_store` means the path is under `paths.knowledge_root` and
`knowledge_root` differs from `repo_root`.

`vault` means the path is under `paths.vault_root` and `vault_root` differs from
`repo_root`.

`external` means the path exists outside all three known roots.

`missing` means the path does not exist.

### target_location

Allowed values:

- `code_repo`
- `knowledge_store`
- `vault`
- `none`

`none` is allowed only for temporary areas that may be cleaned instead of moved
in a later phase.

### data_class

Reuse retention classes:

- `canonical`
- `generated`
- `temporary`

### migration_action

Allowed values:

- `keep_in_code_repo`
- `copy_to_knowledge_store`
- `copy_to_vault`
- `already_external`
- `cleanup_candidate`
- `ignore_missing`
- `manual_decision_required`

Do not use `move_*` in this slice. Future migration must start with copy-first
behavior.

## Managed Areas

The plan must include at least these areas.

| Area key | Data class | Target location | Expected target |
|---|---:|---:|---|
| `raw_readwise` | canonical | knowledge_store | `paths.raw_dir` |
| `reviews` | canonical | knowledge_store | `paths.reviews_dir` |
| `synthesis` | canonical | knowledge_store | `paths.synthesis_dir` |
| `render_graph` | generated release artifact | knowledge_store | `paths.graph_path` |
| `render_manifest` | generated release artifact | knowledge_store | `paths.manifest_path` |
| `releases` | canonical release metadata | knowledge_store | `paths.release_dir` |
| `wiki` | generated | vault | `paths.wiki_dir` |
| `synthesis_previews` | temporary | none or knowledge_store tmp | `paths.preview_dir` |
| `synthesis_runs` | temporary audit | knowledge_store tmp | `paths.run_dir` |
| `synthesis_backups` | temporary | none or knowledge_store tmp | `paths.backup_dir` |
| `synthesis_prompts` | temporary | none or knowledge_store tmp | `<knowledge_root>/tmp/synthesis_prompts` or configured equivalent |
| `ingest_batches` | temporary audit | knowledge_store tmp | `<knowledge_root>/tmp/ingest_batches` or configured equivalent |
| `config` | canonical code/config | code_repo | `config/` |
| `docs` | code documentation | code_repo | `docs/` |

Use the existing retention area definitions for canonical/generated/temporary
classification where possible.

The plan should not invent a durable `sources/full/` directory if the current
renderer uses generated source pages under `wiki/sources/<source_id>.md`.

## Readiness Checks

The migration plan should include an overall readiness status:

- `ready`
- `warning`
- `blocked`

### Blocked Conditions

The plan is `blocked` if:

- required canonical data is missing:
  - raw source directory
  - reviews directory
  - synthesis directory, if synthesis cache entries exist in status counts
- path configuration cannot be loaded
- a configured target path escapes its intended root
- `knowledge_root` equals `repo_root` while the user requested an external
  migration target
- `vault_root` equals `repo_root` while the user requested an external vault
  target
- a target path overlaps with a source path in a way that would make copy
  planning ambiguous
- retention inventory fails

### Warning Conditions

The plan is `warning` if:

- temporary artifacts exist and should be cleaned after a release before a real
  migration
- no release manifest exists
- the latest release manifest is `warning`
- `wiki-render` appears needed
- uncommitted durable files exist
- source text coverage is low or unknown
- graph or manifest is missing but could be regenerated
- a target path does not exist yet but can be created later

### Ready Conditions

The plan is `ready` only if:

- canonical paths exist
- path configuration is valid
- no blocking path overlap exists
- current ops status has no cache errors
- no render is needed according to the same logic used by `wiki-ops-status`
- there is at least one non-blocked release manifest, or the report clearly
  states that a release should be created before any future real migration

The first implementation may be conservative. It is better to return `warning`
than to incorrectly return `ready`.

## Internal Module

Add a small module:

```text
src/wiki_ops/migration_plan.py
```

Suggested dataclasses:

```python
@dataclass(frozen=True)
class MigrationAreaPlan:
    area_key: str
    current_path: Path
    target_path: Path | None
    current_location: str
    target_location: str
    data_class: str
    migration_action: str
    exists: bool
    file_count: int
    byte_count: int
    status: str
    warnings: list[str]


@dataclass(frozen=True)
class MigrationReadiness:
    status: str
    blocked_reasons: list[str]
    warnings: list[str]
    recommended_next_actions: list[str]


@dataclass(frozen=True)
class KnowledgeStoreMigrationPlan:
    created_at: datetime
    repo_root: Path
    knowledge_root: Path
    vault_root: Path
    areas: list[MigrationAreaPlan]
    readiness: MigrationReadiness
```

Suggested public functions:

```python
def build_migration_plan(
    paths: WikiPaths,
    *,
    require_external_knowledge_root: bool = False,
    require_external_vault_root: bool = False,
) -> KnowledgeStoreMigrationPlan:
    ...


def migration_plan_to_json(plan: KnowledgeStoreMigrationPlan) -> dict[str, object]:
    ...


def format_migration_plan_text(plan: KnowledgeStoreMigrationPlan) -> str:
    ...
```

All public functions must have type hints and docstrings.

## CLI Integration

Extend:

```text
src/wiki_ops/status_cli.py
```

Add:

```bash
--migration-plan
--migration-json
--require-external-knowledge-root
--require-external-vault-root
```

Behavior:

- `--migration-plan` appends a readable migration section to the normal status
  report.
- `--migration-json` outputs only the migration plan JSON.
- `--require-external-knowledge-root` turns repo-local `knowledge_root` into a
  blocked condition.
- `--require-external-vault-root` turns repo-local `vault_root` into a blocked
  condition.
- The command remains read-only.
- It must not create missing target directories.

Use existing path config flags from `wiki-ops-status`.

Do not add a new Hatch script.

## Text Output

Readable output should be concise.

Example:

```text
Knowledge Store Migration Plan

Readiness: warning

Roots
- repo: /Users/plischke/Desktop/Private Development/llm-wiki-karpathy
- knowledge: /Users/plischke/Desktop/Private Development/llm-wiki-data
- vault: /Users/plischke/Documents/Obsidian/llm-wiki-vault-private

Areas
- raw_readwise: copy_to_knowledge_store, 724 files, 88.2 MB
- reviews: copy_to_knowledge_store, 360 files, 12.4 MB
- synthesis: copy_to_knowledge_store, 124 files, 1.8 MB
- wiki: copy_to_vault, 614 files, 9.5 MB
- synthesis_previews: cleanup_candidate, 124 files, 908.2 KB

Warnings
- Temporary artifacts exist. Run cleanup after a non-blocked release before a real migration.
- No external knowledge_root is configured yet.

Recommended next actions
1. Create or update config/wiki_paths.toml with external knowledge_root and vault_root.
2. Run wiki-ops-status --migration-plan --require-external-knowledge-root.
3. Create a release manifest before any future copy migration.
```

## JSON Output

JSON output should be deterministic enough for tests and future web UI use.

Paths should be serialized as strings.

Example shape:

```json
{
  "schema_version": 1,
  "created_at": "2026-07-12T22:30:00Z",
  "roots": {
    "repo_root": "...",
    "knowledge_root": "...",
    "vault_root": "..."
  },
  "readiness": {
    "status": "warning",
    "blocked_reasons": [],
    "warnings": ["No external knowledge_root is configured yet."],
    "recommended_next_actions": ["Create config/wiki_paths.toml"]
  },
  "areas": [
    {
      "area_key": "raw_readwise",
      "current_path": ".../raw/readwise",
      "target_path": ".../raw/readwise",
      "current_location": "code_repo",
      "target_location": "knowledge_store",
      "data_class": "canonical",
      "migration_action": "copy_to_knowledge_store",
      "exists": true,
      "file_count": 724,
      "byte_count": 92484403,
      "status": "ok",
      "warnings": []
    }
  ]
}
```

## Path and Overlap Safety

The planner must detect dangerous or confusing path relationships.

Examples:

- `knowledge_root` inside `vault_root`
- `vault_root` inside `knowledge_root`
- `raw_dir` inside `wiki_dir`
- `wiki_dir` inside `raw_dir`
- target path equal to source path when external root is required
- generated vault path under canonical raw/review/synthesis paths

The planner is read-only, so these checks do not protect a deletion operation.
They protect the user from creating a bad migration design.

## Counting Rules

Use the same inventory behavior as retention:

- do not follow symlink directories
- count regular files only
- count bytes from file metadata
- missing paths count as zero files and zero bytes
- single files such as graph and manifest should count as one file if present

Do not read full file contents for counting.

## Recommended Actions

Recommended actions should be conservative and actionable.

Examples:

- "Create a non-blocked release manifest before real migration."
- "Run temporary cleanup after release before copy migration."
- "Configure an external knowledge_root before requiring external migration."
- "Run wiki-render before migration because rendered wiki is not current."
- "Resolve uncommitted durable files before migration."

Avoid vague recommendations such as "check everything".

## Tests

Add tests for:

- default repo-local layout returns a warning, not a crash
- `--migration-plan` appends a readable section
- `--migration-json` emits valid JSON only
- requiring external knowledge root blocks when `knowledge_root == repo_root`
- requiring external vault root blocks when `vault_root == repo_root`
- external paths are classified as `knowledge_store` and `vault`
- missing optional temporary paths are warnings or ok, not blockers
- missing required canonical paths block or warn according to the rules above
- path overlap detection blocks unsafe layouts
- file counting ignores symlink directories
- no files or directories are created during planning

Run at least:

```bash
hatch run lint:check
hatch run test:run tests/wiki_ops/test_migration_plan.py tests/wiki_ops/test_status_cli_migration.py
```

If the change touches shared status code, also run the existing status,
retention, release, and cleanup tests.

## Acceptance Criteria

This slice is done when:

- `hatch run wiki-ops-status --migration-plan` works without writing files
- `hatch run wiki-ops-status --migration-json` returns machine-readable JSON
- the plan classifies current repo-local paths clearly
- the plan can be run against an external path config
- unsafe path overlaps are detected
- missing or empty important data paths are visible
- no files are copied, moved, deleted, or created
- tests cover both default and external path configurations
- lint and type checks pass

## Future Slices

After this spec is implemented and trusted, later specs can define:

1. copy-only migration execution
2. verification of copied knowledge store against old paths
3. switching default operating config to external paths
4. release-based rollback verification
5. server deployment layout
6. backup integration

Do not implement those in this slice.
