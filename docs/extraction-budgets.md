# extraction-budgets.md

## Purpose

This document defines the philosophy, rationale, and operational behavior of extraction budgets within the LLM wiki ingestion system.

Extraction budgets exist to constrain proposal generation.

Their purpose is not technical limitation.

Their purpose is:

* protecting reviewer attention
* preventing ontology explosion
* suppressing low-value extraction
* improving proposal quality
* maintaining long-term system sustainability

Extraction budgets are one of the primary mechanisms that enforce disciplined knowledge accumulation.

---

# Core Principle

The ingestion system should optimize for:

> fewer stronger proposals

NOT:

> maximal extraction completeness

The system should strongly prefer:

* precision over recall
* durable insights over exhaustive decomposition
* reviewer throughput over extraction volume
* conceptual stability over ontology growth

Budgets operationalize these principles.

---

# Why Extraction Budgets Exist

Without budgets, LLM extraction systems naturally tend toward:

* combinatorial proposal explosion
* semantic redundancy
* ontology fragmentation
* weak concept differentiation
* reviewer fatigue
* excessive taxonomy growth
* declining signal quality

This behavior is especially common in:

* Medium articles
* AI roundups
* interviews
* concept-heavy architecture articles

Budgets act as structural constraints against these failure modes.

---

# Human Attention Is The Real Constraint

Extraction budgets are fundamentally attention-management systems.

Every proposal consumes:

* reviewer time
* reviewer focus
* ontology maintenance cost
* long-term cognitive overhead

Proposal volume therefore has real operational cost.

The ingestion system should continuously ask:

> Is this proposal worth the reviewer attention it requires?

---

# Budget Philosophy

Budgets should remain conservative.

Under-extraction is generally preferable to over-extraction.

Missing some weak insights is acceptable.

Exhausting the reviewer is not.

The system should prefer:

> a small number of durable high-quality proposals

over:

> many weakly differentiated candidates

---

# Default Budget Philosophy

Recommended default philosophy:

| Proposal Type | Recommended Default |
| ------------- | ------------------- |
| glossary      | 0–2                 |
| topics        | 0–2                 |
| howtos        | 0–1                 |
| trends        | 0–1                 |
| tools         | 0–1                 |
| models        | 0–1                 |

Dense concept-heavy articles may occasionally exceed these limits slightly.

However:
large proposal counts should generally be treated as extraction failure signals.

---

# Budgets Are Soft Strategic Constraints

Budgets should not behave like arbitrary truncation limits.

The extraction system should:

1. generate candidate proposals internally
2. rank proposals
3. apply semantic compression
4. suppress weak candidates
5. keep only the strongest surviving proposals

The goal is:

* quality selection
* not random cutoff

---

# Ranking Before Truncation

Budgets should only be applied AFTER proposal ranking.

The system should first estimate:

* value
* confidence
* durability
* novelty
* operational relevance

Then retain only the strongest candidates.

Weak proposals should disappear before review.

---

# Proposal Compression

Before budgets are applied, the system should attempt semantic compression.

Example:

Instead of separately proposing:

* provenance
* auditability
* explainability
* traceability

the system may prefer a stronger compressed proposal such as:

* trustworthy AI grounding architectures

This reduces:

* ontology fragmentation
* reviewer fatigue
* redundant concepts

Budgets and semantic compression are tightly connected.

---

# Glossary Budgets

Glossary extraction should be especially constrained.

Most articles should produce:

* zero
* one
* or two glossary proposals

Generating many glossary terms usually indicates:

* weak filtering
* source-keyword extraction
* semantic redundancy
* article-centric extraction behavior

The glossary should evolve slowly and conservatively.

---

# Topic Budgets

Topics should represent:

* durable operational themes
* recurring architectural concepts
* reusable workflow understanding

Topics should not become:

* article-specific pages
* overly narrow abstractions
* fragmented micro-concepts

The system should prefer broader durable synthesis.

---

# How-To Budgets

How-tos should require:

* clear operational reuse
* implementation relevance
* durable workflow applicability

Micro-howtos should be suppressed aggressively.

The system should avoid:

* tiny procedural fragments
* one-off setup steps
* narrow tooling trivia

---

# Trend Budgets

Trend extraction should be highly conservative.

A trend should require:

* strong evidence
* strategic significance
* repeated signals
* durable directional movement

Most articles should generate zero trend proposals.

Weak speculation should not become durable trend pages.

---

# Tool And Model Budgets

Tool and model extraction should occur only when:

* the source substantially discusses them
* operational implications exist
* workflow relevance is meaningful

Passing mentions should not generate proposals.

Example:

Mentioning Claude briefly is insufficient.

A proposal should require explicit operational discussion.

---

# Dynamic Budgets

Budgets may later become adaptive based on:

* source type
* article quality
* reviewer history
* source trust
* proposal quality distributions
* rejection rates
* defer rates

However:
initial implementations should remain simple and predictable.

Avoid premature optimization.

---

# Source-Type-Specific Budget Philosophy

Different source types naturally require different extraction density.

---

## Standard Articles

Usually:

* low-to-medium extraction density
* one or two strong concepts
* limited durable insights

Conservative budgets are appropriate.

---

## Roundups

Roundups naturally generate many weak signals.

Budgets are especially important here.

The system should prioritize:

* strongest operational shifts
* strongest recurring patterns
* strongest architectural observations

Most roundup content should ultimately be ignored.

---

## Interviews / Transcripts

Interviews often contain:

* repeated themes
* speculative discussion
* conversational redundancy

Budgets prevent over-fragmentation.

The system should prefer:

* compressed operational insights
* durable conceptual shifts
* strategic patterns

---

## Technical How-Tos

Technical guides may occasionally justify slightly denser extraction.

However:
the system should still prefer:

* reusable workflows
* generalized operational patterns

over:

* tiny implementation fragments

---

# Budget Failure Signals

The following are warning signs:

* consistently large proposal counts
* high rejection rates
* reviewer fatigue
* many semantically overlapping proposals
* excessive glossary growth
* taxonomy instability
* long review durations

These indicate extraction budgets are too loose.

---

# Relationship To Review Economics

Extraction budgets are one of the primary tools for maintaining sustainable review economics.

Budgets directly influence:

* review duration
* cognitive load
* reviewer trust
* ontology growth
* long-term maintainability

Budget tuning is therefore a core workflow optimization activity.

---

# Relationship To Proposal Ranking

Budgets should never exist independently of proposal ranking.

The ranking system determines:

> which proposals deserve survival under constrained reviewer attention

Budgets operationalize those prioritization decisions.

---

# Relationship To Skip Logic

Strong skip logic reduces unnecessary extraction pressure.

The system should be allowed to conclude:

> no durable extraction recommended

This is preferable to filling budgets artificially with weak proposals.

Budgets are upper bounds, not extraction targets.

---

# Anti-Goals

Extraction budgets should NOT become:

* arbitrary quotas
* gamified extraction targets
* incentives for proposal inflation
* rigid schema constraints
* excuses for low-quality ranking

The purpose is disciplined knowledge accumulation.

Not volume management for its own sake.

---

# Long-Term Philosophy

Knowledge systems degrade when extraction expands faster than curation quality.

Extraction budgets intentionally slow ontology growth.

This is healthy.

The system should evolve:

* conservatively
* intentionally
* sustainably

A smaller number of durable high-quality concepts is more valuable than a rapidly expanding noisy knowledge graph.
