# Management Web Review Feedback — 2026-07-17

Status: implemented 2026-07-17 (F2–F4)  
Source: live feedback on Review page (+ clarification round)  
Rule for implementers: **mirror Streamlit behavior; do not invent new review
functionality without asking the user.**

---

## Working principles from this feedback round

1. Orient the review UI on the existing Streamlit dashboard.
2. Do not invent review fields, tagging rules, or edit flows that Streamlit does
   not already use for that entity type.
3. Only show tags where tagging actually makes sense for that entity.
4. Capture open questions for the user when Streamlit and product intent are
   unclear; do not invent a new policy unilaterally.
5. Prefer actionable review surfaces over read-only info dumps.

---

## Feedback items

### F1 — Suggested Destinations / Mentioned Entities

**User ask (initial)**

- What are they? Where from? Needed downstream? If not, remove.

**Clarified decision (2026-07-17)**

| Field | Decision |
|---|---|
| **Suggested destinations** | Do **not** keep as primary/read-only review info. Just showing them is useless. Optionally later: action under Edit to move/promote into another entity. Do **not** invent that promote-flow in this fix unless explicitly requested as a scoped slice. |
| **Mentioned entities** | Keep in the **data model** (good for future search / Schlagwortsuche). Do **not** require reviewing them. Safe extraction; can stay out of the primary review UI. |

**Current investigation notes**

- Produced by LLM pre-analysis for signals / interview insights.
- Streamlit shows them as collapsed secondary fields.
- Wiki render still collects them.
- Management web currently elevates them into normal detail lists.

**Implementation guidance**

- Remove from primary review card UI for signals / interview insights.
- Keep storing them in artifacts (especially `mentioned_entities`).
- Keep them in artifact JSON **and** wiki render output.
- Do **not** delete from schema/render in this slice.
- Promote-to-entity action = future optional feature, not default invent.

**Acceptance**

- Primary Review UI no longer presents Suggested Destinations / Mentioned
  Entities as mandatory review information.
- Data remains available in artifacts and render for later use.

---

### F2 — Tag selection in Edit is broken / incomplete

**User ask**

- Edit tag selection broken; only a subset of allowlist tags appears.
- Full configured allowlist for that entity must be selectable.

**Clarified decision**

- Tag dropdown should expose the **full allowlist** (browsable, not truncated).

**Current investigation notes**

- `web/management/src/TagPicker.tsx` hard-limits options with `.slice(0, 12)`.
- Also verify API returns the full entity-specific allowlist.

**Acceptance**

- Full allowlist for the active entity type is selectable in Edit.
- No silent truncation to 12 (or any small cap).
- Selected tags persist after save.

---

### F3 — Tagging policy / signal tags

**User ask**

- Signals having tags was confusing.
- Mirror Streamlit; only tag where it makes sense.
- Do not invent new tagging.

**Clarified decision**

- If Streamlit tags signals → **keep signal tags**.
- Clarify how tags are formed: allowlist vs free LLM invention.

**Investigation: how signal tags are formed**

1. LLM proposes tags for signals.
2. Prompt instructs: copy **exact allowlist strings** into `proposed_tags`; use
   `suggested_new_tags` only when no close allowlist match exists.
3. Post-validation in `analyze.py` demotes off-list tags into
   `suggested_new_tags`.
4. For signals, the allowlist is the **trend tag allowlist**
   (`config/review_tags_trends.yaml`), same vocabulary Streamlit uses.

So tags are **not meant to be free-form**. They should be constrained by the
trend allowlist. If they look “made up” in the UI, likely causes are:

- off-list LLM suggestions surfaced as new tags,
- wrong/empty allowlist wiring in management web,
- TagPicker truncation hiding most allowlist options (F2),
- or reviewer seeing `suggested_new_tags` mixed with allowlist tags.

**Acceptance**

- Signal tagging remains, Streamlit-aligned.
- Management web uses the same trend allowlist for signals.
- Tag options look structured (allowlist-backed), not freely invented.

---

### F4 — Residual extraction should be inspectable (new)

**User ask**

- More interesting than destinations: residual / non-entity extraction that is
  currently not shown.
- Example: limitations and similar source-summary chapters.
- Should **not** be in the primary visible review area.
- Should be available on demand if the user wants to inspect what was extracted.

**Clarified decision (2026-07-17)**

- On-demand panel should expose the **entire Source Summary**, not only
  limitations / contradictions.

**Investigation notes**

- Source summary schema includes chapters such as:
  - `limitations_and_open_questions`
  - `contradictions_and_skepticism`
  - plus other `source_summary` fields
- Management web Review UI currently does not surface these well
  (`App.tsx` has no `source_summary` / limitations usage found).

**Implementation guidance**

- Add an optional/secondary inspect surface (collapsed panel, details drawer,
  or “show extraction leftovers”).
- Show the full Source Summary on demand.
- Do not put this in the main entity-review path.
- Prefer Streamlit-equivalent source-summary review patterns if they already
  exist; do not invent a new ontology.

**Acceptance**

- User can open the full Source Summary on demand.
- Primary review flow stays focused on actionable entity review.

---

### F5 — Future idea: promote Suggested Destinations into entities (parked)

**User ask**

- Showing destinations alone is useless.
- Potentially useful later: Edit action to move a destination into another
  entity.

**Status**

- Parked. Do not implement unless explicitly scoped.
- Mentioned entities remain stored for future search.

---

## Implementation notes (2026-07-17)

Completed in this slice:

1. **F2** — removed TagPicker `.slice(0, 12)`; full allowlist is browsable/scrollable.
2. **F3** — `/api/review/tags?group=...` returns Streamlit-aligned allowlists
   (signals → trend tags, interview insights → topic tags, etc.).
3. **F1** — Suggested Destinations / Mentioned Entities removed from primary
   signal/insight detail lists; still stored in artifacts and render.
4. **F4** — Easy Read card now has an on-demand **Full source summary** panel
   with all source-summary chapters.

Still parked: **F5** destination→entity promote flow.

---

## Suggested implementation order

1. **F2** — remove TagPicker truncation; ensure full allowlist. ✅
2. **F3** — verify signal/entity tag allowlists match Streamlit wiring. ✅
3. **F1** — remove Suggested Destinations / Mentioned Entities from primary
   review UI; keep data stored. ✅
4. **F4** — add on-demand residual extraction inspect (source summary leftovers). ✅
5. **F5** — only if requested later (promote destinations).

---

## Resolved questions

1. Suggested Destinations: not useful as read-only display → hide from primary
   UI. Optional later: promote-to-entity. Keep in artifact JSON and wiki render.
2. Mentioned Entities: keep stored for future search; not required in primary
   review UI. Keep in artifact JSON and wiki render.
3. Signals: keep tags if Streamlit has them; allowlist is trend tags.
4. Tag dropdown: full allowlist, browsable, no truncation.
5. F4 residual panel: full Source Summary on demand.
6. F1 render policy: remove from Review UI only; leave JSON + render unchanged.

---

## Do-not-do list for implementers

- Do not invent new review fields.
- Do not invent new tagging rules for entity types Streamlit does not support.
- Do not delete schema/render fields without confirming product intent.
- Do not build destination→entity promote flow unless explicitly asked.
- Do not put residual extraction into the primary review surface.
- Do not “improve” review UX by inventing a Streamlit-incompatible model.
