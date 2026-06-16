---
title: I Finally Have My Dream Local AI Stack (and it runs on AMD)
slug: i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m
category: source
tags:
- ai-engineering
- api-first
- inference-efficiency
- inference-systems
- local-first
- open-model-pressure
- open-source
- open-weight-model
- reasoning-model
- runtime-architecture
- tool-use-capable
source_id: i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m
author: Cody Sandahl
publication: Medium
published_date: '2026-04-25'
assessed_as_of: '2026-04-25'
ingested_at: '2026-06-06T21:55:41+00:00'
canonical_url: https://medium.com/@codysandahl/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-c9f4935788f9
content_sha256: 83b6d2a619f01dabc292a78fb681165648def211051fdc41a69a0064ed07c27c
derived_models:
- foundation-models/gemma-4.md
derived_tools:
- tools/lemonade-server.md
derived_topics:
- topics/layered-local-and-cloud-inference.md
- topics/openai-compatible-local-endpoints.md
derived_trends:
- industry-trends/open-weight-models-become-viable-on-consumer-hardware.md
derived_pages:
- foundation-models/gemma-4.md
- industry-trends/open-weight-models-become-viable-on-consumer-hardware.md
- tools/lemonade-server.md
- topics/layered-local-and-cloud-inference.md
- topics/openai-compatible-local-endpoints.md
---

# I Finally Have My Dream Local AI Stack (and it runs on AMD)

This piece is about building a personal AI computer that keeps most work local instead of sending requests to cloud services. The unusual part is the hardware: an AMD mini desktop with 128GB of shared memory, which lets big models and media tools fit on one machine. The author says the real breakthrough is Lemonade Server, which made AMD inference much easier than Ollama for this setup. Everything is tied together with simple direct connections, a browser interface, private research tools, and secure remote access through Tailscale. The basic idea is that local AI became practical enough in 2026 to replace many paid cloud calls, as long as you are willing to do the setup work.

## Key insights

- On AMD hardware, a direct Lemonade Server path was more reliable than routing local inference through a generic aggregator like LiteLLM.
- 128GB of unified memory changes what fits locally more than it changes raw speed: large models, embeddings, and some video workflows become practical, but not necessarily fast.
- Using separate direct paths for local and cloud models reduced intermittent failures compared with forcing everything through one abstraction layer.
- For this workload, a smaller embedding model was preferred because larger embeddings did not improve retrieval enough to justify the extra cost.
- A persistent knowledge layer with Obsidian and programmatic read/write access is treated as a core part of the AI stack, not an optional add-on.

## Derived knowledge pages

- [[foundation-models/gemma-4]]
- [[industry-trends/open-weight-models-become-viable-on-consumer-hardware]]
- [[tools/lemonade-server]]
- [[topics/layered-local-and-cloud-inference]]
- [[topics/openai-compatible-local-endpoints]]

## Why it matters

The article is useful because it turns a vague “local AI” idea into a concrete, end-to-end stack with hardware, inference, retrieval, memory, image generation, and remote access all wired together. The strongest engineering takeaway is that unified memory can unlock model classes that would be awkward on typical consumer GPUs, but the article also shows that software compatibility still decides whether the system feels usable. The Lemonade-versus-Ollama comparison is especially practical: the author reports that Lemonade’s OpenAI-compatible API and AMD-native support removed a lot of downstream friction, which is a durable lesson for anyone building on non-NVIDIA hardware. The decision to keep two separate connection paths, rather than forcing a single unified endpoint, is another concrete reliability lesson that should survive beyond this one machine. The stack also highlights that ingestion and persistent memory are not side quests; Docling, LightOnOCR, and Obsidian materially shape day-to-day usefulness. The evidence is still a single-person implementation case, so it is strong for operations guidance but weak as a benchmark. Actionable as of 2026-04-25, with the most durable advice being the architectural pattern rather than the exact product mix. For voice, meetings, support, or back-office automation, the article does not substantively argue those use cases, so any relevance there is limited to the general idea of local tool orchestration.

## Limitations / open questions

This is a single-user implementation report, not a controlled benchmark, so performance claims are subjective and workload-specific. The article gives useful model preferences but no systematic evaluation across tasks, latency, throughput, or cost under repeated measurement. Security is discussed at a high level through firewall rules and Tailscale, but there is no penetration test, threat model, or audit of the local services. The cloud escape hatch through LiteLLM is described as minimal-cost, but the article does not quantify spending, token usage, or how often cloud fallback is still required. It is also unclear how portable the setup would be to other AMD systems, different Linux distributions, or less memory-rich machines. The video-generation portion is acknowledged as incomplete because Lemonade does not yet support video, so ComfyUI remains necessary.

## Contradictions / unverified claims

The piece makes a strong product recommendation for Lemonade over Ollama on AMD, but the evidence is anecdotal and tied to one configuration. Claims that 128GB unified memory makes large local models “genuinely practical” are plausible, yet the article also admits the machine is compute-limited and may still be slow on some tasks. The author’s preference for direct point-to-point connections over an abstraction layer is convincing as a reliability story, but it is not proven that this is the best design for other stacks. The article is candid that local image generation still trails cloud models on quality and text rendering, which tempers any broad local-first enthusiasm. Overall, the skepticism is mild: the setup seems real and useful, but the evidence supports a well-informed personal build rather than a universal recommendation.

## Source metadata

- Canonical URL: https://medium.com/@codysandahl/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-c9f4935788f9
- Raw markdown: `raw/readwise/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m.md`
- Raw HTML: `raw/readwise/i-finally-have-my-dream-local-ai-stack-and-it-runs-on-amd-01kqz00ky4865ndwsss3xegt6m.html`
