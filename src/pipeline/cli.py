"""CLI for source discovery, parsing, and state management."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

from src.pipeline.auth import MediumAuthConfig
from src.pipeline.config import find_source_by_name, load_sources
from src.pipeline.discovery.medium import discover_medium_items_with_options
from src.pipeline.models import DiscoveredItem
from src.pipeline.parser.medium_parser import parse_medium_item
from src.pipeline.staging import stage_document
from src.pipeline.state_store import SourceStateStore, canonicalize_url

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "state" / "sources_config.json"
DEFAULT_STATE = ROOT / "state" / "sources_seen.json"
DEFAULT_STAGING = ROOT / "raw" / "staged"


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level CLI parser."""
    parser = argparse.ArgumentParser(prog="pipeline", description="Source parsing pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Discover new items without parsing")
    check.add_argument("source_name")
    check.add_argument("--limit", type=int, default=10)
    check.add_argument("--window-start-days", type=int, default=5)
    check.add_argument("--window-end-days", type=int, default=2)
    check.add_argument("--use-browser", action="store_true")
    check.add_argument(
        "--max-scrolls",
        type=int,
        default=150,
        help="Safety cap on scroll iterations (browser mode); window coverage stops earlier when "
        "the archive reaches content older than your date window.",
    )
    check.add_argument("--medium-cookie-file", type=Path)
    check.add_argument("--medium-storage-state", type=Path)
    check.add_argument("--medium-user-data-dir", type=Path)

    pull = subparsers.add_parser("pull", help="Discover, parse, and stage new items")
    pull.add_argument("source_name")
    pull.add_argument("--limit", type=int, default=3)
    pull.add_argument("--window-start-days", type=int, default=5)
    pull.add_argument("--window-end-days", type=int, default=2)
    pull.add_argument("--use-browser", action="store_true")
    pull.add_argument(
        "--max-scrolls",
        type=int,
        default=150,
        help="Safety cap on scroll iterations (browser mode); window coverage stops earlier when "
        "the archive reaches content older than your date window.",
    )
    pull.add_argument("--medium-cookie-file", type=Path)
    pull.add_argument("--medium-storage-state", type=Path)
    pull.add_argument("--medium-user-data-dir", type=Path)

    mark = subparsers.add_parser("mark", help="Mark an item status")
    mark.add_argument("source_name")
    mark.add_argument("item_id")
    mark.add_argument("--status", choices=["ignored", "ingested", "parsed"], required=True)

    auth_login = subparsers.add_parser(
        "auth-login",
        help="Open Medium login and save Playwright storage state",
    )
    auth_login.add_argument(
        "--output",
        type=Path,
        default=ROOT / "state" / "medium.storage_state.json",
        help="Path to write Playwright storage state JSON.",
    )
    auth_login.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Seconds to wait for manual Medium sign-in before failing.",
    )

    return parser


def discover_new_items(
    source_name: str,
    limit: int,
    window_start_days: int = 5,
    window_end_days: int = 2,
    *,
    use_browser: bool = False,
    max_scrolls: int = 150,
    auth: MediumAuthConfig | None = None,
) -> list[DiscoveredItem]:
    """Discover unseen items for a configured source."""
    if use_browser and window_start_days < window_end_days:
        raise ValueError("window_start_days must be greater than or equal to window_end_days.")
    sources = load_sources(DEFAULT_CONFIG)
    source = find_source_by_name(sources, source_name)
    if source.kind != "medium":
        raise ValueError(f"Unsupported source kind: {source.kind}")
    discovered = discover_medium_items_with_options(
        source=source,
        limit=None,
        use_browser=use_browser,
        max_scrolls=max_scrolls,
        auth=auth,
        archive_window_start_days=window_start_days if use_browser else None,
        archive_window_end_days=window_end_days if use_browser else None,
    )
    state = SourceStateStore(DEFAULT_STATE)
    unseen = [item for item in discovered if not state.is_seen(source_name, item.item_id)]
    in_window = [
        item
        for item in unseen
        if _is_in_target_window(
            published_at=item.published_at,
            window_start_days=window_start_days,
            window_end_days=window_end_days,
        )
    ]
    return in_window[:limit]


def _is_in_target_window(
    published_at: str | None, window_start_days: int = 5, window_end_days: int = 2
) -> bool:
    """Return whether published date is inside [today-start_days, today-end_days]."""
    if published_at is None:
        return False
    if window_start_days < window_end_days:
        raise ValueError("window_start_days must be greater than or equal to window_end_days.")
    if window_end_days < 0:
        raise ValueError("window_end_days must be non-negative.")
    try:
        published_dt = parsedate_to_datetime(published_at)
    except (TypeError, ValueError):
        try:
            published_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        except ValueError:
            return False
    if published_dt.tzinfo is None:
        published_dt = published_dt.replace(tzinfo=UTC)
    published_date = published_dt.astimezone(UTC).date()
    today = datetime.now(tz=UTC).date()
    window_start = today - timedelta(days=window_start_days)
    window_end = today - timedelta(days=window_end_days)
    return window_start <= published_date <= window_end


