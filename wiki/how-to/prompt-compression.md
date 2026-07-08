---
title: Prompt Compression
slug: prompt-compression
entity_id: how_to:prompt-compression
category: how-to
tags:
- ai-economics
- context-engineering
- prompt-engineering
- retrieval-systems
first_seen: '2026-04-17'
last_seen: '2026-04-17'
source_count: 1
evidence_count: 12
source_ids:
- 8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Prompt Compression

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Prompt compression is about sending fewer tokens while keeping the information the model needs. It helps when long prompts, long retrieved passages, or verbose output formats are making every request more expensive than necessary. The problem is especially sharp because output tokens are described as costing more than input tokens. If you can say the same thing with less text, you reduce cost on every call. That makes compression one of the simplest ways to cut spend.

## Caveats

Compression can hurt quality if you remove information the model actually needs. The article’s output-size examples are illustrative rather than controlled benchmarks, so savings should be validated on the target workload as of 2026-04-17.

## Implementation Steps

- Trim repeated language from system prompts.
- Define constrained output schemas for structured tasks.
- Shorten asks that do not need open-ended detail.
- Compress retrieved context before it enters the prompt.
- Check that answer quality stays within your target bar.

## Prerequisites

- A task with a stable instruction set or structured output
- A way to measure output quality
- Optional: a context-compression tool for retrieval workflows

## Evidence / supporting sources

### 8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained) (2026-04-17)

- Remove repeated wording from system prompts and keep only the rules that matter. Ask for a strict output format instead of open-ended prose when the task is structured. For retrieval-heavy systems, compress long context before sending it to the model. The article specifically points to LLMLingua for reducing retrieved context size. Use this approach before chasing more complex infrastructure changes. (`2f85086c7583` · neutral · answer_summary; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Trim repeated language from system prompts. (`b3f82620e0f4` · neutral · implementation_steps[0]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Define constrained output schemas for structured tasks. (`19db1257216d` · neutral · implementation_steps[1]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Shorten asks that do not need open-ended detail. (`0dda01618539` · neutral · implementation_steps[2]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Compress retrieved context before it enters the prompt. (`0b7a39c0b3b0` · neutral · implementation_steps[3]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Check that answer quality stays within your target bar. (`093582ce2f60` · neutral · implementation_steps[4]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- A task with a stable instruction set or structured output (`2f815c6a323c` · neutral · prerequisites[0]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- A way to measure output quality (`e247ca9be398` · neutral · prerequisites[1]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Optional: a context-compression tool for retrieval workflows (`21445f28d984` · neutral · prerequisites[2]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Prompt compression is about sending fewer tokens while keeping the information the model needs. It helps when long prompts, long retrieved passages, or verbose output formats are making every request more expensive than necessary. The problem is especially sharp because output tokens are described as costing more than input tokens. If you can say the same thing with less text, you reduce cost on every call. That makes compression one of the simplest ways to cut spend. (`af4235e38b9c` · neutral · what_and_problem; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- "Most system prompts have significant redundancy. A 2,000-token prompt often contains the same instruction restated three different ways." (`4c9e862811f8` · supporting · supporting_snippet; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Compression can hurt quality if you remove information the model actually needs. The article’s output-size examples are illustrative rather than controlled benchmarks, so savings should be validated on the target workload as of 2026-04-17. (`36255b427d14` · uncertainty · caveats; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])

## Contradictions / tensions

- Compression can hurt quality if you remove information the model actually needs. The article’s output-size examples are illustrative rather than controlled benchmarks, so savings should be validated on the target workload as of 2026-04-17. (uncertainty; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])

## Related pages

- [[how-to/context-compaction|Context Compaction]]
- [[how-to/prompt-caching|Prompt Caching]]

## Sources

- [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]]
