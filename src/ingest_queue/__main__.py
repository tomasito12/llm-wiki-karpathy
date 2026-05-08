"""Module entry point for ``python -m src.ingest_queue``."""

from __future__ import annotations

from src.ingest_queue.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
