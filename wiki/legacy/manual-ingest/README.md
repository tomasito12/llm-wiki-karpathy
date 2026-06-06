# Manual Ingest (Historical)

These documents describe the **legacy manual-ingest workflow** used before `wiki-render`.

They are **not** contracts for the generated Obsidian knowledge layer. For the current architecture, see [../AGENTS.md](../AGENTS.md).

## Contents

- `stage1-classifier.md` — legacy Stage 1 routing rules
- `stage2-artifact-router.md` — legacy Stage 2 artifact routing
- `ingest-templates.md` — legacy ingest templates

Current workflow:

```text
raw/readwise → ingest review dashboard → state/reviews/* → wiki-render → wiki/
```
