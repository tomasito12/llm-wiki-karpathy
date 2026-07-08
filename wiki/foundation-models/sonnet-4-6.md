---
title: Sonnet 4.6
slug: sonnet-4-6
entity_id: model:sonnet-4-6
category: foundation-model
tags:
- frontier-model
- proprietary-model
first_seen: '2026-04-16'
last_seen: '2026-06-05'
source_count: 2
evidence_count: 23
source_ids:
- antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03
- how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c
value_level: medium
confidence: 0.835
synthesis_state: stage1-placeholder
types:
- frontier-model
- multimodal-model
- proprietary-model
---

# Sonnet 4.6

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
- Described as Claude Code’s default model for most tasks.
- The article presents it as the practical everyday option in a terminal-first coding assistant, with Opus 4.6 reserved for deeper reasoning.
- Its operational identity here is tied to disciplined, approval-based coding rather than unconstrained autonomy.

## Comparative Observations

- The article contrasts Sonnet 4.6 with Opus 4.6 inside Anthropic’s own product stack.
- It is framed as part of a more sequential and permission-based workflow than the parallel agent setup in Antigravity.
- It is described as less intensive than Opus, which makes it the preferred first pass for ordinary work.
- It is treated as a better everyday default than Haiku for anything beyond very lightweight summarization.

## Core Capabilities

- It serves as the default coding model inside Claude Code for most tasks.
- It is presented as the lighter-weight option compared with Opus 4.6 for deeper reasoning.
- It serves as the default general-purpose model for routine assistant work in the described workflow.
- It is positioned as sufficiently capable for most tasks without needing the highest-cost model.
- It supports a routing strategy where stronger models are reserved for harder synthesis tasks.

## Maturity signals

The source treats it as the default choice inside a mature, paid coding product, which suggests practical readiness. However, the article gives no independent enterprise or benchmark evidence for the model itself.

## Pricing / inference implications

The article ties Claude Code’s paid subscription to Anthropic model access, but it does not break out model-level inference economics for Sonnet 4.6 specifically.

## Provider

Anthropic

## Service automation implications

No direct service automation implications are discussed for Sonnet 4.6 in this source.

## Weaknesses / limitations

The article does not isolate Sonnet 4.6 from Claude Code as a distinct model evaluation. The limitations discussed in the source are mostly the assistant’s task-completion ceiling and the need for human correction on complex refactors, not model-specific failure modes.

## Evidence / supporting sources

### Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use? (2026-04-16)

