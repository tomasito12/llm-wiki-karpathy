# Open Migration Findings

This document collects open findings from the repository/vault split and the
next decisions that must not get lost in chat history.

The system is currently in a transition state:

- the code repository has been separated from active generated knowledge data
- the external knowledge store is active
- the external private Obsidian vault is active
- backup, rollback, vault Git versioning, and cleanup policy are not fully
  finished yet

## 1. Private Vault Git Versioning

### Finding

The external private Obsidian vault currently lives at:

```text
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

It is the active generated vault target, but it is not yet its own Git
repository.

This is not the final desired state. Earlier planning documents said that the
generated wiki/vault output should probably be versioned separately from the
code repository, as long as the repository size remains manageable.

### Why This Matters

The generated vault is the human-readable end product. It should be possible to:

- see which pages changed after a render
- roll back a bad render or bad synthesis batch
- separate code commits from knowledge-output commits
- later share or publish selected wiki output without exposing code internals

### Risk

The vault already contains many generated Markdown files, including source pages
with embedded source access. A plain Git repository may still be fine, but this
must be checked before committing blindly.

Potential risks:

- repository size grows too quickly
- full source text may make diffs large
- copyrighted/private source content may make remote hosting sensitive
- rolling back only the vault while leaving the knowledge store newer could
  create inconsistent state

### Preferred Direction

Create a separate private Git repository for `llm-wiki-vault-private`, but only
after a small size and privacy check.

Git should version the generated end product:

- `wiki/`
- source pages needed for reading and agent access
- indexes

Git should not be used as the only backup for all raw/canonical knowledge data.
The knowledge store needs a separate backup/snapshot policy.

### Open Decisions

- Should `llm-wiki-vault-private` be pushed to a private GitHub repository or
  remain local-only at first?
- Should full source text be committed into the private vault repo, or should
  vault pages link to files in the knowledge store?
- Should Git LFS be considered later if vault size grows too fast?
- What should the automatic commit policy be after successful render?

### Next Step

Write and implement a small "private vault Git strategy" slice:

1. Measure vault size and file count.
2. Classify vault contents as safe-to-version or needs-review.
3. Initialize Git only if the report is acceptable.
4. Make the first manual commit.
5. Add later automation only after manual operation feels safe.

## 2. Raw Source Text Access

### Finding

The intended requirement is:

> A human and an agent must be able to get from a source page to the full raw
> source text with very little friction.

The current implementation may not yet satisfy this clearly enough.

The user observed that source pages appear to include metadata and links, but
not necessarily the full raw text itself. Links to the original URL are not
enough, because they may lead to a paywall, changed website, deleted article, or
page that requires login.

### Requirement

For every source that has a local raw export, the system must provide reliable
local access to the content that was actually processed.

This should work for:

- the user inside Obsidian
- local agents reading the vault or knowledge store
- future API/tool access

### Acceptable Implementation Options

There are two acceptable designs.

Option A: Embed full source text into the generated source page.

- Best for Obsidian browsing.
- Best for agent access through the vault.
- Makes the vault larger.
- May make private-vault Git heavier.

Option B: Keep source pages concise, but link to local raw exports.

- Keeps the vault smaller.
- Requires robust Obsidian-compatible local links.
- Requires agents to know how to resolve the link.
- Must not point only to the original web URL.

### Non-Acceptable State

The source page must not only provide:

- original article URL
- metadata
- summary
- source title

That is not enough, because it does not guarantee access to the text that was
actually ingested.

### Decision And Resolution

Resolved on 2026-07-13.

The private vault uses Option A: full raw Markdown is embedded into the existing
generated page at `wiki/sources/<source_id>.md`.

This is an explicit private-vault product decision:

- the knowledge store remains canonical
- the embedded page is a regenerable reading and agent-access copy
- no parallel `sources/full/` hierarchy is introduced
- raw exports that are not yet reviewed remain in the knowledge store and do
  not receive generated source pages until they enter the render graph
- future team/public exports must use an explicit safer source mode such as
  `summary`, `excerpt`, or `none`
- private-vault Git and remote-hosting decisions must treat embedded source text
  as potentially private or copyright-sensitive

`hatch run wiki-ops-status` now includes a read-only `Source Access` section.
It checks:

- source pages with embedded full text
- source pages with a clickable local raw Markdown link
- pages that expose only an external URL
- source-page-to-raw-Markdown alignment
- graph sources without a generated source page
- filename/frontmatter source-id consistency
- broken source wikilinks from managed generated pages

Verification against the active vault:

```text
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

