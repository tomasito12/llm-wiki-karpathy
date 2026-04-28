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

## Required Quality Checks

Run these after substantive code changes:

1. `hatch run lint:check`
2. `hatch run lint:format`
3. `hatch run test:run`
4. `hatch run test:cov`

## Pre-commit Alignment

- Ensure code quality rules enforced by pre-commit match Hatch lint/type commands.
- Prefer changing config in one place (`pyproject.toml`) and reusing it from hooks.

## Safety

- Do not modify `raw/` source documents.
- Avoid touching wiki data unless the user explicitly requests a mixed workflow.
