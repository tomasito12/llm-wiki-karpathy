# Intent Routing Rubric

This document defines how to route chat requests without requiring user prefixes.

## Intent Classes

- `wiki_ops`: ingest/query/lint/wiki content tasks
- `code_ops`: implement/refactor/test/tooling/CLI tasks
- `mixed_ops`: both wiki and code changes in one request
- `unknown_ops`: insufficient signal to route safely

## Signals

### Strong `wiki_ops` signals

- "ingest", "query the wiki", "lint the wiki"
- "update glossary/index/overview/log"
- mentions of `wiki/` and knowledge curation

### Strong `code_ops` signals

- "implement", "refactor", "write tests", "fix lint/type"
- mentions of `pyproject.toml`, `src/`, CLI commands, automation scripts

### `mixed_ops` signals

- requests that explicitly combine code creation and wiki maintenance
- requests to both implement logic and file outcomes into wiki pages

## Decision Policy

1. If one class clearly dominates, route directly.
2. If two classes are close, classify as `mixed_ops`.
3. If confidence is low, classify as `unknown_ops`.
4. For `mixed_ops` and `unknown_ops`, ask one clarifying question before edits.

## Clarifier Templates

- "Do you want wiki maintenance, code changes, or both?"
- "Should I only plan this, or also implement it now?"
- "If both, should I do code first and wiki updates second?"

## Fail-Closed Rule

When intent is ambiguous, do not perform write actions until user clarifies.

## Dry-Run Scenarios

1. "Ingest raw/article.md" -> `wiki_ops`
2. "Add hatch command for analyze and tests" -> `code_ops`
3. "Build crawler and summarize findings into wiki pages" -> `mixed_ops` (requires sequencing confirmation)
4. "Can you improve this setup?" -> `unknown_ops` (requires clarifier)
