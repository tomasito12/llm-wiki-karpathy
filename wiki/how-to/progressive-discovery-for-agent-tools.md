---
title: Progressive Discovery for Agent Tools
slug: progressive-discovery-for-agent-tools
entity_id: how_to:progressive-discovery-for-agent-tools
category: how-to
tags:
- agent-orchestration
- context-engineering
- runtime-architecture
first_seen: '2026-05-02'
last_seen: '2026-05-02'
source_count: 1
evidence_count: 12
source_ids:
- how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2
value_level: high
confidence: 0.93
synthesis_state: stage1-placeholder
---

# Progressive Discovery for Agent Tools

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
When an agent has access to many tools, loading everything into the context window can waste space and slow the system down. Progressive discovery is a way to avoid that by showing the model only the tools it asks for, instead of sending the full catalog up front. This helps when the same agent must work across several applications or services. It is especially useful when tool schemas are large or when most tools are irrelevant to a given task.

## Caveats

This pattern adds a search step, so poorly designed discovery can make tool selection harder rather than easier. It also depends on having good tool metadata and naming, or the model may fail to find the right tool. The source gives a claimed reduction in context usage but does not provide a benchmark methodology.

## Implementation Steps

- Expose a tool_search capability or similar discovery endpoint.
- Index tools with descriptive names and parameter descriptions.
- Load only the short search results into context first.
- Fetch the full schema only after the model picks a tool.
- Measure context usage before and after discovery to verify the savings.

## Prerequisites

- A tool catalog with searchable metadata.
- A runtime that can load tool schemas on demand.
- Consistent naming and parameter descriptions across tools.

## Evidence / supporting sources

### How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job (2026-05-02)

- Start with a searchable tool catalog instead of preloading every tool schema. Let the model look up tools by name, intent, or category when it needs them. Keep the initial context small, and only fetch the full schema for the selected tool. This reduces token use and makes the agent more scalable for large enterprise toolsets. (`090f0164e147` · neutral · answer_summary; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Expose a tool_search capability or similar discovery endpoint. (`882da6bbacbf` · neutral · implementation_steps[0]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Index tools with descriptive names and parameter descriptions. (`4a64854b2185` · neutral · implementation_steps[1]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Load only the short search results into context first. (`43d4a112328f` · neutral · implementation_steps[2]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Fetch the full schema only after the model picks a tool. (`5ad62e024262` · neutral · implementation_steps[3]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Measure context usage before and after discovery to verify the savings. (`1f2a4948ed44` · neutral · implementation_steps[4]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- A tool catalog with searchable metadata. (`d16755a60c28` · neutral · prerequisites[0]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- A runtime that can load tool schemas on demand. (`01e5ccf47e33` · neutral · prerequisites[1]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- Consistent naming and parameter descriptions across tools. (`7c780a70adfe` · neutral · prerequisites[2]; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- When an agent has access to many tools, loading everything into the context window can waste space and slow the system down. Progressive discovery is a way to avoid that by showing the model only the tools it asks for, instead of sending the full catalog up front. This helps when the same agent must work across several applications or services. It is especially useful when tool schemas are large or when most tools are irrelevant to a given task. (`33700e97c010` · neutral · what_and_problem; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- “Progressive discovery reduces context bloat by loading tools on demand via tool search. By providing a tool_search capability, the model can look up tools dynamically. This pattern can reduce context usage by a factor of 5.” (`fd5298e4742b` · supporting · supporting_snippet; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])
- This pattern adds a search step, so poorly designed discovery can make tool selection harder rather than easier. It also depends on having good tool metadata and naming, or the model may fail to find the right tool. The source gives a claimed reduction in context usage but does not provide a benchmark methodology. (`eaf5877598c6` · uncertainty · caveats; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])

## Contradictions / tensions

- This pattern adds a search step, so poorly designed discovery can make tool selection harder rather than easier. It also depends on having good tool metadata and naming, or the model may fail to find the right tool. The source gives a claimed reduction in context usage but does not provide a benchmark methodology. (uncertainty; [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]])

## Related pages

- [[how-to/lazy-loading-tools|Lazy-Loading Tools]]
- [[how-to/context-compaction|Context Compaction]]

## Sources

- [[sources/how-to-build-production-ready-ai-agents-mcp-cli-and-skills-the-right-tool-for-the-right-job-01kr4347xhzg1papsh9y4v36a2|How to Build Production-Ready AI Agents: MCP, CLI, and Skills — the Right Tool for the Right Job]]
