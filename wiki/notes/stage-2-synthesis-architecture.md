---
title: Stage 2 Synthesis Architecture
category: notes
status: draft
created: 2026-06-16
tags:
  - wiki-architecture
  - obsidian
  - stage-2-synthesis
aliases:
  - Stage 2 Wiki Synthesis Plan
---

# Stage 2 Synthesis Architecture

This note captures the architecture decisions for turning the current generated wiki into a maintainable human-reviewable knowledge system.

The goal is not to build a complex ontology engine. The goal is a calm, traceable system where:

- sources remain readable
- evidence remains complete
- synthesis is useful for humans
- LLM calls do not explode
- entity merges remain auditable
- Obsidian does not become a dump of machine intermediate state

> [!important]
> The final rendered pages should be Obsidian-native notes, not generic Markdown exports. They should use stable properties, wikilinks, readable headings, and compact sections that work well in Obsidian Reading View and search.

## Current problem

The current `wiki-render` is a good Stage 1 system. It collects reviewed article artifacts, merges contributions by entity slug, and preserves evidence and provenance.

But it is not yet a good human-facing synthesis layer. Many generated pages contain all relevant evidence, but the reader still has to perform the real synthesis manually.

The existing pages are explicitly marked as:

```yaml
synthesis_state: stage1-placeholder
```

That means the lead prose is not a true multi-source synthesis. It is usually the highest-ranked single-source contribution.

## Target architecture

Use three layers.

```text
state/reviews/*
        |
        v
Stage 1 evidence graph
        |
        v
Stage 2 synthesis cache
        |
        v
human-readable Obsidian pages
```

### Layer 1: review artifacts

Path:

```text
state/reviews/<source_id>/review.json
```

This remains the source of truth.

Rules:

- Keep detailed source-level extraction here.
- Do not treat generated Markdown as canonical.
- If generated content is wrong, fix the review artifact or entity-resolution config, then regenerate.

### Layer 2: Stage 1 evidence

Current path:

```text
state/wiki_render_graph.json
```

Possible future path:

```text
state/evidence/<category>/<slug>.jsonl
```

This layer is allowed to be detailed, redundant, and machine-oriented. It is the evidence ledger.

Rules:

- Preserve all approved EvidenceItems.
- Preserve source IDs, evidence IDs, stance, confidence, dates, fields, and source metadata.
- Do not optimize this layer for pleasant reading.
- Do not make this layer the main Obsidian surface.

### Layer 3: Stage 2 synthesis

Possible cache path:

```text
state/synthesis/<category>/<slug>.json
```

This is the cached LLM-generated synthesis for a knowledge object.

The Obsidian page is a render output from:

- Stage 2 synthesis cache
- Stage 1 evidence metadata
- source links
- related pages

Rules:

- The synthesis is a materialized view, not the source of truth.
- The synthesis must be reproducible from review artifacts plus evidence graph plus synthesis prompt version.
- The old synthesis may be used as context, but it must not be the only input.

## Critical anti-pattern

Do not update synthesis like this:

```text
old compressed page + new source -> new compressed page
```

This causes summary-of-summaries drift. Details disappear over time, and old framing silently dominates new evidence.

Use this instead:

```text
all review artifacts -> evidence graph -> synthesis
```

Pragmatic update form:

```text
previous synthesis + full relevant evidence + new evidence -> updated synthesis
```

The full relevant evidence remains the grounding layer.

## What belongs in Obsidian

Obsidian should stay useful for humans and LLM navigation.

Visible:

- `wiki/sources/`
- `wiki/topics/`
- `wiki/industry-trends/`
- `wiki/how-to/`
- `wiki/tools/`
- `wiki/foundation-models/`
- `wiki/glossary/`
- `wiki/signals/`
- `wiki/interview-insights/`
- `wiki/implementation-studies/`
- `wiki/indexes/`

Not visible as normal wiki pages:

