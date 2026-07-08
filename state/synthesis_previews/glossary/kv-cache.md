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
confidence: 0.956667
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 92350d536bb5fd75
current_input_hash: 92350d536bb5fd75
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-08T19:30:22Z'
---

# KV cache

## Executive synthesis

KV cache is the stored key/value attention state a transformer keeps during autoregressive generation so it can reuse past attention instead of recomputing it for every new token. In practice, it is a speed-versus-memory tradeoff: it makes decoding faster, but its memory footprint grows with context length and can become the main limit on throughput and usable context. The concept is especially important for long-context serving, streaming responses, chat, voice, and agent systems, where cache management can determine whether performance stays predictable or degrades as prompts get longer.

## Context card

- **Use this page when:** Use this page when you need a concise definition of KV cache and want to understand why it is a practical bottleneck in long-context or multi-turn LLM inference.
- **Best for questions about:** What KV cache means in transformer inference, Why KV cache speeds up token generation, Why long prompts and long outputs increase memory use, Why KV cache is important in chat and agent systems, How cache strategy affects long-context runtime behavior
- **Not enough for:** A full transformer architecture explanation, Precise implementation details for a specific runtime or model, Numerical sizing formulas or memory estimates, Comparative benchmarking beyond the cited runtime discussion
- **Strongest sources:** How LLMs Actually Work, Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention, Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks
- **Related tags:** inference, memory-systems

## What to remember

- KV cache stores prior key/value tensors so the model can skip recomputing past attention during generation.
- It speeds up decoding but increases memory use as context grows.
- It is often the main constraint for long-context LLM serving and multi-turn assistants.
- Cache handling can decide whether performance stays stable or falls apart under long prompts.
- This page is useful when thinking about inference latency, throughput, and context-length limits.

## Consensus

- KV cache is the stored attention state—key and value tensors—from earlier tokens in an autoregressive transformer.
- It lets the model reuse past attention work during generation instead of recomputing it for every new token.
- The main tradeoff is memory for speed: decoding gets faster, but memory use grows with context length.
- KV cache pressure matters most in long-context generation, multi-turn chat, streaming assistants, voice agents, and other production inference systems.
- KV-cache size is a major constraint on latency, throughput, and how much conversation history can stay in context.

## Tensions / open questions

- The sources agree on the core mechanism, but they do not claim one universally best cache strategy; runtime behavior differs across systems.
- The Apple Silicon runtime source makes a strong claim that MLC-LLM is strongest for 64K–128K contexts, but that is runtime-specific and not established as a general rule for all deployments.

## Evidence quality

- Strong agreement across three sources on the core definition and tradeoff.
- Evidence is good for practical inference relevance, especially long-context and multi-turn use cases.
- This page is thin on implementation specifics and does not provide quantitative sizing guidance.
- Runtime-specific claims are directional rather than universal; cache strategy varies by system.

## Practical takeaway

If you are optimizing inference, treat KV cache as a first-order resource: bigger context and more concurrent sessions usually mean more memory pressure, so runtime cache strategy can matter as much as raw model speed.

## Evidence index

- Sources: 3
- Evidence items: 12
- Current input hash: `92350d536bb5fd75`
- Cached input hash: `92350d536bb5fd75`
- Last synthesized: 2026-07-08T19:30:22Z
- Synthesis status: `fresh`

## Related pages

- [[glossary/mixture-of-experts|Mixture-of-Experts]]
- [[glossary/grouped-query-attention|Grouped Query Attention]]

## Sources

- [[sources/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj|Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks]]
- [[sources/how-llms-actually-work-01kv4tanr9r0k17sysdm6cv45b|How LLMs Actually Work]]
- [[sources/recent-developments-in-llm-architectures-kv-sharing-mhc-and-compressed-attention-01krrba0929cn5qjh3gve00hyf|Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention]]
