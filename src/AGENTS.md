# Code Operations Rules

Use this file for `code_ops` requests only.

## Scope

Applies when the task is about:

- implementing or refactoring Python code
- adding CLI commands and automation
- updating tests and tooling (`hatch`, `ruff`, `ty`, `pre-commit`)
- improving code architecture or reliability

## Standards

- Keep changes minimal and scoped to the request.
- Add or update tests with code changes.
- Prefer clear function boundaries over large scripts.
- Use existing tooling configuration from `pyproject.toml`.
- Don't assume. Don't hide confusion. Surface tradeoffs.
- Minimum code that solves the problem. Nothing speculative.
- Touch only what you must. Clean up only your own mess.
- Define success criteria. Loop until verified.

## Testing Standards

- Every function must have at least one unit test.
- Prefer tests that use real objects and real logic flows; avoid mocking unless there is a clear need (for example: external APIs, non-deterministic systems, or expensive dependencies).
- Tests should be easy to read and self-explanatory.
- Aim for high coverage, including edge cases and error paths.
- Include explicit edge-case tests where relevant (for example: empty inputs, boundary values, malformed inputs, and failure behavior).

## Function Quality Standards

- Every function must have a docstring.
- Every function must have type hints on parameters and return values.

## Performance and Readability

- Write code that is both performant and understandable.
- If performance is not critical for the code path, prefer readability and maintainability over micro-optimizations.

## Required Quality Checks

Run these after substantive code changes:

1. `hatch run lint:check`
2. `hatch run lint:format`
3. `hatch run test:run`
4. `hatch run test:cov`

## Pre-commit Alignment

- Ensure code quality rules enforced by pre-commit match Hatch lint/type commands.
- Prefer changing config in one place (`pyproject.toml`) and reusing it from hooks.
- Wiki content is versioned in Git; run `hatch run wiki-lint` before committing wiki changes (not yet wired into `.pre-commit-config.yaml` by default).

## Shared wiki contract

Generated wiki layout rules live in [`src/wiki_contract/`](wiki_contract/). Both `wiki-render` and `wiki-lint` import from this module — do not duplicate folder lists, category definitions, required frontmatter fields, or heading contracts elsewhere.

## External knowledge store operating mode

- The preferred local operating mode uses `config/wiki_paths.toml`, which is
  machine-specific and intentionally gitignored. Keep
  `config/wiki_paths.example.toml` as the committed template.
- Current local roots:
  - knowledge store: `/Users/plischke/Desktop/Private Development/llm-wiki-data`
  - private generated vault: `/Users/plischke/Desktop/Private Development/llm-wiki-vault-private`
- Commands should use the central `WikiPaths` layer and respect `--paths-config`
  / `LLM_WIKI_PATHS_CONFIG` instead of hard-coding repo-local `raw/`, `state/`,
  or `wiki/` paths.
- Before migration-sensitive work, run:
  `hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root`.
- The old repo-local data is retained as a development/release artifact for now.
  Do not delete it without an explicit cleanup/migration task.

## Ingest review dashboard (classification + human approval)

- Run: `hatch run dashboard` — opens Streamlit at [`src/dashboard/app.py`](src/dashboard/app.py).
- On startup the app loads **`<repo_root>/.env`** via ``load_repo_dotenv()`` (same rules as Readwise: does **not** override variables already set in your shell). Put **`OPENAI_API_KEY`** there; optionally **`INGEST_OPENAI_MODEL`** (default model shown in the sidebar).
- **Raw inputs:** paired `raw/readwise/<id>.html` + `<id>.md` (same as wiki ingest hygiene).
- **Outputs:**
  - Review artifacts: `state/reviews/<source_id>/review.json` (JSON: `llm_output`, `review` decisions, `analysis_meta`, `source` + `content_sha256`). Safe to commit or keep local-only.
  - Feedback events (for a future learning loop): `state/review_feedback.sqlite` — **gitignored**; append-only rows when you click **Save review artifact**.
