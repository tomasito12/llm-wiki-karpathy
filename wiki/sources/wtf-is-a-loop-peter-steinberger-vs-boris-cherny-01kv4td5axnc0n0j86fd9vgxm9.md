---
title: WTF Is a Loop? Peter Steinberger vs. Boris Cherny
slug: wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9
category: source
tags:
- agent-orchestration
- agent-systems
- coding-agents
- orchestration-layer-growth
- runtime-systems
- software-engineering
- test-and-verification
- verification-systems
- workflow-restructuring
source_id: wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9
author: Matt Van Horn
publication: X (formerly Twitter)
published_date: '2026-06-08'
assessed_as_of: '2026-06-08'
ingested_at: '2026-06-16T15:32:50+00:00'
canonical_url: https://x.com/mvanhorn/status/2063865685558903149/?rw_tt_thread=True
content_sha256: f05f670c97a1ddde04125a7e5b0eeb62ac7a3f69dc94d008c3e400c85bf3375c
derived_topics:
- topics/agentic-coding-workflows.md
- topics/verification-loops-in-ai-workflows.md
derived_trends:
- industry-trends/workflow-restructuring-around-ai-agents.md
derived_pages:
- industry-trends/workflow-restructuring-around-ai-agents.md
- topics/agentic-coding-workflows.md
- topics/verification-loops-in-ai-workflows.md
---

# WTF Is a Loop? Peter Steinberger vs. Boris Cherny

This piece is about what people mean when they say “loops” in AI coding. The short version is: instead of typing prompts into a coding model one by one, you write a little program that keeps prompting the model, checks the result, and decides whether to continue. That matters because the human moves one level up and starts designing the control system, not each prompt. The article says the real challenge is making these loops verify their own work and stop safely. It also says the expensive part is no longer just generating code, but managing the loop itself.

## Key insights

- The important distinction is not “prompting versus not prompting,” but direct prompting versus writing a loop that prompts on your behalf.
- The newer 2026 pattern is orchestration: one loop can supervise other loops, run on a schedule, and recover from crashes with durable state.
- Verification is the central reliability problem; a loop without feedback and self-checks is a mistake factory.
- The main cost center has shifted from token generation to loop management, including iteration limits, no-progress detection, and budget caps.
- Reusable named skills matter more than raw prompting: loops compound only when they call tested skills instead of re-deriving steps each time.

## Derived knowledge pages

- [[industry-trends/workflow-restructuring-around-ai-agents]]
- [[topics/agentic-coding-workflows]]
- [[topics/verification-loops-in-ai-workflows]]

## Why it matters

The piece is useful because it compresses a lot of loop discourse into a concrete engineering model: a loop is cron plus an agentic decision step, and the interesting work is everything around that decision. It highlights a durable control pattern that already appears in Claude Code /loop, /goal, and related orchestration workflows, so it is more than a semantic argument about prompts. The most practical insight is that reliability depends on feedback, self-verification, and halting conditions; without those, autonomous coding loops can produce confident mistakes and runaway spend. That makes the article relevant to anyone evaluating whether to let agents run unattended for PRs, fixes, or multi-step coding tasks. It also correctly narrows the “magic” to the layer of reusable skills and the operating discipline around them, which is a more reusable abstraction than the hype around a single command. As of 2026-06-08, the pattern is actionable for experimentation, but the article itself suggests adopting it cautiously because the guardrails are still the real work.

## Limitations / open questions

The evidence base is mostly practitioner quotes, social posts, and the author’s own operating experience, not controlled benchmarks. Several claims rely on reported usage or anecdotes, such as GitHub contribution share, PR counts, and company budget caps, without methodological detail. The article does not quantify how often loops outperform direct prompting, how much verification reduces failure rates, or what classes of tasks benefit most. It also leaves open how to design robust self-checking when the checker model shares the same weaknesses as the generator. Security, permissioning, and data access policies are mentioned only indirectly, even though unattended loops create obvious governance and abuse risks.

## Contradictions / unverified claims

The article pushes back on the idea that loops are “just cron,” but the boundary remains partly semantic: scheduling plus a model-driven decision step is still a control loop, so the novelty depends on orchestration depth rather than the timer itself. Some of the social posts quoted in the piece are clearly hype-adjacent, and the author acknowledges that a lot of people repeating the term cannot define it. Claims about scale and adoption are suggestive but thinly evidenced, so they should be treated as discourse analysis rather than proof of a dominant production pattern. The strongest skeptical point in the article is also the most grounded: without explicit caps and verification, loops can compound costs and mistakes quickly.

## Source metadata

- Canonical URL: https://x.com/mvanhorn/status/2063865685558903149/?rw_tt_thread=True
- Raw markdown: `raw/readwise/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9.md`
- Raw HTML: `raw/readwise/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9.html`
