# Management Web Read-Only Batch Review Runbook

Created: 2026-07-15

This runbook covers the local `management-web-v0-readonly-batch-review` slice.

## Scope

The management web app is read-only in this slice. It reads configured local
wiki state and review artifacts, but it does not save review decisions, mutate
`raw/`, mutate `state/reviews/`, mutate `wiki/`, call LLM providers, or run
pipeline commands.

## Backend

Start the FastAPI backend:

```bash
hatch run management-api --paths-config config/wiki_paths.toml
```

Useful defaults:

- host: `127.0.0.1`
- port: `8000`
- mode: `readonly`

If `--paths-config` is omitted, the backend follows the central `WikiPaths`
resolution order: `LLM_WIKI_PATHS_CONFIG`, then `config/wiki_paths.toml` when
present, then repo-local development defaults.

## Frontend

Install dependencies once:

```bash
cd web/management
npm install
```

Start the Vite dev server:

```bash
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Quality Checks

Backend:

```bash
hatch run lint:format
hatch run lint:check
hatch run test:run
```

Frontend:

```bash
cd web/management
npm run test
npm run build
npm run lint
```

## Manual Smoke Test

1. Start the backend with the desired path config.
2. Start the frontend with `npm run dev`.
3. Open the Vite URL in a browser.
4. Confirm the top bar shows `Read-only`.
5. Confirm the path panel shows the configured raw and reviews directories.
6. Confirm queue counts render.
7. Select an in-progress source.
8. Confirm metadata, summary, tags, topics, glossary, and trends render.
9. Open raw source on demand.
10. Open debug JSON on demand.
11. Browse without performing any writes, then verify `raw/`, `state/reviews/`,
    and `wiki/` are unchanged.
