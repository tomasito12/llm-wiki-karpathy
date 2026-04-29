from pathlib import Path

from src.pipeline.models import DiscoveredItem, ParsedDocument
from src.pipeline.staging import stage_document


def test_stage_document_writes_markdown_file(tmp_path: Path) -> None:
    item = DiscoveredItem(
        item_id="deadbeef",
        source_name="example-medium",
        source_url="https://medium.com/@example",
        url="https://medium.com/@example/post",
        title="My Test Title",
        published_at=None,
    )
    parsed = ParsedDocument(
        item=item,
        markdown="# Hello\n\nBody\n",
        author=None,
        canonical_url=item.url,
        claps=None,
        author_followers=None,
        responses=[],
    )

    output = stage_document(parsed=parsed, staging_dir=tmp_path)
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith("# Hello")
