---
title: Stop Using LLMs Like Giant Problem Solvers
slug: stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q
category: source
tags:
- ai-engineering
- ai-operationalization
- auditability
- context-engineering
- enterprise-ai
- orchestration
- verification-systems
- workflow-design
- workflow-restructuring
source_id: stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q
author: Clara Chong
publication: Medium
published_date: '2026-05-26'
assessed_as_of: '2026-05-26'
ingested_at: '2026-06-10T16:15:26+00:00'
canonical_url: https://towardsdatascience.com/stop-using-llms-like-giant-problem-solvers/
content_sha256: 8b8c90ce2e273ca124cef8c7f848d9377a9a1d07f84bdac9fa67d3e98e4e884e
derived_glossary:
- glossary/checkpointing.md
- glossary/reference-ids.md
derived_topics:
- topics/agent-native-auditability.md
- topics/ai-workflow-restructuring.md
derived_trends:
- industry-trends/ai-products-shift-from-models-to-systems.md
derived_pages:
- glossary/checkpointing.md
- glossary/reference-ids.md
- industry-trends/ai-products-shift-from-models-to-systems.md
- topics/agent-native-auditability.md
- topics/ai-workflow-restructuring.md
---

# Stop Using LLMs Like Giant Problem Solvers

This piece is about a practical way to make LLM systems less fragile. The author tried to extract structured rules from messy PDF documents and found that asking an agent to do everything at once produced plausible but unreliable results. The fix was to shrink the model’s job and let code handle the mechanical parts like validation, IDs, retries, and progress tracking. The main idea is simple: the model should handle semantic judgment, while the surrounding system keeps the work traceable and controllable. That makes the pipeline easier to audit and safer to run on large messy inputs. As of 2026-05-26, this is a durable engineering pattern rather than a one-off trick.

## Key insights

- Shrinking the agent’s task was more effective than improving the prompt, toolchain, or agent harness.
- Reducing retrieval uncertainty matters when the model must reason over content; do not also make it guess whether it has the right inputs.
- Processing one document at a time made failures isolated, retries cheap, and checkpoints useful for resuming work.
- Reference IDs turned vague quality checks into specific source-level audits.
- Lightweight manual evals can still be worthwhile when a full golden dataset is impractical, but they do not provide strong benchmark evidence.

## Derived knowledge pages

- [[glossary/checkpointing]]
- [[glossary/reference-ids]]
- [[industry-trends/ai-products-shift-from-models-to-systems]]
- [[topics/agent-native-auditability]]
- [[topics/ai-workflow-restructuring]]

## Why it matters

The article is useful because it shows a concrete way to move from fragile LLM demos to workflows that can be inspected and repaired. Its main contribution is architectural rather than model-specific: prepare inputs ahead of time, remove irrelevant context, split work into smaller units, and keep deterministic code responsible for schema, IDs, logging, caching, and validation. That separation of duties is a durable pattern for any extraction or transformation job where the model must make semantic judgments but the system still needs traceability. The reference-ID idea is especially practical because it converts output review from a subjective read into a source-backed audit. The author’s emphasis on manual sampling and small-batch checks is also a sober reminder that evaluation quality matters when the corpus is large and a gold set is unavailable. The stakes here are real for structured extraction pipelines, but the article stays focused on one implementation case rather than proving a general benchmark result. For code-heavy document workflows, the lesson is actionable as of 2026-05-26; for broader claims about all LLM systems, the evidence here is still limited and should be treated as a strong pattern, not a universal rule.

## Limitations / open questions

The article does not share the exact implementation, so the most useful details are descriptive rather than reproducible. It is also a single first-person case study, not a comparative benchmark, so it does not establish how much each change contributed or whether the same approach would hold across other document types. Manual sampling and lightweight evals help, but they leave open how to measure recall, nuance preservation, and error rates at scale. The local staging approach may not be practical in all environments, and the article does not discuss cost, latency, security, or privacy tradeoffs for storing source data locally. It also does not specify how the orchestrator decided when to retry, how reference traces were enforced, or how downstream deterministic evaluation handled ambiguous cases.

## Contradictions / unverified claims

The framing that the workflow became better mainly by changing the shape of the problem is persuasive, but it is still a single anecdotal case. Claims like “five subagents” and “another agent to selectively run audits” sound operationally useful, yet the article gives no measured comparison against simpler alternatives. The suggestion to keep the model away from retrieval uncertainty is sensible, but the text does not show whether a stronger retrieval layer could have solved some of the same issues. The piece also leans on auditability as the main reliability lever; that helps inspection, but it is not the same as proving correctness.

## Source metadata

- Canonical URL: https://towardsdatascience.com/stop-using-llms-like-giant-problem-solvers/
- Raw markdown: `raw/readwise/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q.md`
- Raw HTML: `raw/readwise/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q.html`
