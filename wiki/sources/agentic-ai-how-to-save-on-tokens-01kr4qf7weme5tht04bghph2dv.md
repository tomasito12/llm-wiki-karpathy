---
title: 'Agentic AI: How to Save on Tokens'
slug: agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv
category: source
tags:
- agent-evals
- agent-memory
- agent-orchestration
- ai-economics
- ai-engineering
- context-engineering
- developer-tooling
- inference-systems
- long-running-agents
- model-behavior
- orchestration
- prompt-engineering
- retrieval-systems
- runtime-systems
source_id: agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv
author: Ida Silfverskiöld
publication: Medium
published_date: '2026-05-08'
assessed_as_of: '2026-05-08'
ingested_at: '2026-05-26T21:53:23.257710+00:00'
canonical_url: https://medium.com/data-science-collective/agentic-ai-how-to-save-on-tokens-9a1571ac6c85
content_sha256: b5998d0f3c9394aa0df3d355271c19c543a7b1fcfdf8bb9283896bb9b0a1507f
derived_how_to:
- how-to/context-compaction.md
- how-to/lazy-loading-tools.md
- how-to/model-routing-and-cascades.md
- how-to/prompt-caching.md
- how-to/semantic-caching.md
derived_pages:
- how-to/context-compaction.md
- how-to/lazy-loading-tools.md
- how-to/model-routing-and-cascades.md
- how-to/prompt-caching.md
- how-to/semantic-caching.md
---

# Agentic AI: How to Save on Tokens

This article is about ways to make AI agents cheaper to run. It says that an agent can get expensive because it keeps sending the same long instructions, tool descriptions, and extra conversation history back to the model again and again. One idea is to save work by reusing earlier processing when the prompt starts the same way, which is called prompt caching. Another idea is to reuse answers when two questions mean almost the same thing, which is called semantic caching, but that is riskier because the system has to decide when two requests are close enough. The article also suggests not loading every tool or every detail all at once, because that makes the prompt bigger and harder to cache. Instead, the agent can search for tools or load them only when needed. It then looks at sending easy tasks to cheaper models, or letting a small model answer first and only escalating if the answer looks weak. Finally, it argues that agents should keep their working memory clean by dropping logs, duplicate notes, and other clutter. The main message is that token savings are possible, but each trick has trade-offs and needs careful testing.

## Key insights

- Prompt caching is the quickest win when the front of the prompt is stable and long enough to match exactly.
- Semantic caching is only attractive when requests repeat in near-identical form; it needs tight metadata, TTL, and scoping rules to avoid bad reuse.
- Lazy-loading tools and tool search help both cost and performance when tool inventories become large enough that upfront context is noisy.
- Routing and cheap-first cascades can reduce spend, but the article treats quality risk and router accuracy as the main limiting factors.
- Context compaction can save tokens without changing model choice, which makes it less risky than semantic reuse or routing if the state pipeline is designed well.

## Derived knowledge pages

- [[how-to/context-compaction]]
- [[how-to/lazy-loading-tools]]
- [[how-to/model-routing-and-cascades]]
- [[how-to/prompt-caching]]
- [[how-to/semantic-caching]]

## Why it matters

The piece is useful because it compresses several cost-control techniques for agent builders into one practical checklist, rather than treating token spend as a single optimization problem. Its strongest contribution is the distinction between reusing tokens exactly, reusing answers semantically, and reducing the amount of context you send in the first place. That separation matters operationally because each lever has different failure modes: exact caching depends on prompt stability, semantic caching depends on similarity and staleness control, and routing depends on judging task difficulty without degrading answer quality. The article also gives implementation-oriented details such as exact-prefix matching, cache TTL windows, deferred tool loading, and cheap-first escalation, which makes it more actionable than generic advice about “use smaller prompts.” The benchmark-style numbers and vendor claims are directionally useful, but several are tied to narrow examples and may not generalize. The article is still valuable as a design map for where token waste tends to accumulate in agent systems as of 2026-05-08, but it is better read as a set of candidate optimizations to test than as a validated recipe. For voice, meetings, support, or back-office agents, the same patterns could reduce repeated prompt and tool overhead, but the article itself does not deeply analyze those domains, so that implication should be treated as plausible rather than established.

## Limitations / open questions

Several savings claims rely on illustrative assumptions, vendor-reported figures, or narrow benchmarks rather than comparable end-to-end evaluations. Prompt caching requires exact prefix matches, so even minor prompt drift can erase the benefit, and the article does not quantify how often real production prompts stay stable enough. Semantic caching raises unresolved questions about threshold choice, user and workspace isolation, cache invalidation, and what to do when a reused answer is wrong. Routing and cascades are presented as promising, but the article notes that learned routers sometimes barely beat simple heuristics, and it does not provide a full apples-to-apples benchmark across tasks. The context-compaction discussion is directionally strong but leaves open how to preserve the right architectural and debugging state while removing noise. The piece also does not deeply address privacy, auditability, or failure recovery when cached or delegated outputs are reused.

## Contradictions / unverified claims

The article is candid that many of the techniques trade cost for complexity, but some of the savings examples still lean on optimistic or narrowly framed numbers. The claim that prompt caching can turn a 10,000-token system prompt into a five-second saving per call is a useful illustration, not a universal result, because prefill throughput and cache hit rates vary by setup. The semantic-caching section is especially sensitive to overclaiming: it can work for repetitive Q and A, but the article itself acknowledges that it quickly becomes a project once scoping, staleness, and wrong-answer risk are considered. Routing and subagents are presented as economical, yet the source also suggests that simple heuristics can be hard to beat, which tempers any enthusiasm for “smart” routers. Overall, the article’s skepticism is adequate, and its main weakness is that many proposals are more operationally plausible than rigorously proven across diverse workloads.

## Source metadata

- Canonical URL: https://medium.com/data-science-collective/agentic-ai-how-to-save-on-tokens-9a1571ac6c85
- Raw markdown: `raw/readwise/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv.md`
- Raw HTML: `raw/readwise/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv.html`
