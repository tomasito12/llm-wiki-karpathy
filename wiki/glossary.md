---
title: Glossary
type: glossary
created: 2026-04-07
updated: 2026-04-25
sources: [How I Stopped My AI Chatbot From making Up Answers.md]
tags: [terminology, style, glossary]
---

# Glossary

Living reference of terms, definitions, and style conventions. The LLM checks this before using any technical term. Updated on every ingest that introduces new or refined terminology.

---

## How to Read This Glossary

Each entry follows this format:

**Term** *(canonical form)*
: Definition. Usage notes. Related terms.
- Preferred: `term` / Avoid: `deprecated term`
- See also: [[related-page]]

---

## Terminology

**Retrieval-Augmented Generation (RAG)** *(canonical form)*
: A system pattern where an LLM retrieves relevant external context before generating an answer, improving factual reliability for domain-specific queries.
- Preferred: `RAG` / Avoid: `memory-only chatbot` for knowledge-critical support use cases
- See also: [[rag-reliability-for-support-chatbots]]

**Hallucination** *(canonical form)*
: A fluent but incorrect or unsupported model output presented as factual.
- Preferred: `hallucination` / Avoid: `creative answer` in support or policy contexts
- See also: [[how-i-stopped-my-ai-chatbot-from-making-up-answers]]

**Chunking** *(canonical form)*
: Splitting documents into retrievable units for embedding and vector search.
- Preferred: `chunking with overlap` / Avoid: `micro-chunks without context`
- See also: [[retrieval-quality-evaluation-checklist]]

**Embedding** *(canonical form)*
: A vector representation of text used to measure semantic similarity during retrieval.
- Preferred: `embedding` / Avoid: `keyword-only matching` as a sole retrieval strategy
- See also: [[retrieval-quality-evaluation-checklist]]

**Vector Search** *(canonical form)*
: Similarity-based retrieval against embedded chunks in a vector index or vector database.
- Preferred: `vector search` / Avoid: `model memory lookup`
- See also: [[rag-reliability-for-support-chatbots]]

---

## Style Conventions

*(Writing rules and tone guidelines specific to this knowledge base's domain. Will populate as style guides and branded content are ingested.)*

| Convention | Rule | Example |
|---|---|---|
| *(none yet)* | | |

---

## Deprecated / Avoid List

Terms that have been replaced, renamed, or should not be used:

| Avoid | Use Instead | Reason |
|---|---|---|
| Bigger model equals better truth | Retrieval quality drives answer reliability | Source emphasizes retrieval quality over model size in business QA contexts |
| Prompting alone fixes factual errors | Retrieval grounding and evaluation loops | Prompting improves style but does not ensure factual correctness |

---

## Regional / Variant Terms

Terms that differ between audiences, teams, or locales:

| Term | Region/Context | Notes |
|---|---|---|
| *(none yet)* | | |

---

## Related Pages

- [[overview]] — big-picture synthesis
- [[index]] — master catalog
- [[how-i-stopped-my-ai-chatbot-from-making-up-answers]] — source summary
- [[rag-reliability-for-support-chatbots]] — chatbot design pattern
- [[ingest-qa-checklist]] — ingest process quality control
