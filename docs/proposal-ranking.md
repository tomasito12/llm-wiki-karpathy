# proposal-ranking.md

## Purpose

This document defines the ranking philosophy and prioritization system for extraction proposals generated during ingestion.

Proposal ranking exists to allocate human attention efficiently.

The purpose is not to rank proposals by technical extractability.

The purpose is to rank proposals by:

* durable operational value
* review worthiness
* strategic importance
* long-term reuse potential
* usefulness for AI engineering and service automation

The ranking system is fundamentally an attention-allocation system.

---

# Core Principle

The ingestion system should ask:

> Which proposals deserve human attention?

NOT:

> Which proposals can technically be extracted?

This distinction is critical.

A proposal may be:

* technically correct
* well-supported
* semantically valid

while still not deserving review attention or durable wiki integration.

---

# Proposal Ranking Goals

The ranking system should:

* prioritize high-value durable knowledge
* reduce reviewer fatigue
* suppress weak proposals
* improve review throughput
* prevent ontology explosion
* minimize low-signal review work
* improve reviewer trust
* support conservative knowledge accumulation

The ranking system should NOT optimize for:

* extraction completeness
* proposal volume
* maximal recall
* taxonomy growth

---

# The Two Axes

Proposal prioritization is based on two independent axes:

1. Value Level
2. Confidence

These axes should remain conceptually separate.

---

# Value Level

Value level estimates:

> How useful is this proposal for long-term operational knowledge accumulation?

Value is primarily about:

* importance
* reuse potential
* durability
* strategic significance
* operational relevance

Value is NOT the same as confidence.

---

# Confidence

Confidence estimates:

> How likely is the extraction itself to be correct and well-supported?

Confidence is primarily about:

* extraction reliability
* evidence quality
* semantic clarity
* ambiguity
* source strength

Confidence is NOT the same as usefulness.

---

# Value Levels

## High Value

High-value proposals should represent:

* durable operational understanding
* reusable conceptual structures
* important architectural patterns
* meaningful workflow implications
* strategically important trends
* strong implementation insights
* concepts likely to recur across many sources

Examples:

* orchestration architectures
* agent workflow patterns
* context engineering shifts
* service automation strategies
* evaluation methodology changes
* durable infrastructure trends

High-value proposals deserve reviewer attention.

---

## Medium Value

Medium-value proposals may be:

* useful but narrow
* operationally relevant but not foundational
* moderately reusable
* context-dependent
* partially redundant with existing knowledge

Medium-value proposals should usually remain collapsed by default.

---

## Low Value

Low-value proposals often include:

* supporting terminology
* transient observations
* shallow trends
* hype-driven claims
* weakly differentiated concepts
* obvious definitions
* repetitive insights
* low-reuse operational details

Low-value proposals should usually be:

* hidden
* collapsed
* batch-rejected
* or skipped entirely

The system should aggressively suppress low-value extraction noise.

---

# Confidence Levels

## High Confidence

Characteristics:

* strong textual evidence
* clear semantic boundaries
* explicit discussion in source
* low ambiguity
* repeated reinforcement in source

High-confidence proposals should be easy to approve quickly.

---

## Medium Confidence

Characteristics:

* moderate evidence
* partially inferred extraction
* some ambiguity
* incomplete support
* possible overlap with other concepts

These deserve normal review.

---

## Low Confidence

Characteristics:

* weak evidence
* speculative extraction
* ambiguous wording
* inferred conceptual mapping
* unclear routing
* unclear operational significance

Low-confidence proposals should receive careful review or suppression.

---

# Value × Confidence Matrix

The dashboard should prioritize proposals based on the combination of:

* value
* confidence

Example behavior:

| Value  | Confidence | Recommended UX             |
| ------ | ---------- | -------------------------- |
| High   | High       | Auto-expanded, prioritized |
| High   | Medium     | Explicit review            |
| High   | Low        | Careful review             |
| Medium | High       | Collapsed but visible      |
| Medium | Medium     | Collapsed                  |
| Medium | Low        | Hidden unless expanded     |
| Low    | High       | Batch actions allowed      |
| Low    | Medium     | Hidden by default          |
| Low    | Low        | Suppressed or skipped      |

The reviewer should spend most attention on:

* high-value proposals
* high-impact low-confidence proposals
* ontology-changing proposals

