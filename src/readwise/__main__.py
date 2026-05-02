"""Allow ``python -m src.readwise``."""

from src.readwise.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
