---
title: 'Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human
  review — Ryan Lopopolo, OpenAI Frontier & Symphony'
slug: extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy
category: source
tags:
- agent-systems
- ai-engineering
- coding-agents
- developer-tooling
- runtime-architecture
- test-and-verification
- workflow-design
source_id: extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy
author: Latent Space
publication: Latent
published_date: '2026-04-07'
assessed_as_of: '2026-04-07'
ingested_at: '2026-06-05T16:17:02.989387+00:00'
canonical_url: https://www.latent.space/p/harness-eng
content_sha256: ccef8a231ac0f42e08a2c8753a60adb2f0ccc0e9e00c7643ed630023dcb748c7
derived_interview_insights:
- interview-insights/2026-04/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-fast-build-loops-and-agent-legible-repos-matter-more-than-human-frien-4b4f024150.md
- interview-insights/2026-04/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-harness-engineering-treats-human-attention-as-the-scarce-resource-4bd55e8f88.md
---

# Extreme Harness Engineering: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony

This piece is about how one OpenAI team changed software development so the model does almost all the coding work. The big idea is not just better prompts; it is building a whole harness around the model so it can build, test, review, and merge with minimal human touch. Ryan Lopopolo calls this “harness engineering.” The team focused on fast builds, clear specs, observability, and agents that can inspect their own work. It is interesting because it shows how much of the job can move from typing code to designing the system that guides the model. As of 2026-04-07, it is a useful example for people building agent-heavy engineering workflows, but it is still one team’s experience, not a general proof.

## Key insights

- The team treated human attention as the main bottleneck and redesigned the workflow so agents, not people, could stay in the inner loop.
- Fast builds mattered operationally: the team pushed the build loop under one minute because background shells and longer-running tasks made the model less effective.
- Markdown specs, skills, tests, and review agents were used to encode engineering taste and non-functional requirements into text the model can consume.
- Symphony is described as a coordination layer that can spin up, supervise, rework, and merge many coding-agent tasks without constant human terminal presence.
- The article’s strongest reusable pattern is to make software agent-legible first and human-legible second, while keeping humans for the hardest white-space or net-new problems.

## Derived knowledge pages

- [[interview-insights/2026-04/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-fast-build-loops-and-agent-legible-repos-matter-more-than-human-frien-4b4f024150]]
- [[interview-insights/2026-04/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-harness-engineering-treats-human-attention-as-the-scarce-resource-4bd55e8f88]]

## Why it matters

The piece is useful because it gives a concrete operating model for agent-heavy software development: don’t just add a coding model to a normal repo, redesign the repo, build system, review path, and documentation so the model can complete the whole task loop. Ryan’s account is especially grounded in implementation detail: build times, background shells, worktrees, merge queues, review agents, markdown trackers, and observability all become part of the product surface for the agent. The article also highlights a practical distinction between tasks that are still hard for models—new product ideas and gnarly refactors—and tasks that become much cheaper once the harness is good, such as sideways migrations, dependency internalization, and repeatable fixes. Another durable takeaway is that the harness itself becomes a knowledge base: each failure is treated as missing context, missing capability, or missing structure, then folded back into docs, skills, tests, or prompts. The Symphony layer adds a second reusable abstraction: orchestration of many agents is not just a larger single-agent problem, but a coordination problem with its own supervisor, rework, and review states. The enterprise angle is meaningful because Frontier is framed as a platform for observable, governed agents that can plug into company tools and security controls, which makes the workflow discussion more than a local engineering curiosity. The stakes are still narrower than the marketing tone suggests, because the evidence is one team’s internal experiment and not a comparative study. As of 2026-04-07, the pattern looks actionable for teams already operating with coding agents, but it should be adopted as an engineering experiment, not as settled doctrine.

## Limitations / open questions

The evidence is almost entirely a first-person interview about one greenfield internal project, so the article does not establish general performance gains across teams or codebases. The reported outcomes rely on anecdotes like PR volume, codebase size, and faster loops, but there is no independent measurement of defect rates, maintainability, security, or total cost of ownership. The zero human-written and zero human-reviewed framing is provocative, but the transcript still describes human-set constraints, human release approval, smoke tests, and humans deciding when to add structure or escalate issues. It is also unclear how transferable the approach is to legacy repositories, highly regulated systems, or teams that cannot tolerate rapid refactors and repo-wide architectural changes. The economics of spending more than one billion tokens per day are mentioned, but only as a rough estimate; the source does not compare that spend to alternative engineering methods. The enterprise/security story is promising but underspecified: there is little detail on failure modes, authorization boundaries, auditability, or how safety specs are enforced in practice.

## Contradictions / unverified claims

The strongest claims are also the hardest to validate. Saying human review is no longer needed before merge sounds like a major departure from normal software practice, but the source gives little detail on how correctness, security, and regressions are controlled at scale beyond the same agents and a final human release step. The argument that dependencies can be internalized or vendored quickly is plausible for smaller packages, but the article itself admits scale testing and security are the main counterweights. The suggestion that code should be written primarily for the model can conflict with human maintainability, especially in mixed human-agent teams, and the article acknowledges that the repo became highly decomposed to prevent people from trampling each other. The “ghost libraries” and spec-driven reproduction story is compelling, but it reads more like a prototype workflow than a proven distribution model.

## Source metadata

- Canonical URL: https://www.latent.space/p/harness-eng
- Raw markdown: `raw/readwise/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy.md`
- Raw HTML: `raw/readwise/extreme-harness-engineering-1m-loc-1b-toks-day-0-human-code-0-human-review-ryan-lopopolo-openai-frontier-symphony-01knmf4r6yqgf92rpgng02z3wy.html`
