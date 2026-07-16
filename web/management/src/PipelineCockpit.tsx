import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import {
  getOpsOperations,
  getOpsStatus,
  getOperationRun,
  listOperationRuns,
  startOperationRun
} from "./api";
import type {
  OperationDefinition,
  OperationParameter,
  OperationRun,
  OperationRunStatus,
  OpsStatusResponse
} from "./types";

type ParameterValues = Record<string, boolean | number>;

interface PendingConfirmation {
  operation: OperationDefinition;
  parameters: ParameterValues;
}

interface OperationCardGroup {
  title: string;
  description: string;
  operationIds: string[];
}

const OPERATION_CARD_GROUPS: OperationCardGroup[] = [
  {
    title: "Wiki lint",
    description: "Validate generated wiki markdown and vault hygiene without writes.",
    operationIds: ["wiki_lint"]
  },
  {
    title: "Wiki render",
    description: "Preview or write generated Obsidian wiki pages from finished reviews.",
    operationIds: ["wiki_render_dry_run", "wiki_render"]
  },
  {
    title: "Synthesis select",
    description: "Rank changed synthesis candidates without LLM calls.",
    operationIds: ["synthesis_select"]
  },
  {
    title: "Synthesis batch",
    description: "Plan or run a bounded synthesis batch against the cache.",
    operationIds: ["synthesis_batch_dry_run", "synthesis_batch"]
  }
];

const TERMINAL_STATUSES = new Set<OperationRunStatus>(["succeeded", "failed", "cancelled"]);
const POLL_INTERVAL_MS = 3000;

function recommendationOperationId(recommendation: string): string | null {
  const lowered = recommendation.toLowerCase();
  if (lowered.includes("dry-run") && lowered.includes("synthesis")) {
    return "synthesis_batch_dry_run";
  }
  if (lowered.includes("synthesis") && lowered.includes("batch")) {
    return "synthesis_batch";
  }
  if (lowered.includes("synthesis") && (lowered.includes("refresh") || lowered.includes("stale"))) {
    return "synthesis_batch_dry_run";
  }
  if (lowered.includes("render") && lowered.includes("dry-run")) {
    return "wiki_render_dry_run";
  }
  if (lowered.includes("render")) {
    return "wiki_render";
  }
  if (lowered.includes("lint")) {
    return "wiki_lint";
  }
  if (lowered.includes("synthesis") && lowered.includes("select")) {
    return "synthesis_select";
  }
  return null;
}

function defaultParameters(operation: OperationDefinition): ParameterValues {
  return Object.fromEntries(operation.parameters.map((param) => [param.name, param.default]));
}

function formatSafety(operation: OperationDefinition): string {
  const bits = [
    operation.writes ? "writes files" : "read-only",
    operation.llm_calls ? "LLM calls possible" : "no LLM calls"
  ];
  return bits.join(" · ");
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) {
    return "—";
  }
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}

function statusLabel(status: OperationRunStatus): string {
  switch (status) {
    case "queued":
      return "Queued";
    case "running":
      return "Running";
    case "succeeded":
      return "Succeeded";
    case "failed":
      return "Failed";
    case "cancelled":
      return "Cancelled";
  }
}

