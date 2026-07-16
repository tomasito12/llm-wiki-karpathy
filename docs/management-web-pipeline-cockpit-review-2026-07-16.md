# Management Web Pipeline Cockpit Review

Date: 2026-07-16

## Short Verdict

The Pipeline Cockpit is a useful first version. It makes the important operations visible and moves the system away from CLI-only usage. The current implementation is functionally promising, but the UX still feels more like a list of command wrappers than a real operations cockpit.

The next pass should not add many new capabilities. It should make the existing cockpit safer, easier to scan, and more operationally useful.

## What Works Well

- The page has the right basic structure: current status, recommended next actions, available operations, recent runs, and run details.
- The safety metadata is present: read-only vs. writes, LLM calls vs. no LLM calls.
- The status summary is easy to understand at first glance.
- The UI is calmer and cleaner than the old Streamlit-style command surface.
- Recent runs and stdout/stderr tails are valuable because they reduce the need to jump back to the terminal.

## Findings

### P1: Loading And Error States Are Too Weak

When the backend/status endpoint is unavailable or slow, the Pipeline page can show `Loading status...` and `No recommendations yet.` without making the problem obvious enough.

This is risky because the operator may think the system is idle or empty, while the real issue is that the cockpit cannot reach the backend.

Recommendation:

- Show a clear top-level state for `loading`, `loaded`, and `failed`.
- If status loading fails, show a visible error panel inside the Pipeline tab, not only a generic banner.
- Disable operation buttons until both operations and status have loaded.
- Add a retry button directly in the error state.

Definition of done:

- A stopped backend produces an explicit "Pipeline backend unavailable" or equivalent message.
- The page never presents "No recommendations yet" as the main message when status loading failed.

### P2: Recent Runs Are Buried Too Far Down

The operation cards currently form a long vertical block. Recent runs and run details appear only after all operation cards, which means the user has to scroll far down to see what just happened.

For a cockpit, recent execution state is almost as important as available actions.

Recommendation:

- Use a two-column desktop layout:
  - Left/main column: recommended actions and operation cards.
  - Right/side column: recent runs and selected run details.
- Keep the side column sticky on larger screens if it does not harm readability.
- On smaller screens, fall back to the current single-column layout.

Definition of done:

- On a large monitor, the user can see at least one action area and the latest run state in the first viewport.

### P2: Operation Cards Are Too Command-Centric

The current grouping repeats similar labels, for example a card titled `Wiki lint` containing an operation also called `Wiki lint`. The page reads like a thin GUI layer over CLI commands.

Recommendation:

- Rename groups around operator intent:
  - `Check wiki health`
  - `Preview or publish wiki`
  - `Inspect synthesis candidates`
  - `Run synthesis batch`
- Keep CLI-like names available only as secondary technical text or tooltip.
- Prefer action labels like `Run health check`, `Preview render`, `Write render`, `Show candidates`, `Dry-run batch`, `Run batch`.

Definition of done:

- A non-CLI user can understand what each block is for without knowing the hatch command name.

### P2: Recommendation Actions Are Not Safe Enough By Default

Recommendations can surface real operations directly, including synthesis batch actions that may write files and call the LLM.

This is convenient but too easy to click casually.

Recommendation:

- Recommended actions should prefer safe actions first:
  - For synthesis: show `Dry-run batch` first.
  - For render: show `Dry-run render` first unless the system already knows a dry-run just succeeded.
- Real write/LLM operations should either:
  - open the operation card with parameters visible, or
  - require a stronger confirmation modal.

Definition of done:

- No recommendation launches a write/LLM-capable operation without a clear confirmation step that explains impact, parameters, and expected output.

### P2: Parameter Inputs Need A Compact, Intentional Layout

Some parameters look visually odd because the current grid gives tiny controls too much horizontal space. For example, a boolean checkbox can appear detached from its label, and numeric inputs can span an unnecessarily wide column.

Recommendation:

- Use compact form rows for parameters.
- For booleans, use an inline checkbox or toggle with label beside it.
- For numbers, use a small fixed-width input.
- Add short helper text for high-impact parameters:
  - `limit`
  - `between_calls`
  - `require_source_text`

Definition of done:

- Parameter controls look intentionally placed and can be understood without guessing what the field changes.

### P2: Confirmation Modal Needs More Operational Context

The confirmation dialog lists writes, LLM calls, and raw parameter names. That is useful, but still too technical and not reassuring enough for dangerous operations.

Recommendation:

- Show the human operation label and a one-sentence consequence.
- Translate raw parameter keys into labels.
- Highlight danger level:
  - read-only
  - writes files
  - LLM calls
  - writes files and LLM calls
- For write/LLM operations, include expected output locations, for example cache files, wiki files, run reports.
- Keep `Cancel` visually neutral and make the destructive/real action clearly secondary until reviewed.

Definition of done:

- Before running a real operation, the user can answer: "What will this change, where will it write, and can it call the API?"

### P2: Status Summary Needs More Diagnostic Depth

The summary line is useful, but some phrases are too compressed. Example: `42 stale syntheses` is actionable only if the user already knows what stale syntheses imply.

Recommendation:

- Keep the compact summary.
- Add small status chips below it:
  - sources
  - finished reviews
  - render status
  - synthesis cache
  - uncommitted artifacts
- Use color sparingly:
  - green for ready/current
  - yellow for attention
  - red for blocked/error

Definition of done:

- The top status band tells the user whether the system is safe to continue, needs review, or is blocked.

### P3: Run History Needs Better Scanability

The run list currently uses three columns but all rows look similar. Failed runs are visible by text, but not visually strong enough.

Recommendation:

- Add status chips for succeeded/failed/running.
- Make failed runs visually stand out.
- Show relative time if possible, with absolute timestamp available.
- Keep the selected run highlighted.

Definition of done:

- The user can identify the latest failed operation within one second.

### P3: Visual Design Is Clean But Still Generic

The cockpit already looks calmer than the old dashboard, but it still feels like a generic admin surface. The hierarchy could be sharper.

Recommendation:

- Reduce repeated card chrome.
- Make the status band visually distinct from operation cards.
- Use smaller, denser typography for secondary metadata.
- Keep the palette restrained, but use semantic accents for health states.

Definition of done:

- The page feels like a purpose-built workflow console, not a collection of generic cards.

## Suggested Next Implementation Slice

Implement a `Pipeline Cockpit UX Pass` with this scope:

1. Strong loading/error/empty states.
2. Desktop two-column layout with recent runs/details visible earlier.
3. Operator-oriented operation labels and grouping.
4. Compact parameter controls.
5. Safer recommendation actions and stronger confirmation modal.
6. Better run status chips and failed-run visibility.

Out of scope for this slice:

- New backend operations.
- Scheduling/cron automation.
- Public wiki UI.
- Full redesign of the management app.

This keeps the implementation focused: the cockpit should become safer and easier to operate before adding more automation.
