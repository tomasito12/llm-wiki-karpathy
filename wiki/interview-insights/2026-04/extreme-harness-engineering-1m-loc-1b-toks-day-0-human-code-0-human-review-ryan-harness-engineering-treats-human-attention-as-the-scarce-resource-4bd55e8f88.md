---
title: Harness engineering treats human attention as the scarce resource
slug: harness-engineering-treats-human-attention-as-the-scarce-resource
category: insight
tags:
- ai-engineering
- coding-agents
- workflow-design
source_id: extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy
source_title: 'Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0%
  human review — Ryan Lopopolo, OpenAI Frontier & Symphony'
source_date: '2026-04-07'
month: 2026-04
evidence_count: 8
evidence_set_hash: 66d90a4f2fd9a123
insight_title: Harness engineering treats human attention as the scarce resource
insight_type: topic
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Harness engineering treats human attention as the scarce resource

## Interview Insight

### Summary

Ryan frames the main bottleneck in agentic software development as synchronous human attention, not token supply. The workflow is therefore designed so agents can build, review, and merge work with humans only stepping in to change structure or handle the hardest cases. That shifts the unit of optimization from writing code faster to designing a system that keeps the model productive end to end.

### Why It Matters

As of 2026-04-07, this is a durable operating model for teams already using coding agents: the biggest gains come from redesigning the workflow around what humans should stop doing, not from prompting harder. The source is explicit that the value is in removing unnecessary human touchpoints, especially in the PR and terminal loop. The stakes are practical rather than hype-driven because the account is about a real internal workflow, but it is still one team’s experience rather than a benchmarked proof.

### Operational Relevance

Focus on reducing synchronous review, tightening the inner loop, and using the harness to route mistakes into missing context, missing structure, or missing capability. The repo, build system, docs, and review agents all become part of the model’s operating environment. Teams should treat human time as a scarce budget and ask where agents can safely absorb the work.

### Service Automation Relevance

Support automation systems can use the same principle: minimize agent dependence on live human supervision by encoding policy, workflows, and escalation rules in machine-readable text. The transcript does not describe a customer-support deployment directly, but the pattern maps to reducing handoffs and keeping the automation loop closed.

### Mentioned Entities

- OpenAI Frontier
- Codex
- Ryan Lopopolo
- Symphony

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- The source suggests human review before merge can be reduced to near zero in some internal coding workflows, but this is an internal experiment, not a generalizable proof.

### Evidence Snippets

- "The only fundamentally scarce thing is the synchronous human attention of my team."
- "We’ve moved beyond even the humans reviewing the code as well. Most of the human review is post merge at this point."
- "the agent, the harness, as part of building AI products"

## Evidence / supporting sources

### Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony (2026-04-07)

- The source suggests human review before merge can be reduced to near zero in some internal coding workflows, but this is an internal experiment, not a generalizable proof. (`cedd785c4174` · counter · contrarian_or_speculative_claims[0]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- Focus on reducing synchronous review, tightening the inner loop, and using the harness to route mistakes into missing context, missing structure, or missing capability. The repo, build system, docs, and review agents all become part of the model’s operating environment. Teams should treat human time as a scarce budget and ask where agents can safely absorb the work. (`64329fa66ae3` · neutral · operational_relevance; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- Support automation systems can use the same principle: minimize agent dependence on live human supervision by encoding policy, workflows, and escalation rules in machine-readable text. The transcript does not describe a customer-support deployment directly, but the pattern maps to reducing handoffs and keeping the automation loop closed. (`95f4cb7f7439` · neutral · service_automation_relevance; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- Ryan frames the main bottleneck in agentic software development as synchronous human attention, not token supply. The workflow is therefore designed so agents can build, review, and merge work with humans only stepping in to change structure or handle the hardest cases. That shifts the unit of optimization from writing code faster to designing a system that keeps the model productive end to end. (`c18f559346c2` · neutral · summary; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- As of 2026-04-07, this is a durable operating model for teams already using coding agents: the biggest gains come from redesigning the workflow around what humans should stop doing, not from prompting harder. The source is explicit that the value is in removing unnecessary human touchpoints, especially in the PR and terminal loop. The stakes are practical rather than hype-driven because the account is about a real internal workflow, but it is still one team’s experience rather than a benchmarked proof. (`61a83ec644fa` · neutral · why_it_matters; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- "The only fundamentally scarce thing is the synchronous human attention of my team." (`41b879bbc168` · supporting · evidence_snippets[0]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- "We’ve moved beyond even the humans reviewing the code as well. Most of the human review is post merge at this point." (`7ee2dd82597c` · supporting · evidence_snippets[1]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])
- "the agent, the harness, as part of building AI products" (`9d04bb3232a0` · supporting · evidence_snippets[2]; [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]])

## Source

- [[sources/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy|Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony]]
