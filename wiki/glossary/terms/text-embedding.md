---
title: Text embedding
type: glossary-term
created: 2026-05-06
updated: 2026-05-06
tags: [ai-engineering]
---

## Definition

A **text embedding** is a **dense vector representation** of text produced by an **embedding model**, such that **semantically similar** texts map to **numerically nearby** vectors in that space—enabling similarity search and clustering.

## Usage Notes

Embeddings underpin **semantic search**, **RAG retrieval**, **deduplication**, and many **agent memory** designs. Similarity is typically computed with geometric measures (e.g., cosine similarity) over normalized vectors; “close in embedding space” is a model-dependent notion and can fail on adversarial or domain-shifted inputs.

## Disagreements

Embedding quality varies by **domain**, **language**, and **training objective**; there is no single universal embedding space. Hybrid retrieval (dense + sparse keywords) is often advocated when pure vector search misses exact-token critical evidence.

## Sources

- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8]]
