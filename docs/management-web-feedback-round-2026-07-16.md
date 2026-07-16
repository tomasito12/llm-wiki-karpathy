# Management Web Feedback Round

Date: 2026-07-16
Scope: current write-enabled management web review workspace

## Short Verdict

The management web app has crossed an important threshold: it is no longer only
a prototype for looking at artifacts. It now has the core shape of a real review
workspace:

- queue filtering
- article-level decisions
- finish review workflow
- full entity group visibility
- entity editing
- hide/unhide support
- raw source and debug access

That is a strong foundation. The main problem is now different: the UI exposes
too much operational complexity at once. It works, but it still asks the user to
think like the system.

The next product step should be a focused UX/design pass for fast article
review. The goal is not to make the app decorative. The goal is to make it feel
like a calm cockpit for quickly deciding whether a pre-analysis is good enough.

## What Works Well

### The Main Workflow Is Finally Visible

The app now shows the real work:

1. pick an article from the queue
2. read the Easy Read
3. inspect tags and extracted entities
4. edit or hide entities if needed
5. finish or mark the article

This is the right product direction. It matches the actual mental model better
than the old Streamlit dashboard.

### The Queue Defaults Are Directionally Correct

Defaulting to `Ready for review` and `Not reviewed` is good. It keeps the user
focused on the next actionable batch instead of mixing finished, pending, and
skipped material.

The queue also now sorts older articles first, which supports the backlog
cleanup goal.

### Easy Read Is The Right First Reading Surface

Using Easy Read as the primary article summary is correct. It is much more
reviewable than raw JSON and much less tiring than forcing the user into the
full source text immediately.

Key insights being collapsed by default is also correct.

### Entity Coverage Is A Big Product Improvement

Showing all entity groups matters. The user can now approve an article without
wondering whether invisible tools, models, how-tos, signals, or interview
insights are hiding somewhere.

The split between `Wiki entities` and `Source-specific insights` is also a good
conceptual boundary.

### Raw Source Access Is In The Right Place

Raw source access should remain available but secondary. The current "Show raw
source" drawer points in the right direction: use it when something feels wrong,
not as the default path.

## UX Findings

### 1. The Header Contains Too Many Primary Decisions

The source header currently combines:

- article identity
- source metadata
- stale/readwise state
- management decision state
- previous/next navigation
- finish review
- approve
- needs attention
- skip
- request re-analysis

This makes the first viewport feel action-heavy. The user sees many buttons
before they have reviewed the content.

Recommended change:

- Make `Finish review` the only visually primary action.
- Move secondary decisions into a quieter action row or menu.
- Keep previous/next navigation compact.
- Make state metadata less prominent than the article title and Easy Read.

### 2. Article-Level Decision Semantics Are Still Slightly Confusing

There are two overlapping ideas:

- `Finish review`
- `Approve article`

For a human reviewer, these sound close. If finishing a review also approves the
article, the UI should make that relationship very explicit.

Recommended change:

- Rename or clarify the actions.
- Possible model:
  - primary: `Finish as approved`
  - secondary: `Needs attention`, `Skip`, `Request re-analysis`
- Avoid showing both `Finish review` and `Approve article` as equally plausible
  final actions.

### 3. The Queue Is Useful But Still Visually Dense

The queue works, but it still carries many responsibilities:

- status filter
- decision filter
- decision counts
- search
- global counts
- 100+ queue rows

Observed in the current app:

- 166 queue rows are rendered for the default filter.
- The queue is scrollable, which is good.
- But the filter/count area still consumes a lot of visual height.

Recommended change:

- Make the filter area more compact.
- Combine counts into one thin summary line or compact segmented summary.
- Keep queue rows visually quieter.
- Consider showing entity counts only when they help scanning.

### 4. Entity Cards Are Correct But Still Too Document-Like

The entity section is the most important review area after Easy Read. It is
currently accurate, but the cards often read like small articles.

This creates friction because the user is not trying to deeply read every
entity. The user is trying to answer:

- Is this extraction plausible?
- Are the tags roughly right?
- Is something obviously wrong?
- Should this article be approved?

Recommended change:

- Make entity cards more scannable.
- Put title, tags, and a short description in the first visual layer.
- Keep detail lists and evidence collapsed.
- Consider limiting description height with an intentional "expand" affordance
  only for long descriptions.

### 5. Edit Buttons Are Too Verbose

Buttons such as `Edit LLM-Maintained Knowledge Bases` become visually noisy.
They repeat the title that is already right next to them.

Recommended change:

- Use a compact `Edit` button.
- Add a tooltip or accessible label for the full action.
- Keep the visual row calm.

### 6. Hidden Entity Workflow Is Technically Present But Not Yet Obvious

`Show hidden` exists, and hide/unhide is available in edit mode. But the mental
model is not yet clear from the visible page.

Recommended change:

- Make hide/unhide a direct secondary action on the entity card.
- Keep editing for title/description/tags.
- Use edit mode for content changes, not for every visibility decision.

