# Second Brain Vision

This document captures the long-term purpose of the LLM Wiki system.

It is not an implementation plan. It is the north star that should help future
sessions decide whether a proposed change supports the real goal or only adds
complexity.

## Core Goal

The goal is to build a personal and eventually team-usable AI knowledge system
that supports real work.

The system should help with project drafts, research, concept work, daily
reflection, trend monitoring, and decision support by giving an LLM agent access
to the knowledge the user has already read, written, reviewed, or discussed.

In short:

> The wiki should become a grounded second brain for work, not just a collection
> of summaries.

## Knowledge Domains

The long-term knowledge base is expected to contain several connected domains.

### Read Sources

Articles, papers, newsletters, documentation, and other source material captured
through Readwise or similar workflows.

These sources are processed into the generated wiki:

- source pages
- topic pages
- glossary pages
- how-to pages
- trend pages
- tool and model pages
- signals, interview insights, and implementation studies

The raw source text should remain available so an agent can always go deeper
than the synthesized page when needed.

### Personal Notes

Daily notes, reflections, working notes, and project notes should live in
Obsidian beside the generated wiki, but not be overwritten by the wiki renderer.

These notes capture:

- what happened during the day
- what the user learned
- open questions
- decisions
- rough ideas
- weak signals that are not yet formal wiki knowledge

### Meeting Transcripts

Meeting transcripts and related notes should become another knowledge domain.

They should help an agent understand:

- project history
- team decisions
- commitments
- unresolved questions
- customer or stakeholder context

### Generated Wiki

The generated wiki is the curated knowledge layer built from reviewed sources.

Its purpose is to provide:

- stable concepts
- reusable summaries
- source-backed synthesis
- related-page navigation
- tag-based routing
- compact context pages for agents

The wiki should stay human-readable, but it is also designed to be loaded by an
LLM agent as structured context.

## Architectural Layers

The generated wiki is not the final product by itself. It is the grounding
layer for agents and for human review.

Over time, the complete system may contain several layers:

- raw source storage
- reviewed source artifacts
- evidence graph data
- synthesized wiki pages
- personal notes and meeting notes
- retrieval indexes across all knowledge domains
- agent-facing tools or APIs
- optional web or team-facing surfaces

The generated Obsidian wiki should remain the durable, readable knowledge
surface. Retrieval and agent tooling can be built around it later, but they
should not make the core knowledge layer opaque.

## Primary Use Cases

### Human Browsing

The user can open Obsidian and browse the generated wiki, follow related links,
inspect sources, and review what the system currently knows.

This is useful, but it is not the only or even the final use case.

### Agent Context for Daily Work

The more important use case is that a local agent can access the wiki while the
user works on projects.

When the user asks a question, drafts a concept, researches a topic, or prepares
a project plan, the agent should be able to:

- search the wiki
- inspect tag indexes
- load relevant synthesis pages
- follow related-page links
- open source pages
- read raw source text when deeper evidence is needed
- compare generated wiki knowledge with personal notes and meeting notes

The user should not have to remember where every relevant idea came from. The
agent should help retrieve and connect it.

### Retrieval Across Knowledge Domains

Long term, agents should not search only generated wiki pages.

They should be able to retrieve across:

- Stage 2 synthesis pages
- Stage 1 evidence metadata
- source pages
- raw source text
- daily notes
- project notes
- meeting notes and transcripts

Not everything should become a polished wiki page. Some information is better
used through retrieval, while the generated wiki remains the curated layer for
stable concepts and reusable synthesis.

### Team or API Access

Later, the wiki may be exposed through an API or web surface so that teammates
or other agents can query it.

This is a future possibility, not a current implementation priority.

The important design implication is that the knowledge layer should remain:

- source-backed
- structured
- versionable
- machine-readable
- not locked inside only one chat session or UI

### Weekly Intelligence and Trend Monitoring

In a later stage, an agent may compare:

- new sources
- recent notes
- meeting context
- existing wiki knowledge

and produce weekly suggestions such as:

