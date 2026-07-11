---
title: Build a RAG agent with LangChain
slug: build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1
category: source
tags:
- agent-orchestration
- ai-engineering
- ai-safety
- context-engineering
- retrieval-systems
- workflow-design
source_id: build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1
author: Docs by LangChain
publication: Langchain
ingested_at: '2026-06-06T21:43:58+00:00'
canonical_url: https://docs.langchain.com/oss/python/langchain/rag
content_sha256: d0de89e58c39ad43ea38affc88080295b5daf3e557a36dba94c3b9ee23d85537
source_text_available: true
source_text_mode: full
source_text_source: raw_markdown
derived_how_to:
- how-to/two-step-document-ingestion.md
derived_topics:
- topics/prompt-injection-defensive-context-handling.md
- topics/rag-orchestration-patterns.md
derived_pages:
- how-to/two-step-document-ingestion.md
- topics/prompt-injection-defensive-context-handling.md
- topics/rag-orchestration-patterns.md
---

# Build a RAG agent with LangChain

This page explains how to build a question-answering app that looks up information in a document before answering. It uses one blog post as the example source. You can do this in two main ways: let an agent decide when to search, or always search first and then answer in one model call. The tutorial shows the basic pipeline: load the page, split it into chunks, store embeddings in a vector store, and retrieve the best matches for a user question. It also highlights safety basics like telling the model to treat retrieved text as data, not instructions.

## Key insights

- A retrieval tool can be wrapped as a LangChain tool and used by an agent for multi-step Q&A over a document.
- A two-step retrieval-then-answer chain is simpler and lower-latency than an agent loop, but gives up flexibility.
- LangSmith tracing is presented as the way to inspect retrieval and generation steps during debugging.
- The tutorial recommends defensive prompting, structural delimiters, and output validation to reduce prompt injection risk.
- The example uses WebBaseLoader plus RecursiveCharacterTextSplitter as the indexing path for a web article.

## Derived knowledge pages

- [[how-to/two-step-document-ingestion]]
- [[topics/prompt-injection-defensive-context-handling]]
- [[topics/rag-orchestration-patterns]]

## Why it matters

The piece is useful because it compresses a complete RAG implementation into a small, inspectable pattern: load documents, split them, index them, retrieve relevant chunks, and feed them into a model. It gives two orchestration choices that map to different product needs: an agent when you want the model to decide whether and how to search, or a fixed retrieval-plus-generation chain when you want predictable one-call behavior. That distinction is operationally important because the article is explicit about the trade-off between flexibility and latency, and it shows how the prompt changes in each case. The tutorial also makes a practical point that is easy to miss in toy examples: the retrieved context should be treated as untrusted data, not instructions, because prompt injection remains possible even with simple retrieval. LangSmith is positioned as the observability layer for understanding what the chain or agent actually did, which is relevant when debugging search quality or tool-use behavior. The source is narrow, though: it demonstrates one blog-post Q&A setup and does not provide benchmarks, cost analysis, or evaluation against alternatives. As of the source publication date being unavailable, the guidance is best treated as durable implementation scaffolding, but the exact API calls and defaults should be verified against the live LangChain docs before use. The service automation or support implication is only indirect here: the same RAG pattern could power knowledge lookups, but the article does not discuss contact centers, voice, meetings, or back-office workflows.

## Limitations / open questions

The example is intentionally small and does not evaluate answer quality, retrieval recall, hallucination rate, or latency under load. It uses a single blog post, so it does not show how the approach behaves with multiple sources, conflicting documents, or noisy corpora. The article mentions prompt injection risk, but the proposed mitigations are generic and explicitly not foolproof. It also does not cover indexing refresh, access control, citation formatting, or cost management for repeated retrieval and model calls. Because the source is documentation, some claims are instructional rather than evidence-backed performance results.

## Contradictions / unverified claims

The tutorial presents the agent and two-step chain as straightforward options, but it does not prove that either is better in practice for any specific workload. The note that the agent can make multiple searches is useful, yet it also means the behavior is partly delegated to the model and may be less controllable than many production teams want. The prompt-injection guidance is sensible but generic; it reduces risk without solving the underlying problem that instructions and data share the same context window. The source is clear about trade-offs, so there is little hype, but the absence of benchmarks means claims like "fast and effective" should be read as tutorial guidance rather than validated performance evidence.

## Source metadata

- Canonical URL: https://docs.langchain.com/oss/python/langchain/rag
- Raw markdown: `raw/readwise/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1.md`
- Raw HTML: `raw/readwise/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1.html`

## Full source text

---
readwise_id: 01kqh06nqcje2w0skbcbhj1fn1
title: Build a RAG agent with LangChain
author: Docs by LangChain
source_url: https://docs.langchain.com/oss/python/langchain/rag
category: article
location: archive
saved_at: '2026-05-01T05:29:22.924000+00:00'
updated_at: '2026-05-02T14:22:05.882073+00:00'
tags:
- processed
publication: Langchain
---

One of the most powerful applications enabled by LLMs is sophisticated question-answering (Q&A) chatbots. These are applications that can answer questions about specific source information.
