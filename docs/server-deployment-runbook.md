# Server Deployment Runbook (LLM Wiki Management App)

Status: v1 packaging
Related:

- `docs/server-deployment-packaging-spec.md`
- `docs/hetzner-server-primary-deployment-spec.md`
- `docs/superpowers/plans/2026-07-18-server-deployment-packaging.md`

## 1. What v1 deploys

v1 deploys only the private management app behind:

```text
https://wiki.plattenradar.de
```

It does **not** deploy a team-facing read-only wiki website, cron automation,
app-level login, or data migration/cutover.

## 2. Server layout

```text
/srv/llm-wiki/
  app/                  # git checkout of this repo (DEPLOY_PATH)
  data/                 # productive knowledge store (not Git-versioned)
  vault-private/        # productive private vault (separate private Git repo)
  backups/              # server-side backups/snapshots
```

Productive data stays on the server. GitHub Actions deploys **code images only**
and must not upload or overwrite productive data, `deploy/llm-wiki.env`, or the
real path config.

## 3. Required server-only files

Create these on the server (never commit real values):

1. `/srv/llm-wiki/app/deploy/llm-wiki.env` from `deploy/llm-wiki.env.example`
   (Compose reads this via `env_file`; do not point Compose at a developer
   `.env` that also holds unrelated local secrets)
2. `/srv/llm-wiki/app/config/wiki_paths.server.toml` from
   `config/wiki_paths.server.example.toml`
3. Music Review Caddy Basic Auth env for wiki (user + password hash)
4. Optional local operator file `.env.server` for `scripts/server_llm_wiki.sh`

## 4. Required GitHub secrets

Deploy workflow (`.github/workflows/deploy-llm-wiki.yml`):

| Secret | Purpose |
|--------|---------|
| `DEPLOY_HOST` | Hetzner host |
| `DEPLOY_USER` | SSH user |
| `DEPLOY_SSH_KEY` | Deploy private key |
| `DEPLOY_PATH` | App checkout, usually `/srv/llm-wiki/app` |
| `DEPLOY_PORT` | SSH port (default 22) |
| `LLM_WIKI_HEALTH_URL` | e.g. `https://wiki.plattenradar.de` |
| `LLM_WIKI_BASIC_AUTH_USER` | Basic Auth username |
| `LLM_WIKI_BASIC_AUTH_PASSWORD` | Basic Auth password for health curls |

## 5. DNS

Point `wiki.plattenradar.de` at the existing Hetzner VM that already serves
Music Review.

## 6. Caddy integration model

Keep the **existing Music Review Caddy** as the only public edge on ports
`80`/`443`.

1. Ensure `llm-wiki-api` and `llm-wiki-frontend` join the Music Review Docker
   network (compose default: `music-review_default`, override with
   `LLM_WIKI_DOCKER_NETWORK` if needed).
2. Merge `deploy/Caddyfile.llm-wiki.example` into the Music Review Caddyfile.
3. Provide `LLM_WIKI_BASIC_AUTH_USER` / `LLM_WIKI_BASIC_AUTH_HASH` to that Caddy
   process (hash via `caddy hash-password`).
4. Reload/recreate **only** the Music Review Caddy container.

Do **not** start a second public Caddy from `compose.llm-wiki.yml`.

Use `handle /api*` (not `handle_path`) so FastAPI keeps the `/api` prefix.

## 7. Deploy from GitHub Actions

```bash
gh workflow run "Deploy LLM Wiki" --field branch=main
```

The workflow:

1. lints and tests backend + frontend
2. builds Docker images
3. SSH fast-forwards `/srv/llm-wiki/app`
4. rebuilds/restarts only `llm-wiki-api` and `llm-wiki-frontend`
5. runs read-only health checks against the public URL

It does not install cron and does not overwrite server `deploy/llm-wiki.env` or
path config.

## 8. Manual health checks

```bash
export LLM_WIKI_HEALTH_URL=https://wiki.plattenradar.de
export LLM_WIKI_BASIC_AUTH_USER=...
export LLM_WIKI_BASIC_AUTH_PASSWORD=...
./scripts/check_llm_wiki_deploy_health.sh
```

Checks are read-only: frontend root, `/api/health`, `/api/config`,
`/api/ops/status`. They must not call OpenAI, Readwise, render, synthesis, or
cleanup.

## 9. Server helper

```bash
# local .env.server with DEPLOY_* values
./scripts/server_llm_wiki.sh status
./scripts/server_llm_wiki.sh logs api
./scripts/server_llm_wiki.sh compose ps
./scripts/server_llm_wiki.sh health
./scripts/server_llm_wiki.sh --dry-run compose up
```

## 10. Local packaging verification

```bash
hatch run lint:check
hatch run test:run
npm --prefix web/management run lint
npm --prefix web/management run test -- --run
npm --prefix web/management run build
cp deploy/llm-wiki.env.example deploy/llm-wiki.env
cp config/wiki_paths.server.example.toml config/wiki_paths.server.toml
# Always use -q. Plain `config` prints resolved secrets from env files.
docker compose -f compose.llm-wiki.yml config -q
docker compose -f compose.llm-wiki.yml build
```

Never run `docker compose ... config` without `-q` against a file that
contains real API tokens. If that already happened locally, rotate the exposed
OpenAI and Readwise credentials.

## 11. Cutover warning

After cutover, the Hetzner server is the productive source of truth. Local
machines must not write productive knowledge-store or vault data. Local Obsidian
mirrors of the private vault are read-only.

## 12. Out of scope for v1

- data migration / cutover execution
- cron automation
- app-level login
- team-facing wiki site
- public agent API
- backup automation beyond documenting the requirement
- vault auto-commit/push
