# Hetzner Server-Primary Deployment Specification

Status: Draft / interview decisions captured
Created: 2026-07-18

This document captures the planning state for moving the LLM Wiki system from
local operation to a server-primary deployment on the user's existing Hetzner
virtual machine.

It is intentionally a specification and decision log first, not yet a Cursor
implementation plan. The next step is to complete the remaining interview
questions, then split implementation into safe technical slices.

## 1. Goal

Run the LLM Wiki management dashboard on the Hetzner VM instead of operating it
locally.

The deployed system should let the user:

- open the management dashboard over the internet
- authenticate with username/password protection
- start existing pipeline jobs from the dashboard
- operate against the productive knowledge store and private vault on the server
- avoid local/server data drift
- prepare for future scheduled cron-based automation

The first server deployment is still private. It is not the team-facing public
wiki product.

Decision: v1 exposes only the private management app. A read-only wiki website
or team-facing knowledge surface is a separate future feature.

## 2. Source Documents Reviewed

This spec is based on these existing project documents:

- `docs/internal-management-web-app-spec.md`
- `docs/repo-vault-split-migration-spec.md`
- `docs/product-roadmap-spec.md`
- `docs/path-configuration-technical-spec.md`
- `docs/private-vault-source-access-spec.md`
- `docs/management-web-pipeline-cockpit-spec.md`
- `docs/management-web-update-wiki-workflow-spec.md`

The adjacent `music-review` repository was also reviewed as an infrastructure
reference, especially:

- `deploy/README.md`
- `compose.yml`
- `deploy/Caddyfile`
- `scripts/server.sh`
- `.github/workflows/deploy.yml`
- `scripts/sync_server_git.sh`

Important constraint: secrets, `.env` values, SSH keys, and private server
credentials must remain outside documentation and must not be printed in agent
responses.

## 3. Captured Interview Decisions

### 3.1 Production Data Authority

Decision: the Hetzner server becomes the productive source of truth.

After cutover:

- productive ingestion runs on the server
- productive review decisions are written on the server
- productive synthesis cache lives on the server
- productive render output is generated on the server
- productive backups happen on the server
- local operation should not write productive data anymore

Local development remains possible, but it should be code-focused. If local
testing needs data, it should use a copied snapshot or test fixture, not write
back to the productive store.

Rejected approach: bidirectional sync between local and server. It is too likely
to create inconsistent review, synthesis, render, and manifest state.

### 3.2 Server

Decision: deploy LLM Wiki on the same Hetzner VM that already hosts
`music-review`.

This means the LLM Wiki deployment must coexist with the existing Music Review
stack and must not compete for ports `80` or `443`.

### 3.3 Domain

Decision: use the existing `plattenradar.de` domain temporarily.

Recommended route:

```text
wiki.plattenradar.de
```

Use a subdomain instead of a path under `plattenradar.de` because it keeps the
management app cleanly separated from Music Review routing, auth, cookies, and
future migration.

### 3.4 Reverse Proxy and Auth

Decision: use Caddy Basic Auth for the first deployment.

Reason:

- simple and robust
- enough for a first private single-user deployment
- avoids delaying server migration with app-level auth
- keeps all management endpoints behind a password gate

Future app-level login can be added later if needed.

### 3.5 Obsidian and Private Vault Access

Decision: use a read-only local mirror for Obsidian.

The productive private vault is rendered and versioned on the server. The user
can pull a local copy for Obsidian browsing, but local edits are not part of the
productive workflow.

The local Obsidian copy should be treated as read-only. Manual edits to the
generated wiki are out of scope and should not be pushed back as productive
state.

### 3.6 Knowledge Store Backup Model

Decision: the knowledge store is not Git-versioned initially.

Instead, `/srv/llm-wiki/data` should be protected by regular server-side file
backups/snapshots.

The knowledge store contains raw exports, reviews, synthesis state, manifests,
and operational run reports. It is the canonical source for regenerating the
rendered vault.

### 3.7 Private Vault Versioning

Decision: the private generated vault should be Git-versioned separately.

Decision update: the private vault Git remote should be a private GitHub
repository.

This gives the user a clean local read-only mirror workflow:

```bash
git pull
```

The private vault Git repo contains the rendered Obsidian wiki output, including
source pages as designed by the source-access specs. It does not replace the
knowledge store.

Expected direction:

- server renders the productive vault
- server commits rendered vault changes when a productive render/release is
  accepted
- server pushes to the private GitHub vault repository
- local Obsidian vault pulls from the private GitHub vault repository
- local vault usage is read-only by convention

### 3.8 Deployment Mechanism

Decision: use GitHub Actions deployment like Music Review.

The deployment should:

