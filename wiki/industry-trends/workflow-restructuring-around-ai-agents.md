---
title: Software workflows are restructuring around durable agents
slug: workflow-restructuring-around-ai-agents
entity_id: trend:workflow-restructuring-around-ai-agents
category: industry-trend
tags:
- ai-operationalization
- automation-supervision
- enterprise-ai
- execution-oriented-agents
- human-ai-collaboration
- orchestration-layer-growth
- persistent-agents
- runtime-systems
- verification-over-principles
- workflow-restructuring
aliases:
- AI Workflows Shift Toward Orchestrated Loops
- AI workflows are shifting toward parallel subagent orchestration
- AI workflows are shifting toward systems that act over time
- AI workflows shift from prompting to orchestrated loops
- Workflow Restructuring Around AI Agents
first_seen: '2026-04-16'
last_seen: '2026-06-12'
source_count: 13
evidence_count: 112
source_ids:
- a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn
- ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33
- ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2
- ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs
- ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y
- ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh
- ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz
- ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm
- ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m
- from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs
- how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2
- the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye
- wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9
value_level: high
confidence: 0.8961538461538462
synthesis_state: stage1-placeholder
maturity: unknown
---

# Software workflows are restructuring around durable agents

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
AI workflows are moving away from single-turn prompting and toward orchestrated loops with persistent state, isolated execution, browser grounding, and artifact handling. The structural change is that the agent runtime becomes the workflow boundary, not the chat UI. This trend is especially relevant when the system must execute, recover, and resume multi-step work over time.

## Related Trends

- harness-design-becomes-more-important-for-agent-reliability
- persistent-agents
- verification-loops-become-central-to-ai-workflows
- ai-products-shift-from-models-to-systems
- enterprise-ai-moves-toward-governed-human-oversight-workflows
- artifact-first-ai-workflows
- agent-tooling-shifts-from-prompting-to-workflow-architecture
- execution-oriented-agents
- models-becoming-execution-layers
- workflow-based-evaluation

## Supporting Data Points

- OpenAI Agents SDK emphasized file/computer use, skills, memory, and compaction.
- Cloudflare emphasized durable execution, sub-agents, persistent sessions, sandboxed code execution, and workspace filesystem.
- Hermes Agent was described as turning completed workflows into reusable skills.
- Over 93% of PRs across the two main codebases are Agent-driven.
- Over 19% are auto-approved with no human reviewer in the loop.
- A controlled pilot of over 100 PRs reported zero reverts of AI-approved PRs.
- 497 PRs went fully autonomous in the first four weeks of broader rollout.
- OpenAI launched shared, Codex-powered workspace agents for Business/Enterprise/Edu/Teachers.
- Google launched Gemini Enterprise Agent Platform with Agent Studio and governance.
- Cursor added Slack invocation for task kick-off and streaming updates.
- The article describes long prompts, open-model RLFT, retrieval, routing, and infrastructure as part of the same decision space.
- Agent runtimes are described as needing replay, rollback, and durable state semantics.
- Training-time wrappers are highlighted because they can be removed before deployment.
- Antigravity 2.0 desktop app
- Antigravity CLI
- Antigravity SDK
- Managed Agents in the Gemini API
- 93 parallel sub-agents
- 15k+ model requests
- 2.6B tokens
- < $1K API credits
- Dynamic Workflows is in research preview.
- Hundreds of subagents are spawned in parallel.
- The article cites a 750k LOC Bun rewrite as an example.
- Users warned that the approach can be token-expensive and quota-burning.
- AI used across the full DavaFlow lifecycle
- Adoption extended into legal, finance/project management, commercial teams, and leadership
- The company frames AI as part of its operating model
- Claude Code workflow described as writing loops instead of prompting
- Dynamic workflows reworked into branching research, verification, triage, data synthesis, and eval generation
- Multiple adjacent tools framed around harnesses, sandboxes, traces, and evals
- Stratix Cup frames evaluation around simulated soccer and multi-agent behavior.
- Microsoft's MAI releases are described alongside tighter integration with Copilot, agents, and devices.
- OpenAI's memory work and NVIDIA's Cosmos 3 both emphasize longer-horizon model operation.
- ReAct is described as the stage-one loop pattern in 2022.
- AutoGPT is described as an earlier self-prompting stage in 2023.
- The newer pattern includes supervision of other loops, scheduling, and restart durability.
- Claude Code and Codex are described as shipping /goal or /loop commands in spring 2026.
- Teams across product, engineering, research, and operations used AI to draft reports, synthesize market data, prototype products, and streamline workflows.
- The company says it is expanding beyond individual productivity gains to workflow-level AI applications.
- Product release cycles reportedly fell from 3-6 months to 2 weeks.
- Steipete: "designing loops that prompt your agents"
- Boris Cherny: "I write loops, the loops do the work"
- Andrej Karpathy: "arrange things such that they’re completely autonomous"
- The author says he no longer writes tickets and instead talks about them with the agent.
- The agent produces a product pulse from analytics, tracing, payments, and read-only database inputs.
- The workflow is described as changing at least weekly, which suggests the implementation details are fluid.

