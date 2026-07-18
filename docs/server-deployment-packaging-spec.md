# Server Deployment Packaging Implementation Specification

Status: Ready for Cursor implementation
Created: 2026-07-18
Depends on: `docs/hetzner-server-primary-deployment-spec.md`

## 1. Purpose

Implement the first server deployment slice for the LLM Wiki management app.

The goal is to run the management app on the existing Hetzner VM behind:

```text
https://wiki.plattenradar.de
```

with Caddy Basic Auth, server-primary paths, Docker Compose packaging, and a
GitHub Actions deployment flow modeled after the adjacent `music-review`
project.

This spec is written for Cursor. Cursor should assume no chat context beyond the
files listed here.

## 2. Non-Negotiable Architecture Decisions

These are already decided and must not be re-litigated during implementation.

- The Hetzner server is the productive source of truth after cutover.
- LLM Wiki runs on the same Hetzner VM as Music Review.
- The management app is private and single-user in v1.
- Public domain for v1 is `wiki.plattenradar.de`.
- v1 uses Caddy Basic Auth, not app-level login.
- v1 exposes only the management app, not a read-only team wiki surface.
- Productive code deploys through GitHub Actions.
- Productive data is not uploaded by GitHub Actions.
- The existing Music Review Caddy remains the public edge proxy for the first
  slice. Do not run a second public Caddy container on ports `80`/`443`.
- Knowledge Store is not Git-versioned; it is backed up by server snapshots.
- Private Vault is a separate private GitHub repo and can be pulled locally as a
  read-only Obsidian mirror.
- Cron automation is out of scope for this slice.

## 3. Existing Code Context

Backend:

- `src/management_web/app.py`
- `src/management_web/api.py`
- Hatch command: `hatch run management-api`
- Existing health endpoint: `GET /api/health`
- Existing ops endpoint: `GET /api/ops/status`
- Existing path config support: `--paths-config`

Frontend:

- `web/management/package.json`
- Vite app under `web/management/src`
- Build command: `npm --prefix web/management run build`
- Dev command: `hatch run management-ui`

Path config:

- `src/wiki_paths/config.py`
- `src/wiki_paths/cli_helpers.py`
- `config/wiki_paths.example.toml`

Reference infrastructure:

- Adjacent repo: `../music-review`
- Reference docs: `../music-review/deploy/README.md`
- Reference compose: `../music-review/compose.yml`
- Reference Caddyfile: `../music-review/deploy/Caddyfile`
- Reference GitHub deploy: `../music-review/.github/workflows/deploy.yml`

Do not copy secrets from Music Review. Do not document host IPs, SSH keys,
tokens, or `.env` values.

## 4. Target Server Layout

The server should use:

```text
/srv/llm-wiki/
  app/                  # code repo checkout
  data/                 # productive knowledge store, not Git-versioned
  vault-private/        # productive private vault, separate Git repo
  backups/              # server-side backups/snapshots
```

The deployment must not assume productive data lives inside the app checkout.

## 5. Server Path Configuration

Add a committed server example config:

```text
config/wiki_paths.server.example.toml
```

Required content:

```toml
[paths]
knowledge_root = "/srv/llm-wiki/data"
vault_root = "/srv/llm-wiki/vault-private"

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
```

On the server, the real config may be:

```text
/srv/llm-wiki/app/config/wiki_paths.server.toml
```

or a server-only path such as:

```text
/srv/llm-wiki/secrets/wiki_paths.toml
```

The Docker/Compose setup must support passing the selected path config through:

```text
LLM_WIKI_PATHS_CONFIG=/app/config/wiki_paths.server.toml
```

or an equivalent container path.

## 6. Environment Variables

Create a committed example:

```text
deploy/llm-wiki.env.example
```

It must include only placeholder values:

```env
LLM_WIKI_PATHS_CONFIG=/app/config/wiki_paths.server.toml
OPENAI_API_KEY=
READWISE_TOKEN=
PYTHONUNBUFFERED=1
```

The real production env file must remain server-side and untracked.

Do not put Basic Auth credentials in this env example. They belong in the
server Caddy configuration or in a server-only Caddy env file, depending on the
final Caddy implementation.

## 7. Docker Packaging

Implement Docker packaging for two LLM Wiki services.

### 7.1 Backend Image

Create:

```text
deploy/Dockerfile.api
```

