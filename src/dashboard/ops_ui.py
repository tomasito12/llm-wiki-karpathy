"""Temporary Streamlit controls for common wiki operations."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.dashboard.paths import readwise_library_index_path
from src.dashboard.readwise_sync_ui import (
    format_sync_summary,
    readwise_token_from_env,
    try_readwise_sync,
)
from src.wiki_ops.release_manifest import RELEASE_MANIFEST_AREA_KEYS
from src.wiki_paths.config import WikiPaths


@dataclass(frozen=True)
class DashboardCommandResult:
    """Captured result for one dashboard command."""

    label: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        """Return True when the command exited successfully."""
        return self.returncode == 0


def command_text(command: list[str]) -> str:
    """Return a readable shell-like command."""
    return " ".join(command)


def run_dashboard_command(
    *,
    label: str,
    command: list[str],
    cwd: Path,
    timeout_seconds: int = 300,
) -> DashboardCommandResult:
    """Run a short-lived wiki operation and capture its output."""
    try:
        completed = subprocess.run(  # noqa: S603
            command,
            cwd=cwd,
            env=os.environ.copy(),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return DashboardCommandResult(
            label=label,
            command=command,
            returncode=124,
            stdout=stdout,
            stderr=(stderr + f"\nTimed out after {timeout_seconds}s.").strip(),
        )
    except OSError as exc:
        return DashboardCommandResult(
            label=label,
            command=command,
            returncode=1,
            stdout="",
            stderr=str(exc),
        )
    return DashboardCommandResult(
        label=label,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def render_command_result(st: Any, result: DashboardCommandResult) -> None:
    """Render one command result."""
    if result.ok:
        st.success(f"{result.label} completed.", icon=":material/check_circle:")
    else:
        st.error(
            f"{result.label} failed with exit code {result.returncode}.",
            icon=":material/error:",
        )
    st.caption(f"`{command_text(result.command)}`")
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    if output:
        st.code(output, language="text")
    interpretation = _output_interpretation(result.label)
    if interpretation:
        st.info(interpretation, icon=":material/lightbulb:")


def _output_interpretation(label: str) -> str | None:
    """Return a short plain-language hint for one command label."""
    hints = {
        "Ops status": (
            "This is a health snapshot. Look for warnings about stale synthesis, missing "
            "source text, or uncommitted files. Fix warnings before a big render or batch."
        ),
        "Render dry-run": (
            "Nothing was written. Default scope is finished reviews only; in-progress sources "
            "stay on disk as protected preview files. Key lines: sources = finished source pages; "
            "would write = new/changed files; protected = in-progress preview files not deleted. "
            "If the summary looks right, run “Render wiki” next."
        ),
        "Render wiki": (
            "The private vault was updated from finished reviews only. In-progress preview pages "
            "on disk are left untouched. Open Obsidian and spot-check a few changed pages. "
            "Then run “Wiki lint” if you want a consistency check."
        ),
        "Wiki lint": (
            "Checks wiki_contract rules plus vault hygiene: stale orphans vs the render "
            "manifest, protected in-progress pages, manual legacy folders, and exact duplicates. "
            "Zero contract errors is the goal; hygiene findings need review before deletion."
        ),
        "Synthesis cache lint": (
            "Checks whether synthesis cache files still match the render graph. "
            "Stale or error rows mean you may need a new synthesis batch or a re-render."
        ),
        "Show synthesis plan": (
            "Read the summary line first (new / stale / unchanged). "
            "Each row is one wiki page that may need Stage 2 synthesis. "
            "“new” = no cache yet, “stale” = reviews changed since last synthesis."
        ),
        "Select next candidates": (
            "This is the ranked shortlist the batch would pick. "
            "Use it to decide whether limit and category look right before spending API calls."
        ),
        "Batch dry-run": (
            "Same candidate list as a real batch, but no OpenAI calls and no file writes. "
            "If this looks good, enable “Allow real synthesis batch” and run step 4."
        ),
        "Run synthesis batch": (
            "Synthesis text was written to the synthesis cache. "
            "Next: “Render wiki” so the vault shows the new synthesis, then optional lint checks."
        ),
        "Release manifest": (
            "A release manifest records one checkpoint of the knowledge store. "
            "For restore later, the manifest must include a snapshot id. "
            "Status “ready” is best; “warning” is often still usable but worth reading."
        ),
        "Release restore": (
            "Dry-run shows which folders would be replaced. "
            "After a real restore, check the verify section: “ok” means the store matches "
            "the release manifest again."
        ),
    }
    return hints.get(label)


def _python_command(module: str, *args: str) -> list[str]:
    """Build a Python module command using the current interpreter."""
    return [sys.executable, "-m", module, *args]


def _paths_config_args(paths_config: Path | None) -> list[str]:
    """Return CLI args for the active path config."""
    return ["--paths-config", str(paths_config)] if paths_config is not None else []


def _store_result(st: Any, result: DashboardCommandResult) -> None:
    """Persist the latest operation result across Streamlit reruns."""
    st.session_state["_ops_last_result"] = result


def _render_button_command(
    st: Any,
    *,
    label: str,
    key: str,
    command: list[str],
    repo_root: Path,
    timeout_seconds: int = 300,
    button_type: str = "secondary",
    help_text: str | None = None,
) -> None:
    """Render a button that runs a command and stores the result."""
    if help_text:
        st.caption(help_text)
    if st.button(label, key=key, type=button_type, width="stretch"):
        with st.spinner(f"Running {label}…"):
            _store_result(
                st,
                run_dashboard_command(
                    label=label,
                    command=command,
                    cwd=repo_root,
                    timeout_seconds=timeout_seconds,
                ),
            )
        st.rerun()


def _render_operations_overview(st: Any) -> None:
    """Render a plain-language map of the operations page."""
    with st.expander("How this page works (start here)", expanded=True):
        st.markdown(
            """
