# Tool Kind + Traits Review UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make tool cards show labeled, editable **Tool kind** and **Traits** in the management web review UI.

**Architecture:** Extend entity edit API with optional `types` (tools only), add `GET /api/review/types?group=tools`, and update the React entity card/editor to use two labeled `TagPicker`s. Persist kinds via `types.approved_types` + mirrored `proposed_types`.

**Tech Stack:** FastAPI/Pydantic backend, React + Vitest frontend, existing `TagPicker` and review-tree accessors.

**Spec:** `docs/superpowers/specs/2026-07-22-tool-kind-traits-review-ux-design.md`

## Global Constraints

- Tools only; models and other groups unchanged for kind editing.
- UI labels: **Tool kind** / **Traits** (not “types” / “tags”).
- Do not auto-write new values into YAML allowlists.
- Empty chip rows stay hidden.

## File map

| File | Responsibility |
|------|----------------|
| `src/management_web/models.py` | `EntityEditRequest.types` |
| `src/management_web/review_data.py` | Types registry + persist types on edit |
| `src/management_web/api.py` | `GET /api/review/types` |
| `tests/management_web/test_review_data.py` | Persist + registry tests |
| `tests/management_web/test_api.py` | Types endpoint tests |
| `web/management/src/types.ts` | Request/response types |
| `web/management/src/api.ts` | `fetchReviewTypes` |
| `web/management/src/TagPicker.tsx` | Configurable label |
| `web/management/src/App.tsx` | Dual pickers + labeled read view |
| `web/management/src/styles.css` | Kind/traits section styles |
| Frontend tests under `web/management/src/` | Card/editor behavior |

---

### Task 1: Backend — persist tool kinds on entity edit

**Files:**
- Modify: `src/management_web/models.py`
- Modify: `src/management_web/review_data.py`
- Test: `tests/management_web/test_review_data.py`

- [ ] **Step 1: Write failing tests** for tools types edit, empty rejection, non-tools rejection
- [ ] **Step 2: Run tests — expect fail**
- [ ] **Step 3: Add `types` to `EntityEditRequest`; persist `approved_types` + mirror `proposed_types`; reject non-tools**
- [ ] **Step 4: Run tests — expect pass**
- [ ] **Step 5: Commit**

### Task 2: Backend — types allowlist endpoint

**Files:**
- Modify: `src/management_web/review_data.py`
- Modify: `src/management_web/api.py`
- Test: `tests/management_web/test_review_data.py`, `tests/management_web/test_api.py`

- [ ] **Step 1: Write failing tests** for `build_review_type_registry(group="tools")` and API 400 for other groups
- [ ] **Step 2: Implement registry + `GET /api/review/types`**
- [ ] **Step 3: Run tests — expect pass**
- [ ] **Step 4: Commit**

### Task 3: Frontend — labeled dual pickers for tools

**Files:**
- Modify: `web/management/src/{types,api,TagPicker,App,styles}.tsx/css`
- Test: existing App/TagPicker tests + new cases

- [ ] **Step 1: Make `TagPicker` accept `label` + `helperText`**
- [ ] **Step 2: Wire types fetch, draft `types`, payload, read/edit UI for tools only**
- [ ] **Step 3: Run frontend tests**
- [ ] **Step 4: Commit**

### Task 4: Verification

- [ ] Run backend management_web tests + frontend vitest
- [ ] Confirm success criteria from spec
