"""CLI for previewing Stage 2 synthesis prompts without LLM calls."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.ingest_review.paths import repo_root
from src.pipeline.atomic import atomic_write_json, atomic_write_text
from src.wiki_synthesis.cache import load_cache_entry
from src.wiki_synthesis.planner import load_graph_export
from src.wiki_synthesis.prompts import PromptBundle, build_prompt_bundle, find_knowledge_page

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-synthesis-prompt argument parser."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="wiki-synthesis-prompt",
        description="Preview one Stage 2 synthesis prompt without making an LLM call.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=root / "state" / "wiki_render_graph.json",
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=root / "state" / "synthesis",
        help="Directory containing optional previous Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--entity",
        required=True,
        help="Entity id to preview, for example topic:agentic-coding-workflows.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the prompt bundle as JSON instead of readable Markdown.",
    )
    parser.add_argument(
        "--out-path",
        type=Path,
        default=None,
        help="Optional path to write the preview artifact.",
    )
    return parser


def main() -> int:
    """Preview a Stage 2 synthesis prompt."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    graph = load_graph_export(args.graph_path.resolve())
    page = find_knowledge_page(graph, entity_id=args.entity)
    previous_cache = load_cache_entry(
        args.cache_dir.resolve(),
        category=str(page.get("category", "")),
        slug=str(page.get("slug", "")),
    )
    bundle = build_prompt_bundle(graph, entity_id=args.entity, previous_cache=previous_cache)
    if args.json:
        payload = bundle.to_dict()
        output = json.dumps(payload, indent=2, sort_keys=True)
        if args.out_path:
            atomic_write_json(args.out_path.resolve(), payload)
    else:
        output = _markdown_preview(bundle)
        if args.out_path:
            atomic_write_text(args.out_path.resolve(), output)
    print(output)
    LOGGER.info(
        "wiki-synthesis-prompt complete entity=%s prompt_version=%s input_hash=%s",
        bundle.entity_id,
        bundle.prompt_version,
        bundle.synthesis_input_hash,
    )
    return 0


def _markdown_preview(bundle: PromptBundle) -> str:
    """Return a readable prompt preview."""
    return "\n\n".join(
        [
            f"# Synthesis Prompt Preview: {bundle.entity_id}",
            "## Metadata",
            "\n".join(
                [
                    f"- title: {bundle.title}",
                    f"- category: {bundle.category}",
                    f"- slug: {bundle.slug}",
                    f"- prompt_version: {bundle.prompt_version}",
                    f"- synthesis_input_hash: `{bundle.synthesis_input_hash}`",
                    f"- cached_input_hash: `{bundle.cached_input_hash or 'none'}`",
                ]
            ),
            "## System Prompt",
            bundle.system_prompt,
            "## User Prompt",
            bundle.user_prompt,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
