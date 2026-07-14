"""CLI for read-only wiki operations status."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import cast

from src.ingest_review.paths import repo_root
from src.wiki_ops.migration_plan import (
    build_migration_plan,
    format_migration_plan_text,
    migration_plan_to_json,
)
from src.wiki_ops.release_manifest import (
    CheckpointKind,
    build_release_manifest,
    format_release_dry_run_text,
    write_release_manifest,
)
from src.wiki_ops.release_restore import (
    ReleaseRestoreError,
    format_release_restore_plan_text,
    release_restore_plan_to_json,
    restore_release_from_snapshot,
)
from src.wiki_ops.release_verify import (
    ReleaseSelectionError,
    format_release_verification_text,
    release_verification_to_json,
    verify_release,
)
from src.wiki_ops.retention import (
    RetentionInventory,
    build_retention_recommendations,
    collect_retention_inventory,
    format_retention_text,
)
from src.wiki_ops.retirement_plan import (
    build_retirement_plan,
    format_retirement_plan_text,
    retirement_plan_to_json,
)
from src.wiki_ops.status import (
    OpsStatus,
    OpsStatusConfig,
    collect_ops_status,
    format_text_report,
)
from src.wiki_ops.vault_git_strategy import (
    VaultGitStrategy,
    build_vault_git_recommendations_for_status,
    build_vault_git_strategy,
    format_vault_git_strategy_text,
    vault_git_strategy_to_json,
)
from src.wiki_paths.cli_helpers import (
    add_paths_config_argument,
    load_paths_for_cli,
    paths_with_status_cli_overrides,
)
from src.wiki_paths.config import WikiPaths, WikiPathsConfigError

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the wiki-ops-status argument parser."""
    parser = argparse.ArgumentParser(
        prog="wiki-ops-status",
        description="Summarize wiki source, review, render, synthesis, and artifact state.",
    )
    add_paths_config_argument(parser)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: detected repo root).",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing Readwise raw exports.",
    )
    parser.add_argument(
        "--reviews-dir",
        type=Path,
        default=None,
        help="Directory containing review artifacts.",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=None,
        help="Generated Obsidian wiki directory.",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Path to the wiki-render graph export.",
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=None,
        help="Path to the wiki-render manifest.",
    )
    parser.add_argument(
        "--synthesis-cache-dir",
        type=Path,
        default=None,
        help="Directory containing Stage 2 synthesis cache entries.",
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis preview markdown files.",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis run audit reports.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory containing synthesis backup artifacts.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the status report as JSON.",
    )
    parser.add_argument(
        "--paths-json",
        action="store_true",
        help="Print resolved wiki path configuration as JSON and exit.",
    )
    parser.add_argument(
        "--retention",
        action="store_true",
        help="Append artifact retention inventory to the status report.",
    )
    parser.add_argument(
        "--retention-json",
        action="store_true",
        help="Print artifact retention inventory as JSON and exit.",
    )
    parser.add_argument(
        "--release-dry-run",
        action="store_true",
        help="Preview a release manifest without writing files.",
    )
    parser.add_argument(
        "--release-json",
        action="store_true",
        help="Print a release manifest as JSON without writing files.",
    )
    parser.add_argument(
        "--write-release-manifest",
        action="store_true",
        help="Write a release manifest JSON file under paths.release_dir.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm writing a release manifest.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing release manifest file.",
    )
    parser.add_argument(
        "--release-id",
        default=None,
        help="Optional fixed release id for manifest preview or write.",
    )
    parser.add_argument(
        "--checkpoint-kind",
        default="release",
        choices=("release", "pre_ingest", "pre_review", "pre_synthesis", "pre_render"),
        help="Optional checkpoint kind label recorded in release manifests.",
    )
    parser.add_argument(
        "--snapshot-id",
        default=None,
        help="Optional external snapshot identifier recorded in release manifests.",
    )
    parser.add_argument(
        "--migration-plan",
        action="store_true",
        help="Append knowledge store migration plan to the status report.",
    )
    parser.add_argument(
        "--migration-json",
        action="store_true",
        help="Print knowledge store migration plan as JSON and exit.",
    )
    parser.add_argument(
        "--require-external-knowledge-root",
        action="store_true",
        help="Block migration readiness when knowledge_root equals repo_root.",
    )
    parser.add_argument(
        "--require-external-vault-root",
        action="store_true",
        help="Block migration readiness when vault_root equals repo_root.",
    )
    parser.add_argument(
        "--verify-release",
        metavar="RELEASE_ID",
        default=None,
        help="Verify current knowledge store state against a release manifest (use 'latest').",
    )
    parser.add_argument(
        "--verify-json",
        action="store_true",
        help="Print release verification as JSON only and exit.",
    )
    parser.add_argument(
        "--verify-allow-path-mismatch",
        action="store_true",
        help="Downgrade release path mismatches from error to warning.",
    )
    parser.add_argument(
        "--restore-release",
        metavar="RELEASE_ID",
        default=None,
        help="Restore selected areas from an external snapshot recorded in the release manifest.",
    )
    parser.add_argument(
        "--restore-snapshot-root",
        type=Path,
        default=None,
        help="Root directory of a filesystem snapshot that contains knowledge_root and vault_root.",
    )
    parser.add_argument(
        "--restore-areas",
        default="all",
        help="Comma-separated area keys to restore (default: all).",
    )
    parser.add_argument(
        "--restore-dry-run",
        action="store_true",
        help="Preview restore actions without modifying files.",
    )
    parser.add_argument(
        "--restore-json",
        action="store_true",
        help="Print restore plan/result as JSON.",
    )
    parser.add_argument(
        "--retirement-plan",
        action="store_true",
        help="Append old repo data retirement plan to the status report.",
    )
    parser.add_argument(
        "--retirement-json",
        action="store_true",
        help="Print old repo data retirement plan as JSON and exit.",
    )
    parser.add_argument(
        "--vault-git-strategy",
        action="store_true",
        help="Append private vault Git strategy report to the status output.",
    )
    parser.add_argument(
        "--vault-git-json",
        action="store_true",
        help="Print private vault Git strategy report as JSON and exit.",
    )
    return parser