### 7. No Fast-Review Rhythm Yet

The app supports review, but it does not yet feel optimized for fast batch work.

Missing rhythm:

- approve current article
- automatically move to next
- keep the same scroll position model predictable
- avoid re-reading the action area each time

Recommended change:

- After finishing, move to the next unreviewed article.
- Keep the action feedback small and temporary.
- Add keyboard shortcuts later, but only after the visual workflow is stable.

## UI And Visual Design Findings

### 1. The Visual Direction Is Much Better Than Streamlit

The app already feels calmer than Streamlit. The light background, constrained
content width, sticky queue, and softer cards are all good choices.

This is worth keeping. Do not restart from scratch.

### 2. It Still Feels Like A Functional Admin App

The current design is clean but not yet elegant. It has many standard cards,
buttons, borders, and pills. Nothing is terrible, but many elements have similar
visual weight.

Recommended change:

- Reduce the number of card-like surfaces.
- Use stronger hierarchy between article, summary, tags, and entities.
- Let secondary information sit on the page more quietly.

### 3. The First Viewport Is Slightly Unbalanced

The first viewport shows:

- large queue controls
- a large source header
- many action buttons
- then Easy Read

The actual review content starts after a heavy control area.

Recommended change:

- Compress the source header.
- Move secondary actions out of the dominant header area.
- Bring Easy Read closer to the top of the review flow.

### 4. Typography Is Serviceable But Not Yet Refined

The typography is readable, but the hierarchy could be more polished.

Specific issues:

- body text is readable but sometimes feels large in entity cards
- card headings and entity titles have similar weights
- queue text can feel cramped

Recommended change:

- Slightly reduce entity body size or line-height.
- Strengthen article title and section hierarchy.
- Make queue row titles compact and predictable.

### 5. Tags Are Helpful But Visually Busy

Tags are important for taxonomy review, but many chips create visual noise.

Recommended change:

- Keep tags visible.
- Reduce chip contrast further.
- Use stronger color only for warnings, edited state, hidden state, or conflicts.

## Product Risks

### Risk 1: The User Approves Without Really Seeing The Problem

If the page contains too much text, the user may start approving articles based
only on the Easy Read. That would make the review fast but weaker.

Mitigation:

- Add a compact extraction summary near the top:
  - topics
  - glossary
  - trends
  - how-tos
  - tools
  - models
  - source-specific insights
- Let the user see at a glance whether the extraction shape looks plausible.

### Risk 2: Taxonomy Quality Still Has No Dedicated Workflow

Entity editing exists, but taxonomy maintenance is still mixed into normal
article review.

Mitigation:

- Keep article review lightweight.
- Later add a separate taxonomy cleanup view:
  - suspicious tags
  - near-duplicate tags
  - entities with weak or missing tags
  - overly broad tags

### Risk 3: Review State And Render State May Feel Too Abstract

Terms like `stale`, `current`, `management decision`, `ready for review`, and
`finished` are technically accurate but cognitively heavy.

Mitigation:

- Use user-facing labels based on action:
  - `Needs analysis`
  - `Ready to review`
  - `Reviewed`
  - `Needs re-analysis`
- Keep technical states in details/debug areas.

## Recommended Next Slice

Suggested slice name:

```text
management-web-fast-review-design-pass
```

Goal:

Make the current write-enabled review workspace faster, calmer, and easier to
trust without adding new backend capabilities.

Definition of Done:

- Header is compressed and action hierarchy is clearer.
- `Finish review` / `Approve article` ambiguity is resolved.
- Queue controls and counts are more compact.
- Easy Read appears earlier and remains fully visible.
- Extraction overview is visible near the top.
- Entity cards are more compact and scannable.
- Detail lists and evidence remain available but secondary.
- Hide/unhide is available without entering full edit mode.
- Raw source and debug JSON remain available but visually secondary.
- No new LLM calls.
- No new persistence model.
- No changes to render semantics.

## Suggested Implementation Order

1. Header and action model
   - simplify primary/secondary actions
   - clarify finish vs approve
   - compress metadata pills

2. Queue compaction
   - smaller control area
   - compact counts
   - quieter rows

3. Extraction overview
   - show entity group counts near top
   - make missing groups visible without full cards

4. Entity card redesign
   - shorter first layer
   - compact edit/hide actions
   - details/evidence secondary

5. Visual polish
   - reduce card proliferation
   - tune typography
   - quiet tag chips
   - improve spacing rhythm

6. Browser review
   - desktop 1280px
   - large monitor
   - narrow laptop width

## Recommendation

Do this design/UX pass before adding more product features. The backend can
already support meaningful article review. The limiting factor is now whether
the user can review 20-50 articles without fatigue.

The app should become less like a data inspector and more like a fast editorial
review desk.

## User Feedback Round

