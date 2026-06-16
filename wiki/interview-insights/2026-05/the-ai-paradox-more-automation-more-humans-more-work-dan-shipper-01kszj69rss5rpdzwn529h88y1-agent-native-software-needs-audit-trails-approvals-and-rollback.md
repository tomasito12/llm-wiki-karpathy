---
title: Agent-native software needs audit trails, approvals, and rollback
slug: agent-native-software-needs-audit-trails-approvals-and-rollback
category: insight
tags:
- auditability
- verification-systems
source_id: the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1
source_title: 'The AI paradox: More automation, more humans, more work | Dan Shipper'
source_date: '2026-05-24'
month: 2026-05
evidence_count: 9
evidence_set_hash: 4b0a1a9f2b5426e2
insight_title: Agent-native software needs audit trails, approvals, and rollback
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Agent-native software needs audit trails, approvals, and rollback

## Interview Insight

### Summary

The transcript argues that when agents can make many changes quickly, software must expose what happened and let humans control the blast radius. Shipper specifically calls for approval flows, an inbox that summarizes pending and completed actions, logs, and fast rollback. He frames this as a new product requirement created by agent concurrency and error speed.

### Why It Matters

This is a durable design pattern for AI engineering as of 2026-05-24. The more capable the agent, the more important auditability and reversible actions become, especially in enterprise settings. It is directly relevant to governance, operational safety, and adoption because users will not trust systems they cannot inspect or undo.

### Operational Relevance

Build agent workflows with explicit state transitions, event logs, and reversible operations. If an agent can edit documents, code, or operational systems, the product needs review queues and recovery mechanisms before scale. This is especially important where many low-friction edits can create hidden damage.

### Service Automation Relevance

In support automation, auditability and rollback reduce the risk of bad automated replies, incorrect account actions, and irrecoverable side effects. Human handoff systems should preserve action history so an operator can understand and correct what the agent did.

### Mentioned Entities

- Proof
- GitHub

### Suggested Destinations

- topics/

### Contrarian Or Speculative Claims

- Agents can make a billion requests in three seconds, so product UX must change around that concurrency.
- Logs, approvals, and rollback become core product features in agent-native software.

### Evidence Snippets

- "You need, um. You need like approval. You need a sort of inbox that sort of summarizes, here's all the stuff that's going to happen or has happened. You need, um, you need logs and the ability to roll it back real quick."
- "agents can make a billion requests in like three seconds"
- "when someone has a problem, they don't email support. Their agent sends a bug report."

## Evidence / supporting sources

### The AI paradox: More automation, more humans, more work | Dan Shipper (2026-05-24)

- Agents can make a billion requests in three seconds, so product UX must change around that concurrency. (`c5ff2b7c7377` · counter · contrarian_or_speculative_claims[0]; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- Logs, approvals, and rollback become core product features in agent-native software. (`7b0c49f6c8ce` · counter · contrarian_or_speculative_claims[1]; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- Build agent workflows with explicit state transitions, event logs, and reversible operations. If an agent can edit documents, code, or operational systems, the product needs review queues and recovery mechanisms before scale. This is especially important where many low-friction edits can create hidden damage. (`07c77a387f53` · neutral · operational_relevance; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- In support automation, auditability and rollback reduce the risk of bad automated replies, incorrect account actions, and irrecoverable side effects. Human handoff systems should preserve action history so an operator can understand and correct what the agent did. (`28b0a2c2e087` · neutral · service_automation_relevance; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- The transcript argues that when agents can make many changes quickly, software must expose what happened and let humans control the blast radius. Shipper specifically calls for approval flows, an inbox that summarizes pending and completed actions, logs, and fast rollback. He frames this as a new product requirement created by agent concurrency and error speed. (`6a3d866a8978` · neutral · summary; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- This is a durable design pattern for AI engineering as of 2026-05-24. The more capable the agent, the more important auditability and reversible actions become, especially in enterprise settings. It is directly relevant to governance, operational safety, and adoption because users will not trust systems they cannot inspect or undo. (`7dc95c75b00d` · neutral · why_it_matters; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- "You need, um. You need like approval. You need a sort of inbox that sort of summarizes, here's all the stuff that's going to happen or has happened. You need, um, you need logs and the ability to roll it back real quick." (`76ab1de5cd21` · supporting · evidence_snippets[0]; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- "agents can make a billion requests in like three seconds" (`fbc1a3c8f7c0` · supporting · evidence_snippets[1]; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])
- "when someone has a problem, they don't email support. Their agent sends a bug report." (`8a1dea084981` · supporting · evidence_snippets[2]; [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]])

## Source

- [[sources/the-ai-paradox-more-automation-more-humans-more-work-dan-shipper-01kszj69rss5rpdzwn529h88y1|The AI paradox: More automation, more humans, more work | Dan Shipper]]