- The article contrasts Sonnet 4.6 with Opus 4.6 inside Anthropic’s own product stack. (`9af8f2c08322` · neutral · comparative_observations[0]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- It is framed as part of a more sequential and permission-based workflow than the parallel agent setup in Antigravity. (`f9b06d0d4be5` · neutral · comparative_observations[1]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- Using Sonnet 4.6 through Claude Code means teams get a controlled sequential workflow with explicit approvals and diff visibility. That makes it easier to apply in codebases where stepwise validation matters more than maximum parallelism. The source does not provide hard numbers on latency, cost per task, or reliability beyond the general Claude Code experience. (`976608f947b4` · neutral · deployment_implications; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- The source treats it as the default choice inside a mature, paid coding product, which suggests practical readiness. However, the article gives no independent enterprise or benchmark evidence for the model itself. (`b381fc0219bf` · neutral · maturity_signals; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- - Described as Claude Code’s default model for most tasks.
- The article presents it as the practical everyday option in a terminal-first coding assistant, with Opus 4.6 reserved for deeper reasoning.
- Its operational identity here is tied to disciplined, approval-based coding rather than unconstrained autonomy. (`ea6d3b4b6143` · neutral · operational_profile; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- The article ties Claude Code’s paid subscription to Anthropic model access, but it does not break out model-level inference economics for Sonnet 4.6 specifically. (`56cc276b014d` · neutral · pricing_inference_implications; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- No direct service automation implications are discussed for Sonnet 4.6 in this source. (`15a095decdc9` · neutral · service_automation_implications; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- It serves as the default coding model inside Claude Code for most tasks. (`037dc75026c2` · supporting · core_capabilities[0]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- It is presented as the lighter-weight option compared with Opus 4.6 for deeper reasoning. (`db87801a954a` · supporting · core_capabilities[1]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- "You get Sonnet 4.6 (the default for most tasks), or Opus 4.6 if you need deeper reasoning on complex work." (`d70c45b52658` · supporting · supporting_snippet; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- The article does not isolate Sonnet 4.6 from Claude Code as a distinct model evaluation. The limitations discussed in the source are mostly the assistant’s task-completion ceiling and the need for human correction on complex refactors, not model-specific failure modes. (`beafa53a8ef2` · uncertainty · weaknesses_limitations; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])

### How I Use Obsidian + Claude Cowork to Run My Life (2026-06-05)

- It is described as less intensive than Opus, which makes it the preferred first pass for ordinary work. (`dd1ff6e051de` · neutral · comparative_observations[0]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- It is treated as a better everyday default than Haiku for anything beyond very lightweight summarization. (`2b1db962514c` · neutral · comparative_observations[1]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Using Sonnet first suggests a routing strategy where most routine tasks stay on the cheaper or more efficient model, and only hard synthesis tasks escalate. For production workflows, that implies an orchestration policy that reduces cost pressure and keeps the expensive model reserved for high-stakes work. The source does not provide throughput, latency, or context-window data, so deployment guidance remains qualitative. (`ee6671b272b1` · neutral · deployment_implications; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- The model is presented as established enough to be part of a stable everyday routing pattern. The source assumes users can switch models inside the same product without reworking the workflow. No external adoption evidence is provided. (`7a0ade3f52b1` · neutral · maturity_signals; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- Sonnet 4.6 is used as the default model for most tasks in the workflow because it offers a practical middle ground between cost and capability.
- The source positions it as the first-choice model for ordinary work, which implies good general-purpose quality without the cost of a larger model.
- It is the model used when the task does not need the extra depth of the top-tier option.
- It is treated as the model that helps the user preserve Pro usage for harder jobs. (`da9ba4c57e34` · neutral · operational_profile; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- The advice to use Sonnet first is an explicit cost-management cue: it is meant to preserve higher-tier usage for harder tasks. The source implies it is cheaper in practical token usage than Opus, but gives no price figures. (`0e4431780ee9` · neutral · pricing_inference_implications; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- For service automation, the implication is that a mid-tier model can handle many routine support or planning tasks, while escalation paths reserve stronger models for harder synthesis or exception handling. That is useful for building tiered agent workflows rather than sending every request to the most expensive model. (`0ac6371783e0` · neutral · service_automation_implications; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- It serves as the default general-purpose model for routine assistant work in the described workflow. (`c0afeb8c12e5` · supporting · core_capabilities[0]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- It is positioned as sufficiently capable for most tasks without needing the highest-cost model. (`1d90cac8b039` · supporting · core_capabilities[1]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- It supports a routing strategy where stronger models are reserved for harder synthesis tasks. (`c357f04981d0` · supporting · core_capabilities[2]; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- "The first is that Claude says that they don't train on your data... The other reason I'm using Claude is that it's one of the least restrictive Frontier apps out there... The best general approach and to allow you to use Pro more often, try to use the sonnet model first. That's themiddle model. It's less intensive, butit's good for most tasks." (`f1b40b6b6209` · supporting · supporting_snippet; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])
- The source does not describe specific technical weaknesses beyond being the middle-tier option, so any capability limits are unclear. Its role is defined relative to Opus and Haiku, not by measured performance on external benchmarks. (`47838362ac90` · uncertainty · weaknesses_limitations; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])

## Contradictions / tensions

- The article does not isolate Sonnet 4.6 from Claude Code as a distinct model evaluation. The limitations discussed in the source are mostly the assistant’s task-completion ceiling and the need for human correction on complex refactors, not model-specific failure modes. (uncertainty; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- The source does not describe specific technical weaknesses beyond being the middle-tier option, so any capability limits are unclear. Its role is defined relative to Opus and Haiku, not by measured performance on external benchmarks. (uncertainty; [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]])

## Related pages

- [[foundation-models/opus-4-6|Opus 4.6]]
- [[foundation-models/gemini-3-pro|Gemini 3 Pro]]

## Sources

- [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]]
- [[sources/how-i-use-obsidian-claude-cowork-to-run-my-life-01kv4tcedck5ftexd9hqeptc7c|How I Use Obsidian + Claude Cowork to Run My Life]]
