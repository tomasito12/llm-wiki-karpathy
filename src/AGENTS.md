# Code Operations Rules

Use this file for `code_ops` requests only.

## Scope

Applies when the task is about:

- implementing or refactoring Python code
- adding CLI commands and automation
- updating tests and tooling (`hatch`, `ruff`, `ty`, `pre-commit`)
- improving code architecture or reliability

## Standards

- Keep changes minimal and scoped to the request.
- Add or update tests with code changes.
- Prefer clear function boundaries over large scripts.
- Use existing tooling configuration from `pyproject.toml`.
- Don’t assume. Don’t hide confusion. Surface tradeoffs.
- Minimum code that solves the problem. Nothing speculative.
- Touch only what you must. Clean up only your own mess.
- Define success criteria. Loop until verified.

## Testing Standards

- Every function must have at least one unit test.
- Prefer tests that use real objects and real logic flows; avoid mocking unless there is a clear need (for example: external APIs, non-deterministic systems, or expensive dependencies).
- Tests should be easy to read and self-explanatory.
- Aim for high coverage, including edge cases and error paths.
- Include explicit edge-case tests where relevant (for example: empty inputs, boundary values, malformed inputs, and failure behavior).

## Function Quality Standards

- Every function must have a docstring.
- Every function must have type hints on parameters and return values.

## Performance and Readability

- Write code that is both performant and understandable.
- If performance is not critical for the code path, prefer readability and maintainability over micro-optimizations.

## Required Quality Checks

Run these after substantive code changes:

1. `hatch run lint:check`
2. `hatch run lint:format`
3. `hatch run test:run`
4. `hatch run test:cov`

## Pre-commit Alignment

- Ensure code quality rules enforced by pre-commit match Hatch lint/type commands.
- Prefer changing config in one place (`pyproject.toml`) and reusing it from hooks.

## Readwise Reader export

- Set `READWISE_TOKEN` (or `READWISE_API_TOKEN`) from [readwise.io/access_token](https://readwise.io/access_token), or put it in a repo-root `.env` file (loaded automatically; does not override existing shell variables).
- Run: `hatch run readwise-sync` (optional: `--dry-run`, `--prune-missing`, `--reset-watermark`, `--output-dir`, `--index`).
- Each run passes Readwise **`updatedAfter`**: either `last_updated_after` from `state/readwise_library.json`, or on the **first run** (no watermark yet) a timestamp **~100 days** in the past so the initial sync still uses a bounded window.
- Exports Reader **Library Archive** documents tagged **processed** to `raw/readwise/` as paired `.html` + `.md`, with dedupe in `state/readwise_library.json`.

## Safety

- Do not modify `raw/` source documents (except via the explicit Readwise export command above).
- Avoid touching wiki data unless the user explicitly requests a mixed workflow.
