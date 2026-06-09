"""CLI for importing Medium Reading List articles into Readwise via Brave."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from time import monotonic

from playwright.async_api import async_playwright

from src.ingest_review.paths import load_repo_dotenv
from src.medium_to_readwise.browser import connect_over_cdp
from src.medium_to_readwise.collect import collect_reading_list_urls
from src.medium_to_readwise.human_guard import (
    HourlyRateLimiter,
    HumanVerificationRequired,
    RateLimitReached,
    ensure_no_human_verification,
    sleep_with_jitter,
)
from src.medium_to_readwise.process import process_article_with_retries
from src.medium_to_readwise.progress import format_progress_line
from src.medium_to_readwise.shortcut import (
    DEFAULT_BROWSER_APP_NAME,
    DEFAULT_READWISE_SHORTCUT,
    default_shortcut_mode,
)
from src.medium_to_readwise.state import (
    append_run_log,
    default_state_dir,
    ensure_state_dir,
    load_article_state,
    merge_article_urls,
    pending_urls,
    processed_entries,
    save_article_state,
    save_processed_entries,
    upsert_processed_entry,
)

DEFAULT_CDP_URL = "http://127.0.0.1:9222"
FALLBACK_READING_LIST_URL = "https://medium.com/list/reading-list"


def default_reading_list_url() -> str:
    """Return the configured Reading List URL from env or the generic fallback."""
    return os.environ.get("MEDIUM_READING_LIST_URL", FALLBACK_READING_LIST_URL)


def build_parser() -> argparse.ArgumentParser:
    """Construct the ``medium-to-readwise`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="medium-to-readwise",
        description="Save Medium Reading List articles to Readwise through Brave automation.",
    )
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help="Brave CDP endpoint URL.")
    parser.add_argument(
        "--reading-list-url",
        default=default_reading_list_url(),
        help=(
            "Medium Reading List URL to harvest "
            "(default: MEDIUM_READING_LIST_URL env or generic /list/reading-list)."
        ),
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=default_state_dir(),
        help="Directory for articles.json, processed.json, run.log, and screenshots.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Collect and print plan only.")
    parser.add_argument(
        "--limit", type=int, default=None, help="Maximum pending articles to process."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds to wait after triggering the Readwise shortcut.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Retries per article after the first attempt.",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=5.0,
        help="Seconds to wait between retries.",
    )
    parser.add_argument(
        "--refresh-articles",
        action="store_true",
        help="Re-harvest the Reading List before processing.",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Harvest URLs and exit without processing articles.",
    )
    parser.add_argument(
        "--no-retry-failed",
        dest="retry_failed",
        action="store_false",
        default=True,
        help="Skip URLs previously marked as failed.",
    )
    parser.add_argument(
        "--scroll-delay",
        type=float,
        default=1.0,
        help="Seconds to wait after each Reading List scroll.",
    )
    parser.add_argument(
        "--readwise-shortcut",
        default=os.environ.get("READWISE_SAVE_SHORTCUT", DEFAULT_READWISE_SHORTCUT),
        help="Readwise save shortcut (default: READWISE_SAVE_SHORTCUT or Alt+KeyR / Option+R).",
    )
    parser.add_argument(
        "--shortcut-mode",
        choices=("system", "playwright"),
        default=os.environ.get("READWISE_SHORTCUT_MODE", default_shortcut_mode()),
        help=(
            "How to send the shortcut. Use 'system' on macOS so Brave extension shortcuts fire; "
            "'playwright' only sends page-level key events."
        ),
    )
    parser.add_argument(
        "--browser-app-name",
        default=os.environ.get("READWISE_BROWSER_APP_NAME", DEFAULT_BROWSER_APP_NAME),
        help="macOS application name used for system shortcut delivery (default: Brave Browser).",
    )
    parser.add_argument(
        "--remove-from-list",
        dest="remove_from_list",
        action="store_true",
        default=os.environ.get("MEDIUM_REMOVE_FROM_LIST", "true").lower() in {"1", "true", "yes"},
        help="Remove articles from the Medium Reading List after Readwise confirms the save.",
    )
    parser.add_argument(
        "--no-remove-from-list",
        dest="remove_from_list",
        action="store_false",
        help="Keep articles on the Medium Reading List after saving to Readwise.",
    )
    parser.add_argument(
        "--readwise-confirm-timeout",
        type=float,
        default=float(os.environ.get("READWISE_CONFIRM_TIMEOUT", "15")),
        help="Seconds to wait for visible Readwise save confirmation before failing.",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=float(os.environ.get("MEDIUM_DELAY_JITTER", "3")),
        help="Random +/- seconds applied to delay and between-article pauses.",
    )
    parser.add_argument(
        "--between-articles",
        type=float,
        default=float(os.environ.get("MEDIUM_BETWEEN_ARTICLES_DELAY", "8")),
        help="Extra pause between articles to reduce bot-detection risk.",
    )
    parser.add_argument(
        "--max-per-hour",
        type=int,
        default=int(os.environ.get("MEDIUM_MAX_PER_HOUR", "20")),
        help="Maximum articles to process per hour (0 disables the cap).",
    )
    return parser


def limited_urls(urls: list[str], limit: int | None) -> list[str]:
    """Apply an optional positive limit to ``urls``."""
    if limit is None:
        return urls
    if limit < 0:
        raise ValueError("--limit must be zero or greater")
    return urls[:limit]


async def collect_urls_if_needed(args: argparse.Namespace, page: object) -> list[str]:
    """Load cached article URLs or refresh them from Medium when needed."""
    article_state = load_article_state(args.state_dir)
    cached_urls = [str(url) for url in article_state.get("urls", []) if isinstance(url, str)]
    should_collect = args.refresh_articles or args.dry_run or args.collect_only or not cached_urls
    if not should_collect:
        return merge_article_urls([], cached_urls)

    urls = await collect_reading_list_urls(
        page,
        reading_list_url=args.reading_list_url,
        scroll_delay_seconds=args.scroll_delay,
        log=lambda message: append_run_log(args.state_dir, message),
    )
    if args.refresh_articles:
        merged = urls
    else:
        merged = merge_article_urls(cached_urls, urls)
    save_article_state(args.state_dir, reading_list_url=args.reading_list_url, urls=merged)
    return merged


async def run(args: argparse.Namespace) -> int:
    """Run the Medium to Readwise automation workflow."""
    ensure_state_dir(args.state_dir)
    append_run_log(args.state_dir, "run started")
    playwright = await async_playwright().start()
    try:
        session = await connect_over_cdp(playwright, cdp_url=args.cdp_url)
        all_urls = await collect_urls_if_needed(args, session.page)
        entries = processed_entries(args.state_dir)
        todo = limited_urls(
            pending_urls(all_urls, entries, retry_failed=args.retry_failed), args.limit
        )
        print(f"Discovered {len(all_urls)} article URLs; {len(todo)} pending for this run.")
        if args.dry_run or args.collect_only:
            for url in todo:
                suffix = " and remove from Reading List" if args.remove_from_list else ""
                print(f"Would process: {url}{suffix}")
            append_run_log(args.state_dir, f"planned {len(todo)} urls dry_run={args.dry_run}")
            return 0

        await ensure_no_human_verification(session.page)
        rate_limiter = HourlyRateLimiter(max_per_hour=args.max_per_hour)
        started = monotonic()
        total = len(todo)
        for index, url in enumerate(todo, start=1):
            try:
                rate_limiter.ensure_can_start()
            except RateLimitReached as exc:
                append_run_log(args.state_dir, f"rate limit reached: {exc}")
                print(str(exc), file=sys.stderr)
                return 0
            rate_limiter.record_start()
            try:
                result = await process_article_with_retries(
                    session.page,
                    url=url,
                    state_dir=args.state_dir,
                    reading_list_url=args.reading_list_url,
                    delay_seconds=args.delay,
                    jitter_seconds=args.jitter,
                    dry_run=False,
                    max_retries=args.max_retries,
                    retry_delay_seconds=args.retry_delay,
                    remove_from_list=args.remove_from_list,
                    readwise_confirm_timeout=args.readwise_confirm_timeout,
                    readwise_shortcut=args.readwise_shortcut,
                    shortcut_mode=args.shortcut_mode,
                    browser_app_name=args.browser_app_name,
                    log=lambda message: append_run_log(args.state_dir, message),
                )
            except HumanVerificationRequired as exc:
                append_run_log(args.state_dir, f"human verification required: {exc}")
                print(f"medium-to-readwise stopped:\n{exc}", file=sys.stderr)
                return 2
            entries = upsert_processed_entry(entries, result)
            save_processed_entries(args.state_dir, entries)
            append_run_log(
                args.state_dir,
                (
                    f"processed {url} status={result['status']} "
                    f"readwise_saved={result.get('readwise_saved')} "
                    f"removed_from_list={result.get('removed_from_list')} "
                    f"attempts={result['attempts']} elapsed={result['elapsed_seconds']}"
                ),
            )
            print(
                format_progress_line(
                    processed_count=index,
                    total_count=total,
                    elapsed_seconds=monotonic() - started,
                )
            )
            if index < total and result["status"] == "ok":
                slept = await sleep_with_jitter(
                    args.between_articles,
                    jitter_seconds=args.jitter,
                )
                append_run_log(
                    args.state_dir,
                    f"between-articles pause slept={round(slept, 2)}",
                )
        append_run_log(args.state_dir, "run finished")
    finally:
        await playwright.stop()
    return 0


def main() -> int:
    """Run from CLI arguments and return a process exit code."""
    load_repo_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(run(args))
    except RuntimeError as exc:
        print(f"medium-to-readwise failed:\n{exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"medium-to-readwise failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
