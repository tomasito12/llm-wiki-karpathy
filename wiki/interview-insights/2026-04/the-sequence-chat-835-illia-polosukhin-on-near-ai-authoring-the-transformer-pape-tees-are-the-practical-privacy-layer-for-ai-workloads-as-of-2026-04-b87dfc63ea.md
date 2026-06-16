---
title: TEEs are the practical privacy layer for AI workloads as of 2026-04-02
slug: tees-are-the-practical-privacy-layer-for-ai-workloads-as-of-2026-04-02
category: insight
tags:
- execution-environments
- inference-systems
- infrastructure
source_id: the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8
source_title: 'The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the
  Transformer Paper and Decentralized and Private AI'
source_date: '2026-04-02'
month: 2026-04
evidence_count: 6
evidence_set_hash: 0eba00434fdc7b88
insight_title: TEEs are the practical privacy layer for AI workloads as of 2026-04-02
insight_type: privacy_security
confidence: high
durability_estimate: medium_term
wiki_worthiness: strong_candidate
---

# TEEs are the practical privacy layer for AI workloads as of 2026-04-02

## Interview Insight

### Summary

Polosukhin says trusted execution environments are the only feasible solution for private AI at this point. He adds that FHE and similar approaches are too slow for performance-sensitive inference and that MPC is being used as a component of the TEE setup for key generation. The operational takeaway is that private AI infrastructure should be designed around TEEs first, not around cryptographic schemes that are still too slow for production use.

### Why It Matters

As of 2026-04-02, this is a concrete boundary on private-AI architecture: if you need usable latency, TEEs are the path he considers workable. The claim is opinionated, not benchmark-backed, but it is still useful as a deployment filter for teams choosing between TEE-based systems and slower cryptographic alternatives.

### Operational Relevance

Bias privacy architecture toward TEE-backed confidential compute for inference and key handling. Treat FHE/MPC as supporting components or long-horizon options rather than the core runtime for latency-sensitive serving.

### Service Automation Relevance

Directly relevant for service automation that handles sensitive user data: chat histories, account details, and enterprise support cases can be routed through confidential inference designs if latency and hardware trust assumptions are acceptable.

### Mentioned Entities

- NEAR AI
- MPC
- FHE
- Trusted Execution Environments

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- FHE and similar approaches are too slow for a practical privacy stack at this stage.

### Evidence Snippets

- "Currently TEEs are the only feasible solution. We use MPC as a component of our TEE setup to ensure that there is a robust key generation process that is not dependent on an individual machine or specific hardware provider. This setup also allows users to control their encryption keys. FHE and similar approaches are way too slow from a performance perspective."

## Evidence / supporting sources

### The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI (2026-04-02)

- FHE and similar approaches are too slow for a practical privacy stack at this stage. (`30b0d1f44f4a` · counter · contrarian_or_speculative_claims[0]; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- Bias privacy architecture toward TEE-backed confidential compute for inference and key handling. Treat FHE/MPC as supporting components or long-horizon options rather than the core runtime for latency-sensitive serving. (`67a748677964` · neutral · operational_relevance; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- Directly relevant for service automation that handles sensitive user data: chat histories, account details, and enterprise support cases can be routed through confidential inference designs if latency and hardware trust assumptions are acceptable. (`19ad6ab09f17` · neutral · service_automation_relevance; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- Polosukhin says trusted execution environments are the only feasible solution for private AI at this point. He adds that FHE and similar approaches are too slow for performance-sensitive inference and that MPC is being used as a component of the TEE setup for key generation. The operational takeaway is that private AI infrastructure should be designed around TEEs first, not around cryptographic schemes that are still too slow for production use. (`6c26498ce0a6` · neutral · summary; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- As of 2026-04-02, this is a concrete boundary on private-AI architecture: if you need usable latency, TEEs are the path he considers workable. The claim is opinionated, not benchmark-backed, but it is still useful as a deployment filter for teams choosing between TEE-based systems and slower cryptographic alternatives. (`67f5286aebcb` · neutral · why_it_matters; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])
- "Currently TEEs are the only feasible solution. We use MPC as a component of our TEE setup to ensure that there is a robust key generation process that is not dependent on an individual machine or specific hardware provider. This setup also allows users to control their encryption keys. FHE and similar approaches are way too slow from a performance perspective." (`c96e4a46b879` · supporting · evidence_snippets[0]; [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]])

## Source

- [[sources/the-sequence-chat-835-illia-polosukhin-on-near-ai-authoring-the-transformer-paper-and-decentralized-and-private-ai-01knem854rccyz9jt3tmexffg8|The Sequence Chat #835: Illia Polosukhin on NEAR AI, Authoring the Transformer Paper and Decentralized and Private AI]]
