"""Tests for wiki schema/link validator."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

from src.wiki_lint.validator import validate_wiki


def write(path: Path, text: str) -> None:
    """Write a markdown fixture file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_valid_minimal_wiki_passes(tmp_path: Path) -> None:
    """A small wiki satisfying core contracts produces no issues."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "tools" / "index.md",
        """---
title: Tools
type: tools-index
created: 2026-05-07
updated: 2026-05-07
---

| Category | Page |
|----------|------|
| AI assistants | [[tools/ai-assistants/index]] |
""",
    )
    write(
        wiki / "tools" / "ai-assistants" / "index.md",
        """---
title: AI assistants
type: tools-category-index
created: 2026-05-07
updated: 2026-05-07
---

| Tool | Page |
|------|------|
| ChatGPT | [[tools/ai-assistants/chatgpt]] |
""",
    )
    write(
        wiki / "tools" / "ai-assistants" / "chatgpt.md",
        """---
title: ChatGPT
type: tool
created: 2026-05-07
updated: 2026-05-07
tags:
  - tools
---

## What problem does this tool solve?

...

## Properties

- ...

## Author assessments

- ... [[sources/source]]

## Sources

- [[sources/source]]
""",
    )
    write(
        wiki / "sources" / "source.md",
        """---
title: Source
type: source
author: Author
publication: Publication
created: 2026-05-07
updated: 2026-05-07
tags:
  - tools
---

Summary.

## Apps and platforms covered

- [[tools/ai-assistants/chatgpt]]

## Why it matters

...

## Context and Limitations

...

## Contradictions / Unverified Claims

...

## Sources

- [Original](https://example.com)
""",
    )
    assert validate_wiki(wiki) == []


def test_validator_reports_bad_tag_heading_and_broken_link(tmp_path: Path) -> None:
    """Validator catches unsupported tags, heading drift, and broken links."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "tools" / "bad.md",
        """---
title: Bad
type: tool
created: 2026-05-07
updated: 2026-05-07
tags:
  - bad-tag
---

## Properties

- [[missing/page]]
""",
    )
    messages = [issue.message for issue in validate_wiki(wiki)]
    assert "unsupported tag: bad-tag" in messages
    assert any(message.startswith("unexpected headings") for message in messages)
    assert "broken wikilink: [[missing/page]]" in messages


def test_wiki_lint_cli_returns_nonzero_on_issues(tmp_path: Path) -> None:
    """CLI returns 1 when validation fails."""
    from src.wiki_lint import cli

    wiki = tmp_path / "wiki"
    write(
        wiki / "source.md",
        """---
title: Source
type: unknown
created: 2026-05-07
updated: 2026-05-07
---
""",
    )
    with mock.patch.object(cli, "validate_wiki", return_value=validate_wiki(wiki)):
        with mock.patch("sys.argv", ["wiki-lint", "--wiki-dir", str(wiki)]):
            assert cli.main() == 1
