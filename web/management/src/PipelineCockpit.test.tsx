import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import PipelineCockpit from "./PipelineCockpit";
import * as api from "./api";
import type { OperationsListResponse } from "./types";

vi.mock("./api");

const operationsPayload: OperationsListResponse = {
  operations: [
    {
      id: "readwise_sync",
      label: "Readwise sync",
      description: "Download new processed Readwise documents and remove near-duplicates.",
      writes: true,
      llm_calls: false,
      requires_confirmation: true,
      parameters: []
    },
    {
      id: "ingest_preanalyze",
      label: "Ingest pre-analysis",
      description: "Pre-analyze a bounded batch of pending documents with OpenAI.",
      writes: true,
      llm_calls: true,
      requires_confirmation: true,
      parameters: [
        {
          name: "limit",
          label: "Documents",
          type: "integer",
          default: 10,
          minimum: 1,
          maximum: 100
        },
        {
          name: "between_articles",
          label: "Pause between documents (seconds)",
          type: "float",
          default: 300,
          minimum: 0,
          maximum: 3600
        }
      ]
    },
    {
      id: "wiki_lint",
      label: "Wiki lint",
      description: "Validate generated wiki markdown and vault hygiene without writes.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: []
    },
    {
      id: "wiki_render",
      label: "Wiki render",
      description: "Write generated Obsidian wiki pages from finished reviews.",
      writes: true,
      llm_calls: false,
      requires_confirmation: true,
      parameters: [
        {
          name: "require_source_text",
          label: "Require source text",
          type: "boolean",
          default: true
        }
      ]
    },
    {
      id: "synthesis_select",
      label: "Synthesis select",
      description: "Rank changed synthesis candidates without LLM calls.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: [{ name: "limit", label: "Limit", type: "integer", default: 20 }]
    },
    {
      id: "synthesis_batch_dry_run",
      label: "Synthesis batch dry-run",
      description: "Plan a bounded synthesis batch without API calls or cache writes.",
      writes: false,
      llm_calls: false,
      requires_confirmation: false,
      parameters: [{ name: "limit", label: "Limit", type: "integer", default: 10 }]
    },
    {
      id: "synthesis_batch",
      label: "Synthesis batch",
      description: "Run a bounded synthesis batch with OpenAI calls and cache writes.",
      writes: true,
      llm_calls: true,
      requires_confirmation: true,
      parameters: [
        { name: "limit", label: "Limit", type: "integer", default: 5 },
        {
          name: "between_calls",
          label: "Pause between calls (seconds)",
          type: "float",
          default: 300
        },
        { name: "continue_on_error", label: "Continue on error", type: "boolean", default: false }
      ]
    }
  ]
};

const statusPayload = {
  status: {
    recommendations: [
      "Refresh stale synthesis entries before final render.",
      "Review uncommitted docs and code files before continuing."
    ]
  },
  collected_at: "2026-07-16T10:00:00Z",
  summary: "12 sources · 8 reviewed · render current · 3 stale syntheses"
};

const queuedRun = {
  run_id: "20260716T100000Z-wiki-lint",
  operation_id: "wiki_lint",
  label: "Wiki lint",
  status: "queued" as const,
  parameters: {},
  command: ["python", "-m", "src.wiki_lint"],
  cwd: "/tmp/repo",
  writes: false,
  llm_calls: false,
  started_at: "2026-07-16T10:00:00Z",
  finished_at: null,
  duration_seconds: null,
  exit_code: null,
  stdout_tail: "",
  stderr_tail: "",
  report_path: "/tmp/knowledge/tmp/management_runs/20260716T100000Z-wiki-lint.json"
};

const selectRun = {
  ...queuedRun,
  run_id: "20260716T100030Z-synthesis-select",
  operation_id: "synthesis_select",
  label: "Synthesis select",
  status: "succeeded" as const,
  parameters: { limit: 20 },
  finished_at: "2026-07-16T10:00:31Z",
  duration_seconds: 1,
  exit_code: 0,
  stdout_tail: JSON.stringify({
    total_changed: 42,
    shown: 20,
    entries: [
      {
        entity_id: "topic:service-automation",
        score: 120,
        source_count: 7,
        state: "stale",
        title: "Service Automation"
      },
      { entity_id: "tool:cognigy", score: 118, source_count: 4, state: "new", title: "Cognigy" }
    ]
  }),
  stderr_tail: ""
};

