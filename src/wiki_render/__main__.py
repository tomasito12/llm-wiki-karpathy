"""Allow ``python -m src.wiki_render``."""

from __future__ import annotations

from src.wiki_render.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
