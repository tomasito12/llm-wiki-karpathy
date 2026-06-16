---
title: Search is being rebuilt as code rather than iterative tool calls
slug: search-is-being-rebuilt-as-code-rather-than-iterative-tool-calls
category: signal
tags:
- runtime-systems
- knowledge-systems
- tool-centric-agents
source_id: ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp
source_title: '[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark'
source_date: '2026-06-02'
month: 2026-06
evidence_count: 6
evidence_set_hash: 55e19d76111badc9
signal_title: Search is being rebuilt as code rather than iterative tool calls
signal_type: tool
signal_strength: medium
time_horizon: medium_term
wiki_worthiness: review_candidate
---

# Search is being rebuilt as code rather than iterative tool calls

## Signal

### Summary

Perplexity's 'Search as Code' replaces repeated search-tool prompting with Python against a search SDK. The source says this enables custom ranking pipelines, map-reduce over indexes, batching, aggregation, and lower token overhead. That is a concrete pattern for reducing tool-call chatter in search-heavy agents.

### Why It Matters

This is a reusable design pattern for retrieval-heavy assistants: move the search logic into executable code when the workflow needs ranking, aggregation, or batching. As of 2026-06-02, it is especially relevant for high-volume internal search and research assistants.

### Operational Relevance

Useful when an agent repeatedly calls search, re-ranks results, or combines many retrieval steps into one controllable pipeline.

### Service Automation Relevance

Support bots that rely on knowledge search can reduce latency and token spend by executing structured search workflows instead of chatty back-and-forth retrieval.

### Mentioned Entities

- Perplexity

### Suggested Destinations

- trends/

### Evidence Snippets

- Perplexity’s “Search as Code” is the clearest example: instead of iterative search tool calls, the model writes Python against a search SDK, enabling custom ranking pipelines, map-reduce over indexes, batching, aggregation, and lower token overhead.
- Perplexity reports a jump on its internal WANDR benchmark from 0.152 to 0.386 with this architecture

## Evidence / supporting sources

### [AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark (2026-06-02)

- Useful when an agent repeatedly calls search, re-ranks results, or combines many retrieval steps into one controllable pipeline. (`4a8c5a66e4df` · neutral · operational_relevance; [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]])
- Support bots that rely on knowledge search can reduce latency and token spend by executing structured search workflows instead of chatty back-and-forth retrieval. (`16435b487131` · neutral · service_automation_relevance; [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]])
- Perplexity's 'Search as Code' replaces repeated search-tool prompting with Python against a search SDK. The source says this enables custom ranking pipelines, map-reduce over indexes, batching, aggregation, and lower token overhead. That is a concrete pattern for reducing tool-call chatter in search-heavy agents. (`d05cad17debd` · neutral · summary; [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]])
- This is a reusable design pattern for retrieval-heavy assistants: move the search logic into executable code when the workflow needs ranking, aggregation, or batching. As of 2026-06-02, it is especially relevant for high-volume internal search and research assistants. (`f13004ceae2c` · neutral · why_it_matters; [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]])
- Perplexity’s “Search as Code” is the clearest example: instead of iterative search tool calls, the model writes Python against a search SDK, enabling custom ranking pipelines, map-reduce over indexes, batching, aggregation, and lower token overhead. (`8fcf0a793636` · supporting · evidence_snippets[0]; [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]])
- Perplexity reports a jump on its internal WANDR benchmark from 0.152 to 0.386 with this architecture (`e49ad77971d5` · supporting · evidence_snippets[1]; [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]])

## Source

- [[sources/ainews-nvidia-cosmos-3-nemotron-3-ultra-and-rtx-spark-01kt363pc5f8s2fhketwp5jdkp|[AINews] NVIDIA Cosmos 3, Nemotron 3 Ultra, and RTX Spark]]
