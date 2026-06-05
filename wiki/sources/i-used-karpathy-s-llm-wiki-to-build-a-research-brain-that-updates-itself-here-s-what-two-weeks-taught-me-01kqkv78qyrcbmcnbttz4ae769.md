---
title: I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s
  What Two Weeks Taught Me.
slug: i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
category: source
tags:
- ai-engineering
- knowledge-systems
- workflow-restructuring
source_id: i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
author: Adi Insights
publication: Towardsai
published_date: '2026-04-19'
assessed_as_of: '2026-04-19'
ingested_at: '2026-05-22T18:23:52.315022+00:00'
canonical_url: https://pub.towardsai.net/i-used-karpathys-llm-wiki-to-build-a-research-brain-that-updates-itself-ff02dda47335
content_sha256: f404b854921821e384331b6a340188de422bd1544de00c5a9689327e0aa689eb
derived_tools:
- claude-code
- obsidian
derived_topics:
- llm-assisted-knowledge-compilation
- wiki-schema-governance
derived_trends:
- llm-maintained-knowledge-bases
---

# I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.

The article is about a way to turn a pile of saved files, notes, and articles into a living knowledge base that keeps itself organized. Instead of asking an AI to answer questions from a folder of documents every time, the idea is to let the AI read the material, write pages, make links between ideas, and keep the whole collection updated. The author says this worked with a folder of research materials, the Claude Code agent, and the Obsidian note-taking app. The result was a wiki made of simple text files that could be searched and browsed like a connected map of ideas. A key part of the setup is that the original files stay untouched, so the wiki can always be rebuilt if needed. The system also checks itself for missing links, repeated ideas, and contradictions between sources. The author found that this made old reading easier to revisit and new connections easier to spot. The main takeaway is that an AI can act like a librarian for your notes, but a person still has to choose the sources and review the output. As of 2026-04-19, the idea looks practical for small personal or team knowledge collections, but the article also says it starts to hit limits as the number of sources grows.

## Key insights

- The strongest value is not retrieval at question time but maintenance at ingest time: the model does the filing, linking, and reconciliation work that people usually stop doing.
- A schema file is the control surface for making the wiki consistent; without it, the model drifts into slightly different page structures across ingests.
- Linting is treated as a first-class operation, not a cleanup task; it surfaces contradictions, orphan pages, and missing concepts before decay spreads.
- The wiki works best when raw sources stay immutable and the generated wiki is treated as an interpretation that can be rebuilt.
- Front-loaded ingest cost is the tradeoff: the system spends more tokens and time upfront so later queries can read a pre-synthesised knowledge base instead of rediscovering fragments.

## Derived knowledge pages

- [[industry-trends/llm-maintained-knowledge-bases]]
- [[tools/claude-code]]
- [[tools/obsidian]]
- [[topics/llm-assisted-knowledge-compilation]]
- [[topics/wiki-schema-governance]]

## Why it matters

The piece is practically useful because it reframes personal knowledge work as a maintenance problem that an LLM can partially automate. That is a durable design idea for anyone building research workflows, internal knowledge bases, or agent-assisted documentation systems: keep raw sources immutable, make generated summaries and links a separate layer, and use a schema to constrain how the model edits the corpus. The article also gives a concrete operating model for this pattern: ingest one source at a time, review the diffs, and run periodic lint passes for contradictions and orphan pages. Its value is higher than a generic note-taking tip because it shows the system behavior across ingest, query, and lint loops, including the tradeoff that ingest is token-heavy while query becomes cheaper once the wiki compiles. The claims are still personal and not benchmarked, so the significance is limited to a small-scale workflow as of 2026-04-19. For service automation, the closing implication is that the same maintenance pattern could help support teams keep case notes, internal procedures, and handoff knowledge synchronized, but the article does not test that use case directly; it only suggests the general maintenance loop.

## Limitations / open questions

The evidence is a single person’s two-week experience, so there are no controlled comparisons, measured accuracy rates, or long-run durability results. The article says the pattern hits a wall around 100-200 sources and may need hybrid search, multi-agent governance, or a proper retrieval-augmented generation pipeline beyond that scale. It also acknowledges epistemic drift: if the model misreads a source during ingest, that error can propagate into later pages. The article does not quantify how often linting catches mistakes, how expensive the workflow becomes at scale, or how well it performs on highly technical corpora with dense citation requirements.

## Contradictions / unverified claims

The write-up is enthusiastic, but the claims are mostly anecdotal and self-reported. The system’s success depends on disciplined human review of diffs and source selection, which means the automation reduces maintenance work rather than eliminating it. The suggestion that a wiki can become a personalized model through synthetic data and fine-tuning is explicitly future-looking and should be treated as speculative as of 2026-04-19.

## Source metadata

- Canonical URL: https://pub.towardsai.net/i-used-karpathys-llm-wiki-to-build-a-research-brain-that-updates-itself-ff02dda47335
- Raw markdown: `raw/readwise/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769.md`
- Raw HTML: `raw/readwise/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769.html`
