---
title: Two-Step Document Ingestion
slug: two-step-document-ingestion
entity_id: how_to:two-step-document-ingestion
category: how-to
tags:
- ai-engineering
- context-engineering
- retrieval-systems
source_count: 1
evidence_count: 15
source_ids:
- build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1
value_level: high
confidence: 0.96
synthesis_state: stage1-placeholder
---

# Two-Step Document Ingestion

## Current understanding

<!-- stage1-placeholder: single-source lead; Stage 2 will synthesize from accumulated EvidenceItems -->
This is a practical way to turn a long document into something a retrieval system can search and answer from. It helps when the source text is too large for a model context window and when you want simpler, more predictable question answering. The main problem is not just storing text, but making the right pieces available at answer time. It also helps separate indexing work from runtime answering work.

## Caveats

This pattern does not solve answer quality by itself. It depends on chunking, retrieval quality, and prompt hygiene, and the source explicitly notes that prompt-injection mitigations are not foolproof. The example is narrow and does not cover refresh, access control, or evaluation.

## Implementation Steps

- Load the document with a document loader such as WebBaseLoader.
- Restrict parsing to the relevant HTML sections if the source is web content.
- Split the document into chunks with a text splitter such as RecursiveCharacterTextSplitter.
- Embed the chunks and add them to a vector store.
- At query time, retrieve the most relevant chunks with similarity search or a retriever.
- Pass the retrieved text into the model through a tool or a dynamic prompt.
- Instruct the model to treat retrieved context as data only and ignore any instructions inside it.

## Prerequisites

- A document source to ingest.
- A text splitter.
- Embeddings and a vector store.
- A model or agent that can consume retrieved context.

## Evidence / supporting sources

### Build a RAG agent with LangChain (undated)

- Load the source document, split it into smaller chunks, and store those chunks in a vector store. At query time, search the vector store for the most relevant chunks and pass them to the model as context. For simple setups, you can do retrieval inside an agent tool or inject retrieved context into the prompt before a single model call. Keep the retrieved text clearly separated from instructions and tell the model to treat it as data only. (`e57fc0352fa6` · neutral · answer_summary; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Load the document with a document loader such as WebBaseLoader. (`cc7c1963d7f8` · neutral · implementation_steps[0]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Restrict parsing to the relevant HTML sections if the source is web content. (`bcca1749c5b8` · neutral · implementation_steps[1]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Split the document into chunks with a text splitter such as RecursiveCharacterTextSplitter. (`05c2bb286a60` · neutral · implementation_steps[2]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Embed the chunks and add them to a vector store. (`aa5ff81add87` · neutral · implementation_steps[3]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- At query time, retrieve the most relevant chunks with similarity search or a retriever. (`6b1b126ebce0` · neutral · implementation_steps[4]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Pass the retrieved text into the model through a tool or a dynamic prompt. (`ec25dd6c5912` · neutral · implementation_steps[5]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Instruct the model to treat retrieved context as data only and ignore any instructions inside it. (`df9b4c3d3855` · neutral · implementation_steps[6]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- A document source to ingest. (`b9f7d5d5aaee` · neutral · prerequisites[0]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- A text splitter. (`9a4e382c5eb4` · neutral · prerequisites[1]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- Embeddings and a vector store. (`cb993d6a9699` · neutral · prerequisites[2]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- A model or agent that can consume retrieved context. (`a8d4e343e140` · neutral · prerequisites[3]; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- This is a practical way to turn a long document into something a retrieval system can search and answer from. It helps when the source text is too large for a model context window and when you want simpler, more predictable question answering. The main problem is not just storing text, but making the right pieces available at answer time. It also helps separate indexing work from runtime answering work. (`38c3435af8b5` · neutral · what_and_problem; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- "Indexing: a pipeline for ingesting data from a source and indexing it. This usually happens in a separate process." (`6abea515f5f1` · supporting · supporting_snippet; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])
- This pattern does not solve answer quality by itself. It depends on chunking, retrieval quality, and prompt hygiene, and the source explicitly notes that prompt-injection mitigations are not foolproof. The example is narrow and does not cover refresh, access control, or evaluation. (`bca5a5429c5c` · uncertainty · caveats; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])

## Contradictions / tensions

- This pattern does not solve answer quality by itself. It depends on chunking, retrieval quality, and prompt hygiene, and the source explicitly notes that prompt-injection mitigations are not foolproof. The example is narrow and does not cover refresh, access control, or evaluation. (uncertainty; [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]])

## Related pages

No related pages captured.

## Sources

- [[sources/build-a-rag-agent-with-langchain-01kqh06nqcje2w0skbcbhj1fn1|Build a RAG agent with LangChain]]
