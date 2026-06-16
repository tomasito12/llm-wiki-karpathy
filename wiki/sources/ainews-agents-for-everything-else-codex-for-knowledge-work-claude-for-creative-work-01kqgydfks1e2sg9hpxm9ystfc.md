---
title: '[AINews] Agents for Everything Else: Codex for Knowledge Work, Claude for
  Creative Work'
slug: ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-work-01kqgydfks1e2sg9hpxm9ystfc
category: source
tags:
- ai-governance
- ai-operationalization
- continuous-evaluation
- enterprise-ai
- runtime-systems
- verification-over-principles
- workflow-restructuring
source_id: ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-work-01kqgydfks1e2sg9hpxm9ystfc
author: AINews
publication: Substack
published_date: '2026-05-01'
assessed_as_of: '2026-05-01'
ingested_at: '2026-06-07T20:39:45.055354+00:00'
canonical_url: mailto:reader-forwarded-email/3e9240d094814941466d9ad21ac971bc
content_sha256: 56ca82fb9bba31b077f6b28a9b6e8632bbfbb4d04d83297a7d40a8561c8a3e9c
derived_signals:
- signals/2026-05/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-w-computer-use-agents-are-expanding-beyond-coding-into-general-office-fc9cf754d4.md
- signals/2026-05/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-w-security-review-is-becoming-a-product-category-for-model-vendors-f8332c5e29.md
derived_trends:
- industry-trends/ai-products-shift-from-models-to-systems.md
derived_pages:
- industry-trends/ai-products-shift-from-models-to-systems.md
- signals/2026-05/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-w-computer-use-agents-are-expanding-beyond-coding-into-general-office-fc9cf754d4.md
- signals/2026-05/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-w-security-review-is-becoming-a-product-category-for-model-vendors-f8332c5e29.md
---

# [AINews] Agents for Everything Else: Codex for Knowledge Work, Claude for Creative Work

This is a roundup of AI product and model updates, not one deep story. The main theme is that agent tools are spreading beyond coding into general computer work, creative apps, and security tasks. OpenAI’s Codex update is the clearest example: it is being presented as useful for spreadsheets, slides, documents, and planning, not just code. Anthropic is pushing Claude into code review and creative software, while several model releases are competing on benchmarks, cost, and context length. The practical takeaway is that as of 2026-05-01, the interesting work is shifting toward how these systems are packaged and connected to real software, not only how big the base model is.

## Key insights

- Codex is being repositioned from a coding agent to a general computer-use agent with app connections, planning UI, and file editing for office workflows.
- Claude is being pushed in two distinct directions: security scanning for codebases and direct support for creative production tools like Blender, Adobe Creative Cloud, Ableton, and Canva.
- GPT-5.5 is described as strong on long-horizon cyber evaluations, which weakens the claim that Anthropic has a unique lead in offensive cyber automation.
- Qwen3.6 27B stands out as the most important open-weight release because it combines Apache 2.0 licensing, 262K context, and native multimodal input with strong capability-per-size.
- The article repeatedly emphasizes harness engineering, evals, and deployment plumbing as the differentiator for agents, not just raw model scores.

## Derived knowledge pages

- [[industry-trends/ai-products-shift-from-models-to-systems]]
- [[signals/2026-05/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-w-computer-use-agents-are-expanding-beyond-coding-into-general-office-fc9cf754d4]]
- [[signals/2026-05/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-w-security-review-is-becoming-a-product-category-for-model-vendors-f8332c5e29]]

## Why it matters

The piece is useful because it captures where practical AI systems are being productized as of 2026-05-01: general computer-use agents, model-specific harness engineering, security review tools, and workflow integrations for office and creative software. The OpenAI Codex section matters because it is explicitly framed as “for everyone, for any task done with a computer,” and the listed features—faster CUA, responsive browser, planning UI, Microsoft/Google/Salesforce onboarding, and in-app Office file editing—are concrete signs that agent UX is being tuned around everyday software interaction. Anthropic’s Claude Security launch and the support for Blender, Adobe Creative Cloud, Ableton, Splice, Canva, and Affinity show a parallel attempt to wrap models around existing work surfaces rather than asking users to change tools. The benchmark notes on GPT-5.5, GPT-5.5 Pro, and Grok 4.3 matter mainly because they tie capability gains to efficiency and specific tasks such as cyber simulations and GDPval-style work, which is more operationally relevant than headline scores alone. The open-model section is also durable: Qwen3.6 27B’s licensing, context window, and multimodal support make it a concrete candidate for teams evaluating local or self-hosted stacks, even though its inference cost is high. The infrastructure commentary around Cursor, LangChain, and agent collaboration suggests that the bottleneck is increasingly runtime behavior, evaluation, and deployment hygiene. For service automation, the article’s Codex and Claude examples are relevant only insofar as they point to agents handling computer-bound office work and review tasks, but the source does not provide enough evidence to claim customer support or back-office transformation beyond that. Actionable as of 2026-05-01, but the strongest claims are product-launch and benchmark-specific rather than durable general laws.

## Limitations / open questions

Most claims are drawn from launches, benchmark reports, and social posts rather than full technical reports, so the evidence quality is uneven. Several benchmark comparisons depend on proprietary or partially described evals such as GDPval-AA, CritPt, and AA-Omniscience, which limits external interpretability. The Codex and Claude product descriptions do not explain failure modes, latency, security boundaries, or how well these systems handle real enterprise permissions and data isolation. The open-weight model notes give capability, context, and cost signals, but not deployment economics beyond suite-run estimates, so practical adoption cost remains uncertain. The speculative scaling comments about >100T tokens and large GB200 clusters are explicitly conjectural and should not be treated as measured facts.

## Contradictions / unverified claims

The roundup sometimes leans on product framing that is stronger than the underlying evidence, especially when a landing-page repositioning is treated as a major capability shift. Benchmark deltas are described as meaningful, but in several cases the gains are incremental and eval-specific rather than proof of general intelligence improvements. The cyber-eval discussion also shows how fragile frontier narratives are: a single result can change claims about which vendor has the lead, but that depends heavily on the benchmark design. The DeepSeek visual-primitives discussion is interesting, but the repo disappearance and the speculative interpretation of the work make it hard to separate signal from rumor.

## Source metadata

- Canonical URL: mailto:reader-forwarded-email/3e9240d094814941466d9ad21ac971bc
- Raw markdown: `raw/readwise/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-work-01kqgydfks1e2sg9hpxm9ystfc.md`
- Raw HTML: `raw/readwise/ainews-agents-for-everything-else-codex-for-knowledge-work-claude-for-creative-work-01kqgydfks1e2sg9hpxm9ystfc.html`
