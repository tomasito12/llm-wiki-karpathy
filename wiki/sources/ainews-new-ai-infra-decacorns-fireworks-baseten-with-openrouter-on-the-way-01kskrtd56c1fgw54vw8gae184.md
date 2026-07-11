---
title: '[AINews] New AI Infra decacorns: Fireworks, Baseten (with OpenRouter on the
  way)'
slug: ainews-new-ai-infra-decacorns-fireworks-baseten-with-openrouter-on-the-way-01kskrtd56c1fgw54vw8gae184
category: source
source_id: ainews-new-ai-infra-decacorns-fireworks-baseten-with-openrouter-on-the-way-01kskrtd56c1fgw54vw8gae184
author: Latent Space
publication: latent.space
published_date: '2026-05-27'
assessed_as_of: '2026-05-27'
ingested_at: '2026-06-06T21:38:31+00:00'
canonical_url: https://www.latent.space/p/ainews-new-ai-infra-decacorns-fireworks
content_sha256: c33e1208a0e4e9b7e58cc1e59163f5c9456ce5c645f7e1c168335e2bb7088339
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# [AINews] New AI Infra decacorns: Fireworks, Baseten (with OpenRouter on the way)

This issue is a roundup of AI infra and tooling news. The main idea is that serving models, routing requests across models, and building reliable agent harnesses are becoming more important than just having a better base model. It highlights big funding rounds for Fireworks, Baseten, and OpenRouter, plus product updates from vLLM, W&B, and others. It also surfaces research on long-term memory, long-context bottlenecks, and deep research agents. In plain English: the stack around the model is getting a lot of attention because real applications need routing, memory, and recovery, not just generation quality.

## Key insights

- OpenRouter’s reported volume growth from 5T to 25T weekly tokens is the clearest concrete signal in the piece that routing is becoming a production layer worth paying for.
- The roundup repeatedly frames harness quality, eval loops, and memory handling as differentiators, not just model size, which matters for agent builders.
- The article treats long-context serving as a systems bottleneck, with inference demand potentially outrunning capacity for longer workloads.
- vLLM’s Rust frontend is a practical serving optimization for CPU/API-server bottlenecks, with a cited throughput jump on a preprocess-heavy workload.
- Several benchmark and product examples are used to argue that real-world agent performance is separating from simple model leaderboard performance.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful because it compresses several adjacent signals about AI infrastructure into one date-stamped snapshot: funding, routing, serving, benchmark design, memory systems, and agent tooling. The strongest durable takeaway is that inference and orchestration layers are receiving enough usage and capital to justify standalone attention, especially where one application must route across multiple models or maintain long-running agent state. OpenRouter’s reported Series B and token growth make that point most concretely, while Fireworks and Baseten are presented as the other large funding markers in the same lane. The roundup also shows that operational concerns are becoming more central: context handling, durable turns, reconnects, stale state, and observability are described as practical differentiators, not afterthoughts. On the research side, the “sleep” memory idea and deep-research agents suggest active exploration of ways to manage long trajectories without unbounded KV-cache growth, but those are still early-stage as of 2026-05-27. The article’s evidence is mixed and often comes from company posts, tweets, or benchmark claims, so the value is in pattern recognition rather than settled conclusions. As of 2026-05-27, this is actionable mainly as a monitor-and-adopt signal for teams building multi-model or long-context systems, not as proof of a single dominant architecture. For chat, voice, meetings, and back-office automation, the practical relevance is that durable state, routing, and recovery are the infrastructure constraints that will shape those products if they rely on long-running agents.

## Limitations / open questions

Many of the strongest claims are provisional: Fireworks’ and Baseten’s rounds are described as being in talks or raising, not fully closed, and several benchmark results rely on vendor or practitioner commentary rather than independent replication. The article does not provide detailed workload breakdowns, cost curves, or failure modes for the reported serving and inference gains, so it is hard to judge how broadly they transfer. The “sleep” memory idea is conceptually interesting, but the roundup does not show production validation, latency tradeoffs across workloads, or security implications of persistent fast weights. OpenRouter’s volume growth is impressive, but the source does not separate organic demand from routing-induced token inflation or explain how much of that volume is durable versus bursty. The benchmark and product references also mix closed and open systems, which makes apples-to-apples comparison difficult.

## Contradictions / unverified claims

The roundup leans heavily on funding and engagement as proxies for significance, so some of the momentum could be narrative amplification rather than evidence of durable product advantage. Several technical claims are explicitly framed by the article itself as unverified, especially around Huawei’s engineering roadmap and some benchmark comparisons. The piece also suggests that better harnesses can reveal hidden capability, but that does not automatically imply those capabilities are reliable enough for production without stronger eval discipline. Overall skepticism should remain moderate: the signal is plausible and useful, but much of it is still a mix of product marketing, early measurements, and enthusiast interpretation.

## Source metadata

- Canonical URL: https://www.latent.space/p/ainews-new-ai-infra-decacorns-fireworks
- Raw markdown: `raw/readwise/ainews-new-ai-infra-decacorns-fireworks-baseten-with-openrouter-on-the-way-01kskrtd56c1fgw54vw8gae184.md`
- Raw HTML: `raw/readwise/ainews-new-ai-infra-decacorns-fireworks-baseten-with-openrouter-on-the-way-01kskrtd56c1fgw54vw8gae184.html`

## Full source text

---
readwise_id: "01kskrtd56c1fgw54vw8gae184"
title: "[AINews] New AI Infra decacorns: Fireworks, Baseten (with OpenRouter on the way)"
author: "Latent Space"
publication: "latent.space"
source_url: "https://www.latent.space/p/ainews-new-ai-infra-decacorns-fireworks"
category: "rss"
location: "archive"
published_date: "2026-05-27"
saved_at: "2026-05-27T03:49:24.847000+00:00"
updated_at: "2026-05-27T10:11:05.690875+00:00"
tags: ["processed"]
---

it's funding news, but it's good news.
