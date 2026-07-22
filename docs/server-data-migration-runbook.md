# Server Data Migration Runbook (Cutover)

Status: ready to execute after checklist sign-off  
Related:

- `docs/hetzner-server-primary-deployment-spec.md` (cutover model)
- `docs/server-deployment-runbook.md` (app deploy; already done)
- `docs/knowledge-store-migration-plan-spec.md`

This runbook covers **copying productive knowledge store + private vault** to
the Hetzner VM and declaring the server the source of truth. It does **not**
cover cron, app login, or a public team wiki.

**Do not run the copy steps until Section 2 blockers are resolved or explicitly
accepted.**

---

## 1. Prerequisite audit (2026-07-21)

### 1.1 Local sources (OK to copy from)

| Item | Value |
|------|--------|
| Knowledge root | `/Users/plischke/Desktop/Private Development/llm-wiki-data` (~60 MB) |
| Vault root | `/Users/plischke/Desktop/Private Development/llm-wiki-vault-private` (~37 MB) |
| Path config | `config/wiki_paths.toml` (external roots already) |
| Raw pairs | 506 |
| Review artifacts | 460 (307 finished, 153 in progress) |
| Synthesis cache | 121 entries |
| Vault wiki files | ~1321 |
| Total transfer size | ~100 MB (comfortable for rsync over SSH) |

`hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root`:

- Roots already external (good).
- Readiness: **warning** (not blocked).

### 1.2 Server targets (empty, ready)

| Item | Value |
|------|--------|
| Data mount | `/srv/llm-wiki/data` — empty, owned by `deploy` |
| Vault mount | `/srv/llm-wiki/vault-private` — empty, owned by `deploy` |
| Path config | `/srv/llm-wiki/app/config/wiki_paths.server.toml` present |
| Env | `/srv/llm-wiki/app/deploy/llm-wiki.env` present |
| App | `llm-wiki-api` / `llm-wiki-frontend` up; public UI behind Basic Auth |
| Disk | ~15 GB free on `/` (enough) |

Compose already mounts host paths into the API container at the same absolute
paths as `wiki_paths.server.toml`.

### 1.3 Deploy / DNS (already done)

- `https://wiki.plattenradar.de` serves management UI + `/api/health`.
- Caddy Basic Auth on Music Review Caddy (not in `deploy/llm-wiki.env`).

---

## 2. Blockers / accept-as-is before copy

Resolve or consciously accept each item:

| # | Finding | Recommendation |
|---|---------|----------------|
| B1 | Local `hatch run management-api` still running against local data | Stop before freeze/copy so nothing writes during transfer |
| B2 | Vault has **no Git remote** (`git remote -v` empty) | Optional before cutover: create private GitHub vault repo + `git remote add`. Can defer; rsync still works |
| B3 | Vault has **~108 uncommitted modified files** on `master` | Prefer commit (or stash decision) so server copy matches a known commit; or copy dirty tree as-is and note it |
| B4 | Render **stale**: 7 finished sources not in last render | Optional: `wiki-render` locally before copy so vault matches reviews |
| B5 | Migration plan: temp artifacts under `tmp/` (~2.9 MB) | Optional: cleanup after a release; safe to copy and clean on server later |
| B6 | Synthesis: 28 stale / 53 changed candidates | Optional hygiene; not a hard stop for first cutover |
| B7 | After cutover, local writes must stop | Agree: no local Review/Render/Synthesis against productive roots |

Minimum for a first cutover: **B1** + accept B2–B6 (or fix preferred ones).

---

## 3. Freeze checklist (operator)

- [ ] Stop local management API / UI / Streamlit dashboard
- [ ] Stop any local ingest, render, synthesis, readwise-sync jobs
- [ ] Confirm no other machine writes the same folders
- [ ] Re-run status once more (optional snapshot of counts):

```bash
cd "/Users/plischke/Desktop/Private Development/llm-wiki-karpathy"
hatch run wiki-ops-status --paths-config config/wiki_paths.toml \
  --migration-plan --require-external-knowledge-root --require-external-vault-root
```

- [ ] Local backup (tar or copy) of both trees, e.g.:

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$HOME/Backups/llm-wiki-pre-cutover-$STAMP"
mkdir -p "$BACKUP_DIR"
rsync -a "/Users/plischke/Desktop/Private Development/llm-wiki-data/" \
  "$BACKUP_DIR/llm-wiki-data/"
rsync -a "/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/" \
  "$BACKUP_DIR/llm-wiki-vault-private/"
```

---

## 4. Copy to server (sensitive — run only after Section 2/3)

Use the existing deploy SSH key. Paths assume defaults from Music Review sync /
`hatch run server`.

```bash
SSH_KEY="${MUSIC_REVIEW_SYNC_KEY:-$HOME/.ssh/music_review_deploy}"
SERVER="${MUSIC_REVIEW_SYNC_USER:-deploy}@${MUSIC_REVIEW_SYNC_HOST:-167.233.138.166}"

