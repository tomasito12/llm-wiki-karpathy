# LLM Wiki (Karpathy Pattern)

A self-maintaining personal knowledge base powered by LLMs, based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285).

Instead of re-searching raw documents on every question (like RAG), the LLM **reads your sources once and builds a persistent, interlinked wiki** that compounds over time. The more sources you feed it, the richer and more connected it gets.

The long-term goal is broader than browsing generated notes in Obsidian: the wiki should become a grounded second brain for local agents, project work, personal notes, meeting transcripts, and eventually team or API access. See [Second Brain Vision](docs/second-brain-vision.md).

For the current implementation status and next stabilization steps, see [Current System Status](docs/current-system-status.md).

The active local operating mode now uses an external knowledge store and a
separate private generated vault. See [External Knowledge Store Operating
Mode](docs/external-operating-mode.md).

## Domain Focus

This wiki is optimized for the user's work as an AI expert at EnBW. The strongest relevance signal is knowledge that helps design, evaluate, operate, or improve AI-supported customer service: chatbots, voicebots, Cognigy AI, contact-center automation, service workflows, human handoff, quality evaluation, governance, and surrounding orchestration.

Cognigy is important because it is part of the current work context, but the wiki should not become vendor-locked. Competitors, replacement platforms, adjacent tools, and workflow architecture around bot platforms are also high-value when they help decide what to build, buy, replace, or integrate.

A second relevance signal is broader AI expertise: models, agents, tooling, evaluation, workflow automation, and practices that help teams work more efficiently with AI.

---

## Prerequisites

