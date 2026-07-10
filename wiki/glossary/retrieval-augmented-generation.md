---
title: Retrieval-Augmented Generation
slug: retrieval-augmented-generation
entity_id: glossary:retrieval-augmented-generation
category: glossary
tags:
- memory-systems
- rag
- retrieval
- runtime-architecture
first_seen: '2025-11-17'
last_seen: '2026-05-13'
source_count: 5
evidence_count: 20
source_ids:
- andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw
- everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2
- the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769
- this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g
- why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8
value_level: high
confidence: 0.882
synthesis_state: synthesized
synthesis_stale: false
synthesis_input_hash: 0e7ebbc6a7aa6655
current_input_hash: 0e7ebbc6a7aa6655
synthesis_schema_version: 1
synthesis_prompt_version: 1
last_synthesized_at: '2026-07-09T18:58:44Z'
---

# Retrieval-Augmented Generation

## Executive synthesis

Retrieval-Augmented Generation (RAG) is a pattern where a model answers by retrieving relevant external information at query time and then using that material as context for generation. In practice, that usually means the system searches documents, databases, or an index, pulls back a few relevant chunks, and asks the model to synthesize an answer from them. The main value is grounding: RAG helps when the knowledge is too large to fit in context, changes frequently, or must stay tied to organization-specific sources. The main caveat is that it is not magical memory. If retrieval is weak, the answer can still be weak; stale, poorly chunked, or badly curated sources can degrade output. So RAG is best understood as search plus synthesis, not long-term learning.

## Example in practice

### Support bot answering from policy documents

A support agent asks, “What is our refund policy for annual plans?” The system first searches the product docs and internal policy pages, then retrieves the most relevant passages. The LLM uses those passages to draft an answer and can cite the source snippets. If the policy changes next week, the team updates the source document rather than retraining the model, so the answer can change immediately on the next query.

- Why it helps: This makes the benefit of RAG concrete: the answer comes from current source material, not from what the model happened to memorize, and policy changes can be reflected by updating the knowledge source.

- Basis: `source-grounded`

## Context card

- **Use this page when:** Use this page when you need a compact definition of RAG, want to judge whether it fits a document-grounded or enterprise knowledge workflow, or need to remember its main tradeoff: better grounding and freshness, but dependence on retrieval and source quality.
- **Best for questions about:** What RAG is in plain language, When RAG is a good fit for AI systems, How retrieval, chunking, and synthesis fit together, Why RAG is common in enterprise and support workflows, What RAG does and does not solve
- **Not enough for:** Designing a full RAG architecture, Choosing embedding models, chunk sizes, rerankers, or vector databases, Evaluating retrieval quality with metrics, Solving long-term memory or persistent learning, Claims about performance benchmarks or best-in-class implementations
- **Strongest sources:** Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge, This Open-Source App Turns Your Documents Into a Self-Building Wiki, The ultimate guide to knowledge management for your Sales Agent, 💠🌐 Everyone Is Wrong About NotebookLM
- **Related tags:** memory-systems, rag, retrieval, runtime-architecture

## What to remember

- RAG = retrieve first, then generate from the retrieved context.
- It is useful when facts change often, live in private documents, or are too large for the model’s context.
- Good retrieval and good source curation are part of system quality, not just implementation details.
- It helps grounding and freshness, but it does not automatically create durable memory or deeper understanding.
- Common uses include document Q&A, enterprise search, support bots, and internal assistants.

## Consensus

- RAG means answering a query by first retrieving relevant external information and then generating a response from that retrieved context.
- The retrieved material is usually pulled from documents, databases, search indexes, or other curated knowledge sources.
- It is commonly used when facts change often, when the source material is too large for the model’s context, or when answers need to stay grounded in private or organization-specific information.
- In production systems, retrieval quality, chunking/segmentation, and source quality can matter as much as the model itself.
- RAG is widely used for document Q&A, internal knowledge search, support bots, enterprise assistants, and similar knowledge-grounded workflows.

## Tensions / open questions

- RAG improves freshness and grounding, but it often re-derives the answer each time instead of building persistent understanding across related questions.
- Sources present RAG as a stateless lookup pattern that is excellent at finding information but weak at building structure or memory.
- The term is sometimes used broadly for many document-grounded systems, but the reviewed sources emphasize a fairly standard pattern: retrieve first, then generate.
- There is a practical tension between easier updating and better auditability on one side, and dependence on retrieval quality on the other.

## Evidence quality

- High agreement across five sources on the core definition and typical workflow.
- Evidence is strong for practical use cases in document Q&A, enterprise assistants, and support workflows.
- Evidence is moderate for limitations: several sources agree that retrieval quality and source quality are critical, but they do not provide quantitative evaluation.
- The sources are recent and consistent, but this page is still a synthesis of descriptive explanations rather than experimental evidence.

## Practical takeaway

Use RAG when the answer should come from current, curated, or private source material; do not treat it as a substitute for good document organization, retrieval design, and source maintenance.

## Evidence index

- Sources: 5
- Evidence items: 20
- Current input hash: `0e7ebbc6a7aa6655`
- Cached input hash: `0e7ebbc6a7aa6655`
- Last synthesized: 2026-07-09T18:58:44Z
- Synthesis status: `fresh`

## Related pages

- [[glossary/knowledge-management|Knowledge Management]]

## Sources

- [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]]
- [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]]
- [[sources/the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769|The ultimate guide to knowledge management for your Sales Agent]]
- [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]]
- [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]]
