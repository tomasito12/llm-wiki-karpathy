---
title: Approval-Based Coding Workflows
slug: approval-based-coding-workflows
entity_id: topic:approval-based-coding-workflows
category: topic
tags:
- agent-orchestration
- agent-systems
- ai-engineering
- ai-governance
- auditability
- coding-agents
- enterprise-workflows
- runtime-architecture
- software-engineering
first_seen: '2026-04-16'
last_seen: '2026-05-08'
source_count: 3
evidence_count: 24
source_ids:
- ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33
- antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03
- running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc
value_level: high
confidence: 0.943333
synthesis_state: stage1-placeholder
---

# Approval-Based Coding Workflows

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Approval-based coding workflows keep a human in the loop for significant or destructive changes while still letting the assistant handle planning, edits, and command execution. The practical advantage is reduced risk: the user can inspect a plan or diff before committing to each step. This pattern is especially valuable in refactoring, large codebases, or regulated environments where irreversible mistakes are costly. The tradeoff is slower throughput and more manual review overhead.

## Examples

The source says Claude Code "shows you the plan, then executes step by step" and "asks before running destructive commands, shows you exactly what it’s changing, and provides clear diffs."

## Key Points

- Planning plus approval reduces coordination errors in multi-step tasks.
- Diff visibility is an operational control, not just a UX detail.
- The pattern is slower than full autonomy but usually easier to trust on critical changes.
- Automated approval can be used to force smaller changes rather than merely speed up merges.
- A strict gate is safer when it refuses oversized or overly broad changes instead of trying to handle everything.
- Human override remains important for exceptions and accountability.
- The gate should be paired with production monitoring and rollback readiness.
- Sandboxing and approval policy solve different problems and should not be conflated.
- Auto-approval is useful only for clearly low-risk requests; otherwise it becomes a hidden escalation path.
- The operational goal is frictionless routine work plus explicit review for higher-risk actions.
- Policy design must account for developer throughput, not just risk reduction.

## Operational Insight

Use approvals where correctness and reversibility matter more than speed; the workflow is valuable because it turns AI output into an inspectable sequence rather than a black box.

## Evidence / supporting sources

### AI is approving our pull requests: Here’s how we made it safe (2026-04-21)

- Approval-gated coding workflows use an automated reviewer or policy gate to decide whether a change can merge or ship, with humans retaining override paths for higher-risk cases. The durable design idea is to treat approval as a controllable safety mechanism, not just a clerical step. These workflows work best when they are strict about scope, produce auditable evidence, and push engineers toward smaller, easier-to-review changes. They also need a clear fallback path for larger, more complex, or ambiguous changes that exceed the automation's confidence or policy envelope. (`1b55d6262cb1` · neutral · knowledge_summary; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Use the approval gate to enforce change discipline: small diffs, explicit intent, and auditable review artifacts. Do not treat the gate as a substitute for accountability; keep human override and production monitoring in place. (`390950385afd` · neutral · operational_insight; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- This pattern matters for AI engineering because approval gates can reduce review bottlenecks while also shaping safer release behavior. It is especially relevant in software teams that want AI-assisted code changes without losing auditability or rollback discipline as of 2026-04-21. (`d87c440ac144` · neutral · relevance_note; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Automated approval can be used to force smaller changes rather than merely speed up merges. (`37ff710a7d2f` · supporting · key_points[0]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- A strict gate is safer when it refuses oversized or overly broad changes instead of trying to handle everything. (`f8a00eb47af0` · supporting · key_points[1]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Human override remains important for exceptions and accountability. (`5dbdb08bafd1` · supporting · key_points[2]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- The gate should be paired with production monitoring and rollback readiness. (`185eaa2c4597` · supporting · key_points[3]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- "Our Agent is strict. It won’t approve large PRs. If a change is too big, too complex, or too broad in scope, it flags it and requires it to be broken down." (`dac6b0888a03` · supporting · supporting_snippet; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])

### Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use? (2026-04-16)

