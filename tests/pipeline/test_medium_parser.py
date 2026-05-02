from pathlib import Path

from src.pipeline.models import DiscoveredItem
from src.pipeline.parser.medium_parser import (
    _detect_browser_executable,
    _looks_like_challenge,
    _looks_like_member_preview,
    parse_medium_html,
)


def test_parse_medium_html_extracts_main_content_and_strips_noise() -> None:
    fixture_path = Path("tests/fixtures/medium_article.html")
    html = fixture_path.read_text(encoding="utf-8")
    item = DiscoveredItem(
        item_id="abc123",
        source_name="example-medium",
        source_url="https://medium.com/@example",
        url="https://medium.com/@example/fixture-article",
        title="Fallback title",
        published_at="Mon, 01 Jan 2024 00:00:00 GMT",
    )

    parsed = parse_medium_html(item=item, html=html)

    assert parsed.author == "Fixture Author"
    assert parsed.canonical_url == "https://medium.com/@example/fixture-article"
    assert parsed.claps == 42
    assert parsed.author_followers is None
    assert parsed.responses == ["Great explanation and very practical recommendations."]
    assert "# Fixture Article Heading" in parsed.markdown
    assert "Top navigation" not in parsed.markdown
    assert "Read more from this publication" not in parsed.markdown
    assert "- First bullet" in parsed.markdown
    assert "> Important quote" in parsed.markdown
    assert "- Claps: 42" in parsed.markdown
    assert "## Response Snippets" in parsed.markdown


def test_looks_like_member_preview_detects_cropped_member_story() -> None:
    body = "Member-only story\n\nSome text here and then it cuts off…"
    assert _looks_like_member_preview(body)


def test_looks_like_challenge_detects_cloudflare_page() -> None:
    html = "<html><title>Just a moment...</title>https://challenges.cloudflare.com</html>"
    assert _looks_like_challenge(html=html, status_code=403)


def test_detect_browser_executable_returns_none_for_unknown_path(tmp_path: Path) -> None:
    assert _detect_browser_executable(tmp_path / "unknown") is None
