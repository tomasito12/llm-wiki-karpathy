"""Tests for tag YAML loaders."""

from __future__ import annotations

from pathlib import Path

from src.ingest_review.tags import (
    add_tags_to_list,
    append_tags_to_yaml,
    build_tag_select_options,
    find_similar_tags,
    load_glossary_tags,
    load_impl_study_tags,
    load_model_types,
    load_tag_list,
    load_tool_types,
    load_topic_tags,
    load_trend_tags,
    normalize_tag,
    parse_comma_separated_tags,
    remove_tags_from_list,
    rename_tag_in_list,
    save_tag_list,
)


def test_load_tag_list_accepts_bare_list(tmp_path: Path) -> None:
    """YAML list at root is loaded as strings."""
    p = tmp_path / "t.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")
    assert load_tag_list(p) == ["a", "b"]


def test_load_tag_list_accepts_tags_key(tmp_path: Path) -> None:
    """YAML object with ``tags`` key is supported."""
    p = tmp_path / "t.yaml"
    p.write_text("tags: [x, y]\n", encoding="utf-8")
    assert load_tag_list(p) == ["x", "y"]


def test_load_tag_list_missing_returns_empty(tmp_path: Path) -> None:
    """Missing file yields empty list."""
    assert load_tag_list(tmp_path / "nope.yaml") == []


def test_load_impl_study_tags_from_config(tmp_path: Path) -> None:
    """load_impl_study_tags reads from config/review_tags_impl_study.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_impl_study.yaml").write_text(
        "tags:\n  - voice-ai\n  - pilot-program\n", encoding="utf-8"
    )
    tags = load_impl_study_tags(tmp_path)
    assert tags == ["voice-ai", "pilot-program"]


def test_load_impl_study_tags_missing_returns_empty(tmp_path: Path) -> None:
    """Missing impl-study tag file yields empty list."""
    tags = load_impl_study_tags(tmp_path)
    assert tags == []


def test_load_glossary_tags_from_config(tmp_path: Path) -> None:
    """load_glossary_tags reads from config/review_tags_glossary.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_glossary.yaml").write_text(
        "tags:\n  - agentic-ai\n  - rag\n", encoding="utf-8"
    )
    tags = load_glossary_tags(tmp_path)
    assert tags == ["agentic-ai", "rag"]


def test_load_glossary_tags_empty_returns_empty(tmp_path: Path) -> None:
    """Empty glossary tag file yields empty list."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_glossary.yaml").write_text("tags: []\n", encoding="utf-8")
    tags = load_glossary_tags(tmp_path)
    assert tags == []


def test_load_glossary_tags_missing_returns_empty(tmp_path: Path) -> None:
    """Missing glossary tag file yields empty list."""
    tags = load_glossary_tags(tmp_path)
    assert tags == []


def test_append_tags_to_yaml_adds_and_deduplicates(tmp_path: Path) -> None:
    """append_tags_to_yaml adds new tags without duplicating existing ones."""
    p = tmp_path / "tags.yaml"
    p.write_text("tags:\n  - alpha\n  - beta\n", encoding="utf-8")
    append_tags_to_yaml(p, ["beta", "gamma", "delta"])
    result = load_tag_list(p)
    assert "alpha" in result
    assert "beta" in result
    assert "gamma" in result
    assert "delta" in result
    assert result.count("beta") == 1


def test_append_tags_to_yaml_creates_file(tmp_path: Path) -> None:
    """append_tags_to_yaml creates the file if it does not exist."""
    p = tmp_path / "new_tags.yaml"
    append_tags_to_yaml(p, ["one", "two"])
    result = load_tag_list(p)
    assert "one" in result
    assert "two" in result


def test_append_tags_to_yaml_noop_when_all_exist(tmp_path: Path) -> None:
    """No write when all tags already exist."""
    p = tmp_path / "tags.yaml"
    content = "tags:\n  - alpha\n"
    p.write_text(content, encoding="utf-8")
    append_tags_to_yaml(p, ["alpha"])
    assert p.read_text(encoding="utf-8") == content


def test_load_topic_tags_from_config(tmp_path: Path) -> None:
    """load_topic_tags reads from config/review_tags_topics.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_topics.yaml").write_text(
        "tags:\n  - context-engineering\n  - evaluation\n", encoding="utf-8"
    )
    tags = load_topic_tags(tmp_path)
    assert tags == ["context-engineering", "evaluation"]


