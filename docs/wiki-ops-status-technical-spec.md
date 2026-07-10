# Technical Specification: Wiki Ops Status Layer

Last updated: 2026-07-10

This specification is intended for an implementation agent that has no prior
chat context. It explains the system background, the concrete feature to build,
and the acceptance criteria.

## Background Context

This repository is `llm-wiki-karpathy`, a local AI knowledge-base system.

The system ingests articles from Readwise, lets the user review LLM-extracted
knowledge fragments, renders a generated Obsidian wiki, and optionally creates
Stage 2 synthesis pages that combine evidence from multiple sources.

The user wants to evolve the project from a collection of CLI commands and a
Streamlit dashboard into a more reliable product with:

- a future elegant web management UI
- safer automation
- clear operating status
- cost-aware LLM workflows
- possible team-facing wiki publication later

Before building the web UI or automation, we need a small operational status
layer. This layer should summarize the current state of the system in one
command and provide a JSON output that a future frontend can consume.

The immediate feature is a new CLI command:

```bash
hatch run wiki-ops-status
```

It should make no LLM calls and should not modify files.

## Current System Architecture

Important paths:

- `raw/readwise/`
  - Local Readwise exports.
  - Usually paired `.html` and `.md` files.
  - Not committed to Git.

- `state/reviews/<source_id>/review.json`
  - Human-reviewed extraction artifacts.
  - These are the canonical source of truth for generated wiki content.

- `wiki/`
  - Generated Obsidian wiki output.
  - Managed pages should not be hand-edited.

- `state/wiki_render_manifest.json`
  - Advisory manifest from `wiki-render`.
  - Contains rendered file paths and hashes.

- `state/wiki_render_graph.json`
  - Machine-readable graph export from `wiki-render`.
  - Used by Stage 2 synthesis planning/execution.

- `state/synthesis/<category>/<slug>.json`
  - Final Stage 2 synthesis cache entries.
  - These are durable artifacts and should usually be committed.

- `state/synthesis_previews/`
  - Rendered Markdown previews for human review.
  - Transitional/review artifacts. Do not commit by default.

- `state/synthesis_runs/`
  - Audit reports from real synthesis workflow runs.
  - Transitional/audit artifacts. Do not commit by default.

- `state/synthesis_backups/`
  - Backup artifacts created by refreshes.
  - Transitional artifacts. Do not commit by default unless deliberately needed.

Key existing commands:

```bash
hatch run readwise-sync
hatch run wiki-render
hatch run wiki-render --dry-run
hatch run wiki-synthesis-plan --changed-only --limit 20
hatch run wiki-synthesis-cache-lint
hatch run wiki-synthesis-workflow --entity topic:example --yes
hatch run wiki-lint
hatch run lint:check
hatch run test:run
hatch run test:cov
```

Important docs:

- `docs/current-system-status.md`
- `docs/second-brain-vision.md`
- `docs/product-roadmap-spec.md`
- `src/AGENTS.md`
- `wiki/AGENTS.md`

## Problem

The system currently has many commands and many state directories. The user can
operate it, but it creates cognitive load:

- Which sources are pending review?
- Is the wiki render clean?
- Are synthesis caches fresh?
- How many changed synthesis candidates remain?
- Are there uncommitted final artifacts?
- Are there only preview/run artifacts left?
- What should be done next?

The future management UI should not duplicate this logic. It should consume a
small operations API or status layer.

Therefore, implement a CLI status command first.

## Goal

Create a read-only operations status command:

```bash
hatch run wiki-ops-status
```

It should produce a concise human-readable report and support machine-readable
JSON output:

```bash
hatch run wiki-ops-status --json
```

The command should summarize:

- source/review counts
- render graph/manifest presence
- synthesis cache health
- changed synthesis candidates
- durable vs. temporary artifact state
- git cleanliness by artifact class
- recommended next actions

It must not call the OpenAI API.

It must not run expensive workflows unless explicitly requested by a safe flag.

## Non-Goals

Do not build:

- the React/Next.js web UI
- cron jobs
- automatic commits
- automatic cleanup
- automatic synthesis execution
- repo splitting
- semantic LLM linting
- website publication

This task is only the first operations/status layer.

## Proposed Command

Add a Hatch script in `pyproject.toml`:

```toml
wiki-ops-status = "python -m src.wiki_ops.status_cli"
```

Suggested module structure:

```text
src/wiki_ops/
  __init__.py
  status.py
  status_cli.py
```

Tests:

```text
tests/wiki_ops/
  test_status.py
  test_status_cli.py
```

Follow existing project conventions:

- every function should have type hints
- every function should have a docstring
- keep code small and readable
- prefer reusing existing modules where reasonable
- avoid shelling out for core counts if direct file/JSON parsing is easy

## CLI Behavior

Default:

```bash
hatch run wiki-ops-status
```

Print a readable text report.

