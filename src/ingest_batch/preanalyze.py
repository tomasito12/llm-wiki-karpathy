"""Run the existing ingest review pipeline over pending sources unattended."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic, sleep
from typing import Any, Protocol

from src.ingest_queue.queue import IngestItem, list_ingest_items
from src.ingest_review.analyze import run_classification
from src.ingest_review.artifact import review_artifact_path, save_artifact
from src.ingest_review.extract import load_readwise_pair
from src.ingest_review.providers.openai_provider import OpenAIIngestionProvider
from src.ingest_review.schema import PROMPT_VERSION
from src.ingest_review.skipped_sources import load_skipped_source_ids
from src.ingest_review.tags import (
    load_extraction_budgets,
    load_glossary_tags,
    load_howto_tags,
    load_impl_study_tags,
    load_model_tags,
    load_model_types,
    load_tool_tags,
    load_tool_types,
    load_topic_tags,
    load_trend_tags,
)


class ClassificationRunner(Protocol):
    """Callable protocol for running one source through classification."""

    def __call__(
        self,
        provider: Any,
        document: Any,
        *,
        wiki_root: Path,
        tool_types: list[str],
        howto_tags: list[str],
        impl_study_tags: list[str] | None = None,
        glossary_tags: list[str] | None = None,
        topic_tags: list[str] | None = None,
        trend_tags: list[str] | None = None,
        model_types: list[str] | None = None,
        tool_tags: list[str] | None = None,
        model_tags: list[str] | None = None,
        extraction_budgets: dict[str, int] | None = None,
        model: str,
        prompt_version: str | None = None,
        reviews_root: Path | None = None,
    ) -> tuple[dict[str, object], Any]:
        """Run classification and return artifact plus parsed output."""


@dataclass(frozen=True)
class PreanalyzeFailure:
    """One source that failed during pre-analysis."""

    source_id: str
    message: str


@dataclass(frozen=True)
class PreanalyzeProgress:
    """Progress event emitted after each source decision."""

    source_id: str
    status: str
    index: int
    total: int
    message: str = ""


@dataclass(frozen=True)
class PreanalyzeResult:
    """Summary of one unattended pre-analysis run."""

    selected: int = 0
    processed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[PreanalyzeFailure] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    @property
    def all_failed(self) -> bool:
        """Return True when at least one item was selected and none were processed."""
        return self.selected > 0 and not self.processed and bool(self.failed)


def create_ingestion_provider(provider: Any | None = None) -> tuple[Any, bool]:
    """Return an ingestion provider and whether this run owns its lifecycle."""
    if provider is not None:
        return provider, False
    return OpenAIIngestionProvider(), True


def close_ingestion_provider(provider: Any, *, owns_provider: bool) -> None:
    """Close a provider created for one article when this run owns it."""
    if not owns_provider:
        return
    close = getattr(provider, "close", None)
    if callable(close):
        close()


def wait_between_articles(
    seconds: float,
    *,
    source_id: str,
    index: int,
    total: int,
    on_progress: Callable[[PreanalyzeProgress], None] | None = None,
) -> None:
    """Pause between article ingestions so each run uses a fresh provider session."""
    if seconds <= 0:
        return
    _emit_progress(
        on_progress,
        PreanalyzeProgress(
            source_id,
            "waiting",
            index,
            total,
            f"pausing {seconds:.0f}s before next article (OpenAI disconnected)",
        ),
    )
    sleep(seconds)


def select_pending_items(
    raw_dir: Path,
    reviews_root: Path,
    *,
    limit: int | None,
) -> list[IngestItem]:
    """Return the first pending, non-skipped ingest items up to ``limit``."""
    skipped_ids = load_skipped_source_ids(reviews_root)
    pending = [
        item
        for item in list_ingest_items(raw_dir, reviews_root)
        if item.status == "pending" and item.basename not in skipped_ids
    ]
    if limit is None:
        return pending
    return pending[: max(limit, 0)]


def preanalyze_pending(
    *,
    raw_dir: Path,
    reviews_root: Path,
    wiki_root: Path,
    tool_types: list[str],
    howto_tags: list[str],
    impl_study_tags: list[str] | None,
    glossary_tags: list[str] | None,
    topic_tags: list[str] | None,
    trend_tags: list[str] | None,
    model_types: list[str] | None,
    tool_tags: list[str] | None,
    model_tags: list[str] | None,
    extraction_budgets: dict[str, int],
    model: str,
    prompt_version: str = PROMPT_VERSION,
    limit: int | None = 50,
    skip_existing: bool = True,
    between_articles_seconds: float = 0.0,
    provider: Any | None = None,
    runner: ClassificationRunner = run_classification,
    on_progress: Callable[[PreanalyzeProgress], None] | None = None,
) -> PreanalyzeResult:
    """Pre-analyze pending sources using the existing synchronous pipeline."""
    started = monotonic()
    items = select_pending_items(raw_dir, reviews_root, limit=limit)
    processed: list[str] = []
    skipped: list[str] = []
    failed: list[PreanalyzeFailure] = []
    total = len(items)

    for index, item in enumerate(items, start=1):
        artifact_path = review_artifact_path(item.basename, state_reviews=reviews_root)
        if skip_existing and artifact_path.is_file():
            skipped.append(item.basename)
            _emit_progress(
                on_progress,
                PreanalyzeProgress(item.basename, "skipped", index, total, "review.json exists"),
            )
            continue
        active_provider, owns_provider = create_ingestion_provider(provider)
        try:
            document = load_readwise_pair(item.raw_html_path)
            artifact, _parsed = runner(
                active_provider,
                document,
                wiki_root=wiki_root,
                tool_types=tool_types,
                howto_tags=howto_tags,
                impl_study_tags=impl_study_tags,
                glossary_tags=glossary_tags,
                topic_tags=topic_tags,
                trend_tags=trend_tags,
                model_types=model_types,
                tool_tags=tool_tags,
                model_tags=model_tags,
                extraction_budgets=extraction_budgets,
                model=model,
                prompt_version=prompt_version,
                reviews_root=reviews_root,
            )
            save_artifact(artifact_path, artifact)
            processed.append(item.basename)
            _emit_progress(
                on_progress,
                PreanalyzeProgress(item.basename, "processed", index, total, str(artifact_path)),
            )
        except Exception as exc:  # noqa: BLE001
            failure = PreanalyzeFailure(item.basename, str(exc))
            failed.append(failure)
            _emit_progress(
                on_progress,
                PreanalyzeProgress(item.basename, "failed", index, total, failure.message),
            )
        finally:
            close_ingestion_provider(active_provider, owns_provider=owns_provider)
        if index < total:
            wait_between_articles(
                between_articles_seconds,
                source_id=item.basename,
                index=index,
                total=total,
                on_progress=on_progress,
            )

    return PreanalyzeResult(
        selected=total,
        processed=processed,
        skipped=skipped,
        failed=failed,
        elapsed_seconds=round(monotonic() - started, 3),
    )


def preanalyze_pending_with_repo_defaults(
    *,
    repo_root: Path,
    raw_dir: Path,
    reviews_root: Path,
    wiki_root: Path,
    model: str,
    prompt_version: str = PROMPT_VERSION,
    limit: int | None = 50,
    skip_existing: bool = True,
    between_articles_seconds: float = 0.0,
    on_progress: Callable[[PreanalyzeProgress], None] | None = None,
) -> PreanalyzeResult:
    """Pre-analyze pending sources using the same allowlist defaults as the dashboard."""
    return preanalyze_pending(
        raw_dir=raw_dir,
        reviews_root=reviews_root,
        wiki_root=wiki_root,
        tool_types=load_tool_types(repo_root),
        howto_tags=load_howto_tags(repo_root),
        impl_study_tags=load_impl_study_tags(repo_root),
        glossary_tags=load_glossary_tags(repo_root),
        topic_tags=load_topic_tags(repo_root),
        trend_tags=load_trend_tags(repo_root),
        model_types=load_model_types(repo_root),
        tool_tags=load_tool_tags(repo_root),
        model_tags=load_model_tags(repo_root),
        extraction_budgets=load_extraction_budgets(repo_root),
        model=model,
        prompt_version=prompt_version,
        limit=limit,
        skip_existing=skip_existing,
        between_articles_seconds=between_articles_seconds,
        on_progress=on_progress,
    )


def _emit_progress(
    callback: Callable[[PreanalyzeProgress], None] | None,
    progress: PreanalyzeProgress,
) -> None:
    """Call progress callback when configured."""
    if callback is not None:
        callback(progress)
