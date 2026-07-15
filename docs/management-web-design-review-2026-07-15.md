# Management Web Design Review

Date: 2026-07-15
Scope: first read-only batch review UI
Related implementation: `management-web-v0-readonly-batch-review`

## 1. Review Summary

The current management web app is directionally correct, but still feels like a
technical prototype rather than a polished review tool.

The functional foundation is good:

- queue-based review exists
- source metadata is visible
- Easy Read is visible
- tags and extracted entities are visible
- raw source and debug JSON are available on demand
- the app is read-only

The main issue is not missing backend capability. The main issue is visual and
interaction design: the current layout creates too much vertical sprawl, weak
hierarchy, and too many equally weighted cards.

Before adding write actions such as approve / needs attention / skip, the UI
should receive a focused design pass.

## 2. UX Findings

### 2.1 Queue Dominates The Page

The left queue currently renders the full list in the normal page flow. On a
large monitor the page can become extremely tall because every queue item
contributes to the document height.

Observed effect:

- the page becomes visually dominated by the queue
- scrolling feels like scrolling the whole app rather than reviewing one source
- the main review area does not feel stable

Recommended fix:

- make the queue a fixed-height, independently scrollable panel
- keep the selected article and review workspace stable while scrolling the
  queue
- consider a compact row style for queue items

### 2.2 Right Panel Is Not Worth Its Visual Weight Yet

The right panel currently contains mostly placeholder actions and small status
information. It takes a full column, but does not yet provide enough utility.

Observed effect:

- placeholder actions compete with the real review content
- the right panel makes the layout feel more complex than the current slice
  needs

Recommended fix:

- either remove the right panel for the read-only slice
- or reduce it to a small sticky utility strip
- move previous / next navigation into the article header or above the review
  card
- keep future article actions visually muted until they are write-capable

### 2.3 Header Metadata Is Too Prominent

The title should dominate the article header. Current status pills such as
`Ready for review`, `Stale unknown`, and `Readwise unknown` have too much visual
weight.

Observed effect:

- metadata competes with the article title
- the header looks busy
- unknown values draw attention even when they are not actionable

Recommended fix:

- reduce metadata styling
- make unknown values quieter
- keep only actionable state visually prominent
- consider a compact metadata row below the title

### 2.4 Entity Cards Are Too Text-Heavy For Fast Review

Entity cards currently show title, description, tags, and evidence in a long
vertical card. This is useful, but not optimized for fast plausibility review.

Observed effect:

- the user has to read too much per entity
- cards feel like mini documents
- evidence can make the card visually heavy

Recommended fix:

- show entity title and a 1-2 line description first
- keep tags visible but quieter
- move evidence into an expandable detail or visually secondary block
- allow scanning by category and count

### 2.5 Empty Sections Consume Too Much Attention

For some articles, tags/topics/glossary/trends are empty. Empty states are useful,
but currently they still appear as full cards.

Observed effect:

- empty cards make the article look sparse and unfinished
- the user spends attention confirming absence

Recommended fix:

- collapse or compact empty categories
- show empty categories as a small muted row
- reserve full cards for categories with extracted content

### 2.6 Easy Read Is Correct But Feels Longer Than Streamlit

The new UI uses `accessible_overview`, which is the same conceptual Easy Read
field as Streamlit. However, Streamlit displays it inside a 200px text area,
which makes it feel visually shorter and more contained.

Observed effect:

- the same text feels longer in the new UI
- free-flowing paragraph text increases perceived reading effort

Recommended fix:

- keep the full Easy Read visible, because the user wants to read it
- improve typography and width
- do not show key insights by default
- consider slightly smaller line length and better paragraph rhythm

## 3. Aesthetic Findings

### 3.1 The UI Still Looks Like A Default Web App

The current interface is functional, but not yet elegant.

Signals:

- many white cards
- similar border/shadow treatment everywhere
- weak visual hierarchy
- default-feeling form controls and buttons

Recommended fix:

- define a small design system for this app
- reduce card proliferation
- use cards only where they frame a meaningful unit
- use subtler surfaces for secondary information

### 3.2 Top Bar Feels Heavy

The dark top bar is visually strong and not fully integrated with the rest of
the page.

Observed effect:

- it feels like an admin template header
- it draws attention away from the review workspace

Recommended fix:

- reduce top bar height and contrast
- consider a lighter header
- keep the read-only state visible but less dominant

### 3.3 Typography Needs Refinement

The current typography feels somewhat clunky.

Issues:

- headings and body text do not yet form a refined hierarchy
- queue item text is dense but not elegant
- card headings feel over-prominent relative to content

Recommended fix:

- use smaller, calmer card headings
- improve source title hierarchy
- reduce visual weight in queue rows
- keep body line length comfortable

### 3.4 Tags Are Useful But Visually Noisy

The green tag chips are helpful for taxonomy review, but they create a lot of
visual activity.

Recommended fix:

- reduce tag saturation
- use a quieter neutral chip style
- reserve stronger color for important warnings or changes

## 4. Recommended Next Design Slice

Suggested slice name:

```text
management-web-v0-design-pass-1
```

Goal:

Improve the read-only review surface before adding write-capable review actions.

Definition of Done:

- queue is independently scrollable
- main review panel remains stable while queue scrolls
- default view still starts with Ready for review
- article header has clearer hierarchy
- Easy Read remains fully visible but more readable
- key insights remain collapsed
- entity cards are more compact and scannable
- empty entity categories are visually quieter
- right panel is removed, reduced, or repositioned
- paths remain available but hidden
- no write actions are introduced
- no LLM calls are introduced

## 5. Suggested Implementation Order

1. Layout stabilization
   - fixed-height scrollable queue
   - main content width and spacing
   - right-panel reduction

2. Typography and hierarchy
   - article title
   - section headings
   - queue rows
   - Easy Read body text

3. Entity card redesign
   - compact title/description/tag layout
   - evidence secondary or expandable
   - empty category compaction

4. Color and surface cleanup
   - less saturated tags
   - lighter header
   - fewer heavy cards

5. Browser review
   - desktop large monitor
   - 1280px laptop width
   - narrow/mobile fallback

## 6. Recommendation On Product Sequence

Do a focused design pass before adding write functionality.

Reason:

The next write actions depend on the review rhythm. If the layout still feels
heavy or unpleasant, write actions may be added in the wrong place or with the
wrong visual emphasis.

This should not become a long design detour. The target is a practical pass that
makes the existing read-only review UI pleasant enough to use, then move on to
article-level write decisions.
