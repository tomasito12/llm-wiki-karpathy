"""Allow ``python -m src.wiki_lint``."""

from src.wiki_lint.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
