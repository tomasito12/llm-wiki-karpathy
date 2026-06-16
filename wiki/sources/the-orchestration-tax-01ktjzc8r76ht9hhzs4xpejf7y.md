---
title: The Orchestration Tax
slug: the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
category: source
tags:
- agent-orchestration
- ai-assisted-development
- ai-engineering
- coding-agents
- human-ai-collaboration
- human-ai-workflows
- organizational-design
- software-engineering
- workflow-design
- workflow-restructuring
source_id: the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
author: Addy Osmani
publication: X (formerly Twitter)
published_date: '2026-05-28'
assessed_as_of: '2026-05-28'
ingested_at: '2026-06-16T01:25:20+00:00'
canonical_url: https://x.com/addyosmani/status/2059844244907696186/?rw_tt_thread=True
content_sha256: 564c021f3c26d82b4d89ab858e6ea5908f0a83317f1c67a3df9e7899541ac368
derived_topics:
- topics/agentic-coding-workflows.md
- topics/cognitive-debt-in-ai-workflows.md
derived_trends:
- industry-trends/agentic-coding-shifts-toward-higher-supervision-costs.md
derived_pages:
- industry-trends/agentic-coding-shifts-toward-higher-supervision-costs.md
- topics/agentic-coding-workflows.md
- topics/cognitive-debt-in-ai-workflows.md
---

# The Orchestration Tax

This piece says that agent tools can make you feel much busier than you really are. You can start many agents, but you still have to review, judge, and merge their work yourself. That review step is the slow part, so it becomes the bottleneck. The author calls this the "orchestration tax." The basic fix is to treat your attention like a scarce system resource: keep agent count low enough that you can review well, batch your checks, and use agents to verify simple things while you focus on the hard decisions.

## Key insights

- Starting more agents does not create more human attention; it only increases the amount of work queued for review.
- The true bottleneck in agentic workflows is often judgment and integration, not generation.
- Busy dashboards can hide low throughput if the serial review step cannot keep up.
- Batching reviews and reducing context switches can materially lower the cognitive cost of orchestrating agents.
- Use agents to prove the boring 80% themselves, so human attention is spent on the 20% that requires judgment.

## Derived knowledge pages

- [[industry-trends/agentic-coding-shifts-toward-higher-supervision-costs]]
- [[topics/agentic-coding-workflows]]
- [[topics/cognitive-debt-in-ai-workflows]]

## Why it matters

The article is useful because it reframes agentic coding as a systems-design problem instead of a productivity contest. That is a durable mental model for AI engineering: the limiting resource is often not model output, but the human process that validates, merges, and understands it. The concurrency analogies are concrete and operationally relevant as of 2026-05-28 because they translate well into everyday workflow choices: cap parallelism to review capacity, separate delegation-friendly tasks from judgment-heavy tasks, and use backpressure instead of letting queues expand unchecked. The piece is strongest where it describes the failure mode of shallow reviews and cognitive surrender, because those are realistic risks when agent volume rises faster than human inspection time. It is weaker as evidence for any broad productivity claim, since it is mostly expert opinion and personal experience rather than measurement. Still, the guidance is practical enough to adopt as a working heuristic: treat attention as the scarce serial resource and design around it. For conversational AI, chatbots, voicebots, and service automation work, the same logic applies to handoff quality, review gates, and avoiding over-automation of complex judgment steps.

## Limitations / open questions

The piece does not provide benchmarks, experiments, or case studies showing how much throughput changes under different agent counts or review patterns. The advice is directionally strong but leaves open how to set the right review threshold for different task types, team sizes, or codebase complexity. It also does not quantify the cost of batching versus immediate feedback, or discuss how tooling, pair review, or automated checks could change the serial bottleneck. The concurrency metaphors are helpful, but they can oversimplify workflows where humans and agents have different error modes or where partial automation is safe. There is also no discussion of security, privacy, or organizational controls around agent-generated code.

## Contradictions / unverified claims

The argument is persuasive, but it is still a conceptual essay, not evidence that agentic development is broadly bottlenecked exactly this way in every team. The claim that the right number of parallel agents is usually a low single digit is presented as experience-based guidance, not a general result. The GIL and Amdahl’s Law analogies are useful, but they can encourage overconfidence in the neatness of the mapping; human judgment is less deterministic than CPU scheduling. The warning about cognitive surrender is plausible, though the article does not show how often it happens in practice or how to measure it reliably.

## Source metadata

- Canonical URL: https://x.com/addyosmani/status/2059844244907696186/?rw_tt_thread=True
- Raw markdown: `raw/readwise/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y.md`
- Raw HTML: `raw/readwise/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y.html`
