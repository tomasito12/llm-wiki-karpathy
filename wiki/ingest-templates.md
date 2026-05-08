---
title: Ingest markdown templates
type: style
created: 2026-05-02
updated: 2026-05-06
sources: []
tags: []
---

Use these templates during ingest. Contract is defined in `wiki/AGENTS.md`. For **tools-overview** ingests, use the tools source and tool-page templates at the end of this file; do not use `## Questions addressed by the text`. After Stage 1 says tools-overview, run **Stage 2** per `wiki/stage2-artifact-router.md` before placing wikilinks into coverage sections.

## Stage 1 classifier output (working notes only)

```markdown
## Stage 1 verdict

- Industry radar digest: Yes | No
- Primary subject is named software tool(s) (incl. single-product review): Yes | No (only if radar = No)
- Rationale: ...
- Branch: radar (defer) | tools-overview (source + `wiki/tools` / `wiki/foundation-models` per Stage 2, no questions) | non-radar questions/source/glossary
```

Do **not** paste this classifier block into final source pages.

## Stage 2 artifact router output (working notes only)

```markdown
## Stage 2 routing

- <Artifact name> → foundation-model | app | MCP | skipped
- ...
- Notes: ...
```

Do **not** paste this block into final source pages.

## Glossary index — `wiki/glossary/index.md`

```markdown
---
title: Glossary
type: glossary
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

| Term | Page |
|------|------|
| Retrieval Augmented Generation | [[glossary/terms/retrieval-augmented-generation]] |
```

## Glossary term page — `wiki/glossary/terms/<slug>.md`

```markdown
---
title: Retrieval Augmented Generation
type: glossary-term
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - ai-engineering
---

## Definition

...

## Usage Notes

...

## Disagreements

None.

## Sources

- [[source-slug]]
```

## Questions catalog — `wiki/questions/question-catalog.md`

```markdown
---
title: Questions catalog
type: questions-catalog
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## ai-engineering

- [[q-which-elements-underpin-production-ai-systems]]
- [[q-why-is-context-engineering-important-for-ai-systems]]
```

## Question page — `wiki/questions/q-<slug>.md`

```markdown
---
title: Which elements underpin production AI systems?
type: question
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - ai-engineering
---

## Synthesized answer

...

## Sources

- [[source-slug]]
```

## Source page — `wiki/sources/<raw-basename>.md`

```markdown
---
title: <Source title>
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - raw/readwise/<basename>.md
  - raw/readwise/<basename>.html
tags:
  - ai-engineering
---

Tutorial-style primer arguing that conceptual literacy makes production failures diagnosable ...

## Questions addressed by the text

### What concepts underpin production AI systems?

Linked question page: [[q-which-elements-underpin-production-ai-systems]]

Answer grounded in this source ...

### Why is context engineering important for AI systems?

Linked question page: [[q-why-is-context-engineering-important-for-ai-systems]]

Answer grounded in this source ...

## Why it matters

...

## Implications for service-call automation

... (omit section if no real implications)

## Context and Limitations

...

## Contradictions / Unverified Claims

...

## Sources

- [[source-slug]]
```

## Post-ingest QA checklist

- [ ] Source page section order matches contract (standard vs tools overview).
- [ ] No process instructions in content pages.
- [ ] Question headings are readable natural language.
- [ ] Question page has no aliases and has `## Sources` bullets.
- [ ] Glossary term pages use exact fixed headings.
- [ ] Only allowed tags used.
- [ ] No unintended tag-hub folders/pages created.
- [ ] Tools-overview sources: tag `tools`, no `## Questions addressed by the text`, split coverage sections per contract **6)**; tools + foundation-models index parity as applicable.

## Tools-overview source page — `wiki/sources/<raw-basename>.md`

```markdown
---
title: <Source title>
type: source
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - raw/readwise/<basename>.md
  - raw/readwise/<basename>.html
tags:
  - tools
---

One-paragraph summary of the tool-focused source (listicle, single-product review, or comparison framed around named products) (no heading).

Omit any coverage section below that has **zero** bullets; keep the **Apps → Foundation models → MCP servers** order for sections you keep.

## Apps and platforms covered

- [[tools/<category>/<tool-slug>]]

## Foundation models covered

- [[foundation-models/<model-slug>]]

## MCP servers covered

- [[tools/mcp-servers/<slug>]]

## Why it matters

...

## Implications for service-call automation

... (omit section if no real implications)

## Context and Limitations

...

## Contradictions / Unverified Claims

...

## Sources

- [Original article](https://...)
```

## Tool page — `wiki/tools/<category>/<slug>.md`

```markdown
---
title: <Tool display name>
type: tool
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - tools
---

## What problem does this tool solve?

...

## Properties

- ...

## Author assessments

- ... [[sources/<raw-basename-without-path-or-extension>]]

## Sources

- [[sources/<raw-basename-without-path-or-extension>]]
```

## Tool category index — `wiki/tools/<category>/index.md`

```markdown
---
title: <Category display name>
type: tools-category-index
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

| Tool | Page |
|------|------|
| Firecrawl | [[tools/mcp-servers/firecrawl]] |
```

## Tools master index — `wiki/tools/index.md`

```markdown
---
title: Tools
type: tools-index
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

| Category | Page |
|----------|------|
| MCP servers | [[tools/mcp-servers/index]] |
```

## Foundation models index — `wiki/foundation-models/index.md`

```markdown
---
title: Foundation models
type: foundation-models-index
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

| Model | Page |
|-------|------|
| Example Model | [[foundation-models/example-model]] |
```

## Foundation model page — `wiki/foundation-models/<slug>.md`

```markdown
---
title: <Model display name>
type: foundation-model
created: YYYY-MM-DD
updated: YYYY-MM-DD
vendor: <Vendor>
homepage: https://...
open_weights: yes | no | partial | unknown
tags:
  - models
---

## Summary

...

## Technical snapshot

- ...

## Access and licensing

...

## Evaluation claims

- **Vendor-claimed:** ...

## Limitations and risks

Not covered in current sources.

## Timeline

### YYYY-MM-DD

- Factual bullet(s).

**Source:** [[sources/<raw-basename>]]

## Commentary

- Opinion bullet ... [[sources/<raw-basename>]]

## Sources

- [[sources/<raw-basename>]]
```
