# Product Roadmap Specification

Last updated: 2026-07-10

This document captures the next product directions for the LLM Wiki system.

It is not an implementation plan yet. Its purpose is to preserve the feature
ideas, constraints, risks, and open decisions before they are broken down into
smaller engineering tasks.

## Product Direction

The current system is still mostly operated through command-line commands and a
Streamlit review dashboard. That is acceptable for development, but it is not a
good long-term operating experience.

The next phase should move the system toward a maintainable product:

- a pleasant internal management interface
- a public or team-facing wiki surface
- stronger quality control over generated knowledge
- cleaner separation between code and knowledge repositories
- controlled automation for recurring work

The guiding principle is: automate the boring work, keep humans in control where
judgment matters, and avoid creating an expensive or opaque system.

## Feature Area 1: Internal Management Web App

### Goal

Replace the current Streamlit dashboard with a modern, elegant web application
for operating the whole system.

The current Streamlit dashboard is functional but visually unpleasant and
cognitively heavy. The new interface should make review and system management
feel calm, focused, and lightweight.

### Scope

The internal web app should eventually support:

- source ingestion review
- source summaries
- tag review and correction
- approval of extracted knowledge fragments
- execution of existing CLI workflows through buttons
- visibility into pipeline state
- configuration management
- run reports and failure states
- cost-aware controls for LLM calls

### UX Requirements

The interface should reduce cognitive load.

Important UX qualities:

- clean visual design
- step-by-step review flow
- compact but readable information density
- obvious next actions
- keyboard-friendly review where useful
- minimal repeated decisions
- clear separation between "needs my judgment" and "system status"
- graceful handling of long source documents
- no overwhelming wall of JSON unless explicitly requested

The user should be able to quickly answer:

- What sources need review?
- What did the model extract?
- Which tags look wrong?
- What will happen if I approve this?
- What pipeline steps are ready to run?
- Did the last run succeed?
- What needs attention?

### Technology Direction

Streamlit should not be the long-term UI layer.

Likely candidates:

- React with a Python backend
- Next.js with API routes or a separate backend
- FastAPI backend plus React frontend
- another modern web stack if it gives a better local-product experience

Open decision:

- whether this should start as a local-only app or be designed from day one as a
  deployable service.

## Feature Area 2: Team-Facing Wiki and Public Surface

### Goal

Make the generated wiki accessible beyond the local Obsidian vault, especially
for teammates.

The internal management app is for operating the system. The team-facing surface
is for reading and exploring knowledge.

### Possible Surfaces

The system may eventually expose:

- a published version of the Obsidian-style wiki
- a web version of generated synthesis pages
- tag and topic indexes
- source-backed pages with clear evidence links
- a trend/intelligence homepage
- daily or weekly highlights
- "tip of the day" or "idea of the day" sections
- new AI models and tools worth watching
- service automation insights
- contact-center and chatbot/voicebot trends

### Design Intent

The team-facing surface should be useful and stimulating, not just an archive.

It should help teammates discover:

- current AI developments
- service automation ideas
- relevant new models
- useful tools
- patterns that matter for chatbot and voicebot work
- operational risks and governance considerations

### Agent/API Entry Point

The public or team-facing site may later become an agent-facing entry point.

Possible agent use cases:

- search the wiki for relevant context
- load synthesis pages for an answer
- follow tags and related pages
- retrieve original sources when deeper evidence is needed
- provide context to other agents or workflows through an API

Open decision:

- whether agent access should be built into the same web application or exposed
  as a separate API/tool layer.

## Feature Area 3: Wiki Quality Linting and Knowledge Maintenance

### Goal

Build stronger quality-control passes over the finished wiki and underlying
knowledge graph.

The current linting is mostly structural. The next phase should include
semantic and maintenance-oriented checks.

### Desired Checks

The linting system should help answer:

- Which pages have become too large and should be split?
- Which pages are near-duplicates and should be merged?
- Which topics are semantically close but currently separate?
- Which tags are overused, vague, or drifting?
- Which pages have tags that do not fit the actual content?
- Which important tags are missing?
- Which categories are becoming too broad?
- Which pages are thin, stale, or weakly supported?
- Which source claims conflict with older synthesis?

### Tagging System Maintenance

Tags are important because they become routing handles for humans and agents.

The current tag system risks drifting because:

- LLM-suggested tags accumulate over time
- manual correction becomes tiring
- some tags may not match the extracted knowledge anymore
- too many similar tags can weaken search and retrieval

Future linting should propose:

- tag corrections
- tag merges
- tag deprecations
- new tags when they improve retrieval structure
- pages that need tag review

### Cost Constraints

Semantic linting must be cost-aware.

It should not blindly send every full article and every wiki page to an LLM on
each run.

Preferred strategies:

- use metadata, hashes, and embeddings before LLM calls
- lint only changed or suspicious pages
- use cheap local/static checks first
- batch expensive checks deliberately
- cache LLM lint decisions
- produce review suggestions instead of rewriting automatically

### Cadence

Possible linting cadence:

- lightweight checks after each render
- medium checks weekly
- deeper semantic maintenance monthly

Open decision:

- which lint suggestions can be auto-applied and which must always require human
  approval.

## Feature Area 4: Repository Split and Versioning Model

### Goal

Separate code development from knowledge production.

The current repository contains both:

- application/tooling code
- generated wiki and synthesis artifacts

That creates noise because normal knowledge operations produce Git changes while
code development is happening.

### Target Direction

Consider splitting into separate repositories:

- one repository for code and tooling
- one repository for the generated Obsidian/wiki knowledge base

Possible additional local-only or private storage:

- raw Readwise exports
- local API keys and configuration
- transient run logs
- preview artifacts
- backups

### Benefits

A split could make it easier to:

- version code changes separately from knowledge changes
- roll back bad ingestion or synthesis batches
- keep product development commits clean
- publish or share the wiki without exposing tooling internals
- eventually give teammates access to wiki output without code access

### Automatic Commits

Successful ingestion, review, render, or synthesis steps may eventually trigger
automatic commits.

This could provide a clean audit trail:

- one commit for new reviewed sources
- one commit for generated wiki render
- one commit for synthesis cache updates
- one commit for published-site updates

Safety requirement:

- automatic commits must be transparent and reversible.
- no automated job should push or publish without explicit policy.

### Vault Cleanup

The generated Obsidian vault should be cleaned up as part of this direction.

Known issue:

- the vault contains many files, instructions, and helper folders whose purpose
  is no longer obvious.

Future work should clarify:

- which folders are generated
- which folders are manual
- which files are Obsidian-facing
- which files are machine-only
- which instructions are still active
- which old artifacts can be archived or removed

## Feature Area 5: Automation and Scheduled Jobs

### Goal

Move repetitive operations into controlled scheduled jobs.

The user should not have to manually trigger every routine step. Human review
should remain where judgment matters.

### Candidate Jobs

Potential scheduled jobs:

- Readwise export/sync into local raw storage
- pre-analysis of newly exported sources
- first-pass extraction of knowledge fragments
- update of review queues
- render Stage 1 after approved reviews
- plan Stage 2 synthesis work
- run small approved synthesis batches
- wiki linting
- tag quality checks
- trend/intelligence page generation
- website rebuild and deployment

### Human Control Points

The most important human control point remains the ingestion/review step.

The user wants to review:

- source summaries
- extracted knowledge fragments when needed
- tags
- approvals before knowledge becomes durable

After approval, more steps can become automatic if they are well linted and
reversible.

### LLM Safety Controls

Automated LLM calls require strict safeguards.

Required controls:

- explicit batch limits
- cost limits
- no infinite retry loops
- dry-run modes
- audit logs
- idempotent jobs
- changed-only behavior
- cache usage
- failure reports
- no silent overwrites of reviewed human decisions

### Hosting Context

The user has a Hetzner virtual machine that may later host:

- the team-facing website
- cron jobs
- scheduled linting
- automated ingestion/export steps
- possibly an API layer

Open decision:

- whether the VM should run only published/read-only surfaces first, or also
  operate write-capable ingestion and synthesis jobs.

## Suggested Implementation Order

The feature areas should not all be built at once.

Recommended order:

1. Stabilize operating documentation and artifact boundaries.
2. Define which artifacts belong in Git and which are local-only.
3. Build a small operations command/report that summarizes current system state.
4. Replace or wrap the Streamlit review experience with a focused modern UI.
5. Add safe buttons for existing CLI workflows.
6. Improve semantic linting for tags and page maintenance.
7. Split repositories only after artifact boundaries are clear.
8. Add scheduled jobs with conservative limits.
9. Build the team-facing wiki surface.
10. Add agent/API access after retrieval semantics are stable.
11. Add trend/intelligence pages once the underlying data is reliable.

## Non-Goals For The Immediate Next Step

Do not immediately build:

- a full public website
- a complex multi-user permission system
- fully autonomous ingestion-to-publication
- automated semantic rewrites without review
- broad cron jobs that can create large LLM bills
- repository splitting before artifact boundaries are documented

## Open Questions

Key decisions still needed:

- Should the new internal UI be local-only first?
- Which frontend stack should be used?
- Should the backend reuse the existing Python CLI modules directly?
- Which CLI commands are safe to expose as buttons first?
- Which outputs should be committed automatically?
- Which preview and run artifacts should remain local-only?
- Should the team-facing wiki be a static site, an app, or an Obsidian publish
  style output?
- How should agent/API access authenticate?
- Which semantic linting checks can be done without LLM calls?
- What monthly LLM cost budget is acceptable for automation?
- Which jobs are safe to run on the Hetzner VM?

## Product Judgment

These directions are coherent with the second-brain vision, but they must be
sequenced carefully.

The system should first become easier to operate. The biggest near-term risk is
not missing features; it is operational overload. A beautiful management UI,
clear reports, and safe automation will likely create more value than adding
more knowledge categories.

The next concrete step should be a small operating layer: a status/report
command or simple management screen that shows what needs attention without
triggering expensive actions automatically.