Requirements:

- Python 3.12
- install Hatch or install runtime dependencies in a reproducible way
- run the FastAPI backend
- bind to `0.0.0.0`
- expose internal port `8000`
- accept `LLM_WIKI_PATHS_CONFIG`
- do not bake secrets into the image

Recommended command:

```bash
hatch run management-api --host 0.0.0.0 --port 8000 --paths-config "$LLM_WIKI_PATHS_CONFIG"
```

If shell variable expansion inside Docker `CMD` is awkward, use an entrypoint
script:

```text
deploy/docker-entrypoint-api.sh
```

The entrypoint should fail clearly when `LLM_WIKI_PATHS_CONFIG` is empty or the
file does not exist.

### 7.2 Frontend Image

Create:

```text
deploy/Dockerfile.management-ui
```

Requirements:

- build `web/management` with Node
- serve static assets with nginx or another tiny static server
- expose internal port `80`
- frontend should use relative `/api/...` paths so it works behind Caddy
- no secrets in frontend image

If the current frontend already uses relative API paths, preserve that. If it
does not, change it to use relative paths by default and cover the behavior with
a frontend test.

## 8. LLM Wiki Compose File

Create:

```text
compose.llm-wiki.yml
```

or, if the project convention prefers it:

```text
deploy/compose.llm-wiki.yml
```

The file must define:

```text
llm-wiki-api
llm-wiki-frontend
```

Required mounts:

```text
/srv/llm-wiki/data:/srv/llm-wiki/data
/srv/llm-wiki/vault-private:/srv/llm-wiki/vault-private
```

If the container path config references `/srv/llm-wiki/...`, mount the host
paths at the same absolute paths inside the container. That avoids path
translation mistakes.

Required behavior:

- API service reads production env file from the server.
- API service runs on internal port `8000`.
- frontend service runs on internal port `80`.
- services are attached to a Docker network reachable by the existing Music
  Review Caddy.
- no host port binding for API/frontend is required for public access.

Important: do not define a public Caddy service in this compose file for v1.

## 9. Caddy Integration

Create a documented Caddy snippet for the existing Music Review Caddy config:

```text
deploy/Caddyfile.llm-wiki.example
```

It should contain a site block for:

```text
wiki.plattenradar.de
```

Required behavior:

- protect the entire site with Basic Auth
- proxy `/api/*` to the LLM Wiki API service
- proxy all other paths to the LLM Wiki frontend service

Illustrative shape:

```caddyfile
wiki.plattenradar.de {
  basicauth {
    {$LLM_WIKI_BASIC_AUTH_USER} {$LLM_WIKI_BASIC_AUTH_HASH}
  }

  handle_path /api/* {
    reverse_proxy llm-wiki-api:8000
  }

  handle {
    reverse_proxy llm-wiki-frontend:80
  }
}
```

Cursor must verify the exact Caddy syntax. Do not commit real Basic Auth hashes
or passwords.

The implementation notes must explain how this snippet is applied to the
existing Music Review Caddy without starting a second Caddy on ports `80`/`443`.

## 10. Deployment Workflow

Create GitHub Actions workflow:

```text
.github/workflows/deploy-llm-wiki.yml
```

Model it after Music Review's deploy workflow.

Required secrets:

```text
DEPLOY_HOST
DEPLOY_USER
DEPLOY_SSH_KEY
DEPLOY_PATH
DEPLOY_PORT
```

`DEPLOY_PATH` should point to the server app checkout:

```text
/srv/llm-wiki/app
```

Required verify job:

- checkout
- install Python 3.12
- install Hatch or project tooling
- run `hatch run lint:check`
- run `hatch run test:run`
- install frontend dependencies
- run `npm --prefix web/management run lint`
- run `npm --prefix web/management run test -- --run`
- run `npm --prefix web/management run build`
- build Docker images with the LLM Wiki compose file

Required deploy job:

- SSH into the server
- `cd "$DEPLOY_PATH"`
- fetch selected branch
- fast-forward the checkout
- build/restart `llm-wiki-api` and `llm-wiki-frontend`
- do not touch productive data except through normal container mounts
- do not overwrite server `.env`
- do not overwrite server path config
- run health checks

Do not add automatic cron installation in this workflow. Cron automation is a
later feature.

## 11. Server Helper Script

Create:

```text
scripts/server_llm_wiki.sh
```