reported:

```text
source pages: 360
embedded full text: 360
locally linked source text: 0
external URL only: 0
graph sources missing pages: 0
source pages missing raw markdown: 0
broken source wikilink targets: 0
```

Finding 2 is complete. Re-run `hatch run wiki-ops-status` after render or path
changes to prevent regressions.

## 3. Duplicate And Orphan Wiki Pages

### Finding

The active private vault appears to contain duplicate or orphaned generated
pages from older render structures.

Known example area:

- `interview-insights/`
- especially older 2026-04/2026-06 generated pages with similar GitHub-related
  titles

Previous inspection indicated that some duplicates have identical content and
the same source/evidence metadata, while only the filename differs.

### Why This Happened

The renderer is manifest-aware, but it only prunes files that were known in the
previous render manifest. If a file was never part of the current manifest
history, it can remain as an orphan.

This is expected during migration because historical repo-local and vault-local
files were moved and regenerated over time.

### Requirement

Duplicate and orphan cleanup should become part of the regular wiki linting
system, not another isolated one-off command that increases CLI sprawl.

The future lint/check should detect:

- files in the vault that are not present in the current render manifest
- exact duplicate pages
- same entity rendered under multiple filenames
- pages with same `source_id`, `slug`, or `evidence_set_hash`
- stale generated pages that no longer correspond to the graph

### Safety Requirement

The first implementation must be read-only.

It should not delete files automatically. It should produce a report with:

- safe delete candidates
- needs manual review candidates
- reason for each candidate
- current manifest path, if one exists

Actual cleanup should happen only after:

- release manifest exists
- vault backup or Git commit exists
- user approves deletion

### Next Step

Extend the existing wiki lint concept with an orphan/duplicate report.

Preferred behavior:

```text
hatch run wiki-lint
```

or the future consolidated ops status should include a section like:

```text
Vault Hygiene
- orphan generated pages: 30
- exact duplicate pages: 8 groups
- unsafe cleanup candidates: 0
- recommended action: review orphan report before deletion
```

## 4. Old Repo-Local Wiki Files Still Exist

### Finding

The old repo-local `wiki/` folder still exists physically inside the code
repository working tree.

It has been removed from Git tracking and is now ignored by `.gitignore`, but
the files were intentionally not deleted.

### Why This Was Done

The migration used `git rm --cached`, not deletion. This was deliberate:

- avoid destructive cleanup before backup is reliable
- keep a fallback copy during migration
- prevent accidental loss while path configuration is still settling

### User Impact

If Obsidian still opens the old code-repo folder, the user will see the old
structure and stale generated pages.

The active vault should be:

