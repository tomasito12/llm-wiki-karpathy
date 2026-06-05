---
title: Giving Agents Computers — Ivan Burazin, Daytona
slug: giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb
category: source
tags:
- agent-memory
- agent-orchestration
- agent-systems
- ai-evaluation
- context-engineering
- developer-tools
- distribution
- enterprise-ai
- execution-environments
- infrastructure
- infrastructure-economics
- long-running-agents
- platform-strategy
- runtime-architecture
- runtime-systems
- workflow-automation
source_id: giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb
author: Latent.Space
publication: Substack
published_date: '2026-05-21'
assessed_as_of: '2026-05-21'
ingested_at: '2026-06-05T20:03:22.630168+00:00'
canonical_url: mailto:reader-forwarded-email/4376b12461831122fa971a2dbfd2f2cb
content_sha256: 2c241735b4efa8f912e4bd56d8658d4cb044a00edad2fd013013a5cf81db1d33
derived_interview_insights:
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-agents-need-a-computer-shaped-runtime-not-just-code-execution.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-cli-access-can-outperform-api-only-integrations-for-agent-workflows.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-open-source-improves-trust-and-context-more-than-direct-conversion.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-spiky-rl-and-eval-workloads-create-a-different-capacity-planning-problem-than-93ac6af44f.md
- interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-stateful-pause-resume-plus-instant-startup-are-first-order-agent-runtime-requirements.md
---

# Giving Agents Computers — Ivan Burazin, Daytona

This is a conversation about what AI agents need underneath them to actually work. Daytona’s CEO says agents do not just need a code runner; they need a real computer they can control through an API, with state, fast startup, and the ability to pause and resume. The company built this by running on bare metal and using its own scheduler so sandboxes can start quickly and scale in large bursts. The interesting part is the workload shift: agent builders, RL evals, and computer-use systems seem to stress infrastructure in very spiky ways. The article is mainly useful as a practical look at how one infra company is adapting to those needs, not as neutral research.

## Key insights

- For agent workloads, Daytona treats the primitive as a composable computer, not a disposable code-execution box.
- Stateful pause/resume and instant startup are presented as first-order requirements for agent runtimes, especially when tasks need to survive interruptions.
- The company claims its bare-metal design and custom scheduler are what make 60 ms startup and large-scale concurrent sandbox launches possible.
- Burazin says RL/eval workloads changed Daytona’s usage mix sharply, which implies very different capacity-planning behavior from background agent traffic.
- Open source appears to help Daytona most by giving integrators more context and trust, not by directly converting self-hosters into customers.

## Derived knowledge pages

- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-agents-need-a-computer-shaped-runtime-not-just-code-execution]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-cli-access-can-outperform-api-only-integrations-for-agent-workflows]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-open-source-improves-trust-and-context-more-than-direct-conversion]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-spiky-rl-and-eval-workloads-create-a-different-capacity-planning-problem-than-93ac6af44f]]
- [[interview-insights/2026-05/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb-stateful-pause-resume-plus-instant-startup-are-first-order-agent-runtime-requirements]]

## Why it matters

This piece is valuable because it shows how an agent-infrastructure vendor is thinking from first principles about runtime design for AI agents. The core claim is that agents need a computer-shaped abstraction with state, speed, resizing, and multiple operating systems, not just isolated code execution. That distinction matters because it changes what counts as a baseline product feature: a sandbox that can pause, resume, fork, and scale unpredictably becomes more important than a simple container API. The interview also gives concrete operating assumptions: bare metal is used to reduce latency, snapshots are preloaded locally, and the service is optimized for both long-running background agents and highly spiky RL/eval workloads. Those details are operationally useful for anyone comparing sandbox, container, and VM approaches for agent runtimes as of 2026-05-21. The discussion of Windows and macOS support is especially relevant because many real enterprise workflows still live in legacy GUI apps, and the source argues that agents will need access to those environments. The open-source section is also practical: Daytona’s experience suggests that openness can improve trust and integration context without automatically becoming a direct growth engine. The article’s stakes are real for AI infrastructure builders, but the evidence is still mainly vendor-reported, so the claims are better treated as an informed operator’s view than as settled market fact. As of 2026-05-21, the operational lesson is to monitor and selectively adopt these agent-runtime assumptions where your workloads are stateful, spiky, or GUI-bound, rather than assuming a generic container or VM layer is enough.

## Limitations / open questions

Most of the hard numbers come from the company itself, so the 60 ms startup, 50,000-sandbox burst, 850,000 daily runs, and 74% month-over-month growth claims are not independently verified here. The transcript does not provide detailed benchmarking methodology, customer segmentation, or a clear apples-to-apples comparison against competitors, so performance claims are hard to evaluate externally. The economics are also incomplete: CPU, RAM, disk, and network are discussed qualitatively, but pricing, margins, and unit costs are not fully exposed. macOS support is described as difficult because of licensing and concurrency constraints, but there is no concrete shipping plan or technical resolution beyond “fairly soon.” The article argues that agents will need Windows and macOS computers, but it does not show enough evidence that these workloads are already large enough to justify the full product bet beyond the vendor’s customer anecdotes. The future “agent cloud” idea is interesting, but it remains an aspirational architecture, not a validated category definition.

## Contradictions / unverified claims

The strongest claims are also the least independently testable: market leadership, explosive growth, and customer urgency are all described from the vendor’s perspective. The comparison to AWS, Stripe, or a new cloud category is directionally suggestive, but it is still a narrative frame rather than demonstrated market structure. The transcript also leans on large TAM arguments for agentic computer-use, but those estimates depend on assumptions about automation rates and adoption that are not evidenced here. Another tension is that Daytona says open source helps with context and trust, yet it does not materially convert users; that limits how much strategic weight one should put on the open-source posture alone. Overall, the piece is credible as a founder/operator interview, but it should be read as product strategy and market positioning, not as settled proof of a new infrastructure layer.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/4376b12461831122fa971a2dbfd2f2cb
- Raw markdown: `raw/readwise/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb.md`
- Raw HTML: `raw/readwise/giving-agents-computers-ivan-burazin-daytona-01ks648fjsck6wg8fj5zjhj9sb.html`
