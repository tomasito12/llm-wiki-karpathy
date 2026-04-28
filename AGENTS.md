# LLM Wiki — Schema for AI Expert

This file is your operating manual. Read it at the start of every session. It defines the wiki structure, entity types, workflows, and conventions you must follow.

---

## Intent Router (Root Policy)

This root file routes requests between two domains:

- `wiki_ops`: ingest/query/lint and wiki maintenance tasks
- `code_ops`: Python/tooling/CLI/software-development tasks

Classification states:

- `wiki_ops`
- `code_ops`
- `mixed_ops`
- `unknown_ops`

Routing behavior:

1. Classify intent first.
2. If confidence is high, follow scoped rules for that domain.
3. If `mixed_ops` or `unknown_ops`, ask one focused clarification before edits.
4. Fail-closed on ambiguity: do not perform write actions until clarified.

Scoped instruction files:

- `wiki/AGENTS.md` for wiki workflows
- `src/AGENTS.md` for code-development workflows

Canonicality note:

- Treat scoped files as the canonical source of detailed behavior.
- Keep this root file focused on routing and cross-domain safety.

Conflict handling:

1. Scoped instructions override root notes inside their path scope.
2. Mixed tasks require explicit user-confirmed sequencing.
3. Default mixed sequence: code phase first, wiki update/logging phase second.

---

Root file ends here intentionally. Detailed wiki rules live in `wiki/AGENTS.md`; detailed code rules live in `src/AGENTS.md`.
