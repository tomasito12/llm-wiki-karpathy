"""Medium article parser that extracts main content into markdown."""

from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from src.pipeline.auth import MediumAuthConfig, build_medium_headers
from src.pipeline.models import DiscoveredItem, ParsedDocument
from src.pipeline.state_store import canonicalize_url


def parse_medium_item(item: DiscoveredItem, auth: MediumAuthConfig | None = None) -> ParsedDocument:
    """Fetch and parse a Medium article into markdown text."""
    html = _fetch_medium_html(item.url, auth=auth)
    preview_body = _extract_article_text(BeautifulSoup(html, "html.parser"))
    if (
        _looks_like_member_preview(preview_body)
        and auth is not None
        and auth.storage_state is not None
    ):
        rendered_html = _fetch_medium_html_with_browser(item.url, auth=auth)
        if rendered_html:
            html = rendered_html
    base_doc = parse_medium_html(item=item, html=html)

    author_followers = _fetch_author_followers(html=html, fallback_url=item.url, auth=auth)
    responses = _fetch_responses(item.url, auth=auth)

    return _rebuild_document(
        item=base_doc.item,
        title=_extract_title(BeautifulSoup(html, "html.parser"), fallback=item.title),
        body=_extract_article_text(BeautifulSoup(html, "html.parser")),
        author=base_doc.author,
        canonical_url=base_doc.canonical_url,
        claps=base_doc.claps,
        author_followers=author_followers,
        responses=responses,
    )


def _fetch_medium_html(article_url: str, auth: MediumAuthConfig | None = None) -> str:
    """Fetch Medium article HTML via HTTP request."""
    request = Request(article_url, headers=build_medium_headers(auth))
    with urlopen(request, timeout=20) as response:  # noqa: S310
        return response.read().decode("utf-8", errors="replace")


def _fetch_medium_html_with_browser(
    article_url: str,
    auth: MediumAuthConfig | None = None,
) -> str | None:
    """Fetch rendered article HTML with Playwright and authenticated storage state."""
    if auth is None:
        return None
    has_storage_state = auth.storage_state is not None and auth.storage_state.exists()
    has_user_data_dir = auth.user_data_dir is not None and auth.user_data_dir.exists()
    if not has_storage_state and not has_user_data_dir:
        return None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    with sync_playwright() as playwright:  # pragma: no cover - runtime integration path
        # Medium's anti-bot checks are less aggressive in headed mode.
        if has_user_data_dir and auth.user_data_dir is not None:
            executable_path = _detect_browser_executable(auth.user_data_dir)
            if executable_path is not None:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(auth.user_data_dir),
                    headless=False,
                    executable_path=str(executable_path),
                )
            else:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(auth.user_data_dir),
                    headless=False,
                )
            browser = None
        else:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context(storage_state=str(auth.storage_state))
        page = context.new_page()

        # Warm-up navigation helps settle challenge/cookie checks.
        page.goto("https://medium.com", wait_until="domcontentloaded", timeout=30000)

        for attempt in range(4):
            try:
                response = page.goto(article_url, wait_until="domcontentloaded", timeout=30000)
            except Exception:
                response = None
            status_code = response.status if response is not None else None
            html = page.content()
            blocked = _looks_like_challenge(html=html, status_code=status_code)
            if not blocked:
                # Give lazy-loaded article body a brief chance to render.
                page.wait_for_timeout(1500)
                html = page.content()
                context.close()
                if browser is not None:
                    browser.close()
                return html
            time.sleep(1.5 * (attempt + 1))

        context.close()
        if browser is not None:
            browser.close()
        return None


def _looks_like_member_preview(body: str) -> bool:
    """Heuristic to detect cropped member-only preview content."""
    return "Member-only story" in body and body.rstrip().endswith("…")


def _looks_like_challenge(html: str, status_code: int | None) -> bool:
    """Return whether the response appears to be a bot/challenge page."""
    lower = html.lower()
    if status_code in {403, 429}:
        return True
    if "just a moment" in lower:
        return True
    if "challenges.cloudflare.com" in lower:
        return True
    return False


def _detect_browser_executable(user_data_dir: Path) -> Path | None:
    """Best-effort detect browser executable for known user data directories."""
    data_path = str(user_data_dir)
    if "BraveSoftware/Brave-Browser" in data_path:
        brave_binary = Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser")
        if brave_binary.exists():
            return brave_binary
    if "Google/Chrome" in data_path:
        chrome_binary = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if chrome_binary.exists():
            return chrome_binary
    return None


def parse_medium_html(item: DiscoveredItem, html: str) -> ParsedDocument:
    """Parse article HTML and extract core markdown content."""
    soup = BeautifulSoup(html, "html.parser")
    title = _extract_title(soup, fallback=item.title)
    author = _extract_author(soup)
    canonical_url = _extract_canonical_url(soup, fallback=item.url)
    body = _extract_article_text(soup)
    claps = _extract_claps(soup=soup)
    responses = _extract_response_snippets(soup=soup)

    return _rebuild_document(
        item=item,
        title=title,
        body=body,
        author=author,
        canonical_url=canonical_url,
        claps=claps,
        author_followers=None,
        responses=responses,
    )


