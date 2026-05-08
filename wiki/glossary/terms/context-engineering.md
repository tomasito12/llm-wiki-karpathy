---
title: Context engineering
type: glossary-term
created: 2026-05-06
updated: 2026-05-06
tags: [ai-engineering]
---

## Definition

**Context engineering** is the practice of deciding **what information** is placed into an LLM’s **context window**, **how it is structured** (sections, labels, ordering), and **what is omitted**, so that policies, goals, and evidence remain **actionable** as conversations or runs grow long.

## Usage Notes

Contrasts with **prompt engineering** in scope: context work spans retrieved documents, tool outputs, conversation history, system instructions, and compression/summarization—not only the final user message. Tactics include **selection**, **compression**, **ordering** (notably mitigating “lost in the middle” effects in long contexts), **pruning**, and consistent **formatting**.

## Disagreements

Some teams collapse “context engineering” into prompt tuning; others treat it as a broader **systems** responsibility owned jointly by retrieval, agent orchestration, and observability. The boundary with **RAG** is porous: retrieval decides *candidate* content; context engineering decides *what actually ships* in the assembled prompt.

## Sources

- [[sources/6-ai-concepts-you-must-master-to-build-production-ready-ai-systems-01kqfz8qd4s3rz9n6sx9dma9a8]]
