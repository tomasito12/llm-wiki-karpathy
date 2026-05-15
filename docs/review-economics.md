# review-economics.md

## Purpose

This document defines the philosophy and operational principles behind the human-review workflow of the LLM wiki ingestion system.

The purpose of review is not merely quality control.

The purpose of review is to allocate scarce human cognitive attention toward the highest-value knowledge decisions.

The system should optimize for:

> maximum durable operational knowledge gained per minute of human attention

Review time is not an implementation detail.

It is a primary system constraint.

---

# Human Attention Is The Bottleneck

The limiting factor of the system is not:

* storage
* inference cost
* extraction capability
* prompt complexity
* schema richness

The limiting factor is:

* reviewer energy
* reviewer focus
* reviewer consistency
* reviewer motivation
* long-term cognitive sustainability

A system that requires excessive review effort will eventually collapse under its own maintenance burden.

---

# The Core Failure Mode

The primary failure mode of AI-assisted ingestion systems is:

> extraction recall optimized beyond human review capacity

Symptoms include:

* too many proposals
* ontology explosion
* endless taxonomy decisions
* micro-decision fatigue
* over-reviewing low-risk content
* declining reviewer trust
* growing deferred backlogs
* increasing review avoidance

The system must actively resist this tendency.

---

# Durable Knowledge Per Minute

The primary KPI of the ingestion-review system is:

> durable operational knowledge gained per minute of human review

Not:

* number of extracted entities
* number of wiki pages
* ingestion throughput
* extraction completeness
* number of tags
* amount of generated text

The goal is not to maximize output volume.

The goal is to maximize long-term useful understanding.

---

# Review-Time Targets

The review process should remain lightweight.

Target review durations:

| Source Type             | Target         |
| ----------------------- | -------------- |
| Normal article          | 2–5 minutes    |
| Dense technical article | max 10 minutes |
| Roundup                 | 3–8 minutes    |
| Interview/transcript    | 5–10 minutes   |

If review consistently exceeds these targets, the system should be considered operationally unhealthy.

Long review times indicate:

* over-extraction
* poor prioritization
* weak ranking
* low proposal precision
* excessive visible complexity
* ontology instability

---

# Precision Over Recall

The ingestion-review workflow should strongly prefer:

* precision over recall
* fewer strong proposals over many mediocre ones
* durable concepts over supporting details
* operationally relevant insights over exhaustive coverage

The system should intentionally under-extract when uncertain.

Missing a few weak insights is acceptable.

Exhausting the reviewer is not.

---

# Proposal Economics

Every proposal consumes human attention.

Therefore every proposal has a cost.

The system should ask:

> Is this proposal worth the reviewer attention it requires?

This is more important than:

> Can this proposal technically be extracted?

---

# Extraction Budgets

Proposal generation must remain constrained.

Unlimited extraction creates:

* review fatigue
* ontology drift
* taxonomy explosion
* declining signal quality

The system should use explicit extraction budgets.

Conservative defaults are preferred.

Example philosophy:

* glossary proposals should be rare
* trends should require strong evidence
* how-tos should require real reuse potential
* topics should emerge gradually

The system should prefer:

> fewer stronger candidates

over:

> many weak candidates

---

# Value-Based Attention Allocation

Not all proposals deserve equal attention.

Each proposal should include:

* value level
* confidence
* durability estimate
* operational relevance

Human attention should prioritize:

* high-value proposals
* low-confidence high-impact proposals
* novel operational concepts
* strategic trends
* reusable workflow knowledge

Low-value proposals should:

* remain collapsed
* remain hidden
* or be skipped entirely

---

# Confidence-Weighted Review

High-confidence, low-risk proposals should be easy to approve quickly.

Detailed review should focus on:

* ambiguous proposals
* novel concepts
* ontology-changing proposals
* weakly evidenced claims
* strategic trend extraction
* new tags/categories

The reviewer should not spend most time validating obvious low-risk content.

---

# Proposal-Level Review

Review should happen primarily at the proposal level.

The default reviewer actions should be:

* approve
* reject
* defer
* edit

The system should avoid:

* field-by-field approvals
* repetitive micro-edits
* excessive metadata validation
* taxonomy micromanagement

Field-level editing should remain available, but not dominant.

---

# Progressive Disclosure

Visible complexity creates cognitive cost.

The dashboard should therefore:

* show high-value information first
* collapse secondary metadata
* reduce simultaneous decisions
* reveal complexity only when needed

The reviewer should never feel overwhelmed by the UI.

---

# Deferred Decisions Are Healthy

The system should support uncertainty.

Not every proposal requires an immediate decision.

Deferred proposals are valid and expected outcomes.

Deferred queues reduce:

* forced binary decisions
* ontology instability
* reviewer fatigue
* rushed judgments

The deferred queue functions as a knowledge inbox.

---

# Review Trust

The reviewer must trust the system.

Trust emerges from:

* transparency
* predictable behavior
* good ranking
* understandable reasoning
* conservative extraction
* low hallucination rates
* visible provenance

The system should avoid:

* aggressive extraction
* fake certainty
* excessive hype
* overconfident weak proposals

---

# Reviewer Calibration

The reviewer is continuously calibrating the ingestion system.

Review behavior itself is valuable signal.

Important metrics include:

* approval rate
* rejection rate
* defer rate
* edit frequency
* review duration
* proposal-type friction
* repeated rewrite patterns

Review telemetry should guide future improvements.

---

# Review Analytics

The system should track review economics explicitly.

Important metrics include:

* review duration
* proposals per article
* edits per proposal type
* approval/rejection/defer rates
* hidden vs expanded proposal usage
* glossary acceptance rates
* trend rejection rates
* average edits per accepted proposal

The purpose is not surveillance.

The purpose is workflow optimization.

---

# Proposal Quality > Proposal Quantity

Once basic extraction works, the primary optimization target becomes:

> proposal quality calibration

The system should improve:

* ranking precision
* worthiness detection
* novelty estimation
* operational usefulness estimation
* reviewer trust

Increasing extraction quantity is usually harmful.

---

# Ontology Stability

Ontology instability creates hidden review costs.

Too many:

* tags
* concepts
* categories
* micro-topics
* weak pages

eventually degrade system usability.

Ontology growth should remain conservative and slow.

Stable structures are more valuable than rapid expansion.

---

# Skip Logic Is Healthy

The ingestion system must be allowed to conclude:

> This source does not justify durable extraction.

This is a sign of maturity, not failure.

Not every article deserves long-term integration.

Especially:

* low-signal Medium posts
* repetitive news
* weak trend speculation
* hype-driven discourse
* shallow summaries

should often be skipped.

---

# The Goal Is Long-Term Sustainability

The ingestion-review workflow should remain maintainable by a single human operator over many years.

A slower, more sustainable system is preferable to:

* aggressive autonomous ingestion
* uncontrolled page growth
* rapidly expanding ontology
* permanently growing review debt

The system should remain:

* understandable
* maintainable
* trustworthy
* cognitively sustainable

over the long term.

---

# Anti-Goals

The review system should avoid becoming:

* a bureaucracy simulator
* a metadata management exercise
* a taxonomy obsession engine
* a micro-approval workflow
* a high-volume extraction machine
* a gamified ingestion system

The purpose is durable operational understanding accumulation.

Not maximal information extraction.

---

# Long-Term Philosophy

The highest-quality knowledge systems are not built through maximal ingestion.

They are built through disciplined curation.

The system should evolve slowly, intentionally, and conservatively.

The goal is not to collect everything.

The goal is to build a durable operational intelligence system that remains useful, understandable, and reviewable for many years.
