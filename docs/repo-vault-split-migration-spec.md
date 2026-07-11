# Technical Specification: Repository and Vault Split Migration

Last updated: 2026-07-11

This specification defines how to move from the current single-repository
layout toward a cleaner separation between code, knowledge data, and Obsidian
vault content.

It is intended for an implementation agent that has no prior chat context.

## Current Problem

The current repository mixes several concerns:

- Python code and tests
- configuration
- raw Readwise exports
- review state
- synthesis cache
- temporary previews and run reports
- generated Obsidian wiki pages
- future private notes and meeting transcripts

This makes the system feel hard to maintain.

The user wants a product-like architecture where:

- code development does not mix with generated knowledge changes
- raw data is backed up safely
- Obsidian has direct access to full source text
- future server deployment has clear paths
- future team/public export can be filtered
- rollbacks restore consistent knowledge releases

## Target Architecture

Use three logical areas:

```text
code repo
knowledge store
private vault
```

These may initially still live on the same machine. The first implementation
should make paths configurable before moving files.

### Code Repo

Example:

```text
llm-wiki-karpathy/
  src/
  tests/
  docs/
  config/
  pyproject.toml
  README.md
```

Contains:

- application code
- tests
- prompts
- config templates
- architecture docs
- CLI wiring

Does not own long-term generated knowledge data.

### Knowledge Store

Example:

```text
llm-wiki-data/
  raw/
    readwise/
  state/
    reviews/
    synthesis/
    wiki_render_graph.json
    wiki_render_manifest.json
    releases/
  tmp/
    synthesis_previews/
    synthesis_runs/
    synthesis_backups/
    synthesis_prompts/
    ingest_batches/
```

Contains:

- raw source exports
- canonical review artifacts
- canonical synthesis cache
- render graph/manifest
- release manifests
- temporary operational artifacts

Recommended storage:

- local/server filesystem
- backed up by snapshot/backup tooling
- not necessarily a Git repo

### Private Vault

Example:

```text
llm-wiki-vault-private/
  wiki/
  sources/
    full/
    index.md
  indexes/
  attachments/
```

Contains:

- generated Obsidian wiki pages
- full local source pages
- indexes
- attachments if needed

This vault is primarily for the user and local agents.

### Private Notes Vault

Personal daily notes, meeting transcripts, and confidential work notes should
live in a separate Obsidian vault or separate top-level private area.

Recommended:

```text
plischke-work-private-vault/
  daily/
  meetings/
  projects/
  notes/
```

Reason:

- may contain EnBW, customer, or meeting-sensitive data
- should not be mixed with a future team-facing article wiki
- can still be indexed by an agent later with separate permissions

## Why Separate Vaults?

Two vaults add some operational overhead, but they create safer boundaries:

- article/wiki vault can later be shared or published in filtered form
- private notes vault remains confidential by default
- server/API permissions can differ
- accidental publication risk is lower

The generated wiki should not be hand-edited. Personal notes should be
hand-edited freely in the private notes vault.

## Path Configuration Requirement

Before moving files, introduce a central path configuration layer.

Goal:

Commands should no longer assume all important paths are inside the code repo.

Suggested config file:

```text
config/wiki_paths.toml
```

Example:

```toml
[paths]
code_root = "/Users/plischke/Desktop/Private Development/llm-wiki-karpathy"
knowledge_root = "/Users/plischke/Desktop/Private Development/llm-wiki-data"
vault_root = "/Users/plischke/Documents/Obsidian/llm-wiki-vault-private"

raw_dir = "{knowledge_root}/raw/readwise"
reviews_dir = "{knowledge_root}/state/reviews"
synthesis_dir = "{knowledge_root}/state/synthesis"
graph_path = "{knowledge_root}/state/wiki_render_graph.json"
manifest_path = "{knowledge_root}/state/wiki_render_manifest.json"
release_dir = "{knowledge_root}/state/releases"

preview_dir = "{knowledge_root}/tmp/synthesis_previews"
run_dir = "{knowledge_root}/tmp/synthesis_runs"
backup_dir = "{knowledge_root}/tmp/synthesis_backups"

wiki_dir = "{vault_root}/wiki"
source_pages_dir = "{vault_root}/sources/full"
source_index_path = "{vault_root}/sources/index.md"
indexes_dir = "{vault_root}/indexes"
```

Implementation note:

- support environment override, for example `LLM_WIKI_PATHS_CONFIG`
- keep current defaults when config is absent
- expand `{knowledge_root}` and `{vault_root}` placeholders
- resolve paths to absolute paths internally

## Commands That Need Path Support

At minimum:

