---
title: 'Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over'
slug: karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr
category: source
tags:
- agent-memory
- agent-systems
- ai-engineering
- cli-tool
- knowledge-systems
- local-first
- long-context-model
- proprietary-model
- reasoning-model
- workflow-automation
source_id: karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr
author: Kristopher Dunham
publication: Medium
published_date: '2026-04-21'
assessed_as_of: '2026-04-21'
ingested_at: '2026-06-06T21:58:55+00:00'
canonical_url: https://medium.com/@creativeaininja/karpathys-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-21c5146a7b53
content_sha256: 86b040241603558dc57ae280dff5743e4bfc7eaff8263f45601fb0e90c841cc7
derived_how_to:
- how-to/agent-maintained-knowledge-bases.md
derived_models:
- foundation-models/claude-opus-4-7.md
derived_tools:
- tools/claude-code.md
derived_topics:
- topics/llm-assisted-knowledge-compilation.md
derived_trends:
- industry-trends/knowledge-systems-shift-toward-compilation-over-retrieval.md
derived_pages:
- foundation-models/claude-opus-4-7.md
- how-to/agent-maintained-knowledge-bases.md
- industry-trends/knowledge-systems-shift-toward-compilation-over-retrieval.md
- tools/claude-code.md
- topics/llm-assisted-knowledge-compilation.md
---

# Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over

This piece is about a way to make AI remember your work instead of restarting every time you ask a question. The idea is to have the model turn raw notes and documents into a structured wiki, then answer future questions from that compiled wiki. That way, the hard thinking happens once during ingestion, not again at every query. The article also explains a simple folder structure, a schema file, and a maintenance loop for checking links and contradictions. It is basically a knowledge-compilation workflow for people with lots of notes, papers, or research. The main promise is accumulated understanding; the main warning is that bad ingestions can contaminate the wiki if you do not review provenance and lint regularly.

## Key insights

- The central design shift is from query-time retrieval to ingestion-time compilation, which preserves synthesized knowledge instead of redoing it each session.
- Treating raw sources as immutable and the wiki as the compiled output gives the system a clean audit boundary and a practical rollback story.
- A schema file such as CLAUDE.md is the real control surface; changing generated pages directly is discouraged because it breaks the model's mapping.
- The optional --save path makes the wiki cumulative by promoting useful answers from ad hoc queries into durable pages.
- The biggest operational risk is not hallucinated answers but hallucinated knowledge being written into the wiki and reused later without linting or provenance checks.

## Derived knowledge pages

- [[foundation-models/claude-opus-4-7]]
- [[how-to/agent-maintained-knowledge-bases]]
- [[industry-trends/knowledge-systems-shift-toward-compilation-over-retrieval]]
- [[tools/claude-code]]
- [[topics/llm-assisted-knowledge-compilation]]

## Why it matters

The article is useful because it turns a vague “AI memory” desire into a concrete operating model: compile once, query many times, and keep provenance attached to every claim. For AI engineers, the important idea is that knowledge work can be structured like software compilation, with a schema file, immutable sources, generated artifacts, and explicit lint passes. That makes the pattern more durable than ad hoc chat logs or pure vector search when the goal is accumulated understanding over weeks or months. The article is also candid about tradeoffs: ingestion is token-heavy because the model rereads existing pages and rewrites connected pages, and the approach depends on discipline around review and rollback. Its strongest contribution is not a new algorithm but a reusable workflow for keeping synthesized knowledge queryable. The evidence is still mostly expert synthesis and community enthusiasm rather than benchmarked evaluation, so the practical value is clearer than the comparative proof. Actionable as of 2026-04-21 for personal or team-scale knowledge bases, with adoption best treated as an experiment rather than a settled standard.

## Limitations / open questions

The article does not provide benchmark comparisons against conventional RAG, notebook workflows, or alternative memory systems, so the claimed advantage remains mostly architectural and anecdotal. It also leaves open how to evaluate whether a compiled wiki is accurate enough to trust, beyond manual linting and provenance inspection. The token and cost discussion is informative but not quantified with real workload measurements, so the economics are approximate. Security, privacy, and access control concerns are barely addressed, even though the pattern assumes the model can read and rewrite a potentially sensitive knowledge store. The piece says the pattern is for personal and team-scale use, but it does not define the boundary precisely or explain migration paths for larger corpora.

## Contradictions / unverified claims

The article leans heavily on the compiler analogy, but that analogy can hide how much interpretation and lossiness still happens when an LLM rewrites source material into pages. It also assumes that structured note-taking by the model is an acceptable substitute for human synthesis, which is exactly the part critics worry about because the act of filing is itself a learning step. The claim that 1M-token context makes the pattern less necessary is plausible within the article's framing, but the piece still argues for compilation because retrieval does not preserve accumulated structure. That is a reasonable tension, but it is not resolved with empirical evidence. The enthusiasm around the Karpathy gist and community tools is interesting, yet the article does not show whether the pattern outperforms simpler systems in controlled use.

## Source metadata

- Canonical URL: https://medium.com/@creativeaininja/karpathys-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-21c5146a7b53
- Raw markdown: `raw/readwise/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr.md`
- Raw HTML: `raw/readwise/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr.html`
