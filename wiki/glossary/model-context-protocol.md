---
title: Model Context Protocol
slug: model-context-protocol
entity_id: glossary:model-context-protocol
category: glossary
tags:
- ai-engineering
- runtime-architecture
first_seen: '2026-01-16'
last_seen: '2026-04-23'
source_count: 2
evidence_count: 8
source_ids:
- obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk
- the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b
value_level: high
confidence: 0.88
synthesis_state: stage1-placeholder
---

# Model Context Protocol

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A protocol for connecting AI agents to external tools and resources through a structured, typed interface. It is designed to make available tools discoverable, permissioned, and easier to integrate across clients and servers.

## Related Terms

- Agentic Workflows

## Relevance Note

This is a durable concept for agent tooling because it shapes how assistants discover and invoke external capabilities. It matters in conversational AI and service automation when multiple systems, permissions, and tool schemas must be exposed in a controlled way.

## Evidence / supporting sources

### Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault. (2026-01-16)

- Model Context Protocol is useful when you want different AI clients to plug into the same tool or data source without custom integrations for each one. In practice, it acts like a common adapter layer between models and the rest of a software stack. That makes it easier to build reusable agent workflows, especially when the same tool needs to work across multiple products or runtimes. It is especially relevant when teams want composable systems rather than a single vendor app that owns everything. (`a7cd2bae53d5` · neutral · extended_explanation; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- A standard for connecting AI systems to external tools and data sources through a shared interface. It lets applications expose capabilities in a way that models or agents can discover and use. (`eef58ab6b769` · neutral · proposed_definition; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- This matters for AI engineering because shared tool interfaces reduce integration duplication and make agent systems more portable across clients. It is especially relevant for conversational systems and workflow automation that need to call many tools reliably. (`91f9df553a6f` · neutral · relevance_note; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- "Skills (and the previously buzzy MCP, Model Context Protocol) are open standards proposed by Anthropic." (`7d7846aca83e` · supporting · supporting_snippet; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])

### The Sequence Opinion #848: The Agent’s Hands: CLI or MCP? (2026-04-23)

- Model Context Protocol is a way to present tools to an AI system in a consistent format so the system can inspect what exists, understand how to call it, and respect access rules. Instead of treating each tool as an ad hoc special case, the protocol aims to make tool use more standardized. That can help when agents need to work across many systems, because the tool descriptions, inputs, and permissions travel with the interface. In practice, this matters when teams want model-driven workflows to be safer and easier to wire up than direct one-off integrations. (`1d21df16f52c` · neutral · extended_explanation; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])
- A protocol for connecting AI agents to external tools and resources through a structured, typed interface. It is designed to make available tools discoverable, permissioned, and easier to integrate across clients and servers. (`c30bd6e4933a` · neutral · proposed_definition; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])
- This is a durable concept for agent tooling because it shapes how assistants discover and invoke external capabilities. It matters in conversational AI and service automation when multiple systems, permissions, and tool schemas must be exposed in a controlled way. (`8b4a40fdc4c8` · neutral · relevance_note; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])
- MCP says: “Agents need structured, discoverable, typed tools. Give them a protocol, schemas, resources, prompts, permissions, and a client-server architecture.” (`a6449b9bb86f` · supporting · supporting_snippet; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Agentic Workflows

## Sources

- [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]]
- [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]]
