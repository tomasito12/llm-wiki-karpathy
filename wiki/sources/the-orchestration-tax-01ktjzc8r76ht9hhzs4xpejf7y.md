---
title: The Orchestration Tax
slug: the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
category: source
tags:
- agent-orchestration
- agent-systems
- human-ai-workflows
- inference
- orchestration
- software-engineering
- tool-use
- workflow-restructuring
source_id: the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
author: Addy Osmani
publication: X (formerly Twitter)
published_date: '2026-05-28'
assessed_as_of: '2026-05-28'
ingested_at: '2026-06-17T15:54:02.846021+00:00'
canonical_url: https://x.com/addyosmani/status/2059844244907696186/?rw_tt_thread=True
content_sha256: 564c021f3c26d82b4d89ab858e6ea5908f0a83317f1c67a3df9e7899541ac368
derived_glossary:
- glossary/amdahl-s-law.md
- glossary/harness.md
derived_topics:
- topics/cognitive-debt-in-ai-workflows.md
derived_trends:
- industry-trends/ai-workflows-shift-toward-verification-loops.md
derived_pages:
- glossary/amdahl-s-law.md
- glossary/harness.md
- industry-trends/ai-workflows-shift-toward-verification-loops.md
- topics/cognitive-debt-in-ai-workflows.md
---

# The Orchestration Tax

This piece says the hard part of using lots of AI agents is not launching them. It is keeping up with their output. One person still has to read, judge, and merge the results, and that creates a bottleneck. The author calls this the “orchestration tax.” He uses computer systems ideas like single-threaded execution and bottlenecks to explain why more agents can make you feel productive without making you more productive. The practical advice is to limit agents to the amount you can really review, batch the checks, and save your best attention for the decisions that only a human can make.

## Key insights

- The real limit in agent-heavy workflows is the human review loop, not agent creation.
- More parallel agents can increase context-switching and shallow reviews without increasing shipped output.
- Treat attention as a serial production resource and size agent concurrency to review capacity, not to UI convenience.
- Split work into low-judgment delegation and high-judgment tasks; only the former benefits cleanly from background agents.
- Offload verifiable substeps to agents with tests or screenshots so human attention goes only to the irreducible judgment calls.

## Derived knowledge pages

- [[glossary/amdahl-s-law]]
- [[glossary/harness]]
- [[industry-trends/ai-workflows-shift-toward-verification-loops]]
- [[topics/cognitive-debt-in-ai-workflows]]

## Why it matters

The piece is useful because it reframes agentic development as a systems-design problem with a human bottleneck, not as a matter of working harder or spawning more copilots. That framing is durable as of 2026-05-28 because it is grounded in a concrete workflow failure mode the author describes from practice: multiple agents can increase surface activity while the review step stays single-threaded. The concurrency analogies are not research results, but they are operationally helpful because they force a review of where work is actually serial. The most actionable guidance is to match agent count to review throughput, batch checks to reduce context switching, and reserve human effort for cases where judgment is the work. The article also points to a real quality risk: if orchestration overhead is ignored, teams may accept code they have not really understood and accumulate cognitive debt. Its value is strongest for people already using multiple agents in coding workflows and trying to avoid a false sense of productivity. For service automation, support, voice, meetings, or back-office workflows, the implication is only indirect: any system that adds AI workers without respecting the human review bottleneck will feel busier than it is productive, but the article does not analyze those domains in depth. Actionable as of 2026-05-28; the guidance is practical rather than speculative, but it remains an opinion essay without benchmarks.

## Limitations / open questions

The argument is persuasive but anecdotal; it relies on the author’s experience and concurrency metaphors rather than measurements of throughput, defect rates, or review latency. It does not quantify where the optimal agent count lands for different tasks, teams, or levels of reviewer expertise. The piece assumes a human remains the final gate for meaningful judgment, which may not hold for all workflows or for future automation levels. It also does not discuss failure modes like security review, auditability, or how to structure multi-agent systems when no single reviewer can understand all output. The recommendation to batch reviews or give agents a long leash may improve efficiency in some settings, but the article does not show tradeoffs with urgency, deadline pressure, or risk-sensitive work.

## Contradictions / unverified claims

The essay’s main tension is that it borrows hard systems language while offering no hard data; the analogies are useful, but they can overstate precision. The claim that the right agent count is a “low single digit” for most people is presented as experience, not evidence. There is also an implicit assumption that review quality scales linearly with uninterrupted attention, which may not always be true. Still, the core warning is coherent: orchestration can become the hidden cost of agentic work, and feeling busy is not proof of productivity.

## Source metadata

- Canonical URL: https://x.com/addyosmani/status/2059844244907696186/?rw_tt_thread=True
- Raw markdown: `raw/readwise/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y.md`
- Raw HTML: `raw/readwise/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y.html`
