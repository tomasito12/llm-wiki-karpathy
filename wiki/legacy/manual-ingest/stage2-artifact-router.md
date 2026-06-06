---
title: Stage 2 — Artifact router (foundation model vs tool vs MCP)
type: style
created: 2026-05-06
updated: 2026-05-06
sources: []
tags: [ingest, classifier, stage-2]
---

Run **after** Stage 1 (`wiki/stage1-classifier.md`) routes an ingest to **tools-overview** (or when a radar bullet names a specific model you choose to capture).

Stage 1 picks the **article archetype**. Stage 2 assigns **each named product** in the source to exactly one wiki contract. **Do not** paste Stage 2 notes into final `wiki/sources/*.md` pages—use `wiki/log.md` or scratch only.

## Routing table

For **each** named artifact, pick one route:

| Route | Examples | Wiki target |
|-------|----------|-------------|
| **Foundation model** | Kimi K2.5, DeepSeek V4, Mercury 2, “open-weights LLM family,” API model line | `wiki/foundation-models/<slug>.md` + row in `wiki/foundation-models/index.md`; use foundation-model section contract in `wiki/AGENTS.md` |
| **App / platform** | Lovable, Granola, Gumloop, Wispr Flow, Pomelli | `wiki/tools/<category>/<slug>.md` + category gate (`wiki/tools/index.md`, relevant category index) |
| **MCP server** | Firecrawl MCP, GitHub MCP | `wiki/tools/mcp-servers/<slug>.md` (or existing MCP category) |
| **Ambiguous** | “Kimi” as website + model | Prefer **foundation model** if the paragraph centers **model capability / benchmarks / API**; **tool** if it centers Changelog UX or installable product |

## Heuristics

**Signals for foundation model:** marketed as model / checkpoint / API model name; weights (open or closed); benchmarks vs other models; context length / MoE / diffusion LM; vendor reads as a **lab** and the artifact is **inference**.

**Signals for tool/app:** installable app, SaaS dashboard, workflow canvas, integration as main value; model mention is incidental.

## Mixed listicles (source page body)

Do not mix `[[foundation-models/...]]` wikilinks into `## Apps and platforms covered` or `[[tools/...]]` into `## Foundation models covered`. Use the split coverage sections defined in `wiki/AGENTS.md` contract **6)**.

## PATH A (thesis-first) touches a model name

Default: **questions + source** only; **no** foundation-model page if the model is illustrative.

If the source adds **material new facts** (release date, benchmark, pricing) about a named model: append one `### YYYY-MM-DD` block under that page’s `## Timeline`, add `[[sources/...]]` to `## Sources`, and optionally one line in `wiki/log.md`.
