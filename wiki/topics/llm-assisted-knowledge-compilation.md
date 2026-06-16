---
title: LLM-Assisted Knowledge Compilation
slug: llm-assisted-knowledge-compilation
entity_id: topic:llm-assisted-knowledge-compilation
category: topic
tags:
- agent-systems
- ai-engineering
- knowledge-systems
first_seen: '2026-04-19'
last_seen: '2026-04-21'
source_count: 2
evidence_count: 17
source_ids:
- i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769
- karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr
value_level: high
confidence: 0.965
synthesis_state: stage1-placeholder
---

# LLM-Assisted Knowledge Compilation

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A useful pattern is to treat source materials as raw inputs and ask an LLM to compile them into a structured, cross-referenced knowledge base. The compiled layer should not replace the originals; it should synthesize them into durable pages that can be updated as new sources arrive. This shifts the model's role from answering isolated questions to maintaining accumulated understanding over time. The workflow is most valuable when the knowledge domain benefits from repeated synthesis across many documents rather than one-off retrieval.

## Examples

The article describes compiling raw sources into markdown pages, with one source touching "10 to 15 wiki pages" and query answers sometimes being filed back as new pages.

## Key Points

- Keep raw sources immutable so the compiled layer can always be regenerated.
- Treat cross-references and page updates as part of the ingest process.
- Use the compiled artifact for later questions so the model reads synthesized pages instead of re-discovering fragments every time.
- File valuable query answers back into the wiki so the corpus compounds over time.
- Raw documents stay immutable while generated pages evolve over time.
- Compilation happens once during ingest, so repeated queries can reuse synthesized structure.
- Provenance and linting are the controls that keep the compiled knowledge trustworthy.
- Cross-references between pages matter because they preserve relationships that chunking can destroy.

## Operational Insight

Use the model to produce a maintained artifact, not just answers. That means investing in page structure, link conventions, and review loops so the output can be reused across future questions.

## Related Topics

- two-step-document-ingest
- provenance-tracking
- wiki-schema-governance

## Evidence / supporting sources

### I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me. (2026-04-19)

- The article describes compiling raw sources into markdown pages, with one source touching "10 to 15 wiki pages" and query answers sometimes being filed back as new pages. (`c676dd695d5a` · neutral · examples; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- A useful pattern is to treat source materials as raw inputs and ask an LLM to compile them into a structured, cross-referenced knowledge base. The compiled layer should not replace the originals; it should synthesize them into durable pages that can be updated as new sources arrive. This shifts the model's role from answering isolated questions to maintaining accumulated understanding over time. The workflow is most valuable when the knowledge domain benefits from repeated synthesis across many documents rather than one-off retrieval. (`c9e88175263f` · neutral · knowledge_summary; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Use the model to produce a maintained artifact, not just answers. That means investing in page structure, link conventions, and review loops so the output can be reused across future questions. (`3ea113b67013` · neutral · operational_insight; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- This pattern matters because many AI workflows fail when they stop at retrieval and never create a durable synthesized layer. Compiled knowledge bases can make research, internal documentation, and agent memory more reusable because each new source can strengthen the whole corpus rather than sit in isolation. (`363e3b77bb1f` · neutral · relevance_note; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Keep raw sources immutable so the compiled layer can always be regenerated. (`3264d9aeb3fa` · supporting · key_points[0]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Treat cross-references and page updates as part of the ingest process. (`2473ea3e40b5` · supporting · key_points[1]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- Use the compiled artifact for later questions so the model reads synthesized pages instead of re-discovering fragments every time. (`ecedc99e94df` · supporting · key_points[2]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- File valuable query answers back into the wiki so the corpus compounds over time. (`0d928a8c8f68` · supporting · key_points[3]; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])
- "instead of you maintaining a knowledge base and occasionally asking AI questions about it, the LLM builds and maintains the entire knowledge base for you." (`8fba60764ab8` · supporting · supporting_snippet; [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]])

### Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over (2026-04-21)

- LLM-assisted knowledge compilation is a workflow where the model turns raw documents into a structured knowledge base instead of answering each query from scratch. The important shift is that synthesis happens during ingestion, so later queries can read integrated pages rather than reassembling context fragments under time pressure. This pattern depends on separating source material from generated output, tracking provenance, and using a schema to control what gets written. It is most useful when the goal is durable, queryable understanding across a bounded corpus rather than one-off chat responses. (`ab1964128935` · neutral · knowledge_summary; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Treat the model as a compiler for accumulated knowledge, not as a search engine for every question. That framing changes the system design: source files become immutable inputs, generated pages become maintained artifacts, and linting becomes part of the workflow. (`f38ea8812016` · neutral · operational_insight; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- This matters for AI engineering because many knowledge workflows fail by redoing synthesis at query time instead of preserving it. The pattern is durable wherever teams need accumulated understanding across documents, notes, tickets, or research without relying on human memory or chat logs. (`ce64729c5f3f` · neutral · relevance_note; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Raw documents stay immutable while generated pages evolve over time. (`5797e752ee25` · supporting · key_points[0]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Compilation happens once during ingest, so repeated queries can reuse synthesized structure. (`f7dab985a15b` · supporting · key_points[1]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Provenance and linting are the controls that keep the compiled knowledge trustworthy. (`46455ce90c2a` · supporting · key_points[2]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- Cross-references between pages matter because they preserve relationships that chunking can destroy. (`8f9f514b1324` · supporting · key_points[3]; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])
- "Treat your raw documents the way a compiler treats source code." (`84bf93b4b00b` · supporting · supporting_snippet; [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- provenance-tracking
- two-step-document-ingest
- wiki-schema-governance

## Sources

- [[sources/i-used-karpathy-s-llm-wiki-to-build-a-research-brain-that-updates-itself-here-s-what-two-weeks-taught-me-01kqkv78qyrcbmcnbttz4ae769|I Used Karpathy’s LLM Wiki to Build a Research Brain That Updates Itself. Here’s What Two Weeks Taught Me.]]
- [[sources/karpathy-s-llm-wiki-how-to-actually-use-ai-so-it-stops-starting-over-01kqktnemtp7dbmtzfbef6h1hr|Karpathy’s LLM Wiki: How to Actually Use AI So It Stops Starting Over]]