def run_check(
    source_name: str,
    limit: int,
    window_start_days: int,
    window_end_days: int,
    *,
    use_browser: bool,
    max_scrolls: int,
    auth: MediumAuthConfig | None,
) -> int:
    """Run discovery-only check command."""
    new_items = discover_new_items(
        source_name=source_name,
        limit=limit,
        window_start_days=window_start_days,
        window_end_days=window_end_days,
        use_browser=use_browser,
        max_scrolls=max_scrolls,
        auth=auth,
    )
    print(f"New items for '{source_name}': {len(new_items)}")
    for item in new_items:
        print(f"- {item.item_id} | {item.title} | {item.url}")
    return 0


def run_pull(
    source_name: str,
    limit: int,
    window_start_days: int,
    window_end_days: int,
    *,
    use_browser: bool,
    max_scrolls: int,
    auth: MediumAuthConfig | None,
) -> int:
    """Run discovery + parse + staging command."""
    new_items = discover_new_items(
        source_name=source_name,
        limit=limit,
        window_start_days=window_start_days,
        window_end_days=window_end_days,
        use_browser=use_browser,
        max_scrolls=max_scrolls,
        auth=auth,
    )
    state = SourceStateStore(DEFAULT_STATE)
    for item in new_items:
        parsed = parse_medium_item(item, auth=auth)
        path = stage_document(parsed=parsed, staging_dir=DEFAULT_STAGING)
        state.upsert_item(
            source_name=source_name,
            item_id=item.item_id,
            title=item.title,
            canonical_url=canonicalize_url(parsed.canonical_url),
            published_at=item.published_at,
            local_path=str(path),
            status="parsed",
        )
        print(f"Staged: {path}")
    print(f"Completed. Newly staged: {len(new_items)}")
    return 0


def run_mark(source_name: str, item_id: str, status: str) -> int:
    """Update status for an already-seen item."""
    store = SourceStateStore(DEFAULT_STATE)
    state = store.load()
    source_items = state.get(source_name, {})
    if item_id not in source_items:
        raise ValueError(f"Unknown item_id '{item_id}' for source '{source_name}'.")
    item = source_items[item_id]
    store.upsert_item(
        source_name=source_name,
        item_id=item.item_id,
        title=item.title,
        canonical_url=item.canonical_url,
        published_at=item.published_at,
        local_path=item.local_path,
        status=status,
    )
    print(f"Updated {item_id} -> {status}")
    return 0


def run_auth_login(output: Path, timeout_seconds: int) -> int:
    """Open interactive Medium login and persist Playwright auth state."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required. Install dependencies and run "
            "`hatch run playwright install chromium`."
        ) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    print(
        "Opening Medium login. Complete sign-in in the browser window. "
        "The command saves auth state after successful login."
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://medium.com/m/signin", wait_until="domcontentloaded", timeout=30000)
        deadline = datetime.now(tz=UTC).timestamp() + timeout_seconds
        has_sid = False
        while datetime.now(tz=UTC).timestamp() < deadline:
            cookies = context.cookies(["https://medium.com"])
            has_sid = any(cookie.get("name") == "sid" for cookie in cookies)
            if has_sid:
                break
            page.wait_for_timeout(1000)
        if not has_sid:
            browser.close()
            raise RuntimeError(
                f"Login timed out after {timeout_seconds}s. "
                "Re-run `pipeline auth-login` and complete sign-in."
            )
        context.storage_state(path=str(output))
        browser.close()
    print(f"Saved Medium auth storage state: {output}")
    return 0


def main() -> int:
    """Entry point for CLI execution."""
    parser = build_parser()
    args = parser.parse_args()
    auth = MediumAuthConfig(
        cookie_file=getattr(args, "medium_cookie_file", None),
        storage_state=getattr(args, "medium_storage_state", None),
        user_data_dir=getattr(args, "medium_user_data_dir", None),
    )
    if args.command == "check":
        return run_check(
            source_name=args.source_name,
            limit=args.limit,
            window_start_days=args.window_start_days,
            window_end_days=args.window_end_days,
            use_browser=args.use_browser,
            max_scrolls=args.max_scrolls,
            auth=auth,
        )
    if args.command == "pull":
        return run_pull(
            source_name=args.source_name,
            limit=args.limit,
            window_start_days=args.window_start_days,
            window_end_days=args.window_end_days,
            use_browser=args.use_browser,
            max_scrolls=args.max_scrolls,
            auth=auth,
        )
    if args.command == "mark":
        return run_mark(source_name=args.source_name, item_id=args.item_id, status=args.status)
    if args.command == "auth-login":
        return run_auth_login(output=args.output, timeout_seconds=args.timeout_seconds)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