- important new AI trends
- new models or tools worth watching
- concepts that deserve synthesis
- weak signals becoming stronger
- project opportunities based on the user's current work

This should feel like an assistant that notices meaningful changes, not like a
feed of generic AI news.

## Design Principles

### Preserve Raw Evidence

The system must not depend only on compressed summaries.

Raw sources, reviewed source artifacts, evidence items, and generated synthesis
each have a role. The agent should be able to move from a compact page back to
the original evidence when needed.

### Keep Obsidian Useful

Obsidian should remain a readable workspace.

The generated wiki should not flood the vault with every intermediate machine
artifact. Machine-heavy state can live under `state/`; human-facing pages should
remain navigable.

### Prefer Retrieval Before More Ontology

As the corpus grows, not every distinction needs a new page or category.

Before adding new ontology or new page types, prefer better retrieval, better
indexes, better evaluation questions, and clearer page quality rules.

### Treat Synthesis as a Materialized View

Synthesized pages are useful, but they are not the source of truth.

They can be regenerated from review artifacts, evidence graph data, prompt
versions, and cache state.

### Separate Trust Levels

The system should preserve the difference between types of knowledge.

An agent should not treat all retrieved text as equally authoritative. It should
be able to distinguish:

- raw source text
- reviewed source summaries
- Stage 1 evidence items
- Stage 2 synthesis pages
- personal notes
- meeting transcripts
- agent-generated suggestions
- unreviewed hypotheses

This distinction matters because personal notes, source claims, and synthesized
wiki statements have different reliability and different uses.

### Separate Working Memory from Long-Term Memory

Not every useful note belongs in the long-term wiki.

Daily notes, meeting notes, project drafts, and rough observations can act as
working memory. They may inform future synthesis, but they do not automatically
become durable wiki knowledge.

The generated wiki should remain the long-term memory layer for stable,
source-backed concepts. Working memory can stay messier, more temporary, and
closer to active projects.

### Keep Suggestions Separate from Truth

Future weekly intelligence or trend-monitoring agents should produce
suggestions, not silently update the user's truth layer.

Good outputs are things like:

- "This trend may be getting stronger."
- "These notes suggest a possible project opportunity."
- "This new source may belong on an existing page."
- "This claim appears to conflict with older evidence."

Those outputs should invite review. They should not automatically become
canonical wiki facts.

### Reduce Cognitive Load

The system should reduce the user's cognitive load, not create another inbox.

If a feature creates more review work, more decisions, or more pages without
making daily work easier, it should be treated with suspicion.

The best version of the system helps the user remember, connect, and act
without forcing constant maintenance.

### Optimize for Trust

The system is valuable only if the user can trust where knowledge came from.

Useful pages should make it clear:

- which sources support the claim
- how strong the evidence is
- where there is disagreement
- where a page is thin or single-source
- when deeper source inspection is needed

### Avoid Feature Sprawl

The near-term priority is to complete and stabilize the current wiki synthesis
step.

New ideas such as APIs, web dashboards, weekly agents, team access, and
cross-note intelligence are part of the long-term vision, but they should not
pull attention away from making the current foundation reliable.

## Current Strategic Priority

The next phase should focus on finishing the existing Stage 2 synthesis layer:

- make generated pages more human-readable
- keep source and evidence access intact
- avoid unnecessary LLM calls
- ensure only changed pages need new synthesis
- preserve deterministic rendering and linting
- keep Obsidian output usable

Do not add major new product surfaces until this layer feels stable enough to
trust.

## What Success Looks Like

The system is succeeding when:

- the user can ask work questions and the agent finds relevant wiki context
- important source knowledge is not lost after weeks or months
- the user can inspect sources behind important claims
- Obsidian remains useful rather than overwhelming
- weekly or project-level synthesis can build on existing knowledge
- the system helps the user notice connections they would otherwise miss
- maintenance effort stays low enough that the system survives real life

The final product is not just an archive.

It is a working memory layer for the user's projects, research, notes, meetings,
and decisions.
