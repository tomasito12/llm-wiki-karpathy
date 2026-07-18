# Management Web Design Review

Date: 2026-07-18
Scope: visual design only
Viewport inspected: desktop, approximately 1440 x 1000

This review deliberately ignores workflow logic, backend behavior, and feature
scope. It evaluates only the visible arrangement of elements, typography,
spacing, alignment, density, contrast, and overall visual calm.

## Overall Impression

The management web app is moving in the right direction. It already feels much
cleaner than the old Streamlit dashboard, and the visual language is becoming
quiet, utilitarian, and appropriate for an internal operations tool.

The main remaining design issue is not ugliness, but visual unevenness. Some
areas feel polished and calm, while others still look like raw form controls or
debug output placed into cards. The next design pass should focus less on new
visual style and more on making the existing layout feel deliberate,
proportioned, and rhythmically consistent.

## Global Design Findings

### 1. Page Shell Is Calm, But Slightly Too Sparse

The top header, navigation pills, and status badge are visually restrained and
pleasant. The large background and generous margins help the app feel less
stressful.

However, the pages sometimes feel like content is floating in a very large
empty canvas. This is especially visible in the Pipeline tab and in the Review
tab when no source is selected or while the queue is loading.

Recommendation:

- Keep the calm spacing, but make the main content area feel more intentionally
  anchored.
- Use consistent max-widths and column proportions instead of letting sections
  appear as isolated islands.

### 2. Card Language Is Mostly Good, But Too Repetitive In Dense Areas

Cards work well for the article header, Easy Read section, entity groups, and
pipeline operation areas. The 8px-radius style feels appropriate.

In dense areas, the repeated card-within-card feeling returns slightly:
operation card, result panel, status pill, nested list, button, technical link.
This creates visual stacking and makes the page feel heavier than it needs to.

Recommendation:

- Keep cards for major content groups.
- Use flatter dividers, subtle section headers, or compact rows inside cards
  instead of nesting more framed surfaces.

### 3. Typography Is Readable, But Hierarchy Needs Tightening

Body text is generally readable. The Easy Read section now has a comfortable
line length and feels much better than earlier versions.

Some headings and labels compete for attention:

- `Queue`, `Status`, `Decision`, `Search`, and count summaries all have similar
  visual weight.
- Pipeline operation headings and sub-operation labels sometimes feel only one
  step apart in hierarchy, even though they represent different levels.
- Some metadata text is slightly too prominent for information that is mostly
  contextual.

Recommendation:

- Define a clearer type scale for:
  - page title
  - section title
  - card title
  - entity title
  - form label
  - metadata
  - helper text
- Reduce metadata and helper text weight/contrast slightly.

### 4. Horizontal Alignment Is Not Yet Fully Systematic

Most sections align well, but there are still small visual jumps:

- Review action buttons in the article header occupy a right-side block that
  feels slightly detached from the title area.
- Pipeline controls align in one row, but the checkbox label sits visually low
  and does not align cleanly with the number inputs or Update Wiki button.
- Advanced manual operation buttons are sometimes far to the right of their
  labels, creating long empty gaps inside cards.

Recommendation:

- Introduce stricter internal grid rules for action rows.
- Align labels, inputs, checkboxes, and buttons to a shared baseline.
- Avoid very long horizontal distances between a setting and its action.

## Review Workspace

### 1. Queue Column Has Good Density, But Needs More Visual Refinement

The queue is much better than before: it is narrow, scannable, and date/entity
metadata is visible without overwhelming the article titles.

Design issues:

- The filter area is visually a little cramped compared to the content list.
- The select boxes are large relative to their labels.
- The count summary wraps into multiple lines and becomes visually noisy.
- The selected item border is useful, but the selected state could be more
  elegant and less boxy.

Recommendation:

- Make queue metadata smaller and quieter.
- Consider a more compact filter layout with stronger vertical rhythm.
- Keep the selected source clear, but soften the selected outline or use a
  left accent bar.

### 2. Main Article Header Is Strong, But Action Area Feels Slightly Mechanical

The title, source metadata, and status are arranged clearly. The right-side
action group is functional and visually understandable.

Design issues:

- The navigation counter and action buttons form a very separate block.
- The primary blue button is visually strong, which is good, but it dominates
  the header more than the article title in some cases.
- Secondary buttons are arranged in a way that can feel like a control panel
  rather than part of the article review flow.

Recommendation:

- Keep `Finish as approved` visually primary.
- Reduce the visual mass of secondary decisions.
- Consider grouping navigation separately from review decisions, with more
  deliberate spacing between those two concerns.

### 3. Easy Read Section Is The Best-Reading Area

This is currently the strongest part of the Review tab. The card width, text
line length, padding, and typography are comfortable.

Recommendation:

- Treat Easy Read as the typographic model for other long-text areas.
- Reuse its text width and paragraph rhythm for entity descriptions where
  possible.

### 4. Extraction Overview Chips Are Useful, But Slightly Too Flat

The overview chips are compact and visually quiet. That is good for reducing
noise.

Design issue:

- All chips have nearly equal visual weight, including zero-count categories.
  This makes the eye scan more than necessary.

Recommendation:

- Make zero-count chips quieter.
- Give non-zero chips a slightly stronger text color or subtle border.
- Keep the row compact; do not turn it into large cards.

### 5. Entity Cards Are Readable, But Too Uniform

Entity sections are clear enough to review. Titles, tags, descriptions, and
Edit/Reject actions are visible.

Design issues:

- All entity cards look very similar regardless of importance.
- Section headers like `Topics`, `Trends`, and `Tools` are clear, but the entity
  boundaries rely mostly on whitespace and dividers.
- Edit/Reject buttons repeat at the same visual strength on every card, adding
  action noise.
- Long descriptions use acceptable line length, but could feel a bit more
  editorial and less dense.

Recommendation:

- Make entity titles slightly stronger than action buttons.
- Make Edit/Reject visually quieter until hover/focus.
- Add a little more vertical rhythm between title, tags, description, and
  details.
- Keep descriptions readable but avoid expanding cards into overly large blocks.

### 6. Sticky Header Overlay Looks Visually Awkward While Scrolling

When scrolling down the Review page, the sticky top header overlays content with
a translucent/faded look. This creates a moment where text behind the header
looks ghosted and visually messy.

Recommendation:

- Give the sticky header a solid background and clear lower border/shadow.
- Ensure content never visually bleeds behind it.

## Pipeline Cockpit

### 1. New Primary Update Area Is Much Calmer Than The Old Command Panel

The new `Wiki update available` section is a strong improvement. It reduces the
feeling of being presented with many unrelated CLI buttons.

Design issues:

- The status card is very wide, but its content occupies only the left and lower
  portions.
- The `Refresh status` button sits far away from the main status text.
- The hint list still looks like plain document text rather than an app status
  surface.

Recommendation:

- Consider a two-column status layout: summary and action on top, compact hints
  below.
- Style hints as quiet status rows rather than a plain bullet list.
- Reduce unused horizontal emptiness.

### 2. Update Controls Need Better Alignment

The batch size input, pause input, checkbox, and Update Wiki button are now in
one visible control row. This is conceptually good.

Design issues:

- The checkbox is vertically misaligned with its label and neighboring inputs.
- The checkbox label is long and visually competes with the primary action.
- The Update Wiki button appears as one item in a row rather than the main
  action of the card.

Recommendation:

- Place advanced/safety toggles below or beside the main controls with quieter
  styling.
- Make `Update Wiki` the clear visual endpoint of the card.
- Align numeric inputs and primary action to a consistent baseline.

### 3. Advanced Manual Operations Are Correctly De-Emphasized

Collapsing advanced operations is the right direction. When collapsed, the page
is much calmer.

Design issue:

- When expanded, the advanced area becomes visually dominant again.
- The focus outline around the expanded header is strong and a little harsh.

Recommendation:

- Keep the advanced section collapsed by default.
- Use a softer expanded-state indicator.
- If expanded, make it feel like a secondary drawer, not another primary page.

### 4. Pipeline Operation Cards Are Cleaner, But Still Heavy

The operation cards are now more legible than before. Result summaries are much
better than raw JSON.

Design issues:

- There is a lot of repeated structure: heading, paragraph, subheading,
  metadata, helper text, button, result panel.
- Buttons often sit far to the right, creating empty space and weak association
  with the operation they trigger.
- Result panels are visually large for short summaries.

Recommendation:

- Convert sub-operations into compact rows where possible.
- Keep result summaries visually smaller unless they contain warnings or errors.
- Use status badges sparingly; repeated green badges create visual clutter.

### 5. Recent Runs Sidebar Is Useful But Too Visually Prominent

The recent runs list is readable and structured. The card selection state is
clear.

Design issue:

- The sidebar competes with the primary operation cards because every run item
  is a bordered mini-card with a green badge.
- The repeated green `Succeeded` badges create more visual emphasis than the
  historical nature of the list deserves.

Recommendation:

- Make recent runs visually quieter.
- Consider a denser list layout with a small status dot instead of full badges.
- Reserve strong badges for failed/warning states.

## Visual Priority List

### Priority 1: Fix Sticky Header Overlay

The translucent overlap while scrolling makes the app feel less polished. This
is the most visible pure-design issue.

### Priority 2: Improve Pipeline Control Alignment

The Update Wiki card is the future center of the product. Its controls should
feel carefully aligned and intentional.

### Priority 3: Reduce Repeated Visual Weight In Pipeline Results

The Pipeline tab still becomes visually heavy once advanced operations are
expanded. Result panels and repeated success badges should be quieter.

### Priority 4: Refine Queue Filter And Count Area

The Review queue is central to daily work. Its information is useful, but the
top filter/count area can become calmer and more proportional.

### Priority 5: Quiet Entity Action Buttons

Edit and Reject are important, but their repeated presence adds visual noise.
They should remain discoverable while becoming less dominant.

## Design Direction

The app should continue moving toward:

- quiet internal tool
- compact but not cramped
- strong reading surfaces
- restrained color
- clear alignment
- low visual noise
- warnings/errors emphasized only when needed

Avoid moving toward:

- marketing-style cards
- oversized dashboard widgets
- many equally prominent action buttons
- repeated status badges everywhere
- raw technical output as a visual centerpiece

The current design is solid enough to build on. The next pass should be a
polish pass, not a redesign.