Purpose:

- mirror the usefulness of Music Review's `scripts/server.sh`
- make common server operations visible and repeatable
- avoid memorizing SSH and Docker commands

Commands:

```text
status
ssh
logs api
logs frontend
compose ps
compose pull
compose up
health
```

Configuration:

- load `.env.server` if present
- use `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH`, `DEPLOY_PORT`, and optionally
  `DEPLOY_SSH_KEY`
- never print secret values

The script should be safe by default. Any command that changes server state must
show what it will run and should be easy to audit.

## 12. Health Checks

Create health check script:

```text
scripts/check_llm_wiki_deploy_health.sh
```

Required checks:

1. Frontend reachable behind Caddy/Basic Auth.
2. API `/api/health` reachable behind Caddy/Basic Auth.
3. API returns `ok: true`.
4. API `/api/config` reachable behind Caddy/Basic Auth.
5. API `/api/ops/status` reachable behind Caddy/Basic Auth.

Constraints:

- checks must be read-only
- checks must not trigger OpenAI calls
- checks must not trigger Readwise sync
- checks must not run render
- checks must not run synthesis
- checks must not run cleanup

The script may require:

```text
LLM_WIKI_HEALTH_URL=https://wiki.plattenradar.de
LLM_WIKI_BASIC_AUTH_USER=...
LLM_WIKI_BASIC_AUTH_PASSWORD=...
```

These variables must be provided by GitHub Actions secrets or server env and
must not be committed with real values.

## 13. Documentation

Create:

```text
docs/server-deployment-runbook.md
```

It must document:

- server layout
- required GitHub secrets
- required server-only files
- DNS requirement for `wiki.plattenradar.de`
- Caddy integration model
- how to deploy from GitHub Actions
- how to run manual health checks
- what is not included in v1
- clear warning that productive data is server-primary after cutover

Also update:

```text
docs/hetzner-server-primary-deployment-spec.md
```

Add a short link from the architecture spec to the new implementation/runbook
docs after implementation.

## 14. Tests

Add tests where behavior is code-owned.

Required backend tests:

- `GET /api/health` still works with a resolved path config.
- `GET /api/config` returns expected configured server-like paths when app is
  created with test `WikiPaths`.
- app creation fails clearly or health/config tests document expected behavior
  when path config is invalid, depending on current `load_wiki_paths` behavior.

Required frontend tests:

- API client uses relative `/api/...` paths by default.
- no hardcoded localhost URL is required for production build.

Required script tests, if the repo already has shell-script testing patterns:

- health script refuses to run without required URL/auth variables.
- helper script does not print secret values.

If there is no shell-script test pattern, document manual test commands in the
runbook and keep shell scripts small and reviewable.

## 15. Manual Verification Commands

Cursor must run the relevant checks before handing back.

Required local checks:

```bash
hatch run lint:check
hatch run test:run
npm --prefix web/management run lint
npm --prefix web/management run test -- --run
npm --prefix web/management run build
docker compose -f compose.llm-wiki.yml config
docker compose -f compose.llm-wiki.yml build
```

If Docker is not available locally, Cursor must state that clearly and still run
the non-Docker checks.

No command in this implementation should contact OpenAI or Readwise.

## 16. Out Of Scope

Do not implement in this slice:

- data migration to server
- actual server cutover
- cron automation
- app-level login
- team-facing read-only wiki site
- public API for agents
- backup automation beyond documenting the v1 requirement
- private vault Git auto-commit/push workflow
- changes to synthesis, ingestion, or render semantics

## 17. Definition Of Done

Implementation is done when:

- server example path config exists
- production env example exists
- backend Docker image exists
- frontend Docker image exists
- LLM Wiki Compose file exists
- Caddy snippet for `wiki.plattenradar.de` exists
- GitHub Actions deploy workflow exists
- server helper script exists
- deployment health check script exists
- deployment runbook exists
- tests and local quality gates pass
- docs clearly state that v1 deploys only the management app
- docs clearly state that productive data remains server-side and is not managed
  by GitHub Actions

## 18. Suggested Commit Split

Use small commits:

1. `docs: add llm wiki server deployment runbook`
2. `build: package management app for docker deployment`
3. `ops: add caddy snippet and server helpers`
4. `ci: add llm wiki deploy workflow`
5. `test: cover production management app config assumptions`

Do not commit secrets.
