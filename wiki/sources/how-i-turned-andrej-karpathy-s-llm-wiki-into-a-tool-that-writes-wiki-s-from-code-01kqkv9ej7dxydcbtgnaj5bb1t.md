---
title: How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from
  code
slug: how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t
category: source
tags:
- execution-oriented-agents
- knowledge-systems
- workflow-restructuring
source_id: how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t
author: Balu Kosuri
publication: Medium
published_date: '2026-04-17'
assessed_as_of: '2026-04-17'
ingested_at: '2026-05-22T16:24:01.156554+00:00'
canonical_url: https://medium.com/@k.balu124/how-i-turned-andrej-karpathys-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-cfb7f73afa52
content_sha256: 6347fd613475869e22dd07440cacb1922edd49b41b060eb0754972ee55ce5b00
derived_how_to:
- how-to/commit-driven-documentation-sync.md
derived_topics:
- topics/citation-locked-ai-documentation.md
- topics/commit-driven-documentation-generation.md
derived_trends:
- industry-trends/agent-maintained-documentation-pipelines.md
derived_pages:
- how-to/commit-driven-documentation-sync.md
- industry-trends/agent-maintained-documentation-pipelines.md
- topics/citation-locked-ai-documentation.md
- topics/commit-driven-documentation-generation.md
---

# How I turned Andrej Karpathy’s LLM Wiki into a tool that writes wiki’s from code

This article is about a tool that helps documentation keep up with code changes. The idea is simple: every time a developer saves work and makes a git commit, a background agent reads what changed and updates a wiki automatically. Instead of writing and maintaining docs by hand all the time, the team gets a draft that is grounded in the code. The tool is designed for internal use, such as developer documentation, library docs, and notes for small teams. It is not meant to replace a technical writer, because a human is still needed for judgment, voice, and final review. The author also explains safeguards that reduce mistakes, like forcing citations and checking whether the code has changed since a page was written. Some kinds of code are harder to document this way, especially user interface code where behavior depends on what happens at runtime. As of 2026-04-17, the idea looks practical for internal documentation workflows, but it still needs human oversight.

## Key insights

- Using git commit as the trigger keeps documentation at most one commit behind the code, which is a tighter loop than manual doc upkeep.
- A citation rule of “cite or do not claim” plus freshness checks turns doc drift into a visible maintenance problem instead of silent decay.
- The template is configurable by doc type, so teams can choose internal architecture pages, API references, user drafts, decisions, or concepts without changing code.
- The weakest cases are UI-heavy systems and large refactors, where the source code does not fully explain runtime behavior and the agent can misread renames.
- The tool is positioned as a draft-and-review workflow, not as a writer replacement or a source of customer-ready documentation.

## Derived knowledge pages

- [[how-to/commit-driven-documentation-sync]]
- [[industry-trends/agent-maintained-documentation-pipelines]]
- [[topics/citation-locked-ai-documentation]]
- [[topics/commit-driven-documentation-generation]]

## Why it matters

This piece is useful because it turns documentation maintenance into an operational workflow instead of a manual side task. The main pattern is commit-driven documentation generation: code changes become the trigger for doc updates, which reduces the time gap between implementation and explanation. That is a durable idea for teams that struggle with stale README files, internal references, and API notes. The article is also explicit about the failure modes: code that does not narrate runtime behavior invites hallucination, so citation discipline and freshness checks become part of the documentation system itself. The configurable doc-type setup is practical because different repos need different output mixes, and one rigid format would not fit every codebase. Actionable as of 2026-04-17, this is a promising internal-doc automation pattern, but the source supports a review-first posture rather than full automation. For service automation specifically, the article does not discuss support flows in depth; the closest implication is that the same draft-and-review model could help keep internal runbooks and support-facing references synchronized with code, but that remains an inference rather than a demonstrated case.

## Limitations / open questions

The source is a personal build description, not a measured deployment study, so it does not give success metrics, adoption data, or error rates. UI-heavy apps are explicitly called out as a weak case because runtime behavior is hard to infer from source code alone. Large diffs above 2000 lines are skipped by default, which avoids cost but leaves open how well the system handles major refactors. Renames are only heuristically detected, so correctness depends partly on commit subjects and git metadata. The article also notes that the wiki is not a single source of truth and does not replace review or broader documentation systems.

## Contradictions / unverified claims

The strongest claims are moderated by the author’s own caveats: the system reduces hallucinations but does not eliminate them, and it documents code rather than judging whether the code is good, secure, or simple. The notion that a wiki can “maintain itself” is therefore more of an automation goal than a literal outcome. The article is honest that generated output still needs human review, especially for customer-facing or UI-driven documentation.

## Source metadata

- Canonical URL: https://medium.com/@k.balu124/how-i-turned-andrej-karpathys-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-cfb7f73afa52
- Raw markdown: `raw/readwise/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t.md`
- Raw HTML: `raw/readwise/how-i-turned-andrej-karpathy-s-llm-wiki-into-a-tool-that-writes-wiki-s-from-code-01kqkv9ej7dxydcbtgnaj5bb1t.html`
