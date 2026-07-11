---
title: Learning on the Shop floor
slug: learning-on-the-shop-floor-01krv8e47g986qdzdmbcdny96n
category: source
source_id: learning-on-the-shop-floor-01krv8e47g986qdzdmbcdny96n
author: tobi lutke
publication: X (formerly Twitter)
published_date: '2026-05-09'
assessed_as_of: '2026-05-09'
ingested_at: '2026-06-06T21:59:18+00:00'
canonical_url: https://x.com/tobi/status/2053121182044451016/?rw_tt_thread=True
content_sha256: 8ca8f630d83aa0b7cf8a45a7bf215fa0bf8212d8fc2cb1af6982622ca1a00c5c
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
---

# Learning on the Shop floor

This is about using an AI agent as a shared coworker instead of a private assistant. Shopify built River inside Slack, where people can watch each other ask questions, debug problems, and teach the system company-specific knowledge. The interesting part is not just that River can write code or run tests, but that the public setup lets everyone learn from every interaction. The author says this makes the whole company feel like an apprenticeship workshop, where newcomers learn by seeing experts work. It also helps River get better because people can correct it in the open. The main idea is simple: visibility turns AI work into organizational learning.

## Key insights

- A public Slack-based agent can turn routine AI use into a shared apprenticeship instead of a private productivity boost.
- Refusing direct messages is not just a policy choice; it is the mechanism that makes work searchable and teachable across the company.
- People can learn practical prompt patterns, debugging moves, and domain context by observing other teams’ interactions with the agent.
- The system can improve without model retraining when employees annotate failures and write down missing context for the agent.
- The article’s strongest claim is organizational, not model-level: visibility compounds knowledge if the work happens in open channels.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful because it identifies a concrete product and workflow choice that changes what AI use teaches the organization. River is not presented as a smarter model; it is presented as a social interface that makes code reading, test running, pull requests, and data queries visible to everyone in Slack. That visibility creates a durable knowledge trail: senior developers’ requests become templates, new hires can inspect prior threads, and team-specific instructions can be attached to the channels where the work happens. The article also gives a plausible mechanism for agent improvement that does not depend on retraining: people notice where River gets stuck, document missing knowledge, and feed that back into the shared workflow. The practical lesson is that if an organization wants AI to raise collective skill rather than isolate it, the default should be public-by-design workspaces with searchable interactions. The evidence is still anecdotal and comes from one company, so the generality is limited. As of 2026-05-09, this is a useful operating pattern to consider for internal engineering workflows, but it is best treated as a case study rather than proof that open-agent work is universally superior.

## Limitations / open questions

This is a single company case study with no controlled comparison against private assistants, so the reported gains may depend on Shopify’s culture, Slack usage, or engineering structure. The post gives usage counts and a merge-rate change, but not a rigorous evaluation of code quality, defect rates, reviewer load, or long-term maintenance costs. It is unclear how much of River’s usefulness comes from its public design versus Shopify’s ability to encode strong team-specific instructions and norms. The article does not address privacy, sensitive code exposure, compliance boundaries, or situations where open channels are inappropriate. It also leaves open whether the apprenticeship effect persists as teams scale, channels proliferate, or novelty fades.

## Contradictions / unverified claims

The post makes a strong case for public visibility, but it is still partly a narrative of organizational taste and belief. The rise in merge rate is interesting, yet without a baseline and controls it does not prove that the open-channel design caused the improvement. The claim that the company did not retrain a model but still improved River may understate the importance of the custom instructions, memory, and human curation that shaped the system. The broader argument against private AI windows is compelling in this context, but it should not be assumed to generalize to all work, especially sensitive or regulated tasks.

## Source metadata

- Canonical URL: https://x.com/tobi/status/2053121182044451016/?rw_tt_thread=True
- Raw markdown: `raw/readwise/learning-on-the-shop-floor-01krv8e47g986qdzdmbcdny96n.md`
- Raw HTML: `raw/readwise/learning-on-the-shop-floor-01krv8e47g986qdzdmbcdny96n.html`

## Full source text

---
readwise_id: "01krv8e47g986qdzdmbcdny96n"
title: "Learning on the Shop floor"
author: "tobi lutke"
publication: "X (formerly Twitter)"
source_url: "https://x.com/tobi/status/2053121182044451016/?rw_tt_thread=True"
category: "tweet"
location: "archive"
published_date: "2026-05-09"
saved_at: "2026-05-17T15:21:21.904000+00:00"
updated_at: "2026-05-18T14:31:29.292501+00:00"
tags: ["processed"]
---

Tobi Lutke shares how Shopify built an AI agent called River that helps employees work and learn together publicly on Slack. River’s open and shared use creates a teaching workshop where everyone watches, learns, and improves from each other’s work. This approach speeds up the company by making knowledge visible and spreading skills, not replacing people but making everyone an apprentice.
