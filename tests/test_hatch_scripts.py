"""Tests for Hatch CLI script wiring."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_hatch_scripts_include_local_clis() -> None:
    """Default Hatch scripts expose the local CLIs."""
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    scripts = data["tool"]["hatch"]["envs"]["default"]["scripts"]
    assert scripts["wiki-lint"] == ["python -m src.wiki_lint {args}"]
    assert scripts["wiki-render"] == ["python -m src.wiki_render {args}"]
    assert scripts["wiki-reset"] == ["python -m src.wiki_reset {args}"]
    assert scripts["dashboard"] == ["streamlit run src/dashboard/app.py {args}"]
    assert scripts["ingest-manifest"] == ["python -m src.pipeline.ingest_manifest {args}"]
    assert scripts["ingest-queue"] == ["python -m src.ingest_queue {args}"]
    assert scripts["readwise-rebuild-index"] == ["python -m src.readwise.rebuild {args}"]
    assert scripts["readwise-dedupe"] == ["python -m src.readwise.dedupe_cli {args}"]
