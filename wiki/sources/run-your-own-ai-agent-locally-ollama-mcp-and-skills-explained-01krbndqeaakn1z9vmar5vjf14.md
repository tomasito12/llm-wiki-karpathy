---
title: 'Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained'
slug: run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14
category: source
tags:
- agent-systems
- ai-engineering
- inference-systems
- prompt-engineering
source_id: run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14
author: Jes Fink-Jensen
publication: Medium
published_date: '2026-05-05'
assessed_as_of: '2026-05-05'
ingested_at: '2026-05-17T20:06:17.267395+00:00'
canonical_url: https://medium.com/generative-ai/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-a913fe46e938
content_sha256: 30ab954001bdfba64fcc36992a7585a7cb8508c3aac4a50e332fd8a7b6dcdd8a
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_how_to:
- how-to/local-coding-model-setup.md
derived_models:
- foundation-models/qwen-3-5-9b.md
derived_tools:
- tools/ollama.md
derived_topics:
- topics/agentic-workflows.md
- topics/context-engineering.md
derived_pages:
- foundation-models/qwen-3-5-9b.md
- how-to/local-coding-model-setup.md
- tools/ollama.md
- topics/agentic-workflows.md
- topics/context-engineering.md
---

# Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained

This piece explains how to build a small AI helper that runs entirely on one laptop. It uses a local model instead of a cloud service, so there are no API keys to manage and no paid accounts to set up. The helper checks who is on call, asks whether that person’s country has a public holiday, and then lists open important issues if backup coverage may be needed. To do that, the author splits the system into three parts: a model runtime, a pair of small data services, and a skill file that tells the model what steps to follow. One data service looks up public holidays from a free website, and the other reads a local database of engineers and issues. A short Python orchestrator connects everything, sends the user’s question to the model, and passes tool requests back and forth. The article also shows how to test the pieces one by one before running the full system. The main idea is that each layer is easy to inspect and replace, so the same pattern could be reused for other small agent workflows. As of 2026-05-05, it reads like a practical template for local agent builds rather than a claim about production-scale AI deployment.

## Key insights

- A single JSON config can act as the control plane for a local agent stack, reducing hardcoded orchestration logic.
- A skill file can function like a program: it sets the procedure, tool order, and output constraints the model should follow.
- MCP servers work well as a library layer when the model only needs tool names, descriptions, and schemas, not function bodies.
- Keeping one server pure-local and one server as a thin wrapper around an external API makes the boundaries between state and network I/O easy to inspect.
- A bounded tool-call loop with stderr tracing is a simple but useful debugging pattern for agent runs.

## Derived knowledge pages

- [[foundation-models/qwen-3-5-9b]]
- [[how-to/local-coding-model-setup]]
- [[tools/ollama]]
- [[topics/agentic-workflows]]
- [[topics/context-engineering]]

## Why it matters

The main value here is architectural, not product-specific: it demonstrates a clean separation between model runtime, tool surface, procedural skill, and orchestration code. That separation makes local agent systems easier to reason about, swap, and test than ad hoc prompt-and-tool setups. The article also gives a concrete example of how a skill can constrain tool use and output format without embedding business logic in the model prompt alone. Its most durable lesson is that an agent workflow can be treated like software with visible interfaces rather than as a single opaque prompt. The specific choices here—Ollama, MCP, SQLite, and a Markdown procedure—are practical because they keep the whole stack inspectable and runnable on one machine. The piece does not show production-scale reliability, security hardening, or throughput testing, so its stakes are limited to local or prototype-grade builds. For service automation, the closing example is directly relevant because the workflow turns a holiday check plus internal issue lookup into a terse escalation or coverage message. As of 2026-05-05, this is best treated as a reusable local pattern to adopt and adapt, not as evidence of mature operational deployment.

## Limitations / open questions

The article is a build walkthrough, not a production case study, so it does not provide latency, cost, failure-rate, or user-satisfaction data. The model choice is a local 9B class model, but there is no evaluation of tool-call reliability beyond the worked example. The public-holidays dependency is a single external API, so availability and rate-limit behavior are not explored. Security, authentication, and data governance are mostly absent because the example is intentionally local and simple. It also does not test the stack under concurrent users, changing schemas, or malformed tool outputs.

## Contradictions / unverified claims

The article presents the stack as a practical template, but the evidence is mainly a single scripted scenario and personal experimentation. Claims about replaceability and inspectability are plausible, yet they are not backed by stress tests or maintenance data. The analogy between skills, MCPs, and programming is useful, but it can oversimplify how brittle real tool-use orchestration can become once the tool set grows. The end-to-end demo succeeds, but that does not establish robustness for repeated operational use.

## Source metadata

- Canonical URL: https://medium.com/generative-ai/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-a913fe46e938
- Raw markdown: `raw/readwise/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14.md`
- Raw HTML: `raw/readwise/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-01krbndqeaakn1z9vmar5vjf14.html`

## Full source text

---
readwise_id: "01krbndqeaakn1z9vmar5vjf14"
title: "Run Your Own AI Agent Locally: Ollama, MCP, and Skills Explained"
author: "Jes Fink-Jensen"
publication: "Medium"
source_url: "https://medium.com/generative-ai/run-your-own-ai-agent-locally-ollama-mcp-and-skills-explained-a913fe46e938"
category: "article"
location: "archive"
published_date: "2026-05-05"
saved_at: "2026-05-11T14:00:29.386000+00:00"
updated_at: "2026-05-12T09:43:33.508740+00:00"
tags: ["processed"]
---

A working implementation of the LLM-as-language, MCP-as-library analogy — every layer visible and replaceable.
