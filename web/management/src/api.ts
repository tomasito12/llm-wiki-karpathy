import type {
  ConfigResponse,
  EntityEditRequest,
  EntityEditResponse,
  FinishReviewRequest,
  FinishReviewResponse,
  ManagementDecisionResponse,
  ManagementDecisionFilter,
  ManagementReviewRequest,
  OperationRun,
  OperationRunListResponse,
  OperationsListResponse,
  OpsStatusResponse,
  QueueResponse,
  QueueStatusFilter,
  RawSourceResponse,
  ReviewTagsResponse,
  SourceDetailResponse,
  StartOperationRequest,
  StartOperationResponse,
  StartUpdateWikiRequest,
  StartUpdateWikiResponse,
  ActiveUpdateWikiWorkflowResponse,
  ConfirmUpdateWikiRequest,
  UpdateWikiAvailabilityResponse,
  UpdateWikiWorkflowRun,
  UpdateWikiWorkflowRunListResponse
} from "./types";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export function getConfig(): Promise<ConfigResponse> {
  return fetchJson<ConfigResponse>("/api/config");
}

export function getReviewTags(): Promise<ReviewTagsResponse> {
  return fetchJson<ReviewTagsResponse>("/api/review/tags");
}

export function getReviewQueue(params: {
  status: QueueStatusFilter;
  decision: ManagementDecisionFilter;
  q: string;
  limit?: number;
  offset?: number;
}): Promise<QueueResponse> {
  const search = new URLSearchParams({
    status: params.status,
    decision: params.decision,
    limit: String(params.limit ?? 50),
    offset: String(params.offset ?? 0)
  });
  if (params.q.trim()) {
    search.set("q", params.q.trim());
  }
  return fetchJson<QueueResponse>(`/api/review/queue?${search.toString()}`);
}

export function getSourceDetail(sourceId: string): Promise<SourceDetailResponse> {
  return fetchJson<SourceDetailResponse>(`/api/review/source/${encodeURIComponent(sourceId)}`);
}

export function getRawSource(sourceId: string): Promise<RawSourceResponse> {
  return fetchJson<RawSourceResponse>(`/api/review/source/${encodeURIComponent(sourceId)}/raw`);
}

export function writeManagementDecision(
  sourceId: string,
  decision: ManagementReviewRequest
): Promise<ManagementDecisionResponse> {
  return fetchJson<ManagementDecisionResponse>(
    `/api/review/source/${encodeURIComponent(sourceId)}/decision`,
    {
      body: JSON.stringify(decision),
      headers: { "Content-Type": "application/json" },
      method: "PATCH"
    }
  );
}

export function updateReviewEntity(
  sourceId: string,
  edit: EntityEditRequest
): Promise<EntityEditResponse> {
  return fetchJson<EntityEditResponse>(`/api/review/source/${encodeURIComponent(sourceId)}/entity`, {
    body: JSON.stringify(edit),
    headers: { "Content-Type": "application/json" },
    method: "PATCH"
  });
}

export function finishReview(
  sourceId: string,
  request: FinishReviewRequest
): Promise<FinishReviewResponse> {
  return fetchJson<FinishReviewResponse>(`/api/review/source/${encodeURIComponent(sourceId)}/finish`, {
    body: JSON.stringify(request),
    headers: { "Content-Type": "application/json" },
    method: "PATCH"
  });
}

export function getOpsStatus(): Promise<OpsStatusResponse> {
  return fetchJson<OpsStatusResponse>("/api/ops/status");
}

export function getOpsOperations(): Promise<OperationsListResponse> {
  return fetchJson<OperationsListResponse>("/api/ops/operations");
}

export function startOperationRun(request: StartOperationRequest): Promise<StartOperationResponse> {
  return fetchJson<StartOperationResponse>("/api/ops/runs", {
    body: JSON.stringify(request),
    headers: { "Content-Type": "application/json" },
    method: "POST"
  });
}

export function getOperationRun(runId: string): Promise<OperationRun> {
  return fetchJson<OperationRun>(`/api/ops/runs/${encodeURIComponent(runId)}`);
}

export function listOperationRuns(limit = 20): Promise<OperationRunListResponse> {
  return fetchJson<OperationRunListResponse>(`/api/ops/runs?limit=${limit}`);
}

export function getUpdateWikiStatus(): Promise<UpdateWikiAvailabilityResponse> {
  return fetchJson<UpdateWikiAvailabilityResponse>("/api/ops/workflows/update-wiki/status");
}

export function startUpdateWiki(
  request: StartUpdateWikiRequest
): Promise<StartUpdateWikiResponse> {
  return fetchJson<StartUpdateWikiResponse>("/api/ops/workflows/update-wiki/start", {
    body: JSON.stringify(request),
    headers: { "Content-Type": "application/json" },
    method: "POST"
  });
}

export function getActiveUpdateWikiRun(): Promise<ActiveUpdateWikiWorkflowResponse> {
  return fetchJson<ActiveUpdateWikiWorkflowResponse>(
    "/api/ops/workflows/update-wiki/active"
  );
}

export function getUpdateWikiRun(runId: string): Promise<UpdateWikiWorkflowRun> {
  return fetchJson<UpdateWikiWorkflowRun>(
    `/api/ops/workflows/update-wiki/${encodeURIComponent(runId)}`
  );
}

export function confirmUpdateWikiStep(
  runId: string,
  request: ConfirmUpdateWikiRequest
): Promise<UpdateWikiWorkflowRun> {
  return fetchJson<UpdateWikiWorkflowRun>(
    `/api/ops/workflows/update-wiki/${encodeURIComponent(runId)}/confirm`,
    {
      body: JSON.stringify(request),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    }
  );
}

export function skipUpdateWikiStep(
  runId: string,
  request: ConfirmUpdateWikiRequest
): Promise<UpdateWikiWorkflowRun> {
  return fetchJson<UpdateWikiWorkflowRun>(
    `/api/ops/workflows/update-wiki/${encodeURIComponent(runId)}/skip`,
    {
      body: JSON.stringify(request),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    }
  );
}

export function listUpdateWikiRuns(limit = 10): Promise<UpdateWikiWorkflowRunListResponse> {
  return fetchJson<UpdateWikiWorkflowRunListResponse>(
    `/api/ops/workflows/update-wiki/runs?limit=${limit}`
  );
}
