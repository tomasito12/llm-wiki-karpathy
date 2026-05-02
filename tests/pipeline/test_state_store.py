from pathlib import Path

from src.pipeline.state_store import SourceStateStore, canonicalize_url, make_item_id


def test_canonicalize_url_removes_query_fragment_and_slash() -> None:
    assert (
        canonicalize_url("https://example.com/@example/post/?utm_source=rss#part")
        == "https://example.com/@example/post"
    )


def test_make_item_id_is_stable() -> None:
    first = make_item_id("https://example.com/@example/post?utm_source=x")
    second = make_item_id("https://example.com/@example/post")
    assert first == second


def test_state_store_upsert_and_seen_lookup(tmp_path: Path) -> None:
    state_path = tmp_path / "sources_seen.json"
    store = SourceStateStore(state_path)

    assert not store.is_seen("example", "item-1")

    store.upsert_item(
        source_name="example",
        item_id="item-1",
        title="Title",
        canonical_url="https://example.com/x",
        published_at=None,
        local_path=None,
        status="parsed",
    )

    assert store.is_seen("example", "item-1")
    loaded = store.load()
    assert loaded["example"]["item-1"].status == "parsed"
