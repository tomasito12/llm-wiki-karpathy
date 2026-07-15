# Internal Management Web App Specification

Status: Draft 2 / review workspace decisions captured
Created: 2026-07-15

This document defines the planning track for Feature Area 1 from the product
roadmap: replacing the current Streamlit dashboard with a modern internal
management web application.

The document is intentionally not implementation-ready yet. It captures the
known goal, likely architecture, constraints, and the interview questions that
must be answered before a technical implementation spec is handed to Cursor.

## 1. Product Goal

Build a calm, reliable, modern web application for operating the LLM Wiki
system.

The current Streamlit dashboard remains useful as a temporary operator tool, but
it should not be the long-term product interface. The new app should reduce
cognitive load, make the system state understandable, and make common operations
safe to run without memorizing CLI commands.

The app should start local-first, but it must be designed with a clear path to
deployment on the user's Hetzner Cloud server.

Long-term direction:

- local development and personal operation first
- deployable private management app second
- team-facing reading surface remains separate from management
- no accidental public exposure of private source text, notes, or credentials

## 1.1 Interview Decisions Captured

Decision date: 2026-07-15

The management app is a personal operator cockpit.

Decisions:

- The management app is for the user only, even after deployment.
- The user is the only person who selects sources, reviews extracted knowledge,
  approves or rejects proposals, and operates write-capable workflows.
- The future team/public wiki surface should be separate from the management
  app.
- The team-facing surface should expose the curated end product: generated and
  synthesized wiki pages, indexes, and possibly trend/intelligence pages.
- The Hetzner deployment should eventually be write-capable for the user, not
  read-only forever.
- Authentication can start lightweight, with a single-user password login as the
  preferred direction.
- The first product pain to solve is article review: reviewing sources and
  extracted knowledge should become much more pleasant, focused, and less
  cognitively heavy than in Streamlit.

Second interview decisions:

- The first review workspace should be optimized for fast batch review, not
  deep reading by default.
- The normal review question is: "Does this look plausible enough?" The user
  wants to check whether tags roughly fit, whether the extracted concepts make
  sense, and whether the proposed knowledge fragments are understandable.
- The main review action should happen at article level. The user should not
  have to approve every extracted entity individually when the extraction is
  broadly correct.
- Article-level approval is only useful if the UI first gives a strong overview
  of the extracted entities. The user must be able to see what would be
  accepted before approving the article.
- Detail inspection must remain possible, but it should be secondary and
  available on demand.
- The current Streamlit pain points are:
  - the interface is visually unpleasant and cognitively heavy
  - raw JSON is not useful as the primary review surface
  - checking source text is cumbersome
  - maintaining the tag taxonomy is difficult
- The first implementation slice should show a read-only review experience
  before implementing writes, so the UX can be reviewed cheaply.
- Keyboard navigation is desirable and should be designed for, but it does not
  need to ship in the first read-only slice.

## 2. Relationship To Existing System

The web app should not replace the Python pipeline logic.

It should reuse existing modules for:

- path configuration via `config/wiki_paths.toml`
- Readwise sync and index safety
- ingest queue status
- source loading and source hashes
- review artifact loading/saving
- pre-analysis execution
- wiki render and lint checks
- synthesis plan, selection, and batch execution
- ops status, vault hygiene, release verification, and migration reports

The app should replace the Streamlit interaction layer over time, not duplicate
pipeline behavior in frontend code.

## 3. Proposed Architecture Direction

Recommended starting architecture:

```text
Browser UI
  |
  v
React or Next.js frontend
  |
  v
FastAPI backend
  |
  v
Existing Python modules and filesystem state
```

The backend should be the only layer that reads or writes local wiki state.

The frontend should call API endpoints and avoid direct filesystem assumptions.

This keeps the design compatible with:

- local-only operation
- deployment behind HTTPS on Hetzner
- future authentication
- future agent/API access
- future separation between management UI and public/team wiki surface

