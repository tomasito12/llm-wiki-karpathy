---
title: Model Context Protocol
slug: model-context-protocol
entity_id: glossary:model-context-protocol
category: glossary
tags:
- agent-systems
- ai-engineering
- context-engineering
- governance
- orchestration
- runtime-architecture
- tool-use
first_seen: '2026-01-16'
last_seen: '2026-06-07'
source_count: 7
evidence_count: 28
source_ids:
- give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k
- how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2
- mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g
- obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk
- obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7
- technology-radar-01krc5f8a8a6x35ke2kdjn5d9w
- the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b
value_level: high
confidence: 0.874286
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 530d8261b70ffbf5
current_input_hash: 530d8261b70ffbf5
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-08T19:30:38Z'
---

# Model Context Protocol

## Executive synthesis

Model Context Protocol (MCP) is a standardized way for AI systems to discover and use external tools and data sources through a common client-server interface. Across the sources, it is presented as a reusable integration layer that reduces custom adapters, makes tool access more portable across clients, and helps with governed access, authentication boundaries, and auditability. The main caveat is that MCP is not free: it adds another abstraction layer, so teams still need to manage security, deployment, compatibility, and whether the protocol is worth the added complexity for a given use case.

## Context card

- **Use this page when:** Use this page when you need a quick definition of MCP and want to know why it matters in agent/tool integration, especially for reusable, governed, or portable tool access.
- **Best for questions about:** What Model Context Protocol is in plain English, Why people use MCP instead of custom adapters, How MCP fits into agent/tool orchestration, Where MCP helps with governance, access control, and audit trails, When MCP is a better fit than direct API calls or a CLI
- **Not enough for:** Implementation details or wire-level protocol specifics, How to build an MCP server or client step by step, Whether MCP is the best choice for a specific production system without more context, Security design beyond the general need for trust, monitoring, and compatibility
- **Strongest sources:** MCP Is Dead: Why This Protocol Breaks in Production (And How to Fix It), Technology Radar, How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job, Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here, The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?
- **Related tags:** agent-systems, ai-engineering, context-engineering, governance, orchestration, runtime-architecture, tool-use

## What to remember

- MCP is a standard interface for AI-to-tool integration, not just a single app feature.
- It reduces bespoke integrations by letting one server serve multiple compatible AI clients.
- It is most useful when tool discovery, permissions, governance, and portability matter.
- It adds complexity, so it is a tradeoff, not an automatic upgrade.
- For simple tasks, a CLI or direct API may still be the better choice.

## Consensus

- MCP is a standardized protocol for connecting AI applications or agents to external tools, data sources, resources, and prompts through a common interface.
- Its main value is reducing one-off integrations: one MCP server or tool exposure can be reused across compatible clients and models.
- MCP gives models a structured way to discover what tools exist, what they do, how to call them, and what access rules apply.
- It is especially relevant for agent systems, workflow automation, knowledge systems, and other settings where many tools or systems need to be connected consistently.
- The protocol is often framed as helpful for governance, authentication boundaries, auditability, and controlled access in enterprise or multi-tenant environments.

## Tensions / open questions

- Some sources describe MCP broadly as connecting AI to tools, data, and prompts; others focus more narrowly on tools and data sources.
- Several sources highlight enterprise/governance benefits, but others warn that the protocol introduces abstraction tax and operational burden.
- The sources agree MCP helps interoperability, but they do not agree that it should replace simpler approaches like direct APIs or CLI for all tasks.

## Evidence quality

- Overall evidence is strong on the basic definition and practical role of MCP; multiple sources converge on the same core description.
- Evidence is weaker on precise scope and framing details: some sources emphasize tools, others include resources, prompts, governance, or authentication boundaries.
- The sources are mostly secondary commentary rather than primary specification text, so this page should be treated as a synthesis of usage and interpretation.
- There is consistent caution that MCP adds abstraction and operational overhead, so benefits depend on the system and may not justify another protocol layer for simple APIs.

## Practical takeaway

Think of MCP as a shared adapter layer for AI tool use. Use it when you need reusable, discoverable, governed access across multiple clients or systems; skip it when a simpler CLI or direct API is enough.

## Evidence index

- Sources: 7
- Evidence items: 28
- Current input hash: `530d8261b70ffbf5`
- Cached input hash: `530d8261b70ffbf5`
- Last synthesized: 2026-07-08T19:30:38Z
- Synthesis status: `fresh`

## Related pages

- [[glossary/passkey|Passkey]]
- [[glossary/harness|Harness]]

## Sources

- [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]]
- [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]]
- [[sources/mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g|MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It)]]
- [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]]
- [[sources/obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7|Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here]]
- [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]]
- [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]]
