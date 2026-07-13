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
) -> None:
    """Render a button that runs a command and stores the result."""
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


def render_readwise_operations(
    st: Any,
    *,
    repo_root: Path,
    paths: WikiPaths,
) -> None:
    """Render Readwise sync and raw export controls."""
    with st.container(border=True):
        st.subheader("Readwise export")
        st.caption("Fetches Reader archive items tagged processed into the configured raw folder.")
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
        st.caption("Dry-run first when you are unsure. Real render writes to the private vault.")
        _render_button_command(
            st,
            label="Ops status",
            key="ops_status_button",
            command=_python_command("src.wiki_ops.status_cli", *config_args),
            repo_root=repo_root,
        )
        _render_button_command(
            st,
            label="Render dry-run",
            key="ops_render_dry_run_button",
            command=_python_command(
                "src.wiki_render",
                *config_args,
                "--dry-run",
                "--require-source-text",
            ),
            repo_root=repo_root,
        )
        _render_button_command(
            st,
            label="Render wiki",
            key="ops_render_button",
            command=_python_command("src.wiki_render", *config_args, "--require-source-text"),
            repo_root=repo_root,
            button_type="primary",
        )
        _render_button_command(
            st,
            label="Wiki lint",
            key="ops_wiki_lint_button",
            command=_python_command("src.wiki_lint", *config_args),
            repo_root=repo_root,
        )
        _render_button_command(
            st,
            label="Synthesis cache lint",
            key="ops_synthesis_cache_lint_button",
            command=_python_command("src.wiki_synthesis.cache_lint_cli", *config_args),
            repo_root=repo_root,
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
        st.caption("Plan and batch-run Stage 2 syntheses. Real batches call the OpenAI API.")
        limit = int(
            st.number_input(
                "Limit",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                key="ops_synthesis_limit",
            )
        )
        category = st.selectbox("Category", categories, key="ops_synthesis_category")
        category_args = [] if category == "all" else ["--category", category]

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
        )
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
        )
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
        )
        allow_real_batch = st.checkbox(
            "Allow real synthesis batch",
            value=False,
            key="ops_allow_real_synthesis_batch",
            help="Real synthesis sends local synthesis contexts to the OpenAI API.",
        )
        between_calls = int(
            st.number_input(
                "Seconds between calls",
                min_value=0,
                max_value=3600,
                value=10,
                step=10,
                key="ops_synthesis_between_calls",
            )
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


def render_operations_page(
    st: Any,
    *,
    repo_root: Path,
    paths: WikiPaths,
    paths_config: Path | None,
) -> None:
    """Render the temporary operations dashboard."""
    st.title("LLM Wiki — operations")
    st.caption("Temporary command center for the current CLI workflows.")
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

    result = st.session_state.get("_ops_last_result")
    if isinstance(result, DashboardCommandResult):
        with st.container(border=True):
            st.subheader("Latest command output")
            render_command_result(st, result)
