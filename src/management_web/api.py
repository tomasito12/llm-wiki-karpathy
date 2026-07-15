"""FastAPI application for the management web backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.management_web.models import (
    MANAGEMENT_WEB_MODE,
    MANAGEMENT_WEB_WRITE_CAPABILITIES,
    ConfigResponse,
    EntityEditRequest,
    EntityEditResponse,
    FinishReviewRequest,
    FinishReviewResponse,
    HealthResponse,
    ManagementDecisionFilter,
    ManagementDecisionResponse,
    ManagementReviewRequest,
    QueueResponse,
    QueueStatusFilter,
    RawSourceResponse,
    SourceDetailResponse,
)
from src.management_web.review_data import (
    EntityEditConflictError,
    FinishConflictError,
    build_review_queue,
    finish_review,
    get_source_detail,
    read_raw_markdown,
    update_review_entity,
    write_management_decision,
)
from src.wiki_paths.config import WikiPaths, load_wiki_paths


def create_app(
    *,
    paths: WikiPaths | None = None,
    paths_config: Path | None = None,
) -> FastAPI:
    """Create the management web FastAPI application.

    Args:
        paths: Optional pre-resolved paths, mainly for tests.
        paths_config: Optional path config file to pass to `load_wiki_paths`.

    Returns:
        Configured FastAPI application.
    """
    resolved_paths = paths or load_wiki_paths(config_path=paths_config)
    app = FastAPI(title="LLM Wiki Management Web", version="0.1.0")
    app.state.paths = resolved_paths
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "PATCH"],
        allow_headers=["*"],
    )

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Return basic service health and enabled write capabilities."""
        return HealthResponse(
            ok=True,
            service="management-web",
            mode=MANAGEMENT_WEB_MODE,
            capabilities=list(MANAGEMENT_WEB_WRITE_CAPABILITIES),
        )

    @app.get("/api/config", response_model=ConfigResponse)
    def config() -> ConfigResponse:
        """Return selected resolved paths safe for the private operator UI."""
        current_paths: WikiPaths = app.state.paths
        path_payload = current_paths.to_dict()
        return ConfigResponse(
            mode=MANAGEMENT_WEB_MODE,
            capabilities=list(MANAGEMENT_WEB_WRITE_CAPABILITIES),
            paths={
                "repo_root": path_payload["repo_root"],
                "knowledge_root": path_payload["knowledge_root"],
                "vault_root": path_payload["vault_root"],
                "raw_dir": path_payload["raw_dir"],
                "reviews_dir": path_payload["reviews_dir"],
                "wiki_dir": path_payload["wiki_dir"],
            },
        )

    @app.get("/api/review/queue", response_model=QueueResponse)
    def review_queue(
        status: QueueStatusFilter = "all",
        decision: ManagementDecisionFilter = "not_reviewed",
        limit: int = Query(default=50, ge=0),
        offset: int = Query(default=0, ge=0),
        q: str | None = None,
    ) -> QueueResponse:
        """Return paginated review queue rows and status counts."""
        return build_review_queue(
            app.state.paths,
            status=status,
            decision=decision,
            limit=limit,
            offset=offset,
            query=q,
        )

    @app.get("/api/review/source/{source_id}", response_model=SourceDetailResponse)
    def review_source(source_id: str) -> SourceDetailResponse:
        """Return normalized review detail for one source."""
        try:
            return get_source_detail(app.state.paths, source_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/review/source/{source_id}/raw", response_model=RawSourceResponse)
    def review_source_raw(source_id: str) -> RawSourceResponse:
        """Return local raw Markdown for one source when available."""
        try:
            return read_raw_markdown(app.state.paths, source_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.patch(
        "/api/review/source/{source_id}/decision",
        response_model=ManagementDecisionResponse,
    )
    def review_source_decision(
        source_id: str,
        decision: ManagementReviewRequest,
    ) -> ManagementDecisionResponse:
        """Write an article-level management review decision."""
        try:
            return write_management_decision(app.state.paths, source_id, decision)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=500, detail="Failed to write decision") from exc

    @app.patch(
        "/api/review/source/{source_id}/entity",
        response_model=EntityEditResponse,
    )
    def review_source_entity(
        source_id: str,
        edit: EntityEditRequest,
    ) -> EntityEditResponse:
        """Apply a targeted edit to one normalized entity card."""
        try:
            return update_review_entity(app.state.paths, source_id, edit)
        except EntityEditConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=500, detail="Failed to edit entity") from exc

    @app.patch(
        "/api/review/source/{source_id}/finish",
        response_model=FinishReviewResponse,
    )
    def review_source_finish(
        source_id: str,
        request: FinishReviewRequest,
    ) -> FinishReviewResponse:
        """Finish the selected review artifact and approve it."""
        try:
            return finish_review(app.state.paths, source_id, request)
        except FinishConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except OSError as exc:
            raise HTTPException(status_code=500, detail="Failed to finish review") from exc

    return app
