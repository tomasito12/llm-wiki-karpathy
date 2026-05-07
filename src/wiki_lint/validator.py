"""Validate wiki markdown contracts, links, and index parity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_TAGS = {"ai-engineering", "tools", "models"}
ALLOWED_TYPES = {
    "foundation-model",
    "foundation-models-index",
    "glossary",
    "glossary-term",
    "index",
    "log",
    "question",
    "questions-catalog",
    "source",
    "style",
    "tool",
    "tools-category-index",
    "tools-index",
}

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
HEADING_RE = re.compile(r"^(##+)\s+(.+?)\s*$", re.MULTILINE)
INSTRUCTION_RELPATHS = {
    "AGENTS.md",
    "ingest-templates.md",
    "stage1-classifier.md",
    "stage2-artifact-router.md",
}


@dataclass(frozen=True)
class WikiLintIssue:
    """One wiki validation finding."""

    path: str
    message: str


@dataclass(frozen=True)
class WikiPage:
    """Parsed wiki markdown page."""

    path: Path
    relpath: str
    frontmatter: dict[str, Any]
    body: str

    @property
    def page_type(self) -> str | None:
        """Return frontmatter ``type`` if present."""
        value = self.frontmatter.get("type")
        return str(value) if isinstance(value, str) else None

    @property
    def tags(self) -> list[str]:
        """Return frontmatter tags as strings."""
        value = self.frontmatter.get("tags")
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]


def parse_frontmatter_value(raw: str) -> str | list[str]:
    """Parse the scalar/list subset of YAML used by this wiki."""
    text = raw.strip()
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",")]
    return text.strip("\"'")


def parse_markdown(path: Path, wiki_root: Path) -> WikiPage:
    """Parse frontmatter and body from one markdown file."""
    text = path.read_text(encoding="utf-8")
    frontmatter: dict[str, Any] = {}
    body = text
    if text.startswith("---\n"):
        try:
            _start, yaml_text, body = text.split("---\n", maxsplit=2)
        except ValueError:
            yaml_text = ""
        current_list_key: str | None = None
        for line in yaml_text.splitlines():
            if not line.strip():
                continue
            if line.startswith("  - ") and current_list_key is not None:
                values = frontmatter.setdefault(current_list_key, [])
                if isinstance(values, list):
                    values.append(line[4:].strip().strip("\"'"))
                continue
            if ":" not in line:
                current_list_key = None
                continue
            key, value = line.split(":", maxsplit=1)
            key = key.strip()
            value = value.strip()
            if value:
                frontmatter[key] = parse_frontmatter_value(value)
                current_list_key = None
            else:
                frontmatter[key] = []
                current_list_key = key
    return WikiPage(
        path=path,
        relpath=path.relative_to(wiki_root).as_posix(),
        frontmatter=frontmatter,
        body=body,
    )


def extract_headings(body: str, *, level: int = 2) -> list[str]:
    """Return headings at the requested markdown level without hashes."""
    return [
        match.group(2).strip()
        for match in HEADING_RE.finditer(body)
        if len(match.group(1)) == level
    ]


def extract_wikilinks(body: str) -> list[str]:
    """Return wikilink targets from markdown body."""
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(body)]


def read_wiki_pages(wiki_root: Path) -> dict[str, WikiPage]:
    """Read all markdown files below ``wiki_root`` keyed by relative path."""
    pages: dict[str, WikiPage] = {}
    for path in sorted(wiki_root.rglob("*.md")):
        page = parse_markdown(path, wiki_root)
        pages[page.relpath] = page
    return pages


def validate_wiki(wiki_root: Path) -> list[WikiLintIssue]:
    """Validate wiki markdown files below ``wiki_root``."""
    pages = read_wiki_pages(wiki_root)
    issues: list[WikiLintIssue] = []
    for page in pages.values():
        if page.relpath in INSTRUCTION_RELPATHS:
            continue
        issues.extend(validate_frontmatter(page))
        issues.extend(validate_headings(page))
        issues.extend(validate_wikilinks(page, pages))
    issues.extend(validate_tools_parity(pages))
    issues.extend(validate_foundation_models_parity(pages))
    issues.extend(validate_glossary_parity(pages))
    issues.extend(validate_question_catalog(pages))
    return sorted(issues, key=lambda issue: (issue.path, issue.message))


def validate_frontmatter(page: WikiPage) -> list[WikiLintIssue]:
    """Validate frontmatter keys shared across page contracts."""
    issues: list[WikiLintIssue] = []
    page_type = page.page_type
    if page_type is None:
        issues.append(WikiLintIssue(page.relpath, "missing frontmatter type"))
    elif page_type not in ALLOWED_TYPES:
        issues.append(WikiLintIssue(page.relpath, f"unsupported type: {page_type}"))

    for tag in page.tags:
        if tag not in ALLOWED_TAGS:
            issues.append(WikiLintIssue(page.relpath, f"unsupported tag: {tag}"))

    if page_type in {"tool", "source", "question", "glossary-term", "foundation-model"}:
        for key in ("title", "created", "updated"):
            if not page.frontmatter.get(key):
                issues.append(WikiLintIssue(page.relpath, f"missing frontmatter key: {key}"))

    if page_type == "tool" and "tools" not in page.tags:
        issues.append(WikiLintIssue(page.relpath, "tool page must include tag: tools"))
    if page_type == "foundation-model" and "models" not in page.tags:
        issues.append(WikiLintIssue(page.relpath, "foundation-model page must include tag: models"))
    if page_type == "source" and "tools" in page.tags:
        for key in ("author", "publication"):
            if not page.frontmatter.get(key):
                issues.append(WikiLintIssue(page.relpath, f"tools source missing: {key}"))
    return issues


def validate_headings(page: WikiPage) -> list[WikiLintIssue]:
    """Validate heading contracts for known page types."""
    headings = extract_headings(page.body)
    page_type = page.page_type
    if page_type == "tool":
        return expect_exact_headings(
            page,
            headings,
            [
                "What problem does this tool solve?",
                "Properties",
                "Author assessments",
                "Sources",
            ],
        )
    if page_type == "glossary-term":
        return expect_exact_headings(
            page, headings, ["Definition", "Usage Notes", "Disagreements", "Sources"]
        )
    if page_type == "foundation-model":
        expected = [
            "Summary",
            "Technical snapshot",
            "Access and licensing",
            "Evaluation claims",
            "Limitations and risks",
            "Timeline",
            "Commentary",
            "Sources",
        ]
        without_commentary = [heading for heading in expected if heading != "Commentary"]
        if headings == expected or headings == without_commentary:
            return []
        return [WikiLintIssue(page.relpath, f"unexpected foundation-model headings: {headings}")]
    if page_type == "question":
        if not headings or headings[0] != "Synthesized answer" or headings[-1:] != ["Sources"]:
            return [
                WikiLintIssue(
                    page.relpath, "question must start with Synthesized answer and end with Sources"
                )
            ]
    if page_type == "source":
        return validate_source_headings(page, headings)
    return []


def expect_exact_headings(
    page: WikiPage,
    actual: list[str],
    expected: list[str],
) -> list[WikiLintIssue]:
    """Return an issue if heading order differs from expected."""
    if actual == expected:
        return []
    return [WikiLintIssue(page.relpath, f"unexpected headings: {actual}")]


def validate_source_headings(page: WikiPage, headings: list[str]) -> list[WikiLintIssue]:
    """Validate source-page heading variants."""
    if "tools" in page.tags:
        if "Questions addressed by the text" in headings:
            return [
                WikiLintIssue(
                    page.relpath, "tools source must not include Questions addressed by the text"
                )
            ]
        coverage = [
            heading
            for heading in headings
            if heading
            in {"Apps and platforms covered", "Foundation models covered", "MCP servers covered"}
        ]
        if not coverage:
            return [WikiLintIssue(page.relpath, "tools source must include a coverage section")]
        coverage_order = [
            "Apps and platforms covered",
            "Foundation models covered",
            "MCP servers covered",
        ]
        if coverage != [heading for heading in coverage_order if heading in coverage]:
            return [WikiLintIssue(page.relpath, f"coverage sections out of order: {coverage}")]
        required_tail = [
            "Why it matters",
            "Context and Limitations",
            "Contradictions / Unverified Claims",
            "Sources",
        ]
        for heading in required_tail:
            if heading not in headings:
                return [WikiLintIssue(page.relpath, f"missing source heading: {heading}")]
        return []

    if headings[:1] != ["Questions addressed by the text"]:
        return [
            WikiLintIssue(
                page.relpath, "standard source must start with Questions addressed by the text"
            )
        ]
    for heading in [
        "Why it matters",
        "Context and Limitations",
        "Contradictions / Unverified Claims",
        "Sources",
    ]:
        if heading not in headings:
            return [WikiLintIssue(page.relpath, f"missing source heading: {heading}")]
    return []


def validate_wikilinks(page: WikiPage, pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate that wikilink targets resolve to markdown files where appropriate."""
    issues: list[WikiLintIssue] = []
    for target in extract_wikilinks(page.body):
        normalized = normalize_wikilink_target(target)
        if normalized is None:
            continue
        candidates = [f"{normalized}.md", f"{normalized}/index.md"]
        if not any(candidate in pages for candidate in candidates):
            issues.append(WikiLintIssue(page.relpath, f"broken wikilink: [[{target}]]"))
    return issues


