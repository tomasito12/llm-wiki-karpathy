"""Module entry point for ``python -m src.ingest_batch``."""

from __future__ import annotations

from src.ingest_batch.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
