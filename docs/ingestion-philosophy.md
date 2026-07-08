# ingestion-philosophy.md

## Purpose

This wiki is not a generic note-taking system and not a document archive.

It is a long-term operational knowledge system focused on AI engineering, AI tooling, orchestration, service automation, coding agents, evaluation systems, infrastructure, and industry developments.

The purpose of ingestion is not to preserve everything.

The purpose is to accumulate durable operational understanding over time.

The ingestion system should optimize for:

* reusable knowledge
* durable concepts
* operational relevance
* strategic understanding
* architectural patterns
* implementation lessons
* long-term maintainability
* human review efficiency

The system should not optimize for extraction completeness.

---

# User Role And Relevance Filter

The primary user works at EnBW as an AI expert in a team that builds Cognigy AI
chatbots and voicebots for customer service. The operating goal is to shift
suitable service volume into reliable AI-supported chat and voice channels while
preserving quality, escalation, governance, and maintainability.

During ingestion, treat these as strong relevance signals:

* service automation and contact-center transformation
* chatbot and voicebot architecture, evaluation, reliability, and monitoring
* Cognigy AI implementation knowledge
* Cognigy competitors, replacement platforms, and adjacent tools
* orchestration and workflow design around bot platforms
* human handoff, routing, fallbacks, and operational governance
* AI workflow improvement for internal teams
* general AI expertise with practical engineering, product, strategy, or governance value

Cognigy is context, not a vendor lock-in boundary. Do not reject useful ideas
only because they are not Cognigy-specific. Knowledge about alternatives,
surrounding workflows, and broader AI practice is valuable when it helps the
user make better decisions as an AI expert.

---

# Core Principle

The central question during ingestion is:

> What durable operational understanding from this source deserves long-term accumulation?

NOT:

> What can technically be extracted from this source?

This distinction is fundamental.

The ingestion system should prefer:

* precision over recall
* fewer high-value proposals over many mediocre proposals
* reviewer attention efficiency over exhaustive extraction
* durable insights over transient discourse
* operational usefulness over summarization completeness

---

# Human Attention Is The Scarce Resource

The bottleneck of the system is not:

* LLM capability
* extraction capability
* prompt complexity
* storage

The bottleneck is human cognitive attention.

The ingestion-review workflow must therefore optimize for:

> maximum durable knowledge gained per minute of human review

Review ergonomics are a first-class architectural concern.

---

# The Role Of Human Review

The human reviewer is not validating every sentence.

The reviewer acts as:

* curator
* prioritizer
* ontology stabilizer
* strategic filter
* long-term memory architect

The reviewer should focus attention on:

* high-value proposals
* ambiguous proposals
* novel concepts
* strategic trends
* operationally important insights

The reviewer should NOT spend most time on:

* obvious definitions
* low-value metadata
* repetitive taxonomy work
* micro-edits
* field-by-field approvals

---

# Durable Knowledge vs Source Summarization

The system is not primarily designed to summarize articles.

The system is designed to extract reusable operational knowledge.

A source may be:

* interesting
* well-written
* technically accurate
* insightful

while still not deserving durable wiki extraction.

The ingestion system must be allowed to conclude:

> No durable wiki extraction recommended.

This is healthy behavior.

---

# Knowledge Layers

Different layers of the wiki have different purposes.

## Sources

Purpose:
Preserve provenance and source-level context.

Sources are archives of what was said.

They are not the main durable knowledge layer.

---

## Glossary

Purpose:
Maintain durable conceptual reference knowledge.

Glossary entries should represent concepts that matter independently of a specific article.

A glossary term should only be proposed if:

* it is reusable
* industry-relevant
* operationally meaningful
* likely to recur across sources
* useful for AI engineering or service automation

The glossary is NOT a summary of article terminology.

---

## Topics

Purpose:
Accumulate reusable operational understanding around a durable theme.

Topics should emerge from repeated evidence across sources.

Topics are long-lived operational knowledge structures.

---

## How-Tos

Purpose:
Capture reusable implementation or workflow knowledge.

How-tos should focus on:

* operational execution
* implementation strategies
* workflows
* practical architecture patterns

How-tos should avoid becoming fragmented micro-pages.

---

## Trends

Purpose:
Track durable strategic industry developments.

Trends should represent:

* recurring shifts
* emerging practices
* changing architecture patterns
* workflow transformations
* ecosystem movements

Trends are not daily news summaries.

---

## Implementation studies

Purpose:
Document **organizational operational deployments** with auditable real-world evidence — not generic “someone built something” narratives.

An implementation study should only be proposed when the source supports at least one of:

* production or serious pilot deployment in real operations
* operational metrics or measurable outcomes
* organizational adoption at stated scale
* scaling constraints discovered in live usage
* grounded success/failure or maintenance lessons from deployment

