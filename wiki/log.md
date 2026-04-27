# Wiki Log

Append-only chronological record of all activity: ingests, queries, and lint passes.

To view recent activity: `grep "^## \[" log.md | tail -10`

---

## [2026-04-07] init | Wiki created

Wiki initialized for a technical writer's personal knowledge base.

Structure created:
- `raw/` — source documents folder
- `wiki/` — LLM-maintained knowledge base
- `wiki/sources/` — per-source summary pages
- `AGENTS.md` — schema and operating instructions

Core pages created:
- `wiki/index.md`
- `wiki/log.md`
- `wiki/overview.md`
- `wiki/glossary.md`

Next step: Drop your first source into `raw/` and say **"ingest [filename]"**.

Migration note:
- `CLAUDE.md` was renamed to `AGENTS.md`; `AGENTS.md` is now the canonical operating manual reference.

## [2026-04-25] ingest | How I Stopped My AI Chatbot From Making Up Answers

Pages created:
- `wiki/sources/how-i-stopped-my-ai-chatbot-from-making-up-answers.md`
- `wiki/bot-design/rag-reliability-for-support-chatbots.md`
- `wiki/evaluate/retrieval-quality-evaluation-checklist.md`

Pages updated:
- `wiki/glossary.md`
- `wiki/index.md`
- `wiki/overview.md`
- `wiki/log.md`

Key additions:
- First source ingest completed with source summary and reliability-focused extraction
- Introduced canonical terminology for RAG reliability work
- Added chatbot design pattern page and retrieval evaluation checklist page