## Time sensitivity

Actionable as of 2026-04-16; this is a live architecture pattern in the source, but the roundup does not quantify how broadly it has been adopted.

## Uncertainty / maturity

The source is a roundup of launches and commentary, so it shows convergence in product direction more than proven production success. The long-term durability of each implementation pattern remains uncertain.

## Evidence / supporting sources

### A Guide to Agent-native Product Management - Every (2026-04-27)

- Knowledge work is being reorganized so that agents handle repetitive coordination, reporting, and artifact maintenance while humans focus on judgment, design, and exception handling. The shift is strongest when the work can be expressed as conversational loops over connected tools and explicit documents. This is not a claim that agents replace experts; it is a shift in where expert time is spent. (`97f8a2031f35` · neutral · trend_description; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- The article describes product management moving from manual ticket writing and dashboard review toward conversational work in Claude Code, with the agent handling strategy interviews, ticket updates, and product pulse generation. (`7ff923948786` · supporting · evidence_from_source; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- The author says he no longer writes tickets and instead talks about them with the agent. (`277a5f4da42c` · supporting · supporting_data_points[0]; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- The agent produces a product pulse from analytics, tracing, payments, and read-only database inputs. (`c577ca79aa75` · supporting · supporting_data_points[1]; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- The workflow is described as changing at least weekly, which suggests the implementation details are fluid. (`b754d51e8799` · supporting · supporting_data_points[2]; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- "The conversation is the work." (`2470cb95d7f6` · supporting · supporting_snippet; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- Actionable as of 2026-04-27; the exact workflow will change as tools and integrations change, but the underlying restructuring pattern is likely to remain relevant. (`38f78867c2c1` · uncertainty · time_sensitivity; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- The evidence is a single practitioner workflow at one company, so it shows a plausible operating pattern rather than a broadly validated industry standard. (`a23f04a9bb3c` · uncertainty · uncertainty_note; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])

### AI is approving our pull requests: Here’s how we made it safe (2026-04-21)

- Organizations are restructuring engineering workflows so AI agents handle narrower operational sub-tasks while humans retain oversight, exception handling, and accountability. The shift is less about replacing humans than about redesigning work so automated systems can safely take on higher-volume, lower-latency parts of the pipeline. In practice, this pushes teams toward decomposed workflows, explicit decision gates, and better traceability. (`89c7a767424b` · neutral · trend_description; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Intercom says its PR review system breaks review into independent sub-agents, auto-approves some pull requests, and still allows human review on any change. The system is presented as a way to remove a review bottleneck created by AI-generated code while preserving safety and compliance. (`25f11a1b2c57` · supporting · evidence_from_source; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Over 93% of PRs across the two main codebases are Agent-driven. (`6c2f69c49860` · supporting · supporting_data_points[0]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Over 19% are auto-approved with no human reviewer in the loop. (`71b004196773` · supporting · supporting_data_points[1]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- A controlled pilot of over 100 PRs reported zero reverts of AI-approved PRs. (`4ccee4b79511` · supporting · supporting_data_points[2]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- 497 PRs went fully autonomous in the first four weeks of broader rollout. (`4c66a78e22b9` · supporting · supporting_data_points[3]; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- "Our PR review Agent doesn’t treat code review as a single task. It decomposes it into separate sub-jobs, each handled by an independent sub-Agent." (`a7f1afdb7f95` · supporting · supporting_snippet; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Actionable as of 2026-04-21; the source describes a live rollout rather than a speculative future pattern. (`5da9be65f79d` · uncertainty · time_sensitivity; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- This is based on a single company case study, so it shows one workable operating model rather than a general industry baseline. The same structure may not transfer cleanly to teams without similar logging, deployment discipline, or codebase context. (`e6b05b3afe04` · uncertainty · uncertainty_note; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])

### [AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode (2026-05-29)

- Model use is moving from single-shot prompting toward workflows where a primary agent plans work and delegates to many parallel subagents. The operational pattern is not just more autonomy; it is orchestration, verification, and task decomposition inside the product. This matters most for large coding, refactor, and audit jobs where parallel work can reduce wall-clock time if the harness is reliable. (`ae67a48c6b66` · neutral · trend_description; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- Anthropic’s Claude Code Dynamic Workflows feature is described as a system where Claude writes an orchestration script, launches hundreds of coordinated subagents in parallel, and uses a prompt trigger like the word “workflow.” The article cites uses such as a 750k LOC Bun rewrite and parallel processing of hundreds of A/B test flags. (`860e3dc8b94c` · supporting · evidence_from_source; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- Dynamic Workflows is in research preview. (`d463b23cbf76` · supporting · supporting_data_points[0]; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- Hundreds of subagents are spawned in parallel. (`05f8797e3457` · supporting · supporting_data_points[1]; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- The article cites a 750k LOC Bun rewrite as an example. (`07d1656e9bdf` · supporting · supporting_data_points[2]; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- Users warned that the approach can be token-expensive and quota-burning. (`642fa70cfe7d` · supporting · supporting_data_points[3]; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- “Claude writes an orchestration script on the fly” then spins up “a large fleet of coordinated subagents in parallel” ... Examples cited: porting Bun from Zig to Rust ... using hundreds of parallel agents (`1047d2f6bed7` · supporting · supporting_snippet; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- Actionable as of 2026-05-29; likely relevant through the next product cycle for teams evaluating agentic coding and large-task orchestration. (`ce71def6ebac` · uncertainty · time_sensitivity; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- The source is launch coverage with mixed evidence. It shows that the pattern is operationally promising, but it also notes token cost, quota burn, and conflicting parallel edits, so real-world ROI depends on harness quality and task structure. (`57de02747be8` · uncertainty · uncertainty_note; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])

### [AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit… (2026-05-20)

- AI products are moving from single-turn chat toward agent systems that run many concurrent subtasks, use hosted sandboxes, and produce artifacts that can be inspected or exported. The operational pattern is not just better prompting; it is workflow decomposition, execution control, and long-running task management. (`93bbcc9a8a92` · neutral · trend_description; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Google framed Antigravity around desktop, CLI, SDK, and API-managed agents, and its demo of an OS built in 12 hours used 93 parallel sub-agents, 15k+ requests, and 2.6B tokens. (`bb0c67f98794` · supporting · evidence_from_source; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Antigravity 2.0 desktop app (`f69e77857d26` · supporting · supporting_data_points[0]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Antigravity CLI (`bf75aaf20fa1` · supporting · supporting_data_points[1]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Antigravity SDK (`d2376dd92826` · supporting · supporting_data_points[2]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Managed Agents in the Gemini API (`1b3fa93a434b` · supporting · supporting_data_points[3]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- 93 parallel sub-agents (`9e592f8b23fe` · supporting · supporting_data_points[4]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- 15k+ model requests (`66ebaf6d1c7a` · supporting · supporting_data_points[5]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- 2.6B tokens (`a95b015bba2f` · supporting · supporting_data_points[6]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- < $1K API credits (`6b6d70b52206` · supporting · supporting_data_points[7]; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Google’s own demos centered on parallel sub-agents, hosted execution, high-frequency iterative loops, and artifact-oriented workflows. The marquee proof point: OS built in 12h, 93 parallel sub-agents, 15k+ requests, 2.6B tokens, < $1K credits. (`4253dd3a08b9` · supporting · supporting_snippet; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Actionable as of 2026-05-20; this pattern is relevant while agent runtimes, hosted sandboxes, and parallel subagent workflows are being productized. (`0fd0d03b8767` · uncertainty · time_sensitivity; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- The evidence is strong for Google’s product direction, but the OS demo is stage-managed and does not prove production reliability or general cost efficiency. (`55933f22f47c` · uncertainty · uncertainty_note; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])

### [AINews] Loopcraft: The Art of Stacking Loops (2026-06-12)

- AI work is moving from single-turn prompting toward systems that run repeated steps with explicit goals, review points, and handoffs. The operational change is not just more automation; it is a refactor of the workflow so humans are removed from the critical path where possible, while still retaining control boundaries where needed. (`f84b1cfc1766` · neutral · trend_description; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- The roundup frames the core idea as "stacking loops" and says practitioners should "design loops that prompt your agents" and "arrange things such that they’re completely autonomous." It also links that framing to systems like Recursive SI, Arbor, managed agents, and scheduled deployments. (`85539772524d` · supporting · evidence_from_source; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- Steipete: "designing loops that prompt your agents" (`80fa7742b382` · supporting · supporting_data_points[0]; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- Boris Cherny: "I write loops, the loops do the work" (`1700ce9c44d2` · supporting · supporting_data_points[1]; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- Andrej Karpathy: "arrange things such that they’re completely autonomous" (`57cd966ebb99` · supporting · supporting_data_points[2]; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- "The entire game of the next century is to be able to stack loops as effectively as possible." ... "Instead focus on systems that scale with more agents, like goals and orchestration." (`f30b9246250a` · supporting · supporting_snippet; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- Actionable as of 2026-06-12; this is a live engineering pattern in the source, but the exact tooling and best practices may evolve as models improve. (`391fa8c2453f` · uncertainty · time_sensitivity; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- The source mixes strong operational examples with rhetoric, so the pattern is real but not fully validated across all agent workloads. Several cited systems still depend on benchmark environments, human curation, or vendor-controlled behavior. (`6aa8fd057317` · uncertainty · uncertainty_note; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])

### [AINews] not much happened today (2026-06-05)

- AI engineering is moving from single-shot prompting toward looped control structures that branch, verify, triage, and generate evals. The durable pattern is not better prompts, but more explicit workflow architecture around model calls. This matters most for agentic coding, research, and other tasks that need repeated tool use and recovery. (`b492e5d727e1` · neutral · trend_description; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- The roundup says a recurring theme was that the bottleneck is increasingly the harness/orchestrator, not just prompting, and quotes workflow examples built around loops, branching research, verification, triage, data synthesis, and eval generation. (`d953b8149d0b` · supporting · evidence_from_source; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- Claude Code workflow described as writing loops instead of prompting (`98be69a29e12` · supporting · supporting_data_points[0]; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- Dynamic workflows reworked into branching research, verification, triage, data synthesis, and eval generation (`bec82c2efb58` · supporting · supporting_data_points[1]; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- Multiple adjacent tools framed around harnesses, sandboxes, traces, and evals (`946f787b2cba` · supporting · supporting_data_points[2]; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- A recurring theme was that the bottleneck is increasingly the harness/orchestrator, not just prompting. A popular clip summarized the Claude Code workflow as “I don’t prompt Claude anymore, I write loops,” while @omarsar0 described reverse-engineering dynamic workflows into his own orchestrator for branching research, verification, triage, data synthesis, and eval generation. (`4d848a76bf5a` · supporting · supporting_snippet; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- Actionable as of 2026-06-05; the source suggests this is already a live engineering shift, though the exact best harness design remains unsettled. (`0d890ca04a42` · uncertainty · time_sensitivity; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- The evidence is a roundup synthesis of tweets and product launches, not a controlled comparative study, so it shows direction more than measured causality. (`6aa98b5e07d5` · uncertainty · uncertainty_note; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])

### [AINews] RIP Pull Requests (2005-2026) (2026-04-16)

- AI workflows are moving away from single-turn prompting and toward orchestrated loops with persistent state, isolated execution, browser grounding, and artifact handling. The structural change is that the agent runtime becomes the workflow boundary, not the chat UI. This trend is especially relevant when the system must execute, recover, and resume multi-step work over time. (`b56e35c3ffa1` · neutral · trend_description; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- The roundup repeatedly links OpenAI, Cloudflare, and Hermes to durable execution, sandboxed workspaces, memory, compaction, and reusable skills, and explicitly says the production agent platform is a composition of durable runtime, UI grounding, browser, voice, and sandbox. (`8cdbd5a4d918` · supporting · evidence_from_source; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- OpenAI Agents SDK emphasized file/computer use, skills, memory, and compaction. (`128b2d3b5c02` · supporting · supporting_data_points[0]; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- Cloudflare emphasized durable execution, sub-agents, persistent sessions, sandboxed code execution, and workspace filesystem. (`95eae383245f` · supporting · supporting_data_points[1]; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- Hermes Agent was described as turning completed workflows into reusable skills. (`f0ad97fc6978` · supporting · supporting_data_points[2]; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- "Taken together, Cloudflare is making a strong case that the production agent platform is really a composition of durable runtime + UI grounding + browser + voice + sandbox." (`8dd95acc0e86` · supporting · supporting_snippet; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- Actionable as of 2026-04-16; this is a live architecture pattern in the source, but the roundup does not quantify how broadly it has been adopted. (`c545d0fea58b` · uncertainty · time_sensitivity; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- The source is a roundup of launches and commentary, so it shows convergence in product direction more than proven production success. The long-term durability of each implementation pattern remains uncertain. (`6d9f45a45d79` · uncertainty · uncertainty_note; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])

### [AINews] Tasteful Tokenmaxxing (2026-04-23)

- AI product design is moving from single-shot chat toward shared, persistent, and governed agent workflows that can operate across tools, documents, and tasks. The operational shift is not just model capability; it is the surrounding harness, approvals, scheduling, and team context that make agents useful in production. (`abc1820f211c` · neutral · trend_description; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- The roundup says OpenAI launched shared Codex-powered workspace agents for teams, Google launched Gemini Enterprise Agent Platform with Agent Studio and governance, Cursor added Slack invocation for task kick-off and streaming updates, and the article frames this as a converging pattern of cloud-hosted agents, shared team context, approvals, and long-running execution. (`2343f4cfb8f8` · supporting · evidence_from_source; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- OpenAI launched shared, Codex-powered workspace agents for Business/Enterprise/Edu/Teachers. (`ebe58b37a0a3` · supporting · supporting_data_points[0]; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- Google launched Gemini Enterprise Agent Platform with Agent Studio and governance. (`e646e70ebb0a` · supporting · supporting_data_points[1]; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- Cursor added Slack invocation for task kick-off and streaming updates. (`a683b9a047ab` · supporting · supporting_data_points[2]; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- The pattern is converging: cloud-hosted agents, shared team context, approvals, and long-running execution rather than single-user chat. (`48e182a02520` · supporting · supporting_snippet; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- Actionable as of 2026-04-23; the source presents this as an active platform shift across multiple vendors rather than a settled endpoint. (`0b4257e12948` · uncertainty · time_sensitivity; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- The article is a roundup and relies on vendor announcements plus editorial synthesis, so the exact durability of each vendor implementation is uncertain even if the cross-vendor pattern is plausible. (`91a41f94586f` · uncertainty · uncertainty_note; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])

### [AINews] The End of Finetuning (2026-05-13)

- AI products and internal tooling are moving away from one-shot prompt usage toward orchestrated workflows that combine retrieval, routing, long-lived state, and post-training where needed. The architectural unit is increasingly the loop, not the prompt alone. (`7b3a1174320c` · neutral · trend_description; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- The roundup repeatedly contrasts simple model usage with more specialized stacks: long prompts, open-model RLFT, dedicated inference stacks, persistent agent runtimes, and workflow packaging. The finetuning section explicitly says the durable choice is whichever combination of prompts, retrieval, routing, post-training, and infrastructure best fits the task. (`f61f13950def` · supporting · evidence_from_source; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- The article describes long prompts, open-model RLFT, retrieval, routing, and infrastructure as part of the same decision space. (`248c9120e892` · supporting · supporting_data_points[0]; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- Agent runtimes are described as needing replay, rollback, and durable state semantics. (`ff9a51ac472d` · supporting · supporting_data_points[1]; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- Training-time wrappers are highlighted because they can be removed before deployment. (`c9b424a7796f` · supporting · supporting_data_points[2]; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- the durable work is moving toward whichever combination of prompts, retrieval, routing, post-training, and infrastructure best fits the task, not toward a single universal recipe. (`d054d058b031` · supporting · supporting_snippet; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- As of 2026-05-13, this is a live architectural shift described across multiple roundup sections, but the exact winning pattern will vary by workload. (`6b33c1006fbd` · uncertainty · time_sensitivity; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- The source is a newsletter roundup with mixed evidence quality, so this is a directional pattern rather than a measured adoption curve. It also concedes that top-tier teams still use stronger adaptation methods, so the shift is about defaults, not a universal replacement. (`f86839cafb64` · uncertainty · uncertainty_note; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])

### From data to decisions: how LSEG is scaling trusted AI (2026-06-10)

- Enterprise AI adoption is shifting from isolated task assistance toward redesigning workflows so AI can participate in research, product, and operations processes. The structural change is that organizations are redesigning how work gets done rather than only accelerating individual steps. This tends to matter most where information flow, review, and handoff are part of the bottleneck. (`4f266ad1a6f2` · neutral · trend_description; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- LSEG says the biggest gains came from rethinking workflows, and it is expanding from individual productivity into embedded workflow-level applications in research, product development, and client solutions. (`507b9c8bcd4f` · supporting · evidence_from_source; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- Teams across product, engineering, research, and operations used AI to draft reports, synthesize market data, prototype products, and streamline workflows. (`4a944ab46957` · supporting · supporting_data_points[0]; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- The company says it is expanding beyond individual productivity gains to workflow-level AI applications. (`7698217b6f3d` · supporting · supporting_data_points[1]; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- Product release cycles reportedly fell from 3-6 months to 2 weeks. (`ba8bf74a4009` · supporting · supporting_data_points[2]; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- "The biggest gains come from redesigning how work gets done" (`9e1302ad0177` · supporting · supporting_snippet; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- Actionable as of 2026-06-10; this observation reflects a live enterprise adoption pattern in the source and is likely relevant while organizations are still moving from chatbot use to embedded workflow design. (`3cd9a69ebf94` · uncertainty · time_sensitivity; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- This is based on one vendor case study, so it does not prove the pattern is universal or quantify how often workflow redesign outperforms simpler task-level adoption. (`a674e5f284b8` · uncertainty · uncertainty_note; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])

### How Endava is redesigning software delivery around AI agents (2026-06-04)

- Organizations are moving from using AI as a point productivity tool toward restructuring end-to-end workflows around agents, models, and human coordination. The change matters because the main value comes from redesigning the process, not just automating an isolated step. (`42f732d6b693` · neutral · trend_description; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- Endava says its AI work moved from developer experimentation to a company-wide methodology, and that OpenAI technology now spans planning, discovery, engineering, deployment, legal research, reporting, and leadership coordination. (`8d981c2883dd` · supporting · evidence_from_source; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- AI used across the full DavaFlow lifecycle (`29993763299a` · supporting · supporting_data_points[0]; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- Adoption extended into legal, finance/project management, commercial teams, and leadership (`70a854a55cab` · supporting · supporting_data_points[1]; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- The company frames AI as part of its operating model (`f701f72d0f49` · supporting · supporting_data_points[2]; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- “There isn’t a part of DavaFlow that doesn’t use OpenAI technology.” ... “From reasoning models and Codex agents to automation and enterprise-scale collaboration, Endava believes AI is becoming more than a productivity layer. It’s becoming the operating model itself.” (`dce2a1372916` · supporting · supporting_snippet; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- Actionable as of 2026-06-04; this is a live organizational pattern, but the article provides only one company case and no independent validation. (`7bb9fea0d8e9` · uncertainty · time_sensitivity; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- Evidence is limited to a vendor-published case study, so generalization is uncertain and measured gains are not reported. (`860f569dbc46` · uncertainty · uncertainty_note; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])

### The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels (2026-06-07)

- A recurring pattern in the source is that AI value is moving from isolated answers to systems that can plan, adapt, and keep state across multiple steps. That includes agentic workflows, memory architectures, live simulation evals, and product stacks that connect models to tools and devices. The pattern is operationally important because it changes what needs to be evaluated, instrumented, and trusted. (`0367a0e2650c` · neutral · trend_description; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- The roundup ties together the Stratix Cup, Microsoft's MAI releases, Anthropic's S-1, NVIDIA's Cosmos 3 and Nemotron 3 Ultra, and OpenAI's memory work as signs that models are becoming systems that act in environments rather than standalone chat interfaces. (`3919674e82e7` · supporting · evidence_from_source; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- Stratix Cup frames evaluation around simulated soccer and multi-agent behavior. (`fa13bf3ce5ab` · supporting · supporting_data_points[0]; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- Microsoft's MAI releases are described alongside tighter integration with Copilot, agents, and devices. (`a190e17163c0` · supporting · supporting_data_points[1]; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- OpenAI's memory work and NVIDIA's Cosmos 3 both emphasize longer-horizon model operation. (`4d54128068c4` · supporting · supporting_data_points[2]; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- "The rest of the week echoed the same shift from models as artifacts to models as operating systems." (`e28d1c8588dd` · supporting · supporting_snippet; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- As of 2026-06-07, this is an active product and evaluation direction in the source; its relevance should persist if agentic deployments keep expanding beyond chat UI use cases. (`8b334d681fc7` · uncertainty · time_sensitivity; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- The source is a roundup, so the evidence is heterogeneous and mostly announcement-level. It supports the direction of change, but not the maturity or broad adoption of any single implementation. (`f3c89ae00e2f` · uncertainty · uncertainty_note; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])

### WTF Is a Loop? Peter Steinberger vs. Boris Cherny (2026-06-08)

- AI use in coding is moving from single prompts toward orchestrated loops that keep prompting, checking, and re-routing work over time. The structural change is that the agent is no longer just a response generator; it becomes one component inside a larger runtime with scheduling, state, and supervision. This raises the importance of verification, halting conditions, and durable state because the workflow can continue without direct human presence. The shift is most visible in coding automation, but the pattern generalizes to other repeatable knowledge-work tasks. (`3e05e87857d1` · neutral · trend_description; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- The source contrasts direct prompting with writing loops, then distinguishes a newer orchestration layer where loops supervise other loops, run on schedules, and survive restarts with durable state. (`d0384af92045` · supporting · evidence_from_source; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- ReAct is described as the stage-one loop pattern in 2022. (`4452414133b9` · supporting · supporting_data_points[0]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- AutoGPT is described as an earlier self-prompting stage in 2023. (`9a46a9ba9469` · supporting · supporting_data_points[1]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- The newer pattern includes supervision of other loops, scheduling, and restart durability. (`5d990af6d67c` · supporting · supporting_data_points[2]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- Claude Code and Codex are described as shipping /goal or /loop commands in spring 2026. (`9deef6aebc19` · supporting · supporting_data_points[3]; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- “Stage five is what Boris and Steinberger actually mean, and it is genuinely new, not just renamed. Four things changed. The loop became the unit of work, not the task. Loops started supervising other loops, concurrently and on a schedule.” (`d0ac2da34385` · supporting · supporting_snippet; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- Actionable as of 2026-06-08; the source presents this as an emerging 2026 pattern rather than a settled norm. (`a41a3b1bc81f` · uncertainty · time_sensitivity; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- The evidence is discourse-heavy and largely practitioner anecdote rather than controlled adoption data, so the breadth of the shift is suggestive rather than proven. (`551e03882378` · uncertainty · uncertainty_note; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])

## Contradictions / tensions

- Actionable as of 2026-04-16; this is a live architecture pattern in the source, but the roundup does not quantify how broadly it has been adopted. (uncertainty; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- The source is a roundup of launches and commentary, so it shows convergence in product direction more than proven production success. The long-term durability of each implementation pattern remains uncertain. (uncertainty; [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]])
- Actionable as of 2026-04-21; the source describes a live rollout rather than a speculative future pattern. (uncertainty; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- This is based on a single company case study, so it shows one workable operating model rather than a general industry baseline. The same structure may not transfer cleanly to teams without similar logging, deployment discipline, or codebase context. (uncertainty; [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]])
- Actionable as of 2026-04-23; the source presents this as an active platform shift across multiple vendors rather than a settled endpoint. (uncertainty; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- The article is a roundup and relies on vendor announcements plus editorial synthesis, so the exact durability of each vendor implementation is uncertain even if the cross-vendor pattern is plausible. (uncertainty; [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]])
- Actionable as of 2026-04-27; the exact workflow will change as tools and integrations change, but the underlying restructuring pattern is likely to remain relevant. (uncertainty; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- The evidence is a single practitioner workflow at one company, so it shows a plausible operating pattern rather than a broadly validated industry standard. (uncertainty; [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]])
- As of 2026-05-13, this is a live architectural shift described across multiple roundup sections, but the exact winning pattern will vary by workload. (uncertainty; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- The source is a newsletter roundup with mixed evidence quality, so this is a directional pattern rather than a measured adoption curve. It also concedes that top-tier teams still use stronger adaptation methods, so the shift is about defaults, not a universal replacement. (uncertainty; [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]])
- Actionable as of 2026-05-20; this pattern is relevant while agent runtimes, hosted sandboxes, and parallel subagent workflows are being productized. (uncertainty; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- The evidence is strong for Google’s product direction, but the OS demo is stage-managed and does not prove production reliability or general cost efficiency. (uncertainty; [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]])
- Actionable as of 2026-05-29; likely relevant through the next product cycle for teams evaluating agentic coding and large-task orchestration. (uncertainty; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- The source is launch coverage with mixed evidence. It shows that the pattern is operationally promising, but it also notes token cost, quota burn, and conflicting parallel edits, so real-world ROI depends on harness quality and task structure. (uncertainty; [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]])
- Actionable as of 2026-06-04; this is a live organizational pattern, but the article provides only one company case and no independent validation. (uncertainty; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- Evidence is limited to a vendor-published case study, so generalization is uncertain and measured gains are not reported. (uncertainty; [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]])
- Actionable as of 2026-06-05; the source suggests this is already a live engineering shift, though the exact best harness design remains unsettled. (uncertainty; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- The evidence is a roundup synthesis of tweets and product launches, not a controlled comparative study, so it shows direction more than measured causality. (uncertainty; [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]])
- As of 2026-06-07, this is an active product and evaluation direction in the source; its relevance should persist if agentic deployments keep expanding beyond chat UI use cases. (uncertainty; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- The source is a roundup, so the evidence is heterogeneous and mostly announcement-level. It supports the direction of change, but not the maturity or broad adoption of any single implementation. (uncertainty; [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]])
- Actionable as of 2026-06-08; the source presents this as an emerging 2026 pattern rather than a settled norm. (uncertainty; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- The evidence is discourse-heavy and largely practitioner anecdote rather than controlled adoption data, so the breadth of the shift is suggestive rather than proven. (uncertainty; [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]])
- Actionable as of 2026-06-10; this observation reflects a live enterprise adoption pattern in the source and is likely relevant while organizations are still moving from chatbot use to embedded workflow design. (uncertainty; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- This is based on one vendor case study, so it does not prove the pattern is universal or quantify how often workflow redesign outperforms simpler task-level adoption. (uncertainty; [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]])
- Actionable as of 2026-06-12; this is a live engineering pattern in the source, but the exact tooling and best practices may evolve as models improve. (uncertainty; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])
- The source mixes strong operational examples with rhetoric, so the pattern is real but not fully validated across all agent workloads. Several cited systems still depend on benchmark environments, human curation, or vendor-controlled behavior. (uncertainty; [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]])

## Related pages

- agent-tooling-shifts-from-prompting-to-workflow-architecture
- ai-products-shift-from-models-to-systems
- artifact-first-ai-workflows
- enterprise-ai-moves-toward-governed-human-oversight-workflows
- execution-oriented-agents
- harness-design-becomes-more-important-for-agent-reliability
- models-becoming-execution-layers
- persistent-agents
- verification-loops-become-central-to-ai-workflows
- workflow-based-evaluation

## Sources

- [[sources/a-guide-to-agent-native-product-management-every-01krc5a85g6t1qh1y38nt7yzmn|A Guide to Agent-native Product Management - Every]]
- [[sources/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33|AI is approving our pull requests: Here’s how we made it safe]]
- [[sources/ainews-anthropic-raises-965b-series-h-releases-opus-4-8-and-dynamic-workflows-ultracode-01ksrqx88nm20rzp6vm3cbd7y2|[AINews] Anthropic raises $965B Series H, releases Opus 4.8 and Dynamic Workflows/ultracode]]
- [[sources/ainews-google-i-o-2026-gemini-3-5-flash-omni-nanobanana-for-video-spark-background-agents-and-antigravit-01ks1q9kfz8jyg2t8sxed9j4bs|[AINews] Google I/O 2026: Gemini 3.5 Flash, Omni (NanoBanana for Video), Spark (background agents), and Antigravit…]]
- [[sources/ainews-loopcraft-the-art-of-stacking-loops-01ktx5ag5dag2znp3fdp4c7c5y|[AINews] Loopcraft: The Art of Stacking Loops]]
- [[sources/ainews-not-much-happened-today-01ktb8kxqz1915aaav17340cgh|[AINews] not much happened today]]
- [[sources/ainews-rip-pull-requests-2005-2026-01kpagqv8ysqr6n4axvvh6xpcz|[AINews] RIP Pull Requests (2005-2026)]]
- [[sources/ainews-tasteful-tokenmaxxing-01kpw4p15evjfpkqg4pmccnejm|[AINews] Tasteful Tokenmaxxing]]
- [[sources/ainews-the-end-of-finetuning-01krfm1m5y8h163awpkk32925m|[AINews] The End of Finetuning]]
- [[sources/from-data-to-decisions-how-lseg-is-scaling-trusted-ai-01ktrc9qnkbwsc52asg7w7a8xs|From data to decisions: how LSEG is scaling trusted AI]]
- [[sources/how-endava-is-redesigning-software-delivery-around-ai-agents-01kt8x3jzyv9b8kp095aw2p4x2|How Endava is redesigning software delivery around AI agents]]
- [[sources/the-sequence-radar-873-last-week-in-ai-soccer-s-1s-and-supermodels-01ktgwcb0ytk4gvgteb59ksqye|The Sequence Radar #873: Last Week in AI: Soccer, S-1s, and Supermodels]]
- [[sources/wtf-is-a-loop-peter-steinberger-vs-boris-cherny-01kv4td5axnc0n0j86fd9vgxm9|WTF Is a Loop? Peter Steinberger vs. Boris Cherny]]
