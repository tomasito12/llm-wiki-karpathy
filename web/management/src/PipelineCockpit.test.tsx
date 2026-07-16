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

const failedRun = {
  ...queuedRun,
  run_id: "20260716T100100Z-wiki-lint",
  status: "failed" as const,
  finished_at: "2026-07-16T10:01:00Z",
  duration_seconds: 1,
  exit_code: 2,
  stderr_tail: "lint failed"
};

describe("PipelineCockpit", () => {
  beforeEach(() => {
    vi.mocked(api.getOpsStatus).mockResolvedValue(statusPayload);
    vi.mocked(api.getOpsOperations).mockResolvedValue(operationsPayload);
    vi.mocked(api.listOperationRuns).mockResolvedValue({ runs: [] });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it("loads the status summary and recommendations", async () => {
    render(<PipelineCockpit />);

    expect(await screen.findByText("12 sources · 8 reviewed · render current · 3 stale syntheses")).toBeInTheDocument();
    expect(screen.getByText("Refresh stale synthesis entries before final render.")).toBeInTheDocument();
    expect(screen.getByText("Review uncommitted docs and code files before continuing.")).toBeInTheDocument();
  });

  it("renders operation cards with safety metadata", async () => {
    render(<PipelineCockpit />);

    expect(await screen.findByText("read-only · no LLM calls")).toBeInTheDocument();
    expect(screen.getByText("writes files · no LLM calls")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run Wiki render…" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run Synthesis batch…" })).toBeInTheDocument();
  });

  it("starts a read-only operation without confirmation", async () => {
    vi.mocked(api.startOperationRun).mockResolvedValue({
      run_id: queuedRun.run_id,
      operation_id: "wiki_lint",
      status: "queued"
    });
    vi.mocked(api.getOperationRun).mockResolvedValue(queuedRun);

    render(<PipelineCockpit />);
    await screen.findByText("12 sources · 8 reviewed · render current · 3 stale syntheses");

    const lintButtons = screen.getAllByRole("button", { name: "Wiki lint" });
    await userEvent.click(lintButtons[lintButtons.length - 1]);

    await waitFor(() => {
      expect(api.startOperationRun).toHaveBeenCalledWith({
        operation_id: "wiki_lint",
        parameters: {},
        confirmed: false
      });
    });
    expect(await screen.findByText("Wiki lint · Queued")).toBeInTheDocument();
  });

  it("opens confirmation for write and LLM operations", async () => {
    render(<PipelineCockpit />);
    await screen.findByText("12 sources · 8 reviewed · render current · 3 stale syntheses");

    await userEvent.click(screen.getByRole("button", { name: "Run Wiki render…" }));

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("Confirm operation")).toBeInTheDocument();
    expect(within(dialog).getByText("Writes: yes")).toBeInTheDocument();
    expect(within(dialog).getByText("LLM calls: no")).toBeInTheDocument();
    expect(api.startOperationRun).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "Run Synthesis batch…" }));
    expect(await screen.findByText("LLM calls: yes")).toBeInTheDocument();
  });

  it("shows running state for active runs", async () => {
    vi.mocked(api.listOperationRuns).mockResolvedValue({
      runs: [{ ...queuedRun, status: "running" }]
    });

    render(<PipelineCockpit />);

    expect(await screen.findByText("Wiki lint · Running")).toBeInTheDocument();
    expect(screen.getByText("Running. Close terminal/server to interrupt if necessary.")).toBeInTheDocument();
  });

  it("refreshes status when the refresh button is clicked", async () => {
    render(<PipelineCockpit />);
    await screen.findByText("12 sources · 8 reviewed · render current · 3 stale syntheses");

    await userEvent.click(screen.getByRole("button", { name: "Refresh status" }));

    await waitFor(() => {
      expect(api.getOpsStatus).toHaveBeenCalledTimes(2);
    });
  });

  it("shows stderr tail for failed runs", async () => {
    vi.mocked(api.listOperationRuns).mockResolvedValue({ runs: [failedRun] });

    render(<PipelineCockpit />);

    expect(await screen.findByText("lint failed")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Run details" })).toBeInTheDocument();
  });
});
