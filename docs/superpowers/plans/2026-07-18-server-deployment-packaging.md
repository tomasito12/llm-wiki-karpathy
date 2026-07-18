# Server Deployment Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the LLM Wiki management app for Hetzner deployment behind `wiki.plattenradar.de` with Docker, Caddy Basic Auth snippet, GitHub Actions deploy, helper/health scripts, and runbook.

**Architecture:** Two containers (`llm-wiki-api`, `llm-wiki-frontend`) on a Docker network shared with the existing Music Review Caddy. No public Caddy in this compose file. Productive data stays on host mounts under `/srv/llm-wiki/{data,vault-private}` and is never deployed by CI.

**Tech Stack:** Docker Compose, Hatch/Python 3.12 FastAPI, Node/Vite static nginx, Caddy Basic Auth, GitHub Actions SSH deploy.

## Global Constraints

- Domain: `wiki.plattenradar.de`; Basic Auth only; management app only.
- Do not start a second public Caddy on 80/443.
- Do not bake secrets into images or commit real credentials.
- Productive data is not uploaded by GitHub Actions.
- Cron, data migration, cutover, app login are out of scope.
- Do not commit unless the user asks (user rule overrides plan commit steps).
- Caddy must proxy `/api*` without stripping the `/api` prefix (FastAPI routes are under `/api/...`). Prefer `handle /api*` over `handle_path /api/*`.

## File Map

| Path | Responsibility |
|------|----------------|
| `config/wiki_paths.server.example.toml` | Server path placeholders |
| `deploy/llm-wiki.env.example` | Env placeholders |
| `deploy/Dockerfile.api` | Backend image |
| `deploy/docker-entrypoint-api.sh` | Validate paths config + start API |
| `deploy/Dockerfile.management-ui` | Frontend build + nginx |
| `deploy/nginx.management-ui.conf` | SPA + `/api` not served by nginx (Caddy routes API) |
| `compose.llm-wiki.yml` | API + frontend services + mounts + external network |
| `deploy/Caddyfile.llm-wiki.example` | Site block for Music Review Caddy |
| `.github/workflows/deploy-llm-wiki.yml` | Verify + SSH deploy |
| `scripts/server_llm_wiki.sh` | SSH/compose/health helper |
| `scripts/check_llm_wiki_deploy_health.sh` | Read-only health checks |
| `docs/server-deployment-runbook.md` | Operator runbook |
| `docs/hetzner-server-primary-deployment-spec.md` | Link to runbook |
| `tests/management_web/test_api.py` (+ maybe new) | Health/config with paths |
| `web/management/src/api.test.ts` | Relative `/api` paths |

---

### Task 1: Server config + env examples

**Files:**
- Create: `config/wiki_paths.server.example.toml`
- Create: `deploy/llm-wiki.env.example`

- [ ] **Step 1:** Write files exactly as specified in `docs/server-deployment-packaging-spec.md` sections 5–6.
- [ ] **Step 2:** Verify placeholders only (no secrets, no host IPs).

### Task 2: Docker packaging + Compose

**Files:**
- Create: `deploy/Dockerfile.api`, `deploy/docker-entrypoint-api.sh`
- Create: `deploy/Dockerfile.management-ui`, `deploy/nginx.management-ui.conf`
- Create: `compose.llm-wiki.yml`

- [ ] **Step 1:** API image: Python 3.12, install hatch deps from `pyproject.toml`, entrypoint fails if `LLM_WIKI_PATHS_CONFIG` missing/absent file, run management-api on `0.0.0.0:8000`.
- [ ] **Step 2:** Frontend image: multi-stage Node build of `web/management`, nginx serves `dist` on port 80, SPA fallback.
- [ ] **Step 3:** Compose: services `llm-wiki-api` / `llm-wiki-frontend`; mount `/srv/llm-wiki/data` and `vault-private` at same absolute paths; `env_file` for API; join external network `music-review_default` (document if name differs); no public ports required.
- [ ] **Step 4:** `docker compose -f compose.llm-wiki.yml config` (and `build` if Docker available).

### Task 3: Caddy snippet + server scripts

**Files:**
- Create: `deploy/Caddyfile.llm-wiki.example`
- Create: `scripts/server_llm_wiki.sh`
- Create: `scripts/check_llm_wiki_deploy_health.sh`

- [ ] **Step 1:** Caddy site with basicauth placeholders; `handle /api*` → api:8000; `handle` → frontend:80. Notes in runbook how to merge into Music Review Caddy.
- [ ] **Step 2:** Helper script: `status|ssh|logs|compose|health`; loads `.env.server`; never prints secrets; dry-run friendly.
- [ ] **Step 3:** Health script: requires `LLM_WIKI_HEALTH_URL` + basic auth; checks frontend, `/api/health`, `/api/config`, `/api/ops/status`; read-only; exits non-zero if vars missing.

### Task 4: GitHub Actions deploy workflow

**Files:**
- Create: `.github/workflows/deploy-llm-wiki.yml`

- [ ] **Step 1:** Verify job: Python 3.12, hatch lint+test, npm lint/test/build, docker compose build.
- [ ] **Step 2:** Deploy job: SSH secrets, ff-only pull at `DEPLOY_PATH`, rebuild/restart only llm-wiki services, run health script, never overwrite server `.env` or path config, no cron.

### Task 5: Docs + tests + verification

**Files:**
- Create: `docs/server-deployment-runbook.md`
- Modify: `docs/hetzner-server-primary-deployment-spec.md`
- Modify/add: management_web API tests; `web/management/src/api.test.ts`

- [ ] **Step 1:** Runbook covering layout, secrets, DNS, Caddy merge, deploy, health, out-of-scope, server-primary warning.
- [ ] **Step 2:** Link from architecture spec.
- [ ] **Step 3:** Tests for health/config and relative `/api` client paths.
- [ ] **Step 4:** Run local verification commands from spec §15.

## Self-Review

- Spec §§5–17 mapped to tasks 1–5.
- No cron/cutover/migration.
- Caddy prefix stripping called out explicitly.
