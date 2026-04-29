from pathlib import Path

from src.pipeline.models import DiscoveredItem
from src.pipeline.parser.medium_parser import parse_medium_html


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
