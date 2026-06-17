---
title: Amdahl's law
slug: amdahl-s-law
entity_id: glossary:amdahl-s-law
category: glossary
tags:
- agent-systems
- inference
- orchestration
first_seen: '2026-05-28'
last_seen: '2026-05-28'
source_count: 2
evidence_count: 8
source_ids:
- the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
- when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp
value_level: high
confidence: 0.935
synthesis_state: stage1-placeholder
---

# Amdahl's law

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Amdahl's law states that the overall speedup of a system is limited by the portion of the workflow that does not speed up. Even large gains in one step can produce modest end-to-end improvement if another step becomes the bottleneck.

## Related Terms

- Harness

## Relevance Note

Useful for designing AI workflows, support automation, and agent systems where one faster component can expose a different constraint. It is a durable lens for estimating whether gains from model automation will actually translate into faster end-to-end delivery.

## Evidence / supporting sources

### The Orchestration Tax (2026-05-28)

- In practice, the bottleneck matters more than the number of workers. If review, approval, or integration remains a single-threaded step, the whole system is capped by that step no matter how many tasks run in parallel. This is why teams can create the impression of speed while the real throughput of delivered work stays flat. The concept is useful any time AI outputs still need human judgment before they can be merged, shipped, or trusted. (`d9e23e3e9035` · neutral · extended_explanation; [[sources/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y|The Orchestration Tax]])
- Amdahl's law states that the maximum speedup from parallelizing a system is limited by the portion of work that must remain serial. If a meaningful part of the process cannot be parallelized, adding more parallel workers eventually yields diminishing returns. (`00a2e25212ea` · neutral · proposed_definition; [[sources/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y|The Orchestration Tax]])
- This matters for AI engineering because many agent workflows still depend on one human reviewer, operator, or approver. It helps teams size agent concurrency to the real review bottleneck instead of to UI convenience or wishful thinking. (`fd4c81e42adb` · neutral · relevance_note; [[sources/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y|The Orchestration Tax]])
- "Amdahl’s Law makes this very precise. The speedup you get from parallelizing is capped by the fraction of work that stays serial." (`b5ff08467931` · supporting · supporting_snippet; [[sources/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y|The Orchestration Tax]])

### When AI builds itself (undated)

- In AI systems, this means faster model generation does not automatically make the whole organization faster if review, approval, data access, or verification remain slow. The useful operational lesson is to identify the remaining human or system bottleneck before assuming the new capability will raise total throughput proportionally. This is especially important in agentic workflows, where execution can be cheap while judgment and oversight remain expensive. (`570d0fe6ef16` · neutral · extended_explanation; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Amdahl's law states that the overall speedup of a system is limited by the portion of the workflow that does not speed up. Even large gains in one step can produce modest end-to-end improvement if another step becomes the bottleneck. (`d86597e22401` · neutral · proposed_definition; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Useful for designing AI workflows, support automation, and agent systems where one faster component can expose a different constraint. It is a durable lens for estimating whether gains from model automation will actually translate into faster end-to-end delivery. (`4b77f50fdd48` · neutral · relevance_note; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- But speeding up one part of a process often just shifts the bottleneck elsewhere: overall pace is capped by the parts that haven’t sped up. In computing, this is known as Amdahl’s law, and the same logic can apply to organizations. (`e335fc85459e` · supporting · supporting_snippet; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Harness

## Sources

- [[sources/the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y|The Orchestration Tax]]
- [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]]