- `wiki-ops-status`
- `wiki-render`
- `wiki-synthesis-plan`
- `wiki-synthesis-select`
- `wiki-synthesis-batch`
- `wiki-synthesis-cache-lint`
- `wiki-synthesis-workflow`
- `wiki-synthesis-review`
- ingest review/dashboard paths later

Do not migrate all commands in one risky change if that becomes too large.
Start with render/synthesis/status.

## Migration Strategy

Use small steps with dry-runs.

### Phase 1: Path Config Without Moving Data

Implement central path config while defaults still point to current repo paths.

Acceptance:

- all existing tests pass
- existing commands behave exactly as before without config
- commands can print resolved paths for debugging

### Phase 2: External Knowledge Store Dry-Run

Create a dry-run migration command or script specification.

It should report what would move:

```text
raw/readwise -> <knowledge_root>/raw/readwise
state/reviews -> <knowledge_root>/state/reviews
state/synthesis -> <knowledge_root>/state/synthesis
state/wiki_render_graph.json -> <knowledge_root>/state/wiki_render_graph.json
state/wiki_render_manifest.json -> <knowledge_root>/state/wiki_render_manifest.json
state/synthesis_previews -> <knowledge_root>/tmp/synthesis_previews
state/synthesis_runs -> <knowledge_root>/tmp/synthesis_runs
state/synthesis_backups -> <knowledge_root>/tmp/synthesis_backups
```

No writes by default.

### Phase 3: Copy, Do Not Move

First real migration should copy data, not move it.

Reason:

- easy rollback
- no data loss if config is wrong
- user can compare old/new outputs

### Phase 4: Run Pipeline Against External Paths

Run:

```bash
hatch run wiki-ops-status
hatch run wiki-synthesis-select --limit 5
hatch run wiki-render --dry-run
```

using external path config.

Acceptance:

- counts match old setup
- no broken source links
- render dry-run is stable or expected

### Phase 5: Switch Default Operating Mode

Once verified:

- code repo no longer stores active knowledge data
- knowledge store and vault are the active paths
- old in-repo data folders are marked deprecated

### Phase 6: Cleanup Old Repo Data

Only after backups and release manifests exist.

Do not delete old data as part of the initial migration.

## Git Strategy

### Code Repo

Always Git-versioned.

Contains:

- code
- tests
- docs
- config templates

### Knowledge Store

Default recommendation:

- not a Git repo initially
- backed up by snapshot tooling
- release manifests hash canonical state

Reason:

Raw files and operational state can grow large, and Git is not ideal as the
primary backup for everything.

### Private Vault

Can be a private Git repo if size remains reasonable.

Contains:

- generated wiki pages
- generated source Markdown pages
- indexes

If source pages become too large, switch to backup/snapshot only or use Git LFS
for selected large files. Do not make that decision prematurely.

### Private Notes Vault

Separate policy.

Because it may contain confidential work and meeting data, do not mix it with
the generated article wiki repo.

## Rollback Strategy

Rollback must be release-based.

Do not roll back only the vault repo while leaving reviews/synthesis state at a
newer version.

A release manifest should bind:

- code commit
- path config hash
- raw snapshot id
- reviews hash
- synthesis hash
- graph hash
- wiki hash
- sources hash
- index hash

Rollback should restore or verify all of those.

## Server Preparation

The split should prepare for this later server layout:

```text
/srv/llm-wiki/app
/srv/llm-wiki/data
/srv/llm-wiki/vault-private
/srv/llm-wiki/vault-public
/srv/llm-wiki/backups
```

The server may:

- pull the code repo
- run cron jobs
- store raw and canonical data
- host an API
- host a filtered website later

The server should not expose raw/private data publicly by default.

## Temporary Folder Reduction

As part of this migration, move temporary folders out of the durable `state/`
surface:

Current:

```text
state/synthesis_previews/
state/synthesis_runs/
state/synthesis_backups/
```

Target:

```text
<knowledge_root>/tmp/synthesis_previews/
<knowledge_root>/tmp/synthesis_runs/
<knowledge_root>/tmp/synthesis_backups/
```

This makes it obvious they are not durable knowledge.

## Implementation Specs to Create Next

Break implementation into smaller Cursor tasks:

1. Path configuration module.
2. Source page generation and linking.
3. Release manifest generator.
4. External path support for render/synthesis/status.
5. Migration dry-run/copy tool.
6. Cleanup tool for temporary artifacts.
7. Server deployment and backup spec.

Do not combine all of these into one large implementation.

## Acceptance Criteria

The migration architecture is successful when:

- code can run with current in-repo defaults
- code can run with external knowledge/vault paths
- full source pages are accessible from Obsidian
- raw data is preserved outside the code repo
- generated wiki and source pages are separated from canonical state
- temporary artifacts are no longer confused with durable data
- rollback is release-based, not folder-by-folder guesswork

