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
synthesis_state: stage1-placeholder
---

# Retrieval-Augmented Generation

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
A method that improves language model answers by retrieving relevant external documents or chunks and feeding them into the model at query time.

## Related Terms

- Knowledge Management

## Relevance Note

This is a core pattern in document-grounded AI systems, especially for chatbots, enterprise search, and service workflows that need answers from private material. Understanding its strengths and limits helps practitioners decide when retrieval is enough and when they need higher-level structure or curation.

## Evidence / supporting sources

### Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead (2026-04-05)

- Instead of expecting the model to remember everything, the system looks up supporting material from a document store, vector database, or search index before answering. This is useful when the underlying knowledge changes often or when the source material is too large to fit in context. The tradeoff is that the system redoes the search-and-stitch process for each question, so it may not build persistent structure across related questions. In practice, it is often used for document question answering, internal knowledge search, and support bots. (`9a47da47d21e` · neutral · extended_explanation; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- A method that improves language model answers by retrieving relevant external documents or chunks and feeding them into the model at query time. (`40ea35b16061` · neutral · proposed_definition; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- This is a core pattern in document-grounded AI systems, especially for chatbots, enterprise search, and service workflows that need answers from private material. Understanding its strengths and limits helps practitioners decide when retrieval is enough and when they need higher-level structure or curation. (`ebc694ed41c5` · neutral · relevance_note; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])
- Here’s how it typically works: your documents get chopped into small chunks, those chunks get converted into mathematical representations called embeddings, and when you ask a question, the system searches for the most similar chunks and feeds them to the AI. (`300426729168` · supporting · supporting_snippet; [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]])

### 💠🌐 Everyone Is Wrong About NotebookLM (2025-11-17)

- Retrieval-augmented generation is common in enterprise assistants because it lets a model use a curated knowledge base instead of relying only on parametric memory. The quality of the retrieval step often matters as much as the model itself: bad source selection leads to bad answers. In operational settings, it is often combined with citations, document segmentation, and access controls. It is especially useful when the source material changes frequently or must remain auditable. (`b47bd0ce15dc` · neutral · extended_explanation; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- A pattern where a model answers by retrieving relevant external documents or passages and then generating a response grounded in that retrieved context. It is used to improve factuality, freshness, and domain specificity. (`7cad671dbc6b` · neutral · proposed_definition; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- This is a core pattern for document assistants, support search, internal copilots, and knowledge-grounded chat systems. It affects chunking, retrieval quality, citation design, and whether an assistant can be trusted in regulated or high-stakes workflows. (`8143408b6b57` · neutral · relevance_note; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])
- A real API → NLM becomes a RAG microservice for EVERYTHING (`f2e1e93369f4` · supporting · supporting_snippet; [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]])

### The ultimate guide to knowledge management for your Sales Agent (2026-05-13)

- This pattern is useful when the model needs current, organization-specific, or policy-specific information that should not be memorized in the model itself. A retrieval layer can pull from product docs, FAQs, or internal policies before the model generates a response. That makes it easier to refresh answers when facts change, and it can reduce unsupported guesses if the retrieval set is well maintained. The tradeoff is that retrieval quality and content quality become part of system quality; stale or poorly structured sources can still produce bad outputs. (`1b760a3c78e6` · neutral · extended_explanation; [[sources/the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769|The ultimate guide to knowledge management for your Sales Agent]])
- Retrieval-Augmented Generation is a pattern in which a model answers questions using retrieved external information rather than relying only on its internal parameters. The retrieved material is typically drawn from a curated knowledge source, making the system more grounded and easier to update. (`4aa9db67fa08` · neutral · proposed_definition; [[sources/the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769|The ultimate guide to knowledge management for your Sales Agent]])
- This is a core pattern for AI systems that need organization-specific answers, especially chatbots and agent workflows that must stay aligned with changing facts. It is also central to service automation when systems need to explain policies, plans, or procedures with grounded source material. (`58353d04e576` · neutral · relevance_note; [[sources/the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769|The ultimate guide to knowledge management for your Sales Agent]])
- Your knowledge base is no longer just static collateral for buyers to read, whether it’s your website, pricing pages, or internal sales materials. It powers your Sales Agent and entire inbound motion. (`fba4cc1cdaf4` · supporting · supporting_snippet; [[sources/the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769|The ultimate guide to knowledge management for your Sales Agent]])

