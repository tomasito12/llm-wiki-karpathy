---
title: Benchmark audits can materially change reported capability
slug: benchmark-audits-can-materially-change-reported-capability
category: signal
tags:
- continuous-evaluation
- qualitative-evals
source_id: ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv
source_title: '[AINews] Fable and Mythos officially too dangerous to release'
source_date: '2026-06-13'
month: 2026-06
evidence_count: 6
evidence_set_hash: 875216348e477d76
signal_title: Benchmark audits can materially change reported capability
signal_type: research_eval
signal_strength: medium
time_horizon: medium_term
wiki_worthiness: review_candidate
---

# Benchmark audits can materially change reported capability

## Signal

### Summary

FrontierMath v2 reportedly changed scores after auditing errors in 42% of problems, and the roundup says scores rose while rankings largely held. This is a reminder that benchmark datasets can be fragile and that corrected evaluation sets may move reported capability substantially. Static leaderboard snapshots are therefore weaker evidence than they appear.

### Why It Matters

If a benchmark contains many errors, the apparent model gap can be an artifact of the test set rather than a stable capability difference.

### Operational Relevance

Evaluation pipelines should track dataset revisions, audit status, and benchmark provenance before using scores for model selection or regression monitoring.

### Service Automation Relevance

For service workflows, benchmark brittleness means teams should validate models against their own task sets rather than assuming published scores transfer cleanly.

### Mentioned Entities

- Epoch AI
- FrontierMath

### Suggested Destinations

- trends/
- topics/

### Evidence Snippets

- “released FrontierMath: Tiers 1–4 (v2) after auditing errors in 42% of problems”
- “This substantially raised scores while preserving rankings”

## Evidence / supporting sources

### [AINews] Fable and Mythos officially too dangerous to release (2026-06-13)

- Evaluation pipelines should track dataset revisions, audit status, and benchmark provenance before using scores for model selection or regression monitoring. (`82bfd6f76483` · neutral · operational_relevance; [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]])
- For service workflows, benchmark brittleness means teams should validate models against their own task sets rather than assuming published scores transfer cleanly. (`30a3f1796487` · neutral · service_automation_relevance; [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]])
- FrontierMath v2 reportedly changed scores after auditing errors in 42% of problems, and the roundup says scores rose while rankings largely held. This is a reminder that benchmark datasets can be fragile and that corrected evaluation sets may move reported capability substantially. Static leaderboard snapshots are therefore weaker evidence than they appear. (`21360d5ca141` · neutral · summary; [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]])
- If a benchmark contains many errors, the apparent model gap can be an artifact of the test set rather than a stable capability difference. (`585eeaa81db2` · neutral · why_it_matters; [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]])
- “released FrontierMath: Tiers 1–4 (v2) after auditing errors in 42% of problems” (`d9ec6c4fe539` · supporting · evidence_snippets[0]; [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]])
- “This substantially raised scores while preserving rankings” (`644d36957553` · supporting · evidence_snippets[1]; [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]])

## Source

- [[sources/ainews-fable-and-mythos-officially-too-dangerous-to-release-01ktzm3wmdhptvdzsea8sh3tqv|[AINews] Fable and Mythos officially too dangerous to release]]