def normalize_wikilink_target(target: str) -> str | None:
    """Normalize a wikilink target to a wiki-root relative path or None to skip."""
    clean = target.strip().strip("/")
    if not clean or clean.startswith("http"):
        return None
    if clean.startswith("wiki/"):
        clean = clean.removeprefix("wiki/")
    if clean.endswith(".md"):
        clean = clean.removesuffix(".md")
    return clean


def validate_tools_parity(pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate tools master/category/page parity."""
    issues: list[WikiLintIssue] = []
    tool_pages = sorted(
        path
        for path, page in pages.items()
        if page.page_type == "tool" and path.startswith("tools/")
    )
    category_indexes = sorted(
        path
        for path, page in pages.items()
        if page.page_type == "tools-category-index" and path.startswith("tools/")
    )
    master = pages.get("tools/index.md")
    if tool_pages and master is None:
        issues.append(WikiLintIssue("tools/index.md", "missing tools master index"))
        return issues

    if master is not None:
        for index_path in category_indexes:
            link = f"tools/{Path(index_path).parent.name}/index"
            if link not in extract_wikilinks(master.body):
                issues.append(WikiLintIssue("tools/index.md", f"missing category row: [[{link}]]"))

    for tool_path in tool_pages:
        category = Path(tool_path).parent.as_posix()
        index_path = f"{category}/index.md"
        if index_path not in pages:
            issues.append(WikiLintIssue(index_path, f"missing category index for {tool_path}"))
            continue
        link = tool_path.removesuffix(".md")
        if link not in extract_wikilinks(pages[index_path].body):
            issues.append(WikiLintIssue(index_path, f"missing tool row: [[{link}]]"))
    return issues


def validate_foundation_models_parity(pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate foundation model index/page parity."""
    issues: list[WikiLintIssue] = []
    model_pages = sorted(
        path
        for path, page in pages.items()
        if page.page_type == "foundation-model" and path.startswith("foundation-models/")
    )
    index = pages.get("foundation-models/index.md")
    if model_pages and index is None:
        issues.append(
            WikiLintIssue("foundation-models/index.md", "missing foundation models index")
        )
        return issues
    if index is None:
        return issues
    links = set(extract_wikilinks(index.body))
    for model_path in model_pages:
        link = model_path.removesuffix(".md")
        if link not in links:
            issues.append(
                WikiLintIssue("foundation-models/index.md", f"missing model row: [[{link}]]")
            )
    for link in links:
        if link.startswith("foundation-models/") and f"{link}.md" not in pages:
            issues.append(
                WikiLintIssue("foundation-models/index.md", f"index row target missing: [[{link}]]")
            )
    return issues


def validate_glossary_parity(pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate glossary index/page parity."""
    issues: list[WikiLintIssue] = []
    term_pages = sorted(
        path
        for path, page in pages.items()
        if page.page_type == "glossary-term" and path.startswith("glossary/terms/")
    )
    index = pages.get("glossary/index.md")
    if term_pages and index is None:
        issues.append(WikiLintIssue("glossary/index.md", "missing glossary index"))
        return issues
    if index is None:
        return issues
    links = set(extract_wikilinks(index.body))
    for term_path in term_pages:
        link = term_path.removesuffix(".md")
        if link not in links:
            issues.append(WikiLintIssue("glossary/index.md", f"missing term row: [[{link}]]"))
    return issues


def validate_question_catalog(pages: dict[str, WikiPage]) -> list[WikiLintIssue]:
    """Validate question catalog wikilinks resolve to question pages."""
    catalog = pages.get("questions/question-catalog.md")
    if catalog is None:
        return []
    issues: list[WikiLintIssue] = []
    for link in extract_wikilinks(catalog.body):
        target = normalize_wikilink_target(link)
        if target is not None and f"{target}.md" not in pages:
            issues.append(
                WikiLintIssue(catalog.relpath, f"question catalog target missing: [[{link}]]")
            )
    return issues