export default function PipelineCockpit(): ReactElement {
  const [statusPayload, setStatusPayload] = useState<OpsStatusResponse | null>(null);
  const [operations, setOperations] = useState<OperationDefinition[]>([]);
  const [runs, setRuns] = useState<OperationRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [parameterValues, setParameterValues] = useState<Record<string, ParameterValues>>({});
  const [pendingConfirmation, setPendingConfirmation] = useState<PendingConfirmation | null>(null);
  const [busyOperationId, setBusyOperationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);

  const operationsById = useMemo(
    () => Object.fromEntries(operations.map((operation) => [operation.id, operation])),
    [operations]
  );

  const selectedRun = useMemo(
    () => runs.find((run) => run.run_id === selectedRunId) ?? null,
    [runs, selectedRunId]
  );

  const activeRun = useMemo(
    () => runs.find((run) => run.status === "queued" || run.status === "running") ?? null,
    [runs]
  );

  const recommendations = useMemo(() => {
    const raw = statusPayload?.status.recommendations;
    return Array.isArray(raw) ? raw.filter((item): item is string => typeof item === "string") : [];
  }, [statusPayload]);

  const refreshStatus = useCallback(async (): Promise<void> => {
    setStatusLoading(true);
    try {
      const payload = await getOpsStatus();
      setStatusPayload(payload);
      setError(null);
    } catch (err: unknown) {
      setError(String(err));
    } finally {
      setStatusLoading(false);
    }
  }, []);

  const refreshRuns = useCallback(async (): Promise<void> => {
    const payload = await listOperationRuns();
    setRuns(payload.runs);
    setSelectedRunId((current) => current ?? payload.runs[0]?.run_id ?? null);
  }, []);

  const loadInitialData = useCallback(async (): Promise<void> => {
    try {
      const [statusResponse, operationsResponse] = await Promise.all([
        getOpsStatus(),
        getOpsOperations()
      ]);
      setStatusPayload(statusResponse);
      setOperations(operationsResponse.operations);
      setParameterValues(
        Object.fromEntries(
          operationsResponse.operations.map((operation) => [
            operation.id,
            defaultParameters(operation)
          ])
        )
      );
      await refreshRuns();
      setError(null);
    } catch (err: unknown) {
      setError(String(err));
    }
  }, [refreshRuns]);

  useEffect(() => {
    void loadInitialData();
  }, [loadInitialData]);

  useEffect(() => {
    if (!selectedRun || TERMINAL_STATUSES.has(selectedRun.status)) {
      return;
    }
    const timer = window.setInterval(() => {
      void (async () => {
        try {
          const run = await getOperationRun(selectedRun.run_id);
          setRuns((current) =>
            current.map((entry) => (entry.run_id === run.run_id ? run : entry))
          );
          if (TERMINAL_STATUSES.has(run.status)) {
            await refreshRuns();
            await refreshStatus();
          }
        } catch (err: unknown) {
          setError(String(err));
        }
      })();
    }, POLL_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [refreshRuns, refreshStatus, selectedRun]);

  function updateParameter(
    operationId: string,
    parameter: OperationParameter,
    rawValue: string | boolean
  ): void {
    setParameterValues((current) => {
      const next = { ...(current[operationId] ?? defaultParameters(operationsById[operationId])) };
      if (parameter.type === "boolean") {
        next[parameter.name] = Boolean(rawValue);
      } else if (parameter.type === "integer") {
        next[parameter.name] = Number.parseInt(String(rawValue), 10);
      } else {
        next[parameter.name] = Number.parseFloat(String(rawValue));
      }
      return { ...current, [operationId]: next };
    });
  }

  async function launchOperation(
    operation: OperationDefinition,
    confirmed = false
  ): Promise<void> {
    if (activeRun && activeRun.operation_id !== operation.id) {
      setError("Another operation is already running.");
      return;
    }
    const parameters = parameterValues[operation.id] ?? defaultParameters(operation);
    if (operation.requires_confirmation && !confirmed) {
      setPendingConfirmation({ operation, parameters });
      return;
    }
    setBusyOperationId(operation.id);
    setError(null);
    try {
      const response = await startOperationRun({
        operation_id: operation.id,
        parameters,
        confirmed: operation.requires_confirmation ? true : confirmed
      });
      const run = await getOperationRun(response.run_id);
      setRuns((current) => [run, ...current.filter((entry) => entry.run_id !== run.run_id)]);
      setSelectedRunId(run.run_id);
      setPendingConfirmation(null);
    } catch (err: unknown) {
      setError(String(err));
    } finally {
      setBusyOperationId(null);
    }
  }

  return (
    <main className="pipeline-page">
      {error ? <div className="error-banner">{error}</div> : null}

      <section className="panel-card pipeline-status-band">
        <div className="pipeline-section-header">
          <div>
            <h2>Pipeline status</h2>
            <p>{statusPayload?.summary ?? "Loading status…"}</p>
          </div>
          <button disabled={statusLoading} onClick={() => void refreshStatus()} type="button">
            {statusLoading ? "Refreshing…" : "Refresh status"}
          </button>
        </div>
        {statusPayload ? (
          <p className="pipeline-meta">Updated {statusPayload.collected_at}</p>
        ) : null}
      </section>

      <section className="panel-card">
        <h2>Recommended next actions</h2>
        {recommendations.length === 0 ? (
          <p className="pipeline-muted">No recommendations yet.</p>
        ) : (
          <ol className="pipeline-recommendations">
            {recommendations.map((recommendation) => {
              const operationId = recommendationOperationId(recommendation);
              const operation = operationId ? operationsById[operationId] : undefined;
              return (
                <li key={recommendation}>
                  <span>{recommendation}</span>
                  {operation ? (
                    <button
                      disabled={Boolean(activeRun) || busyOperationId !== null}
                      onClick={() => void launchOperation(operation)}
                      type="button"
                    >
                      {operation.label}
                    </button>
                  ) : null}
                </li>
              );
            })}
          </ol>
        )}
      </section>

      <section className="pipeline-operations">
        {OPERATION_CARD_GROUPS.map((group) => {
          const groupOperations = group.operationIds
            .map((operationId) => operationsById[operationId])
            .filter((operation): operation is OperationDefinition => Boolean(operation));
          if (groupOperations.length === 0) {
            return null;
          }
          return (
            <article className="panel-card operation-card" key={group.title}>
              <h3>{group.title}</h3>
              <p>{group.description}</p>
              {groupOperations.map((operation) => (
                <div className="operation-card-body" key={operation.id}>
                  <div className="operation-card-meta">
                    <strong>{operation.label}</strong>
                    <span>{formatSafety(operation)}</span>
                    <span>{operation.description}</span>
                  </div>
                  {operation.parameters.length > 0 ? (
                    <div className="operation-parameters">
                      {operation.parameters.map((parameter) => (
                        <label key={`${operation.id}-${parameter.name}`}>
                          {parameter.label}
                          {parameter.type === "boolean" ? (
                            <input
                              checked={Boolean(
                                (parameterValues[operation.id] ?? defaultParameters(operation))[
                                  parameter.name
                                ]
                              )}
                              onChange={(event) =>
                                updateParameter(operation.id, parameter, event.target.checked)
                              }
                              type="checkbox"
                            />
                          ) : (
                            <input
                              onChange={(event) =>
                                updateParameter(operation.id, parameter, event.target.value)
                              }
                              type="number"
                              value={String(
                                (parameterValues[operation.id] ?? defaultParameters(operation))[
                                  parameter.name
                                ]
                              )}
                            />
                          )}
                        </label>
                      ))}
                    </div>
                  ) : null}
                  <div className="operation-card-actions">
                    <button
                      disabled={Boolean(activeRun) || busyOperationId !== null}
                      onClick={() => void launchOperation(operation)}
                      type="button"
                    >
                      {operation.requires_confirmation ? `Run ${operation.label}…` : operation.label}
                    </button>
                  </div>
                </div>
              ))}
            </article>
          );
        })}
      </section>

      <section className="panel-card pipeline-runs">
        <div className="pipeline-section-header">
          <h2>Recent runs</h2>
          {activeRun ? (
            <span className="pipeline-run-badge running">
              {activeRun.label} · {statusLabel(activeRun.status)}
            </span>
          ) : null}
        </div>
        {runs.length === 0 ? (
          <p className="pipeline-muted">No runs yet.</p>
        ) : (
          <ul className="pipeline-run-list">
            {runs.map((run) => (
              <li key={run.run_id}>
                <button
                  className={run.run_id === selectedRunId ? "active" : undefined}
                  onClick={() => setSelectedRunId(run.run_id)}
                  type="button"
                >
                  <span>{run.label}</span>
                  <span>{statusLabel(run.status)}</span>
                  <span>{run.started_at}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {selectedRun ? (
        <section className="panel-card pipeline-run-details">
          <h2>Run details</h2>
          <dl className="pipeline-run-facts">
            <div>
              <dt>Status</dt>
              <dd>{statusLabel(selectedRun.status)}</dd>
            </div>
            <div>
              <dt>Started</dt>
              <dd>{selectedRun.started_at}</dd>
            </div>
            <div>
              <dt>Duration</dt>
              <dd>{formatDuration(selectedRun.duration_seconds)}</dd>
            </div>
            <div>
              <dt>Exit code</dt>
              <dd>{selectedRun.exit_code ?? "—"}</dd>
            </div>
            <div>
              <dt>Writes</dt>
              <dd>{selectedRun.writes ? "yes" : "no"}</dd>
            </div>
            <div>
              <dt>LLM calls</dt>
              <dd>{selectedRun.llm_calls ? "possible" : "no"}</dd>
            </div>
          </dl>
          {!TERMINAL_STATUSES.has(selectedRun.status) ? (
            <p className="pipeline-muted">
              Running. Close terminal/server to interrupt if necessary.
            </p>
          ) : null}
          {selectedRun.report_path ? (
            <p className="pipeline-meta">Report: {selectedRun.report_path}</p>
          ) : null}
          {selectedRun.stdout_tail ? (
            <details open={selectedRun.status === "succeeded"}>
              <summary>Stdout tail</summary>
              <pre>{selectedRun.stdout_tail}</pre>
            </details>
          ) : null}
          {selectedRun.stderr_tail ? (
            <details open={selectedRun.status === "failed"}>
              <summary>Stderr tail</summary>
              <pre>{selectedRun.stderr_tail}</pre>
            </details>
          ) : null}
        </section>
      ) : null}

      {pendingConfirmation ? (
        <div className="pipeline-modal-backdrop" role="presentation">
          <section aria-modal="true" className="pipeline-modal" role="dialog">
            <h2>Confirm operation</h2>
            <p>{pendingConfirmation.operation.label}</p>
            <ul className="pipeline-confirm-list">
              <li>Writes: {pendingConfirmation.operation.writes ? "yes" : "no"}</li>
              <li>LLM calls: {pendingConfirmation.operation.llm_calls ? "yes" : "no"}</li>
              {Object.entries(pendingConfirmation.parameters).map(([name, value]) => (
                <li key={name}>
                  {name}: {String(value)}
                </li>
              ))}
            </ul>
            <div className="pipeline-modal-actions">
              <button onClick={() => setPendingConfirmation(null)} type="button">
                Cancel
              </button>
              <button
                className="danger-action"
                onClick={() => void launchOperation(pendingConfirmation.operation, true)}
                type="button"
              >
                Confirm and run
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </main>
  );
}