This page wraps the CLI tools you would otherwise run by hand.
**Nothing runs until you click a button.**

**Typical day-to-day order**

1. **Readwise export** — pull new sources into `llm-wiki-data`
   (only when you have new Reader items).
2. **Review sources** — use the *Review* page in this dashboard (not this ops page).
3. **Render and checks** — turn reviews into Obsidian wiki pages.
4. **Synthesis workflow** — optional Stage 2 text for multi-source pages
   (costs OpenAI API calls).
5. **Releases and restore** — safety net before/after risky batches; not needed every day.

**Where output appears**

Every command prints to **Latest command output** at the bottom. A green box means exit code 0.
Read the text block first; the blue hint below explains what to do next.

**Safe defaults**

- Prefer **dry-run** buttons before anything that writes files or calls APIs.
- Before a big synthesis batch or mass render: write a **release manifest** with a snapshot id.
            """
        )


def render_readwise_operations(
    st: Any,
    *,
    repo_root: Path,
    paths: WikiPaths,
) -> None:
    """Render Readwise sync and raw export controls."""
    with st.container(border=True):
        st.subheader("Readwise export")
        st.caption("Step 0 — ingest new sources from Readwise Reader into the knowledge store.")
        with st.expander("When and how to use this"):
            st.markdown(
                """
Run this when you tagged new articles **processed** in Readwise Reader
and want them as raw files locally.

**What it does:** downloads HTML/Markdown exports into your configured raw folder
and updates the Readwise index.

**After sync:** go to the **Review** page and work through new sources.
Do not render until reviews exist.

**Options**
- *Re-export missing files* — use when the index says a file exists
  but the file is gone on disk.
