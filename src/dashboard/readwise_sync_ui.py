"""Dashboard controls for syncing Readwise Reader exports into ``raw/readwise/``."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.readwise.sync import SyncResult, run_sync


class ReadwiseSyncConfigurationError(ValueError):
    """Raised when Readwise sync cannot run due to missing configuration."""


def readwise_token_from_env() -> str | None:
    """Return the Readwise API token from the environment, if configured."""
    for key in ("READWISE_TOKEN", "READWISE_API_TOKEN"):
        value = os.environ.get(key)
        if value and value.strip():
            return value.strip()
    return None


def format_sync_summary(result: SyncResult) -> str:
    """Build a user-facing summary line after a sync run."""
    mode = "Dry run" if result.dry_run else "Sync complete"
    summary = (
        f"{mode}: examined **{result.examined}**, exported **{result.exported}**, "
        f"skipped **{result.skipped}**."
    )
    if result.examined == 0 and result.incremental_filter_active:
        watermark = result.incremental_watermark or "(unknown)"
        summary += (
            " Reader returned no archive items tagged **processed** after the current "
            f"watermark (`{watermark}`). Tag and archive items in Reader, or enable "
            "**Reset watermark** for a ~100-day lookback."
        )
    return summary


def try_readwise_sync(
    *,
    repo_root: Path,
    output_dir: Path,
    index_path: Path | None = None,
    prune_missing: bool = False,
    reset_watermark: bool = False,
) -> tuple[SyncResult | None, str | None]:
    """Run Readwise sync; return ``(result, None)`` or ``(None, error_message)``."""
    token = readwise_token_from_env()
    if not token:
        return (
            None,
            "Missing **READWISE_TOKEN** (or **READWISE_API_TOKEN**). "
            "Add it to `.env` at the repo root or export it in your shell. "
            "Get a token at https://readwise.io/access_token",
        )
    try:
        result = run_sync(
            token,
            index_path=index_path or (repo_root / "state" / "readwise_library.json"),
            output_dir=output_dir,
            repo_root=repo_root,
            dry_run=False,
            prune_missing=prune_missing,
            reset_watermark=reset_watermark,
        )
    except Exception as exc:  # noqa: BLE001
        return None, f"Readwise sync failed: {exc}"
    return result, None


def render_readwise_sync_sidebar(
    st: Any,
    *,
    repo_root: Path,
    output_dir: Path,
    index_path: Path | None = None,
) -> None:
    """Render Readwise sync controls in the dashboard sidebar."""
    st.subheader("Readwise")
    has_token = readwise_token_from_env() is not None
    st.caption(
        "Token: **loaded** from environment or `.env`."
        if has_token
        else "Token: **not set** — required for sync."
    )
    st.caption(
        "Imports Reader **Archive** items tagged **processed** into the raw directory "
        "as paired `.html` + `.md` files."
    )
    prune_missing = st.checkbox(
        "Re-export missing files",
        value=False,
        key="readwise_sync_prune_missing",
        help="Re-download when indexed export files are missing from disk.",
    )
    reset_watermark = st.checkbox(
        "Reset watermark",
        value=False,
        key="readwise_sync_reset_watermark",
        help="Ignore saved sync watermark and use the ~100-day default lookback.",
    )
    if st.button(
        "Sync from Readwise",
        key="readwise_sync_button",
        width="stretch",
        type="primary",
    ):
        with st.spinner("Syncing from Readwise Reader…"):
            result, error = try_readwise_sync(
                repo_root=repo_root,
                output_dir=output_dir,
                index_path=index_path,
                prune_missing=prune_missing,
                reset_watermark=reset_watermark,
            )
        if error:
            st.error(error)
        elif result is not None:
            st.session_state["_readwise_sync_flash"] = format_sync_summary(result)
            st.rerun()