### This Open-Source App Turns Your Documents Into a Self-Building Wiki (2026-05-08)

- Retrieval-augmented generation is useful when the model should not rely only on what it memorized during training. A query first pulls back relevant snippets, and the model then uses those snippets to produce an answer. This can improve factual grounding, but it often behaves like search plus synthesis rather than long-term learning. In practice, teams use it for document Q&A, support knowledge search, and other settings where evidence needs to stay close to the answer. (`f3f7e4161c0c` · neutral · extended_explanation; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- A pattern where a language model answers by retrieving relevant external information first, then using that retrieved context to generate a response. It is commonly used to ground answers in documents, databases, or other knowledge sources. (`202723533355` · neutral · proposed_definition; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- This term remains central in AI systems that need grounded answers from private documents, product knowledge, or operational data. It matters because many production assistants still depend on retrieval for freshness and auditability, even when users expect accumulation or memory. (`bd3f1d8357d5` · neutral · relevance_note; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])
- It doesn’t exist in the most common version of RAG (retrieval-augmented generation). The standard pattern is a stateless lookup tool. It’s brilliant at finding things. It’s terrible at building understanding. (`549eb9108af3` · supporting · supporting_snippet; [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]])

### Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge (2026-04-06)

- In practice, retrieval-augmented generation lets a model answer from documents, databases, or other sources without putting all of that material into the model’s weights. It is common when the underlying knowledge changes often or is too large to fit in context. The tradeoff is that the system often re-derives the answer each time instead of building a persistent structure that improves future work. (`a7991ee550ed` · neutral · extended_explanation; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- A method for answering questions by retrieving relevant external information at query time and using it as context for generation. (`1aa913800d0c` · neutral · proposed_definition; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- RAG remains a core pattern for document-grounded assistants, support bots, and enterprise search. It matters because many production systems still depend on retrieval quality, chunking, and synthesis behavior for answer quality. (`b9f86ef4d848` · neutral · relevance_note; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])
- Currently, the default way we interact with our documents is through Retrieval-Augmented Generation (RAG). You upload a bunch of PDFs, ask a question, and the LLM searches for relevant text chunks to synthesize an answer. (`a149f5b7afcd` · supporting · supporting_snippet; [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]])

## Contradictions / tensions

No contradictions captured in current sources.

## Related pages

- Knowledge Management

## Sources

- [[sources/andrej-karpathy-stopped-using-ai-to-write-code-he-s-using-it-to-build-a-second-brain-instead-01kr4392yb22p11v8q7pqc9npw|Andrej Karpathy Stopped Using AI to Write Code. He’s Using It to Build a Second Brain Instead]]
- [[sources/everyone-is-wrong-about-notebooklm-01kr433qg0ajtewhfmwa96q7a2|💠🌐 Everyone Is Wrong About NotebookLM]]
- [[sources/the-ultimate-guide-to-knowledge-management-for-your-sales-agent-01krh989qjyns47e84f2k7v769|The ultimate guide to knowledge management for your Sales Agent]]
- [[sources/this-open-source-app-turns-your-documents-into-a-self-building-wiki-01krh1c36qjjqw53cwe4hw1s5g|This Open-Source App Turns Your Documents Into a Self-Building Wiki]]
- [[sources/why-andrej-karpathy-s-llm-wiki-is-the-future-of-personal-knowledge-01kqm0rf7jxk8010thyjvag0j8|Why Andrej Karpathy’s “LLM Wiki” is the Future of Personal Knowledge]]
