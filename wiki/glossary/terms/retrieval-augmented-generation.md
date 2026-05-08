---
title: Retrieval-augmented generation (RAG)
type: glossary-term
created: 2026-05-06
updated: 2026-05-06
tags: [ai-engineering]
---

## Definition

**Retrieval-augmented generation (RAG)** is a pattern where, at **query time**, a system **retrieves** relevant documents or chunks (often via embeddings / vector search), **injects** them into the model’s context, and **generates** an answer conditioned on that retrieved evidence—rather than relying solely on static training data inside the model parameters.

## Usage Notes

A common implementation pipeline: embed the query, **retrieve top-k** chunks, **augment** the prompt with those chunks, then **generate**. Operational quality usually depends heavily on **chunking**, **embedding model choice**, and **retrieval metrics**, not only on the generator model.

## Disagreements

“RAG” is sometimes used narrowly (vector DB + LLM) versus broadly (any retrieve-then-read architecture including keyword/BM25 hybrids, rerankers, or knowledge graphs). Some practitioners argue the term is overloaded once **tool-using agents** also fetch external state.

## Sources

- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8]]
