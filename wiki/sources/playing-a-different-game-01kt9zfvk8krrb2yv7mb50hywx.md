---
title: Playing a different game
slug: playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx
category: source
tags:
- agent-systems
- customer-support
- enterprise-ai
- enterprise-oriented
- low-latency
- real-time
- runtime-architecture
- support-automation
- tool-use-capable
- voice
- voice-ai
- workflow-design
- workflow-restructuring
source_id: playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx
author: Eoghan McCabe
publication: The Intercom Blog
published_date: '2026-06-04'
assessed_as_of: '2026-06-04'
ingested_at: '2026-06-06T22:03:31+00:00'
canonical_url: https://www.intercom.com/blog/playing-a-different-game/
content_sha256: d2b9bfcbced37d41d0fdf9b7a1d6c37a69ceb70d8f240343d560c91bd6a2cdae
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_models:
- foundation-models/apex-flash.md
derived_tools:
- tools/fin-voice-2.md
derived_topics:
- topics/agent-runtime-architecture-for-voice.md
- topics/voice-agents-shift-toward-workflow-completion.md
derived_trends:
- industry-trends/voice-agents-shift-toward-workflow-completion.md
derived_pages:
- foundation-models/apex-flash.md
- industry-trends/voice-agents-shift-toward-workflow-completion.md
- tools/fin-voice-2.md
- topics/agent-runtime-architecture-for-voice.md
- topics/voice-agents-shift-toward-workflow-completion.md
---

# Playing a different game

This is a product announcement about a voice AI system called Fin Voice 2. The article says the team is showing a live demo instead of a polished fake one, because voice systems are difficult to make reliable. Its main technical idea is to split speech handling from answer generation so the agent can respond with lower delay. The product is also described as able to do practical tasks like verify identity, issue refunds, book appointments, and hand off to a human when needed. The article is interesting because it reveals how the company is trying to make voice agents feel more usable for real customer conversations. As of 2026-06-04, the claims are worth reviewing as product positioning, but they are still vendor assertions rather than independent evidence.

## Key insights

- The article’s core technical claim is architectural: separate real-time speech handling from answer generation to reduce latency in voice interactions.
- Apex Flash is positioned as the enabling model for low-latency voice, but the evidence provided is the vendor’s own description of training and tuning.
- Fin Voice 2 is framed as an operational system, not just a chat demo, because it is said to handle identity checks, refunds, appointments, and proactive follow-up calls.
- Human handoff is presented as context-preserving, which matters more than raw automation if the system cannot fully resolve a call.
- The strongest product differentiator in the article is control and observability: detailed insights, recommendations, and self-serve management without professional services.

## Derived knowledge pages

- [[foundation-models/apex-flash]]
- [[industry-trends/voice-agents-shift-toward-workflow-completion]]
- [[tools/fin-voice-2]]
- [[topics/agent-runtime-architecture-for-voice]]
- [[topics/voice-agents-shift-toward-workflow-completion]]

## Why it matters

The piece is useful because it compresses a concrete product pattern for voice agents: use a low-latency model, split real-time processing from response generation, and add guardrails for confirmations, handoff, and external actions. That architecture is more durable than the marketing language around “natural” conversation, because it points to the engineering problem the vendor is trying to solve. The article also highlights that product usefulness in voice depends on more than transcription quality; it depends on latency, turn-taking, action execution, and recovery when the agent is uncertain. The emphasis on detailed analytics and one-click recommendations suggests that operability and tuning are part of the product, not an afterthought. But the article does not provide independent benchmarks, failure rates, or economic data, so the practical significance is still limited to the vendor’s claims. As of 2026-06-04, this is actionable mainly as a product-design reference and a signal to evaluate voice-agent demos skeptically rather than as proof that the stated performance is generally achieved. For customer support and phone automation, the article suggests a plausible direction, but it does not establish reliability at scale or across diverse call types.

## Limitations / open questions

The article offers no third-party evaluation, benchmark methodology, or comparison set, so claims about being “fastest,” “most natural,” or delivering higher resolution and satisfaction are unverified. It does not explain failure modes, latency numbers, cost per call, model size, or how the system behaves under noisy audio, accents, interruptions, or long multi-turn tasks. The description of training on millions of customer experience interactions raises unanswered questions about data provenance, consent, privacy, and retention. It is also unclear how robust the handoff flow is when the agent cannot resolve a request, and whether the preserved context is sufficient for a human to continue efficiently. The operational burden of maintaining policies, integrations, and quality controls across many customers is not discussed.

## Contradictions / unverified claims

The article contrasts its live demo with competitors’ “fabricated demos,” but that is a promotional claim rather than substantiated evidence. It presents a familiar vendor pattern of asserting broad capability from a demo and internal metrics without publishing the test conditions. The claim that voice agents are not generally in the wild because the technology has not been ready is plausible in a narrow sense, but it is too sweeping to verify from this source alone. The strongest skepticism is around the performance superlatives and customer-outcome claims, which are exactly the sort of claims that need external validation.

## Source metadata

- Canonical URL: https://www.intercom.com/blog/playing-a-different-game/
- Raw markdown: `raw/readwise/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx.md`
- Raw HTML: `raw/readwise/playing-a-different-game-01kt9zfvk8krrb2yv7mb50hywx.html`

## Full source text

---
readwise_id: "01kt9zfvk8krrb2yv7mb50hywx"
title: "Playing a different game"
author: "Eoghan McCabe"
publication: "The Intercom Blog"
source_url: "https://www.intercom.com/blog/playing-a-different-game/"
category: "rss"
location: "archive"
published_date: "2026-06-04"
saved_at: "2026-06-04T18:49:16.720000+00:00"
updated_at: "2026-06-05T06:52:17.090936+00:00"
tags: ["processed"]
---

Announcing Fin Voice 2, a major upgrade to Fin Voice with over 20 new features, and our first product built on Apex Flash.
