# Tool Kind + Traits Review UX

Date: 2026-07-22  
Status: approved for planning  
Scope: management web review UI — **tools only**

## Problem

Tool entity cards show two unlabeled chip rows. Reviewers cannot tell which row is the product archetype (`proposed_types`) and which is retrieval traits (`proposed_tags`). Only traits are editable; kinds are display-only. That blocks fast correction when the LLM misclassifies a tool (e.g. Ollama as `ai-infrastructure` without a usable form-factor kind).

## Decision

Keep the existing two-layer data model. Make it **explicit and editable** in the management web UI for tools:

| UI label | Backend field | Allowlist |
|----------|---------------|-----------|
| **Tool kind** | `proposed_types` / review `types.approved_types` | `config/review_tool_types.yaml` |
| **Traits** | `proposed_tags` / review `tags.final_tags` | `config/review_tags_tools.yaml` |

Models and other entity groups are out of scope for this slice.

## Non-goals

- Collapsing kinds and traits into one list
- Renaming or cleaning the tool-types ontology (form-factor vs domain mix)
- Editing kinds for foundation models
- Auto-appending new kinds/traits into YAML allowlist files
- Changing wiki render output beyond reading already-supported `reviewed_types()` / `reviewed_tags()`

## UI

### Read card (tools)

1. **Tool kind** chip row (with short helper: “What kind of product?”)
2. Title
3. Description
4. **Traits** chip row (with short helper: “How it’s used or deployed”)
5. Existing full-extraction details

Empty rows stay hidden (no empty labeled section).

Other entity groups keep today’s single unlabeled tag cloud (and type chips if present, still read-only).

### Edit card (tools)

Two pickers reusing `TagPicker` with distinct labels:

- **Tool kind** — options from types allowlist API
- **Traits** — options from existing tags allowlist API

Creating a value not on the allowlist remains allowed (same chip UX as today’s tags). New values are stored on the entity; they are **not** automatically written into the YAML registries in this slice.

Save enables when title, description, kinds, or traits change.

## API

### `GET /api/review/types?group=tools`

- Returns the same shape as tag choices (`name`, `usage_count`).
- Allowlist: `load_tool_types`.
- Usage counts: count occurrences of reviewed/display types across tool entities in existing reviews (mirror tag registry behavior where practical).
- Non-`tools` group → `400`.

### `GET /api/review/tags?group=tools`

Unchanged (traits allowlist).

### `PATCH` entity edit

Extend `EntityEditRequest` with:

```text
types: list[str] | None = None
```

Rules:

- `types` only accepted when `group == "tools"`; otherwise `400`.
- Normalize like tags: trim, reject empties, dedupe preserving order.
- Persist to review tree: `review_node["types"]["approved_types"] = normalized`.
- Mirror to `llm_output` tool item: `proposed_types = normalized`; clear sibling type keys (`proposed_new_type`) when mirroring, analogous to tag mirroring.
- `tags` path unchanged (`final_tags` + `proposed_tags`).

## Frontend wiring

- Load types allowlist when editing a tools entity (or when tools group is visible).
- Entity draft includes `types` and `newTypeNames` parallel to tags.
- Edit payload sends `types` when changed.
- Card labels use **Tool kind** / **Traits**, not “types” / “tags” jargon.

## Testing

Backend:

- Types registry endpoint for `group=tools`
- Reject types endpoint / edit types for non-tool groups
- Tool entity edit persists `approved_types` and mirrored `proposed_types`
- Empty / duplicate type values rejected

Frontend:

- Tool card shows labeled kind + traits rows
- Edit mode exposes two pickers; save sends both fields
- Non-tool entities do not show the dual-picker editor

## Success criteria

A reviewer looking at a tool like Ollama can:

1. See that `ai-infrastructure` is a **Tool kind** and `local-first` is a **Trait**
2. Edit either field without leaving the management web app
3. Save and reload the card with the corrected values
