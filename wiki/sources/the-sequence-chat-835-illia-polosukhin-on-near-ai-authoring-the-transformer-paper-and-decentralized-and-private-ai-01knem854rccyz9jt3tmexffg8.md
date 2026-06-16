---
title: 'The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer
  Paper and Decentralized and Private AI'
slug: the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8
category: source
tags:
- agent-orchestration
- ai-evaluation
- coding-agents
- enterprise-ai
- execution-environments
- inference-systems
- infrastructure
- multi-agent-systems
- serving-infrastructure
- verification-systems
- workflow-design
source_id: the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8
author: Jesus Rodriguez
publication: Substack
published_date: '2026-04-02'
assessed_as_of: '2026-04-02'
ingested_at: '2026-06-09T18:43:16+00:00'
canonical_url: https://thesequence.substack.com/p/the-sequence-chat-835-illia-polosukhin
content_sha256: 6cdf5b8efa350054631607e809e2b3546833e8e5b4709cc41114284e6c7495c5
derived_interview_insights:
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-confidential-inference-is-the-first-useful-entry-point-for-private-a-dbafcb53c8.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-intents-are-a-declarative-interface-for-cross-chain-and-agent-commer-f767db47a9.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-pragmatic-decentralized-ai-favors-data-inference-aggregation-and-ver-8387c574c1.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-tees-are-the-practical-privacy-layer-for-ai-workloads-as-of-2026-04-b87dfc63ea.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-the-execution-harness-can-matter-as-much-as-the-model-e2f5cfaeca.md
derived_pages:
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-confidential-inference-is-the-first-useful-entry-point-for-private-a-dbafcb53c8.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-intents-are-a-declarative-interface-for-cross-chain-and-agent-commer-f767db47a9.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-pragmatic-decentralized-ai-favors-data-inference-aggregation-and-ver-8387c574c1.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-tees-are-the-practical-privacy-layer-for-ai-workloads-as-of-2026-04-b87dfc63ea.md
- interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-the-execution-harness-can-matter-as-much-as-the-model-e2f5cfaeca.md
---

# The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI

This interview is about how one of the transformer paper’s coauthors thinks about AI after the model itself. He says the most useful ideas today are not just bigger models, but better infrastructure around them: private execution, decentralized coordination, and agent-friendly payment rails. The core privacy answer in the piece is trusted execution environments, not fully homomorphic encryption. The core decentralization answer is more modest: data sharing, inference aggregation, and verification tools matter more than distributed training hype. He also argues that “intents” can make wallets and agents work through desired outcomes instead of step-by-step commands.

## Key insights

- Trusted execution environments are presented as the only practical privacy layer for AI workloads as of 2026-04-02; fully homomorphic encryption is described as too slow.
- Confidential inference is the first commercially useful entry point for private AI because multi-node confidential pretraining is still limited.
- In decentralized AI, the interview favors pragmatic components like data collection, inference aggregation, and verifiable benchmarks over distributed training as the headline use case.
- Polosukhin treats blockchains as machine-native trust rails for agents because they already solve payment, Sybil resistance, reputation, and multi-party confirmation problems.
- The interview’s recurring strategic claim is that the execution harness can matter as much as the model, especially for local and privacy-preserving agents.

## Derived knowledge pages

- [[interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-confidential-inference-is-the-first-useful-entry-point-for-private-a-dbafcb53c8]]
- [[interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-intents-are-a-declarative-interface-for-cross-chain-and-agent-commer-f767db47a9]]
- [[interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-pragmatic-decentralized-ai-favors-data-inference-aggregation-and-ver-8387c574c1]]
- [[interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-tees-are-the-practical-privacy-layer-for-ai-workloads-as-of-2026-04-b87dfc63ea]]
- [[interview-insights/2026-04/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-pape-the-execution-harness-can-matter-as-much-as-the-model-e2f5cfaeca]]

## Why it matters

The piece is useful because it separates durable infrastructure ideas from more speculative decentralized-AI rhetoric. Polosukhin is explicit that the transformer story is still about scale plus attention, but he also says the field has not solved data efficiency or a better learning procedure, which keeps the door open for post-next-token training changes. On decentralized AI, the article is narrowly practical: data collection, inference compute aggregation, verifiable benchmarks, and incentivized environments are the parts he says work, while distributed training is framed as hard and not obviously demanded by users. That makes the interview relevant as a filter for what to build around AI models rather than what to claim about model sovereignty. The privacy discussion is similarly concrete: he says TEEs are the only feasible option for now, uses MPC as a key-management component, and treats confidential inference as the first real product, with fine-tuning and pretraining deferred because of multi-node limits. The NEAR Intents discussion adds a clean mental model for agent commerce: declare an outcome, match providers, and settle across heterogeneous networks. As of 2026-04-02, the article is actionable mainly as a design compass for private inference, agent harnesses, and intent-based coordination; it is less useful as evidence that distributed training or FHE is ready for broad adoption. For voice, meetings, and back-office-style automation, the interview’s most relevant point is that agent harnesses and machine-native payment rails may matter more than raw model size when agents are expected to carry out end-to-end tasks.

## Limitations / open questions

The interview offers no benchmarks, cost numbers, latency measurements, or failure-mode analysis for TEEs, MPC, confidential inference, or NEAR Intents. Claims about “the only feasible solution” for privacy and “best model” incentives are judgments, not comparative evaluations. Multi-node confidential computing is acknowledged as limited, but the exact technical constraints, security assumptions, and roadmap for confidential pretraining are not detailed. The discussion of decentralized AI mentions early signals and recent initiatives, but does not establish durability or adoption. The prediction that agents will facilitate global trade and pay via stablecoins is speculative and unsupported by evidence in the transcript.

## Contradictions / unverified claims

Several claims are strong opinions presented without empirical backing, especially that TEEs are the only feasible privacy path and that FHE is too slow for some time. The interview also assumes users will not value decentralized training unless it improves raw performance, which may be true for many buyers but is not demonstrated here. The idea that blockchains are naturally the easiest rails for agents is plausible, but the transcript does not compare them against other machine-payment systems or identity layers. The predictions about nationalization proposals for AI labs and agent-driven global trade are provocative but remain speculative.

## Source metadata

- Canonical URL: https://thesequence.substack.com/p/the-sequence-chat-835-illia-polosukhin
- Raw markdown: `raw/readwise/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8.md`
- Raw HTML: `raw/readwise/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8.html`