The same article may still yield strong **topics**, **how-tos**, or **trends** proposals while correctly producing **zero** implementation studies.

Do **not** use implementation studies for:

* personal experiments or weekend builds
* architecture essays without operational outcomes
* speculative workflows or prototype writeups without deployment evidence
* generic practitioner narratives without deployment facts
* vendor marketing without concrete deployment detail

Prefer **topics** for durable patterns without a specific org case; prefer **how-tos** for reusable procedures without org-specific deployment evidence.

---

## Tools

Purpose:
Track tools relevant to operational AI workflows.

Tool pages should focus on:

* workflow role
* operational strengths
* architectural positioning
* ecosystem relevance
* practical usage implications

Not exhaustive feature lists.

---

## Models

Purpose:
Track foundation models and their operational implications.

Model pages should focus on:

* capabilities
* positioning
* orchestration implications
* workflow suitability
* inference tradeoffs
* ecosystem role

Not benchmark obsession.

---

# Source-Type-Aware Ingestion

Different source types require different extraction behavior.

The system should first detect source type before extraction.

Supported source types include:

* standard_article
* ai_industry_roundup
* interview_or_transcript
* technical_howto
* research_paper_or_report
* unknown

Extraction behavior should adapt to source structure.

---

# Roundup Philosophy

Roundups are not coherent knowledge objects.

They are bundles of:

* weak signals
* strong signals
* news items
* architectural observations
* hype
* tooling updates
* operational discussions

The ingestion system should decompose roundups into smaller signal candidates.

Most signals should ultimately be ignored.

The question is not:

> What happened today?

The question is:

> Which durable operational signals are worth long-term accumulation?

---

# Interview Philosophy

Interviews and transcripts often contain:

* strategic viewpoints
* architectural reasoning
* implementation lessons
* operational observations
* predictions
* industry narratives

The ingestion system should prioritize:

* reusable insights
* operational implications
* conceptual shifts
* strategic patterns

The system should avoid extracting:

* conversational filler
* personality-driven commentary
* repetitive anecdotes

---

# Proposal Budgets

Extraction must remain constrained.

Unlimited extraction causes:

* ontology explosion
* review fatigue
* taxonomy drift
* declining signal quality

The system should use explicit extraction budgets.

Conservative defaults are preferred.

Example philosophy:

* only propose the strongest glossary concepts
* only propose the strongest topics
* only propose how-tos with real operational reuse potential

The system should prefer under-extraction over over-extraction.

---

# Proposal Ranking

Not all proposals deserve equal human attention.

Each proposal should contain:

* value level
* confidence
* operational importance

Human attention should prioritize:

* high-value proposals
* low-confidence high-impact proposals
* durable operational insights

Low-value proposals should be collapsed, hidden, or skipped.

---

# Proposal-Level Review

The review workflow should operate primarily at the proposal level.

The reviewer should mostly decide:

* approve
* reject
* defer
* edit

The system should avoid requiring field-by-field approvals.

Field-level editing should remain possible, but not dominant.

---

# Progressive Disclosure

Visibility builds trust.

Hidden complexity builds efficiency.

The dashboard should therefore:

* expose high-value information first
* collapse secondary metadata
* avoid overwhelming the reviewer
* reveal complexity only when requested

---

# Deferred Knowledge

Not all proposals should require immediate decisions.

Deferred proposals are valid outcomes.

The system should support:

* review later
* revisit later
* delayed ontology decisions

Deferred queues are intentional parts of the workflow.

---

# Tags

Tags are lightweight metadata.

They are not the primary knowledge structure.

Tagging should remain simple and constrained.

The system should avoid:

* taxonomy explosion
* over-tagging
* excessive ontology maintenance

---

# Related Terms And Graph Enrichment

Related terms and semantic graph enrichment are important long-term capabilities.

However:

graph enrichment is NOT the same as ingestion review.

Related terms should generally be:

* generated automatically
* hidden from primary review
* refined later through graph enrichment workflows

---

# Idempotency And Provenance

All ingestion artifacts should preserve:

* source provenance
* extraction provenance
* prompt version
* schema version
* model metadata
* review history
* human modifications

Artifacts should remain reproducible and migratable.

---

# Anti-Goals

The system should avoid becoming:

* a generic PKM system
* a note dump
* an automatic wiki generator
* an autonomous content farm
* an exhaustive article summarizer
* a benchmark archive
* a taxonomy obsession machine

The goal is operational intelligence accumulation.

---

# Long-Term Philosophy

The system should evolve slowly.

Ontology stability is more important than ingestion speed.

A smaller number of durable, high-quality knowledge structures is preferable to large volumes of weakly curated content.

The system should remain understandable, maintainable, and reviewable by a single human operator over many years.
