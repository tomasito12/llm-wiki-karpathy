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
├── llm-wiki.md        # Karpathy's original idea document
├── article.md         # Walkthrough article explaining this project
│
├── raw/               # Your source documents (AI reads, never writes)
│   └── .gitkeep
│
├── wiki/              # AI-generated knowledge base (AI owns this layer)
│   ├── index.md       # Master catalog — the AI reads this first on every query
│   ├── overview.md    # Big-picture synthesis (evolves with each ingest)
│   ├── glossary.md    # Terms, definitions, and style conventions
│   └── log.md         # Chronological record of all activity
│
├── src/               # Code and automation layer
│   └── AGENTS.md      # Scoped coding/tooling instructions
├── state/             # Local pipeline state (e.g. Readwise export index)
├── docs/              # Supporting docs (routing rubric, etc.)
└── .obsidian/         # Pre-configured Obsidian vault settings
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

### Wiki page types

The AI creates different page types depending on what it finds in your sources:

| Type | Location | What it captures |
|------|----------|-----------------|
| Source | `wiki/sources/` | Summary of a raw document — key facts, quotes, metadata |
| Chatbot | `wiki/bot-design/` | Chatbot/voicebot design pattern and implementation concepts |
| Evaluation | `wiki/evaluate/` | Evaluation methods, quality checklists, and validation guidance |
| Transcript | `wiki/transcripts/` | Meeting transcripts, decisions, and timelines |
| AI-Release | `wiki/ai-releases/` | Model/tool release notes and impact interpretation |
| Industry News | `wiki/industry-news/` | External AI usage patterns, trends, and pitfalls |
| Style | `wiki/style/` | Process conventions and wiki maintenance checklists |
| Analysis | `wiki/analyses/` | A synthesized output — comparison table, gap analysis, outline |

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

## Code-Only Git Policy

This repository tracks code and operational configuration only. Treat `raw/` and `wiki/` as local data stores.

- `raw/` and `wiki/` are ignored by Git and should be backed up separately (cloud drive, NAS, or object storage snapshots).
- Commit files such as `AGENTS.md`, `.gitignore`, scripts, and project automation/config.
- Do not commit source data dumps, generated wiki content, or local workspace state.

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
