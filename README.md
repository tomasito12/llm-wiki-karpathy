# LLM Wiki (Karpathy Pattern)

A self-maintaining personal knowledge base powered by LLMs, based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285).

Instead of re-searching raw documents on every question (like RAG), the LLM **reads your sources once and builds a persistent, interlinked wiki** that compounds over time. The more sources you feed it, the richer and more connected it gets.

---

## Prerequisites

- [Cursor](https://cursor.sh/) (or any LLM-powered editor that reads a schema file)
- [Obsidian](https://obsidian.md/) (free) for browsing the wiki in real time

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/balukosuri/llm-wiki-karpathy.git
cd llm-wiki-karpathy
```

### 2. Open the project in Cursor

Cursor reads `AGENTS.md` as a root router. Detailed behavior is scoped:

- `wiki/AGENTS.md` for wiki ingest/query/lint workflows
- `src/AGENTS.md` for code/tooling development workflows

If you use a different AI agent, load root `AGENTS.md` first, then the scoped file for your current task.

### 3. Open the same folder in Obsidian

Open the project directory as an Obsidian vault. You'll have two windows side by side — Cursor on the left where you talk to the AI, Obsidian on the right where you browse the wiki as pages appear.

### 4. Drop a source into `raw/`

Any document works:

- Product specs, design docs, or PRDs
- Meeting transcripts
- Web articles (use [Obsidian Web Clipper](https://obsidian.md/clipper) to save pages as markdown)
- Style guides
- PDFs, reports, email threads saved as text
- Competitor documentation

### 5. Say "ingest"

Type this in Cursor:

> ingest raw/my-document.pdf

The AI will:

1. Read the document
2. Discuss key takeaways with you
3. Create a source summary page in `wiki/sources/`
4. Create new pages for any products, features, personas, or concepts it finds
5. Update the glossary with new terms
6. Update the index with all new pages
7. Update the overview if the big picture shifted
8. Log everything in `wiki/log.md`

A single source can touch 5-15 wiki pages. Watch them appear in Obsidian in real time.

### 6. Ask questions

> What are the main risks identified across all my sources?

The AI reads the wiki, synthesizes an answer with citations, and asks: *"Should I save this as a wiki page?"* If you say yes, the answer becomes a permanent analysis page. Your questions make the knowledge base richer over time.

### 7. Lint the wiki

Every 10 ingests or so, run a health check:

> lint the wiki

The AI checks for contradictions between pages, stale claims, orphan pages with no links, missing cross-references, and inconsistent terminology. It reports what it found and asks which fixes to apply.

---

## Repo Structure

```
llm-wiki-karpathy/
├── AGENTS.md          # Root intent router (wiki_ops vs code_ops)
├── llm-wiki.md        # Karpathy's original idea document (optional root note)
├── article.md         # Walkthrough article (optional root note)
│
├── raw/               # Your source documents (local only; not in Git)
│   └── .gitkeep
│
├── wiki/              # Knowledge base (versioned in Git)
│   ├── AGENTS.md      # Wiki contracts and ingest rules
│   ├── index.md       # Master catalog
│   ├── log.md         # Activity log
│   ├── sources/       # One page per ingested source
│   └── …              # tools/, foundation-models/, questions/, glossary/, …
│
├── src/               # Code and automation layer
│   └── AGENTS.md      # Scoped coding/tooling instructions
├── state/             # Pipeline state (see “What Git tracks” below)
├── docs/              # Supporting docs (routing rubric, etc.)
└── .obsidian/         # Obsidian vault UI state (local only; not in Git)
```

**Readwise Reader:** with `READWISE_TOKEN` set, run `hatch run readwise-sync` to export archived documents tagged `processed` into `raw/readwise/` (paired HTML + Markdown). Details are in [`src/AGENTS.md`](src/AGENTS.md).

### How the layers work

| Layer | Folder | Who owns it | Purpose |
|-------|--------|-------------|---------|
| Raw sources | `raw/` | You | Immutable source documents. The AI reads from here but never modifies anything. |
| The wiki | `wiki/` | The AI | Structured, interlinked markdown pages. The AI creates, updates, and maintains everything here. |
| Routing policy | `AGENTS.md` | You + AI | Routes requests by intent and enforces fail-closed handling for ambiguity. |
| Wiki rules | `wiki/AGENTS.md` | You + AI | Defines wiki entity types, ingest/query/lint workflows, and cross-linking standards. |
| Code rules | `src/AGENTS.md` | You + AI | Defines coding standards, tests, linting, and tooling workflow. |

### Wiki ingest paths

Ingest is **dual-path** at the top level, with **Path A** splitting into two tracks (see `wiki/AGENTS.md` and `wiki/style/ingest-templates.md`):

- **Path A — Questions (deep article):** structured source summary (driving questions, author’s answer, why it matters, **implications for service-call automation**), then file evidence under canonical **`wiki/questions/q-*.md`** pages; read `wiki/questions/question-catalog.md` first to avoid duplicate questions.
- **Path A — Tools (deep article):** same source minimum, but **primary filing** is **`wiki/ai-tools/<slug>.md`** — one persistent page **per named product** (listicles: always one file per name, even if thin at first). Read `wiki/ai-tools/tool-catalog.md` first for dedupe; each ingest appends **`### Update YYYY-MM-DD`** on the tool pages. Question pages are **optional** unless the source also establishes a standalone methodology question.
- **Path B — Radar digest** (e.g. Latent Space, The Sequence, Last Week in AI): merge into **`wiki/ai-news/by-date/YYYY-MM-DD.md`** by publication date; optional **Monday** weekly rollup in `wiki/ai-news/weekly/`.

### Wiki page types

The AI creates different page types depending on what it finds in your sources (see `wiki/AGENTS.md` for the full taxonomy):

| Type | Location | What it captures |
|------|----------|-----------------|
| Source | `wiki/sources/` | Summary of a raw document — key facts, quotes, metadata |
| Question | `wiki/questions/` (`q-*.md`) | One canonical driving question; dated Evidence + citations |
| Questions catalog | `wiki/questions/question-catalog.md` | Table of all questions for dedupe before Path A — Questions ingest |
| Tools catalog | `wiki/ai-tools/tool-catalog.md` | Table of per-product tool pages for dedupe before Path A — Tools ingest |
| Knowledge management | `wiki/knowledge-management/` | RAG, knowledge graphs, LLM-wiki / organizational KM |
| Personal knowledge | `wiki/personal-knowledge/` | PKM, AI-assisted workflows, overlap with KM |
| AI tool | `wiki/ai-tools/<slug>.md` | One page per named product; grows with dated **Update** blocks (see `tool-catalog.md`) |
| AI news | `wiki/ai-news/` | Releases, model updates, industry radar |
| Local AI | `wiki/local-ai/` | Self-hosting, local inference, privacy vs cloud |
| Conversational AI | `wiki/conversational-ai/` | Chat/voice and **service automation** (core domain) |
| Prompting | `wiki/prompting/` | Context and prompt patterns for UX and task quality |
| Models | `wiki/models/` | Open vs proprietary landscape, hosting realism |
| AI engineering | `wiki/ai-engineering/` | Practices, spec-driven delivery, engineering trends |
| Governance & security | `wiki/governance-security/` | Governance and AI security topics |
| Evaluation | `wiki/evaluate/` | Evaluation methods and checklists (cross-topic) |
| Transcript | `wiki/transcripts/` | Meeting transcripts, decisions, and timelines |
| Style | `wiki/style/` | Process conventions and wiki maintenance checklists |
| Analysis | `wiki/analyses/` | Multi-topic synthesis — comparison, gap analysis, outline |

---

## Customizing for Your Domain

The routing + scoped instruction files are not set in stone. Edit them to fit your needs:

- **Adjust routing behavior.** Update root `AGENTS.md` to tune intent classification and ambiguity handling.
- **Change wiki workflow.** Update `wiki/AGENTS.md` for ingest/query/lint behavior.
- **Change code workflow.** Update `src/AGENTS.md` for coding/testing/tooling standards.

---

## Tips

**Ingest one source at a time.** You can batch-ingest, but you lose the chance to guide the AI. Stay involved — read the summaries, tell it what to emphasize, ask follow-ups during ingestion.

**Save your best questions.** When you ask something and get a useful answer, tell the AI to save it as an analysis page. Your explorations compound in the wiki instead of disappearing into chat history.

**Use graph view often.** Press `Cmd+G` in Obsidian. The visual map shows which pages are hubs, which are orphans, and how everything connects.

**Check the glossary before writing.** Open `wiki/glossary.md` before you write anything. It has the right terms, the wrong terms, and the reasons behind each choice.

**Don't write wiki pages yourself.** Your job is to find good sources and ask good questions. The AI handles the summarizing, cross-referencing, filing, and bookkeeping.

---

## What Git tracks

| Tracked (commit these) | Not tracked (local only) |
|------------------------|---------------------------|
| `wiki/**` — the knowledge base and `wiki/AGENTS.md` contracts | `raw/**` — Readwise exports and other large sources |
| `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, root `AGENTS.md`, `README.md` | `state/readwise_library.json` — export index (rebuild with `hatch run readwise-rebuild-index`) |
| `state/ingest_manifest.json` — ingest audit log | `.env`, `.obsidian/**`, Python caches, `coverage.xml` |

**Backups:** mirror `raw/` (and optionally your local `state/readwise_library.json`) via cloud drive or NAS; the wiki and manifest are recoverable from Git history.

**Optional root files:** `article.md` and `llm-wiki.md` are supplementary notes kept at the repo root for convenience. You may delete them, move content into `wiki/`, or stop tracking them with `git rm --cached` if you prefer a slimmer tree—no tooling depends on their paths.

**Wiki health:** run `hatch run wiki-lint` before pushing wiki changes (see [`src/AGENTS.md`](src/AGENTS.md)).

---

## Use Cases

- **Technical writers** — Ingest specs, transcripts, and competitor docs. Get a living glossary, persona pages, and structured outlines without writing them yourself.
- **Researchers** — Feed it papers, articles, and reports over weeks. End up with a wiki that has an evolving thesis and all the connections already made.
- **Product managers** — Ingest PRDs, customer interviews, competitive analyses, and retros. The wiki maintains the big picture.
- **Students** — Ingest textbook chapters one at a time. The AI builds concept pages, links them together, and flags connections between chapters.
- **Anyone accumulating knowledge** — Trip planning, hobby research, health tracking, course notes, book clubs. Anything where information comes from multiple sources and you want it organized.

---

## Credits

- Pattern by [Andrej Karpathy](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285)
- Implementation and article by [Balu Kosuri](https://github.com/balukosuri)
