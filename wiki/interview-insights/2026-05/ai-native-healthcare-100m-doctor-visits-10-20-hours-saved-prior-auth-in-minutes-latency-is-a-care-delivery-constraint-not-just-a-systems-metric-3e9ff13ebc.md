---
title: Latency is a care-delivery constraint, not just a systems metric
slug: latency-is-a-care-delivery-constraint-not-just-a-systems-metric
category: insight
tags:
- workflow-automation
- agent-orchestration
- support-automation
source_id: ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz
source_title: 'AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior
  Auth in Minutes — Janie Lee & Chai Asawa, Abrid…'
source_date: '2026-05-14'
month: 2026-05
evidence_count: 7
evidence_set_hash: 0f9ae326b8faedb6
insight_title: Latency is a care-delivery constraint, not just a systems metric
insight_type: infrastructure
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Latency is a care-delivery constraint, not just a systems metric

## Interview Insight

### Summary

The speakers frame latency as something that can delay care, not just degrade UX. Their prior authorization example shows why useful AI in healthcare must act during the visit, before the patient leaves, rather than after an approval denial arrives weeks later. They also describe a practical constraint: if the product interrupts too often, clinicians ignore it, so the system needs selective, high-confidence intervention timing.

### Why It Matters

As of 2026-05-14, this is a broadly reusable systems lesson for agentic workflows: some domains care about the timing of inference as much as the correctness of inference. Products that can reduce action latency without creating alert fatigue can change downstream operations materially.

### Operational Relevance

Design for event-triggered actions, not only batch summaries. Use triage models, thresholding, and context-aware triggers to decide when to interrupt a human versus when to wait for a safer moment.

### Service Automation Relevance

Highly relevant to support automation: well-timed escalation beats noisy interruption. The same principle applies to chatbots that should surface an exception only when it meaningfully changes the next step.

### Mentioned Entities

- Abridge
- prior authorization
- Aetna

### Suggested Destinations

- topics/

### Evidence Snippets

- "AI has is reducing latency in the world"
- "prior authorization is an example of where care gets delayed and so great AI can reduce that"
- "we would want to tell the doctor... before Sean leaves the room"

## Evidence / supporting sources

### AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid… (2026-05-14)

- Design for event-triggered actions, not only batch summaries. Use triage models, thresholding, and context-aware triggers to decide when to interrupt a human versus when to wait for a safer moment. (`b6a35dcd7d63` · neutral · operational_relevance; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])
- Highly relevant to support automation: well-timed escalation beats noisy interruption. The same principle applies to chatbots that should surface an exception only when it meaningfully changes the next step. (`dd761a981f46` · neutral · service_automation_relevance; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])
- The speakers frame latency as something that can delay care, not just degrade UX. Their prior authorization example shows why useful AI in healthcare must act during the visit, before the patient leaves, rather than after an approval denial arrives weeks later. They also describe a practical constraint: if the product interrupts too often, clinicians ignore it, so the system needs selective, high-confidence intervention timing. (`abcb1eeb10a3` · neutral · summary; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])
- As of 2026-05-14, this is a broadly reusable systems lesson for agentic workflows: some domains care about the timing of inference as much as the correctness of inference. Products that can reduce action latency without creating alert fatigue can change downstream operations materially. (`887d8f96955a` · neutral · why_it_matters; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])
- "AI has is reducing latency in the world" (`2df4184a523e` · supporting · evidence_snippets[0]; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])
- "prior authorization is an example of where care gets delayed and so great AI can reduce that" (`7b0b11cbec5d` · supporting · evidence_snippets[1]; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])
- "we would want to tell the doctor... before Sean leaves the room" (`11af261df9dc` · supporting · evidence_snippets[2]; [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]])

## Source

- [[sources/ai-native-healthcare-100m-doctor-visits-10-20-hours-saved-prior-auth-in-minutes-janie-lee-chai-asawa-abrid-01krm8k6wpq1edyv2270n0kzvz|AI-Native Healthcare: 100M Doctor Visits, 10–20 Hours Saved, Prior Auth in Minutes — Janie Lee & Chai Asawa, Abrid…]]
