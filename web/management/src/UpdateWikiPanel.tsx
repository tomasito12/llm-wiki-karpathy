import { useCallback, useEffect, useRef, useState } from "react";
import type { ReactElement, RefObject } from "react";

import {
  confirmUpdateWikiStep,
  getActiveUpdateWikiRun,
  getUpdateWikiRun,
  getUpdateWikiStatus,
  skipUpdateWikiStep,
  startUpdateWiki
} from "./api";
import type {
  UpdateWikiAvailabilityResponse,
  UpdateWikiWorkflowRun,
  WorkflowPendingConfirmation,
  WorkflowStep,
  WorkflowStepStatus
} from "./types";
import {
  clearStoredUpdateWikiRunId,
  readStoredUpdateWikiRunId,
  writeStoredUpdateWikiRunId
} from "./updateWikiSession";

const POLL_INTERVAL_MS = 2500;
const TERMINAL_STATUSES = new Set(["succeeded", "failed", "stopped"]);

function stepIcon(status: WorkflowStepStatus): string {
  switch (status) {
    case "succeeded":
      return "✓";
    case "failed":
      return "✕";
    case "skipped":
      return "↷";
    case "running":
      return "…";
    case "waiting":
      return "⏸";
    default:
      return "○";
  }
}

export default function UpdateWikiPanel(): ReactElement {
  const [availability, setAvailability] = useState<UpdateWikiAvailabilityResponse | null>(null);
  const [workflowRun, setWorkflowRun] = useState<UpdateWikiWorkflowRun | null>(null);
  const [batchSize, setBatchSize] = useState(5);
  const [betweenCallsSeconds, setBetweenCallsSeconds] = useState(300);
  const [autoConfirm, setAutoConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pendingStepRef = useRef<HTMLLIElement>(null);

  const refreshAvailability = useCallback(async (): Promise<void> => {
    try {
      const payload = await getUpdateWikiStatus();
      setAvailability(payload);
      setError(null);
    } catch (err: unknown) {
      setError(String(err));
    }
  }, []);

  const applyWorkflowRun = useCallback((run: UpdateWikiWorkflowRun): void => {
    setWorkflowRun(run);
    if (TERMINAL_STATUSES.has(run.status)) {
      clearStoredUpdateWikiRunId();
    } else {
      writeStoredUpdateWikiRunId(run.run_id);
    }
  }, []);

  useEffect(() => {
    void refreshAvailability();
  }, [refreshAvailability]);

  useEffect(() => {
    async function restoreActiveRun(): Promise<void> {
      try {
        const active = await getActiveUpdateWikiRun();
        if (active.run) {
          applyWorkflowRun(active.run);
          return;
        }
        const storedRunId = readStoredUpdateWikiRunId();
        if (!storedRunId) {
          return;
        }
        const run = await getUpdateWikiRun(storedRunId);
        if (TERMINAL_STATUSES.has(run.status)) {
          clearStoredUpdateWikiRunId();
          return;
        }
        applyWorkflowRun(run);
      } catch {
        clearStoredUpdateWikiRunId();
      }
    }
    void restoreActiveRun();
  }, [applyWorkflowRun]);

  useEffect(() => {
    if (!workflowRun || TERMINAL_STATUSES.has(workflowRun.status)) {
      return;
    }
    const timer = window.setInterval(() => {
      void getUpdateWikiRun(workflowRun.run_id)
        .then((run) => {
          applyWorkflowRun(run);
          if (TERMINAL_STATUSES.has(run.status)) {
            void refreshAvailability();
          }
        })
        .catch((err: unknown) => setError(String(err)));
    }, POLL_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [applyWorkflowRun, refreshAvailability, workflowRun]);

  useEffect(() => {
    if (!workflowRun?.pending_confirmation || !pendingStepRef.current) {
      return;
    }
    pendingStepRef.current.scrollIntoView?.({ behavior: "smooth", block: "nearest" });
  }, [workflowRun?.pending_confirmation?.id]);

  async function handleStartUpdateWiki(): Promise<void> {
    if (batchSize < 1 || batchSize > 100) {
      setError("Synthesis batch size must be between 1 and 100.");
      return;
    }
    if (betweenCallsSeconds < 0 || betweenCallsSeconds > 3600) {
      setError("Pause between syntheses must be between 0 and 3600 seconds.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await startUpdateWiki({
        synthesis_batch_size: batchSize,
        synthesis_between_calls_seconds: betweenCallsSeconds,
        auto_confirm: autoConfirm
      });
      const run = await getUpdateWikiRun(response.run_id);
      applyWorkflowRun(run);
    } catch (err: unknown) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm(): Promise<void> {
    if (!workflowRun?.pending_confirmation) {
      return;
    }
    setLoading(true);
    try {
      const run = await confirmUpdateWikiStep(workflowRun.run_id, {
        confirmation_id: workflowRun.pending_confirmation.id
      });
      applyWorkflowRun(run);
    } catch (err: unknown) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleSkip(): Promise<void> {
    if (!workflowRun?.pending_confirmation) {
      return;
    }
    setLoading(true);
    try {
      const run = await skipUpdateWikiStep(workflowRun.run_id, {
        confirmation_id: workflowRun.pending_confirmation.id
      });
      applyWorkflowRun(run);
    } catch (err: unknown) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  const workflowBusy =
    workflowRun !== null &&
    (workflowRun.status === "running" || workflowRun.status === "waiting_for_confirmation");

  return (
    <section className="panel-card update-wiki-panel">
      <div className="pipeline-section-header">
        <div>
          <h2>{availability?.headline ?? "Wiki status"}</h2>
          <p>{availability?.detail_line ?? "Loading workflow status…"}</p>
        </div>
        <button disabled={loading} onClick={() => void refreshAvailability()} type="button">
          Refresh status
        </button>
      </div>

      {availability?.blocking_errors.length ? (
        <ul className="update-wiki-blockers">
          {availability.blocking_errors.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : null}

      {availability?.hints.length ? (
        <div className="update-wiki-hints">
          <h3>Hints</h3>
          <ul>
            {availability.hints.map((hint) => (
              <li key={hint}>{hint}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="update-wiki-controls">
        <label>
          Synthesis batch size
          <input
            aria-label="Synthesis batch size"
            max={100}
            min={1}
            onChange={(event) => setBatchSize(Number.parseInt(event.target.value, 10))}
            type="number"
            value={batchSize}
          />
        </label>
        <label>
          Pause between syntheses (seconds)
          <input
            aria-label="Pause between syntheses (seconds)"
            max={3600}
            min={0}
            onChange={(event) =>
              setBetweenCallsSeconds(Number.parseInt(event.target.value, 10))
            }
            type="number"
            value={betweenCallsSeconds}
          />
        </label>
        <label className="update-wiki-auto-confirm">
          <input
            checked={autoConfirm}
            onChange={(event) => setAutoConfirm(event.target.checked)}
            type="checkbox"
          />
          Auto-approve synthesis and render write
        </label>
        {availability?.update_available ? (
          <button
            disabled={loading || workflowBusy || availability.can_start === false}
            onClick={() => void handleStartUpdateWiki()}
            type="button"
          >
            Update Wiki
          </button>
        ) : (
          <button
            disabled={loading || workflowBusy}
            onClick={() => void handleStartUpdateWiki()}
            type="button"
          >
            Run health check
          </button>
        )}
      </div>

      {error ? <p className="error-banner inline">{error}</p> : null}

      {workflowRun ? (
        <div className="update-wiki-workflow">
          <div className="update-wiki-workflow-header">
            <h3>{workflowRun.headline}</h3>
            <span className={`pipeline-run-badge ${workflowRun.status}`}>{workflowRun.status}</span>
          </div>
          {workflowRun.status === "waiting_for_confirmation" ? (
            <p className="workflow-attention-banner">
              Action required: confirm the highlighted step below to continue.
            </p>
          ) : null}
          <ol className="workflow-timeline">
            {workflowRun.steps.map((step) => (
              <WorkflowTimelineStep
                confirmation={
                  workflowRun.pending_confirmation?.id === step.id
                    ? workflowRun.pending_confirmation
                    : null
                }
                key={step.id}
                loading={loading}
                onConfirm={() => void handleConfirm()}
                onSkip={() => void handleSkip()}
                step={step}
                stepRef={
                  workflowRun.pending_confirmation?.id === step.id ? pendingStepRef : undefined
                }
              />
            ))}
          </ol>
        </div>
      ) : null}
    </section>
  );
}

function WorkflowTimelineStep({
  step,
  confirmation,
  loading,
  onConfirm,
  onSkip,
  stepRef
}: {
  step: WorkflowStep;
  confirmation: WorkflowPendingConfirmation | null;
  loading: boolean;
  onConfirm: () => void;
  onSkip: () => void;
  stepRef?: RefObject<HTMLLIElement | null>;
}): ReactElement {
  const [expanded, setExpanded] = useState(false);
  const hasTechnicalDetails = Boolean(step.technical_stdout || step.technical_stderr);
  const showProgress =
    step.status === "running" &&
    step.progress_total != null &&
    step.progress_total > 0 &&
    step.progress_current != null;
  const progressCurrent = step.progress_current ?? 0;
  const progressTotal = step.progress_total ?? 0;
  const progressPercent = showProgress
    ? Math.min(100, Math.round((progressCurrent / progressTotal) * 100))
    : 0;
  const progressLabel =
    step.progress_message ??
    (showProgress ? `${progressCurrent}/${progressTotal}` : null);
  const waitingForApproval = step.status === "waiting" && confirmation !== null;

  return (
    <li
      className={`workflow-step ${step.status}${waitingForApproval ? " needs-approval" : ""}`}
      ref={stepRef}
    >
      <div className="workflow-step-header">
        <span aria-hidden="true">{stepIcon(step.status)}</span>
        <div>
          <strong>{step.label}</strong>
          {progressLabel && step.status === "running" ? <p>{progressLabel}</p> : null}
          {!progressLabel && !confirmation && step.summary_lines[0] ? (
            <p>{step.summary_lines[0]}</p>
          ) : null}
        </div>
      </div>
      {showProgress ? (
        <div
          aria-label={`${step.label} progress`}
          aria-valuemax={progressTotal}
          aria-valuemin={0}
          aria-valuenow={progressCurrent}
          className="workflow-step-progress"
          role="progressbar"
        >
          <div className="workflow-step-progress-bar" style={{ width: `${progressPercent}%` }} />
        </div>
      ) : null}
      {confirmation ? (
        <div className="workflow-step-confirmation">
          <h4>{confirmation.title}</h4>
          <p>{confirmation.description}</p>
          <ul>
            {confirmation.summary_lines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          <div className="workflow-confirmation-actions">
            <button disabled={loading} onClick={onSkip} type="button">
              {confirmation.skip_label}
            </button>
            <button className="danger-action" disabled={loading} onClick={onConfirm} type="button">
              {confirmation.confirm_label}
            </button>
          </div>
        </div>
      ) : step.summary_lines.length > 1 ? (
        <ul className="workflow-step-summary">
          {step.summary_lines.slice(1).map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      ) : null}
      {hasTechnicalDetails ? (
        <button
          className="workflow-step-toggle"
          onClick={() => setExpanded((current) => !current)}
          type="button"
        >
          {expanded ? "Hide technical details" : "Show technical details"}
        </button>
      ) : null}
      {expanded && step.technical_stdout ? (
        <details open>
          <summary>Stdout</summary>
          <pre>{step.technical_stdout}</pre>
        </details>
      ) : null}
      {expanded && step.technical_stderr ? (
        <details open>
          <summary>Stderr</summary>
          <pre>{step.technical_stderr}</pre>
        </details>
      ) : null}
    </li>
  );
}
