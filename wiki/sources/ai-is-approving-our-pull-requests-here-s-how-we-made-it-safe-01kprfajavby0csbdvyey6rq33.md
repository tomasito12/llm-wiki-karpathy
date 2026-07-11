---
title: 'AI is approving our pull requests: Here’s how we made it safe'
slug: ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33
category: source
tags:
- ai-governance
- ai-operationalization
- auditability
- enterprise-ai
- software-engineering
- workflow-restructuring
source_id: ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33
author: Kesha Mykhailov
publication: Intercom
published_date: '2026-04-21'
assessed_as_of: '2026-04-21'
ingested_at: '2026-06-07T20:21:22.030115+00:00'
canonical_url: https://www.intercom.com/blog/ai-is-approving-our-pull-requests-heres-how-we-made-it-safe/
content_sha256: 8422f754cd0c194bccb64256dc95d44ed87e252e0e8798c779188ff501275768
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_implementation_studies:
- implementation-studies/2026-04/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33-intercom-s-ai-approved-pull-request-pipeline.md
derived_topics:
- topics/agent-native-auditability.md
- topics/approval-based-coding-workflows.md
derived_trends:
- industry-trends/workflow-restructuring-around-ai-agents.md
derived_pages:
- implementation-studies/2026-04/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33-intercom-s-ai-approved-pull-request-pipeline.md
- industry-trends/workflow-restructuring-around-ai-agents.md
- topics/agent-native-auditability.md
- topics/approval-based-coding-workflows.md
---

# AI is approving our pull requests: Here’s how we made it safe

This article is about letting AI approve some code changes instead of requiring a human reviewer every time. Intercom says the goal is not just speed; it is to avoid the weak review behavior that happens when humans are overloaded. Their system breaks review into several smaller checks, like correctness, safety, and whether the change matches the stated intent. It also refuses to approve large or risky pull requests, which pushes engineers toward smaller changes. Intercom backs the approach with internal data and says every approval is logged for auditability. The main caveat is that code review still cannot catch every production problem, so they are also building tools for live incident diagnosis.

## Key insights

- Intercom treats code review as multiple specialized checks rather than one general judgment, which is a durable design pattern for AI-assisted engineering workflows.
- The system is intentionally strict about PR size, using approval policy to force smaller, easier-to-revert changes.
- Engineer feedback is part of the review loop, so the prompt or guidance is treated as a living operational asset rather than a static policy document.
- The article’s strongest claim is empirical: a controlled pilot reported zero reverts for AI-approved PRs and much faster approval times, but the evidence is internal and company-specific.
- Intercom’s compliance argument depends on traceability: labels, logs, review comments, test results, and merge events are recorded so auditors can inspect the same evidence regardless of whether a human or AI approved the change.

## Derived knowledge pages

- [[implementation-studies/2026-04/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33-intercom-s-ai-approved-pull-request-pipeline]]
- [[industry-trends/workflow-restructuring-around-ai-agents]]
- [[topics/agent-native-auditability]]
- [[topics/approval-based-coding-workflows]]

## Why it matters

The article is useful because it turns AI code review from a vague productivity claim into an operating model with explicit controls: decomposition into sub-reviews, scope limits on large PRs, human override, auditable logs, and continuous feedback from engineers. That combination is more durable than a generic “LLM approves diffs” pitch because it explains how the system is constrained to reduce rubber-stamping rather than amplify it. The internal metrics are the main reason the piece deserves attention: Intercom reports a controlled pilot with zero reverts on AI-approved PRs, faster approval latency, and lower revert rates for AI-authored code than for human-authored code. Even so, the evidence is still a single-company case study, so it shows what one organization claims is possible, not a general benchmark. The article also makes a practical point that human review quality is limited by attention and time, especially when code generation is faster than review capacity. For engineering teams, the interesting takeaway is the design shape: use AI to enforce small changes, trace execution paths, and preserve an audit trail, rather than to replace accountability. The closing implication is narrower: this is relevant to code review and compliance-heavy change management as of 2026-04-21, but it does not solve production-only incidents, so it should be viewed as a partial safety layer rather than a complete automation story.

## Limitations / open questions

The evidence is entirely internal to Intercom, so the reported revert rates and safety gains may depend on its codebase, engineering culture, and review instrumentation. The article does not specify how the review agents are evaluated, how false positives or false negatives are handled, or what failure modes remain after auto-approval. The approval pipeline is described at a high level, but the mechanics of the sub-agents, their prompts, and their confidence thresholds are not disclosed. It is also unclear how much of the reported improvement comes from the AI reviewer versus the broader push to ship smaller batches and modernize the deployment process. Compliance claims are promising, but the article does not show auditor reports or external validation. The article itself notes that PR review cannot catch infrastructure failures, unusual customer behavior, or third-party outages, which limits the scope of what this system can safely replace.

## Contradictions / unverified claims

The piece argues that human review is an imperfect heuristic, yet it still relies on human accountability and optional human override, which suggests the system is augmenting review rather than eliminating it. The claim that AI approval makes shipping safer is plausible in this context, but it depends on the same organization also enforcing small PRs, strong logging, and a roll-back culture. The comparison against human review is interesting but not decisive: humans may have been reviewing under higher load and with less structured guidance, so the baseline is not necessarily a fair universal comparator. The strongest-sounding numbers are internal and early, so they should be read as evidence of a workable implementation rather than proof of general superiority.

## Source metadata

- Canonical URL: https://www.intercom.com/blog/ai-is-approving-our-pull-requests-heres-how-we-made-it-safe/
- Raw markdown: `raw/readwise/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33.md`
- Raw HTML: `raw/readwise/ai-is-approving-our-pull-requests-here-s-how-we-made-it-safe-01kprfajavby0csbdvyey6rq33.html`

## Full source text

---
readwise_id: 01kprfajavby0csbdvyey6rq33
title: 'AI is approving our pull requests: Here’s how we made it safe'
author: Kesha Mykhailov
source_url: https://www.intercom.com/blog/ai-is-approving-our-pull-requests-heres-how-we-made-it-safe/
category: rss
location: archive
published_date: '2026-04-21'
saved_at: '2026-04-21T16:52:35.363000+00:00'
updated_at: '2026-05-07T17:20:49.979279+00:00'
tags:
- processed
publication: Intercom
---

Intercom uses AI to review and approve many pull requests, making shipping faster and safer. Their AI system checks code deeply and enforces small, manageable changes that reduce errors. Data shows AI-approved code has fewer problems than human-reviewed code, proving that speed and safety can grow together.
