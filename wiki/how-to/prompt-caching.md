---
title: Prompt Caching
slug: prompt-caching
entity_id: how_to:prompt-caching
category: how-to
tags:
- ai-economics
- context-engineering
- inference-systems
- prompt-engineering
- runtime-systems
first_seen: '2026-04-17'
last_seen: '2026-05-08'
source_count: 2
evidence_count: 25
source_ids:
- 8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9
- agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv
value_level: high
confidence: 0.955
synthesis_state: stage1-placeholder
---

# Prompt Caching

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Prompt caching is a way to avoid paying for the same long static text on every request. It helps when your app sends the same system prompt, examples, or retrieved context many times and the repeated prefix drives up cost. The problem is common in chatbots, support tools, and other applications with stable instructions. Without caching, the model recomputes the same prefix from scratch each time. That makes even simple traffic expensive at scale.

## Caveats

Savings depend on having repeated prefixes. If you mix dynamic content into the front of the prompt, cache hits drop. The article also notes provider-specific pricing and break-even behavior, so exact savings are workload- and vendor-dependent as of 2026-04-17.

## Implementation Steps

- Identify repeated static text in your requests.
- Move system prompts, examples, and repeated documents to the front.
- Place the user message and other dynamic fields last.
- Enable provider caching or automatic caching if available.
- Measure cache-hit rate and cost per request over time.
- Identify the stable prefix of the prompt: system instructions, examples, and tools.
- Place that stable content before any user-specific or variable content.
- Keep the cached section byte-for-byte consistent across requests.
- If self-hosting, enable prefix caching in the serving framework and tune cache block size and memory limits.
- If using a provider API, follow the provider's cache parameters and prompt structure requirements.
- Audit prompt drift from timestamps, reordered tool blocks, and formatting changes.

## Prerequisites

- A request pattern with repeated prefixes
- Access to a provider or stack that supports prefix caching
- Basic logging for token counts and cost
- A long prompt that repeats across requests.
- A serving stack or API that supports prompt or prefix caching.
- A prompt design that cleanly separates stable and variable sections.

## Evidence / supporting sources

### 8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained) (2026-04-17)

