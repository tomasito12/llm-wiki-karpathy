---
title: Behind the scene of conversational ai agent
slug: behind-the-scene-of-conversational-ai-agent-01kqh0spkgqy5bvsgb7w50yb4h
category: source
tags:
- agent-systems
- ai-engineering
- context-engineering
- enterprise-ai
- human-ai-workflows
- orchestration
- retrieval-systems
- workflow-design
- workflow-restructuring
source_id: behind-the-scene-of-conversational-ai-agent-01kqh0spkgqy5bvsgb7w50yb4h
author: Yezi Li
publication: Medium
published_date: '2025-11-15'
assessed_as_of: '2025-11-15'
ingested_at: '2026-06-09T16:53:39.011022+00:00'
canonical_url: https://medium.com/@yezi.li_jla/behind-the-scene-of-conversational-ai-agent-ae6fb6e5f57c
content_sha256: c5f9cdf70e839fb22ef42d058abbe9d0cee364054c12721a7ff3128a4cb8519e
derived_topics:
- topics/agent-workflow-vs-workflow-orchestration.md
- topics/rag-as-grounded-retrieval.md
derived_trends:
- industry-trends/ai-products-shift-from-demos-to-grounded-workflows.md
derived_pages:
- industry-trends/ai-products-shift-from-demos-to-grounded-workflows.md
- topics/agent-workflow-vs-workflow-orchestration.md
- topics/rag-as-grounded-retrieval.md
---

# Behind the scene of conversational ai agent

This article is about what makes a conversational AI agent different from a normal workflow. The core idea is simple: a workflow follows fixed steps, while an agent can choose actions based on context and feedback. The author uses a practical example with emails, Slack, and calendar actions to make that idea concrete. It also explains RAG, which helps a model answer using the right source material instead of guessing. A final note introduces MCP as a way to connect the model to outside tools and APIs.

## Key insights

- The article’s simplest durable distinction is that workflows execute predefined paths, while agents decide their own sequence of tool use.
- The author frames agent behavior as a loop of context, action, and feedback rather than a single LLM call.
- The n8n example shows a human-in-the-loop approval step as part of the agent design, not an optional afterthought.
- RAG is presented as a grounding mechanism for reducing unsupported answers by retrieving from a vector database.
- MCP is described as a unified API layer for connecting external resources when the needed knowledge is not already in the database.

## Derived knowledge pages

- [[industry-trends/ai-products-shift-from-demos-to-grounded-workflows]]
- [[topics/agent-workflow-vs-workflow-orchestration]]
- [[topics/rag-as-grounded-retrieval]]

## Why it matters

The piece is useful as a vocabulary reset for builders who conflate workflows, agents, RAG, and function calling. Its main practical value is that it separates three architectural choices that are often mixed together: deterministic orchestration, autonomous tool selection, and retrieval-based grounding. The email-to-Slack-to-calendar example is concrete enough to show where human approval fits, which is helpful when designing agentic systems that should not act blindly. The RAG section reinforces a durable engineering point: if the model needs factual grounding, retrieval matters more than prompt polish. The MCP mention is brief, but it usefully places external API access in the same design space as tool use rather than treating it as a separate concept. The article is still mostly explanatory and does not compare approaches with benchmarks, failure rates, or cost tradeoffs, so its operational guidance is limited. Actionable as of 2025-11-15, but best treated as a conceptual overview and lightweight pattern sketch rather than a validated implementation guide. The service-automation angle is real in the email, Slack, and calendar example, but the post does not go deep on reliability, permissions, or review workflows.

## Limitations / open questions

The post does not provide benchmarks, latency/cost analysis, security controls, or failure-mode evaluation for the proposed agent flow. The RAG explanation is high level and does not discuss retrieval quality, chunking strategy, reranking, or how to handle stale or conflicting sources. The MCP discussion is only a brief mention, so it leaves open how tool schemas, auth, and governance should be managed in practice. The n8n example is illustrative but not enough to show whether the workflow is robust under real email volume, ambiguous intent, or calendar conflicts. The article also does not distinguish clearly between a chatbot with tools and a true autonomous agent beyond the conceptual framing.

## Contradictions / unverified claims

The post simplifies agents into three traits, which is useful pedagogically but compresses a more complex design space. It also treats RAG as the main antidote to hallucination, which is directionally right but incomplete because retrieval can still surface wrong, incomplete, or poorly ranked evidence. The example suggests an agent can safely summarize emails, infer event intent, and act on a calendar with modest human review, but the article does not show safeguards for mistakes, privacy, or permission boundaries. The MCP claim is stated broadly as a unified API layer, but the piece does not substantiate that claim with a concrete integration example or comparison to existing tool-calling patterns.

## Source metadata

- Canonical URL: https://medium.com/@yezi.li_jla/behind-the-scene-of-conversational-ai-agent-ae6fb6e5f57c
- Raw markdown: `raw/readwise/behind-the-scene-of-conversational-ai-agent-01kqh0spkgqy5bvsgb7w50yb4h.md`
- Raw HTML: `raw/readwise/behind-the-scene-of-conversational-ai-agent-01kqh0spkgqy5bvsgb7w50yb4h.html`
