"""FastAPI application for the management web backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.management_web.models import (
    MANAGEMENT_WEB_MODE,
    MANAGEMENT_WEB_WRITE_CAPABILITIES,
    ActiveUpdateWikiWorkflowResponse,
    ConfigResponse,
    ConfirmUpdateWikiRequest,
    EntityEditRequest,
    EntityEditResponse,
    FinishReviewRequest,
    FinishReviewResponse,
    HealthResponse,
    ManagementDecisionFilter,
    ManagementDecisionResponse,
    ManagementReviewRequest,
    OperationDefinitionModel,
    OperationParameterModel,
    OperationRunListResponse,
    OperationRunResponse,
    OperationsListResponse,
    OpsStatusResponse,
    QueueResponse,
    QueueStatusFilter,
    RawSourceResponse,
    ReviewTagsResponse,
    ReviewTypesResponse,
    SourceDetailResponse,
    StartOperationRequest,
    StartOperationResponse,
    StartUpdateWikiRequest,
    StartUpdateWikiResponse,
    UpdateWikiAvailabilityResponse,
    UpdateWikiWorkflowRunListResponse,
    UpdateWikiWorkflowRunModel,
)
from src.management_web.ops import (
    ManagementRunCoordinator,
    OperationConflictError,
    OperationValidationError,
    OpsRunManager,
    collect_management_ops_status,
    format_ops_status_summary,
    list_operation_definitions,
)
from src.management_web.review_data import (
    EntityEditConflictError,
    FinishConflictError,
    build_review_queue,
    build_review_tag_registry,
    build_review_type_registry,
    finish_review,
    get_source_detail,
    read_raw_markdown,
    update_review_entity,
    write_management_decision,
)
from src.management_web.update_wiki_workflow import (
    UPDATE_WIKI_WORKFLOW_ID,
    UpdateWikiWorkflowManager,
    WorkflowConflictError,
    WorkflowValidationError,
    assess_update_wiki_availability,
    validate_synthesis_batch_size,
    validate_synthesis_between_calls_seconds,
)
from src.wiki_paths.config import WikiPaths, load_wiki_paths


def _utc_timestamp() -> str:
    from datetime import UTC, datetime

    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _operation_definition_models() -> list[OperationDefinitionModel]:
    return [
        OperationDefinitionModel(
            id=operation.id,
            label=operation.label,
            description=operation.description,
            writes=operation.writes,
            llm_calls=operation.llm_calls,
            requires_confirmation=operation.requires_confirmation,
            parameters=[
                OperationParameterModel(
                    name=param.name,
                    label=param.label,
                    type=param.type,
                    default=param.default,
                    required=param.required,
                )
                for param in operation.parameters
            ],
        )
        for operation in list_operation_definitions()
    ]


def _operation_run_response(report: dict[str, object]) -> OperationRunResponse:
    return OperationRunResponse.model_validate(report)


def _update_wiki_workflow_run_response(report: dict[str, object]) -> UpdateWikiWorkflowRunModel:
    return UpdateWikiWorkflowRunModel.model_validate(report)


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
    coordinator = ManagementRunCoordinator()
    app = FastAPI(title="LLM Wiki Management Web", version="0.1.0")
    app.state.paths = resolved_paths
    app.state.paths_config = paths_config
    app.state.run_coordinator = coordinator
    app.state.ops_runs = OpsRunManager(
        paths=resolved_paths,
        paths_config=paths_config,
        coordinator=coordinator,
    )
    app.state.update_wiki = UpdateWikiWorkflowManager(
        paths=resolved_paths,
        paths_config=paths_config,
        coordinator=coordinator,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "PATCH", "POST"],
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

    @app.get("/api/review/tags", response_model=ReviewTagsResponse)
    def review_tags(
        group: str | None = Query(default=None, description="Optional editable entity group."),
    ) -> ReviewTagsResponse:
        """Return available tag choices for entity editing."""
        try:
            return build_review_tag_registry(app.state.paths, group=group)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/review/types", response_model=ReviewTypesResponse)
    def review_types(
        group: str = Query(..., description="Editable entity group; only tools is supported."),
    ) -> ReviewTypesResponse:
        """Return available tool-kind choices for entity editing."""
        try:
            return build_review_type_registry(app.state.paths, group=group)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

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

    @app.get("/api/ops/status", response_model=OpsStatusResponse)
    def ops_status() -> OpsStatusResponse:
        """Return current pipeline ops status without writes or LLM calls."""
        current_paths: WikiPaths = app.state.paths
        status = collect_management_ops_status(current_paths)
        return OpsStatusResponse(
            status=status,
            collected_at=_utc_timestamp(),
            summary=format_ops_status_summary(status),
        )

    @app.get("/api/ops/operations", response_model=OperationsListResponse)
    def ops_operations() -> OperationsListResponse:
        """Return allowlisted pipeline operations for the cockpit."""
        return OperationsListResponse(operations=_operation_definition_models())

    @app.post("/api/ops/runs", response_model=StartOperationResponse)
    def ops_start_run(request: StartOperationRequest) -> StartOperationResponse:
        """Start one allowlisted pipeline operation."""
        manager: OpsRunManager = app.state.ops_runs
        try:
            report = manager.start_run(
                request.operation_id,
                parameters=request.parameters,
                confirmed=request.confirmed,
            )
        except OperationValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except OperationConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return StartOperationResponse(
            run_id=str(report["run_id"]),
            operation_id=str(report["operation_id"]),
            status=report["status"],  # type: ignore[arg-type]
        )

    @app.get("/api/ops/runs", response_model=OperationRunListResponse)
    def ops_list_runs(limit: int = Query(default=20, ge=1, le=100)) -> OperationRunListResponse:
        """Return recent management-launched operation runs."""
        manager: OpsRunManager = app.state.ops_runs
        runs = [_operation_run_response(report) for report in manager.list_runs(limit=limit)]
        return OperationRunListResponse(runs=runs)

    @app.get("/api/ops/runs/{run_id}", response_model=OperationRunResponse)
    def ops_get_run(run_id: str) -> OperationRunResponse:
        """Return one management-launched operation run."""
        manager: OpsRunManager = app.state.ops_runs
        try:
            return _operation_run_response(manager.get_run(run_id))
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/ops/workflows/update-wiki/status", response_model=UpdateWikiAvailabilityResponse)
    def update_wiki_status() -> UpdateWikiAvailabilityResponse:
        """Return whether Update Wiki should be offered right now."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        payload = manager.availability()
        availability = assess_update_wiki_availability(payload["status"])
        return UpdateWikiAvailabilityResponse(
            update_available=availability.update_available,
            headline=availability.headline,
            detail_line=availability.detail_line,
            hints=list(availability.hints),
            blocking_errors=list(availability.blocking_errors),
            can_start=availability.can_start,
            collected_at=str(payload["collected_at"]),
        )

    @app.post("/api/ops/workflows/update-wiki/start", response_model=StartUpdateWikiResponse)
    def update_wiki_start(request: StartUpdateWikiRequest) -> StartUpdateWikiResponse:
        """Start the guided Update Wiki workflow."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        try:
            validate_synthesis_batch_size(request.synthesis_batch_size)
            validate_synthesis_between_calls_seconds(request.synthesis_between_calls_seconds)
            report = manager.start(
                synthesis_batch_size=request.synthesis_batch_size,
                synthesis_between_calls_seconds=request.synthesis_between_calls_seconds,
                auto_confirm=request.auto_confirm,
            )
        except WorkflowValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except OperationConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return StartUpdateWikiResponse(
            run_id=str(report["run_id"]),
            workflow_id=UPDATE_WIKI_WORKFLOW_ID,
            status=report["status"],  # type: ignore[arg-type]
        )

    @app.post(
        "/api/ops/workflows/update-wiki/{run_id}/confirm",
        response_model=UpdateWikiWorkflowRunModel,
    )
    def update_wiki_confirm(
        run_id: str,
        request: ConfirmUpdateWikiRequest,
    ) -> UpdateWikiWorkflowRunModel:
        """Confirm one waiting Update Wiki workflow step."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        try:
            report = manager.confirm(run_id, request.confirmation_id)
        except WorkflowValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except WorkflowConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return _update_wiki_workflow_run_response(report)

    @app.post(
        "/api/ops/workflows/update-wiki/{run_id}/skip",
        response_model=UpdateWikiWorkflowRunModel,
    )
    def update_wiki_skip(
        run_id: str,
        request: ConfirmUpdateWikiRequest,
    ) -> UpdateWikiWorkflowRunModel:
        """Skip one waiting Update Wiki workflow step."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        try:
            report = manager.skip(run_id, request.confirmation_id)
        except WorkflowValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except WorkflowConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return _update_wiki_workflow_run_response(report)

    @app.get(
        "/api/ops/workflows/update-wiki/active",
        response_model=ActiveUpdateWikiWorkflowResponse,
    )
    def update_wiki_active_run() -> ActiveUpdateWikiWorkflowResponse:
        """Return the currently active Update Wiki workflow run, if any."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        report = manager.active_run()
        if report is None:
            return ActiveUpdateWikiWorkflowResponse(run=None)
        return ActiveUpdateWikiWorkflowResponse(
            run=_update_wiki_workflow_run_response(report),
        )

    @app.get(
        "/api/ops/workflows/update-wiki/{run_id}",
        response_model=UpdateWikiWorkflowRunModel,
    )
    def update_wiki_get_run(run_id: str) -> UpdateWikiWorkflowRunModel:
        """Return one Update Wiki workflow run."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        try:
            return _update_wiki_workflow_run_response(manager.get_run(run_id))
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/api/ops/workflows/update-wiki/runs",
        response_model=UpdateWikiWorkflowRunListResponse,
    )
    def update_wiki_list_runs(
        limit: int = Query(default=20, ge=1, le=100),
    ) -> UpdateWikiWorkflowRunListResponse:
        """Return recent Update Wiki workflow runs."""
        manager: UpdateWikiWorkflowManager = app.state.update_wiki
        runs = [
            _update_wiki_workflow_run_response(report) for report in manager.list_runs(limit=limit)
        ]
        return UpdateWikiWorkflowRunListResponse(runs=runs)

    return app
