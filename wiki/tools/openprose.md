---
title: OpenProse
slug: openprose
entity_id: tool:openprose
category: tool
tags:
- agentic
- coding
- open-source
- workflow-automation
first_seen: '2026-06-04'
last_seen: '2026-06-04'
source_count: 1
evidence_count: 12
source_ids:
- how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f
value_level: high
confidence: 0.9
synthesis_state: stage1-placeholder
types:
- coding-agent
- workflow-automation
---

# OpenProse

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
OpenProse is an open-source agent skill and programming language for describing agent workflows in logical English, with `.prose.md` files as the source format. It is designed to let coding agents execute reusable, reviewable workflows rather than improvised chat sessions.

## Core Capabilities

- OpenProse turns a successful agent session into a reusable `.prose.md` program that can be reviewed and edited before execution.
- OpenProse supports isolated sub-agent sessions so intermediate work stays contained until declared outputs are carried forward.
- OpenProse can declare real tools or skills as dependencies, which matters when a workflow needs a specific capability to finish correctly.

## Integration Ecosystem

- The article says OpenProse can run in Claude Code, Codex, Hermes, or Pi, which makes it compatible with several coding-agent environments.
- The source mentions `npx skills add openprose/prose`, indicating a lightweight installation path through the Node package ecosystem.
- The workflow can also depend on ordinary executables on `PATH` or an MCP server, which broadens its operational surface beyond a single vendor product.

## Maturity signals

The source presents OpenProse as open source and easy to start with via an `npx` install flow, which suggests a developer-facing tool rather than an enterprise-mature platform. The article describes it as usable with several coding agents, but the evidence is still practitioner testimony rather than broad adoption data. As of 2026-06-04, the maturity signal is promising but still early and anecdotal.

## Related Tools

- Claude Code
- Codex
- OpenClaw

## Strengths

- Separates workflow intent from execution by using logical English contracts, which makes the resulting program easier for humans to review before an agent runs it.
- Runs each service in its own isolated sub-agent session, which helps keep scratch work and dead-end reasoning from polluting the main context.
- Leaves receipts under `runs/{run-id}/`, which gives operators an audit trail for what the agent actually did rather than what it claimed to do.
- Allows explicit dependencies on tools and skills, which is useful when a workflow needs a specific capability such as document editing or JSON parsing.
- Can be used across multiple coding-agent harnesses, so the workflow is not locked to one specific runtime.

## Weaknesses / limitations

The source is clear that OpenProse does not make the underlying model deterministic, so it improves repeatability without removing the need for judgment and verification. The agent still decides when to invoke tools, so determinism lives in the script or executable rather than in the orchestration layer. The article also suggests there is real overhead, and that not every prompt deserves to become a program.

## Evidence / supporting sources

### How OpenProse Makes AI Agent Behavior Repeatable (2026-06-04)

- The article says OpenProse can run in Claude Code, Codex, Hermes, or Pi, which makes it compatible with several coding-agent environments. (`7737a22b253e` · neutral · integration_ecosystem[0]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- The source mentions `npx skills add openprose/prose`, indicating a lightweight installation path through the Node package ecosystem. (`7198556cbb58` · neutral · integration_ecosystem[1]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- The workflow can also depend on ordinary executables on `PATH` or an MCP server, which broadens its operational surface beyond a single vendor product. (`e61336c28c2f` · neutral · integration_ecosystem[2]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- The source presents OpenProse as open source and easy to start with via an `npx` install flow, which suggests a developer-facing tool rather than an enterprise-mature platform. The article describes it as usable with several coding agents, but the evidence is still practitioner testimony rather than broad adoption data. As of 2026-06-04, the maturity signal is promising but still early and anecdotal. (`04397fffd7af` · neutral · maturity_signals; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- OpenProse fits best where teams want to capture a reliable agent workflow and rerun it across sessions or harnesses. It is especially relevant for coding-agent workflows that need reviewable contracts, isolated sub-agent work, and durable receipts. The practical value is less about raw capability and more about making agent output inspectable and reusable in a git-like way. (`93e48333886a` · neutral · operational_relevance; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- OpenProse is an open-source agent skill and programming language for describing agent workflows in logical English, with `.prose.md` files as the source format. It is designed to let coding agents execute reusable, reviewable workflows rather than improvised chat sessions. (`e0bddb08d3c7` · neutral · short_description; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- - Separates workflow intent from execution by using logical English contracts, which makes the resulting program easier for humans to review before an agent runs it.
- Runs each service in its own isolated sub-agent session, which helps keep scratch work and dead-end reasoning from polluting the main context.
- Leaves receipts under `runs/{run-id}/`, which gives operators an audit trail for what the agent actually did rather than what it claimed to do.
- Allows explicit dependencies on tools and skills, which is useful when a workflow needs a specific capability such as document editing or JSON parsing.
- Can be used across multiple coding-agent harnesses, so the workflow is not locked to one specific runtime. (`f80b1d3bb111` · neutral · strengths; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- OpenProse turns a successful agent session into a reusable `.prose.md` program that can be reviewed and edited before execution. (`4a5582bf8d34` · supporting · core_capabilities[0]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- OpenProse supports isolated sub-agent sessions so intermediate work stays contained until declared outputs are carried forward. (`79c4ef4cd088` · supporting · core_capabilities[1]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- OpenProse can declare real tools or skills as dependencies, which matters when a workflow needs a specific capability to finish correctly. (`cb13aee55686` · supporting · core_capabilities[2]; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- OpenProse – it’s open sourced! – turns successful Claude Code and Codex sessions into reusable, reviewable programs written in logical English. (`c9bfe9009b71` · supporting · supporting_snippet; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])
- The source is clear that OpenProse does not make the underlying model deterministic, so it improves repeatability without removing the need for judgment and verification. The agent still decides when to invoke tools, so determinism lives in the script or executable rather than in the orchestration layer. The article also suggests there is real overhead, and that not every prompt deserves to become a program. (`a32a708424d5` · uncertainty · weaknesses_limitations; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])

## Contradictions / tensions

- The source is clear that OpenProse does not make the underlying model deterministic, so it improves repeatability without removing the need for judgment and verification. The agent still decides when to invoke tools, so determinism lives in the script or executable rather than in the orchestration layer. The article also suggests there is real overhead, and that not every prompt deserves to become a program. (uncertainty; [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]])

## Related pages

- Claude Code
- Codex
- OpenClaw

## Sources

- [[sources/how-openprose-makes-ai-agent-behavior-repeatable-01ktb3ceq8be6weh8yt0k73z4f|How OpenProse Makes AI Agent Behavior Repeatable]]
