---
title: Spec Driven Development — Three Maturity Levels Every AI Team Should Know
slug: spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w
category: source
tags:
- agent-orchestration
- agent-systems
- ai-engineering
- ai-operationalization
- cli-tool
- coding
- coding-agents
- context-engineering
- open-source
- verification-systems
- workflow-design
- workflow-restructuring
source_id: spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w
author: Jarosław Wasowski
publication: Medium
published_date: '2026-04-30'
assessed_as_of: '2026-04-30'
ingested_at: '2026-06-09T17:40:29+00:00'
canonical_url: https://medium.com/@wasowski.jarek/spec-driven-development-three-maturity-levels-every-ai-team-should-know-648c93cf1e1d
content_sha256: b7d8284f3e77495ab5441e1dba3757aab42451844aa4a1fdca329379f6d2ac7d
derived_glossary:
- glossary/living-specification.md
- glossary/specification-drift.md
derived_how_to:
- how-to/spec-anchored-development.md
derived_tools:
- tools/github-spec-kit.md
derived_topics:
- topics/agent-specification-bidirectionality.md
- topics/structured-specification-for-agentic-development.md
derived_trends:
- industry-trends/ai-coding-moves-from-prompting-to-persistent-specs.md
derived_pages:
- glossary/living-specification.md
- glossary/specification-drift.md
- how-to/spec-anchored-development.md
- industry-trends/ai-coding-moves-from-prompting-to-persistent-specs.md
- tools/github-spec-kit.md
- topics/agent-specification-bidirectionality.md
- topics/structured-specification-for-agentic-development.md
---

# Spec Driven Development — Three Maturity Levels Every AI Team Should Know

This article says AI coding has three levels of maturity. The first level uses files like CLAUDE.md to guide the model, but those instructions often get stale after the feature ships. The second level keeps a living spec in the repo and updates it as code changes, so the model has a durable contract instead of a one-time prompt. The third level goes further and treats code as generated from the spec, but the author says that is still a horizon rather than the safest target. The core idea is simple: if the AI loses context between sessions, keep the important context in a persistent, machine-readable spec.

## Key insights

- A repo-local specification matters more than a large prompt file because it can be updated bidirectionally after implementation, not just used once at the start.
- The article’s strongest operational claim is that moving requirements from chat into a persistent file recovered 90% of lost faithfulness in the SLUMP benchmark.
- Level 1 SDD is already happening in teams using CLAUDE.md, .cursorrules, or AGENTS.md, but it does not prevent spec drift after shipping.
- The safest boundary is to specify what the system must do and the constraints it must respect, not line-by-line implementation details.
- The article treats spec-as-source as aspirational and explicitly warns that over-heavy specification systems can collapse into the same problems that killed MDA.

## Derived knowledge pages

- [[glossary/living-specification]]
- [[glossary/specification-drift]]
- [[how-to/spec-anchored-development]]
- [[industry-trends/ai-coding-moves-from-prompting-to-persistent-specs]]
- [[tools/github-spec-kit]]
- [[topics/agent-specification-bidirectionality]]
- [[topics/structured-specification-for-agentic-development]]

## Why it matters

The piece is useful because it compresses a messy debate about AI-assisted coding into a practical maturity model with clear operational differences. Its most durable contribution is the distinction between a prompt-like spec and a living specification that is versioned in the repo, updated from implementation, and used as a contract for tests and documentation. That distinction is directly relevant for teams using agents across sessions, since the author argues that the main failure mode is specification drift rather than model incapacity alone. The article also gives a concrete migration target: move from spec-first habits to spec-anchored workflows where the spec is the source of truth and implementation feedback flows back into it. The evidence is mixed but nontrivial, combining benchmark results, product examples, and security data; the strongest claims are benchmark-based, while the more ambitious vision of code-as-source remains unproven. As of 2026-04-30, the practical advice is to adopt the persistent-spec pattern where you already have multi-step AI workflows, and to treat spec-as-source as experimental rather than default. For support, voice, meetings, or back-office automation, the article has no substantive discussion, so those implications are not supported here.

## Limitations / open questions

The article leans heavily on benchmarks and selected examples, but it does not provide full experimental details, replication methods, or failure rates for the cited systems. The SLUMP result is compelling as presented, yet it is one study and the article does not show how well the effect generalizes across codebases, domains, or team sizes. The Constitutional SDD banking result is promising, but the implementation context is narrow and the operational cost of maintaining the constitution is not analyzed. The article acknowledges that complex compositional specifications can have high error rates, but it does not quantify where the line lies between useful constraints and harmful over-specification. The spec-as-source vision lacks production evidence in the article, so its economics, maintenance burden, and debugging workflow remain open questions.

## Contradictions / unverified claims

The piece argues that specs should be living contracts, but many of its examples still rely on human discipline to keep the spec current, which is the hard part in practice. Kent Beck’s and François Zaninotto’s objections are taken seriously, and they point to a real tension: the more complete the spec, the more likely it becomes bureaucratic and brittle. The article’s confidence in Level 2 is stronger than its evidence base would justify in every setting, especially because the cited gains come from specific benchmarks and one banking example. Its comparison to waterfall is directionally helpful but simplified; a bidirectional spec reduces drift, but it does not eliminate ambiguity, organizational churn, or poor judgment. The spec-as-source layer is the most speculative part, and the article itself concedes that rushing to micromanage implementation would recreate the failures of MDA.

## Source metadata

- Canonical URL: https://medium.com/@wasowski.jarek/spec-driven-development-three-maturity-levels-every-ai-team-should-know-648c93cf1e1d
- Raw markdown: `raw/readwise/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w.md`
- Raw HTML: `raw/readwise/spec-driven-development-three-maturity-levels-every-ai-team-should-know-01kr432t128r5x0bvxwskbtd1w.html`
