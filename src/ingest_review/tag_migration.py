"""Migrate review artifact tags from legacy slugs to the redesigned ontology."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from src.ingest_review.artifact import load_artifact, save_artifact
from src.ingest_review.paths import repo_root
from src.ingest_review.tags import normalize_tag, normalize_tag_list

REVIEW_LIST_TAG_MAP: dict[str, str] = {
    "topics": "topics",
    "how_to": "howto",
    "glossary": "glossary",
    "industry_trends": "trends",
    "roundup_signals": "trends",
    "interview_insights": "topics",
    "implementation_studies": "impl_study",
    "tools": "tool_tags",
    "foundation_models": "model_tags",
}


@dataclass
class MigrationReport:
    """Per-artifact migration statistics."""

    source_id: str
    remapped: int = 0
    dropped: int = 0
    unmapped_slugs: list[str] = field(default_factory=list)


@dataclass
class MigrationSummary:
    """Aggregate result of migrating many review artifacts."""

    artifacts_processed: int = 0
    reports: list[MigrationReport] = field(default_factory=list)

    @property
    def total_remapped(self) -> int:
        return sum(r.remapped for r in self.reports)

    @property
    def total_dropped(self) -> int:
        return sum(r.dropped for r in self.reports)


def default_migration_map_path(root: Path | None = None) -> Path:
    """Path to ``config/tag_migration.yaml``."""
    return (root or repo_root()) / "config" / "tag_migration.yaml"


def load_migration_map(path: Path | None = None) -> dict[str, dict[str, str]]:
    """Load per-taxonomy old→new slug maps from YAML."""
    map_path = path or default_migration_map_path()
    if not map_path.is_file():
        return {}
    raw = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, str]] = {}
    for section, mapping in raw.items():
        if not isinstance(mapping, dict):
            continue
        section_map: dict[str, str] = {}
        for old, new in mapping.items():
            old_n = normalize_tag(str(old))
            new_n = normalize_tag(str(new))
            if old_n and new_n:
                section_map[old_n] = new_n
        out[str(section)] = section_map
    return out


def migrate_slug(slug: str, mapping: dict[str, str]) -> str | None:
    """Return mapped slug, or *slug* unchanged if not in map, or None if dropped."""
    norm = normalize_tag(slug)
    if not norm:
        return None
    if norm in mapping:
        return mapping[norm]
    return norm


def migrate_tag_list(
    slugs: list[str],
    mapping: dict[str, str],
    *,
    report: MigrationReport | None = None,
) -> list[str]:
    """Map each slug; dedupe; drop unmapped-only when mapping explicitly omits identity."""
    result: list[str] = []
    for raw in slugs:
        norm = normalize_tag(str(raw))
        if not norm:
            continue
        if norm in mapping:
            mapped = mapping[norm]
            if report is not None and mapped != norm:
                report.remapped += 1
            if mapped and mapped not in result:
                result.append(mapped)
        elif norm in result:
            continue
        else:
            if report is not None:
                if norm not in report.unmapped_slugs:
                    report.unmapped_slugs.append(norm)
            if norm not in result:
                result.append(norm)
    return normalize_tag_list(result, cap=0)


def _migrate_llm_item_tags(
    llm_item: dict[str, Any],
    mapping: dict[str, str],
    *,
    report: MigrationReport,
) -> None:
    proposed = llm_item.get("proposed_tags")
    if isinstance(proposed, list):
        llm_item["proposed_tags"] = migrate_tag_list(
            [str(x) for x in proposed],
            mapping,
            report=report,
        )
    suggested = llm_item.get("suggested_new_tags")
    if isinstance(suggested, list):
        llm_item["suggested_new_tags"] = migrate_tag_list(
            [str(x) for x in suggested],
            mapping,
            report=report,
        )
    for legacy_key in ("primary_tag", "secondary_tag"):
        raw = str(llm_item.get(legacy_key) or "").strip()
        if not raw:
            continue
        mapped = migrate_slug(raw, mapping)
        if mapped:
            llm_item[legacy_key] = mapped
        else:
            llm_item[legacy_key] = ""


def _migrate_proposal_node(
    node: dict[str, Any],
    tag_mapping: dict[str, str],
    *,
    report: MigrationReport,
    type_mapping: dict[str, str] | None = None,
) -> None:
    llm_item = node.get("llm_item")
    if isinstance(llm_item, dict):
        _migrate_llm_item_tags(llm_item, tag_mapping, report=report)
        if type_mapping:
            types = llm_item.get("proposed_types")
            if isinstance(types, list):
                new_types: list[str] = []
                for raw in types:
                    norm = normalize_tag(str(raw))
                    if not norm:
                        continue
                    mapped = type_mapping.get(norm, norm)
                    if mapped and mapped not in new_types:
                        new_types.append(mapped)
                llm_item["proposed_types"] = new_types[:5]
            pnt = llm_item.get("proposed_new_type")
            if pnt:
                mapped_type = type_mapping.get(normalize_tag(str(pnt)), normalize_tag(str(pnt)))
                llm_item["proposed_new_type"] = mapped_type or None

    tags = node.get("tags")
    if isinstance(tags, dict):
        final = tags.get("final_tags")
        if isinstance(final, list):
            tags["final_tags"] = migrate_tag_list(
                [str(x) for x in final],
                tag_mapping,
                report=report,
            )
        approved = tags.get("approved_new_tags")
        if isinstance(approved, list):
            tags["approved_new_tags"] = migrate_tag_list(
                [str(x) for x in approved],
                tag_mapping,
                report=report,
            )

    types_node = node.get("types")
    if isinstance(types_node, dict) and type_mapping:
        for key in ("approved_types", "reviewer_types_added"):
            raw_list = types_node.get(key)
            if isinstance(raw_list, list):
                types_node[key] = migrate_tag_list(
                    [str(x) for x in raw_list],
                    type_mapping,
                    report=report,
                )
        pnt = types_node.get("proposed_new_type")
        if pnt:
            mapped = type_mapping.get(normalize_tag(str(pnt)), normalize_tag(str(pnt)))
            types_node["proposed_new_type"] = mapped


def migrate_review_artifact(
    artifact: dict[str, Any],
    migration_map: dict[str, dict[str, str]],
    *,
    source_id: str = "",
) -> tuple[dict[str, Any], MigrationReport]:
    """Migrate tag fields in one review artifact in place."""
    sid = source_id or str((artifact.get("source") or {}).get("source_id") or "")
    report = MigrationReport(source_id=sid)
    review = artifact.get("review") or {}
    llm = artifact.get("llm_output") or {}

    for list_key, map_key in REVIEW_LIST_TAG_MAP.items():
        tag_mapping = migration_map.get(map_key, {})
        type_mapping = None
        if list_key == "tools":
            type_mapping = migration_map.get("tool_types", {})
        elif list_key == "foundation_models":
            type_mapping = migration_map.get("model_types", {})

        nodes = review.get(list_key)
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dict):
                    _migrate_proposal_node(
                        node,
                        tag_mapping,
                        report=report,
                        type_mapping=type_mapping,
                    )

        llm_items = llm.get(list_key)
        if isinstance(llm_items, list):
            for item in llm_items:
                if isinstance(item, dict):
                    _migrate_llm_item_tags(item, tag_mapping, report=report)
                    if type_mapping:
                        types = item.get("proposed_types")
                        if isinstance(types, list):
                            new_types: list[str] = []
                            for raw in types:
                                norm = normalize_tag(str(raw))
                                if not norm:
                                    continue
                                mapped = type_mapping.get(norm, norm)
                                if mapped and mapped not in new_types:
                                    new_types.append(mapped)
                            item["proposed_types"] = new_types[:5]

    return artifact, report


def migrate_reviews_root(
    reviews_root: Path,
    migration_map: dict[str, dict[str, str]],
    *,
    dry_run: bool = False,
) -> MigrationSummary:
    """Migrate every ``review.json`` under *reviews_root*."""
    summary = MigrationSummary()
    if not reviews_root.is_dir():
        return summary

    for path in sorted(reviews_root.glob("*/review.json")):
        artifact = load_artifact(path)
        if not artifact:
            continue
        source_id = path.parent.name
        _, report = migrate_review_artifact(artifact, migration_map, source_id=source_id)
        summary.artifacts_processed += 1
        summary.reports.append(report)
        if not dry_run:
            save_artifact(path, artifact)

    return summary


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI parser for tag migration."""
    root = repo_root()
    parser = argparse.ArgumentParser(
        prog="tag-migrate",
        description="Migrate review.json tag slugs to the redesigned ontology.",
    )
    parser.add_argument(
        "--reviews-root",
        type=Path,
        default=root / "state" / "reviews",
        help="Directory containing per-source review.json artifacts.",
    )
    parser.add_argument(
        "--map",
        type=Path,
        default=default_migration_map_path(root),
        help="YAML migration map (default: config/tag_migration.yaml).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing review.json files.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional JSON path for migration report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    migration_map = load_migration_map(args.map)
    summary = migrate_reviews_root(
        args.reviews_root,
        migration_map,
        dry_run=args.dry_run,
    )
    print(
        f"{'[dry-run] ' if args.dry_run else ''}"
        f"Processed {summary.artifacts_processed} artifact(s); "
        f"remapped {summary.total_remapped} slug(s); "
        f"{summary.total_dropped} unmapped slug occurrence(s) logged."
    )
    if args.report:
        payload = {
            "artifacts_processed": summary.artifacts_processed,
            "total_remapped": summary.total_remapped,
            "reports": [
                {
                    "source_id": r.source_id,
                    "remapped": r.remapped,
                    "unmapped_slugs": r.unmapped_slugs,
                }
                for r in summary.reports
                if r.unmapped_slugs or r.remapped
            ],
        }
        from src.pipeline.atomic import atomic_write_json

        atomic_write_json(args.report, payload)
        print(f"Wrote report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
