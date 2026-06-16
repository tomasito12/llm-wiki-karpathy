---
title: Confidential inference is the first useful entry point for private AI
slug: confidential-inference-is-the-first-useful-entry-point-for-private-ai
category: insight
tags:
- inference-systems
- enterprise-ai
- serving-infrastructure
source_id: the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8
source_title: 'The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the
  Transformer Paper and Decentralized and Private AI'
source_date: '2026-04-02'
month: 2026-04
evidence_count: 7
evidence_set_hash: d8edaabc57a2be99
insight_title: Confidential inference is the first useful entry point for private
  AI
insight_type: service_automation
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Confidential inference is the first useful entry point for private AI

## Interview Insight

### Summary

NEAR AI is described as building confidential computing for the full model lifecycle, but Polosukhin says multi-node limits make private pretraining ineffective for now. Because of that, the first product focus is confidential inference, which he says has immediate value for enterprises and privacy-focused prosumers. He also notes that the platform can host closed-weight models without exposing weights to providers or consumers, while keeping model builders away from consumer data.

### Why It Matters

As of 2026-04-02, this is a practical prioritization rule for private-AI product strategy: start with inference, not pretraining. It is especially relevant for teams trying to monetize privacy claims without waiting for cluster-scale confidential training to mature.

### Operational Relevance

Design roadmaps around confidential inference first, then fine-tuning, then pretraining only if multi-node confidentiality becomes viable. For enterprise deployments, this suggests focusing on serving-time privacy guarantees and key ownership workflows before attempting full private training pipelines.

### Service Automation Relevance

Strongly relevant for support automation and agent assistants that must protect customer data. A confidential inference layer can support private chat, private knowledge access, and controlled access to model weights while limiting exposure on both sides of the interaction.

### Mentioned Entities

- NEAR AI
- confidential computing
- NEAR AI Cloud

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- Fine tuning would be the next step, and pretraining beyond that, but multi-node confidential pretraining is not yet effective.

### Evidence Snippets

- "At NEAR AI we are building confidential computing infrastructure that should work for the full workflow. That said, currently there are limitations to how confidential computing works for multi-node systems. Which means that it is very ineffective to do pretraining. We have started by offering confidential inference because it’s the most direct and has immediate value for customers, from enterprises to privacy-focused prosumers."
- "Confidential inference also is not limited to open weight models. Our platform can host closed weight models in such a way that neither hardware providers or consumers are accessing the weights directly, while the model builders don’t get access to consumer data."

## Evidence / supporting sources

### The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI (2026-04-02)

- Fine tuning would be the next step, and pretraining beyond that, but multi-node confidential pretraining is not yet effective. (`16c23e8d4370` · counter · contrarian_or_speculative_claims[0]; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- Design roadmaps around confidential inference first, then fine-tuning, then pretraining only if multi-node confidentiality becomes viable. For enterprise deployments, this suggests focusing on serving-time privacy guarantees and key ownership workflows before attempting full private training pipelines. (`c9d65d47df7b` · neutral · operational_relevance; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- Strongly relevant for support automation and agent assistants that must protect customer data. A confidential inference layer can support private chat, private knowledge access, and controlled access to model weights while limiting exposure on both sides of the interaction. (`baf1bb39e8c2` · neutral · service_automation_relevance; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- NEAR AI is described as building confidential computing for the full model lifecycle, but Polosukhin says multi-node limits make private pretraining ineffective for now. Because of that, the first product focus is confidential inference, which he says has immediate value for enterprises and privacy-focused prosumers. He also notes that the platform can host closed-weight models without exposing weights to providers or consumers, while keeping model builders away from consumer data. (`07638836fe18` · neutral · summary; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- As of 2026-04-02, this is a practical prioritization rule for private-AI product strategy: start with inference, not pretraining. It is especially relevant for teams trying to monetize privacy claims without waiting for cluster-scale confidential training to mature. (`c530ef966dd5` · neutral · why_it_matters; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- "At NEAR AI we are building confidential computing infrastructure that should work for the full workflow. That said, currently there are limitations to how confidential computing works for multi-node systems. Which means that it is very ineffective to do pretraining. We have started by offering confidential inference because it’s the most direct and has immediate value for customers, from enterprises to privacy-focused prosumers." (`c298c69caf3f` · supporting · evidence_snippets[0]; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- "Confidential inference also is not limited to open weight models. Our platform can host closed weight models in such a way that neither hardware providers or consumers are accessing the weights directly, while the model builders don’t get access to consumer data." (`cf00a9ed5ad7` · supporting · evidence_snippets[1]; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])

## Source

- [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]]