- **Tag allowlists** (see [`docs/tagging-ontology.md`](../docs/tagging-ontology.md)): `config/review_tags_{topics,trends,glossary,impl_study,tools,models}.yaml`; how-tos reuse topics. **Product types** (separate from retrieval tags): `config/review_tool_types.yaml`, `config/review_model_types.yaml`. Migrate legacy slugs: `hatch run tag-migrate`.
- This stage **does not** write `wiki/sources/*.md`; it only prepares human-reviewed classification.
- **Classification pipeline** (default): three LLM calls per source — triage → `source_summary` → route-specific entity extraction (`src/ingest_review/classification_pipeline.py`). Set `INGEST_CLASSIFICATION_PIPELINE=monolithic` to use the legacy single-call path. Prompt version `43` records per-stage `token_usage` / `cached_tokens` under `analysis_meta.classification_pipeline`.
- Trend titles follow the decomposition rule: name one outcome-level directional change in `trend_title`; put mechanisms, implementations, and explanations in `trend_description`, evidence, or supporting observations.
- Glossary proposals are a learning/reference layer: extract source-taught AI or technical terms that help practitioners answer “what does this mean?”, without requiring topic-level ontology worthiness.
- **Domain relevance profile:** extraction and prompt work should prioritize knowledge useful to the user's role as an EnBW AI expert building service chatbots and voicebots. High-value signals include Cognigy AI, competitor or replacement platforms, contact-center automation, human handoff, evaluation, governance, surrounding workflow orchestration, and broader AI workflow improvements for internal teams. Cognigy is current context, not a vendor lock-in boundary.
- **Nightly pre-analysis:** run `hatch run ingest-preanalyze --limit 100` to process pending `raw/readwise` exports through the normal synchronous review pipeline unattended. The command writes `state/reviews/<source_id>/review.json` without `review_finished_at`, so sources appear as **In progress** in the dashboard and still require normal human review. The dashboard sidebar can start the same background process and show the latest log from `state/ingest_batches/`. Re-analyze a single source with the existing **Analyze source** button; that path remains synchronous and does not use the pre-analysis loop.
- **Spaced pre-analysis (usage experiments):** pass `--between-articles 600` (or `INGEST_BETWEEN_ARTICLES_DELAY=600` in `.env`) to pause 10 minutes between articles. Each article uses a fresh `OpenAIIngestionProvider`; the HTTP client is closed before the pause so no OpenAI connection stays open between ingestions. Example: `hatch run ingest-preanalyze --between-articles 600 --limit 20`.

## Wiki render (generated Obsidian vault)

- Run: `hatch run wiki-render`
- Options: `--dry-run`, `--no-prune`, `--paths-config`, `--reviews-dir`, `--out-dir`, `--manifest-path`, `--graph-path`, `--synthesis-cache-dir`, `--raw-dir`, `--require-source-text`
- **Canonical input:** `state/reviews/*/review.json`
- **Raw source input:** `raw/readwise/<source_id>.md` (or configured `paths.raw_dir` via `--paths-config` / `LLM_WIKI_PATHS_CONFIG`; override with `--raw-dir`)
- **Output:** full regeneration of managed folders under `wiki/` (see [`wiki/AGENTS.md`](../wiki/AGENTS.md))
- Generated source pages at `wiki/sources/<source_id>.md` include a `## Full source text` section with embedded raw Markdown when the export exists locally
- Full source text is **private/local vault content** by default — not automatically safe for team or public export without an explicit source-mode decision
- Use `--require-source-text` to fail when fewer than half of source pages would include full raw text (guards against empty/misconfigured `raw_dir`)
- **Audit artifacts:** `state/wiki_render_manifest.json` (advisory file list + hashes), `state/wiki_render_graph.json` (Stage 2 graph export)
- The renderer may read existing Stage 2 cache entries from `state/synthesis/<category>/<slug>.json`; it never creates cache entries and never makes LLM calls. Fresh cache entries render synthesized Obsidian pages, stale cache entries render with a visible warning, and missing/invalid cache entries fall back to Stage 1.
- After review changes, rerun `wiki-render` — do not hand-edit generated pages.