The user reviewed the current UI after the write-enabled entity editing slice.
The feedback confirms the main direction but adds several concrete usability
issues that should be treated as implementation requirements for the next design
pass.

### 1. `Finish review` And `Approve article` Are Ambiguous

The user does not understand the difference between `Finish review` and
`Approve article`.

This is not only a wording problem. It means the article-level action model is
unclear.

Required decision:

- Define one primary happy-path action.
- If finishing means approving, the button should say that directly.
- Do not show `Finish review` and `Approve article` as two competing primary
  choices.

Preferred direction:

- Replace `Finish review` with `Finish as approved`.
- Keep `Needs attention`, `Skip`, and `Request re-analysis` as secondary
  alternatives.
- Remove or hide the separate `Approve article` button unless it has a distinct
  behavior.

### 2. Header Buttons Shift And Wrap Depending On Title Width

The action buttons in the upper-right header area change layout depending on
the article title length. With long titles, buttons become narrow or wrap into
two lines.

This makes the UI feel unstable.

Required change:

- Give the action area a stable layout independent of title length.
- Prevent action buttons from changing height unexpectedly.
- Prefer a compact action rail or fixed-width action block.
- Long titles should wrap inside the title area, not compress the action area.

### 3. Easy Read And Collapsed Key Insights Are Good

The current Easy Read behavior is acceptable.

Keep:

- full Easy Read visible
- Key Insights collapsed by default

### 4. `Show hidden` Is Not Understandable

The user does not know what `Show hidden` means. Clicking it often creates no
visible change, which makes it feel broken or irrelevant.

Required change:

- Do not show `Show hidden` prominently when there are no hidden entities.
- Rename the concept in user-facing language.
- Show a count when hidden entities exist.

Preferred direction:

- Use `Show rejected entities (n)` or `Show hidden entities (n)`.
- Disable or hide the control when `n = 0`.
- Add a short tooltip or helper text only if needed.

### 5. Entity Edit Buttons Repeat Too Much Text

Buttons like `Edit LLM-Maintained Knowledge Bases` repeat the entity title even
though the title is already visible.

Required change:

- Use a compact visual label: `Edit`.
- Preserve accessibility with an `aria-label`, for example
  `Edit LLM-Maintained Knowledge Bases`.

### 6. Tag Editing Needs A Controlled Tag Picker

The current tag editing field is a free text field. That is not sufficient.

The intended behavior is:

- By default, users should select from existing tags.
- The UI should show which tags are available.
- In exceptional cases, the user should be able to create a new tag.
- Creating a new tag should be deliberate, not an accidental typo.

Required change:

- Replace the comma-separated tag input with a controlled tag picker.
- Existing tags should be selectable.
- New tags should require an explicit "create new tag" affordance.

Open implementation question:

- Which tag universe should be used initially?
  - all tags from current queue/source data
  - tags from config registries
  - tags from rendered wiki graph
  - a merged tag registry

Recommended first implementation:

- Backend exposes a read-only tag registry endpoint for the management UI.
- Frontend uses a multi-select tag picker with search.
- Unknown tag input becomes `Create new tag: <tag>`.

### 7. `Hidden` Inside Edit Mode Is Confusing

The edit form contains a `Hidden` field. The user does not understand what this
means or why it affects whether `Save entity` is enabled.

Observed problem:

- The user reports that `Save entity` only becomes available when `Hidden` is
  activated.
- This makes the save behavior feel broken, even if the underlying rule is
  "save only when something changed".

Required change:

- Remove `Hidden` from the normal content edit form.
- Make hide/reject a separate action on the entity card.
- Rename it to a clearer user-facing concept.

Preferred direction:

- Entity card actions:
  - `Edit`
  - `Reject`
- Hidden/rejected entities show a visible badge and can be restored with
  `Restore`.
- The edit form only edits title, description, and tags.

### 8. Left Sidebar Form Controls Need More Breathing Room

In the left column, some label text visually overlaps or sits too close to the
select boxes.

Required change:

- Increase spacing between labels and controls.
- Ensure labels never overlap select/input borders.
- Test with default browser font rendering on macOS.

### 9. Search And Count Cards Are Positive

The user likes:

- search functionality
- the count cards in the sidebar

Keep these concepts, but they can still be made more compact in the design
pass.

## Updated Next-Slice Requirements

The next implementation slice should focus on the review workspace UX, not on
new backend workflow capabilities.

Must fix:

- Resolve `Finish review` vs `Approve article`.
- Stabilize header action layout.
- Replace verbose entity edit buttons with compact `Edit`.
- Replace free-text tag editing with a controlled tag picker.
- Separate entity rejection/hiding from normal edit mode.
- Hide or clarify `Show hidden`.
- Fix left-sidebar label/control spacing.

Should keep:

- full Easy Read visible
- Key Insights collapsed
- search
- sidebar count cards
- collapsible entity details/evidence

Should avoid:

- new LLM calls
- new render semantics
- broad backend rewrites
- large product additions before this UX pass is complete