```text
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

not the code repository.

### Next Step

1. Confirm Obsidian is opening the external private vault.
2. Verify the external private vault contains the current render output.
3. After backup and vault Git strategy are in place, archive or delete the old
   repo-local `wiki/` folder.

Do not delete the old repo-local folder before the active vault is versioned or
backed up.

## 5. Automatic Commits After Knowledge Operations

### Finding

Earlier planning discussed automatic commits after successful knowledge
operations, but this is not implemented yet.

### Desired Future Behavior

After a successful operation, the system should be able to create transparent,
separate commits.

Examples:

- after approved ingestion/review: commit canonical review state or release
  snapshot, depending on final backup strategy
- after synthesis: commit synthesis cache changes or bind them to a release
- after render: commit generated vault output in the private vault repo
- after cleanup: commit removal of obsolete generated pages

### Important Constraint

Automatic commits must not hide changes.

Before automatic commit behavior is enabled, the system should provide:

- status report
- changed file summary
- release manifest or equivalent integrity anchor
- clear commit message
- no automatic push unless explicitly configured

### Next Step

Implement manual-first commit helpers before fully automatic commits.

For example:

```text
hatch run wiki-ops-status
hatch run wiki-render --dry-run --require-source-text
hatch run wiki-render --require-source-text
hatch run wiki-ops-status
```

Then a future helper could say:

```text
Vault has 24 generated file changes.
Recommended commit:
Render wiki after 5 new syntheses
```

Only later should the command perform the commit itself.

## 6. Readwise Index Is Canonical Bookkeeping

### Finding

During the external knowledge-store migration, raw Readwise exports were present
in the external raw directory, but the active external Readwise index was not
treated as equally critical operational state.

That allowed the dashboard sync to run against an effectively fresh
`readwise_library.json`. The command then used the initial Reader lookback
window and re-exported the available Readwise documents instead of recognizing
that most raw exports already existed.

### Why This Matters

`state/readwise_library.json` is not just a performance cache. It contains:

- the Readwise document id to raw filename mapping
- the incremental `last_updated_after` watermark
- `suppressed_ids` from duplicate cleanup
- the stable link between raw exports and existing review artifacts

If raw files move without the index, the system can:

- re-export a large Reader window unnecessarily
- lose duplicate suppression state
- produce new filename slugs when Readwise titles changed
- orphan existing review artifacts, because reviews are keyed by raw filename
  stem

### Current Repair

The active external knowledge store has been repaired so that:

- raw export pairs and index entries are aligned
- old suppressed ids are restored
- existing review artifacts again have matching raw source files
- replaced/quarantined files are preserved under the external knowledge store
  `tmp/` repair folders

There are still near-duplicate candidates reported by `readwise-dedupe
--dry-run`. These were not deleted automatically because they require the normal
dedupe policy/manual review.

### New Safety Rule

Real `readwise-sync` must fail closed when:

- the configured raw directory already contains exports, and
- the configured Readwise index is missing or empty, and
- the operator has not explicitly passed `--allow-index-bootstrap`.

`--allow-index-bootstrap` is only acceptable for an intentional first sync into a
confirmed fresh raw directory.

### Agent Checklist

Before any migration-sensitive Readwise operation, run:

```text
hatch run wiki-ops-status
hatch run readwise-rebuild-index --dry-run --paths-config config/wiki_paths.toml --force
hatch run readwise-dedupe --dry-run --paths-config config/wiki_paths.toml
hatch run ingest-queue --status all --json
```

The status report must expose Readwise index health, not only raw file counts.

## 7. Legacy Root Pages And Manual Vault Folders

### Finding

The active private vault still contains legacy/manual pages and folders directly
under the generated wiki root that may no longer fit the current generated
Obsidian structure.

Observed examples in the active vault:

```text
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki/log.md
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki/AGENTS.md
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki/legacy/
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki/notes/
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/wiki/questions/
```

The `log.md` root page appears to be a legacy "Log Index" style page. It is not
clear whether it still has a useful role now that generated indexes and ops
status pages exist. The same uncertainty applies to `legacy/`, `notes/`, and
`questions/`. `AGENTS.md` may still be useful for Obsidian/agent context, but
its ownership and placement should be reviewed.

### Why This Matters

The generated wiki should have a clear information architecture. Old manual
pages at the root can confuse both humans and agents because they look as
important as the generated index, even when they are stale.

This matters especially because:

- root-level pages are high-salience in Obsidian
- agents may treat root files as current instructions or navigation
- manual folders may duplicate newer generated indexes or notes
- deleting too eagerly could remove useful historical context

### Requirement

Do not delete these pages ad hoc. First create a read-only vault hygiene review
that classifies root/manual items as:

- keep as active navigation or instruction
- move to an archive/manual area
- fold into generated indexes or docs
- safe delete after backup/versioning
- needs human review

### Next Step

Extend the planned vault hygiene/orphan report to include non-managed root
items and manual folders.

The report should list:

- root-level files besides `index.md`
- non-managed folders such as `legacy/`, `notes/`, and `questions/`
- whether each item is referenced by current generated pages
- last modified time and approximate content purpose
- recommended action, without deleting anything automatically

Cleanup should happen only after:

- the private vault is backed up or versioned
- the report is reviewed
- the user approves deletion/move/archive actions

## Working Order

Recommended order from here:

1. Path-configuration/dashboard slice — completed.
2. Raw source text access verification and private full-text decision — completed.
3. Decide private vault Git strategy.
4. Initialize/version the private vault if approved.
5. Add read-only vault duplicate/orphan lint.
6. Review legacy root pages and manual vault folders (`log.md`, `legacy/`,
   `notes/`, `questions/`, root `AGENTS.md`).
7. Clean or archive old repo-local wiki files.
8. Design manual-first commit helpers.
9. Keep Readwise raw/index/review alignment visible in `wiki-ops-status`.
10. Only then add automatic commit behavior.
