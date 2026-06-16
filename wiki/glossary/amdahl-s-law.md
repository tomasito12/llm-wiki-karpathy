---
title: Amdahl's law
slug: amdahl-s-law
entity_id: glossary:amdahl-s-law
category: glossary
tags:
- agent-systems
- inference
- orchestration
source_count: 1
evidence_count: 4
source_ids:
- when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
---

# Amdahl's law

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Amdahl's law states that the overall speedup of a system is limited by the portion of the workflow that does not speed up. Even large gains in one step can produce modest end-to-end improvement if another step becomes the bottleneck.

## Relevance Note

Useful for designing AI workflows, support automation, and agent systems where one faster component can expose a different constraint. It is a durable lens for estimating whether gains from model automation will actually translate into faster end-to-end delivery.

## Evidence / supporting sources

### When AI builds itself (undated)

- In AI systems, this means faster model generation does not automatically make the whole organization faster if review, approval, data access, or verification remain slow. The useful operational lesson is to identify the remaining human or system bottleneck before assuming the new capability will raise total throughput proportionally. This is especially important in agentic workflows, where execution can be cheap while judgment and oversight remain expensive. (`570d0fe6ef16` · neutral · extended_explanation; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Amdahl's law states that the overall speedup of a system is limited by the portion of the workflow that does not speed up. Even large gains in one step can produce modest end-to-end improvement if another step becomes the bottleneck. (`d86597e22401` · neutral · proposed_definition; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- Useful for designing AI workflows, support automation, and agent systems where one faster component can expose a different constraint. It is a durable lens for estimating whether gains from model automation will actually translate into faster end-to-end delivery. (`4b77f50fdd48` · neutral · relevance_note; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])
- But speeding up one part of a process often just shifts the bottleneck elsewhere: overall pace is capped by the parts that haven’t sped up. In computing, this is known as Amdahl’s law, and the same logic can apply to organizations. (`e335fc85459e` · supporting · supporting_snippet; [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

No related pages captured.

## Sources

- [[sources/when-ai-builds-itself-01kv4t9e77krbk1p0jwvt7pkyp|When AI builds itself]]