# Knowledge store → /srv/llm-wiki/data
rsync -avz --progress \
  -e "ssh -i $SSH_KEY -o IdentitiesOnly=yes" \
  "/Users/plischke/Desktop/Private Development/llm-wiki-data/" \
  "$SERVER:/srv/llm-wiki/data/"

# Private vault → /srv/llm-wiki/vault-private
rsync -avz --progress \
  -e "ssh -i $SSH_KEY -o IdentitiesOnly=yes" \
  "/Users/plischke/Desktop/Private Development/llm-wiki-vault-private/" \
  "$SERVER:/srv/llm-wiki/vault-private/"
```

Notes:

- Trailing `/` on sources copies **contents** into the target dirs.
- Exclude nothing required; `.git` in the vault **should** be included if you
  want Git history on the server.
- Optional exclude of junk: `--exclude '.DS_Store'`.
- Do **not** rsync into `/srv/llm-wiki/app` (code stays Git-deployed).

Ownership (if anything lands as wrong user):

```bash
ssh -i "$SSH_KEY" -o IdentitiesOnly=yes "$SERVER" \
  'sudo chown -R deploy:deploy /srv/llm-wiki/data /srv/llm-wiki/vault-private'
```

Restart API so it re-reads mounts (usually unnecessary for bind mounts, but
safe after first fill):

```bash
ssh -i "$SSH_KEY" -o IdentitiesOnly=yes "$SERVER" \
  'cd /srv/llm-wiki/app && docker compose -f compose.llm-wiki.yml up -d --force-recreate llm-wiki-api'
```

---

## 5. Verify on server

```bash
ssh -i "$SSH_KEY" -o IdentitiesOnly=yes "$SERVER" bash -s <<'EOF'
set -euo pipefail
du -sh /srv/llm-wiki/data /srv/llm-wiki/vault-private
test -d /srv/llm-wiki/data/raw/readwise
test -d /srv/llm-wiki/data/state/reviews
test -d /srv/llm-wiki/vault-private/wiki
# counts should be in the same ballpark as local
find /srv/llm-wiki/data/raw/readwise -type f | wc -l
find /srv/llm-wiki/vault-private/wiki -type f | wc -l
docker run --rm --network music-review_default curlimages/curl:8.5.0 \
  -sS http://llm-wiki-api:8000/api/health
docker run --rm --network music-review_default curlimages/curl:8.5.0 \
  -sS http://llm-wiki-api:8000/api/ops/status | head -c 2000
echo
EOF
```

From your laptop (with Basic Auth):

```bash
export LLM_WIKI_HEALTH_URL=https://wiki.plattenradar.de
export LLM_WIKI_BASIC_AUTH_USER=...
export LLM_WIKI_BASIC_AUTH_PASSWORD=...
./scripts/check_llm_wiki_deploy_health.sh
```

In the UI: Review queue should show sources; Ops/status should match local
counts approximately.

Optional inside API container / on host checkout:

```bash
cd /srv/llm-wiki/app
# if hatch/python available on host; otherwise use docker exec
docker exec -w /app llm-wiki-api \
  hatch run wiki-ops-status --paths-config /app/config/wiki_paths.server.toml
```

---

## 6. Declare cutover

After verification passes:

- [ ] Server is the **only** productive writer for knowledge store + vault
- [ ] Local `config/wiki_paths.toml` may remain for **read-only** experiments;
      do not run write workflows against those roots
- [ ] Local Obsidian: pull/mirror only once a vault remote exists; until then,
      treat server tree as canonical
- [ ] Take a server-side snapshot under `/srv/llm-wiki/backups/` or a Hetzner
      snapshot soon after cutover
- [ ] Record cutover date/time in your ops notes

Rollback (only if verification fails **before** productive server writes):

- Leave server dirs in place or empty them after backup
- Resume local API against local roots
- Do **not** rsync server → local blindly if you already wrote on the server

---

## 7. Explicitly out of scope here

- Automating cron on the server
- Vault auto-commit/push to GitHub
- Making the vault public / team read-only site
- Replacing Caddy Basic Auth with app login
- Continuous sync local ↔ server (one-shot cutover only)

---

## 8. Suggested execution order (next session)

1. Decide B2–B6 (commit vault? render first? remote?).
2. Complete Section 3 freeze + backup.
3. Run Section 4 rsync.
4. Run Section 5 verify.
5. Tick Section 6 cutover.

---

## 9. Cutover log

| When (UTC) | What |
|------------|------|
| 2026-07-21 ~16:00 | Local backup `~/Backups/llm-wiki-pre-cutover-20260721-175935` |
| 2026-07-21 ~16:00 | rsync data + vault to `/srv/llm-wiki/{data,vault-private}`; API recreated |
| 2026-07-21 | Verified: raw 1012, reviews 521, vault wiki ~1319; health ok; ops shows 506 paired / 307 finished |

Decisions at cutover: vault remote `tomasito12/llm-wiki-vault-private` on `main` (clean); stale render accepted — render on server later; local management-api stopped.