- all atomized EvidenceItems
- append-only grouped evidence dumps
- machine-oriented intermediate states

The complete evidence should remain reachable through state files and source backlinks, but it should not dominate normal Obsidian search and graph navigation.

## Primary access patterns

The architecture must support two main ways of using the wiki.

### Human question flow

The user starts with a question or problem and wants to reach a useful page quickly.

Expected flow:

```text
question/problem
        |
        v
tag or related tag
        |
        v
tag hub / by-tag index
        |
        v
best how-to, topic, trend, or source
        |
        v
source backlinks if verification is needed
```

This means tag navigation must not only list all matching pages. It must help the user choose the right starting point.

Intent routing by page type:

```text
"How do I do X?"        -> how-to first
"What is X?"            -> glossary or topic first
"What is changing?"     -> industry-trend first
"Which tool/model?"     -> tool or foundation-model first
"Where did I read this?"-> sources first
"What evidence exists?" -> signals, interview insights, implementation studies, and sources
```

### LLM context flow

An LLM or agent should be able to use indexes as a routing layer before loading full pages.

Expected flow:

```text
user question
        |
        v
wiki/indexes/index.md
        |
        v
tag hub or relevant by-tag index
        |
        v
small set of best entry pages
        |
        v
source pages and evidence objects only when needed
```

The LLM should not need to scan hundreds of full pages just to decide where to look. Indexes should expose enough routing metadata to select context cheaply.

## Tag navigation model

The current `*-by-tag.md` pages are useful, but long tag sections can become hard to use. Stage 2 should add a more deliberate tag navigation layer.

Recommended addition:

```text
wiki/indexes/tags/<tag>.md
```

Each tag hub should be an Obsidian-native index page for one tag.

Suggested tag hub structure:

```text
# <tag>

## Best entry points
- 3 to 8 highest-value pages to read first.

## How-to answers
- Practical pages for "how do I..." questions.

## Concepts and definitions
- Topics and glossary pages.

## Trends and market direction
- Industry trends and signals.

## Tools and models
- Relevant tool and model pages.

## Primary sources
- The most relevant source pages, preferably ranked.

## Evidence objects
- Signals, interview insights, and implementation studies.

## Related tags
- Adjacent tags to continue exploration.

## LLM context recipe
- Suggested read order for an agent building context.
```

The `*-by-tag.md` pages can remain as complete global lists. Tag hubs should be curated routing pages.

## LLM retrieval contract

Generated pages and indexes should make retrieval cheap and predictable.

Each Stage 2 knowledge page should include a compact context card near the top or after the executive synthesis.

Suggested structure:

```text
## Context card

- Use this page when: ...
- Best for questions about: ...
- Not enough for: ...
- Strongest sources: ...
- Related tags: ...
```

For humans this section is optional reading. For an LLM it is a routing hint.

Indexes should expose routing metadata in plain Markdown, not hidden comments. Useful metadata includes:

- category
- source count
- evidence count
- synthesis state
- confidence
- value level
- last synthesized date
- whether the page is candidate, stale, or synthesized

Example index entry:

```text
- [[topics/agentic-coding-workflows|Agentic Coding Workflows]] — synthesized; sources: 8; evidence: 61; confidence: high
```

This is more useful than a bare link when an LLM must choose context quickly.

## Retrieval packet strategy

For common agent use, it may be useful to generate small retrieval packets later.

Possible path:

```text
state/context-packs/<tag>.json
```

or a visible index:

```text
wiki/indexes/context-packs.md
```

A context packet is not a new source of truth. It is a precomputed read list for a tag or question area.

Suggested contents:

- tag
- best entry pages
- top how-to pages
- top synthesis pages
- top source pages
- recent signals
- known contradictions
- suggested read order

This should be optional and generated only after tag hubs are working. It is a convenience layer, not core architecture.

## Obsidian page contract

Final Stage 2 pages should follow Obsidian conventions consistently.

Rules:

