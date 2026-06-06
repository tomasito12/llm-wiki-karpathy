#!/usr/bin/env python3
"""Backward-compatible wrapper for ``hatch run readwise-dedupe``."""

from src.readwise.dedupe_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