## Wiki synthesis planning (Stage 2 groundwork)

- Run: `hatch run wiki-synthesis-plan`
- This command makes **no LLM calls** and writes no files.
- Input: `state/wiki_render_graph.json`
- Cache lookup path: `state/synthesis/<category>/<slug>.json`
- Purpose: classify knowledge pages as `new`, `stale`, `unchanged`, or skipped before any future synthesis execution.
- Default behavior skips single-source knowledge pages and always treats signals, interview insights, and implementation studies as evidence objects rather than synthesis targets.
- Useful options:
  - `--changed-only` — show only pages that would need synthesis work.
  - `--limit 20` — cap displayed entries.
  - `--category topic` — inspect one graph category.
  - `--entity topic:agentic-coding-workflows` — inspect one entity.
  - `--include-single-source` — include candidate/thin single-source pages.
  - `--json` — print machine-readable output.

## Wiki synthesis selection and batch automation

- Run `hatch run wiki-synthesis-select --limit 20` to inspect ranked changed synthesis candidates.
- This command is read-only and makes no LLM calls.
- Run `hatch run wiki-synthesis-batch --dry-run --limit 10` before real automation.
- Real batch execution requires `--yes`.
- Use `--between-calls 300` for slow nightly-style runs.
- The batch command writes synthesis cache files, previews, and an audit report, but does not run `wiki-render`.
- After a real batch, run `hatch run wiki-synthesis-cache-lint` and `hatch run wiki-render --dry-run`.

## Wiki synthesis workflow (Stage 2 primary command)

- Run: `hatch run wiki-synthesis-workflow --dry-run --entity glossary:fine-tuning`
- This is the preferred day-to-day wrapper once the individual steps are understood.
- Dry-run mode makes **no LLM calls**, writes no cache files, and writes no preview files.
- Real mode requires `--yes`, writes validated cache entries, and renders review previews unless `--no-review` is passed.
- Real mode writes an audit report to `state/synthesis_runs/<timestamp>.json` unless `--no-audit-log` is passed.
- It intentionally does **not** run `wiki-render`; inspect previews first, then run `hatch run wiki-render --dry-run`.
- Useful examples:
  - `hatch run wiki-synthesis-workflow --dry-run --entity glossary:fine-tuning --json`
  - `hatch run wiki-synthesis-workflow --entity glossary:fine-tuning --yes`
  - `hatch run wiki-synthesis-workflow --category glossary --limit 5 --yes`
  - `hatch run wiki-synthesis-workflow --entity glossary:example --include-single-source --yes`
  - `hatch run wiki-synthesis-workflow --entity glossary:fine-tuning --yes --no-audit-log`

## Wiki synthesis doctor (Stage 2 preflight)

- Run: `hatch run wiki-synthesis-doctor --entity glossary:fine-tuning`
- This command makes **no LLM calls** and writes no files.
- Purpose: check whether a target is ready for the synthesis workflow before running a paid API call.
- Checks:
  - graph path exists
  - cache/preview/report parent directories are usable
  - model value is set
  - `OPENAI_API_KEY` is present or missing
  - target has executable `new`/`stale` work
  - existing cache files have no blocking lint errors
- Useful examples:
  - `hatch run wiki-synthesis-doctor --entity glossary:fine-tuning --json`
  - `hatch run wiki-synthesis-doctor --entity glossary:fine-tuning --require-api-key`

## Wiki synthesis cache lint (Stage 2 pre-render check)

- Run: `hatch run wiki-synthesis-cache-lint`
- This command makes **no LLM calls** and writes no files.
- It validates existing cache files against `state/wiki_render_graph.json`.
- Results:
  - `ok` — cache is fresh and renderable.
  - `warning` — cache is stale but renderable.
  - `error` — cache is missing when required, invalid, or orphaned.