- *Reset watermark* — re-fetch from an older point in time
  (slower; only when you suspect missed items).
                """
            )
        st.caption(f"Raw folder: `{paths.raw_dir}`")
        st.caption(f"Index: `{readwise_library_index_path(paths)}`")
        has_token = readwise_token_from_env() is not None
        if not has_token:
            st.warning("READWISE_TOKEN or READWISE_API_TOKEN is not set.", icon=":material/key:")
        prune_missing = st.checkbox(
            "Re-export missing files",
            value=False,
            key="ops_readwise_prune_missing",
            help="Re-download documents when the index says they exist but files are missing.",
        )
        reset_watermark = st.checkbox(
            "Reset watermark",
            value=False,
            key="ops_readwise_reset_watermark",
            help="Ignore the saved Readwise sync watermark for this run.",
        )
        if st.button(
            "Sync Readwise into wiki data",
            key="ops_readwise_sync",
            type="primary",
            width="stretch",
            disabled=not has_token,
        ):
            with st.spinner("Syncing from Readwise Reader…"):
                result, error = try_readwise_sync(
                    repo_root=repo_root,
                    output_dir=paths.raw_dir,
                    index_path=readwise_library_index_path(paths),
                    prune_missing=prune_missing,
                    reset_watermark=reset_watermark,
                )
            if error:
                st.session_state["_ops_readwise_flash"] = ("error", error)
            elif result is not None:
                st.session_state["_ops_readwise_flash"] = (
                    "success",
                    format_sync_summary(result),
                )
            st.rerun()

        flash = st.session_state.pop("_ops_readwise_flash", None)
        if flash:
            level, message = flash
            if level == "success":
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/error:")


def render_render_and_lint_operations(
    st: Any,
    *,
    repo_root: Path,
    paths_config: Path | None,
) -> None:
    """Render wiki render, status, and lint controls."""
    config_args = _paths_config_args(paths_config)
    with st.container(border=True):
        st.subheader("Render and checks")
        st.caption("Step 3 — build the Obsidian wiki from reviewed knowledge.")
        with st.expander("Recommended order and what each button does"):
            st.markdown(
                """
**Order**

1. **Ops status** — quick health check (optional but useful).
2. **Render dry-run** — preview changes; no files written. Scope: **finished only**.
3. **Render wiki** — updates the private vault (**finished reviews only**).
4. **Wiki lint** — contract checks plus vault hygiene (orphans, duplicates, manual folders).
5. **Synthesis cache lint** — checks Stage 2 cache vs render graph (after synthesis work).

**When to render**

After you finished reviewing sources, or after a synthesis batch updated cache entries.
Rendering is what makes changes visible in Obsidian.
                """
            )
        _render_button_command(
            st,
            label="1. Ops status",
            key="ops_status_button",
            command=_python_command("src.wiki_ops.status_cli", *config_args),
            repo_root=repo_root,
            help_text="Read-only summary of sources, reviews, render, and synthesis state.",
        )
        _render_button_command(
            st,
            label="2. Render dry-run",
            key="ops_render_dry_run_button",
            command=_python_command(
                "src.wiki_render",
                *config_args,
                "--dry-run",
                "--show-writes",
                "--require-source-text",
            ),
            repo_root=repo_root,
            help_text="Finished-only preview. In-progress preview files stay protected.",
        )
        _render_button_command(
            st,
            label="2b. Render dry-run (incl. in-progress)",
            key="ops_render_dry_run_preview_button",
            command=_python_command(
                "src.wiki_render",
                *config_args,
                "--dry-run",
                "--include-in-progress",
                "--require-source-text",
            ),
            repo_root=repo_root,
            help_text="Optional preview including in-progress reviews.",
        )
        _render_button_command(
            st,
            label="3. Render wiki",
            key="ops_render_button",
            command=_python_command("src.wiki_render", *config_args, "--require-source-text"),
            repo_root=repo_root,
            button_type="primary",
            help_text="Writes finished reviews. In-progress preview files stay on disk.",
        )
        _render_button_command(
            st,
            label="4. Wiki lint",
            key="ops_wiki_lint_button",
            command=_python_command("src.wiki_lint", *config_args),
            repo_root=repo_root,
            help_text="Contract checks plus vault hygiene (orphans, duplicates, manual folders).",
        )
        _render_button_command(
            st,
            label="4b. Vault cleanup dry-run",
            key="ops_vault_cleanup_dry_run_button",
            command=_python_command("src.wiki_ops.vault_cleanup_cli", *config_args, "--dry-run"),
            repo_root=repo_root,
            help_text=(
                "Lists safe-delete orphans and duplicate removals; "
                "use --after-release --yes to delete."
            ),
        )
        _render_button_command(
            st,
            label="5. Synthesis cache lint",
            key="ops_synthesis_cache_lint_button",
            command=_python_command("src.wiki_synthesis.cache_lint_cli", *config_args),
            repo_root=repo_root,
            help_text="Validates synthesis cache entries against the current render graph.",
        )


def render_synthesis_operations(
    st: Any,
    *,
    repo_root: Path,
    paths_config: Path | None,
) -> None:
    """Render synthesis planning and batch controls."""
    config_args = _paths_config_args(paths_config)
    categories = [
        "all",
        "glossary",
        "how_to",
        "topic",
        "trend",
        "tool",
        "model",
    ]
    with st.container(border=True):
        st.subheader("Synthesis workflow")
        st.caption("Step 4 — optional Stage 2 text for multi-source wiki pages (OpenAI API).")
        with st.expander("What is synthesis, and when do I need it?"):
            st.markdown(
                """