Management and team-facing reading should be separate applications or at least
separate route groups with separate authentication and source-text policies.
Combining them is only acceptable if there is a strong operational reason later,
such as sharing a backend search API. Even then, the management UI must remain
private and write-protected.

## 4. Deployment Intent

The app may run locally at first, but it should be designed as a deployable
service from the beginning.

Target deployment context:

- Hetzner Cloud VM
- private server process managed by systemd or Docker Compose
- reverse proxy such as Caddy or nginx
- HTTPS
- authentication before any management or source access
- environment-based secrets
- mounted or cloned knowledge store and vault directories

The deployed management app should eventually be allowed to run write-capable
operations for the user, including ingestion review, pre-analysis, synthesis,
render, and lint workflows. This requires stronger safety UX than a read-only
viewer:

- visible operation scope before execution
- dry-run previews where possible
- explicit confirmation for write operations
- operation logs
- no automatic public publishing as a side effect of management actions

Deployment must not be treated as an afterthought because it affects:

- authentication
- filesystem paths
- secrets handling
- background job execution
- long-running LLM operations
- access to private source text
- backup and rollback policy

## 5. Security And Privacy Principles

The app will manage private data.

Sensitive data may include:

- full Readwise source text
- copyrighted article exports
- personal notes
- future meeting transcripts
- EnBW/customer-related notes
- API keys and tokens
- generated synthesis and review state

Therefore:

- no management endpoint should be public without authentication
- management access is single-user by default
- source text access must be explicitly controlled
- write operations must require authenticated operator access
- destructive operations must require confirmation
- API keys must never be sent to the frontend
- logs must avoid leaking full article text unless intentionally requested
- future team/public surfaces must have a different source-text policy than the
  private management app

Preferred first deployed authentication direction:

- single-user login with a strong password
- HTTPS at the reverse proxy
- secure session cookie
- no public registration
- no team accounts in v0

Basic Auth is acceptable only as a temporary deployment shield if it meaningfully
speeds up the first private deployment. OAuth and VPN-only are not required for
v0 unless the deployment threat model changes.

## 6. Initial Product Scope

The first version should focus on making the existing system easier to operate.

After the first interview, the primary v0 product priority is:

> Make article review substantially more pleasant than the current Streamlit
> workflow.

Status and operations remain important, but they should support the review flow
rather than dominate the first product slice.

Recommended v0 scope:

- System status dashboard based on `wiki-ops-status`
- Ingestion queue overview
- Source detail view
- Current raw/source hash and stale-analysis warnings
- Review artifact status: not started, in progress, finished, skipped
- readable source summary display
- focused batch article review workspace
- extracted proposal review with approve/reject/defer/edit actions
- tag review and correction
- clear "what changed / what will be saved" preview
- Buttons for safe dry-runs
- Explicit buttons for real operations with confirmations
- Run logs and recent failures
- Path configuration visibility

Recommended first write-capable actions:

- start pre-analysis with limit and delay
- re-analyze one source
- save review draft
- finish review
- run wiki render dry-run
- run wiki lint
- run synthesis plan/select

Real operations that call LLMs or rewrite many files should be gated behind
clear confirmations and visible limits.

The v0 review surface should prioritize the following information:

- source title, author, publication, date, and category
- source summary and key insights in human-readable prose
- extracted tags as visible chips
- proposed entities grouped by category
- clear stale-analysis state
- quick movement between sources
- optional drill-down into the source text and full structured artifact

JSON must not be the primary UI. It may exist in a collapsed debug/details area
for troubleshooting.

For the first read-only UX slice, it is acceptable to implement only these
entity groups:

- source summary
- topics
- glossary
- trends

However, the data model and layout must be designed so these groups can be
added immediately afterward without redesigning the page:

- how-tos
- tools
- models
- signals
- interview insights

The full review workflow is not considered complete until all extracted entity
types can be inspected.

