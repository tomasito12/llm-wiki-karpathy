# Management Web Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe Readwise sync and bounded pre-analysis controls to a focused Intake & Analysis stage inside Pipeline.

**Architecture:** Extend the existing allowlisted operation runner with two CLI-backed operations and reuse its confirmation, concurrency, polling, and reporting contracts. Refactor Pipeline presentation into three local stages while leaving Review untouched.

**Tech Stack:** Python 3.12, FastAPI, React 19, TypeScript, Vitest, pytest

## Global Constraints

- Keep global navigation as `Review | Pipeline`.
- Default Pipeline stage is `Intake & Analysis`.
- Readwise sync uses normal automatic dedupe and requires confirmation.
- Pre-analysis defaults to 10 documents and 300 seconds between articles.
- Only one management run may execute at a time.
- Do not expose tokens or add new ingestion algorithms.

---

### Task 1: Add allowlisted ingestion operations

**Files:**
- Modify: `src/management_web/ops.py`
- Test: `tests/management_web/test_ops.py`

- [ ] Add failing tests for `readwise_sync` and `ingest_preanalyze` definitions, defaults, validation, and exact module commands.
- [ ] Run the focused tests and confirm the new expectations fail.
- [ ] Add the two operation builders and definitions with confirmation metadata.
- [ ] Add bounded seconds validation without weakening existing parameter validation.
- [ ] Run focused backend tests and commit the passing change.

### Task 2: Add focused Pipeline stage UI

**Files:**
- Modify: `web/management/src/PipelineCockpit.tsx`
- Modify: `web/management/src/styles.css`
- Test: `web/management/src/PipelineCockpit.test.tsx`

- [ ] Add failing tests for the three stages and the default Intake view.
- [ ] Add failing tests for sync/pre-analysis defaults, confirmation copy, and operation payloads.
- [ ] Run focused Vitest tests and confirm the expectations fail.
- [ ] Implement stage navigation and place existing Update Wiki and advanced operations in their assigned stages.
- [ ] Add concise Intake cards using the existing operation metadata and run feedback.
- [ ] Run focused frontend tests and commit the passing change.

### Task 3: Improve ingestion result summaries and integration coverage

**Files:**
- Modify: `web/management/src/PipelineCockpit.tsx`
- Test: `web/management/src/PipelineCockpit.test.tsx`
- Test: `web/management/src/App.test.tsx`

- [ ] Add failing tests for readable Readwise and pre-analysis result summaries and shared busy-state behavior.
- [ ] Implement only the parsing and labels required by those outputs.
- [ ] Run frontend tests, lint, and build.
- [ ] Run Python lint and the complete Python test suite.
- [ ] Verify the worktree is clean except for intentional commits.
