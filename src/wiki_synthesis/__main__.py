"""Allow ``python -m src.wiki_synthesis``."""

from __future__ import annotations

from src.wiki_synthesis.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
