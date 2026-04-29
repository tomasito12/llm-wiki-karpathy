"""Medium source discovery via public /archive pages (HTTP or headless browser)."""

from __future__ import annotations

import re
from collections import deque
from datetime import UTC, date, datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from src.pipeline.auth import USER_AGENT, MediumAuthConfig, build_medium_headers
from src.pipeline.models import DiscoveredItem, SourceConfig
from src.pipeline.state_store import canonicalize_url, make_item_id

ARTICLE_SLUG_PATTERN = re.compile(r"^[a-z0-9-]+-[0-9a-f]{8,}$")

# Browser archive: stop scrolling after this many iterations with no new article links.
_ARCHIVE_STALL_SCROLL_LIMIT = 5


def published_at_to_utc_date(published_at: str | None) -> date | None:
    """Parse Medium / HTTP date / ISO publish strings to a UTC calendar date."""
    if not published_at:
        return None
    try:
        parsed_dt = parsedate_to_datetime(published_at.strip())
    except (TypeError, ValueError):
        try:
            parsed_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed_dt.tzinfo is None:
        parsed_dt = parsed_dt.replace(tzinfo=UTC)
    return parsed_dt.astimezone(UTC).date()


def archive_scroll_window_calendar_bounds(
    window_start_days: int, window_end_days: int
) -> tuple[date, date]:
    """Return inclusive UTC calendar dates [start, end] for the CLI window."""
    today = datetime.now(tz=UTC).date()
    return (
        today - timedelta(days=window_start_days),
        today - timedelta(days=window_end_days),
    )


def archive_scroll_should_stop(
    *,
    min_published_date: date | None,
    window_start_date: date,
    stall_scrolls: int,
    scroll_index: int,
    max_scrolls: int,
    stall_limit: int = _ARCHIVE_STALL_SCROLL_LIMIT,
) -> bool:
    """Return True when browser scrolling should stop.

    Stops when the oldest seen article is strictly before the window start day (so the
    full inclusive window has been scrolled past), or on stall/safety caps.
    """
    if scroll_index >= max_scrolls:
        return True
    if stall_scrolls >= stall_limit:
        return True
    if min_published_date is not None and min_published_date < window_start_date:
        return True
    return False


def discover_medium_items(source: SourceConfig, limit: int | None = None) -> list[DiscoveredItem]:
    """Discover candidate items from Medium website archive pages."""
    return discover_medium_items_with_options(source=source, limit=limit)


def discover_medium_items_with_options(
    source: SourceConfig,
    limit: int | None = None,
    *,
    use_browser: bool = False,
    max_archive_pages: int = 8,
    max_scrolls: int = 8,
    auth: MediumAuthConfig | None = None,
    archive_window_start_days: int | None = None,
    archive_window_end_days: int | None = None,
) -> list[DiscoveredItem]:
    """Discover candidate items from ``{source.url}/archive`` (HTTP or browser)."""
    if source.kind != "medium":
        raise ValueError(f"Unsupported source kind for Medium discovery: {source.kind}")
    if use_browser:
        discovered = _discover_from_archive_browser(
            source=source,
            max_links=(limit if limit is not None else 10_000),
            max_scrolls=max_scrolls,
            auth=auth,
            archive_window_start_days=archive_window_start_days,
            archive_window_end_days=archive_window_end_days,
        )
    else:
        discovered = _discover_from_archive_http(
            source=source,
            max_links=limit or 50,
            max_archive_pages=max_archive_pages,
            auth=auth,
        )
    deduped = _dedupe_discovered(discovered)
    if limit is not None:
        return deduped[:limit]
    return deduped


