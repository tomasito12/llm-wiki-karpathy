---
title: '95% of Devs Are Using AI Agents Completely Wrong: A Hermes Guide'
slug: 95-of-devs-are-using-ai-agents-completely-wrong-a-hermes-guide-01krbnbbbpznzgbeefqnzapsz3
category: source
source_id: 95-of-devs-are-using-ai-agents-completely-wrong-a-hermes-guide-01krbnbbbpznzgbeefqnzapsz3
author: Shashwat
publication: Medium
published_date: '2026-05-06'
assessed_as_of: '2026-05-06'
ingested_at: '2026-06-07T19:56:26.419643+00:00'
canonical_url: https://medium.com/ai-in-plain-english/95-of-devs-are-using-ai-agents-completely-wrong-a-hermes-guide-905df737a49d
content_sha256: 423c3805ab914510c37f6b44c518e4aec30331894740dbbca8d36206dd6c27ae
---

# 95% of Devs Are Using AI Agents Completely Wrong: A Hermes Guide

This article says most people use Hermes like a smarter chat box, but its real value is in persistent memory, safe experimentation, and automation. Hermes is presented as an agent that can keep project context, remember user preferences, branch a session, roll back bad file changes, and accept steering commands while work is in progress. It can also switch models, route background work to cheaper models, and run the same agent across multiple chat platforms. The author’s main point is simple: if you only type prompts and close the tab, you are ignoring the parts that make the system useful. The article is interesting as a practical feature tour, but it is mostly promotional and does not prove that these features outperform alternatives.

## Key insights

- Persistent identity and memory files are positioned as the main fix for repeated re-prompting and context loss across sessions.
- Session branching and filesystem rollback are the most operationally useful safety features because they let you test risky changes without losing the main thread.
- Mid-flight steering and queued instructions are designed for long-running agent runs where requirements change after execution starts.
- Model swapping plus auxiliary routing suggests a cost-control pattern: reserve frontier models for core reasoning and offload compression or summarization to cheaper models.
- Cron jobs, webhook subscriptions, and custom slash commands turn the agent from a chat tool into a reusable workflow runner.

## Derived knowledge pages

No derived knowledge pages captured.

## Why it matters

The piece is useful because it compresses a practical agent-operating model into a small set of durable behaviors: persistent identity, persistent memory, reversible execution, live steering, model routing, and workflow automation. For AI engineers, the main value is not the marketing claim that Hermes is powerful, but the concrete reminder that agent quality often depends on how state, recovery, and routing are configured rather than on prompt quality alone. The article also surfaces a cost pattern worth remembering: background tasks such as summarization and title generation can be routed away from the most expensive model without changing the main session state. The session-forking and rollback features are especially relevant for long-lived development workflows because they reduce the risk of corrupting a working branch of agent activity. The cross-platform layer and custom commands matter because they imply the same agent state can be reused across terminal and messaging surfaces instead of rebuilt in each channel. The claims about eliminating Zapier and pushing webhook payloads into direct agent workflows are interesting, but the evidence in the article is purely descriptive. As of 2026-05-06, the article is actionable as a feature checklist for Hermes users, but it should be read as a vendor-style guide rather than a verified performance benchmark.

## Limitations / open questions

The article provides no benchmarks, latency numbers, cost comparisons, or failure rates for the listed features. It does not explain how Hermes handles security, access control, secret storage, auditability, or data retention across 17 platforms. The memory claim relies on FTS5 and an LLM summarizer, but the article does not show retrieval quality, update behavior, or how stale memory is corrected. Rollback is described as a filesystem checkpoint, but the boundaries of that snapshotting system are not specified. The webhook and cron examples are plausible, but the article does not prove reliability, idempotency, or error handling for production workflows. The feature list is broad enough that the practical complexity of operating all of it may offset some of the promised leverage.

## Contradictions / unverified claims

Several claims are rhetorically strong without independent evidence, especially the opening claim that 95% of developers are using agents completely wrong. The framing that Hermes can replace tools like Zapier and support 17 platforms is impressive on paper, but the article does not show a comparison against existing automation stacks or the operational tradeoffs of consolidation. The promise that persistent memory and model routing solve the main productivity problem may be overstated; poor prompt quality, weak task decomposition, and brittle workflows can still dominate outcomes. The article also assumes that users want a highly stateful, command-heavy agent rather than a simpler tool with fewer modes of failure. Overall, the skepticism level should remain moderate: the features are plausible and operationally relevant, but the evidence is promotional and anecdotal rather than validated.

## Source metadata

- Canonical URL: https://medium.com/ai-in-plain-english/95-of-devs-are-using-ai-agents-completely-wrong-a-hermes-guide-905df737a49d
- Raw markdown: `raw/readwise/95-of-devs-are-using-ai-agents-completely-wrong-a-hermes-guide-01krbnbbbpznzgbeefqnzapsz3.md`
- Raw HTML: `raw/readwise/95-of-devs-are-using-ai-agents-completely-wrong-a-hermes-guide-01krbnbbbpznzgbeefqnzapsz3.html`
