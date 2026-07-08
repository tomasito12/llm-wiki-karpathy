---
title: Reference IDs
slug: reference-ids
entity_id: glossary:reference-ids
category: glossary
tags:
- context-engineering
first_seen: '2026-05-26'
last_seen: '2026-05-26'
source_count: 1
evidence_count: 4
source_ids:
- stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q
value_level: high
confidence: 0.91
synthesis_state: stage1-placeholder
---

# Reference IDs

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
Reference IDs are unique identifiers attached to generated outputs so each item can be traced back to a specific source record, document, or chunk. They support auditability, debugging, and selective verification in automated workflows.

## Relevance Note

Traceability is central in production AI systems that generate or transform regulated, high-stakes, or user-facing content. Reference IDs make audits, partial retries, and human review much cheaper because reviewers can inspect the exact source behind each output item.

## Evidence / supporting sources

### Stop Using LLMs Like Giant Problem Solvers (2026-05-26)

- In AI workflows, reference IDs let you move from vague quality checks to source-specific checks. Instead of asking whether an output seems reasonable, you can verify that the exact source fragment exists and that the output really points to it. This is especially useful in document extraction, compliance review, and other settings where traceability matters more than fluent prose. Reference IDs also make it easier to retry or repair only the affected items when something goes wrong. (`1fff1aa1d679` · neutral · extended_explanation; [[sources/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q|Stop Using LLMs Like Giant Problem Solvers]])
- Reference IDs are unique identifiers attached to generated outputs so each item can be traced back to a specific source record, document, or chunk. They support auditability, debugging, and selective verification in automated workflows. (`cab8fd495585` · neutral · proposed_definition; [[sources/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q|Stop Using LLMs Like Giant Problem Solvers]])
- Traceability is central in production AI systems that generate or transform regulated, high-stakes, or user-facing content. Reference IDs make audits, partial retries, and human review much cheaper because reviewers can inspect the exact source behind each output item. (`6751e1c0e6c8` · neutral · relevance_note; [[sources/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q|Stop Using LLMs Like Giant Problem Solvers]])
- "A useful design decision was adding reference IDs to every generated rule. This meant that each output item pointed back to a specific source." (`451669e8e951` · supporting · supporting_snippet; [[sources/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q|Stop Using LLMs Like Giant Problem Solvers]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- [[glossary/harness|Harness]]

## Sources

- [[sources/stop-using-llms-like-giant-problem-solvers-01kta19b01w75cp072qdrvrh3q|Stop Using LLMs Like Giant Problem Solvers]]