const failedRun = {
  ...queuedRun,
  run_id: "20260716T100100Z-wiki-lint",
  status: "failed" as const,
  finished_at: "2026-07-16T10:01:00Z",
  duration_seconds: 1,
  exit_code: 2,
  stderr_tail: "lint failed"
};

async function openAdvancedOperations(): Promise<void> {
  await screen.findByRole("heading", { name: "Source intake" });
  await userEvent.click(screen.getByRole("button", { name: "Advanced" }));
  await userEvent.click(screen.getByText("Advanced manual operations"));
}

describe("PipelineCockpit", () => {
  beforeEach(() => {
    vi.mocked(api.getOpsStatus).mockResolvedValue(statusPayload);
    vi.mocked(api.getOpsOperations).mockResolvedValue(operationsPayload);
    vi.mocked(api.listOperationRuns).mockResolvedValue({ runs: [] });
    vi.mocked(api.getUpdateWikiStatus).mockResolvedValue({
      update_available: true,
      headline: "Wiki update available",
      detail_line: "42 stale syntheses · render needs refresh · no blocking errors",
      hints: ["42 stale syntheses are ready for the next update."],
      blocking_errors: [],
      can_start: true,
      collected_at: "2026-07-16T10:00:00Z"
    });
    vi.mocked(api.getActiveUpdateWikiRun).mockResolvedValue({ run: null });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it("opens Intake and Analysis by default and keeps the other stages focused", async () => {
    render(<PipelineCockpit />);

    expect(await screen.findByRole("heading", { name: "Source intake" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Intake & Analysis" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(screen.getByRole("button", { name: "Build Wiki" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Advanced" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Update Wiki" })).not.toBeInTheDocument();
    expect(screen.queryByText("Advanced manual operations")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Build Wiki" }));

    expect(await screen.findByRole("button", { name: "Update Wiki" })).toBeInTheDocument();
    expect(screen.getByText("Wiki update available")).toBeInTheDocument();
    expect(screen.getByText("Hints")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Recommended next actions" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Plan synthesis refresh" })).not.toBeInTheDocument();
  });

  it("starts Readwise sync only after confirming automatic duplicate cleanup", async () => {
    vi.mocked(api.startOperationRun).mockResolvedValue({
      run_id: "20260806T120000Z-readwise-sync",
      operation_id: "readwise_sync",
      status: "queued"
    });
    vi.mocked(api.getOperationRun).mockResolvedValue({
      ...queuedRun,
      run_id: "20260806T120000Z-readwise-sync",
      operation_id: "readwise_sync",
      label: "Readwise sync"
    });

    render(<PipelineCockpit />);
    await userEvent.click(await screen.findByRole("button", { name: "Sync new documents…" }));

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText(/shorter near-duplicates may be removed/i)).toBeInTheDocument();
    expect(api.startOperationRun).not.toHaveBeenCalled();

    await userEvent.click(within(dialog).getByRole("button", { name: "Confirm and run" }));
    await waitFor(() =>
      expect(api.startOperationRun).toHaveBeenCalledWith({
        operation_id: "readwise_sync",
        parameters: {},
        confirmed: true
      })
    );
  });

  it("starts pre-analysis with editable batch size and pause defaults", async () => {
    vi.mocked(api.startOperationRun).mockResolvedValue({
      run_id: "20260806T120100Z-ingest-preanalyze",
      operation_id: "ingest_preanalyze",
      status: "queued"
    });
    vi.mocked(api.getOperationRun).mockResolvedValue({
      ...queuedRun,
      run_id: "20260806T120100Z-ingest-preanalyze",
      operation_id: "ingest_preanalyze",
      label: "Ingest pre-analysis"
    });

    render(<PipelineCockpit />);
    const documents = await screen.findByLabelText("Documents");
    const pause = screen.getByLabelText("Pause between documents (seconds)");
    expect(documents).toHaveValue(10);
    expect(documents).toHaveAttribute("min", "1");
    expect(documents).toHaveAttribute("max", "100");
    expect(pause).toHaveValue(300);

    await userEvent.clear(documents);
    await userEvent.type(documents, "6");
    await userEvent.clear(pause);
    await userEvent.type(pause, "450");
    await userEvent.click(screen.getByRole("button", { name: "Start pre-analysis…" }));

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText(/up to 6 documents/i)).toBeInTheDocument();
    expect(within(dialog).getByText(/450 seconds/i)).toBeInTheDocument();
    await userEvent.click(within(dialog).getByRole("button", { name: "Confirm and run" }));

    await waitFor(() =>
      expect(api.startOperationRun).toHaveBeenCalledWith({
        operation_id: "ingest_preanalyze",
        parameters: { limit: 6, between_articles: 450 },
        confirmed: true
      })
    );
  });

  it("summarizes Readwise sync and duplicate cleanup results", async () => {
    vi.mocked(api.listOperationRuns).mockResolvedValue({
      runs: [
        {
          ...queuedRun,
          run_id: "20260806T130000Z-readwise-sync",
          operation_id: "readwise_sync",
          label: "Readwise sync",
          status: "succeeded",
          finished_at: "2026-08-06T13:00:04Z",
          duration_seconds: 4,
          exit_code: 0,
          stdout_tail:
            "sync: examined=12 exported=3 skipped=9\n" +
            "dedupe: scanned=509 pairs=2 deleted=1\n  Deleted: shorter-copy"
        }
      ]
    });

    render(<PipelineCockpit />);

    const result = await screen.findByLabelText("Readwise sync result");
    expect(within(result).getByText("12 examined · 3 downloaded · 9 already local")).toBeInTheDocument();
    expect(within(result).getByText("2 duplicate pairs · 1 removed")).toBeInTheDocument();
    expect(within(result).queryByText(/Deleted: shorter-copy/)).not.toBeInTheDocument();
  });

  it("summarizes pre-analysis progress without showing raw progress lines", async () => {
    vi.mocked(api.listOperationRuns).mockResolvedValue({
      runs: [
        {
          ...queuedRun,
          run_id: "20260806T130100Z-ingest-preanalyze",
          operation_id: "ingest_preanalyze",
          label: "Ingest pre-analysis",
          status: "succeeded",
          finished_at: "2026-08-06T13:00:43Z",
          duration_seconds: 42.5,
          exit_code: 0,
          stdout_tail:
            "[1/10] processing: source-a\n" +
            "Pre-analysis complete: selected 10, processed 8, skipped 1, failed 1, elapsed 42.5s."
        }
      ]
    });

    render(<PipelineCockpit />);

    const result = await screen.findByLabelText("Pre-analysis result");
    expect(within(result).getByText("10 selected · 8 processed · 1 skipped · 1 failed")).toBeInTheDocument();
    expect(within(result).getByText("Elapsed 42.5s")).toBeInTheDocument();
    expect(within(result).queryByText(/processing: source-a/)).not.toBeInTheDocument();
  });

  it("renders operation cards with safety metadata inside advanced manual operations", async () => {
    render(<PipelineCockpit />);
    await screen.findByRole("heading", { name: "Source intake" });
    await userEvent.click(screen.getByRole("button", { name: "Advanced" }));
    await userEvent.click(screen.getByText("Advanced manual operations"));

    expect((await screen.findAllByText("read-only · no LLM calls")).length).toBeGreaterThan(0);
    expect(screen.getByText("writes files · no LLM calls")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Write render..." })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run batch..." })).toBeInTheDocument();
  });

  it("starts a read-only operation without confirmation", async () => {
    vi.mocked(api.startOperationRun).mockResolvedValue({
      run_id: queuedRun.run_id,
      operation_id: "wiki_lint",
      status: "queued"
    });
    vi.mocked(api.getOperationRun).mockResolvedValue(queuedRun);

    render(<PipelineCockpit />);
    await openAdvancedOperations();

    const lintButtons = screen.getAllByRole("button", { name: "Run health check" });
    await userEvent.click(lintButtons[lintButtons.length - 1]);

    await waitFor(() => {
      expect(api.startOperationRun).toHaveBeenCalledWith({
        operation_id: "wiki_lint",
        parameters: {},
        confirmed: false
      });
    });
    expect(await screen.findByText("Health check · Queued")).toBeInTheDocument();
    expect(await screen.findByText("Health check started")).toBeInTheDocument();
  });

  it("opens confirmation for write and LLM operations", async () => {
    render(<PipelineCockpit />);
    await openAdvancedOperations();

    await userEvent.click(screen.getByRole("button", { name: "Write render..." }));

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("Confirm operation")).toBeInTheDocument();
    expect(within(dialog).getByText("Writes: yes")).toBeInTheDocument();
    expect(within(dialog).getByText("LLM calls: no")).toBeInTheDocument();
    expect(api.startOperationRun).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "Run batch..." }));
    expect(await screen.findByText("LLM calls: yes")).toBeInTheDocument();
  });

  it("shows running state for active runs", async () => {
    vi.mocked(api.listOperationRuns).mockResolvedValue({
      runs: [{ ...queuedRun, status: "running" }]
    });

    render(<PipelineCockpit />);
    expect(await screen.findByRole("button", { name: "Sync new documents…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Start pre-analysis…" })).toBeDisabled();
    await openAdvancedOperations();

    expect(await screen.findByText("Health check · Running")).toBeInTheDocument();
    expect(screen.getByText("Running. Close terminal/server to interrupt if necessary.")).toBeInTheDocument();
  });

  it("refreshes status when the refresh button is clicked", async () => {
    render(<PipelineCockpit />);
    await screen.findByRole("heading", { name: "Source intake" });
    await userEvent.click(screen.getByRole("button", { name: "Build Wiki" }));
    await screen.findByRole("button", { name: "Update Wiki" });

    const refreshButtons = screen.getAllByRole("button", { name: "Refresh status" });
    await userEvent.click(refreshButtons[0]);

    await waitFor(() => {
      expect(api.getUpdateWikiStatus).toHaveBeenCalledTimes(2);
    });
  });

  it("shows stderr tail for failed runs", async () => {
    vi.mocked(api.listOperationRuns).mockResolvedValue({ runs: [failedRun] });

    render(<PipelineCockpit />);
    await openAdvancedOperations();

    expect((await screen.findAllByText("lint failed")).length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "Run details" })).toBeInTheDocument();
  });

  it("shows a readable inline result summary for the operation that was clicked", async () => {
    vi.mocked(api.startOperationRun).mockResolvedValue({
      run_id: selectRun.run_id,
      operation_id: "synthesis_select",
      status: "succeeded"
    });
    vi.mocked(api.getOperationRun).mockResolvedValue(selectRun);

    render(<PipelineCockpit />);
    await openAdvancedOperations();

    await userEvent.click(screen.getByRole("button", { name: "Show candidates" }));

    const operation = await screen.findByLabelText("Candidate ranking result");
    expect(within(operation).getByText("Candidate ranking succeeded")).toBeInTheDocument();
    expect(within(operation).getByText("42 total · 20 shown")).toBeInTheDocument();
    expect(within(operation).getByText(/topic:service-automation/)).toBeInTheDocument();
    expect(within(operation).getByText(/Service Automation/)).toBeInTheDocument();
    expect(within(operation).getByText(/7 sources/)).toBeInTheDocument();
    expect(within(operation).queryByText(/"entries"/)).not.toBeInTheDocument();

    await userEvent.click(within(operation).getByRole("button", { name: "Show technical details" }));

    expect(within(operation).getByText("Technical stdout")).toBeInTheDocument();
    expect(within(operation).getByText(/20260716T100030Z-synthesis-select/)).toBeInTheDocument();
  });
});
