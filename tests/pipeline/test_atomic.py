"""Tests for atomic write helpers."""

from __future__ import annotations

import json
from pathlib import Path

from src.pipeline.atomic import atomic_write_json, atomic_write_text


def test_atomic_write_text_creates_parent_and_overwrites(tmp_path: Path) -> None:
    """Text writes create parents and replace existing content."""
    path = tmp_path / "state" / "file.txt"
    atomic_write_text(path, "first")
    atomic_write_text(path, "second")
    assert path.read_text(encoding="utf-8") == "second"


def test_atomic_write_json_uses_stable_format(tmp_path: Path) -> None:
    """JSON writes can be loaded and use sorted keys."""
    path = tmp_path / "state" / "file.json"
    atomic_write_json(path, {"b": 2, "a": 1})
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1, "b": 2}
    assert path.read_text(encoding="utf-8").splitlines()[1].strip().startswith('"a"')
