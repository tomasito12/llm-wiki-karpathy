---
title: Specification quality is the real bottleneck in verified AI
slug: specification-quality-is-the-real-bottleneck-in-verified-ai
category: insight
tags:
- verification-systems
- workflow-design
source_id: scaling-past-informal-ai-carina-hong-axiom-math-01kt7fvv1fxx82p8qqktgdd1qa
source_title: 🔬Scaling Past Informal AI - Carina Hong, Axiom Math
source_date: '2026-06-03'
month: 2026-06
evidence_count: 4
evidence_set_hash: 840b9d92f5551cba
insight_title: Specification quality is the real bottleneck in verified AI
insight_type: topic
confidence: high
durability_estimate: long_term
wiki_worthiness: strong_candidate
---

# Specification quality is the real bottleneck in verified AI

## Interview Insight

### Summary

The transcript repeatedly narrows the problem from "can the model generate correct proofs?" to "can humans specify the task precisely enough to verify it?" Carina’s line is that anything that can be specified can be proven, but humans are often bad at specifying everything they want. That makes specification quality the gating constraint for how far verification can scale.

### Why It Matters

As of 2026-06-03, this is a valuable corrective to simplistic claims about formal methods solving AI reliability. Verification only helps when the task boundary is crisp enough to formalize. For builders, the important question is often not model capability but whether the workflow can be rewritten into checkable constraints.

### Operational Relevance

Before building verifier-backed systems, invest in crisp specs, invariant definitions, and failure conditions. This changes the engineering center of gravity toward task formalization, not just model prompting. The source also implies that specification work may become a separate skill area for AI teams.

### Service Automation Relevance

Highly relevant for service automation because support and back-office workflows often fail at ambiguous requirements. The transcript suggests verified automation will work best where the task can be made explicit enough for automatic checking; otherwise human handoff remains necessary.

## Evidence / supporting sources

### 🔬Scaling Past Informal AI - Carina Hong, Axiom Math (2026-06-03)

- Before building verifier-backed systems, invest in crisp specs, invariant definitions, and failure conditions. This changes the engineering center of gravity toward task formalization, not just model prompting. The source also implies that specification work may become a separate skill area for AI teams. (`6964d80aa23b` · neutral · operational_relevance; [[sources/scaling-past-informal-ai-carina-hong-axiom-math-01kt7fvv1fxx82p8qqktgdd1qa|🔬Scaling Past Informal AI - Carina Hong, Axiom Math]])
- Highly relevant for service automation because support and back-office workflows often fail at ambiguous requirements. The transcript suggests verified automation will work best where the task can be made explicit enough for automatic checking; otherwise human handoff remains necessary. (`390fb8cd1ef9` · neutral · service_automation_relevance; [[sources/scaling-past-informal-ai-carina-hong-axiom-math-01kt7fvv1fxx82p8qqktgdd1qa|🔬Scaling Past Informal AI - Carina Hong, Axiom Math]])
- The transcript repeatedly narrows the problem from "can the model generate correct proofs?" to "can humans specify the task precisely enough to verify it?" Carina’s line is that anything that can be specified can be proven, but humans are often bad at specifying everything they want. That makes specification quality the gating constraint for how far verification can scale. (`8c5f3665e767` · neutral · summary; [[sources/scaling-past-informal-ai-carina-hong-axiom-math-01kt7fvv1fxx82p8qqktgdd1qa|🔬Scaling Past Informal AI - Carina Hong, Axiom Math]])
- As of 2026-06-03, this is a valuable corrective to simplistic claims about formal methods solving AI reliability. Verification only helps when the task boundary is crisp enough to formalize. For builders, the important question is often not model capability but whether the workflow can be rewritten into checkable constraints. (`5133c4a6d5e3` · neutral · why_it_matters; [[sources/scaling-past-informal-ai-carina-hong-axiom-math-01kt7fvv1fxx82p8qqktgdd1qa|🔬Scaling Past Informal AI - Carina Hong, Axiom Math]])

## Source

- [[sources/scaling-past-informal-ai-carina-hong-axiom-math-01kt7fvv1fxx82p8qqktgdd1qa|🔬Scaling Past Informal AI - Carina Hong, Axiom Math]]