- Use YAML properties for stable machine-readable metadata.
- Use wikilinks for internal vault links.
- Use normal Markdown links only for external URLs.
- Prefer concise sections over long evidence dumps.
- Keep headings predictable across categories.
- Preserve backlinks to source pages.
- Avoid embeds for generated pages unless a future use case clearly needs them.
- Use callouts sparingly for status warnings, stale synthesis, or review notes.

Internal links should use Obsidian wikilinks:

```text
[[sources/<source_id>|Source title]]
[[topics/agentic-coding-workflows|Agentic Coding Workflows]]
[[industry-trends/harness-design-becomes-more-important-for-agent-reliability|Agent reliability is shifting toward harness design]]
```

External links should remain standard Markdown:

```text
[Canonical URL](https://example.com/article)
```

Generated pages should not rely on note embeds such as `![[...]]` for core content. Embeds are convenient for human notes, but generated knowledge pages should remain self-contained and robust when rendered, exported, searched, or parsed by an LLM.

## Obsidian properties

Stage 2 knowledge pages should expose synthesis status through properties.

Suggested properties:

```yaml
---
title: Agentic Coding Workflows
slug: agentic-coding-workflows
entity_id: topic:agentic-coding-workflows
category: topic
tags:
  - coding-agents
  - ai-assisted-development
aliases:
  - Agentic Coding Workflow Shape
source_count: 8
evidence_count: 61
synthesis_state: synthesized
synthesis_version: 1
synthesis_prompt_version: 1
synthesis_input_hash: abc123
synthesis_stale: false
last_synthesized_at: 2026-06-16T00:00:00Z
---
```

For stale pages:

```yaml
synthesis_state: stale
synthesis_stale: true
```

And near the top of the page:

```text
> [!warning] Synthesis may be stale
> New or changed evidence exists. The evidence index is current, but the prose synthesis has not been regenerated yet.
```

Do not hide important status only in comments. Obsidian Reading View should make stale or candidate state visible.

## Sources policy

Sources stay visible permanently.

Path:

```text
wiki/sources/<source_id>.md
```

Reasons:

- Sources are the article archive.
- Sources are the provenance anchor for synthesized claims.
- Sources are useful for human review.
- Sources let the LLM return to the original reviewed article summary.

Preferred source page contents:

- accessible overview
- key insights
- derived knowledge pages
- why it matters
- limitations and skepticism
- contradictions or unverified claims
- source evidence profile
- canonical URL
- raw Markdown / HTML paths

The source folder will grow over time. That is acceptable. Growth here is less dangerous than growth in synthetic topic pages, because source pages correspond to real inputs.

Source pages should also remain Obsidian-native.

Suggested properties:

```yaml
---
title: The Orchestration Tax
slug: the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
category: source
source_id: the-orchestration-tax-01ktjzc8r76ht9hhzs4xpejf7y
author: Addy Osmani
publication: X
published_date: 2026-05-28
source_evidence_type: expert_opinion
tags:
  - coding-agents
  - workflow-design
---
```

Source pages should link to derived pages with wikilinks. They should not embed derived pages.

## Knowledge object policy

These categories may receive Stage 2 synthesis:

- topics
- industry trends
- how-to
- tools
- foundation models
- glossary

Default rule:

```text
source_count >= 2 -> eligible for Stage 2 synthesis
source_count == 1 -> thin/candidate page unless manually pinned
```

This prevents the wiki from turning every one-off extraction into a full synthesized page.

Single-source pages can still exist, but they should be visually and semantically marked as thin or candidate pages.

## Evidence object policy

These categories should not receive Stage 2 synthesis as individual pages:

- signals
- interview insights
- implementation studies

They are evidence objects, not synthesized knowledge objects.

Rules:

- Keep them individual.
- Do not merge them.
- Do not synthesize them into compressed pages.
- Improve their templates if needed.
- Let topic and trend pages synthesize across them later.

### Signal template direction

