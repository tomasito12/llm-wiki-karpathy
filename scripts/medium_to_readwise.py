#!/usr/bin/env python3
"""Backward-compatible wrapper for ``hatch run medium-to-readwise``."""

from src.medium_to_readwise.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