- Python 3.12. Hatch is pinned to Python 3.12 in `pyproject.toml`.
- [Hatch](https://hatch.pypa.io/) for running project commands.
- [Obsidian](https://obsidian.md/) (free) for browsing the wiki in real time
- Optional: [Cursor](https://cursor.sh/) or another LLM-powered editor that reads `AGENTS.md`

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/balukosuri/llm-wiki-karpathy.git
cd llm-wiki-karpathy
```

### 2. Open the project in your editor

Agents should read `AGENTS.md` first. Detailed behavior is scoped:

- `wiki/AGENTS.md` for the generated Obsidian vault contract
- `src/AGENTS.md` for code/tooling development workflows

### 3. Configure local paths

The real path config is machine-specific and intentionally not committed.

Copy the example and adjust paths if needed:

```bash
cp config/wiki_paths.example.toml config/wiki_paths.toml
```

The current local operating mode uses:

```text
knowledge store: /Users/plischke/Desktop/Private Development/llm-wiki-data
private vault:   /Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

Commands load `config/wiki_paths.toml` automatically when it exists.

### 4. Open the generated vault in Obsidian

Open the private generated vault in Obsidian:

```text
/Users/plischke/Desktop/Private Development/llm-wiki-vault-private
```

The managed wiki lives under its `wiki/` folder. The older repo-local `wiki/`
folder is kept as a development/release artifact, but the external vault is the
preferred browsing surface.

### 5. Export sources from Readwise

Set `READWISE_TOKEN` or `READWISE_API_TOKEN`, then run:

```bash
hatch run readwise-sync
```

With external paths configured, this exports archived Readwise Reader documents
tagged `processed` into the external knowledge store under `raw/readwise/` as
paired `.html` and `.md` files. Raw exports are local/private data and are not
committed to the code repo.

### 6. Review and approve extraction

Start the review dashboard:

```bash
hatch run dashboard
```

The dashboard analyzes raw Readwise exports and writes human-reviewed artifacts
under `state/reviews/<source_id>/review.json` in the configured knowledge
store. These review artifacts are the canonical source of truth for generated
wiki pages.

For unattended pre-analysis of pending exports:

```bash
hatch run ingest-preanalyze --limit 100
```

Pre-analysis still requires later human review in the dashboard.

### 7. Render the generated wiki

After review artifacts change, regenerate the Obsidian wiki:

```bash
hatch run wiki-render --dry-run
hatch run wiki-render
```

`wiki-render` fully regenerates managed folders under the configured `wiki_dir`,
writes `state/wiki_render_manifest.json`, and exports the Stage 2 graph to
`state/wiki_render_graph.json`.

Do not hand-edit managed generated pages. Fix the review artifact or synthesis cache, then render again.

### 8. Run Stage 2 synthesis in small batches

Plan first:

```bash
hatch run wiki-synthesis-plan --changed-only --limit 20
```

Run a controlled synthesis batch only after reviewing the plan:

```bash
hatch run wiki-synthesis-workflow --category glossary --limit 5 --yes
```

Then inspect previews in `state/synthesis_previews/`, run:

```bash
hatch run wiki-render --dry-run
hatch run wiki-render
```

Stage 2 writes cache entries under `state/synthesis/<category>/<slug>.json` in
the configured knowledge store; the renderer reads those cache entries and turns
fresh ones into human-readable synthesized wiki pages.

### 9. Check health before committing

```bash
hatch run lint:check
hatch run test:run
hatch run wiki-render --dry-run
hatch run wiki-lint
hatch run wiki-synthesis-cache-lint --json
```

For the external operating mode, also run:

```bash
hatch run wiki-ops-status --migration-plan --require-external-knowledge-root --require-external-vault-root
```

---

## Repo Structure

```
llm-wiki-karpathy/
├── AGENTS.md          # Root intent router (wiki_ops vs code_ops)
├── llm-wiki.md        # Karpathy's original idea document (optional root note)
├── article.md         # Walkthrough article (optional root note)
│
├── raw/               # Legacy/default local source path (active data is external)
│   └── .gitkeep
│
├── wiki/              # Legacy/default generated wiki path (active vault is external)
│   ├── AGENTS.md      # Generated vault contract
│   ├── sources/       # One page per reviewed source
│   ├── topics/        # Merged knowledge pages
│   ├── glossary/
│   ├── industry-trends/
│   ├── tools/
│   ├── foundation-models/
│   ├── how-to/
│   ├── signals/       # Individual evidence objects
│   ├── interview-insights/
│   ├── implementation-studies/
│   └── indexes/       # Generated routing and diagnostics indexes
│
├── src/               # Code and automation layer
│   └── AGENTS.md      # Scoped coding/tooling instructions
├── state/             # Legacy/default pipeline state path (active state is external)
├── docs/              # Architecture, status, and design notes
└── .obsidian/         # Obsidian vault UI state (local only; not in Git)
```

**Readwise Reader:** with `READWISE_TOKEN` set, run `hatch run readwise-sync`
to export archived documents tagged `processed` into the configured
`raw/readwise/` path (paired HTML + Markdown). Details are in
[`src/AGENTS.md`](src/AGENTS.md).

### How the layers work

| Layer | Folder | Who owns it | Purpose |
|-------|--------|-------------|---------|
| Raw sources | `<knowledge_root>/raw/` | You + Readwise sync | Local source exports. The pipeline reads them but does not commit them to the code repo. |
| Review artifacts | `<knowledge_root>/state/reviews/` | Human + dashboard | Canonical reviewed extraction output. |
| Render graph | `<knowledge_root>/state/wiki_render_graph.json` | `wiki-render` | Machine-readable Stage 1 graph and Stage 2 input. |
| Synthesis cache | `<knowledge_root>/state/synthesis/` | Stage 2 workflow | LLM synthesis cache keyed by evidence hash. |
| The wiki | `<vault_root>/wiki/` | Generator | Structured, interlinked Obsidian markdown projection. |
| Routing policy | `AGENTS.md` | You + AI | Routes requests by intent and enforces fail-closed handling for ambiguity. |
| Wiki rules | `wiki/AGENTS.md` | You + AI | Defines generated vault structure, provenance, and Obsidian conventions. |
| Code rules | `src/AGENTS.md` | You + AI | Defines coding standards, tests, linting, and tooling workflow. |

### Generated wiki page types

| Type | Location | What it captures |
|------|----------|-----------------|
| Source | `wiki/sources/` | One reviewed source and links to all derived pages |
| Topic | `wiki/topics/` | Merged conceptual knowledge pages |
| Glossary | `wiki/glossary/` | Terms and definitions |
| Industry trend | `wiki/industry-trends/` | Directional market or practice shifts |
| Tool | `wiki/tools/` | Named products and tools |
| Foundation model | `wiki/foundation-models/` | Named models |
| How-to | `wiki/how-to/` | Operational guidance and procedural knowledge |
| Signal | `wiki/signals/` | Individual time-based evidence observations |
| Interview insight | `wiki/interview-insights/` | Individual interview takeaways |
| Implementation study | `wiki/implementation-studies/` | Individual case studies and deployment evidence |
| Index | `wiki/indexes/` | Generated routing, diagnostics, tag hubs, and synthesis status |

---

## Customizing for Your Domain

The routing + scoped instruction files are not set in stone. Edit them to fit your needs:

- **Adjust routing behavior.** Update root `AGENTS.md` to tune intent classification and ambiguity handling.
- **Change generated vault rules.** Update `wiki/AGENTS.md` for page structure, provenance, and Obsidian conventions.
- **Change code workflow.** Update `src/AGENTS.md` for coding/testing/tooling standards.

---

## Tips

**Keep review artifacts canonical.** Generated wiki pages are projections. If a generated page is wrong, fix the review artifact or synthesis cache and rerender.

**Use small synthesis batches.** Stage 2 makes LLM calls. Plan first, run small batches, inspect previews, then render.

**Use indexes for navigation.** `wiki/indexes/` exposes tag hubs, synthesis status, source indexes, and diagnostics for both humans and LLM agents.

**Do not hand-edit managed pages.** Manual notes belong in `wiki/notes/` or another non-managed folder. Managed folders are regenerated.

**Watch cost boundaries.** `wiki-render`, `wiki-synthesis-plan`, `wiki-synthesis-cache-lint`, `wiki-synthesis-indexes`, and `wiki-synthesis-review` make no LLM calls. Real Stage 2 synthesis requires `--yes`.

---

## What Git tracks

| Tracked (commit these) | Not tracked (local only) |
|------------------------|---------------------------|
| `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, root `AGENTS.md`, `README.md` | `config/wiki_paths.toml` — machine-specific absolute paths |
| `docs/**` — architecture and status notes | `.env`, `.obsidian/**`, Python caches, `coverage.xml` |
| `config/*.example.toml` and non-secret config templates | external `llm-wiki-data/**` and `llm-wiki-vault-private/**` until a separate backup/repo policy is chosen |
| Repo-local `wiki/**` and durable `state/**` only when deliberately kept as release/development artifacts | `raw/**` — legacy/default local source path, not committed |

**Backups:** the external knowledge store is now the important backup target.
Mirror `/Users/plischke/Desktop/Private Development/llm-wiki-data` with a real
backup tool before deleting old repo-local data. The generated private vault is
recoverable from the knowledge store plus code, but it may still be worth
backing up for convenience.

**Optional root files:** `article.md` and `llm-wiki.md` are supplementary notes kept at the repo root for convenience. You may delete them, move content into `wiki/`, or stop tracking them with `git rm --cached` if you prefer a slimmer tree—no tooling depends on their paths.

**Wiki health:** run `hatch run wiki-lint` before pushing wiki changes (see [`src/AGENTS.md`](src/AGENTS.md)).

---

## Use Cases

- **Personal AI research memory** — Turn read articles into a persistent, source-grounded Obsidian wiki.
- **Agent context layer** — Give local agents stable wiki pages, indexes, and source links instead of only ad hoc retrieval.
- **Trend tracking** — Maintain industry-trend pages and tag hubs for recurring AI-market and AI-engineering themes.
- **Operational knowledge base** — Preserve how-tos, tools, implementation studies, and evidence trails for project work.
- **Second brain groundwork** — Prepare a future layer where personal notes, meeting transcripts, raw sources, and generated wiki pages can all be queried together.

---

## Credits

- Pattern by [Andrej Karpathy](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285)
- Implementation and article by [Balu Kosuri](https://github.com/balukosuri)
