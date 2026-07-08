---
title: Claude Opus 4.7
slug: claude-opus-4-7
entity_id: model:claude-opus-4-7
category: foundation-model
tags:
- long-context-model
- proprietary-model
- reasoning-model
first_seen: '2026-04-21'
last_seen: '2026-04-21'
source_count: 1
evidence_count: 14
source_ids:
- karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr
value_level: high
confidence: 0.88
synthesis_state: stage1-placeholder
types:
- proprietary-model
- reasoning-model
---

# Claude Opus 4.7

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A long-context model positioned for heavy document ingestion and synthesis. The source emphasizes that it can run a 1M-token input context at standard API pricing, and that its adaptive thinking allocates reasoning budget per step rather than burning the same budget on every call. It is framed as useful for rereading existing wiki pages, integrating new claims, and rewriting connected pages during compilation workflows.

## Benchmark Observations

- The source does not provide formal benchmark results, but it does state that the model ships with a 1M-token context window.
- It claims a new tokenizer produces up to 35% more tokens per character than Opus 4.6, which affects practical capacity calculations.

## Comparative Observations

- The source contrasts it with Opus 4.6 by saying the newer tokenizer yields up to 35% more tokens per character.
- It is described as having no long-context premium at standard API pricing, which is presented as better economics than older assumptions around large-context use.

## Core Capabilities

- It supports a 1M-token input context window, which the source says can cover roughly 300 to 400 densely written wiki pages.
- It uses adaptive thinking, which the source describes as allocating reasoning budget per step instead of using a fixed thinking budget on every call.
- It can support batch ingestion workflows when paired with prompt caching and the Batch API.

## Maturity signals

The article presents it as production-usable as of April 2026, not as a speculative model. It is paired with concrete pricing and context-window claims, but the evidence base in the article is still expert synthesis rather than independent benchmark reporting.

## Pricing / inference implications

The article says Opus 4.7 runs the full 1M-token context at standard API pricing with no long-context premium, and that prompt caching hits at roughly 10% of standard input rate. It also notes that Batch API usage can cut another 50% off overnight ingestion runs, which makes compilation workflows more affordable than earlier generations but still expensive relative to stateless retrieval.

## Provider

Anthropic

## Service automation implications

The source does not connect this model to customer-facing support automation directly. Its implication is mainly on the back-office side: better long-context compilation can help maintain durable internal knowledge that later powers support or agent workflows.

## Weaknesses / limitations

The source still treats ingestion as expensive, even with improved pricing and caching. The million-token window does not eliminate the need for retrieval once the corpus grows beyond that size, and the article warns that hallucinations can be baked into the wiki if ingestion is not reviewed carefully.

## Evidence / supporting sources

### Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over (2026-04-21)

- The source contrasts it with Opus 4.6 by saying the newer tokenizer yields up to 35% more tokens per character. (`3db7bb1b3dc5` · neutral · comparative_observations[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It is described as having no long-context premium at standard API pricing, which is presented as better economics than older assumptions around large-context use. (`118aa5fa4434` · neutral · comparative_observations[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- As of 2026-04-21, this makes large personal or team knowledge bases more feasible because one pass can cover many source documents and related wiki pages without immediately forcing retrieval-only architectures. It also reduces pressure on aggressive chunking for corpora that still fit inside the million-token window, but the source notes that ingestion remains token-heavy and should be treated as the main cost bucket. For higher-volume use, the article recommends batching and caching the stable schema, index, and pages. (`7992e6ea4e4a` · neutral · deployment_implications; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The article presents it as production-usable as of April 2026, not as a speculative model. It is paired with concrete pricing and context-window claims, but the evidence base in the article is still expert synthesis rather than independent benchmark reporting. (`bf5e9de191e0` · neutral · maturity_signals; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- A long-context model positioned for heavy document ingestion and synthesis. The source emphasizes that it can run a 1M-token input context at standard API pricing, and that its adaptive thinking allocates reasoning budget per step rather than burning the same budget on every call. It is framed as useful for rereading existing wiki pages, integrating new claims, and rewriting connected pages during compilation workflows. (`5e54f11d2022` · neutral · operational_profile; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The article says Opus 4.7 runs the full 1M-token context at standard API pricing with no long-context premium, and that prompt caching hits at roughly 10% of standard input rate. It also notes that Batch API usage can cut another 50% off overnight ingestion runs, which makes compilation workflows more affordable than earlier generations but still expensive relative to stateless retrieval. (`5b5bdf9367ba` · neutral · pricing_inference_implications; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The source does not connect this model to customer-facing support automation directly. Its implication is mainly on the back-office side: better long-context compilation can help maintain durable internal knowledge that later powers support or agent workflows. (`98a77176f72c` · neutral · service_automation_implications; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The source does not provide formal benchmark results, but it does state that the model ships with a 1M-token context window. (`a4c6fbc0b001` · supporting · benchmark_observations[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It claims a new tokenizer produces up to 35% more tokens per character than Opus 4.6, which affects practical capacity calculations. (`d1da8b77ab8c` · supporting · benchmark_observations[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It supports a 1M-token input context window, which the source says can cover roughly 300 to 400 densely written wiki pages. (`c34d5396dc9d` · supporting · core_capabilities[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It uses adaptive thinking, which the source describes as allocating reasoning budget per step instead of using a fixed thinking budget on every call. (`f18d326fac8d` · supporting · core_capabilities[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- It can support batch ingestion workflows when paired with prompt caching and the Batch API. (`6d460aabf9c9` · supporting · core_capabilities[2]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- "As of April 2026, Claude Opus 4.7 and Gemini 3.1 Pro both ship with 1M-token input context windows, and Opus 4.7 runs the full million at standard API pricing with no long-context premium." (`f8999f113b28` · supporting · supporting_snippet; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- The source still treats ingestion as expensive, even with improved pricing and caching. The million-token window does not eliminate the need for retrieval once the corpus grows beyond that size, and the article warns that hallucinations can be baked into the wiki if ingestion is not reviewed carefully. (`549bcaf15264` · uncertainty · weaknesses_limitations; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])

## Contradictions / tensions

- The source still treats ingestion as expensive, even with improved pricing and caching. The million-token window does not eliminate the need for retrieval once the corpus grows beyond that size, and the article warns that hallucinations can be baked into the wiki if ingestion is not reviewed carefully. (uncertainty; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])

## Related pages

- [[foundation-models/opus-4-6|Opus 4.6]]

## Sources

- [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]]