def _discover_from_archive_http(
    source: SourceConfig,
    max_links: int = 50,
    max_archive_pages: int = 8,
    auth: MediumAuthConfig | None = None,
) -> list[DiscoveredItem]:
    """Discover candidate article links by fetching and parsing ``/archive`` HTML pages."""
    archive_root = f"{canonicalize_url(source.url)}/archive"
    links = _crawl_archive_pages(
        archive_root=archive_root,
        max_links=max_links,
        max_archive_pages=max_archive_pages,
        auth=auth,
    )
    discovered: list[DiscoveredItem] = []
    for link in links:
        pub_date = _fetch_article_publish_date(link, auth=auth)
        discovered.append(
            DiscoveredItem(
                item_id=make_item_id(link),
                source_name=source.name,
                source_url=source.url,
                url=link,
                title=link,
                published_at=pub_date,
            )
        )
    return discovered


def _discover_from_archive_browser(
    source: SourceConfig,
    max_links: int = 50,
    max_scrolls: int = 8,
    auth: MediumAuthConfig | None = None,
    *,
    archive_window_start_days: int | None = None,
    archive_window_end_days: int | None = None,
) -> list[DiscoveredItem]:
    """Discover archive links by rendering the page and scrolling dynamically.

    When ``archive_window_start_days`` and ``archive_window_end_days`` are set, scrolling
    continues until the oldest article publish date seen is *before* the first day of the
    target window (so the full inclusive day range has been scrolled through), or until
    scroll stall / ``max_scrolls`` safety limits.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError(
            "Browser mode requires Playwright. Install with `uv add playwright` and run "
            "`playwright install chromium`."
        ) from exc

    archive_root = f"{canonicalize_url(source.url)}/archive"
    links: list[str] = []
    url_to_pub: dict[str, str | None] = {}
    use_window_scroll = (
        archive_window_start_days is not None and archive_window_end_days is not None
    )
    window_start_date: date | None = None
    if use_window_scroll:
        assert archive_window_start_days is not None
        assert archive_window_end_days is not None
        window_start_date, _window_end_date = archive_scroll_window_calendar_bounds(
            archive_window_start_days,
            archive_window_end_days,
        )

    def min_seen_date() -> date | None:
        dates: list[date] = []
        for raw in url_to_pub.values():
            d = published_at_to_utc_date(raw)
            if d is not None:
                dates.append(d)
        return min(dates) if dates else None

    def fetch_pub_if_needed(url: str) -> None:
        if url in url_to_pub:
            return
        url_to_pub[url] = _fetch_article_publish_date(url, auth=auth)

    with sync_playwright() as playwright:  # pragma: no cover - integration behavior
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        if auth is not None and auth.storage_state is not None and auth.storage_state.exists():
            context.close()
            context = browser.new_context(
                user_agent=USER_AGENT,
                storage_state=str(auth.storage_state),
            )
        page = context.new_page()
        page.goto(archive_root, wait_until="domcontentloaded", timeout=30000)

        scroll_index = 0
        stall_scrolls = 0
        prev_count = 0

        while True:
            hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            for href in hrefs:
                if not isinstance(href, str):
                    continue
                if not _is_article_link(href):
                    continue
                canonical = canonicalize_url(href)
                if canonical not in links:
                    links.append(canonical)
                    fetch_pub_if_needed(canonical)
                if len(links) >= max_links:
                    break

            if len(links) >= max_links:
                break

            if len(links) == prev_count:
                stall_scrolls += 1
            else:
                stall_scrolls = 0
            prev_count = len(links)

            min_date = min_seen_date()
            if use_window_scroll and window_start_date is not None:
                if archive_scroll_should_stop(
                    min_published_date=min_date,
                    window_start_date=window_start_date,
                    stall_scrolls=stall_scrolls,
                    scroll_index=scroll_index,
                    max_scrolls=max_scrolls,
                ):
                    break
            else:
                if stall_scrolls >= _ARCHIVE_STALL_SCROLL_LIMIT:
                    break
                if scroll_index >= max_scrolls:
                    break

            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
            scroll_index += 1

        context.close()
        browser.close()

    # Ensure every collected link has a publish date (cached where possible).
    for link in links[:max_links]:
        fetch_pub_if_needed(link)

    discovered: list[DiscoveredItem] = []
    for link in links[:max_links]:
        discovered.append(
            DiscoveredItem(
                item_id=make_item_id(link),
                source_name=source.name,
                source_url=source.url,
                url=link,
                title=link,
                published_at=url_to_pub.get(link),
            )
        )
    return discovered


def _crawl_archive_pages(
    archive_root: str,
    max_links: int,
    max_archive_pages: int,
    auth: MediumAuthConfig | None = None,
) -> list[str]:
    """Traverse linked ``/archive`` pages and collect candidate article URLs."""
    visited_pages: set[str] = set()
    page_queue: deque[str] = deque([archive_root])
    links: list[str] = []
    while page_queue and len(visited_pages) < max_archive_pages and len(links) < max_links:
        page_url = canonicalize_url(page_queue.popleft())
        if page_url in visited_pages:
            continue
        visited_pages.add(page_url)
        try:
            request = Request(page_url, headers=build_medium_headers(auth))
            with urlopen(request, timeout=20) as response:  # noqa: S310
                html = response.read().decode("utf-8", errors="replace")
        except Exception:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for link in _extract_medium_links(soup=soup, max_links=max_links):
            if link not in links:
                links.append(link)
                if len(links) >= max_links:
                    break
        for archive_link in _extract_archive_links(soup=soup, archive_root=archive_root):
            if archive_link not in visited_pages:
                page_queue.append(archive_link)
    return links[:max_links]


def _extract_medium_links(soup: BeautifulSoup, max_links: int) -> list[str]:
    """Extract candidate article links from archive page markup."""
    links: list[str] = []
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if not href:
            continue
        if not isinstance(href, str):
            continue
        if not _is_article_link(href):
            continue
        canonical = canonicalize_url(href)
        if canonical in links:
            continue
        links.append(canonical)
        if len(links) >= max_links:
            break
    return links


def _is_article_link(href: str) -> bool:
    """Return whether a URL points to a candidate Medium article."""
    parsed = urlparse(href)
    if "medium.com" not in parsed.netloc:
        return False
    path = parsed.path.strip("/")
    if not path:
        return False
    if path.startswith("tag/") or "/archive" in f"/{path}/":
        return False
    segments = [part for part in path.split("/") if part]
    slug = segments[-1] if segments else ""
    if slug.startswith("@"):
        return False
    if slug in {"signin", "search", "about", "browse", "sitemap.xml"}:
        return False
    return bool(ARTICLE_SLUG_PATTERN.match(slug))


def _extract_archive_links(soup: BeautifulSoup, archive_root: str) -> list[str]:
    """Extract linked archive pages to support deeper traversal."""
    archive_links: list[str] = []
    archive_root_canonical = canonicalize_url(archive_root)
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if not href or not isinstance(href, str):
            continue
        joined = canonicalize_url(urljoin(archive_root, href))
        if "/archive" not in joined:
            continue
        if not joined.startswith(archive_root_canonical):
            continue
        if joined not in archive_links:
            archive_links.append(joined)
    return archive_links


def _fetch_article_publish_date(
    article_url: str, auth: MediumAuthConfig | None = None
) -> str | None:
    """Fetch publish date from article metadata for archive-discovered links."""
    try:
        request = Request(article_url, headers=build_medium_headers(auth))
        with urlopen(request, timeout=10) as response:  # noqa: S310
            html = response.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for property_name in ("article:published_time", "og:pubdate"):
        meta = soup.find("meta", attrs={"property": property_name})
        if meta and meta.get("content"):
            return str(meta["content"]).strip()
    return None


def _dedupe_discovered(items: list[DiscoveredItem]) -> list[DiscoveredItem]:
    """Deduplicate discovered items by item ID, preferring richer metadata."""
    merged: dict[str, DiscoveredItem] = {}
    for item in items:
        current = merged.get(item.item_id)
        if current is None:
            merged[item.item_id] = item
            continue
        if current.published_at is None and item.published_at is not None:
            merged[item.item_id] = item
    return list(merged.values())
