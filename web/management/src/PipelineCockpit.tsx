import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import {
  getOpsOperations,
  getOpsStatus,
  getOperationRun,
  listOperationRuns,
  startOperationRun
} from "./api";
import UpdateWikiPanel from "./UpdateWikiPanel";
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
    title: "Check wiki health",
    description: "Validate the generated wiki and spot stale or unsafe vault state.",
    operationIds: ["wiki_lint"]
  },
  {
    title: "Preview or publish wiki",
    description: "Preview or write generated Obsidian pages from finished reviews.",
    operationIds: ["wiki_render_dry_run", "wiki_render"]
  },
  {
    title: "Inspect synthesis candidates",
    description: "Rank changed synthesis pages before spending API calls.",
    operationIds: ["synthesis_select"]
  },
  {
    title: "Run synthesis batch",
    description: "Dry-run or execute a bounded synthesis batch against the cache.",
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
    return "synthesis_batch_dry_run";
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

function recommendationActionLabel(recommendation: string, operation: OperationDefinition): string {
  const lowered = recommendation.toLowerCase();
  if (operation.id === "synthesis_batch_dry_run") {
    if (lowered.includes("refresh") || lowered.includes("stale")) {
      return "Plan synthesis refresh";
    }
    return "Plan next batch";
  }
  if (operation.id === "wiki_render_dry_run") {
    return "Preview render";
  }
  if (operation.id === "wiki_render") {
    return "Write render...";
  }
  return operationActionLabel(operation);
}

function operationActionLabel(operation: OperationDefinition): string {
  switch (operation.id) {
    case "wiki_lint":
      return "Run health check";
    case "wiki_render_dry_run":
      return "Preview render";
    case "wiki_render":
      return "Write render...";
    case "synthesis_select":
      return "Show candidates";
    case "synthesis_batch_dry_run":
      return "Dry-run batch";
    case "synthesis_batch":
      return "Run batch...";
    default:
      return operation.requires_confirmation ? `Run ${operation.label}...` : operation.label;
  }
}

function operationIntentLabelById(operationId: string, fallback: string): string {
  switch (operationId) {
    case "wiki_lint":
      return "Health check";
    case "wiki_render_dry_run":
      return "Render preview";
    case "wiki_render":
      return "Render write";
    case "synthesis_select":
      return "Candidate ranking";
    case "synthesis_batch_dry_run":
      return "Batch dry-run";
    case "synthesis_batch":
      return "Batch execution";
    default:
      return fallback;
  }
}

function operationIntentLabel(operation: OperationDefinition): string {
  return operationIntentLabelById(operation.id, operation.label);
}

function parameterHelper(parameter: OperationParameter): string | null {
  switch (parameter.name) {
    case "limit":
      return "Maximum number of items for this run.";
    case "between_calls":
      return "Seconds to wait between LLM calls.";
    case "require_source_text":
      return "Stops a real render if source text coverage is unexpectedly low.";
    case "continue_on_error":
      return "Keeps processing after one synthesis item fails.";
    default:
      return null;
  }
}

function operationImpact(operation: OperationDefinition): string {
  if (operation.writes && operation.llm_calls) {
    return "This operation writes files and may call the LLM API.";
  }
  if (operation.writes) {
    return "This operation writes files.";
  }
  if (operation.llm_calls) {
    return "This operation may call the LLM API.";
  }
  return "This operation is read-only.";
}

function expectedOutput(operation: OperationDefinition): string {
  switch (operation.id) {
    case "wiki_render":
      return "Expected output: generated Obsidian wiki pages and an operation run report.";
    case "synthesis_batch":
      return "Expected output: synthesis cache files and an operation run report.";
    case "wiki_lint":
      return "Expected output: a health report in the run details.";
    case "wiki_render_dry_run":
      return "Expected output: a render preview in the run details.";
    case "synthesis_select":
      return "Expected output: ranked synthesis candidates in the run details.";
    case "synthesis_batch_dry_run":
      return "Expected output: a dry-run batch plan in the run details.";
    default:
      return "Expected output: an operation run report.";
  }
}

function runStatusClass(status: OperationRunStatus): string {
  return `pipeline-run-badge ${status}`;
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

function statusChips(statusPayload: OpsStatusResponse | null): Array<{ label: string; value: string; tone: string }> {
  if (!statusPayload) {
    return [];
  }
  const status = statusPayload.status;
  const sources = status.sources as Record<string, unknown> | undefined;
  const reviews = status.reviews as Record<string, unknown> | undefined;
  const render = status.render as Record<string, unknown> | undefined;
  const synthesis = status.synthesis as Record<string, unknown> | undefined;
  const artifacts = status.artifacts as Record<string, unknown> | undefined;
  const renderReady = Boolean(render?.manifest_exists) && Boolean(render?.graph_exists);
  const staleSyntheses = Number(synthesis?.stale ?? 0);
  const errors = Number(synthesis?.errors ?? 0);
  const uncommittedDurable = Number(artifacts?.uncommitted_durable_files ?? 0);
  return [
    { label: "Sources", value: String(sources?.paired ?? "—"), tone: "neutral" },
    { label: "Finished reviews", value: String(reviews?.finished ?? "—"), tone: "neutral" },
    { label: "Render", value: renderReady ? "current" : "incomplete", tone: renderReady ? "ok" : "warn" },
    {
      label: "Synthesis",
      value: errors ? `${errors} errors` : staleSyntheses ? `${staleSyntheses} stale` : "fresh",
      tone: errors ? "error" : staleSyntheses ? "warn" : "ok"
    },
    {
      label: "Durable changes",
      value: String(uncommittedDurable),
      tone: uncommittedDurable ? "warn" : "ok"
    }
  ];
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

function parseStdoutJson(run: OperationRun): Record<string, unknown> | null {
  const trimmed = run.stdout_tail.trim();
  if (!trimmed.startsWith("{")) {
    return null;
  }
  try {
    const parsed = JSON.parse(trimmed) as unknown;
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? (parsed as Record<string, unknown>)
      : null;
  } catch {
    return null;
  }
}

function firstMeaningfulLines(text: string, limit = 4): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, limit);
}

function runSummaryLines(run: OperationRun): string[] {
  const parsed = parseStdoutJson(run);
  if (parsed) {
    if (run.operation_id === "synthesis_select") {
      const total = parsed.total ?? parsed.total_changed ?? "—";
      const shown = parsed.shown ?? "—";
      const items = Array.isArray(parsed.items)
        ? parsed.items
        : Array.isArray(parsed.entries)
          ? parsed.entries
          : [];
      const topItems = items
        .map((item) => {
          if (!item || typeof item !== "object") {
            return null;
          }
          const entry = item as Record<string, unknown>;
          const entity = entry.entity_id ?? entry.title;
          const score = entry.score;
          const bits = [
            entity ? String(entity) : null,
            entry.title && entry.title !== entity ? String(entry.title) : null,
            score === undefined ? null : `score ${String(score)}`,
            entry.source_count === undefined ? null : `${String(entry.source_count)} sources`,
            entry.state ? String(entry.state) : null
          ].filter((bit): bit is string => Boolean(bit));
          return bits.length ? bits.join(" · ") : null;
        })
        .filter((item): item is string => Boolean(item))
        .slice(0, 5);
      return [`${String(total)} total · ${String(shown)} shown`, ...topItems];
    }
    const preferredKeys = [
      "summary",
      "selected",
      "planned",
      "attempted",
      "called",
      "written",
      "failed",
      "dry_run"
    ];
    const lines = preferredKeys
      .filter((key) => key in parsed)
      .map((key) => `${key.replaceAll("_", " ")}: ${String(parsed[key])}`);
    if (lines.length) {
      return lines.slice(0, 5);
    }
  }
  const outputLines = firstMeaningfulLines(run.stdout_tail);
  if (outputLines.length) {
    return outputLines;
  }
  const errorLines = firstMeaningfulLines(run.stderr_tail);
  if (errorLines.length) {
    return errorLines;
  }
  if (run.status === "queued" || run.status === "running") {
    return ["Operation is running. The result will appear here."];
  }
  return ["No readable output was captured."];
}

function runFeedbackTitle(run: OperationRun): string {
  const label = operationIntentLabelById(run.operation_id, run.label);
  if (run.status === "queued" || run.status === "running") {
    return `${label} started`;
  }
  return `${label} ${statusLabel(run.status).toLowerCase()}`;
}

export default function PipelineCockpit(): ReactElement {
  const [statusPayload, setStatusPayload] = useState<OpsStatusResponse | null>(null);
  const [operations, setOperations] = useState<OperationDefinition[]>([]);
  const [runs, setRuns] = useState<OperationRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [parameterValues, setParameterValues] = useState<Record<string, ParameterValues>>({});
  const [pendingConfirmation, setPendingConfirmation] = useState<PendingConfirmation | null>(null);
  const [busyOperationId, setBusyOperationId] = useState<string | null>(null);
  const [expandedResultRunIds, setExpandedResultRunIds] = useState<Set<string>>(new Set());
  const [actionError, setActionError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
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

  const latestRunsByOperationId = useMemo(() => {
    const latest: Record<string, OperationRun> = {};
    for (const run of runs) {
      latest[run.operation_id] ??= run;
    }
    return latest;
  }, [runs]);

  const recommendations = useMemo(() => {
    if (statusError) {
      return [];
    }
    const raw = statusPayload?.status.recommendations;
    return Array.isArray(raw) ? raw.filter((item): item is string => typeof item === "string") : [];
  }, [statusError, statusPayload]);

  const refreshStatus = useCallback(async (): Promise<void> => {
    setStatusLoading(true);
    try {
      const payload = await getOpsStatus();
      setStatusPayload(payload);
      setStatusError(null);
    } catch (err: unknown) {
      const message = String(err);
      setStatusError(message);
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
      const operationsResponse = await getOpsOperations();
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
      await refreshStatus();
    } catch (err: unknown) {
      setActionError(String(err));
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
          setActionError(String(err));
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
      setActionError("Another operation is already running.");
      return;
    }
    const parameters = parameterValues[operation.id] ?? defaultParameters(operation);
    if (operation.requires_confirmation && !confirmed) {
      setPendingConfirmation({ operation, parameters });
      return;
    }
    setBusyOperationId(operation.id);
    setActionError(null);
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
      setActionError(String(err));
    } finally {
      setBusyOperationId(null);
    }
  }

  function toggleExpandedResult(runId: string): void {
    setExpandedResultRunIds((current) => {
      const next = new Set(current);
      if (next.has(runId)) {
        next.delete(runId);
      } else {
        next.add(runId);
      }
      return next;
    });
  }

  return (
    <main className="pipeline-page">
      {actionError ? <div className="error-banner">{actionError}</div> : null}

      <UpdateWikiPanel />

      <details className="panel-card advanced-manual-operations">
        <summary>Advanced manual operations</summary>
      <div className="pipeline-workbench">
        <section className="pipeline-operations" aria-label="Pipeline operations">
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
                      <strong>{operationIntentLabel(operation)}</strong>
                      <span className="operation-safety">{formatSafety(operation)}</span>
                      <span>{operation.description}</span>
                    </div>
                    {operation.parameters.length > 0 ? (
                      <div className="operation-parameters">
                        {operation.parameters.map((parameter) => {
                          const helper = parameterHelper(parameter);
                          return (
                            <label
                              className={
                                parameter.type === "boolean"
                                  ? "operation-parameter boolean"
                                  : "operation-parameter"
                              }
                              key={`${operation.id}-${parameter.name}`}
                            >
                              {parameter.type === "boolean" ? (
                                <>
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
                                  <span>{parameter.label}</span>
                                </>
                              ) : (
                                <>
                                  <span>{parameter.label}</span>
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
                                </>
                              )}
                              {helper ? <small>{helper}</small> : null}
                            </label>
                          );
                        })}
                      </div>
                    ) : null}
                    <div className="operation-card-actions">
                      <button
                        disabled={Boolean(activeRun) || busyOperationId !== null}
                        onClick={() => void launchOperation(operation)}
                        type="button"
                      >
                        {operationActionLabel(operation)}
                      </button>
                    </div>
                    {latestRunsByOperationId[operation.id] ? (
                      <div
                        aria-label={`${operationIntentLabel(operation)} result`}
                        className="operation-result"
                      >
                        <div className="operation-result-header">
                          <strong>{runFeedbackTitle(latestRunsByOperationId[operation.id])}</strong>
                          <span className={runStatusClass(latestRunsByOperationId[operation.id].status)}>
                            {statusLabel(latestRunsByOperationId[operation.id].status)}
                          </span>
                        </div>
                        <ul>
                          {runSummaryLines(latestRunsByOperationId[operation.id]).map((line) => (
                            <li key={line}>{line}</li>
                          ))}
                        </ul>
                        <button
                          className="text-button"
                          onClick={() => toggleExpandedResult(latestRunsByOperationId[operation.id].run_id)}
                          type="button"
                        >
                          {expandedResultRunIds.has(latestRunsByOperationId[operation.id].run_id)
                            ? "Hide technical details"
                            : "Show technical details"}
                        </button>
                        {expandedResultRunIds.has(latestRunsByOperationId[operation.id].run_id) ? (
                          <div className="operation-technical-details">
                            <dl className="operation-technical-facts">
                              <div>
                                <dt>Run</dt>
                                <dd>{latestRunsByOperationId[operation.id].run_id}</dd>
                              </div>
                              <div>
                                <dt>Exit</dt>
                                <dd>{latestRunsByOperationId[operation.id].exit_code ?? "—"}</dd>
                              </div>
                            </dl>
                            {latestRunsByOperationId[operation.id].stdout_tail ? (
                              <details>
                                <summary>Technical stdout</summary>
                                <pre>{latestRunsByOperationId[operation.id].stdout_tail}</pre>
                              </details>
                            ) : null}
                            {latestRunsByOperationId[operation.id].stderr_tail ? (
                              <details>
                                <summary>Technical stderr</summary>
                                <pre>{latestRunsByOperationId[operation.id].stderr_tail}</pre>
                              </details>
                            ) : null}
                          </div>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                ))}
              </article>
            );
          })}
        </section>

        <aside className="pipeline-side" aria-label="Pipeline run state">
          <section className="panel-card pipeline-runs">
            <div className="pipeline-section-header">
              <h2>Recent runs</h2>
              {activeRun ? (
                <span className="pipeline-run-badge running">
                  {operationIntentLabelById(activeRun.operation_id, activeRun.label)} · {statusLabel(activeRun.status)}
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
                      <span>{operationIntentLabelById(run.operation_id, run.label)}</span>
                      <span className={runStatusClass(run.status)}>{statusLabel(run.status)}</span>
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
                  <dd>
                    <span className={runStatusClass(selectedRun.status)}>
                      {statusLabel(selectedRun.status)}
                    </span>
                  </dd>
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
              <div className="pipeline-readable-output">
                <h3>Readable result</h3>
                <ul>
                  {runSummaryLines(selectedRun).map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </div>
              {selectedRun.stdout_tail ? (
                <details>
                  <summary>Technical stdout</summary>
                  <pre>{selectedRun.stdout_tail}</pre>
                </details>
              ) : null}
              {selectedRun.stderr_tail ? (
                <details open={selectedRun.status === "failed"}>
                  <summary>Technical stderr</summary>
                  <pre>{selectedRun.stderr_tail}</pre>
                </details>
              ) : null}
            </section>
          ) : null}
        </aside>
      </div>
      </details>

      {pendingConfirmation ? (
        <div className="pipeline-modal-backdrop" role="presentation">
          <section
            aria-labelledby="pipeline-confirm-title"
            aria-modal="true"
            className="pipeline-modal"
            role="dialog"
          >
            <h2 id="pipeline-confirm-title">Confirm operation</h2>
            <p>{operationIntentLabel(pendingConfirmation.operation)}</p>
            <p className="pipeline-confirm-impact">{operationImpact(pendingConfirmation.operation)}</p>
            <p className="pipeline-meta">{expectedOutput(pendingConfirmation.operation)}</p>
            <ul className="pipeline-confirm-list">
              <li>Writes: {pendingConfirmation.operation.writes ? "yes" : "no"}</li>
              <li>LLM calls: {pendingConfirmation.operation.llm_calls ? "yes" : "no"}</li>
              {Object.entries(pendingConfirmation.parameters).map(([name, value]) => {
                const parameter = pendingConfirmation.operation.parameters.find(
                  (entry) => entry.name === name
                );
                return (
                <li key={name}>
                  {`${parameter?.label ?? name}: ${String(value)}`}
                </li>
                );
              })}
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