**Stage 2 synthesis** writes a richer summary for wiki pages that combine
several reviewed sources (topics, trends, tools, etc.).

**You do not need this for every page.** Many pages work fine with Stage 1 review content alone.

**When to run it**

- After reviews changed and the render graph shows pages as **stale** or **new** in the plan.
- When you want updated narrative text before rendering the vault.

**Cost note:** “Run synthesis batch” calls the OpenAI API (`OPENAI_API_KEY` required).
Dry-run steps are free.

**After a successful batch:** go to **Render and checks → Render wiki**
so Obsidian shows the new text.
                """
            )
        with st.expander("Step-by-step (follow this order)"):
            st.markdown(
                """
| Step | Button | Writes files? | API calls? |
|------|--------|---------------|------------|
| 1 | Show synthesis plan | No | No |
| 2 | Select next candidates | No | No |
| 3 | Batch dry-run | No | No |
| 4 | Run synthesis batch | Yes (cache) | Yes |

**How to read step 1 output**

The summary line shows counts: `new` (never synthesized), `stale` (inputs changed),
`unchanged` (cache still valid).
Each row is one entity (e.g. `topic:foo`) with source/evidence counts.

**How to read steps 2–3**

You get a ranked list — top rows are what the batch would process first, up to your **Limit**.
If the list looks wrong, change **Category** or **Limit** and repeat from step 1.

**How to read step 4 output**