def config_from_args(args: argparse.Namespace) -> OpsStatusConfig:
    """Build status config from parsed CLI arguments."""
    repo = (args.repo_root or repo_root()).resolve()
    paths = paths_with_status_cli_overrides(
        args,
        load_paths_for_cli(args, repo_root_override=repo),
    )
    return OpsStatusConfig(
        repo_root=repo,
        raw_dir=paths.raw_dir,
        reviews_dir=paths.reviews_dir,
        wiki_dir=paths.wiki_dir,
        graph_path=paths.graph_path,
        manifest_path=paths.manifest_path,
        synthesis_cache_dir=paths.synthesis_dir,
        preview_dir=paths.preview_dir,
        run_dir=paths.run_dir,
        backup_dir=paths.backup_dir,
        readwise_index_path=paths.knowledge_root / "state" / "readwise_library.json",
    )


def main(argv: list[str] | None = None) -> int:
    """Collect and print wiki operations status."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    repo = (args.repo_root or repo_root()).resolve()
    try:
        paths = load_paths_for_cli(args, repo_root_override=repo)
    except WikiPathsConfigError as exc:
        LOGGER.error("%s", exc)
        return 2
    if args.paths_json:
        print(json.dumps(paths.to_dict(), indent=2, sort_keys=True))
        return 0
    resolved_paths = paths_with_status_cli_overrides(args, paths)
    if args.retention_json:
        inventory = collect_retention_inventory(resolved_paths)
        print(json.dumps(inventory.to_dict(), indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status retention inventory complete")
        return 0
    if args.migration_json:
        config = config_from_args(args)
        ops_status = collect_ops_status(config)
        plan = build_migration_plan(
            resolved_paths,
            require_external_knowledge_root=args.require_external_knowledge_root,
            require_external_vault_root=args.require_external_vault_root,
            ops_status=ops_status,
        )
        print(json.dumps(migration_plan_to_json(plan), indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status migration plan complete")
        return 0
    if args.retirement_json:
        config = config_from_args(args)
        ops_status = collect_ops_status(config)
        plan = build_retirement_plan(resolved_paths, ops_status=ops_status)
        print(json.dumps(retirement_plan_to_json(plan), indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status retirement plan complete")
        return 0
    if args.vault_git_json:
        config = config_from_args(args)
        ops_status = collect_ops_status(config)
        strategy = build_vault_git_strategy(resolved_paths, ops_status=ops_status)
        print(json.dumps(vault_git_strategy_to_json(strategy), indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status vault git strategy complete")
        return 0
    if args.verify_release is not None:
        return _handle_release_verification(args, resolved_paths)
    if args.release_json or args.release_dry_run or args.write_release_manifest:
        return _handle_release_manifest(args, resolved_paths)
    if args.restore_release is not None:
        return _handle_release_restore(args, resolved_paths)
    config = config_from_args(args)
    status = collect_ops_status(config)
    inventory = None
    if args.retention:
        inventory = collect_retention_inventory(resolved_paths)
        status = _merge_retention_into_status(status, inventory)
    migration_plan = None
    if args.migration_plan:
        migration_plan = build_migration_plan(
            resolved_paths,
            require_external_knowledge_root=args.require_external_knowledge_root,
            require_external_vault_root=args.require_external_vault_root,
            ops_status=status,
        )
    retirement_plan = None
    if args.retirement_plan:
        retirement_plan = build_retirement_plan(resolved_paths, ops_status=status)
    vault_git_strategy = None
    if args.vault_git_strategy:
        vault_git_strategy = build_vault_git_strategy(resolved_paths, ops_status=status)
        status = _merge_vault_git_into_status(status, vault_git_strategy)
    if args.json:
        print(json.dumps(status.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_text_report(status))
        if inventory is not None:
            print("")
            print(format_retention_text(inventory))
        if migration_plan is not None:
            print("")
            print(format_migration_plan_text(migration_plan))
        if retirement_plan is not None:
            print("")
            print(format_retirement_plan_text(retirement_plan))
        if vault_git_strategy is not None:
            print("")
            print(format_vault_git_strategy_text(vault_git_strategy))
    LOGGER.info("wiki-ops-status complete")
    return 0


def _handle_release_verification(args: argparse.Namespace, paths: WikiPaths) -> int:
    """Verify one release manifest against the current knowledge store."""
    try:
        report = verify_release(
            paths,
            selector=args.verify_release,
            allow_path_mismatch=args.verify_allow_path_mismatch,
        )
    except ReleaseSelectionError as exc:
        LOGGER.error("%s", exc)
        return 2
    if args.verify_json:
        print(json.dumps(release_verification_to_json(report), indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status release verification complete")
        return 0 if report.status in {"ok", "warning"} else 2
    config = config_from_args(args)
    status = collect_ops_status(config)
    print(format_text_report(status))
    print("")
    print(format_release_verification_text(report))
    LOGGER.info("wiki-ops-status release verification complete")
    return 0 if report.status in {"ok", "warning"} else 2


def _handle_release_manifest(args: argparse.Namespace, paths: WikiPaths) -> int:
    """Preview or write a release manifest."""
    if args.write_release_manifest and not args.yes:
        LOGGER.error("--write-release-manifest requires --yes")
        return 2
    config = config_from_args(args)
    ops_status = collect_ops_status(config)
    manifest = build_release_manifest(
        paths,
        release_id=args.release_id,
        ops_status=ops_status,
        checkpoint_kind=cast(CheckpointKind, str(args.checkpoint_kind)),
        snapshot_id=str(args.snapshot_id) if args.snapshot_id else None,
    )
    if args.write_release_manifest:
        try:
            output_path = write_release_manifest(manifest, overwrite=args.overwrite)
        except FileExistsError as exc:
            LOGGER.error("%s", exc)
            return 2
        print(f"Wrote release manifest: {output_path}")
        LOGGER.info("wiki-ops-status release manifest written")
        return 0
    if args.release_json:
        print(json.dumps(manifest.to_dict(), indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status release manifest preview complete")
        return 0
    print(format_release_dry_run_text(manifest, paths))
    LOGGER.info("wiki-ops-status release manifest dry-run complete")
    return 0


def _handle_release_restore(args: argparse.Namespace, paths: WikiPaths) -> int:
    """Restore selected knowledge/vault areas from an external snapshot."""
    if args.restore_snapshot_root is None:
        LOGGER.error("--restore-release requires --restore-snapshot-root")
        return 2
    if not args.restore_dry_run and not args.yes:
        LOGGER.error("--restore-release requires --yes unless --restore-dry-run is set")
        return 2
    areas = [part.strip() for part in str(args.restore_areas).split(",") if part.strip()]
    if not areas:
        LOGGER.error("--restore-areas must not be empty")
        return 2
    try:
        plan, verify_report = restore_release_from_snapshot(
            paths,
            selector=str(args.restore_release),
            snapshot_root=Path(args.restore_snapshot_root),
            area_selector=areas,
            dry_run=bool(args.restore_dry_run),
            allow_verify_path_mismatch=bool(args.verify_allow_path_mismatch),
        )
    except ReleaseRestoreError as exc:
        LOGGER.error("%s", exc)
        return 2
    if args.restore_json:
        payload = release_restore_plan_to_json(plan, verify_report=verify_report)
        print(json.dumps(payload, indent=2, sort_keys=True))
        LOGGER.info("wiki-ops-status release restore complete")
        return 0 if verify_report is None or verify_report.status in {"ok", "warning"} else 2
    config = config_from_args(args)
    status = collect_ops_status(config)
    print(format_text_report(status))
    print("")
    print(format_release_restore_plan_text(plan))
    if verify_report is not None:
        print("")
        print(format_release_verification_text(verify_report))
    LOGGER.info("wiki-ops-status release restore complete")
    return 0 if verify_report is None or verify_report.status in {"ok", "warning"} else 2


def _merge_retention_into_status(status: OpsStatus, inventory: RetentionInventory) -> OpsStatus:
    """Merge retention warnings and recommendations into an ops status snapshot."""
    return OpsStatus(
        sources=status.sources,
        readwise_index=status.readwise_index,
        source_access=status.source_access,
        reviews=status.reviews,
        render=status.render,
        synthesis=status.synthesis,
        artifacts=status.artifacts,
        recommendations=[*status.recommendations, *build_retention_recommendations(inventory)],
        warnings=[*status.warnings, *inventory.warnings],
    )


def _merge_vault_git_into_status(status: OpsStatus, strategy: VaultGitStrategy) -> OpsStatus:
    """Merge vault Git strategy warnings and recommendations into ops status."""
    readiness = strategy.readiness
    return OpsStatus(
        sources=status.sources,
        readwise_index=status.readwise_index,
        source_access=status.source_access,
        reviews=status.reviews,
        render=status.render,
        synthesis=status.synthesis,
        artifacts=status.artifacts,
        recommendations=[
            *status.recommendations,
            *build_vault_git_recommendations_for_status(strategy),
        ],
        warnings=[
            *status.warnings,
            *readiness.blocked_reasons,
            *readiness.warnings,
        ],
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