JSON:

```bash
hatch run wiki-ops-status --json
```

Print one JSON object.

Suggested options:

```text
--repo-root PATH
--raw-dir PATH
--reviews-dir PATH
--wiki-dir PATH
--graph-path PATH
--manifest-path PATH
--synthesis-cache-dir PATH
--preview-dir PATH
--run-dir PATH
--backup-dir PATH
--json
```

Default paths should be relative to the repo root.

Do not require `OPENAI_API_KEY`.

## Data Collection Requirements

### Sources

Count Readwise raw exports under `raw/readwise/`.

Useful counts:

- `.html` files
- `.md` files
- paired exports by shared basename
- incomplete pairs

Suggested output:

```text
Sources
- raw html exports: 360
- raw md exports: 360
- paired exports: 360
- incomplete exports: 0
```

### Reviews

Count `state/reviews/*/review.json`.

For each review, detect whether it appears finished.

Current review artifacts may use fields such as:

- `review_finished_at`
- review decision fields
- source metadata

Implementation should be defensive. If exact finished-state logic already exists
in the codebase, reuse it. If not, implement a simple conservative count:

- reviewed artifacts: all `review.json`
- finished reviews: artifacts with `review_finished_at`
- in-progress reviews: artifacts without `review_finished_at`

Do not fail if some review JSON is malformed. Count malformed review artifacts
and include a warning.

### Render State

Check:

- `state/wiki_render_graph.json` exists
- `state/wiki_render_manifest.json` exists
- `wiki/` exists

If possible, read graph metadata/counts:

- `knowledge_pages`
- `sources`
- evidence-object categories if present

Do not run `wiki-render` by default.

Optional future flag, not required in first implementation:

```text
--check-render-dry-run
```

If implemented, it may invoke `wiki-render --dry-run`, but this is not required
for the first version.

### Synthesis Cache Health

Reuse existing synthesis cache-lint logic if possible.

Relevant existing modules likely live under:

```text
src/wiki_synthesis/cache_lint.py
src/wiki_synthesis/planner.py
src/wiki_synthesis/cache.py
```

The status report should include:

- total synthesis cache entries
- ok/fresh count
- stale count
- error count
- missing count if available

It should also include changed-only plan counts:

- new
- stale
- unchanged
- skipped single-source
- skipped evidence objects

Do not make LLM calls.

### Artifact State

Classify artifacts into durable and temporary.

Durable:

- `state/synthesis/**/*.json`
- `wiki/**`
- `state/wiki_render_manifest.json`
- `state/wiki_render_graph.json`
- `state/reviews/**/review.json` if the project chooses to commit reviews

Temporary/review/audit:

- `state/synthesis_previews/**`
- `state/synthesis_runs/**`
- `state/synthesis_backups/**`

The status report should count:

- synthesis preview files
- synthesis run reports
- synthesis backup files/directories
- uncommitted final synthesis cache files
- uncommitted wiki files
- uncommitted docs/code files

Git status parsing is acceptable for this part.

Use `git status --porcelain` or equivalent. Keep parsing simple and covered by
tests.

Do not mutate Git state.

### Recommended Next Actions

Generate a small list of recommended next actions from status facts.

Examples:

- If cache lint has errors:
  - "Fix synthesis cache errors before running wiki-render."

- If stale synthesis entries exist:
  - "Refresh stale synthesis entries before final render."

- If render graph is missing:
  - "Run hatch run wiki-render to create graph state."

- If uncommitted durable synthesis files exist:
  - "Review and commit final synthesis cache files."

- If only preview/run/backup artifacts are uncommitted:
  - "No durable changes pending; preview/run artifacts can remain local or be cleaned deliberately."

- If changed-only synthesis candidates remain:
  - "Optional: synthesize the next small batch from wiki-synthesis-plan."

Keep recommendations conservative. Do not recommend automatic LLM calls as the
first action unless explicitly framed as optional.

## Human-Readable Output Shape

Example:

```text
Wiki Ops Status

Sources
- raw html exports: 360
- raw md exports: 360
- paired exports: 360
- incomplete exports: 0

Reviews
- review artifacts: 360
- finished: 345
- in progress: 15
- malformed: 0

Render
- wiki directory: present
- graph: present
- manifest: present
- graph sources: 360
- graph knowledge pages: 889

Synthesis
- cache entries: 89
- fresh: 89
- stale: 0
- errors: 0
- changed candidates: 78
- skipped single-source: 447
- skipped evidence objects: 275

Artifacts
- uncommitted durable files: 0
- uncommitted preview files: 39
- uncommitted run reports: 25
- backups present: yes

Recommended next actions
1. No render needed.
2. No cache warnings.
3. Optional: run a small synthesis batch if you want to continue Stage 2.
```

Exact wording can differ, but it should be calm, concise, and readable.

## JSON Output Shape

Use a stable top-level object.