Shows per-entity success/skip/error. Errors do not always stop the whole batch.
Then render the wiki and optionally run **Synthesis cache lint**.
                """
            )

        st.markdown("**Shared filters** (apply to all steps below)")
        limit = int(
            st.number_input(
                "Limit",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                key="ops_synthesis_limit",
                help="Maximum number of pages to show or process in one batch.",
            )
        )
        category = st.selectbox(
            "Category",
            categories,
            key="ops_synthesis_category",
            help="Narrow to one page type, or “all” for mixed batches.",
        )
        category_args = [] if category == "all" else ["--category", category]

        st.markdown("**Step 1 — See what needs work**")
        _render_button_command(
            st,
            label="Show synthesis plan",
            key="ops_synthesis_plan_button",
            command=_python_command(
                "src.wiki_synthesis",
                *config_args,
                "--changed-only",
                "--limit",
                str(limit),
                *category_args,
            ),
            repo_root=repo_root,
            help_text=(
                "Overview of new/stale pages. Start here to see whether a batch is worth running."
            ),
        )

        st.markdown("**Step 2 — See the ranked shortlist**")
        _render_button_command(
            st,
            label="Select next candidates",
            key="ops_synthesis_select_button",
            command=_python_command(
                "src.wiki_synthesis.select_cli",
                *config_args,
                "--limit",
                str(limit),
                *category_args,
            ),
            repo_root=repo_root,
            help_text="Same candidates the batch would pick, sorted by priority. No API calls.",
        )

        st.markdown("**Step 3 — Preview the batch (still safe)**")
        _render_button_command(
            st,
            label="Batch dry-run",
            key="ops_synthesis_batch_dry_run_button",
            command=_python_command(
                "src.wiki_synthesis.batch_cli",
                *config_args,
                "--dry-run",
                "--limit",
                str(limit),
                *category_args,
            ),
            repo_root=repo_root,
            timeout_seconds=600,
            help_text="Confirms the exact batch without spending tokens or writing cache files.",
        )

        st.markdown("**Step 4 — Run for real**")
        allow_real_batch = st.checkbox(
            "Allow real synthesis batch",
            value=False,
            key="ops_allow_real_synthesis_batch",
            help=(
                "Required to enable the button below. "
                "Sends contexts to OpenAI and writes cache files."
            ),
        )
        between_calls = int(
            st.number_input(
                "Seconds between calls",
                min_value=0,
                max_value=3600,
                value=10,
                step=10,
                key="ops_synthesis_between_calls",
                help="Pause between API calls to reduce rate-limit risk.",
            )
        )
        st.caption(
            "Tip: write a **release manifest** (with snapshot id) "
            "in the section below before step 4."
        )
        if st.button(
            "Run synthesis batch",
            key="ops_synthesis_batch_run_button",
            type="primary",
            width="stretch",
            disabled=not allow_real_batch,
        ):
            command = _python_command(
                "src.wiki_synthesis.batch_cli",
                *config_args,
                "--limit",
                str(limit),
                "--between-calls",
                str(between_calls),
                "--yes",
                *category_args,
            )
            with st.spinner("Running synthesis batch…"):
                _store_result(
                    st,
                    run_dashboard_command(
                        label="Run synthesis batch",
                        command=command,
                        cwd=repo_root,
                        timeout_seconds=max(600, (between_calls + 120) * limit),
                    ),
                )
            st.rerun()


RELEASE_RESTORE_PRESETS: dict[str, list[str]] = {
    "Custom (pick areas below)": [],
    "Render output only (vault + graph)": ["render_graph", "render_manifest", "wiki"],
    "Synthesis + render downstream": ["synthesis_cache", "render_graph", "render_manifest", "wiki"],
    "Reviews and everything downstream": [
        "reviews",
        "synthesis_cache",
        "render_graph",
        "render_manifest",
        "wiki",
    ],
    "Full knowledge release (all areas)": list(RELEASE_MANIFEST_AREA_KEYS),
}


def render_release_operations(
    st: Any,
    *,
    repo_root: Path,
    paths_config: Path | None,
) -> None:
    """Render release manifest + restore controls."""
    config_args = _paths_config_args(paths_config)
    checkpoint_kinds = ["release", "pre_ingest", "pre_review", "pre_synthesis", "pre_render"]
    with st.container(border=True):
        st.subheader("Releases and restore")
        st.caption("Safety net — checkpoint before risky work, restore if something went wrong.")
        with st.expander("Plain-language guide (read this first)", expanded=False):
            st.markdown(
                """
A **release manifest** is a small JSON file that fingerprints your knowledge store
at one moment: reviews, synthesis cache, render graph, wiki hashes, code commit,
and (optionally) a backup snapshot id.

**Normal workflow (before synthesis batch or mass render)**

1. **Outside this dashboard:** take a filesystem snapshot of `llm-wiki-data` and the vault
   (restic, rsync copy, Time Machine, etc.). Note the snapshot id or folder path.
2. **Here:** write a release manifest and paste the snapshot id
   (e.g. `restic:abc123` or a folder label).
3. Run your risky operation (synthesis batch, render, ingest).
4. If happy: optionally write another manifest labeled `release`.

**If something went wrong**

1. Restore **dry-run** first — shows which folders would be overwritten.
2. If the plan looks right: uncheck dry-run, confirm overwrite, run restore for real.
3. Read the verify section in the output. **ok** means you are back to a consistent state.

**Important limits**