- The source says Claude Code "shows you the plan, then executes step by step" and "asks before running destructive commands, shows you exactly what it’s changing, and provides clear diffs." (`0a5fb173ba31` · neutral · examples; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- Approval-based coding workflows keep a human in the loop for significant or destructive changes while still letting the assistant handle planning, edits, and command execution. The practical advantage is reduced risk: the user can inspect a plan or diff before committing to each step. This pattern is especially valuable in refactoring, large codebases, or regulated environments where irreversible mistakes are costly. The tradeoff is slower throughput and more manual review overhead. (`a4299bc02678` · neutral · knowledge_summary; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- Use approvals where correctness and reversibility matter more than speed; the workflow is valuable because it turns AI output into an inspectable sequence rather than a black box. (`22e1b14c2e22` · neutral · operational_insight; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- This is a durable operating pattern for AI coding assistants, agent tools, and any high-stakes automation that can benefit from staged approval gates. It also transfers well to support automation and other human-facing workflows where auditing and reversibility matter more than raw speed. (`a9f29f967d50` · neutral · relevance_note; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- Planning plus approval reduces coordination errors in multi-step tasks. (`d45931fae119` · supporting · key_points[0]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- Diff visibility is an operational control, not just a UX detail. (`49159288fbbb` · supporting · key_points[1]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- The pattern is slower than full autonomy but usually easier to trust on critical changes. (`93bd6dcb0a73` · supporting · key_points[2]; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])
- "You describe a task, it plans the work, shows you the plan, then executes step by step. Every significant change asks for permission." (`e166ccbd6960` · supporting · supporting_snippet; [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]])

### Running Codex safely at OpenAI (2026-05-08)

- Coding agents can be useful in production only when their execution is partitioned into low-risk actions that run freely and higher-risk actions that require explicit review. The practical design problem is not whether to add approvals, but how to place them so they reduce risk without freezing ordinary engineering work. A workable setup usually separates execution boundaries, approval policy, and logging, because those solve different parts of the control problem. This pattern becomes more important as agents gain access to repositories, shells, and development tools. (`b24ef993d638` · neutral · knowledge_summary; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- Treat approval policy as a separate layer from the sandbox. Let the sandbox define what the agent can physically do, and let approvals decide which actions deserve human sign-off. (`b735d95af303` · neutral · operational_insight; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- This is durable for any organization deploying coding agents or other agentic developer tools. The same pattern applies whenever an autonomous system can edit code, run commands, or touch infrastructure, especially in enterprise environments where safety and developer speed both matter. (`1b5acdaaca2a` · neutral · relevance_note; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- Sandboxing and approval policy solve different problems and should not be conflated. (`e5ea1d25fc91` · supporting · key_points[0]; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- Auto-approval is useful only for clearly low-risk requests; otherwise it becomes a hidden escalation path. (`be3f4db2144d` · supporting · key_points[1]; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- The operational goal is frictionless routine work plus explicit review for higher-risk actions. (`7aebd0d566c1` · supporting · key_points[2]; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- Policy design must account for developer throughput, not just risk reduction. (`800490cd7383` · supporting · key_points[3]; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])
- “Approvals and sandboxing work together. The sandbox defines the technical execution boundary… Approval policy determines when Codex must ask to perform an action…” (`53b07dd22b17` · supporting · supporting_snippet; [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[topics/agent-first-ide-orchestration|Agent-First IDE Orchestration]]
- [[topics/verification-loops-in-ai-workflows|Verification Loops in AI Workflows]]
- [[topics/agent-native-auditability|Agent-Native Auditability]]
- [[topics/agent-runtime-architecture-for-voice|Agent Runtime Architecture for Voice]]

## Sources

- [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]]
- [[sources/antigravity-vs-claude-code-which-ai-coding-assistant-should-you-actually-use-01kqkzbbr47x5jcmdm2wy72k03|Antigravity vs Claude Code: Which AI Coding Assistant Should You Actually Use?]]
- [[sources/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc|Running Codex safely at OpenAI]]
