import type {
  ConfigResponse,
  ManagementDecisionResponse,
  ManagementReviewRequest,
  QueueResponse,
  QueueStatusFilter,
  RawSourceResponse,
  SourceDetailResponse
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

export function getReviewQueue(params: {
  status: QueueStatusFilter;
  q: string;
  limit?: number;
  offset?: number;
}): Promise<QueueResponse> {
  const search = new URLSearchParams({
    status: params.status,
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