def _rebuild_document(
    *,
    item: DiscoveredItem,
    title: str,
    body: str,
    author: str | None,
    canonical_url: str,
    claps: int | None,
    author_followers: int | None,
    responses: list[str],
) -> ParsedDocument:
    """Build parsed document and markdown from extracted metadata."""
    markdown_lines = [
        f"# {title}",
        "",
        f"- Source: {canonical_url}",
        f"- Author: {author or 'Unknown'}",
        f"- Published: {item.published_at or 'Unknown'}",
        f"- Claps: {claps if claps is not None else 'Unknown'}",
        f"- Author Followers: {author_followers if author_followers is not None else 'Unknown'}",
        f"- Responses Captured: {len(responses)}",
        "",
        body,
    ]
    if responses:
        markdown_lines.extend(["", "## Response Snippets", ""])
        for snippet in responses:
            markdown_lines.append(f"- {snippet}")
    markdown = "\n".join(markdown_lines).strip() + "\n"
    return ParsedDocument(
        item=item,
        markdown=markdown,
        author=author,
        canonical_url=canonical_url,
        claps=claps,
        author_followers=author_followers,
        responses=responses,
    )


def _extract_title(soup: BeautifulSoup, fallback: str) -> str:
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return fallback


def _extract_author(soup: BeautifulSoup) -> str | None:
    byline = soup.find("meta", attrs={"name": "author"})
    if byline and byline.get("content"):
        return str(byline["content"]).strip()
    return None


def _extract_canonical_url(soup: BeautifulSoup, fallback: str) -> str:
    link = soup.find("link", attrs={"rel": "canonical"})
    href = link.get("href") if link else None
    return canonicalize_url(str(href).strip() if href else fallback)


def _extract_article_text(soup: BeautifulSoup) -> str:
    article = soup.find("article")
    if article is None:
        article = soup.find("main")
    if article is None:
        article = soup.body
    if article is None:
        return ""

    for tag_name in ["nav", "footer", "aside", "script", "style"]:
        for tag in article.find_all(tag_name):
            tag.decompose()

    lines: list[str] = []
    for node in article.find_all(["h1", "h2", "h3", "p", "li", "pre", "blockquote"]):
        text = node.get_text(" ", strip=True)
        if not text:
            continue
        if node.name in {"h1", "h2", "h3"}:
            level = {"h1": "#", "h2": "##", "h3": "###"}[node.name]
            lines.append(f"{level} {text}")
        elif node.name == "li":
            lines.append(f"- {text}")
        elif node.name == "blockquote":
            lines.append(f"> {text}")
        elif node.name == "pre":
            lines.append("```")
            lines.append(text)
            lines.append("```")
        else:
            lines.append(text)
    return "\n\n".join(lines).strip()


def _extract_claps(soup: BeautifulSoup) -> int | None:
    """Extract clap count if embedded in script payloads."""
    clap_values: list[int] = []
    for script in soup.find_all("script"):
        content = script.string or script.get_text()
        if not content:
            continue
        for match in re.findall(r'"clapCount"\s*:\s*(\d+)', content):
            clap_values.append(int(match))
    if not clap_values:
        return None
    return max(clap_values)


def _extract_response_snippets(soup: BeautifulSoup, limit: int = 5) -> list[str]:
    """Extract response snippets from embedded script payloads when available."""
    snippets: list[str] = []
    for script in soup.find_all("script"):
        content = script.string or script.get_text()
        if not content:
            continue
        matches = re.findall(r'"previewSnippet"\s*:\s*"([^"]+)"', content)
        for raw in matches:
            cleaned = bytes(raw, "utf-8").decode("unicode_escape").strip()
            if cleaned and cleaned not in snippets:
                snippets.append(cleaned)
            if len(snippets) >= limit:
                return snippets
    return snippets


def _fetch_author_followers(
    html: str, fallback_url: str, auth: MediumAuthConfig | None = None
) -> int | None:
    """Fetch follower count from author page when available."""
    soup = BeautifulSoup(html, "html.parser")
    author_url = _extract_author_url(soup=soup, fallback_url=fallback_url)
    if author_url is None:
        return None
    try:
        request = Request(author_url, headers=build_medium_headers(auth))
        with urlopen(request, timeout=20) as response:  # noqa: S310
            author_html = response.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    return _extract_followers_from_text(author_html)


def _extract_author_url(soup: BeautifulSoup, fallback_url: str) -> str | None:
    """Extract author profile URL from article metadata."""
    meta = soup.find("meta", attrs={"property": "article:author"})
    if meta and meta.get("content"):
        return str(meta["content"]).strip()
    rel_author = soup.find("a", attrs={"rel": "author"})
    if rel_author and rel_author.get("href"):
        return urljoin(fallback_url, str(rel_author["href"]).strip())
    return None


def _extract_followers_from_text(html: str) -> int | None:
    """Extract follower count from profile page text."""
    match = re.search(r"([0-9][0-9,\.]*)\s+Followers", html, flags=re.IGNORECASE)
    if match is None:
        return None
    raw = match.group(1).replace(",", "")
    try:
        return int(float(raw))
    except ValueError:
        return None


def _fetch_responses(
    article_url: str, limit: int = 5, auth: MediumAuthConfig | None = None
) -> list[str]:
    """Try to fetch response snippets from the article responses page."""
    responses_url = f"{canonicalize_url(article_url)}/responses"
    try:
        request = Request(responses_url, headers=build_medium_headers(auth))
        with urlopen(request, timeout=20) as response:  # noqa: S310
            html = response.read().decode("utf-8", errors="replace")
    except Exception:
        return []
    soup = BeautifulSoup(html, "html.parser")
    snippets: list[str] = []
    for paragraph in soup.find_all("p"):
        text = paragraph.get_text(" ", strip=True)
        if len(text) < 40:
            continue
        if text in snippets:
            continue
        snippets.append(text)
        if len(snippets) >= limit:
            break
    return snippets
