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
confidence: 0.8742857142857142
synthesis_state: stage1-placeholder
---

# Model Context Protocol

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Model Context Protocol (MCP) is a protocol for connecting AI applications and agents to external tools and data sources through a standardized interface. It is used to define structured tool access, authentication boundaries, and interoperable integrations between models and systems.

## Related Terms

- Passkey
- Agentic Workflows
- Harness

## Relevance Note

MCP is important for agentic systems because it creates a standard integration boundary for tools, retrieval, and governed access. That makes it a recurring building block for conversational AI, support automation, and internal agents that need controlled action surfaces.

## Evidence / supporting sources

### Give Your AI Unlimited Updated Context (2026-05-07)

- Model Context Protocol is useful when you want an AI assistant to work across many tools without building separate adapters each time. In practice, it gives the model a consistent way to discover what tools exist, what they do, and how to call them. That makes tool access more portable across apps and agents. It is especially relevant in workflows where the model needs structured access to files, services, or internal systems. (`083fe5c59821` · neutral · extended_explanation; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- A protocol for connecting an AI system to external tools and data sources through a standardized interface. It helps models access context and actions without custom one-off integrations for every tool. (`258a6f17078f` · neutral · proposed_definition; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- It matters because file-native and agentic workflows often need a stable way for models to discover tools and operating rules across environments. A standardized context interface reduces bespoke glue in orchestration-heavy systems. (`909cf405fd01` · neutral · relevance_note; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])
- If you’re using Codex, AGENTS.md works. Name it anything, as long as you point the AI to it at the start of every session. (`4f3f28bd28fe` · supporting · supporting_snippet; [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]])

### How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job (2026-05-02)

- MCP sits between a model and the software it needs to use. Instead of hard-coding one-off integrations, developers expose tools and resources through a standard protocol so different clients can discover and call them in a similar way. In agent systems, that matters because it can reduce integration fragmentation and make policy enforcement more uniform. The tradeoff is that structured tool catalogs can be expensive in context if everything is loaded at once, so implementation details like discovery and selective loading become important. (`079ed39b49cd` · neutral · extended_explanation; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Model Context Protocol (MCP) is a protocol for connecting AI systems to external tools, resources, and prompts in a structured, machine-readable way. It is designed to make tool access consistent across clients and servers while supporting governance, authorization, and auditability. (`f02f4cf87c0f` · neutral · proposed_definition; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- MCP matters in agent and automation stacks because it standardizes how models reach external systems without every team inventing a custom adapter. In service automation, the governance and auditability angle is especially useful when actions touch customer data, enterprise apps, or regulated workflows. (`e2470a035cc8` · neutral · relevance_note; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- “MCP (The Connective Tissue)
: The integration protocol that provides rich semantics, platform independence, and crucial enterprise features like OAuth, governance policies, and audit trails.” (`fd572fd76b06` · supporting · supporting_snippet; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])

### MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It) (2026-06-07)

- In practice, MCP acts like a shared adapter layer between an AI app and the systems it needs to use. A server wraps a real tool such as a database, ticketing system, or file store, and the client inside the AI app speaks the protocol to discover and invoke those capabilities. The main appeal is reducing integration duplication: one server can be reused across multiple AI hosts and models. The tradeoff is that the protocol adds its own security, deployment, and governance surface, so teams still need to manage trust, monitoring, and compatibility carefully. (`a53f03a3c094` · neutral · extended_explanation; [[sources/mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g|MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It)]])
- Model Context Protocol (MCP) is an open standard for connecting AI applications to external tools and data sources through a common client-server interface. It lets an AI host discover available tools, call them, and exchange structured context without building a custom integration for every model-tool pair. (`2640fcb36fa7` · neutral · proposed_definition; [[sources/mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g|MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It)]])
- MCP matters wherever teams want a shared tool layer across multiple AI apps, especially for agent systems, copilots, and service automation stacks. It is useful as a standard boundary, but production teams need to treat it as infrastructure with security and maintenance requirements, not just a convenience layer. (`ec5058194873` · neutral · relevance_note; [[sources/mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g|MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It)]])
- Released by Anthropic in November 2024, it’s an open standard that provides AI models with a universal way to communicate with external tools. You build an MCP server once, and any MCP-compatible AI can use it. (`fb2d27de01aa` · supporting · supporting_snippet; [[sources/mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g|MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It)]])

### Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault. (2026-01-16)

- Model Context Protocol is useful when you want different AI clients to plug into the same tool or data source without custom integrations for each one. In practice, it acts like a common adapter layer between models and the rest of a software stack. That makes it easier to build reusable agent workflows, especially when the same tool needs to work across multiple products or runtimes. It is especially relevant when teams want composable systems rather than a single vendor app that owns everything. (`a7cd2bae53d5` · neutral · extended_explanation; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- A standard for connecting AI systems to external tools and data sources through a shared interface. It lets applications expose capabilities in a way that models or agents can discover and use. (`eef58ab6b769` · neutral · proposed_definition; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- This matters for AI engineering because shared tool interfaces reduce integration duplication and make agent systems more portable across clients. It is especially relevant for conversational systems and workflow automation that need to call many tools reliably. (`91f9df553a6f` · neutral · relevance_note; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])
- "Skills (and the previously buzzy MCP, Model Context Protocol) are open standards proposed by Anthropic." (`7d7846aca83e` · supporting · supporting_snippet; [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]])

### Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here (2026-05-15)

- MCP matters because it reduces integration friction between models and the software they need to act on. Instead of wiring every agent to every app separately, a developer can expose a standard server and let compatible clients connect to it. In practice, that can make personal or enterprise knowledge systems more reusable, more portable, and easier to govern. It is especially relevant when AI needs access to local files, note vaults, or internal systems with a stable contract. (`2bcfa059521b` · neutral · extended_explanation; [[sources/obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7|Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here]])
- Model Context Protocol (MCP) is an open standard for connecting AI applications to external tools and data sources through a common interface. It lets an AI system discover and use capabilities without custom one-off integrations for each tool. (`593846bf131e` · neutral · proposed_definition; [[sources/obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7|Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here]])
- Useful wherever teams want multiple AI tools to share a consistent integration layer with local or enterprise systems. It is especially relevant to agent workflows, tool governance, and service automation because one protocol can expose structured context without bespoke connectors for every model client. (`e18718bdea2f` · neutral · relevance_note; [[sources/obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7|Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here]])
- “It also includes a Command Line Interface (CLI) (osk-cli) for scripting and a Model Context Protocol (MCP) server so any AI tool (like Claude Code, Claude Cowork, Codex, etc) can talk to your vault directly with full understanding about the whole system.” (`33b8d6676a34` · supporting · supporting_snippet; [[sources/obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7|Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here]])

### Technology Radar (2026-04-13)

- MCP gives agents a common way to discover and call tools without bespoke integrations for every vendor or app. That standardization is useful when teams want governed access to data, OAuth boundaries, or multi-tenant workflows. The tradeoff is abstraction overhead: not every API benefits from another protocol layer, and a simpler CLI or direct API may be better for some tasks. MCP is most valuable when interoperability and governance matter more than raw simplicity. (`4b9852541016` · neutral · extended_explanation; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- Model Context Protocol (MCP) is a protocol for connecting AI applications and agents to external tools and data sources through a standardized interface. It is used to define structured tool access, authentication boundaries, and interoperable integrations between models and systems. (`da87d4daeb20` · neutral · proposed_definition; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- MCP is important for agentic systems because it creates a standard integration boundary for tools, retrieval, and governed access. That makes it a recurring building block for conversational AI, support automation, and internal agents that need controlled action surfaces. (`170611ae01c9` · neutral · relevance_note; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])
- MCP adds real value for structured tool contracts, OAuth-based authentication boundaries and governed multi-tenant access. It also introduces what Justin Poehnelt calls an "abstraction tax": every protocol layer between an agent and an API loses fidelity, and for complex APIs those losses compound. (`f6a0e630578c` · supporting · supporting_snippet; [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]])

### The Sequence Opinion #848: The Agent’s Hands: CLI or MCP? (2026-04-23)

- Model Context Protocol is a way to present tools to an AI system in a consistent format so the system can inspect what exists, understand how to call it, and respect access rules. Instead of treating each tool as an ad hoc special case, the protocol aims to make tool use more standardized. That can help when agents need to work across many systems, because the tool descriptions, inputs, and permissions travel with the interface. In practice, this matters when teams want model-driven workflows to be safer and easier to wire up than direct one-off integrations. (`1d21df16f52c` · neutral · extended_explanation; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])
- A protocol for connecting AI agents to external tools and resources through a structured, typed interface. It is designed to make available tools discoverable, permissioned, and easier to integrate across clients and servers. (`c30bd6e4933a` · neutral · proposed_definition; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])
- This is a durable concept for agent tooling because it shapes how assistants discover and invoke external capabilities. It matters in conversational AI and service automation when multiple systems, permissions, and tool schemas must be exposed in a controlled way. (`8b4a40fdc4c8` · neutral · relevance_note; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])
- MCP says: “Agents need structured, discoverable, typed tools. Give them a protocol, schemas, resources, prompts, permissions, and a client-server architecture.” (`a6449b9bb86f` · supporting · supporting_snippet; [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Agentic Workflows
- Harness
- Passkey

## Sources

- [[sources/give-your-ai-unlimited-updated-context-01krkap6426ped2hk2anmke10k|Give Your AI Unlimited Updated Context]]
- [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]]
- [[sources/mcp-is-dead-why-this-protocol-breaks-in-production-and-how-to-fix-it-01ktkysg8zyd6yfnw3dgy7738g|MCP Is Dead: Why This Protocol Breaks in Production(And How to Fix It)]]
- [[sources/obsidian-s-official-skills-are-here-it-s-time-to-let-ai-plug-into-your-local-vault-01kqfzks8n4e91tn6m1vs562sk|Obsidian’s Official Skills Are Here! It’s time to let AI plug into your local Vault.]]
- [[sources/obsidian-starter-kit-v4-is-live-the-ai-native-release-is-here-01kts4g66e8xermwccbvrd4mz7|Obsidian Starter Kit v4 Is Live: The AI-Native Release Is Here]]
- [[sources/technology-radar-01krc5f8a8a6x35ke2kdjn5d9w|Technology Radar]]
- [[sources/the-sequence-opinion-848-the-agent-s-hands-cli-or-mcp-01kpx19wnknk0ms9zpszqvv62b|The Sequence Opinion #848: The Agent’s Hands: CLI or MCP?]]
