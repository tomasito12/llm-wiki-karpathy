---
title: Running Codex safely at OpenAI
slug: running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc
category: source
tags:
- agent-orchestration
- agent-systems
- agentic
- ai-governance
- auditability
- automation-supervision
- cli-tool
- coding-agents
- compliance-systems
- enterprise-ai
- enterprise-managed
- enterprise-workflows
- ide-integrated
- runtime-architecture
- runtime-systems
- software-development
- verification-over-principles
source_id: running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc
author: OpenAI Blog
publication: openai.com
published_date: '2026-05-08'
assessed_as_of: '2026-05-08'
ingested_at: '2026-06-06T15:15:49.839348+00:00'
canonical_url: https://openai.com/index/running-codex-safely
content_sha256: b0af740d415bfda7519022492a55e3ee610eafe37052f9dcc06d867f68defc11
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_tools:
- tools/codex.md
derived_topics:
- topics/agent-native-auditability.md
- topics/approval-based-coding-workflows.md
derived_trends:
- industry-trends/enterprise-ai-moves-toward-governed-human-oversight-workflows.md
derived_pages:
- industry-trends/enterprise-ai-moves-toward-governed-human-oversight-workflows.md
- tools/codex.md
- topics/agent-native-auditability.md
- topics/approval-based-coding-workflows.md
---

# Running Codex safely at OpenAI

This article explains how OpenAI keeps its coding agent, Codex, inside guardrails. The idea is simple: let the agent do routine developer work with little friction, but stop or review anything risky. OpenAI does that with sandboxes, approval rules, network limits, and locked-down credentials. It also records detailed logs so security teams can see not just what Codex did, but why it did it. The practical point is that agent deployment is as much a controls problem as a model problem.

## Key insights

- OpenAI treats sandboxing and approvals as separate controls: one sets the execution boundary, the other decides when an action needs human review.
- Auto-review is used to reduce approval fatigue by auto-approving only low-risk requests, while higher-risk actions still stop for review.
- Managed network policy is selective rather than open-ended: expected destinations are allowed, unfamiliar domains need approval, and some domains can be denied outright.
- Codex identity is tied to secure keyring storage, forced ChatGPT login, and a specific enterprise workspace, which keeps activity inside workspace-level controls.
- Agent-native telemetry is treated as operationally useful, not just compliance data: logs help explain intent, approval outcomes, tool use, and network decisions during security triage.

## Derived knowledge pages

- [[industry-trends/enterprise-ai-moves-toward-governed-human-oversight-workflows]]
- [[tools/codex]]
- [[topics/agent-native-auditability]]
- [[topics/approval-based-coding-workflows]]

## Why it matters

The article is useful because it shows the control stack needed to deploy a coding agent in an enterprise environment without treating autonomy as all-or-nothing. It lays out concrete mechanisms: sandboxed execution paths, approval policy, auto-review for routine requests, managed network allowlists and denylists, workspace-pinned authentication, and rules for safe shell commands. That combination is more operationally durable than a vague call for “human in the loop,” because it separates routine developer actions from actions that should pause for review. The telemetry section is especially practical: OpenTelemetry logs capture prompts, tool approvals, tool outputs, MCP usage, and network decisions, which lets security teams reconstruct intent instead of only seeing that a process ran or a file changed. OpenAI also uses those logs in an internal security triage workflow, suggesting the logs are meant to support real incident response rather than passive auditing. The piece is strongest as an implementation pattern for organizations planning to run coding agents with enterprise security controls, and weaker as evidence about measured security outcomes because it does not provide benchmarks or incident data. As of 2026-05-08, the guidance is actionable for teams evaluating Codex-style deployments, but it should be read as a vendor implementation example rather than proof that this control set is sufficient in all environments.

## Limitations / open questions

The article does not provide benchmark data, failure rates, or evidence that these controls measurably reduce incidents. It also leaves open how fine-grained approval tuning is maintained over time, how false positives in network or command blocking affect developer productivity, and how well the rules scale across different teams and repositories. The auto-review mechanism is described only at a high level, so it is unclear what classes of low-risk actions qualify and how often it may misclassify an action. The telemetry story is strong on visibility but thin on retention, privacy boundaries, and who exactly can access logs across enterprise workspaces. It also does not address whether similar controls are feasible for agents operating in more heterogeneous or less managed environments.

## Contradictions / unverified claims

The post assumes that more policy layers and telemetry will straightforwardly improve safety, but it does not show tradeoffs such as alert fatigue, approval bottlenecks, or misconfigured rules that block legitimate work. The claim that agent-native logs help explain intent is plausible, but the article does not demonstrate that those logs are reliably interpretable in real incidents. The security posture is presented as a clean system, yet in practice the effectiveness of sandboxing, allowlists, and auto-approval depends heavily on configuration quality. The article is strongest as a description of one vendor’s operating model, not as evidence that this is the best or only safe pattern.

## Source metadata

- Canonical URL: https://openai.com/index/running-codex-safely
- Raw markdown: `raw/readwise/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc.md`
- Raw HTML: `raw/readwise/running-codex-safely-at-openai-01kr4j0wpfyavt95avxpff49qc.html`

## Full source text

---
readwise_id: "01kr4j0wpfyavt95avxpff49qc"
title: "Running Codex safely at OpenAI"
author: "OpenAI Blog"
publication: "openai.com"
source_url: "https://openai.com/index/running-codex-safely"
category: "rss"
location: "archive"
published_date: "2026-05-08"
saved_at: "2026-05-08T19:46:19.032000+00:00"
updated_at: "2026-05-09T14:23:04.684725+00:00"
tags: ["processed"]
---

OpenAI runs Codex with strict controls to keep it safe and productive in coding tasks. It uses sandboxing, approval rules, and limited network access to manage Codex actions. Detailed logs help security teams understand and audit Codex’s behavior in real time.