- Use before `wiki-render` after real synthesis runs.
- Useful examples:
  - `hatch run wiki-synthesis-cache-lint --entity glossary:fine-tuning --json`
  - `hatch run wiki-synthesis-cache-lint --category glossary`
  - `hatch run wiki-synthesis-cache-lint --entity glossary:fine-tuning --include-missing`

## Wiki synthesis indexes (Stage 2 routing)

- Run: `hatch run wiki-synthesis-indexes`
- This command makes **no LLM calls**.
- Inputs: `state/wiki_render_graph.json` and optional `state/synthesis/<category>/<slug>.json` cache entries.
- Outputs:
  - `wiki/indexes/synthesis-status.md`
  - `wiki/indexes/needs-synthesis.md`
  - high-value tag hubs under `wiki/indexes/tags/`
- Purpose: expose Stage 2 planning and tag-based routing in Obsidian so humans and LLMs can find useful entry points without scanning the whole vault.
- Useful options:
  - `--dry-run` — compute output without writing files.
  - `--tag ai-engineering` — render one tag hub; may be passed multiple times.
  - `--out-dir`, `--graph-path`, `--cache-dir` — override default paths.

## Wiki synthesis prompt preview (Stage 2 executor preparation)

- Run: `hatch run wiki-synthesis-prompt --entity topic:agentic-coding-workflows`
- This command makes **no LLM calls**.
- Inputs: `state/wiki_render_graph.json` and optional previous cache entry from `state/synthesis/<category>/<slug>.json`.
- Purpose: preview the exact system prompt, user prompt, evidence context, previous-synthesis continuity block, and expected JSON schema before implementing or running the synthesis executor.
- Useful options:
  - `--json` — print the prompt bundle as machine-readable JSON with chat messages.
  - `--out-path state/synthesis_prompts/<entity>.md` — write a review artifact for a prompt preview.
  - `--graph-path`, `--cache-dir` — override default input paths.

## Wiki synthesis executor (Stage 2 cache writer)

- Run: `hatch run wiki-synthesis-run --dry-run`
- This command makes LLM calls only when `--yes` is passed and `--dry-run` is absent.
- Inputs: `state/wiki_render_graph.json`, the existing synthesis plan, and optional previous cache entries in `state/synthesis/<category>/<slug>.json`.
- Output: validated cache entries under `state/synthesis/<category>/<slug>.json`.
- Safety rules:
  - Default `--limit 1`; raise it deliberately for batches.
  - Only `new` and `stale` plan entries are executable.
  - Single-source pages are skipped by default via the planner.
  - Use `--include-single-source` only when you want a source-grounded readable summary for thin pages; the prompt must not imply multi-source consensus.
  - Provider output is normalized with local entity metadata, prompt version, schema version, timestamp, and current input hash before writing.
  - Invalid provider JSON or incomplete synthesis content must fail without writing a cache file.
- Useful examples:
  - `hatch run wiki-synthesis-run --dry-run --entity glossary:fine-tuning`
  - `hatch run wiki-synthesis-run --dry-run --entity glossary:example --include-single-source`
  - `hatch run wiki-synthesis-run --entity glossary:fine-tuning --yes`
  - `hatch run wiki-synthesis-run --category glossary --limit 5 --yes`

## Wiki synthesis review (Stage 2 human QA)

- Run: `hatch run wiki-synthesis-review --entity glossary:fine-tuning`
- This command makes **no LLM calls** and does **not** write to the Obsidian vault.
- Inputs: `state/wiki_render_graph.json` and `state/synthesis/<category>/<slug>.json`.
- Output: rendered preview markdown under `state/synthesis_previews/<category>/<slug>.md`.
- Purpose: inspect a single synthesized page before running `wiki-render`.
- Review flow:
  - `hatch run wiki-synthesis-run --entity glossary:fine-tuning --yes`
  - `hatch run wiki-synthesis-review --entity glossary:fine-tuning`
  - inspect `state/synthesis_previews/glossary/fine-tuning.md`
  - `hatch run wiki-render --dry-run`
  - `hatch run wiki-render`