- verify code before deploy
- SSH into the existing Hetzner VM
- fetch/fast-forward the server checkout
- rebuild/restart Docker Compose services
- leave production `.env`, data, vault, and backups on the server
- run health checks after deploy

GitHub Actions must not upload local secrets or productive data.

### 3.9 Long-Running Jobs

Decision: first server slice uses a simple server-side single-job runner.

For v1 deployment:

- dashboard buttons start server-side jobs
- backend executes the job
- only one long-running job may run at a time
- job status and logs are visible in the dashboard
- cron automation is explicitly out of scope for the first deployment

Future feature slice:

- cron jobs on the server
- schedules configurable through the dashboard
- safeguards against infinite loops and uncontrolled API spending
- job history, retries, and failure reporting

## 4. Target Server Layout

Recommended layout:

```text
/srv/llm-wiki/
  app/                  # code repo checkout: llm-wiki-karpathy
  data/                 # productive knowledge store, not Git-versioned
  vault-private/        # productive rendered private vault, separate Git repo
  backups/              # server-side backups and snapshots
  secrets/              # optional server-only secret material, not in Git
```

The application should use a server-specific path config, for example:

```text
/srv/llm-wiki/app/config/wiki_paths.server.toml
```

or a server-local config file outside the Git checkout if secrets or
machine-specific paths should never be touched by deploys.

Expected productive roots:

```toml
[paths]
code_root = "/srv/llm-wiki/app"
knowledge_root = "/srv/llm-wiki/data"
vault_root = "/srv/llm-wiki/vault-private"
```

All management app processes, pipeline commands, and jobs must use this server
path configuration.

## 5. Target Runtime Architecture

Recommended Docker Compose services:

```text
shared caddy
  - owns ports 80/443 for the VM
  - routes Music Review and LLM Wiki domains
  - applies Basic Auth for wiki.plattenradar.de
  - terminates HTTPS

llm-wiki-api
  - FastAPI backend
  - reads/writes productive paths through WikiPaths
  - owns job runner API
  - has access to server .env secrets

llm-wiki-frontend
  - built React management frontend
  - served as static frontend
  - talks only to llm-wiki-api
```

The exact service names may differ, but the boundaries should remain:

- frontend has no secrets and no filesystem access
- backend owns all writes
- Caddy owns public ingress and authentication
- data and vault are mounted from server directories

## 6. Caddy / Domain Model

Music Review already uses Caddy for:

```text
plattenradar.de
www.plattenradar.de
```

LLM Wiki should add:

```text
wiki.plattenradar.de
```

Because both projects share one VM, there should be one effective public Caddy
entrypoint for ports `80` and `443`.

Decision: do not introduce a second Caddy container.

For the first deployment slice, keep the existing Music Review Caddy as the
public edge proxy and extend it to route `wiki.plattenradar.de` to the LLM Wiki
services.

Reason:

- Music Review already owns ports `80` and `443`
- Caddy already handles HTTPS for `plattenradar.de`
- introducing a second Caddy would create port conflicts
- moving to a fully shared reverse-proxy stack before the first LLM Wiki deploy
  would add migration risk
- extending the existing edge proxy is the smallest reversible change

Implementation direction:

- avoid two independent Caddy containers competing for ports
- connect the LLM Wiki frontend/API services to a Docker network reachable by
  the existing Caddy container
- add a Caddy site block for `wiki.plattenradar.de`
- apply Caddy Basic Auth to the entire LLM Wiki site block
- route frontend traffic to the LLM Wiki frontend service
- route API traffic to the LLM Wiki API service
- keep the migration incremental and reversible

Future option:

- if more services are added later, extract Caddy into a server-level
  `/srv/edge-proxy` stack. This should be a separate infrastructure refactor,
  not part of the first LLM Wiki deployment.

## 7. Data Ownership Rules

### Code Repo

The code repo contains:

- Python code
- frontend code
- tests
- documentation
- config templates
- Docker and deployment definitions

The code repo must not contain productive server data.

### Knowledge Store

The knowledge store contains:

- `raw/readwise`
- `state/reviews`
- `state/synthesis`
- render graph and render manifest
- release manifests
- run reports
- operational temporary artifacts that are not yet cleaned

It is server-primary and backup-protected.

### Private Vault

The private vault contains:

- generated Obsidian wiki pages
- source pages
- indexes
- rendered synthesis pages

It is server-generated and Git-versioned. Local Obsidian access is via read-only
Git mirror.

## 8. Migration Cutover Model

Recommended migration:

1. Stop local productive jobs.
2. Run local status checks.
3. Create local backup/snapshot before transfer.
4. Copy current `llm-wiki-data` to `/srv/llm-wiki/data`.
5. Copy current `llm-wiki-vault-private` to `/srv/llm-wiki/vault-private`.
6. Configure server paths.
7. Verify server state with:
   - `wiki-ops-status`
   - `wiki-lint`
   - release verification
   - optional `wiki-render --dry-run`
