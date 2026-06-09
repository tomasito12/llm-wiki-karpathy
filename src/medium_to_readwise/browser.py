"""Playwright CDP connection helpers for Brave."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen

from playwright.async_api import Browser, BrowserContext, Page, Playwright

CDP_START_INSTRUCTIONS = """\
Brave CDP is not reachable at {cdp_url}.

On macOS, `open -a "Brave Browser" --args --remote-debugging-port=9222` does NOT
enable debugging when Brave is already running. Quit Brave completely first
(Brave → Quit, or: osascript -e 'quit app "Brave Browser"'), then launch:

  /Applications/Brave\\ Browser.app/Contents/MacOS/Brave\\ Browser --remote-debugging-port=9222

Verify the port is open:

  curl -s http://127.0.0.1:9222/json/version
"""


@dataclass(frozen=True)
class ConnectedBrowser:
    """A connected browser session with an active context and page."""

    browser: Browser
    context: BrowserContext
    page: Page


def cdp_reachable(cdp_url: str, *, timeout_seconds: float = 2.0) -> bool:
    """Return whether the Chrome DevTools Protocol endpoint responds."""
    version_url = f"{cdp_url.rstrip('/')}/json/version"
    try:
        with urlopen(version_url, timeout=timeout_seconds) as response:
            return 200 <= response.status < 300
    except (OSError, URLError, ValueError):
        return False


def cdp_connection_error(cdp_url: str) -> RuntimeError:
    """Build a user-facing error when CDP is unavailable."""
    return RuntimeError(CDP_START_INSTRUCTIONS.format(cdp_url=cdp_url))


async def connect_over_cdp(playwright: Playwright, *, cdp_url: str) -> ConnectedBrowser:
    """Connect to an already-running Brave instance through Chrome DevTools Protocol."""
    if not cdp_reachable(cdp_url):
        raise cdp_connection_error(cdp_url)
    browser = await playwright.chromium.connect_over_cdp(cdp_url)
    context = select_context(browser)
    page = await select_page(context)
    return ConnectedBrowser(browser=browser, context=context, page=page)


def select_context(browser: Browser) -> BrowserContext:
    """Return a useful existing browser context or create one synchronously from CDP state."""
    if browser.contexts:
        contexts_with_pages = [context for context in browser.contexts if context.pages]
        return contexts_with_pages[0] if contexts_with_pages else browser.contexts[0]
    msg = "Connected browser has no contexts; restart Brave with --remote-debugging-port=9222"
    raise RuntimeError(msg)


async def select_page(context: BrowserContext) -> Page:
    """Return an existing page or open a new tab in ``context``."""
    if context.pages:
        return context.pages[0]
    return await context.new_page()