- Put the static parts of the request first so the provider can reuse them. Keep the system prompt, few-shot examples, and any repeated retrieved documents before the user message. Let dynamic content come last. For providers that support it, use prefix caching or automatic caching to reduce repeated-token charges. This works best when the same long prefix shows up across many requests. (`99b2daaf2269` · neutral · answer_summary; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Identify repeated static text in your requests. (`5dc8c612ae4e` · neutral · implementation_steps[0]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Move system prompts, examples, and repeated documents to the front. (`44eb9a667b15` · neutral · implementation_steps[1]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Place the user message and other dynamic fields last. (`7fa9da64fe2a` · neutral · implementation_steps[2]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Enable provider caching or automatic caching if available. (`8d91d1d5f35e` · neutral · implementation_steps[3]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Measure cache-hit rate and cost per request over time. (`d5b1620c192c` · neutral · implementation_steps[4]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- A request pattern with repeated prefixes (`700a73413883` · neutral · prerequisites[0]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Access to a provider or stack that supports prefix caching (`6ac2aa4c8a17` · neutral · prerequisites[1]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Basic logging for token counts and cost (`750541c67d8f` · neutral · prerequisites[2]; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Prompt caching is a way to avoid paying for the same long static text on every request. It helps when your app sends the same system prompt, examples, or retrieved context many times and the repeated prefix drives up cost. The problem is common in chatbots, support tools, and other applications with stable instructions. Without caching, the model recomputes the same prefix from scratch each time. That makes even simple traffic expensive at scale. (`1f11e39f3539` · neutral · what_and_problem; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- "Prefix caching stores the computed result for a repeated prefix. The next request that shares that prefix starts from the cached state." (`4a5797966840` · supporting · supporting_snippet; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Savings depend on having repeated prefixes. If you mix dynamic content into the front of the prompt, cache hits drop. The article also notes provider-specific pricing and break-even behavior, so exact savings are workload- and vendor-dependent as of 2026-04-17. (`fcca56faa11c` · uncertainty · caveats; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])

### Agentic AI: How to Save on Tokens (2026-05-08)

- Put the stable part of the prompt first, keep it exactly the same, and let the variable user-specific content come later. If you are using a provider that supports it, make sure the request meets the provider's cache rules so the repeated prefix can be reused. For self-hosted inference, use a serving framework that supports prefix caching and keep the reusable content in the first part of the prompt. Treat cache hits as a systems problem: even small changes such as spacing, timestamps, or reordered tool definitions can break reuse. Use it first when you have long prompts that do not change much across calls. (`694ad8763207` · neutral · answer_summary; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Identify the stable prefix of the prompt: system instructions, examples, and tools. (`511a64a6eb5a` · neutral · implementation_steps[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Place that stable content before any user-specific or variable content. (`f68e70a28769` · neutral · implementation_steps[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Keep the cached section byte-for-byte consistent across requests. (`058dca0486bb` · neutral · implementation_steps[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- If self-hosting, enable prefix caching in the serving framework and tune cache block size and memory limits. (`a9e1405f62df` · neutral · implementation_steps[3]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- If using a provider API, follow the provider's cache parameters and prompt structure requirements. (`e76594570413` · neutral · implementation_steps[4]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Audit prompt drift from timestamps, reordered tool blocks, and formatting changes. (`5f8bb67615bf` · neutral · implementation_steps[5]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A long prompt that repeats across requests. (`a8bca1653dda` · neutral · prerequisites[0]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A serving stack or API that supports prompt or prefix caching. (`94c69f0d5baa` · neutral · prerequisites[1]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- A prompt design that cleanly separates stable and variable sections. (`5ff28557de49` · neutral · prerequisites[2]; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Prompt caching is a way to avoid paying to process the same long instructions every time an agent calls a model. It matters when an agent has a large stable prompt, such as a system prompt, examples, or tool definitions, that would otherwise be sent again and again. The goal is to reduce both latency and token cost without changing the task itself. It is most useful when the front of the prompt stays fixed across many calls. (`3d086ba2b311` · neutral · what_and_problem; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- "Prompt caching is a quick win for long system prompts" ... "you always put stable instructions, examples, and tools first, and variable content later." (`996359e5494f` · supporting · supporting_snippet; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])
- Exact matching is required, so tiny prompt changes can eliminate the cache hit. Cached state takes memory on the serving side, and providers may evict it after a short time window. Savings depend on prompt stability and on the provider's pricing rules, so illustrative numbers in the article are not universal. (`8c8b17c4313c` · uncertainty · caveats; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Contradictions / tensions

- Savings depend on having repeated prefixes. If you mix dynamic content into the front of the prompt, cache hits drop. The article also notes provider-specific pricing and break-even behavior, so exact savings are workload- and vendor-dependent as of 2026-04-17. (uncertainty; [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]])
- Exact matching is required, so tiny prompt changes can eliminate the cache hit. Cached state takes memory on the serving side, and providers may evict it after a short time window. Savings depend on prompt stability and on the provider's pricing rules, so illustrative numbers in the article are not universal. (uncertainty; [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]])

## Related pages

- [[how-to/semantic-caching|Semantic Caching]]
- [[how-to/prompt-engineering-fundamentals|Prompt Engineering Fundamentals]]

## Sources

- [[sources/8-llm-cost-optimization-techniques-how-to-cut-api-spend-by-up-to-70-visually-explained-01ktkyv6hm99qdvw30jt2405q9|8 LLM Cost Optimization Techniques: How to Cut API Spend by Up to 70% (Visually Explained)]]
- [[sources/agentic-ai-how-to-save-on-tokens-01kr4qf7weme5tht04bghph2dv|Agentic AI: How to Save on Tokens]]