- Restore needs a manifest that records a **snapshot id** and a **snapshot root** folder on disk.
- Restore replaces files; it does not magically undo Git commits in the vault repo.
- For “wrong render only” when the knowledge store did not change, vault Git checkout may be faster.
                """
            )

        with st.form("ops_release_manifest_form"):
            st.markdown("**A. Write a checkpoint manifest**")
            st.caption("Creates one JSON file under `state/releases/` in the knowledge store.")
            release_id = st.text_input(
                "Release id (optional)",
                value="",
                placeholder="YYYYMMDDTHHMMSSZ — leave empty to auto-generate",
                help=(
                    "Only set this if you want a fixed filename. "
                    "Otherwise a timestamp is generated."
                ),
            ).strip()
            snapshot_id = st.text_input(
                "Snapshot id",
                value="",
                placeholder="restic:deadbeef or copy-2026-07-14",
                help=(
                    "Label that links this manifest to your external backup. "
                    "Restore is blocked without this field."
                ),
            ).strip()
            checkpoint_kind = st.selectbox(
                "Checkpoint kind",
                options=checkpoint_kinds,
                index=0,
                help=(
                    "Tag why you created this checkpoint. Use pre_synthesis / pre_render "
                    "before those operations so you can find the right manifest later."
                ),
            )
            with st.expander("What do preview vs write mean?"):
                st.markdown(
                    """
- **Preview (dry-run text)** — human-readable summary; writes nothing.
- **Preview as JSON** — same data as JSON; writes nothing. Good for copying into notes.
- **Write release manifest** — creates the file on disk. Requires the confirmation checkbox.

**Checkpoint kind hints**

| Kind | Use when |
|------|----------|
| `release` | You finished a good state and want a long-term anchor |
| `pre_ingest` | Before Readwise sync or big raw import |
| `pre_review` | Before bulk review edits |
| `pre_synthesis` | Before “Run synthesis batch” |
| `pre_render` | Before “Render wiki” |
                    """
                )
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                submit_preview = st.form_submit_button(
                    "Preview (dry-run text)",
                    type="secondary",
                    use_container_width=False,
                )
            with col_b:
                submit_json = st.form_submit_button(
                    "Preview as JSON",
                    type="secondary",
                    use_container_width=False,
                )
            with col_c:
                confirm_write = st.checkbox(
                    "I understand this writes a file",
                    value=False,
                    help="Required to write a release manifest file.",
                )
                submit_write = st.form_submit_button(
                    "Write release manifest",
                    type="primary",
                    use_container_width=False,
                    disabled=not confirm_write,
                )

        if submit_preview or submit_json or submit_write:
            args: list[str] = []
            if submit_preview:
                args.append("--release-dry-run")
            if submit_json:
                args.append("--release-json")
            if submit_write:
                args.extend(["--write-release-manifest", "--yes"])
            if release_id:
                args.extend(["--release-id", release_id])
            if snapshot_id:
                args.extend(["--snapshot-id", snapshot_id])
            args.extend(["--checkpoint-kind", checkpoint_kind])
            _store_result(
                st,
                run_dashboard_command(
                    label="Release manifest",
                    command=_python_command("src.wiki_ops.status_cli", *config_args, *args),
                    cwd=repo_root,
                ),
            )
            st.rerun()

        st.divider()

        with st.form("ops_release_restore_form"):
            st.markdown("**B. Restore from a snapshot**")
            st.caption("Replaces selected folders from a backup copy on disk.")
            selector = (
                st.text_input(
                    "Release selector",
                    value="latest",
                    help="'latest' uses the newest manifest file, or paste a specific release id.",
                ).strip()
                or "latest"
            )
            snapshot_root = st.text_input(
                "Snapshot root path",
                value="",
                placeholder="/path/to/parent-folder-containing-both-data-and-vault",
                help=(
                    "Folder that contains the same relative paths as today, e.g. "
                    "llm-wiki-data/ and llm-wiki-vault-private/ as siblings."
                ),
            ).strip()
            preset = st.selectbox(
                "Restore preset",
                options=list(RELEASE_RESTORE_PRESETS.keys()),
                index=0,
                help="Quick picks for common rollback scenarios. Custom lets you choose areas.",
            )
            preset_areas = RELEASE_RESTORE_PRESETS[preset]
            if preset_areas:
                st.caption(f"Preset areas: {', '.join(preset_areas)}")
                areas = preset_areas
            else:
                areas = st.multiselect(
                    "Areas to restore",
                    options=list(RELEASE_MANIFEST_AREA_KEYS),
                    default=["render_graph", "render_manifest", "wiki"],
                    help=(
                        "raw_readwise = original exports; reviews = review JSON; "
                        "synthesis_cache = Stage 2 text; render_graph/manifest = render state; "
                        "wiki = generated vault pages."
                    ),
                )
            with st.expander("What do the restore options mean?"):
                st.markdown(
                    """
