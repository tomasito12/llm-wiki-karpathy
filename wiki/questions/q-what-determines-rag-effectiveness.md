---
title: What determines RAG effectiveness?
type: question
created: 2026-05-06
updated: 2026-05-06
tags: [ai-engineering]
---

## Synthesized answer

RAG quality is **bounded by retrieval**: if the model never sees the right evidence, better generation mostly yields confident wrong answers. In practice, **embedding choice**, **chunking strategy** (size, boundaries, overlap), and **evaluation of “did we fetch the right chunk?”** tend to dominate over prose-only prompt tweaks—especially when tables, lists, or procedures split awkwardly across chunks. Hallucination can still occur when retrieved text is ambiguous or insufficient; grounding reduces but does not eliminate that risk.

## Sources

- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8]]
