"""Repository path helpers for ingest review tooling."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (directory containing ``state`` and ``wiki``)."""
    return Path(__file__).resolve().parents[2]


def load_repo_dotenv(*, override: bool = False) -> Path:
    """Load variables from ``<repo_root>/.env`` into ``os.environ``.

    Uses ``python-dotenv`` so local secrets (e.g. ``OPENAI_API_KEY``) are available
    regardless of the process working directory. Existing OS variables are kept
    unless ``override`` is true (same default as :func:`dotenv.load_dotenv`).

    Args:
        override: When true, values from ``.env`` replace existing environment keys.

    Returns:
        The repository root path (same as :func:`repo_root`).
    """
    from dotenv import load_dotenv

    root = repo_root()
    load_dotenv(root / ".env", override=override)
    return root