def test_load_topic_tags_missing_returns_empty(tmp_path: Path) -> None:
    """Missing topic tag file yields empty list."""
    tags = load_topic_tags(tmp_path)
    assert tags == []


def test_load_topic_tags_empty_returns_empty(tmp_path: Path) -> None:
    """Empty topic tag file yields empty list."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_topics.yaml").write_text("tags: []\n", encoding="utf-8")
    tags = load_topic_tags(tmp_path)
    assert tags == []


def test_load_trend_tags_from_config(tmp_path: Path) -> None:
    """load_trend_tags reads from config/review_tags_trends.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_trends.yaml").write_text(
        "tags:\n  - cost-dynamics\n  - adoption\n", encoding="utf-8"
    )
    tags = load_trend_tags(tmp_path)
    assert tags == ["cost-dynamics", "adoption"]


def test_load_trend_tags_missing_returns_empty(tmp_path: Path) -> None:
    """Missing trend tag file yields empty list."""
    tags = load_trend_tags(tmp_path)
    assert tags == []


def test_load_howto_tags_delegates_to_topics(tmp_path: Path) -> None:
    """How-to tags use the topic vocabulary."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_topics.yaml").write_text(
        "tags:\n  - agent-systems\n  - orchestration\n", encoding="utf-8"
    )
    from src.ingest_review.tags import load_howto_tags

    assert load_howto_tags(tmp_path) == ["agent-systems", "orchestration"]


def test_load_tool_tags_from_config(tmp_path: Path) -> None:
    """load_tool_tags reads from config/review_tags_tools.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_tools.yaml").write_text(
        "tags:\n  - cli-tool\n  - coding\n", encoding="utf-8"
    )
    from src.ingest_review.tags import load_tool_tags

    assert load_tool_tags(tmp_path) == ["cli-tool", "coding"]


def test_load_model_tags_from_config(tmp_path: Path) -> None:
    """load_model_tags reads from config/review_tags_models.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tags_models.yaml").write_text("tags:\n  - reasoning-model\n", encoding="utf-8")
    from src.ingest_review.tags import load_model_tags

    assert load_model_tags(tmp_path) == ["reasoning-model"]


def test_load_tool_types_from_config(tmp_path: Path) -> None:
    """load_tool_types reads from config/review_tool_types.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tool_types.yaml").write_text(
        "tags:\n  - coding-agent\n  - mcp-server\n", encoding="utf-8"
    )
    types = load_tool_types(tmp_path)
    assert types == ["coding-agent", "mcp-server"]


def test_load_tool_types_missing_returns_empty(tmp_path: Path) -> None:
    """Missing tool types file yields empty list."""
    types = load_tool_types(tmp_path)
    assert types == []


def test_load_tool_types_empty_returns_empty(tmp_path: Path) -> None:
    """Empty tool types file yields empty list."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_tool_types.yaml").write_text("tags: []\n", encoding="utf-8")
    types = load_tool_types(tmp_path)
    assert types == []


def test_load_model_types_from_config(tmp_path: Path) -> None:
    """load_model_types reads from config/review_model_types.yaml."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_model_types.yaml").write_text(
        "tags:\n  - frontier-model\n  - coding-model\n", encoding="utf-8"
    )
    types = load_model_types(tmp_path)
    assert types == ["frontier-model", "coding-model"]