**Snapshot root path**

Point at the parent directory of your backup trees. The restore maps paths relative to the
common parent of knowledge store + vault. Example layout:

```
/snapshots/2026-07-14/
  llm-wiki-data/...
  llm-wiki-vault-private/...
```

**Areas (if picking manually)**

- `render_graph` / `render_manifest` / `wiki` — typical “bad render” rollback when reviews unchanged
- `synthesis_cache` — undo a synthesis batch (then re-render)
- `reviews` — undo review edits (also restore downstream areas or re-run pipeline)
- `raw_readwise` — only for ingest problems; usually use full preset instead

**Dry-run** — always try this first. Shows the plan only.

**Allow path mismatch during verify** — only if you restored to different absolute paths
but same content.

**Output as JSON** — machine-readable plan plus verify report.
                    """
                )
            dry_run = st.checkbox(
                "Dry-run (plan only)",
                value=True,
                help="Recommended first. No files are changed.",
            )
            allow_path_mismatch = st.checkbox(
                "Allow path mismatch during verify",
                value=False,
                help="Rare. Use when paths moved but content should still match the manifest.",
            )
            col_l, col_r = st.columns(2)
            with col_l:
                output_json = st.checkbox("Output as JSON", value=False)
            with col_r:
                confirm_restore = st.checkbox(
                    "I understand this overwrites files",
                    value=False,
                    disabled=dry_run,
                    help="Required for a real restore. Not needed for dry-run.",
                )
            run_restore = st.form_submit_button(
                "Run restore",
                type="primary",
                disabled=(not dry_run and not confirm_restore),
            )

        if run_restore:
            if not snapshot_root:
                st.error("Snapshot root path is required.", icon=":material/error:")
            elif not areas:
                st.error("Select at least one area to restore.", icon=":material/error:")
            else:
                args = [
                    "--restore-release",
                    selector,
                    "--restore-snapshot-root",
                    snapshot_root,
                    "--restore-areas",
                    ",".join(areas),
                ]
                if dry_run:
                    args.append("--restore-dry-run")
                else:
                    args.extend(["--yes"])
                if output_json:
                    args.append("--restore-json")
                if allow_path_mismatch:
                    args.append("--verify-allow-path-mismatch")
                _store_result(
                    st,
                    run_dashboard_command(
                        label="Release restore",
                        command=_python_command("src.wiki_ops.status_cli", *config_args, *args),
                        cwd=repo_root,
                        timeout_seconds=600,
                    ),
                )
                st.rerun()


def render_operations_page(
    st: Any,
    *,
    repo_root: Path,
    paths: WikiPaths,
    paths_config: Path | None,
) -> None:
    """Render the temporary operations dashboard."""
    st.title("LLM Wiki — operations")
    st.caption(
        "Temporary command center for CLI workflows. Buttons run real commands on your machine."
    )
    _render_operations_overview(st)
    col_left, col_right = st.columns(2)
    with col_left:
        render_readwise_operations(st, repo_root=repo_root, paths=paths)
        render_render_and_lint_operations(
            st,
            repo_root=repo_root,
            paths_config=paths_config,
        )
    with col_right:
        render_synthesis_operations(
            st,
            repo_root=repo_root,
            paths_config=paths_config,
        )
        render_release_operations(
            st,
            repo_root=repo_root,
            paths_config=paths_config,
        )

    result = st.session_state.get("_ops_last_result")
    if isinstance(result, DashboardCommandResult):
        with st.container(border=True):
            st.subheader("Latest command output")
            st.caption(
                "The most recent button you clicked. Scroll up to run another command; "
                "this box updates on each run."
            )
            render_command_result(st, result)
