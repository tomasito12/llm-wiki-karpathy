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
- Don’t assume. Don’t hide confusion. Surface tradeoffs.
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

## Ingest review dashboard (classification + human approval)

- Run: `hatch run dashboard` — opens Streamlit at [`src/dashboard/app.py`](src/dashboard/app.py).
- On startup the app loads **`<repo_root>/.env`** via ``load_repo_dotenv()`` (same rules as Readwise: does **not** override variables already set in your shell). Put **`OPENAI_API_KEY`** there; optionally **`INGEST_OPENAI_MODEL`** (default model shown in the sidebar).
- **Raw inputs:** paired `raw/readwise/<id>.html` + `<id>.md` (same as wiki ingest hygiene).
- **Outputs:**
  - Review artifacts: `state/reviews/<source_id>/review.json` (JSON: `llm_output`, `review` decisions, `analysis_meta`, `source` + `content_sha256`). Safe to commit or keep local-only.
  - Feedback events (for a future learning loop): `state/review_feedback.sqlite` — **gitignored**; append-only rows when you click **Save review artifact**.
- **Tag allowlists** for the LLM / UI: [`config/review_tags_tools.yaml`](config/review_tags_tools.yaml), [`config/review_tags_howto.yaml`](config/review_tags_howto.yaml).
- This stage **does not** write `wiki/sources/*.md`; it only prepares human-reviewed classification. Downstream wiki ingest still re-reads HTML and may use separate LLM prompts.

## Readwise Reader export

- Set `READWISE_TOKEN` (or `READWISE_API_TOKEN`) from [readwise.io/access_token](https://readwise.io/access_token), or put it in a repo-root `.env` file (loaded automatically; does not override existing shell variables).
- Run: `hatch run readwise-sync` (optional: `--dry-run`, `--prune-missing`, `--reset-watermark`, `--output-dir`, `--index`).
- Each run passes Readwise **`updatedAfter`**: either `last_updated_after` from `state/readwise_library.json`, or on the **first run** (no watermark yet) a timestamp **~100 days** in the past so the initial sync still uses a bounded window.
- Exports Reader **Library Archive** documents tagged **processed** to `raw/readwise/` as paired `.html` + `.md`, with dedupe in `state/readwise_library.json`.

## Readwise rebuild (recovery)

- Use when `state/readwise_library.json` was cleared or corrupted but `raw/readwise/*.html` + `*.md` pairs still exist.
- `hatch run readwise-rebuild-index --dry-run` — scan only, no write.
- `hatch run readwise-rebuild-index --force` — rebuild the index (required if the index already lists documents).
- Does not call the Readwise API and does not modify files under `raw/`.

## Ingest queue

- `hatch run ingest-queue` lists exports under `raw/readwise/` and whether `wiki/sources/<same-basename>.md` exists.
- **Dedupe rule:** a raw item is treated as already ingested when that wiki source file exists. Use `--status pending` (default) to see work left.
- Examples: `hatch run ingest-queue --status pending --limit 5`, `hatch run ingest-queue --status incomplete` (missing `.md` sidecar next to `.html`).

## Ingest manifest (audit log)

- Persisted at `state/ingest_manifest.json`. **Not** used for dedupe — only for structured audit (Stage 1/2 routes, artifacts, errors).
- After each completed wiki ingest, the maintainer must upsert one record via `IngestManifestStore.upsert_record` (see `wiki/AGENTS.md` contract).
- Allowed `status` values: `pending`, `rendered`, `validated`, `failed`, `needs_review`.
- Inspect: `hatch run ingest-manifest` or `hatch run ingest-manifest --json`.

## Wiki baseline reset

- Run: `hatch run wiki-reset` interactively. You must type **`RESET-WIKI`** exactly when prompted, or pass `--confirm RESET-WIKI` (non-interactive).
- **Preserves** only: `wiki/AGENTS.md`, `wiki/stage1-classifier.md`, `wiki/ingest-templates.md`, `wiki/stage2-artifact-router.md`.
- **Recreates** empty shells: `wiki/index.md`, `wiki/log.md`, `wiki/questions/question-catalog.md`, `wiki/glossary/index.md`, empty `wiki/sources/` and `wiki/glossary/terms/`.
- **Clears** `state/ingest_manifest.json` by default (ingest audit log).
- **Resets** `config/review_tags_*.yaml` and `config/review_tool_types.yaml` / `config/review_model_types.yaml` to minimal baseline allowlists (unless **`--keep-tag-taxonomy`**).
- Readwise exports store **`publication`** on each `raw/readwise/*.md` sidecar (from API `site_name` or URL via `src/pipeline/source_publication.py`). Backfill existing files: `hatch run readwise-rebuild-index --backfill-publication --backfill-only`.
- **Does not** clear `state/readwise_library.json` unless you pass **`--reset-readwise-index`** (destructive: drops export dedupe + watermark; next sync may use the ~100-day lookback).
- Does **not** delete `raw/readwise/` exports.
- Does **not** reset `config/extraction_budgets.yaml` (proposal caps are unchanged).

## State files and Git

| Path | Role | In Git? |
|------|------|--------|
| `wiki/**` | Knowledge base + instruction markdown (`wiki/AGENTS.md`, sources, tools, etc.) | **Yes** — commit ingests and instruction updates. |
| `state/ingest_manifest.json` | Structured ingest audit (Stage 1/2, artifacts, errors). | **Yes** — commit after ingests that update the manifest. |
| `state/reviews/**` | Human-reviewed ingest classification JSON (per `source_id`). | Optional — commit if you want artifacts in Git. |
| `state/review_feedback.sqlite` | Append-only reviewer decision log for future tuning. | **No** — gitignored; local only. |
| `state/readwise_library.json` | Readwise export index (dedupe + `last_updated_after` watermark). | **No** — local cache only; rebuild with `hatch run readwise-rebuild-index` from `raw/readwise/` pairs. **Not** cleared by default `wiki-reset`. |
| `raw/**` | Readwise exports and other source files. | **No** — keep local / backup separately. |

- `state/ingest_manifest.json` is **cleared** on every `wiki-reset` (regenerate audit from the next ingests, or restore from Git history if needed).

## Safety

- Do not modify `raw/` source documents (except via the explicit Readwise export command above).
- Avoid touching wiki data unless the user explicitly requests a mixed workflow.