8. Start management app behind Basic Auth.
9. Declare server as production source of truth.
10. Treat local vault as read-only mirror.

Decision: the first migration should be a one-time controlled cutover with a
short local freeze.

This means:

- local productive operation stops before copying data
- current local data and vault state are backed up
- the knowledge store and private vault are copied to the server once
- server verification must pass before productive use resumes
- after verification, the server becomes the source of truth
- local productive writes do not resume after cutover

## 9. Backup Requirements

Server backups must protect at least:

```text
/srv/llm-wiki/data
/srv/llm-wiki/vault-private
/srv/llm-wiki/app/config/wiki_paths.server.toml
/srv/llm-wiki/app/.env or server-side env file
```

Secrets should be backed up carefully, but not copied into documentation,
commits, or logs.

Minimum backup model for first deployment:

- manual pre-migration backup
- daily server-side snapshot of `/srv/llm-wiki/data`
- regular backup of `/srv/llm-wiki/vault-private` or rely on Git remote plus
  server snapshots
- retention policy to prevent unlimited backup growth
- Hetzner snapshot/backup should be enabled or documented as part of the v1
  operations model

Future backup improvements:

- offsite copy to local disk, iCloud, or another target
- dashboard visibility for latest successful backup
- restore drill/runbook

## 10. Security Requirements

First deployment:

- HTTPS via Caddy
- Caddy Basic Auth before any LLM Wiki route
- no public unauthenticated management endpoint
- no secrets in frontend bundle
- OpenAI and Readwise credentials only server-side
- logs must avoid dumping full article text by default
- server `.env` must not be overwritten by deployment

Future hardening:

- app-level session login
- CSRF protection for write operations
- per-operation confirmation for destructive actions
- audit trail for all write-capable jobs
- optional IP restrictions or VPN if threat model changes

## 11. Operational Rules After Cutover

After the server becomes primary:

- do not run productive local ingestion
- do not run productive local synthesis
- do not run productive local render
- do not manually edit generated vault pages locally
- use dashboard or server-side commands for production operations
- local code development deploys through GitHub Actions
- local Obsidian uses read-only mirror of the private vault repo

If emergency local operation is required, it needs an explicit runbook:

- pause server jobs
- take backup
- pull latest server state
- run local operation
- push/copy state back intentionally
- verify server state

This emergency path should not be the normal workflow.

## 12. Implementation Slices To Write Next

This deployment should be split into separate Cursor-ready technical specs.

Recommended order:

1. Server deployment packaging
   - Docker Compose for LLM Wiki API/frontend
   - server path config
   - production environment variables
   - health endpoint
   - health checks must be read-only and must not trigger LLM calls

2. Shared Caddy integration
   - add `wiki.plattenradar.de`
   - Basic Auth
   - extend existing Music Review Caddy as edge proxy
   - add shared Docker network or network aliases as needed
   - avoid a second Caddy container

3. GitHub Actions deploy workflow
   - verify
   - SSH deploy
   - fast-forward server checkout
   - rebuild/restart services
   - health checks

4. Server data migration runbook
   - backup local data
   - copy data/vault to server
   - configure paths
   - verify
   - declare cutover

5. Single-job runner hardening
   - enforce one long-running job at a time
   - persist job status and logs
   - dashboard reads job status
   - no cron yet

6. Backup/snapshot automation
   - server-side backup script
   - retention policy
   - status visibility

7. Cron automation
   - scheduled Readwise sync
   - scheduled preanalysis
   - scheduled approved-review processing
   - scheduled lint/status
   - dashboard-managed schedules

## 13. Open Questions

All major v1 deployment architecture questions are answered.

Health checks for v1:

- frontend is reachable behind Caddy and Basic Auth
- API health endpoint is reachable
- backend can load the server path configuration
- backend can see the configured knowledge store path
- backend can see the configured private vault path
- `wiki-ops-status` can run server-side in read-only mode
- checks must not trigger LLM calls
- checks must not run render, synthesis, ingestion, or cleanup automatically

## 14. Current Recommendation Summary

Use a server-primary architecture:

```text
GitHub
  -> deploys code to Hetzner app checkout

Hetzner /srv/llm-wiki/data
  -> productive knowledge store, backed up by snapshots

Hetzner /srv/llm-wiki/vault-private
  -> productive rendered private vault, Git-versioned

Local machine
  -> code development and read-only Obsidian mirror
```

Avoid bidirectional data sync. Use GitHub Actions for code deployment, Caddy for
HTTPS and Basic Auth, and a simple single-job runner for the first write-capable
server dashboard. Add cron automation only after the manual server dashboard is
stable.