---

# Ranking Criteria

The ranking system should consider the following dimensions.

---

# 1. Durability

Question:

> Will this likely still matter in 6–12 months?

Durability is one of the strongest ranking signals.

Durable operational insights should rank highly.

Transient discourse should rank low.

---

# 2. Operational Relevance

Question:

> Does this affect real AI workflows, orchestration, evaluation, automation, or service systems?

Operationally actionable knowledge should rank highly.

Pure commentary should rank lower.

---

# 3. Reuse Potential

Question:

> Could this knowledge reasonably enrich multiple future pages or sources?

Reusable concepts should rank highly.

One-off observations should rank lower.

---

# 4. Strategic Importance

Question:

> Does this reflect a broader industry or architectural shift?

Examples:

* changing orchestration patterns
* context engineering evolution
* coding-agent workflow shifts
* model economics
* infrastructure bottlenecks
* service automation implications

Strategic shifts deserve high ranking.

---

# 5. Novelty

Question:

> Does this add genuinely new understanding?

The system should avoid repeatedly proposing:

* obvious concepts
* already-ingested knowledge
* generic industry talking points

Novelty should strongly influence ranking.

---

# 6. Evidence Strength

Question:

> Is the proposal strongly grounded in the source?

Strong evidence improves confidence.

Weak evidence should suppress ranking.

---

# 7. Relevance To The Operator

The system should prioritize knowledge useful for:

* AI engineering
* orchestration
* evaluation
* coding-agent workflows
* conversational AI
* service automation
* enterprise AI systems
* operational AI tooling

The system is intentionally specialized.

---

# Ranking Philosophy By Knowledge Layer

Different layers require different ranking behavior.

---

## Glossary

Glossary ranking should be extremely conservative.

A glossary proposal should only rank highly if:

* reusable
* durable
* industry-relevant
* operationally meaningful
* likely to recur across sources

Supporting terminology should rank low.

---

## Topics

Topics should prioritize:

* recurring operational themes
* reusable architecture concepts
* durable workflow understanding

Topics should emerge slowly and conservatively.

---

## How-Tos

How-tos should prioritize:

* reusable workflows
* implementation strategies
* operational procedures
* practical engineering patterns

Micro-howtos should rank low.

---

## Trends

Trends should require:

* repeated evidence
* strategic significance
* durable directional movement

Weak speculation should rank low.

---

## Tools

Tool extraction should prioritize:

* workflow relevance
* ecosystem importance
* operational differentiation

Minor tools should rank low.

---

## Models

Model extraction should prioritize:

* workflow implications
* orchestration implications
* positioning shifts
* operational tradeoffs

Minor benchmark differences should rank low.

---

# Skip Recommendations

The ranking system should be allowed to conclude:

> No durable extraction recommended.

This is healthy behavior.

Low-signal articles should not force proposal generation.

---

# Proposal Budgets

Ranking and extraction budgets are tightly connected.

The system should rank candidates before applying extraction budgets.

Only the strongest proposals should survive truncation.

The system should prefer:

> 2 strong proposals

over:

> 10 mediocre proposals

---

# Semantic Compression

The ranking system should prefer semantically compressed proposals.

Example:

Instead of proposing separately:

* provenance
* auditability
* explainability
* grounding

the system may prefer a stronger higher-level proposal such as:

* trustworthy AI grounding architectures

This reduces reviewer fatigue and ontology fragmentation.

---

# Reviewer Attention Is Expensive

Every visible proposal has cognitive cost.

Therefore the ranking system should actively suppress:

* weakly differentiated proposals
* low-value terminology
* repetitive conceptual variants
* ontology clutter
* metadata-heavy low-signal extraction

Review burden is a core ranking consideration.

---

# Anti-Goals

The ranking system should avoid optimizing for:

* maximal extraction volume
* maximal entity counts
* ontology expansion
* aggressive taxonomy growth
* exhaustive article decomposition
* benchmark obsession
* superficial trend extraction

---

# Long-Term Philosophy

The proposal-ranking system exists to protect the long-term sustainability of the knowledge system.

A smaller number of high-quality durable proposals is preferable to a large volume of weakly curated extraction artifacts.

The ranking system should remain conservative, pragmatic, and human-attention-aware.