A signal page should make the observation easy to scan.

Suggested structure:

```text
# <Signal title>

## Signal
What was observed?

## Why it matters
Why might this matter?

## Confidence / evidence quality
Evidence type, confidence, time sensitivity.

## Related pages
Topics, trends, tools, models.

## Source
Backlink to the source.
```

### Interview insight template direction

An interview insight should preserve the speaker/context relationship.

Suggested structure:

```text
# <Insight title>

## Claim
What is the central claim?

## Context
Who said it, in what context, and from what perspective?

## Implication
What follows from it?

## Caveat
What limits the claim?

## Related pages
Topics, trends, tools, models.

## Source
Backlink to the source.
```

## Stage 2 page shape

A synthesized knowledge page should start with a compact human review layer.

Suggested structure:

```text
# <Title>

## Executive synthesis
Short readable synthesis from all current evidence.

## What to remember
- 3 to 6 durable takeaways.

## Consensus
- Claims supported by multiple sources.

## Tensions / open questions
- Real disagreements, unclear scope, or unresolved questions.

## Evidence quality
- Strong evidence
- Medium evidence
- Weak evidence

## Practical takeaway
What this means for the user's work.

## Related pages
Curated links.

## Evidence index
- Sources: N
- Evidence items: N
- Last synthesized: date
- Input hash: hash
- Full ledger: state/evidence/...

## Sources
Source backlinks.
```

The long evidence list should not be the main reading experience. It can be omitted, shortened, or moved behind an evidence index, as long as provenance remains reachable.

### Obsidian reading shape

The first screen of a Stage 2 page should answer the human question:

```text
What is this, what should I remember, and how trustworthy is it?
```

Preferred first-screen order:

1. Title
2. Optional stale/candidate callout
3. Executive synthesis
4. What to remember
5. Evidence quality

This makes the page useful in Obsidian Reading View without forcing the reader to scroll through provenance first.

### Candidate page shape

Single-source candidate pages should be visually distinct.

Suggested callout:

```text
> [!note] Candidate page
> This page is based on one source. It is preserved for retrieval and future synthesis, but it should not yet be treated as a stable multi-source wiki page.
```

Suggested property:

```yaml
synthesis_state: candidate
source_count: 1
```

## Incremental synthesis

Stage 2 must not regenerate every page on every wiki render.

Each synthesis cache entry stores an input hash.

Example:

```yaml
synthesis_state: synthesized
synthesis_version: 1
synthesis_prompt_version: 1
synthesis_input_hash: abc123
last_synthesized_at: 2026-06-16T00:00:00Z
synthesis_evidence_ids:
  - evidence-a
  - evidence-b
```

On each run:

```text
compute current synthesis input hash
compare with cached input hash
if same: no LLM call
if different: mark stale or regenerate
```

Only changed entities should trigger LLM calls.

## What changes the synthesis input hash

Include:

- entity ID
- category
- canonical title
- source IDs
- evidence IDs
- evidence text
- evidence field
- stance
- confidence
- value level
- source date
- source evidence profile
- relevant entity-resolution decisions
- synthesis schema version
- synthesis prompt version

Usually exclude:

- generated Markdown formatting
- render timestamps
- non-substantive manifest metadata
- unrelated index changes

This keeps synthesis invalidation tied to meaning, not noise.

## Stage 2 planner states

The Stage 2 planner should classify each eligible entity.

Suggested states:

```text
unchanged
new
stale
skipped_single_source
skipped_evidence_object
skipped_not_pinned
error
```

The planner should be able to run without making API calls.

Suggested command shape:

```text
hatch run wiki-synthesis-plan
```

Potential options:

```text
--category topics
--entity topic:agentic-coding-workflows
--limit 20
--changed-only
--include-single-source
--dry-run
```

## Stage 2 execution controls

To prevent API-call explosions:

