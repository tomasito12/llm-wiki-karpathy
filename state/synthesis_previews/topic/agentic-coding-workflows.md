---
title: Agentic Coding Workflows
slug: agentic-coding-workflows
entity_id: topic:agentic-coding-workflows
category: topic
tags:
- agent-orchestration
- agent-systems
- ai-assisted-development
- ai-engineering
- ai-evaluation
- coding-agents
- human-ai-workflows
- software-engineering
- test-and-verification
- workflow-design
first_seen: '2026-03-18'
last_seen: '2026-06-08'
source_count: 8
evidence_count: 61
source_ids:
- agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9
- ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f
- domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v
- if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg
- introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1
- setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0
- why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b
- wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9
value_level: high
confidence: 0.92625
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: dded6abffb7f4628
current_input_hash: dded6abffb7f4628
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-08T20:33:20Z'
---

# Agentic Coding Workflows

## Executive synthesis

Agentic coding workflows are not just chatbots that write code; they are supervised execution loops where a model plans, edits, tests, and retries inside a larger human-controlled process. Across the sources, the main shift is from typing code to managing a loop: breaking work into small steps, checking diffs and test results, deciding when to continue, and catching subtle wrongness that still compiles. The practical value comes from delegation with control, especially for long tasks, migrations, terminal-heavy work, and parallel branch-based development. The main risk is that the same delegation that increases throughput can also erode comprehension, debugging skill, and judgment if humans stop doing enough direct implementation.

## Context card

- **Use this page when:** Use this page when you want a compact overview of how agentic coding workflows change development, what design choices matter, and where the main risks and evaluation gaps are.
- **Best for questions about:** what agentic coding workflows are, why they matter for software engineering and AI-assisted development, how to structure supervised coding-agent loops, what makes coding agents succeed or fail in practice, how to evaluate agentic coding beyond one-shot benchmarks
- **Not enough for:** choosing a specific vendor or model, designing a production-grade agent framework from first principles, proving that agentic coding always improves productivity, domain-specific safety requirements not covered by the sources
- **Strongest sources:** WTF Is a Loop? Peter Steinberger vs. Boris Cherny, AI’s Second Moment: The Explosion That Changed Everything, Domain Expertise Has Always Been the Real Moat, If AI Writes Your Code, Why Use Python?, Introducing Composer 2, Setting Up Mac for Development [May 2026], Agentic Coding is a Trap, Why I Stopped Using Gemma 4 and Switched to Qwen 3.6
- **Related tags:** agent-orchestration, agent-systems, ai-assisted-development, ai-engineering, ai-evaluation, coding-agents, human-ai-workflows, software-engineering, test-and-verification, workflow-design

## What to remember

- The unit of work is the loop, not the prompt.
- Human supervision shifts toward architecture, review, and correctness judgment.
- Fast compile/test feedback makes agent output more useful and easier to trust.
- Tool discipline, state tracking, and recovery from errors are often the real bottlenecks.
- Generated code can still be wrong even when it passes tests.
- Keeping some manual implementation helps preserve debugging skill and comprehension.
- Evaluation should focus on end-to-end task completion, retries, and long-horizon behavior, not just one-shot code quality.

## Consensus

- Agentic coding workflows are multi-step, supervised loops: the model reads files, uses tools, edits code, runs checks, and may re-prompt or retry until the task is done.
- The human role shifts from line-by-line implementation toward decomposition, architecture, prompt constraints, review, and correctness judgment.
- Verification matters more than fluent output; compile/test feedback, explicit checks, and halting rules are central to making these workflows reliable.
- Task quality depends heavily on orchestration details such as state management, error recovery, tool discipline, and the surrounding harness or terminal workflow.
- These workflows are most useful when work can be broken into reviewable chunks and when human attention is limited but still available for oversight.

## Tensions / open questions

- Some sources frame agentic coding as a durable productivity pattern, while others warn it can become a trap that reduces understanding and learning.
- There is agreement that tests and compile success are useful, but also clear concern that they are not sufficient when domain rules are not encoded in the checks.
- The evidence supports longer autonomous trajectories as important, but it does not settle how much autonomy is safe or effective in different teams and domains.
- Sources emphasize better orchestration and evaluation, but they do not provide a single standard loop design or universal best practice.

## Evidence quality

- The evidence base is fairly strong for the workflow-level pattern: 8 sources and 61 reviewed evidence items converge on the same core structure.
- Confidence is highest on operational claims about supervision, verification, long-horizon execution, and error recovery, because multiple sources repeat them independently.
- Evidence is weaker on broad productivity claims: the sources support potential gains, but they also emphasize trade-offs and failure modes.
- Several sources are current as of 2026, so the page is time-sensitive; conclusions may shift as agent capabilities and tooling improve.

## Practical takeaway

Treat the agent as a subroutine inside a well-designed loop, not as an autopilot: make work small, add fast feedback, require explicit verification of domain rules, and keep enough manual coding in the process to preserve understanding and debugging ability.

## Evidence index

- Sources: 8
- Evidence items: 61
- Current input hash: `dded6abffb7f4628`
- Cached input hash: `dded6abffb7f4628`
- Last synthesized: 2026-07-08T20:33:20Z
- Synthesis status: `fresh`

## Related pages

- [[topics/approval-based-coding-workflows|Approval-Based Coding Workflows]]
- [[topics/harness-decay|Harness Decay]]
- [[topics/agent-runtime-architecture|Agent Runtime Architecture]]
- [[topics/agent-runtime-architecture-for-voice|Agent Runtime Architecture for Voice]]
- [[topics/verification-loops-in-ai-workflows|Verification Loops in AI Workflows]]
- [[topics/tool-discipline-in-agent-loops|Tool Discipline in Agent Loops]]
- [[topics/workflow-restructuring-around-ai-agents|Workflow Restructuring Around AI Agents]]
- [[topics/domain-expertise-as-verification|Domain Expertise as Verification]]

## Sources

- [[sources/agentic-coding-is-a-trap-01krv8ckkgpcbaz9tn6ryd5vy9|Agentic Coding is a Trap]]
- [[sources/ai-s-second-moment-the-explosion-that-changed-everything-01kr4pq886wnqdq05t20rejy0f|AI’s Second Moment: The Explosion That Changed Everything]]
- [[sources/domain-expertise-has-always-been-the-real-moat-01ktjz6cyb7sg9znxh03mrzw1v|Domain Expertise Has Always Been the Real Moat]]
- [[sources/if-ai-writes-your-code-why-use-python-01krbncwpakyz5n828c0p8fnfg|If AI Writes Your Code, Why Use Python?]]
- [[sources/introducing-composer-2-01kr1qhvfpdcttev7248ae0ba1|Introducing Composer 2]]
- [[sources/setting-up-mac-for-development-may-2026-01ktpm1xqjsx1ra42yp56bera0|Setting Up Mac for Development [May 2026]]]
- [[sources/why-i-stopped-using-gemma-4-and-switched-to-qwen-3-6-01kqm05wc7wq68ypednrdcpa0b|Why I Stopped Using Gemma 4 and Switched to Qwen 3.6]]
- [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]]