Suggested shape:

```json
{
  "sources": {
    "raw_html": 360,
    "raw_markdown": 360,
    "paired": 360,
    "incomplete": 0
  },
  "reviews": {
    "artifacts": 360,
    "finished": 345,
    "in_progress": 15,
    "malformed": 0
  },
  "render": {
    "wiki_dir_exists": true,
    "graph_exists": true,
    "manifest_exists": true,
    "graph_sources": 360,
    "graph_knowledge_pages": 889
  },
  "synthesis": {
    "cache_entries": 89,
    "fresh": 89,
    "stale": 0,
    "errors": 0,
    "plan": {
      "new": 78,
      "stale": 0,
      "unchanged": 89,
      "skipped_single_source": 447,
      "skipped_evidence_object": 275
    }
  },
  "artifacts": {
    "uncommitted_durable": 0,
    "uncommitted_previews": 39,
    "uncommitted_runs": 25,
    "backups_present": true,
    "uncommitted_other": 0
  },
  "recommendations": [
    "No render needed.",
    "No cache warnings.",
    "Optional: run a small synthesis batch if you want to continue Stage 2."
  ]
}
```

Keep field names stable once introduced.

If some value cannot be computed, prefer `null` plus a warning field over
raising an exception.

## Error Handling

The command should be robust.

It should not crash just because:

- `raw/readwise/` does not exist
- `state/wiki_render_graph.json` is missing
- a review JSON is malformed
- synthesis cache directory is empty
- Git is unavailable

Instead, report missing state clearly.

Exit code:

- `0` when status was collected successfully, even if warnings exist
- non-zero only for invalid CLI arguments or unexpected implementation errors

## Implementation Hints

Prefer building a pure data function in `status.py`:

```python
def collect_ops_status(config: OpsStatusConfig) -> OpsStatus:
    """Collect read-only operational status for the wiki system."""
```

Use dataclasses or typed dictionaries for structured output.

Suggested dataclasses:

```python
@dataclass(frozen=True)
class OpsStatusConfig:
    repo_root: Path
    raw_dir: Path
    reviews_dir: Path
    wiki_dir: Path
    graph_path: Path
    manifest_path: Path
    synthesis_cache_dir: Path
    preview_dir: Path
    run_dir: Path
    backup_dir: Path

@dataclass(frozen=True)
class OpsStatus:
    sources: SourceStatus
    reviews: ReviewStatus
    render: RenderStatus
    synthesis: SynthesisStatus
    artifacts: ArtifactStatus
    recommendations: list[str]
```

Then keep `status_cli.py` small:

- parse args
- build config
- call `collect_ops_status`
- print text or JSON

## Tests

Add tests for:

1. Source counting
   - paired `.html`/`.md`
   - incomplete exports
   - missing raw directory

2. Review counting
   - finished review
   - in-progress review
   - malformed JSON

3. Render state
   - missing graph/manifest
   - graph with sources and knowledge pages

4. Artifact classification
   - uncommitted synthesis cache file
   - uncommitted preview file
   - uncommitted run report
   - unrelated uncommitted file

5. JSON output
   - top-level keys are present
   - recommendations are included

6. CLI smoke
   - `--json` returns valid JSON
   - text output contains `Wiki Ops Status`

Avoid tests that depend on the real repository state. Use `tmp_path` fixtures.

If Git status parsing is hard to test with real Git, factor the parser so it can
be tested from porcelain lines.

## Documentation Updates

Update `src/AGENTS.md` with a short section:

```markdown
## Wiki ops status

- Run: `hatch run wiki-ops-status`
- This command makes no LLM calls and writes no files.
- Purpose: summarize source/review/render/synthesis/artifact state before
  deciding what to run next.
- Use `--json` for future web frontend integration.
```

Optionally update `docs/current-system-status.md` after implementation.

## Quality Checks

Run:

```bash
hatch run lint:check
hatch run lint:format
hatch run test:run tests/wiki_ops
hatch run test:run
```

If the implementation touches shared modules, also run:

```bash
hatch run test:cov
```

## Acceptance Criteria

The task is complete when:

- `hatch run wiki-ops-status` prints a readable status report.
- `hatch run wiki-ops-status --json` prints valid JSON.
- The command makes no LLM calls.
- The command writes no files.
- Missing directories or malformed review files are reported without crashing.
- Synthesis health reuses or matches existing cache-lint/planner behavior.
- Temporary artifacts are clearly separated from durable artifacts.
- Recommendations are conservative and useful.
- Tests cover the core counting and formatting behavior.
- `src/AGENTS.md` documents the command.

## Product Judgment

This feature should remain intentionally small.

It is the foundation for:

- a future React/Next.js management UI
- safe cron reports
- automation dashboards
- repository split decisions
- clearer artifact boundaries

Do not expand it into a full dashboard or automation runner during the first
implementation.
