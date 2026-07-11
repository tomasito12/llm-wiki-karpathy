---
title: 'Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond
  Benchmarks'
slug: choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj
category: source
tags:
- ai-engineering
- api-first
- cloud-hosted
- coding
- enterprise-ai
- inference
- inference-efficiency
- inference-systems
- local-first
- memory-systems
- model-architecture
- open-source
- runtime-systems
- software-engineering
source_id: choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj
author: Michael Hannecke
publication: Medium
published_date: '2026-04-20'
assessed_as_of: '2026-04-20'
ingested_at: '2026-07-09T19:30:09.966124+00:00'
canonical_url: https://medium.com/@michael.hannecke/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-2449067b8b67
content_sha256: 7ed1d5f17c02c7433d06a5e33ff0e6bdce685c40f08d53e1f1c03c7d7a99a8e5
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_glossary:
- glossary/kv-cache.md
- glossary/mixture-of-experts.md
derived_tools:
- tools/llama-cpp.md
- tools/mlx.md
- tools/ollama.md
derived_topics:
- topics/runtime-architecture.md
- topics/use-case-specific-local-model-selection.md
derived_trends:
- industry-trends/apple-silicon-local-inference-becomes-practical.md
derived_pages:
- glossary/kv-cache.md
- glossary/mixture-of-experts.md
- industry-trends/apple-silicon-local-inference-becomes-practical.md
- tools/llama-cpp.md
- tools/mlx.md
- tools/ollama.md
- topics/runtime-architecture.md
- topics/use-case-specific-local-model-selection.md
---

# Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks

This piece says you should not pick an Apple Silicon LLM runtime by looking only at tokens-per-second charts. The real choice depends on where your app runs, which model formats you need, whether you must fine-tune locally, and how much hardware variation you have to support. MLX is strong for smaller models and is the only local option here with native LoRA fine-tuning. llama.cpp is broader in model support and can offload layers when memory is tight. The practical takeaway is to build a thin abstraction so you can switch runtimes later without rewriting the whole app.

## Key insights

- For models under about 14B parameters, MLX has a clear speed advantage over llama.cpp, but that advantage shrinks or disappears once memory bandwidth becomes the bottleneck at larger model sizes.
- Ollama 0.19’s impressive MLX benchmark numbers are tied to one MoE model, one chip, and one quantization format, so they are not a general basis for runtime migration.
- The strongest runtime choice can be eliminated before performance matters at all: App Store distribution, local fine-tuning, or layer offload needs each narrow the options sharply.
- MLX is the only local runtime in the article with native LoRA and QLoRA fine-tuning, which makes it a hard requirement for some regulated or domain-adapted workloads.
- A thin inference interface is presented as a default hedge because runtime, model format, and backend choices have all shifted within 18 months, making migration risk real.

## Derived knowledge pages

- [[glossary/kv-cache]]
- [[glossary/mixture-of-experts]]
- [[industry-trends/apple-silicon-local-inference-becomes-practical]]
- [[tools/llama-cpp]]
- [[tools/mlx]]
- [[tools/ollama]]
- [[topics/runtime-architecture]]
- [[topics/use-case-specific-local-model-selection]]

## Why it matters

The article is useful because it turns runtime selection into a reusable decision framework instead of a benchmark chase. That is operationally valuable for teams building on-device inference on Apple Silicon, especially when the same product must survive model-size changes, chip-family differences, and backend swaps over a multi-year lifecycle. Its central contribution is the six-dimension lens: distribution constraints, model ecosystem coverage, integration depth, local fine-tuning, layer offload, and vendor risk. Those dimensions are more durable than any single tok/s result because the article shows how a runtime can be best on speed and still lose on deployment fit or migration cost. The distinction between compute-bound smaller models and bandwidth-bound larger models is also practical, because it explains why MLX can look far better on one workload and nearly tied with llama.cpp on another. The article is strongest when it warns against reading one benchmark as a platform verdict and when it recommends a thin engine abstraction so future runtime shifts are a contained implementation change. The limitations are important: many claims depend on cited third-party benchmarks, and some recommendations assume Apple Silicon-only deployment and local inference as the fixed context. As of 2026-04-20, the advice to evaluate runtime choice as architecture rather than leaderboard is actionable, while the specific performance hierarchy should be treated as model- and hardware-dependent rather than universal.

## Limitations / open questions

The evidence base is mostly benchmark-driven and depends on cited studies plus the author’s interpretation, so the performance claims are not independently validated inside the article. Several recommendations assume Apple Silicon, local inference, and a relatively stable set of deployment constraints; they may not transfer to mixed hardware or cloud-first systems. The article notes MLX’s fine-tuning advantage and llama.cpp’s layer offload advantage, but it does not quantify the engineering cost of maintaining dual backends. The worked examples are plausible but narrow, and the article does not provide a broader sample of enterprise workloads or failure cases. Security, governance, and operational monitoring are mentioned only lightly, so the full cost of adopting an abstraction layer is not explored in depth.

## Contradictions / unverified claims

The strongest skepticism is aimed at benchmark interpretation: the article argues that decode-only or single-model numbers can mislead, especially for MoE models and longer contexts. That critique is well founded, but the article still relies on benchmarks to justify the framework, so the hierarchy of runtimes remains context-specific rather than settled. The claim that engine abstraction is the architectural default is persuasive, but it is also somewhat opinionated; some teams may accept tighter coupling if their runtime and model set are stable. The piece also treats MLX’s local fine-tuning support as decisive, yet that matters only for teams that truly need on-device adapter training. Overall, the article is skeptical of leaderboard thinking, but its own recommendations should still be checked against the exact model, context length, memory budget, and deployment rules in a given project.

## Source metadata

- Canonical URL: https://medium.com/@michael.hannecke/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-2449067b8b67
- Raw markdown: `raw/readwise/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj.md`
- Raw HTML: `raw/readwise/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-01kts1hztetv71p5zgssn119fj.html`

## Full source text

---
readwise_id: "01kts1hztetv71p5zgssn119fj"
title: "Choosing an On-Device LLM Runtime on Apple Silicon: A Decision Framework Beyond Benchmarks"
author: "Michael Hannecke"
publication: "Medium"
source_url: "https://medium.com/@michael.hannecke/choosing-an-on-device-llm-runtime-on-apple-silicon-a-decision-framework-beyond-benchmarks-2449067b8b67"
category: "article"
location: "archive"
published_date: "2026-04-20"
saved_at: "2026-06-10T15:14:03.213000+00:00"
updated_at: "2026-06-14T13:15:11.773993+00:00"
tags: ["processed"]
---

Why token-per-second rankings lead enterprise architects to the wrong runtime, and what to evaluate instead.