- default to changed-only
- support `--limit`
- support exact `--entity`
- skip single-source pages by default
- skip evidence objects always
- store synthesis cache before rendering Markdown
- write a needs-synthesis index instead of forcing all stale pages to regenerate immediately

Suggested command shape:

```text
hatch run wiki-synthesize --changed-only --limit 20
```

## Index policy

Indexes are important because they let humans and LLMs find the right material quickly without exposing every EvidenceItem as an Obsidian page.

Required or high-value indexes:

```text
wiki/indexes/sources-by-tag.md
wiki/indexes/tags/<tag>.md
wiki/indexes/sources-by-month.md
wiki/indexes/sources-by-evidence-type.md
wiki/indexes/topics-by-tag.md
wiki/indexes/trends-by-tag.md
wiki/indexes/how-to-by-tag.md
wiki/indexes/tools-by-tag.md
wiki/indexes/models-by-tag.md
wiki/indexes/glossary-by-tag.md
wiki/indexes/signals-by-tag.md
wiki/indexes/interview-insights-by-tag.md
wiki/indexes/implementation-studies-by-tag.md
wiki/indexes/needs-synthesis.md
wiki/indexes/low-confidence.md
wiki/indexes/contradictions.md
wiki/indexes/entity-resolution-candidates.md
```

Priority:

1. Keep existing indexes working.
2. Add missing evidence-object indexes by tag.
3. Add tag hubs for high-value tags.
4. Add routing metadata to index entries.
5. Add synthesis operational indexes.
6. Add entity-resolution candidate index.

Initial high-value tag hubs should be generated only for tags that are large or strategically important. Do not generate hundreds of tiny tag hubs at first.

Suggested first tags:

```text
ai-engineering
agent-systems
agent-orchestration
knowledge-systems
context-engineering
coding-agents
inference-systems
human-ai-workflows
support-automation
```

This keeps the system useful without creating another page explosion.

## Entity resolution policy

Do not let the LLM automatically merge entities.

Rule:

```text
Entity resolution is advisory first, deterministic after approval.
```

The system may suggest possible duplicates or parent-child relationships, but only approved mappings should affect rendering.

Possible decisions:

```text
keep_separate
alias
parent_child
merge
```

Suggested config path:

```text
config/entity_resolution.yaml
```

Example:

```yaml
aliases:
  topic:agentic-coding-workflow-shape: topic:agentic-coding-workflows

parent_child:
  topic:agentic-workflows:
    - topic:agentic-coding-workflows
    - topic:agent-workflow-vs-workflow-orchestration

keep_separate:
  - [topic:agent-memory, topic:agent-memory-architecture]
```

The renderer should apply this file deterministically.

The LLM may help produce candidates, but it should not silently alter canonical mappings.

## Entity-resolution candidates

Candidate detection should start with cheap heuristics:

- similar slugs
- similar titles
- overlapping tags
- overlapping source IDs
- overlapping related pages
- same primary tag

Optional later:

- LLM explanation for why candidates may or may not belong together

Candidate output path:

```text
wiki/indexes/entity-resolution-candidates.md
```

This is review infrastructure, not an automatic merge system.

## Closed decisions

These decisions are settled for the first implementation pass.

1. Keep `state/reviews/*/review.json` as canonical source of truth.
2. Keep Stage 1 as the complete evidence layer.
3. Do not make Stage 1 evidence dumps the main Obsidian experience.
4. Keep source pages visible in Obsidian permanently.
5. Stage 2 synthesis applies to knowledge objects, not evidence objects.
6. Signals, interview insights, and implementation studies remain individual pages.
7. Use input hashes to avoid unnecessary LLM calls.
8. Store Stage 2 synthesis in a cache under `state/synthesis/`.
9. Render Obsidian pages from synthesis cache plus evidence metadata.
10. Skip single-source synthesis by default.
11. Add operational indexes for synthesis and entity resolution.
12. Use advisory entity-resolution candidates first.
13. Apply only deterministic, approved entity-resolution decisions.
14. Optimize navigation for two access patterns: human tag-based question answering and LLM index-based context selection.
15. Add tag hubs for important tags before considering more complex retrieval infrastructure.