## 7. Non-Goals For The First Slice

Do not build these in the first implementation slice:

- public/team wiki reader
- multi-user permission model
- full replacement of every Streamlit review tab at once
- semantic tag linting UI
- automatic cron scheduling
- autonomous ingestion-to-render pipeline
- public agent API
- source-text sharing policy for teammates
- full mobile-optimized interface
- write-capable approval actions in the first read-only UX slice
- keyboard shortcuts if they slow down the first UX validation

These can be designed later once the management foundation is stable.

## 8. Suggested First Implementation Slice

The first engineering slice should prove the architecture, not the whole
product.

Suggested slice name:

```text
management-web-v0-readonly-batch-review
```

Definition of Done:

- Backend starts locally.
- Frontend starts locally.
- App reads `config/wiki_paths.toml`.
- Queue page displays not started / in progress / finished / skipped counts.
- Review workspace can move quickly through a queue of sources.
- Review workspace can load one source and show:
  - title
  - source id
  - Readwise id
  - raw paths
  - current hash
  - review artifact hash
  - stale/not stale state
  - review status
- Review workspace shows a compact human-readable review card with at least:
  - source summary
  - key insights
  - proposed topics
  - proposed glossary terms
  - proposed trends
- The compact review card must make the extraction inspectable enough that the
  user can decide whether the whole article can be approved.
- The layout includes obvious extension points for how-tos, tools, models,
  signals, and interview insights.
- Raw JSON is hidden by default and only available in a debug/details drawer.
- Source text inspection is available on demand, not forced into the primary
  batch-review surface.
- Review actions can be read-only placeholders in the first technical slice,
  but the UI must be designed around approval workflow rather than JSON display.
- A small status panel shows whether render/synthesis are current, but deep ops
  controls can stay out of the first slice.
- Tests cover backend queue/source endpoints.
- Documentation explains how to run locally.

This slice should avoid LLM calls.

Additional UX expectations:

- The page should feel calm, dense enough for repeated work, and not like a
  marketing page.
- The main flow should support scanning many articles without visual clutter.
- Tags should be visible enough that taxonomy drift is noticed early.
- Entity cards should be easy to compare across categories.
- Detail views should answer "why did the system extract this?" without making
  every review feel like a forensic audit.
- Individual entity approval is not part of the read-only slice. The UI should
  still make it visually clear where later per-entity disable/edit actions would
  live.

## 9. Later Slices

Potential follow-up slices:

1. Add how-tos, tools, models, signals, and interview insights to the review UI
2. Add keyboard navigation for next/previous source and common review actions
3. Persist review decisions from the new review workspace
4. Re-analysis and pre-analysis controls
5. Review artifact editing and approval for all entity categories
6. Operations buttons for render/lint/synthesis dry-runs
7. Real operation execution with confirmations and audit logs
8. Background job runner and progress streaming
9. Authentication layer
10. Hetzner deployment packaging
11. Team-facing reader surface
12. Agent/API search surface

## 10. Open Interview Questions

These questions must be answered before implementation details are finalized.

### 10.1 Users And Access

1. Who is allowed to use the management app at v0: only the user, or also
   trusted teammates?
   - Answer: only the user.
2. Should v0 assume single-user operation even if later deployment is planned?
   - Answer: yes.
3. Should team-facing reading be a separate app/surface from management?
   - Answer: yes, unless a later architecture review finds a strong reason to
     share parts of the app.

### 10.2 Deployment

4. Should the first version be local-only but deployment-shaped, or should it be
   deployed to Hetzner very early?
5. Do you prefer Docker Compose, systemd services, or no preference yet?
6. Should the Hetzner server operate write-capable jobs, or only read/publish at
   first?
   - Answer: eventually write-capable for the user.

### 10.3 Authentication

