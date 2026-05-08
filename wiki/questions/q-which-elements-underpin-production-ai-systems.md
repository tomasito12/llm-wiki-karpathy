---
title: Which elements underpin production AI systems?
type: question
created: 2026-05-06
updated: 2026-05-06
tags: [ai-engineering]
---

## Synthesized answer

Production-style LLM systems are usually described—not as “one model call”—but as a small set of recurring pillars that interact:

1. **Tokens and the context window** — Models consume **discrete tokens**, not prose; every interaction has a **hard budget**. Cost, truncation, and “lost” instructions follow from what fits in the window and what gets crowded out.
2. **Embeddings and vector retrieval** — Text is mapped to vectors so **semantic similarity** is geometric (nearest-neighbor search). This enables scalable “find relevant passages” without keyword equality.
3. **RAG** — At query time, retrieve domain-specific chunks, **place them in context**, then generate; the model grounds answers in what was retrieved rather than only parametric priors.
4. **Agentic loops** — **Goal → choose action / tool → observe → repeat** until done; tools extend the system beyond free text but introduce **control** problems (termination, errors, tool overload).
5. **Evals** — **Systematic measurement** (often small golden sets plus binary checks) so changes to prompts, retrieval, tools, or models produce **comparable** before/after signals.
6. **Context engineering** — The cross-cutting practice of **selecting, compressing, ordering, pruning, and structuring** what enters the window so priorities (policy, task definition, evidence) remain **usable** as sessions lengthen.

Sources in this wiki connect these pillars to operational failures (runaway loops, poor retrieval, buried prompts) and to how service-facing automation should be operated.

## Sources

- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8]]