- Useful options:
  - `--dry-run` — validate and render in memory without writing a preview file.
  - `--json` — print validation state, cache path, target wiki path, and preview path as JSON.
  - `--preview-dir`, `--graph-path`, `--cache-dir` — override default paths.

## Readwise Reader export

- Set `READWISE_TOKEN` (or `READWISE_API_TOKEN`) from [readwise.io/access_token](https://readwise.io/access_token), or put it in a repo-root `.env` file (loaded automatically; does not override existing shell variables).
- Run: `hatch run readwise-sync` (optional: `--dry-run`, `--prune-missing`, `--reset-watermark`, `--no-dedupe`, `--dedupe-threshold`, `--dedupe-interactive`, `--output-dir`, `--index`, `--allow-index-bootstrap`).
- In external operating mode, the Readwise index is canonical operational state:
  `/Users/plischke/Desktop/Private Development/llm-wiki-data/state/readwise_library.json`.
  It is not a disposable cache. It binds Readwise document IDs to raw export
  filenames, stores the incremental watermark, and preserves `suppressed_ids`
  from duplicate cleanup.
- Do not run a real `readwise-sync` when `raw/readwise` already contains exports
  but the configured `readwise_library.json` is missing or empty. That usually
  means raw files were migrated without bookkeeping. First migrate or rebuild
  the index, then dry-run the queue/dedupe checks.
- `readwise-sync` now fails closed in that dangerous state. Use
  `--allow-index-bootstrap` only for an intentional first sync into a confirmed
  fresh raw directory, never as a routine workaround.
- Before migration-sensitive Readwise work, check:
  `hatch run wiki-ops-status`,
  `hatch run readwise-rebuild-index --dry-run --paths-config config/wiki_paths.toml --force`,
  `hatch run readwise-dedupe --dry-run --paths-config config/wiki_paths.toml`,
  and `hatch run ingest-queue --status all --json`.
- Existing review artifacts are keyed by raw filename stem. If Readwise changes
  a title and therefore a future export slug, preserve the review-aligned old
  filename or deliberately migrate the review directory and graph references.
  Do not blindly accept a new slug if it would orphan an existing review.
- Each run passes Readwise **`updatedAfter`**: either `last_updated_after` from `state/readwise_library.json`, or on the **first run** (no watermark yet) a timestamp **~100 days** in the past so the initial sync still uses a bounded window.
- Exports Reader **Library Archive** documents tagged **processed** to `raw/readwise/` as paired `.html` + `.md`, with dedupe in `state/readwise_library.json`.
- After a successful sync (not `--dry-run`), runs **`readwise-dedupe`** by default: scans `raw/readwise/` for near-duplicate HTML exports and **deletes the shorter copy**, adding its Readwise id to `suppressed_ids` so sync will not re-import it. Pass **`--no-dedupe`** to skip.

## Medium → Readwise browser import

- By default the command **auto-launches Brave with CDP**: if `http://127.0.0.1:9222` is unreachable, it quits Brave and relaunches `/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser --remote-debugging-port=9222`. Pass `--no-launch-brave` or `MEDIUM_LAUNCH_BRAVE=false` to require a manually started browser instead.
- Set your Reading List in repo-root `.env` as `MEDIUM_READING_LIST_URL=https://medium.com/@<username>/list/reading-list`, or pass `--reading-list-url` explicitly. The generic `https://medium.com/list/reading-list` is not the same as a user-specific list.
- Dry run first: `hatch run medium-to-readwise --dry-run` — harvests the Medium Reading List and prints planned article saves without triggering Readwise. After changing the list URL or URL filter logic, rerun with `--refresh-articles`.
- Small test batch: `hatch run medium-to-readwise --limit 5 --delay 5`.
- Full resumable run: `hatch run medium-to-readwise`. It connects to the existing Brave session, opens the Medium Reading List, stores discovered URLs in `state/medium_to_readwise/articles.json`, skips successful entries in `state/medium_to_readwise/processed.json`, visits each pending article, waits for article content, dismisses Medium image zoom overlays, and sends **Option+R** through macOS system input (`--shortcut-mode system`, default on macOS). Playwright page-level key events do **not** trigger browser extension shortcuts reliably.
- Optional env vars: `READWISE_SAVE_SHORTCUT=Alt+KeyR` (same as Option+R), `READWISE_SHORTCUT_MODE=system`, `READWISE_BROWSER_APP_NAME=Brave Browser`, `MEDIUM_REMOVE_FROM_LIST=true`, `READWISE_CONFIRM_TIMEOUT=15`, `READWISE_CONFIRM_MODE=relaxed`, `MEDIUM_ARTICLE_MIN_CHARS=1200`, `MEDIUM_ARTICLE_SCROLL_STEPS=6`, `MEDIUM_DELAY_JITTER=3`, `MEDIUM_BETWEEN_ARTICLES_DELAY=8`, `MEDIUM_MAX_PER_HOUR=20`.
- Readwise saves the **rendered** Medium DOM. The script scrolls **down in a few passes** (no top/bottom bouncing), logs article length per pass, then returns to the top once before Option+R. `READWISE_CONFIRM_MODE=relaxed` (default) accepts toolbar checkmarks when Readwise shows no toast.
- Human-like pacing defaults: post-save `--delay` with `--jitter`, extra `--between-articles` pause, and `--max-per-hour` cap. If Medium shows human verification (`Verify you are human`), the run pauses up to `--verification-wait` seconds (default 600) for you to complete the challenge manually in Brave, then continues. Pass `--no-verification-wait` to fail immediately instead.
- Reading List removal clicks the entry menu action **Remove item** and verifies the article link disappears from the list before marking success.
- Before processing, the script checks that Brave is logged into Medium (sign-in URL, visible sign-in controls, or thin paywall copy). If not logged in, it stops immediately with exit code 2. Each article logs step-by-step progress to the terminal and `run.log` (opening URL, waiting for content, Readwise shortcut, confirmation wait, list removal).
- By default, after visible Readwise save confirmation, the script returns to your Reading List and removes the article via the entry menu (`--no-remove-from-list` to keep items on Medium).
- Failure screenshots go to `state/medium_to_readwise/screenshots/`. This state directory is local-only and gitignored.
- This workflow does not call Medium or Readwise APIs and does not bypass paywalls; it only automates the browser session that already has access. If shortcuts do not fire, grant **Accessibility** permission to Terminal/iTerm/Cursor for `osascript` system keystrokes and confirm the Readwise extension shortcut works manually on Medium.
- After articles are saved in Readwise, use the normal `hatch run readwise-sync` export flow.

## Readwise near-duplicate cleanup

- Run: `hatch run readwise-dedupe` (optional: `--dry-run`, `--interactive`, `--threshold 0.50`, `--raw-dir`, `--index`).
- Compares exports with word-shingle Jaccard similarity.
- **Default:** delete the export with fewer plain-text characters and suppress it in `state/readwise_library.json`.
- **`--interactive`:** prompt per pair instead of auto-deleting the shorter copy.
- Legacy wrapper: `python scripts/detect_near_duplicates.py` (same behavior via `readwise-dedupe`).

## Readwise rebuild (recovery)

- Use when `state/readwise_library.json` was cleared or corrupted but `raw/readwise/*.html` + `*.md` pairs still exist.
- `hatch run readwise-rebuild-index --dry-run` — scan only, no write.
- `hatch run readwise-rebuild-index --force` — rebuild the index (required if the index already lists documents).
- Does not call the Readwise API and does not modify files under `raw/`.

## Ingest queue

- `hatch run ingest-queue` lists exports under `raw/readwise/` and whether `state/reviews/<basename>/review.json` exists.
- **Dedupe rule:** a raw item is **pending** when the export pair exists but no review artifact is saved yet. Use `--status pending` (default) to see work left.
- Status values: `pending`, `reviewed`, `incomplete` (missing `.md` sidecar).
- Examples: `hatch run ingest-queue --status pending --limit 5`, `hatch run ingest-queue --status incomplete`

## Ingest manifest (legacy audit log)

- Persisted at `state/ingest_manifest.json`. **Legacy/optional** — no active writer in the current review → render workflow.
- Superseded for generation audit by `state/wiki_render_manifest.json`.
- Inspect: `hatch run ingest-manifest` or `hatch run ingest-manifest --json`.

## Wiki ops status

- Run: `hatch run wiki-ops-status`
- This command makes no LLM calls and writes no files.
- Purpose: summarize source/review/render/synthesis/artifact state before deciding what to run next.
- Use `--json` for future web frontend integration.
- The `Source Access` section verifies the private-vault full-text contract:
  embedded text coverage, local raw-link fallback, external-only pages,
  source-page/raw-Markdown alignment, graph sources without pages, and broken
  source wikilinks from managed generated pages.
- Private-vault policy is to embed full raw Markdown in
  `wiki/sources/<source_id>.md`. The external knowledge store remains canonical;
  future team/public exports require an explicit safer source mode.

## Wiki lint

- Run: `hatch run wiki-lint` — validates generated pages under managed folders using [`src/wiki_contract/`](wiki_contract/).
- `--include-non-managed` also lints preserved/manual paths (`notes/`, `legacy/`, hub files).

## Wiki baseline reset

- Run: `hatch run wiki-reset` interactively. You must type **`RESET-WIKI`** exactly when prompted, or pass `--confirm RESET-WIKI` (non-interactive).
- **Preserves:** `wiki/AGENTS.md`, `wiki/index.md`, `wiki/log.md`, `wiki/notes/**`, `wiki/legacy/**`
- **Recreates:** empty managed-folder shells (`sources/`, `topics/`, `indexes/`, etc.)
- **Clears by default:** `state/ingest_manifest.json`, `state/wiki_render_manifest.json`, `state/reviews/` (unless `--keep-reviews`), tag taxonomy (unless `--keep-tag-taxonomy`)
- **Post-reset:** run `hatch run wiki-render` when review artifacts are available.
- Readwise exports store **`publication`** on each `raw/readwise/*.md` sidecar (from API `site_name` or URL via `src/pipeline/source_publication.py`). Backfill existing files: `hatch run readwise-rebuild-index --backfill-publication --backfill-only`.
- **Does not** clear `state/readwise_library.json` unless you pass **`--reset-readwise-index`** (destructive: drops export dedupe + watermark; next sync may use the ~100-day lookback).
- Does **not** delete `raw/readwise/` exports.
- Does **not** reset `config/extraction_budgets.yaml` (proposal caps are unchanged).

## State files and Git

| Path | Role | In Git? |
|------|------|--------|
| `wiki/**` | Generated knowledge base + operator docs (`wiki/AGENTS.md`, `wiki/notes/`, etc.) | **Yes** — commit renders and instruction updates. |
| `state/reviews/**` | Human-reviewed classification JSON (per `source_id`). | Optional — commit if you want artifacts in Git. |
| `state/wiki_render_manifest.json` | Advisory wiki-render file manifest (paths + hashes). | Optional — useful for prune/idempotency audit. |
| `state/wiki_render_graph.json` | Machine-readable graph export for Stage 2. | Optional |
| `state/ingest_manifest.json` | Legacy manual-ingest audit log. | Optional |
| `state/review_feedback.sqlite` | Append-only reviewer decision log for future tuning. | **No** — gitignored; local only. |
| `state/readwise_library.json` | Readwise export index (dedupe + `last_updated_after` watermark). | **No** — local cache only; rebuild with `hatch run readwise-rebuild-index` from `raw/readwise/` pairs. **Not** cleared by default `wiki-reset`. |
| `raw/**` | Readwise exports and other source files. | **No** — keep local / backup separately. |

## Safety

- Do not modify `raw/` source documents (except via the explicit Readwise export command above).
- Avoid touching wiki data unless the user explicitly requests a mixed workflow.