def test_load_model_types_missing_returns_empty(tmp_path: Path) -> None:
    """Missing model types file yields empty list."""
    types = load_model_types(tmp_path)
    assert types == []


def test_load_model_types_empty_returns_empty(tmp_path: Path) -> None:
    """Empty model types file yields empty list."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "review_model_types.yaml").write_text("tags: []\n", encoding="utf-8")
    types = load_model_types(tmp_path)
    assert types == []


def test_normalize_tag_kebab_case() -> None:
    """normalize_tag lowercases, strips, and hyphenates."""
    assert normalize_tag("Foo Bar") == "foo-bar"
    assert normalize_tag("  AI_Safety  ") == "ai-safety"
    assert normalize_tag("") == ""


def test_find_similar_tags_detects_prefix_family() -> None:
    """Near-duplicate detection flags overlapping token families."""
    allowlist = ["agent-workflow", "evaluation", "rag"]
    similar = find_similar_tags("agentic-workflows", allowlist)
    assert "agent-workflow" in similar


def test_find_similar_tags_exact_match_returns_empty() -> None:
    """Exact allowlist match does not trigger similar-tag warnings."""
    allowlist = ["orchestration"]
    assert find_similar_tags("orchestration", allowlist) == []


def test_build_tag_select_options_includes_orphan_llm_tags() -> None:
    """Select options include allowlist plus LLM values not on the list."""
    opts = build_tag_select_options(
        ["rag", "evaluation"],
        {"primary_tag": "orphan-tag", "secondary_tag": ""},
    )
    assert opts[0] == ""
    assert "rag" in opts
    assert "orphan-tag" in opts


def test_append_tags_to_yaml_normalizes_new_tags(tmp_path: Path) -> None:
    """New tags are normalized before append."""
    p = tmp_path / "tags.yaml"
    p.write_text("tags:\n  - alpha\n", encoding="utf-8")
    append_tags_to_yaml(p, ["Foo Bar"])
    assert "foo-bar" in load_tag_list(p)


def test_save_tag_list_replaces_and_sorts(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["zebra", "alpha", "alpha"], comment="test list")
    assert load_tag_list(p) == ["alpha", "zebra"]
    text = p.read_text(encoding="utf-8")
    assert text.startswith("# test list")


def test_add_tags_to_list_returns_added_slugs(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["alpha"])
    added = add_tags_to_list(p, ["beta", "alpha", "Beta"])
    assert added == ["beta"]
    assert load_tag_list(p) == ["alpha", "beta"]


def test_remove_tags_from_list(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["alpha", "beta", "gamma"])
    removed = remove_tags_from_list(p, ["beta", "missing"])
    assert removed == ["beta"]
    assert load_tag_list(p) == ["alpha", "gamma"]


def test_remove_tags_from_list_empty_remove_set_is_noop(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["alpha"])
    assert remove_tags_from_list(p, ["", "   "]) == []
    assert load_tag_list(p) == ["alpha"]


def test_rename_tag_in_list(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["old-name", "other"])
    rename_tag_in_list(p, "old-name", "new-name")
    assert load_tag_list(p) == ["new-name", "other"]


def test_rename_tag_in_list_same_slug_is_noop(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["alpha"])
    rename_tag_in_list(p, "alpha", "alpha")
    assert load_tag_list(p) == ["alpha"]


def test_rename_tag_in_list_raises_when_missing(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["alpha"])
    try:
        rename_tag_in_list(p, "missing", "new")
    except ValueError as exc:
        assert "not in allowlist" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_rename_tag_in_list_raises_when_duplicate_target(tmp_path: Path) -> None:
    p = tmp_path / "tags.yaml"
    save_tag_list(p, ["alpha", "beta"])
    try:
        rename_tag_in_list(p, "alpha", "beta")
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_parse_comma_separated_tags() -> None:
    assert parse_comma_separated_tags("foo, Bar Baz") == ["foo", "bar-baz"]
