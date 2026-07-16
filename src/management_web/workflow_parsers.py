"""Readable summary parsers for management web pipeline workflow outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_synthesis_select_json(payload: dict[str, Any]) -> list[str]:
    """Turn synthesis select JSON into human-readable summary lines."""
    total = int(payload.get("total_changed") or payload.get("total") or 0)
    shown = int(payload.get("shown") or 0)
    entries_raw = payload.get("entries")
    if isinstance(entries_raw, list):
        entries: list[Any] = entries_raw
    else:
        items_raw = payload.get("items")
        entries = items_raw if isinstance(items_raw, list) else []
    lines = [f"{total} candidates found · {shown} selected for this run"]
    for index, raw_entry in enumerate(entries[:5], start=1):
        if not isinstance(raw_entry, dict):
            continue
        title = str(raw_entry.get("title") or raw_entry.get("entity_id") or "Unknown")
        category = str(raw_entry.get("category") or "entity")
        source_count = raw_entry.get("source_count")
        state = str(raw_entry.get("state") or "changed")
        score = raw_entry.get("score")
        source_label = f"{source_count} sources" if source_count is not None else "sources unknown"
        score_label = f" · score {score}" if score is not None else ""
        lines.append(f"{index}. {title} · {category} · {source_label} · {state}{score_label}")
    return lines


def parse_synthesis_batch_json(payload: dict[str, Any]) -> list[str]:
    """Turn synthesis batch JSON into human-readable summary lines."""
    selected = payload.get("selected", "—")
    attempted = payload.get("attempted", "—")
    written = payload.get("written", "—")
    failed = payload.get("failed", "—")
    dry_run = payload.get("dry_run")
    prefix = "Synthesis batch planned" if dry_run else "Synthesis batch completed"
    return [
        prefix,
        f"{selected} selected · {attempted} attempted · {written} written · {failed} failed",
    ]


def parse_batch_progress_message(message: str) -> dict[str, Any] | None:
    """Turn one synthesis batch progress line into UI-friendly progress fields."""
    processing = re.match(
        r"^processing (?P<entity>\S+) index=(?P<current>\d+) total=(?P<total>\d+)$",
        message,
    )
    if processing:
        current = int(processing.group("current"))
        total = int(processing.group("total"))
        entity = processing.group("entity")
        return {
            "current": current,
            "total": total,
            "display_message": f"Synthesizing {entity} ({current}/{total})",
        }
    waiting = re.match(
        r"^waiting (?P<entity>\S+) index=(?P<current>\d+) total=(?P<total>\d+) "
        r"seconds=(?P<seconds>[\d.]+)(?: remaining=(?P<remaining>\d+))?$",
        message,
    )
    if waiting:
        current = int(waiting.group("current"))
        total = int(waiting.group("total"))
        entity = waiting.group("entity")
        remaining = waiting.group("remaining")
        if remaining:
            display = (
                f"Waiting {remaining}s before next synthesis "
                f"({current}/{total} done, after {entity})"
            )
        else:
            seconds = int(float(waiting.group("seconds")))
            display = (
                f"Waiting {seconds}s before next synthesis ({current}/{total} done, after {entity})"
            )
        return {
            "current": current,
            "total": total,
            "display_message": display,
        }
    return None


def parse_render_summary_text(text: str) -> list[str]:
    """Parse wiki-render stdout into concise summary lines."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ["Render completed"]
    dry_run = any("dry-run" in line.lower() for line in lines[:3])
    prefix = "Render preview completed" if dry_run else "Render written"
    output_files = _first_int_match(text, r"output files:\s*(\d+)")
    would_write = _first_int_match(text, r"would write:\s*(\d+)")
    written = _first_int_match(text, r"written:\s*(\d+)")
    unchanged = _first_int_match(text, r"unchanged:\s*(\d+)")
    would_prune = _first_int_match(text, r"would prune:\s*(\d+)")
    pruned = _first_int_match(text, r"pruned:\s*(\d+)")
    coverage = _first_regex_match(
        text,
        r"(\d+) of (\d+) source pages (?:would include|include) embedded raw text",
    )
    summary_bits: list[str] = []
    if output_files is not None:
        summary_bits.append(f"{output_files} output files")
    if dry_run:
        if would_write is not None:
            summary_bits.append(f"{would_write} would write")
        if unchanged is not None:
            summary_bits.append(f"{unchanged} unchanged")
        if would_prune is not None:
            summary_bits.append(f"{would_prune} would prune")
    else:
        if written is not None:
            summary_bits.append(f"{written} files written")
        if unchanged is not None:
            summary_bits.append(f"{unchanged} unchanged")
        if pruned is not None:
            summary_bits.append(f"{pruned} pruned")
    if coverage:
        summary_bits.append(f"{coverage[0]}/{coverage[1]} source pages include raw text")
    if summary_bits:
        return [prefix, " · ".join(summary_bits)]
    return [prefix, lines[0]]


def parse_wiki_lint_output(text: str) -> list[str]:
    """Parse wiki-lint stdout into concise summary lines."""
    safe_delete = _first_int_match(text, r"safe delete candidates:\s*(\d+)")
    duplicate_groups = _first_int_match(text, r"exact duplicate groups:\s*(\d+)")
    manual_review = _first_int_match(text, r"manual review items:\s*(\d+)")
    contract_issues = _first_int_match(text, r"wiki-lint:\s*(\d+)\s+contract issue")
    lines = ["Wiki health check completed"]
    if safe_delete is not None or duplicate_groups is not None or manual_review is not None:
        lines.append(
            f"{safe_delete or 0} safe delete candidates · "
            f"{duplicate_groups or 0} duplicate groups · "
            f"{manual_review or 0} manual review items"
        )
    elif contract_issues is not None:
        lines.append(f"{contract_issues} contract issue(s)")
    warning_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("WARNING") or line.strip().startswith("warning")
    ]
    lines.extend(warning_lines[:3])
    return lines


def loads_json_object(text: str) -> dict[str, Any] | None:
    """Return the first JSON object found in command stdout."""
    trimmed = text.strip()
    if not trimmed:
        return None
    if trimmed.startswith("{"):
        try:
            parsed = json.loads(trimmed)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    for line in reversed(trimmed.splitlines()):
        candidate = line.strip()
        if candidate.startswith("{"):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def render_changes_pending(text: str) -> bool:
    """Return whether a render dry-run reports files to write or prune."""
    would_write = _first_int_match(text, r"would write:\s*(\d+)")
    would_prune = _first_int_match(text, r"would prune:\s*(\d+)")
    return bool(would_write or would_prune)


def _first_int_match(text: str, pattern: str) -> int | None:
    """Return the first integer captured by a regex pattern."""
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    try:
        return int(match.group(1))
    except (TypeError, ValueError):
        return None


def _first_regex_match(text: str, pattern: str) -> tuple[str, str] | None:
    """Return the first regex match groups as strings."""
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1), match.group(2)
