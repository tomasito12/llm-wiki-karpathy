"""Launch Brave with Chrome DevTools Protocol enabled on macOS."""

from __future__ import annotations

import subprocess
import time
from collections.abc import Callable
from pathlib import Path
from time import monotonic
from urllib.parse import urlparse

from src.medium_to_readwise.browser import cdp_connection_error, cdp_reachable

DEFAULT_BRAVE_BINARY = Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser")
DEFAULT_BRAVE_STARTUP_TIMEOUT_SECONDS = 30.0


def default_brave_binary() -> Path:
    """Return the default Brave executable path on macOS."""
    return DEFAULT_BRAVE_BINARY


def brave_binary_for_app_name(browser_app_name: str) -> Path:
    """Resolve a macOS ``.app`` name to its main executable path."""
    if browser_app_name == "Brave Browser":
        return default_brave_binary()
    return Path(f"/Applications/{browser_app_name}.app/Contents/MacOS/{browser_app_name}")


def cdp_port_from_url(cdp_url: str) -> int:
    """Extract the remote-debugging port from a CDP base URL."""
    parsed = urlparse(cdp_url)
    if parsed.port is not None:
        return parsed.port
    return 9222


def _emit_log(log: Callable[[str], None] | None, message: str) -> None:
    """Write one launcher log line when logging is enabled."""
    if log is not None:
        log(message)


def brave_process_is_running(brave_binary: Path) -> bool:
    """Return whether a Brave process matching ``brave_binary`` is running."""
    result = subprocess.run(  # noqa: S603
        ["pgrep", "-f", str(brave_binary)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def quit_brave_app(browser_app_name: str, *, wait_timeout_seconds: float = 15.0) -> None:
    """Quit Brave through AppleScript and wait until the process exits."""
    subprocess.run(  # noqa: S603
        ["osascript", "-e", f'quit app "{browser_app_name}"'],
        check=False,
    )
    deadline = monotonic() + wait_timeout_seconds
    binary = brave_binary_for_app_name(browser_app_name)
    while monotonic() < deadline:
        if not brave_process_is_running(binary):
            return
        time.sleep(0.25)
    msg = f"Brave ({browser_app_name}) did not exit within {wait_timeout_seconds:.0f}s"
    raise RuntimeError(msg)


def launch_brave_with_cdp(
    brave_binary: Path,
    *,
    cdp_port: int,
) -> subprocess.Popen[bytes]:
    """Start Brave detached with the configured remote-debugging port."""
    if not brave_binary.is_file():
        msg = f"Brave executable not found: {brave_binary}"
        raise RuntimeError(msg)
    return subprocess.Popen(  # noqa: S603
        [str(brave_binary), f"--remote-debugging-port={cdp_port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def wait_for_cdp(
    cdp_url: str,
    *,
    timeout_seconds: float = DEFAULT_BRAVE_STARTUP_TIMEOUT_SECONDS,
) -> None:
    """Poll until the CDP endpoint responds or ``timeout_seconds`` elapses."""
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        if cdp_reachable(cdp_url, timeout_seconds=1.0):
            return
        time.sleep(0.5)
    msg = (
        f"Brave CDP did not become reachable at {cdp_url} within {timeout_seconds:.0f}s. "
        "Confirm Brave is installed and retry."
    )
    raise RuntimeError(msg)


def prepare_brave_cdp_session(
    cdp_url: str,
    *,
    launch_brave: bool,
    browser_app_name: str,
    brave_binary: Path,
    startup_timeout_seconds: float = DEFAULT_BRAVE_STARTUP_TIMEOUT_SECONDS,
    log: Callable[[str], None] | None = None,
) -> None:
    """Ensure Brave is running with a reachable CDP endpoint before automation."""
    if cdp_reachable(cdp_url):
        _emit_log(log, f"Brave CDP already reachable at {cdp_url}")
        return
    if not launch_brave:
        raise cdp_connection_error(cdp_url)
    _emit_log(
        log,
        (
            f"Brave CDP not reachable at {cdp_url}; quitting {browser_app_name} "
            f"and relaunching with --remote-debugging-port={cdp_port_from_url(cdp_url)}"
        ),
    )
    quit_brave_app(browser_app_name)
    launch_brave_with_cdp(brave_binary, cdp_port=cdp_port_from_url(cdp_url))
    wait_for_cdp(cdp_url, timeout_seconds=startup_timeout_seconds)
    _emit_log(log, f"Brave CDP ready at {cdp_url}")