## Open decisions

These can be decided during implementation.

### Should Stage 1 be sharded immediately?

Default answer: no.

Start from `state/wiki_render_graph.json` because it already exists. Add `state/evidence/` later if the graph file becomes too large or too awkward for Stage 2 prompts.

### Should Stage 1 generated knowledge pages remain in Obsidian?

Default answer: temporarily yes.

For the first implementation, avoid a disruptive migration. Add Stage 2 fields/pages gradually. Later, decide whether long evidence sections should be shortened or moved out of visible Markdown.

### Should stale pages render old synthesis or Stage 1 fallback?

Default answer: render old synthesis with a stale marker.

This avoids degrading the user experience while making stale state visible.

### Should synthesis run automatically after wiki-render?

Default answer: no.

Keep `wiki-render` deterministic and cheap. Run Stage 2 as a separate command with limits.

### Should source pages be synthesized further?

Default answer: no.

Source pages already summarize individual articles well. Improve source templates only if a concrete problem appears.

### Should every tag get its own tag hub?

Default answer: no.

Start with high-value tags only. Keep global `*-by-tag.md` indexes as complete coverage. Add more tag hubs when a tag becomes large enough or important enough to need routing help.

### Should context packets be implemented immediately?

Default answer: no.

First make tag hubs and richer index entries work. Context packets are useful later if agents repeatedly need the same bundles of context.

## Implementation phases

### Phase 0: documentation and guardrails

Deliverables:

- this architecture note
- update `wiki/AGENTS.md` with a short Stage 2 pointer later
- update `src/AGENTS.md` after commands exist

No behavior changes.

### Phase 1: Stage 2 data model and planner

Deliverables:

- `src/wiki_synthesis/` package
- synthesis cache model
- input hash computation
- planner that classifies entities as new, unchanged, stale, or skipped
- tests for hash stability and skip rules

No LLM calls yet.

### Phase 2: operational indexes

Deliverables:

- `needs-synthesis.md`
- `sources-by-evidence-type.md`
- missing tag indexes for signals and interview insights if absent
- high-value tag hubs under `wiki/indexes/tags/`
- richer index entries with source count, evidence count, synthesis state, and confidence where available
- entity-resolution candidate index based on heuristics

Still no automatic synthesis required.

### Phase 3: synthesis prompt and cache writer

Deliverables:

- provider interface for synthesis calls
- prompt template
- exact JSON output schema
- `wiki-synthesize --dry-run`
- `wiki-synthesize --changed-only --limit N`
- tests with fake provider

LLM calls only when explicitly invoked.

### Phase 4: Stage 2 Markdown rendering

Deliverables:

- render synthesized knowledge pages from cache
- frontmatter includes synthesis metadata
- stale marker when cache hash does not match current input
- evidence index section
- no loss of source backlinks

### Phase 5: conservative entity resolution

Deliverables:

- `config/entity_resolution.yaml`
- deterministic application of approved aliases / parent-child / keep-separate / merge
- candidate index remains advisory
- tests proving no unapproved merge occurs

This phase should happen after Stage 2 is already useful.

## Success criteria

The implementation is successful when:

- adding one new source does not resynthesize unrelated pages
- changed pages are detectable before spending API calls
- source pages remain readable and linked
- signals and interview insights remain individual evidence pages
- synthesized topic/trend/how-to pages are understandable in under one minute
- every synthesized claim can still be traced back to sources
- entity merge decisions are visible and reversible
- Obsidian search is not dominated by machine evidence dumps

## Non-goals for the first pass

- no fully automatic ontology merging
- no automatic rewrite of every generated wiki page
- no vector database requirement
- no hidden LLM memory for entity decisions
- no summary-of-summaries update loop
- no mandatory synthesis for every single-source page
