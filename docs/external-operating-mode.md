# External Knowledge Store Operating Mode

Last updated: 2026-07-12

This document describes the current preferred local operating mode after the
copy-only migration.

## Summary

The project now separates the code repository from active knowledge data and
the generated private Obsidian vault.

The current local layout is:

```text
Code repo:
/Users/plischke/Desktop/Private Development/llm-wiki-karpathy-source-access-spec

Knowledge store:
/Users/plischke/Desktop/Private Development/llm-wiki-data

Private generated vault:
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

The migration was copy-only. The old in-repo data was not deleted.

## Source of Truth

Use this rule:

Canonical knowledge data now lives in the external knowledge store.

That includes:

- `raw/readwise/`
- `state/reviews/`
- `state/synthesis/`
- `state/wiki_render_graph.json`
- `state/wiki_render_manifest.json`
- `state/releases/`

Generated Obsidian-readable output now lives in the private vault:

- `wiki/`

The code repository remains responsible for:

- `src/`
- `tests/`
- `docs/`
- `config/*.example.toml`
- prompt/config templates
- Hatch scripts and Python tooling

## Local Path Config

The active paths are controlled by:

```text
config/wiki_paths.toml
```

This file is machine-specific and intentionally gitignored.

To recreate it, copy:

```text
config/wiki_paths.example.toml
```

Then adjust the absolute paths for the current machine.

The current example uses:

```toml
knowledge_root = "/Users/plischke/Desktop/Private Development/llm-wiki-data"
vault_root = "/Users/plischke/Desktop/Private Development/llm-wiki-vault-private"
```

Commands load this config automatically when `config/wiki_paths.toml` exists.
You can also point to another config explicitly:

```bash
hatch run wiki-ops-status --paths-config /path/to/wiki_paths.toml
```

## Standard Health Check

Use this after pipeline work:

```bash
hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root
hatch run wiki-synthesis-cache-lint
hatch run wiki-render --dry-run --require-source-text
hatch run wiki-lint
```

Expected healthy baseline after the first copy-only migration:

```text
Sources: 362 paired exports
Reviews: 360 artifacts
Synthesis: 124 fresh, 0 stale, 0 errors
Render dry-run: written=0
Source full text coverage: 358/360
Migration areas: raw, reviews, synthesis, graph, manifest, releases, and wiki already external
```

The migration plan may still show `warning` while retained audit artifacts such
as `synthesis_runs` exist. That is not a data migration failure. The current
cleanup slice intentionally keeps run reports as audit data.

## Normal Workflow

For normal operation, use the same commands as before. With
`config/wiki_paths.toml` present, they read and write external paths.

Typical flow:

```bash
hatch run wiki-ops-status
hatch run wiki-synthesis-plan --changed-only --limit 20
hatch run wiki-synthesis-workflow --entity topic:example --yes
hatch run wiki-synthesis-cache-lint
hatch run wiki-render --dry-run --require-source-text
hatch run wiki-render --require-source-text
hatch run wiki-ops-status --write-release-manifest --yes
```

Do not hand-edit generated vault pages. Fix review artifacts or synthesis cache
entries and rerender.

## Cleanup Policy

Cleanup is allowed only for temporary artifacts and only after a release
manifest exists.

Dry-run first:

```bash
hatch run wiki-cleanup --dry-run
```

Real cleanup:

```bash
hatch run wiki-cleanup --after-release <release_id> --yes
```

Current cleanup removes only allowlisted temporary areas such as synthesis
previews and synthesis backups. It keeps synthesis run reports for audit.

## Git Policy

The real `config/wiki_paths.toml` is not committed.

Commit:

- code
- tests
- docs
- example config files
- durable release artifacts when they intentionally belong to the code repo

Do not commit:

- machine-specific path config
- local secrets
- raw data copied only for local operation
- generated temporary previews or run reports unless there is a deliberate
  audit reason

The external knowledge store and private vault are not yet separate Git repos in
this slice. Backup/versioning policy for those directories should be handled in
a later step.

## Current Release Markers

The first external migration produced these markers:

- pre-cleanup release: `20260712T140439Z`
- cleanup report: `state/cleanup_runs/20260712T140456Z.json`
- post-cleanup release: `20260712T140520Z`

These live in the external knowledge store.

## What Not To Do Yet

Do not delete the old in-repo `state/` or `wiki/` data yet.

Do not assume the external store is backed up just because it exists.

Do not expose the private vault publicly. Source pages contain full source text
and may include copyrighted or sensitive material.

## Next Stabilization Steps

Recommended next slices:

1. Add a copy-verification command that compares old and external stores by
   count and hash.
2. Decide backup strategy for `llm-wiki-data`.
3. Decide whether `llm-wiki-vault-private` should become its own private Git
   repo.
4. Add server path examples for the future Hetzner deployment.