7. What authentication level is acceptable for the first deployed version:
   basic auth, single-user login, OAuth, VPN-only, or something else?
   - Answer: lightweight authentication is acceptable; prefer single-user login
     with password unless implementation cost argues for temporary Basic Auth.
8. Should full source text ever be accessible through the deployed management
   app from outside your local machine?
9. Should teammates ever see raw source text, or only generated summaries and
   synthesis pages?

### 10.4 Product Scope

10. What is the single most painful Streamlit workflow that the new UI should
    fix first?
    - Answer: reviewing articles and extracted knowledge.
11. Is the first priority review quality, operational overview, or fewer CLI
    commands?
    - Answer: review quality and review comfort first.
12. Should the first UI be optimized for batch review, deep review of one
    source, or system operations?
    - Answer: fast batch review first. Deep source review should be available
      on demand, but not dominate the main workspace.

### 10.5 Data And Writes

13. Should the first app version be read-only to reduce risk?
    - Answer: yes. The first implementation slice should be read-only so the
      user can review the UX before write behavior is added.
14. Which write action should be introduced first?
    - Proposed answer: article-level review decisions first. Detail edits can
      follow after the batch review shape is validated.
15. Should write actions call Python functions directly, or run existing CLI
    workflows through a job runner?

### 10.6 Background Jobs

16. Should long-running operations continue after the browser closes?
17. Do you need live progress updates for long runs?
18. Should jobs have explicit cost/delay/batch limits visible in the UI?

### 10.7 Technology Preferences

19. Do you have a preference between FastAPI + React/Vite and Next.js?
20. Should this repo contain frontend and backend together, or should the new UI
    become its own repository later?
21. Should the frontend use a component library such as shadcn/ui, Mantine, or
    plain custom components?

## 11. Review UX Principles

The review workspace should be designed around the actual job the user does:
high-volume plausibility review.

Principles:

- Batch first: the default interaction should help the user move through many
  sources quickly.
- Entity overview before article decision: the main action can be article-level
  approval, but only after the extracted entities are shown clearly enough to
  make that approval meaningful.
- Human-readable first: no raw JSON as the primary interface.
- Detail on demand: source text, raw artifacts, and extraction internals should
  be available, but not visually dominant.
- Taxonomy visible: tags should be prominent enough that drift and bad tags are
  easy to notice.
- Category grouped: topics, glossary, trends, and later how-tos/tools/models/
  signals/interview insights should be visually grouped.
- Keyboard-ready: the UI should be structured so keyboard shortcuts can be
  added cleanly after the first read-only slice.
- No accidental writes: v0 read-only must not save, mutate, call LLMs, render,
  or trigger pipeline commands.

## 12. Planned Review Decision Model

The planned write model should keep the main workflow article-based.

Recommended article-level statuses:

- `approved`: the extraction is good enough to enter the wiki pipeline
- `needs_attention`: the extraction is not trustworthy enough yet
- `skipped`: the source should not enter the wiki pipeline
- `reanalyze_requested`: the extraction should be regenerated before review

Entity-level actions should be secondary. They are useful when one or two
items are wrong but the article is otherwise valuable.

Recommended later entity-level actions:

- disable an extracted entity
- correct tags
- add a short reviewer note
- request re-analysis for the full article

The first write-capable slice should avoid complex rewriting of extracted
content. It should store review decisions and simple overrides rather than
turning the UI into a full knowledge editor.

## 13. Current Recommendation

Start with a local FastAPI backend plus React/Vite frontend in the existing code
repository.

Reasoning:

- the existing pipeline is Python-based
- FastAPI can reuse current modules cleanly
- React/Vite is simple for a local product UI
- deployment to Hetzner remains straightforward
- separating public/team surfaces can happen later

The first slice should be local, read-only, and avoid LLM calls. It should focus
on the batch review workspace, backed by queue/source endpoints and a compact
status panel. This gives confidence before adding write operations,
authentication, deployment packaging, and LLM-triggering controls.
