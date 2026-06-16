---
title: KV cache
slug: kv-cache
entity_id: glossary:kv-cache
category: glossary
tags:
- inference
- memory-systems
first_seen: '2026-04-20'
last_seen: '2026-06-01'
source_count: 3
evidence_count: 12
source_ids:
- choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj
- how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b
- recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf
value_level: high
confidence: 0.9566666666666667
synthesis_state: stage1-placeholder
---

# KV cache

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
The KV cache stores key and value tensors from previous tokens so a transformer model can reuse them during autoregressive generation instead of recomputing attention over the whole context each step. It is a core mechanism for reducing decode-time overhead in long text generation.

## Related Terms

- Mixture-of-Experts
- Grouped Query Attention

## Relevance Note

KV cache behavior is central to long-context serving, streaming assistants, and multi-turn chat systems. It often determines whether latency and memory use stay predictable as prompts get longer.

## Evidence / supporting sources

### Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks (2026-04-20)

- When a model generates text token by token, it needs to attend to all prior context. The KV cache lets the model keep the intermediate attention state from earlier tokens, which speeds up generation but consumes memory. Systems that handle long contexts, streaming responses, or many concurrent requests care a lot about how this cache is managed. Different runtimes use different cache strategies, and that can change whether performance stays steady as context grows or falls apart under long prompts. (`5db51c3f4afe` · neutral · extended_explanation; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- The KV cache stores key and value tensors from previous tokens so a transformer model can reuse them during autoregressive generation instead of recomputing attention over the whole context each step. It is a core mechanism for reducing decode-time overhead in long text generation. (`cb4f12cf2f67` · neutral · proposed_definition; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- KV cache behavior is central to long-context serving, streaming assistants, and multi-turn chat systems. It often determines whether latency and memory use stay predictable as prompts get longer. (`6d6495fea824` · neutral · relevance_note; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])
- "MLC-LLM uses TVM-compiled kernels with paged KV cache. That makes it the strongest option for long contexts (64K to 128K tokens)." (`4670f28fab0b` · supporting · supporting_snippet; [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]])

### How LLMs Actually Work (2026-06-01)

- During generation, each new token needs to attend to the earlier tokens. Instead of recalculating those earlier Key and Value vectors every step, the model keeps them in memory. That makes decoding much faster, but it also means memory usage grows with context length. In production systems, KV-cache size is one of the main limits on throughput and maximum usable context. (`fb66f30f4b2b` · neutral · extended_explanation; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])
- A KV cache is stored attention state used during autoregressive generation so a transformer does not have to recompute all prior Key and Value vectors for every new token. It trades memory for speed, which is especially important for long prompts and long outputs. (`4a44fa25ac51` · neutral · proposed_definition; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])
- Important for any chat, voice, or agent system that must generate multiple turns efficiently. KV-cache pressure directly affects latency, throughput, and how much conversation history a system can keep alive at once. (`3a46bb017dcb` · neutral · relevance_note; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])
- "This is called the KV cache, and it’s the main memory cost of running an LLM at long context lengths." (`4934049ca7cb` · supporting · supporting_snippet; [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]])

### Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention (2026-05-16)

- In a standard transformer, every new token needs access to previous tokens through attention. Caching the key and value tensors avoids recalculating those past states, which makes generation much faster. The tradeoff is that long contexts can consume a lot of memory, especially when many layers and many heads each keep their own cache. Because of that, KV cache design is one of the main levers for long-context efficiency in production LLM systems. (`7f5e8d7d63f7` · neutral · extended_explanation; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- The KV cache is the stored set of key and value tensors used by an autoregressive transformer to avoid recomputing past attention states for every new token. It reduces repeated work during long generation, but its memory use grows with context length. (`6ae14eee4f0f` · neutral · proposed_definition; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- KV cache design is a core constraint in long-context chatbots, voice agents, and workflow assistants because it affects memory footprint, throughput, and how much conversation history can stay in context. It is a durable concept whenever teams optimize inference cost or support longer agent runs. (`8cd4b62ab9df` · neutral · relevance_note; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])
- KV-cache size, memory traffic, and attention cost quickly become the main constraints (`3b641cb41ab1` · supporting · supporting_snippet; [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Grouped Query Attention
- Mixture-of-Experts

## Sources

- [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]]
- [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]]
- [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]]
