---
title: Video system cost is dominated by data logistics as well as GPU time
slug: video-system-cost-is-dominated-by-data-logistics-as-well-as-gpu-time
category: insight
tags:
- infrastructure
- infrastructure-economics
- serving-infrastructure
- ai-engineering
source_id: why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f
source_title: Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead
source_date: '2026-06-01'
month: 2026-06
evidence_count: 8
evidence_set_hash: 3832273926ead867
insight_title: Video system cost is dominated by data logistics as well as GPU time
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Video system cost is dominated by data logistics as well as GPU time

## Interview Insight

### Summary

Ethan says video model training is not just a compute problem. He highlights petabyte-scale storage, repeated data pulls, ingress/egress, and I/O as major costs, alongside the GPUs themselves. He also notes that video models are often more I/O bound than LLM training, which makes caching and data-loading optimizations critical.

### Why It Matters

As of 2026-06-01, this is a durable infrastructure lesson for any team handling large multimodal corpora. It reframes capacity planning: the training bill is not only GPU-hours, but also storage architecture, network transfer, and pipeline efficiency. The exact dollar figures are illustrative, but the operational point is strong and reusable.

### Operational Relevance

Plan for storage tiers, cache design, and dataset movement costs early. For large video and multimodal systems, infra teams should treat data locality and ingestion throughput as training-enabling constraints, not implementation details.

### Service Automation Relevance

No direct service automation implications identified.

### Mentioned Entities

- AWS
- S3
- xAI
- Cosmos

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- Video training cost can be comparable to language-model training once storage and I/O are included.

### Evidence Snippets

- “just storing the videos alone, it costs a lot.”
- “you have the ingress and egress.”
- “video models is-- the cost is very-- is comparable to language models”

## Evidence / supporting sources

### Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead (2026-06-01)

- Video training cost can be comparable to language-model training once storage and I/O are included. (`cce5ab28f71f` · counter · contrarian_or_speculative_claims[0]; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- Plan for storage tiers, cache design, and dataset movement costs early. For large video and multimodal systems, infra teams should treat data locality and ingestion throughput as training-enabling constraints, not implementation details. (`d30faacb6df8` · neutral · operational_relevance; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- No direct service automation implications identified. (`10e7343fb1fd` · neutral · service_automation_relevance; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- Ethan says video model training is not just a compute problem. He highlights petabyte-scale storage, repeated data pulls, ingress/egress, and I/O as major costs, alongside the GPUs themselves. He also notes that video models are often more I/O bound than LLM training, which makes caching and data-loading optimizations critical. (`a735913a2269` · neutral · summary; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- As of 2026-06-01, this is a durable infrastructure lesson for any team handling large multimodal corpora. It reframes capacity planning: the training bill is not only GPU-hours, but also storage architecture, network transfer, and pipeline efficiency. The exact dollar figures are illustrative, but the operational point is strong and reusable. (`70f06b6b6d48` · neutral · why_it_matters; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- “just storing the videos alone, it costs a lot.” (`779e4d31dda5` · supporting · evidence_snippets[0]; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- “you have the ingress and egress.” (`67c6a536f1e9` · supporting · evidence_snippets[1]; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])
- “video models is-- the cost is very-- is comparable to language models” (`15f71c1a1a82` · supporting · evidence_snippets[2]; [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]])

## Source

- [[sources/why-video-agent-models-are-next-ethan-he-xai-grok-imagine-lead-01kt1xt3d2h92v7dq0qs0fwn2f|Why Video Agent models are next — Ethan He, xAI Grok Imagine Lead]]
