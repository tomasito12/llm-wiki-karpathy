"""Tests for wiki schema/link validator."""

from __future__ import annotations

from pathlib import Path

from src.wiki_lint.validator import validate_wiki


def write(path: Path, text: str) -> None:
    """Write a markdown fixture file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_valid_generated_wiki_passes(tmp_path: Path) -> None:
    """A minimal generated-style vault satisfies shared contracts."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "sources" / "source-a.md",
        """---
title: Source A
category: source
source_id: source-a
tags:
  - ai-engineering
derived_topics:
  - topics/local-models.md
derived_pages:
  - topics/local-models.md
---

# Source A

Summary.

## Key insights

- Insight one.

## Derived knowledge pages

- [[topics/local-models]]

## Why it matters

It matters.

## Limitations / open questions

Limits.

## Contradictions / unverified claims

None.

## Source metadata

- Canonical URL: https://example.com

## Full source text

Fixture source text.
""",
    )
    write(
        wiki / "topics" / "local-models.md",
        """---
title: Local Models
category: topic
slug: local-models
entity_id: topic:local-models
synthesis_state: stage1-placeholder
source_count: 1
source_ids:
  - source-a
tags:
  - infrastructure
---

# Local Models

## Current understanding

Lead.

## Evidence / supporting sources

### Source A (2026-01-02)

- Claim (`evidence-id` · supporting · field; [[sources/source-a|Source A]])

## Sources

- [[sources/source-a|Source A]]
""",
    )
    assert validate_wiki(wiki) == []


def test_synthesized_knowledge_page_accepts_evidence_index(tmp_path: Path) -> None:
    """Synthesized knowledge pages use a compact evidence index instead of full evidence."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "topics" / "local-models.md",
        """---
title: Local Models
category: topic
slug: local-models
entity_id: topic:local-models
synthesis_state: synthesized
source_count: 1
source_ids:
  - source-a
tags:
  - infrastructure
---

# Local Models

## Executive synthesis

Summary.

## Evidence index

- Sources: 1
- Evidence items: 2

## Sources

- [[sources/source-a|Source A]]
""",
    )
    write(
        wiki / "sources" / "source-a.md",
        """---
title: Source A
category: source
source_id: source-a
tags:
  - ai-engineering
---

# Source A

## Key insights

None.

## Derived knowledge pages

- [[topics/local-models]]

## Why it matters

It matters.

## Limitations / open questions

None.

## Contradictions / unverified claims

None.

## Source metadata

None.

## Full source text

None.
""",
    )
    assert validate_wiki(wiki) == []


def test_source_page_allows_h2_headings_in_embedded_raw_text(tmp_path: Path) -> None:
    """Raw source text after ## Full source text may contain its own level-2 headings."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "sources" / "source-a.md",
        """---
title: Source A
category: source
source_id: source-a
tags:
  - ai-engineering
derived_topics:
  - topics/local-models.md
derived_pages:
  - topics/local-models.md
---

# Source A

Summary.

## Key insights

- Insight one.

## Derived knowledge pages

- [[topics/local-models]]

## Why it matters

It matters.

## Limitations / open questions

Limits.

## Contradictions / unverified claims

None.

## Source metadata

- Canonical URL: https://example.com

## Full source text

# Original Article Title

## Section inside raw export

Raw paragraph under an article heading.

## Another raw section

More original article content.
""",
    )
    write(
        wiki / "topics" / "local-models.md",
        """---
title: Local Models
category: topic
slug: local-models
entity_id: topic:local-models
synthesis_state: stage1-placeholder
source_count: 1
source_ids:
  - source-a
tags:
  - infrastructure
---

# Local Models

## Current understanding

Lead.

## Evidence / supporting sources

### Source A (2026-01-02)

- Claim (`evidence-id` · supporting · field; [[sources/source-a|Source A]])

## Sources

- [[sources/source-a|Source A]]
""",
    )
    assert validate_wiki(wiki) == []


def test_source_page_ignores_wikilinks_in_embedded_raw_text(tmp_path: Path) -> None:
    """Wikilink validation should ignore links inside embedded raw source text."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "sources" / "source-a.md",
        """---
title: Source A
category: source
source_id: source-a
tags:
  - ai-engineering
derived_topics:
  - topics/local-models.md
derived_pages:
  - topics/local-models.md
---

# Source A

Summary.

## Key insights

- Insight one.

## Derived knowledge pages

- [[topics/local-models]]

## Why it matters

It matters.

## Limitations / open questions

Limits.

## Contradictions / unverified claims

None.

## Source metadata

- Canonical URL: https://example.com

## Full source text

See also [[some/unmanaged/raw-page]] for context.
""",
    )
    write(
        wiki / "topics" / "local-models.md",
        """---
title: Local Models
category: topic
slug: local-models
entity_id: topic:local-models
synthesis_state: stage1-placeholder
source_count: 1
source_ids:
  - source-a
tags:
  - infrastructure
---

# Local Models

## Current understanding

Lead.

## Evidence / supporting sources

### Source A (2026-01-02)

- Claim (`evidence-id` · supporting · field; [[sources/source-a|Source A]])

## Sources

- [[sources/source-a|Source A]]
""",
    )
    assert validate_wiki(wiki) == []


def test_source_page_still_flags_broken_wikilinks_in_managed_body(tmp_path: Path) -> None:
    """Broken wikilinks in managed source sections should still fail validation."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "sources" / "source-a.md",
        """---
title: Source A
category: source
source_id: source-a
tags:
  - ai-engineering
---

# Source A

## Key insights

None.

## Derived knowledge pages

- [[topics/does-not-exist]]

## Why it matters

It matters.

## Limitations / open questions

None.

## Contradictions / unverified claims

None.

## Source metadata

None.

## Full source text

Raw body.
""",
    )
    issues = validate_wiki(wiki)
    assert any("broken wikilink" in issue.message for issue in issues)


def test_missing_category_reports_issue(tmp_path: Path) -> None:
    """Pages without category frontmatter fail validation."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "topics" / "broken.md",
        """---
title: Broken
---

# Broken
""",
    )
    issues = validate_wiki(wiki)
    assert any("missing frontmatter category" in issue.message for issue in issues)


def test_notes_are_skipped_by_default(tmp_path: Path) -> None:
    """Manual notes outside managed folders are not validated by default."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "notes" / "scratch.md",
        """---
title: Scratch
---

# No category required here
""",
    )
    assert validate_wiki(wiki) == []


def test_evidence_page_requires_monthly_path(tmp_path: Path) -> None:
    """Signal pages must use monthly folder layout."""
    wiki = tmp_path / "wiki"
    write(
        wiki / "signals" / "flat-signal.md",
        """---
title: Signal
category: signal
slug: signal
source_id: source-a
source_date: '2026-04-01'
month: 2026-04
---

# Signal

## Signal

## Evidence / supporting sources

No evidence.

## Source

- [[sources/source-a]]
""",
    )
    issues = validate_wiki(wiki)
    assert any("expected monthly path" in issue.message for issue in issues)
