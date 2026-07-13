"""Dashboard controls for unattended ingest pre-analysis."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def latest_preanalyze_log(log_dir: Path) -> Path | None:
    """Return the newest pre-analysis log file, if any."""
    if not log_dir.is_dir():
        return None
    logs = sorted(log_dir.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def read_log_tail(path: Path, *, max_lines: int = 20) -> str:
    """Return the last ``max_lines`` of a UTF-8 log file."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"Could not read log: {exc}"
    return "\n".join(lines[-max_lines:])


def start_preanalyze_process(
    *,
    repo_root: Path,
    raw_dir: Path,
    reviews_root: Path,
    wiki_root: Path,
    model: str,
    prompt_version: str,
    limit: int,
    between_articles_seconds: float,
    log_dir: Path,
    paths_config: Path | None = None,
) -> Path:
    """Start ``ingest-preanalyze`` detached and return the log path."""
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"preanalyze-{stamp}.log"
    command = [
        sys.executable,
        "-m",
        "src.ingest_batch.cli",
        "--limit",
        str(limit),
        "--model",
        model,
        "--prompt-version",
        prompt_version,
        "--between-articles",
        str(between_articles_seconds),
        "--raw-dir",
        str(raw_dir),
        "--reviews-dir",
        str(reviews_root),
        "--wiki-root",
        str(wiki_root),
    ]
    if paths_config is not None:
        command.extend(["--paths-config", str(paths_config)])
    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"$ {' '.join(command)}\n")
        log_file.flush()
        subprocess.Popen(  # noqa: S603
            command,
            cwd=repo_root,
            env=os.environ.copy(),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return log_path


def render_preanalyze_sidebar(
    st: Any,
    *,
    repo_root: Path,
    raw_dir: Path,
    reviews_root: Path,
    wiki_root: Path,
    model: str,
    prompt_version: str,
    paths_config: Path | None = None,
) -> None:
    """Render dashboard controls for pre-analyzing pending sources."""
    st.subheader("Pre-analysis")
    st.caption("Runs pending sources through the normal analysis path in the background.")
    limit = int(
        st.number_input(
            "Reviews vorab analysieren (Anzahl)",
            min_value=1,
            value=50,
            step=10,
            key="preanalyze_limit",
        )
    )
    between_articles_seconds = float(
        st.number_input(
            "Pause zwischen Artikeln (Sekunden)",
            min_value=0,
            value=0,
            step=100,
            key="preanalyze_between_articles_seconds",
            help=(
                "Wartezeit zwischen zwei OpenAI-Analysen. "
                "Für langsame Nachtläufe z. B. 2000 Sekunden verwenden."
            ),
        )
    )
    log_dir = repo_root / "state" / "ingest_batches"
    if st.button(
        "Vorab-Analyse starten",
        key="preanalyze_start_button",
        width="stretch",
    ):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY is not set.")
        else:
            try:
                log_path = start_preanalyze_process(
                    repo_root=repo_root,
                    raw_dir=raw_dir,
                    reviews_root=reviews_root,
                    wiki_root=wiki_root,
                    model=model,
                    prompt_version=prompt_version,
                    limit=limit,
                    between_articles_seconds=between_articles_seconds,
                    log_dir=log_dir,
                    paths_config=paths_config,
                )
            except OSError as exc:
                st.error(f"Could not start pre-analysis: {exc}")
            else:
                st.success(f"Pre-analysis started. Log: `{log_path}`")

    latest = latest_preanalyze_log(log_dir)
    if latest is None:
        st.caption("No pre-analysis log yet.")
        return
    st.caption(f"Latest log: `{latest.name}`")
    if st.button("Vorab-Analyse Status aktualisieren", key="preanalyze_refresh_button"):
        st.rerun()
    with st.expander("Latest pre-analysis log"):
        st.code(read_log_tail(latest), language="text")
