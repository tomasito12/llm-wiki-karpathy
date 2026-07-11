---
title: 'SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development'
slug: sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj
category: source
tags:
- agent-systems
- agentic
- ai-engineering
- ai-evaluation
- ai-operationalization
- cli-tool
- coding
- coding-agents
- context-engineering
- tool-use
- verification-over-principles
- verification-systems
- workflow-based-evaluation
source_id: sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj
author: Jarosław Wasowski
publication: Medium
published_date: '2026-04-30'
assessed_as_of: '2026-04-30'
ingested_at: '2026-06-09T17:29:54+00:00'
canonical_url: https://medium.com/@wasowski.jarek/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-ad1b540b7f75
content_sha256: 1fcd928736309d07f12c6140d01c07922172ed52093fa5a3af8b4554457a0d00
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_glossary:
- glossary/behavior-driven-development.md
- glossary/gherkin.md
derived_tools:
- tools/claude-code.md
derived_topics:
- topics/structured-specification-for-agentic-development.md
- topics/verification-loops-in-ai-workflows.md
derived_trends:
- industry-trends/ai-workflows-shift-toward-verification-loops.md
derived_pages:
- glossary/behavior-driven-development.md
- glossary/gherkin.md
- industry-trends/ai-workflows-shift-toward-verification-loops.md
- tools/claude-code.md
- topics/structured-specification-for-agentic-development.md
- topics/verification-loops-in-ai-workflows.md
---

# SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development

This piece says AI has changed what a software spec is for. Instead of writing long documents that people interpret differently, teams should write short behavior scenarios in Given/When/Then form. Those scenarios are easy for business people to read and clear enough for an AI coding agent to act on. The author’s main point is that BDD sits in the sweet spot between vague requirements and over-detailed design. He also claims AI makes BDD practical by generating the test code that used to make it expensive.

## Key insights

- BDD is presented as the missing specification layer between SRS-level ambiguity and HLD/LLD-level implementation detail.
- A single Given/When/Then scenario is treated as a shared artifact for business review, agent implementation, and executable tests.
- The article’s strongest operational claim is that AI can generate step definitions and test code, which removes BDD’s historical maintenance cost.
- The author frames executable scenarios as living documentation because CI/CD breaks the merge when behavior diverges from the spec.
- The proposed adoption pattern is lightweight: a 30-minute Three Amigos session can replace a much larger chain of handoff documents for features with clear business behavior.

## Derived knowledge pages

- [[glossary/behavior-driven-development]]
- [[glossary/gherkin]]
- [[industry-trends/ai-workflows-shift-toward-verification-loops]]
- [[tools/claude-code]]
- [[topics/structured-specification-for-agentic-development]]
- [[topics/verification-loops-in-ai-workflows]]

## Why it matters

The article is useful because it compresses a common AI-engineering pain point into a specific workflow choice: what should teams write when code is being generated from intent rather than authored directly. Its main contribution is not a new theory of software development, but a practical claim that BDD scenarios are the right abstraction for agent-facing specs because they are concrete enough to reduce ambiguity and still readable to non-engineers. That matters operationally because the author argues traditional SRS/HLD/LLD layers either leave too much undefined for an agent or front-load too much implementation work back onto humans. The article also ties BDD to testing in a way that could reduce duplicate work: one scenario fans out into unit, integration, E2E, UAT, and regression coverage, with CI/CD turning the spec into living documentation. The strongest evidence cited is a case study and a benchmark claim about improved first-attempt code generation from structured scenarios, but the article does not provide full experimental details, so the cost and quality claims should be treated as promising rather than settled. As of 2026-04-30, the piece is actionable for teams already using AI coding tools and willing to standardize on executable behavioral specs; it is less convincing as a universal prescription for all project types. The service automation, voice, and support implications are not discussed, so no broader operational claim is warranted here.

## Limitations / open questions

The evidence base is mixed: the argument combines personal experience, a benchmark claim, historical commentary, and one case study, but it does not present a controlled comparison across teams or domains. The 60–80% cost-reduction estimate is derived from a case study plus assumed project workload math, so it may not generalize beyond features with clear behavioral boundaries. The article assumes AI can reliably generate and maintain step definitions, but it does not address failure modes such as flaky tests, brittle scenario wording, or semantic drift between business language and implementation. Security, privacy, and compliance concerns are mentioned only indirectly through examples like authentication, not analyzed as design constraints. The proposed Three Amigos ritual is lightweight, but the article does not show how it scales to large systems, cross-team dependencies, or long-lived legacy codebases. It also leaves open how to choose among BDD, user stories, OpenAPI, and other specs when the behavior is not easily expressible as concrete scenarios.

## Contradictions / unverified claims

The article’s strongest claim is that BDD is the missing language for AI-era specification, but that may overstate one format’s universality. In practice, many teams already use a mix of user stories, API contracts, design docs, and tests, and the article does not fully show that BDD can replace all of them rather than complement them. The suggestion that AI removes BDD’s main maintenance cost is plausible, but it depends on the quality of generated step definitions and on whether teams trust auto-generated tests enough to keep them. The cost and productivity numbers are directionally interesting, but they are presented in a promotional tone and should be read as illustrative rather than definitive. The claim that the engineer’s role has shifted from coder to contract facilitator is memorable, but it is more of a framing device than a demonstrated industry-wide fact.

## Source metadata

- Canonical URL: https://medium.com/@wasowski.jarek/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-ad1b540b7f75
- Raw markdown: `raw/readwise/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj.md`
- Raw HTML: `raw/readwise/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-01kqz04y32hqhskkq6c3jh3esj.html`

## Full source text

---
readwise_id: 01kqz04y32hqhskkq6c3jh3esj
title: 'SDD Writing Specifications for AI: BDD as the Missing Link — Spec-Driven Development'
author: Jarosław Wasowski
source_url: https://medium.com/@wasowski.jarek/sdd-writing-specifications-for-ai-bdd-as-the-missing-link-spec-driven-development-ad1b540b7f75
category: article
location: archive
published_date: '2026-04-30'
saved_at: '2026-05-06T15:57:48.002000+00:00'
updated_at: '2026-05-06T17:34:03.238445+00:00'
tags:
- processed
publication: Medium
---

In 2026, engineers write specifications, not code, and traditional documents fail for AI-driven development. Behavior-Driven Development (BDD) uses simple scenarios to clearly describe behavior for both humans and AI. A quick weekly meeting called Three Amigos helps teams create specs that save time and improve software quality.
