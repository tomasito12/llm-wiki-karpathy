"""Detect whether Brave is logged into Medium before article automation."""

from __future__ import annotations

from playwright.async_api import Page

MEDIUM_LOGIN_URL_MARKERS: tuple[str, ...] = (
    "accounts.medium.com",
    "/m/signin",
    "/m/login",
    "/m/account",
)

MEDIUM_LOGGED_OUT_PHRASES: tuple[str, ...] = (
    "sign in to read",
    "sign in to continue",
    "sign in with google",
    "sign in with email",
    "sign in with apple",
    "create account",
    "this member-only story",
    "story is for members",
    "upgrade to read the full story",
    "become a member to read",
)

SIGN_IN_CONTROL_SELECTORS: tuple[str, ...] = (
    'a[href*="accounts.medium.com"]',
    'a[href*="/m/signin"]',
)


class MediumLoginRequired(RuntimeError):
    """Raised when Medium requires a logged-in session."""

    def __init__(
        self,
        message: str = (
            "Medium is not logged in. Sign in to Medium in Brave, confirm the "
            "Readwise shortcut works manually, then rerun medium-to-readwise."
        ),
    ) -> None:
        """Initialize with a user-facing message."""
        super().__init__(message)


def page_url_indicates_medium_login(url: str) -> bool:
    """Return whether the current URL is a Medium sign-in or account page."""
    lowered = url.lower()
    return any(marker in lowered for marker in MEDIUM_LOGIN_URL_MARKERS)


def page_text_indicates_medium_logged_out(text: str) -> bool:
    """Return whether visible page text looks like a logged-out Medium gate."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in MEDIUM_LOGGED_OUT_PHRASES)


async def detect_visible_sign_in_controls(page: Page) -> bool:
    """Return whether prominent Medium sign-in controls are visible."""
    for selector in SIGN_IN_CONTROL_SELECTORS:
        locator = page.locator(selector)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    for label in ("Sign in", "Sign up"):
        locator = page.get_by_role("link", name=label)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    return False


async def article_body_is_thin(page: Page, *, min_chars: int = 400) -> bool:
    """Return whether the rendered Medium article body is shorter than ``min_chars``."""
    try:
        article = page.locator("article").first
        if await article.count() == 0:
            return True
        text = await article.inner_text()
        return len(text.strip()) < min_chars
    except Exception:
        return True


async def detect_medium_logged_out(page: Page) -> bool:
    """Return whether the current page indicates an unauthenticated Medium session."""
    if page_url_indicates_medium_login(page.url):
        return True
    if await detect_visible_sign_in_controls(page):
        return True
    for phrase in MEDIUM_LOGGED_OUT_PHRASES:
        locator = page.get_by_text(phrase, exact=False)
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                return True
        except Exception:
            continue
    if not await article_body_is_thin(page):
        return False
    try:
        body_text = await page.locator("body").inner_text()
    except Exception:
        body_text = ""
    return page_text_indicates_medium_logged_out(body_text)


async def ensure_medium_logged_in(page: Page) -> None:
    """Raise ``MediumLoginRequired`` when Medium is not authenticated."""
    if await detect_medium_logged_out(page):
        raise MediumLoginRequired()
